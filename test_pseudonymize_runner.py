import json
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from pseudonymize_runner import (
    audit_output,
    cached_detection,
    clean_date,
    initials,
    initialize,
    local_entities,
    merged_entities,
    parse_detector,
    replace_all,
    replacement_map,
    total_calls,
    total_cost,
)
from openrouter_runner import RunnerError


PROCESS = "1234567-89.2025.8.26.0001"


class PseudonymizeRunnerTests(unittest.TestCase):
    def test_initials_ignore_portuguese_particles(self):
        self.assertEqual(initials("Maria de Souza da Silva"), "M.S.S.")
        self.assertEqual(initials("CLÍNICA EXEMPLO REGIONAL LTDA"), "C.E.R.L.")

    def test_contaminated_date_keeps_only_date(self):
        self.assertEqual(clean_date("27/07/2026 corpo indevido"), "27/07/2026")

    def test_detector_requires_exact_source_substrings(self):
        source = '{"texto":"Maria Exemplo compareceu"}'
        valid = parse_detector(
            '{"entities":[{"text":"Maria Exemplo","kind":"person"}]}', source
        )
        self.assertEqual(valid[0]["text"], "Maria Exemplo")
        with self.assertRaisesRegex(RunnerError, "DETECTOR_ENTITY_INVALID"):
            parse_detector(
                '{"entities":[{"text":"Pessoa Inventada","kind":"person"}]}', source
            )

    def test_local_application_preserves_facts_and_removes_identifiers(self):
        original = {
            "processo": PROCESS,
            "magistrado": "Maria de Souza da Silva",
            "data": "01/09/2026",
            "texto": (
                f"Processo Digital nº: {PROCESS} Requerente: João de Teste "
                "Requerido: CLÍNICA EXEMPLO LTDA VISTOS. JOÃO DE TESTE pagou R$ 400,00."
            ),
        }
        detected = [
            {"text": PROCESS, "kind": "case_number"},
            {"text": "Maria de Souza da Silva", "kind": "person"},
            {"text": "João de Teste", "kind": "person"},
            {"text": "CLÍNICA EXEMPLO LTDA", "kind": "private_organization"},
        ]
        entities = merged_entities([local_entities(original), detected])
        replacements = replacement_map(entities, PROCESS, "0501")
        record = dict(original)
        record["processo"] = "0501"
        record["magistrado"] = replace_all(record["magistrado"], replacements)
        record["texto"] = replace_all(record["texto"], replacements)
        self.assertEqual(record["magistrado"], "M.S.S.")
        self.assertIn("J.T. pagou R$ 400,00", record["texto"])
        self.assertIn("C.E.L.", record["texto"])
        self.assertNotIn(PROCESS, record["texto"])
        self.assertEqual(audit_output(record, original, replacements), [])

    def test_initialize_requires_two_models_and_zdr(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.jsonl"
            source.write_text(json.dumps({
                "processo": PROCESS, "texto": "texto de teste suficientemente simples"
            }) + "\n", encoding="utf-8")
            config = root / "models.json"
            config.write_text(json.dumps({
                "models": ["model/a", "model/b"],
                "provider": {"zdr": True, "data_collection": "deny"},
                "max_tokens": 1000,
            }), encoding="utf-8")
            args = type("Args", (), {
                "out": str(root / "out"), "input": str(source),
                "start_line": 1, "count": 1, "first_id": 501,
                "models": str(config), "max_cost": Decimal("2"),
            })()
            manifest = initialize(args)
            self.assertTrue(manifest["provider"]["zdr"])
            self.assertEqual(manifest["first_internal_id"], 501)

    def test_invalid_detector_response_is_retried_and_charged(self):
        class FakeClient:
            def __init__(self):
                self.calls = 0

            def complete(self, model, prompt, max_tokens):
                self.calls += 1
                text = "not-json" if self.calls == 1 else (
                    '{"entities":[{"text":"Maria Exemplo","kind":"person"}]}'
                )
                return {"text": text, "cost_usd": str(self.calls / 10)}

        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            out = Path(directory)
            entities, _ = cached_detection(
                client, out, "0501", "model/a", "prompt", 1000,
                '{"texto":"Maria Exemplo"}',
            )
            self.assertEqual(client.calls, 2)
            self.assertEqual(entities[0]["text"], "Maria Exemplo")
            self.assertEqual(total_cost(out), Decimal("0.3"))
            self.assertEqual(total_calls(out), 2)

    def test_third_entity_failure_is_filtered_and_flagged_for_review(self):
        class FakeClient:
            def __init__(self):
                self.calls = 0

            def complete(self, model, prompt, max_tokens):
                self.calls += 1
                return {
                    "text": json.dumps({"entities": [
                        {"text": "Maria Exemplo", "kind": "person"},
                        {"text": "Pessoa Inventada", "kind": "person"},
                    ]}),
                    "cost_usd": str(Decimal(self.calls) / 10),
                }

        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            out = Path(directory)
            entities, metadata = cached_detection(
                client, out, "0616", "model/a", "prompt", 1000,
                '{"texto":"Maria Exemplo"}',
            )
            self.assertEqual(entities, [{"text": "Maria Exemplo", "kind": "person"}])
            self.assertTrue(metadata["detector_partial"])
            self.assertEqual(metadata["invalid_entities_dropped"], 1)
            self.assertEqual(total_cost(out), Decimal("0.6"))
            self.assertEqual(total_calls(out), 3)


if __name__ == "__main__":
    unittest.main()
