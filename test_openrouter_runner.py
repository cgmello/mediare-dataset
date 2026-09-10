import json
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

from openrouter_runner import (
    ReplayCaller,
    RunnerError,
    load_contract,
    load_jsonl,
    load_models,
    reconciled_campaign_cost,
    raise_budget,
    render_report,
    total_cost,
)


class FakeClient:
    def __init__(self):
        self.calls = 0
        self.request_attempts = 0

    def complete(self, model, prompt, max_tokens):
        self.calls += 1
        self.request_attempts += 1
        return {
            "text": '{"ok":true}',
            "request_id": "gen-test",
            "requested_model": model,
            "served_model": model,
            "provider": "test",
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
            "cost_usd": "0.0125",
            "duration_seconds": 0.1,
            "http_status": 200,
        }


class OpenRouterRunnerTests(unittest.TestCase):
    def test_budget_raise_is_explicit_and_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "campaign.json").write_text(json.dumps({
                "max_cost_usd": "10", "program_credit_usd": "500",
                "case_ids": [], "models": [], "reviewer_quorum": 0,
                "source_sha256": "test",
            }))
            args = type("Args", (), {
                "out": str(out), "max_cost": 12,
                "report": str(out / "report.html"),
            })()
            result = raise_budget(args)
            self.assertEqual(json.loads((out / "campaign.json").read_text())["max_cost_usd"], "12")
            self.assertEqual(load_jsonl(out / "events.jsonl")[0]["event"], "budget_raised")
            self.assertEqual(result["total"], 0)

    def test_campaign_cost_uses_key_delta_when_itemized_responses_are_incomplete(self):
        manifest = {
            "account_start": {"key_usage_usd": "1.25"},
            "account_latest": {"key_usage_usd": "3.75"},
        }
        actual, delta = reconciled_campaign_cost(manifest, "2.10")
        self.assertEqual(str(actual), "2.50")
        self.assertEqual(str(delta), "2.50")

    def test_concurrent_campaign_cost_uses_only_its_itemized_receipts(self):
        manifest = {
            "cost_basis": "itemized_receipts",
            "account_start": {"key_usage_usd": "1.25"},
            "account_latest": {"key_usage_usd": "13.75"},
        }
        actual, delta = reconciled_campaign_cost(manifest, "2.10")
        self.assertEqual(str(actual), "2.10")
        self.assertEqual(str(delta), "12.50")

    def test_loads_exact_v20_functions(self):
        ic = load_contract("res_canary_v20/20.0.0-experimental.py")
        self.assertEqual(ic["VERSAO"], "20.0.0-experimental")
        self.assertTrue(callable(ic["_painel_de"]))
        self.assertTrue(callable(ic["_revisao_de"]))
        captured = io.StringIO()
        with redirect_stdout(captured):
            ic["_diag_consenso"]("REVISOR_APROVA")
        self.assertEqual(captured.getvalue().strip(), "MEDIARE_DIAG:REVISOR_APROVA")

    def test_model_config_has_five_models_and_quorum_three(self):
        models, quorum, provider, model_options = load_models("openrouter_models_v20.json")
        self.assertEqual(len(models), 5)
        self.assertEqual(quorum, 3)
        self.assertEqual(provider["data_collection"], "deny")
        self.assertEqual(model_options["z-ai/glm-5.3"]["reasoning"]["effort"], "low")

    def test_replay_cache_avoids_second_api_charge(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            first = ReplayCaller(client, directory, "0001", "leader", "test/model", "1")
            self.assertEqual(first("prompt", response_format="text"), '{"ok":true}')
            self.assertEqual(client.calls, 1)
            second = ReplayCaller(client, directory, "0001", "leader", "test/model", "1")
            self.assertEqual(second("prompt", response_format="text"), '{"ok":true}')
            self.assertEqual(client.calls, 1)
            self.assertEqual(total_cost(directory), (total_cost(directory)[0], 1))
            self.assertEqual(str(total_cost(directory)[0]), "0.0125")

    def test_replay_rejects_changed_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            ReplayCaller(client, directory, "0001", "leader", "test/model", "1")("first")
            with self.assertRaisesRegex(RunnerError, "cached call"):
                ReplayCaller(client, directory, "0001", "leader", "test/model", "1")("changed")

    def test_single_investor_report_contains_explanation_results_and_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "campaign"
            result_path = out / "results" / "0001.json"
            result_path.parent.mkdir(parents=True)
            result_path.write_text(json.dumps({
                "case_id": "0001", "category": "locacao", "leader_model": "test/leader",
                "leader_error": None, "reviewer_agree": 3, "reviewer_total": 4,
                "local_consensus": "LOCAL_MAJORITY_AGREE",
                "leader_impression": {"label": "APTO_INTEGRAL"},
                "studio_baseline": {"consensus": "MAJORITY_AGREE", "label": "APTO_INTEGRAL"},
                "elapsed_seconds": 12.5,
            }), encoding="utf-8")
            calls = out / "calls" / "0001" / "leader.jsonl"
            calls.parent.mkdir(parents=True)
            calls.write_text(json.dumps({"cost_usd": "0.25"}) + "\n", encoding="utf-8")
            manifest = {
                "case_ids": [f"{n:04d}" for n in range(1, 51)], "models": ["test/leader"],
                "reviewer_quorum": 3, "source_sha256": "a" * 64,
                "program_credit_usd": "500", "version": "20.0.0-experimental",
            }
            report = Path(directory) / "report.html"
            summary = render_report(manifest, out, report)
            html = report.read_text(encoding="utf-8")
            self.assertIn("Why OpenRouter adds experimental value", html)
            self.assertIn("GenLayer Studio", html)
            self.assertIn("Actual API spend", html)
            self.assertIn("Proposed use of the remaining", html)
            self.assertEqual(summary["cost_usd"], "0.25")


if __name__ == "__main__":
    unittest.main()
