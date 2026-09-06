import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from studio_cycle import CycleError, write_json
from studio_phase2 import Phase2, classify_success, render_report


VERSION = "17.0.0-experimental"


def state_with(option_type="faixa", negotiation_state="condicional"):
    option = {
        "tipo": option_type,
        "base": {"valor_centavos": 10000} if option_type in {"faixa", "formula"} else None,
    }
    negotiation = {
        "estado": negotiation_state,
        "opcao": option,
        "faixa_centavos": [4000, 6000] if option_type == "faixa" else None,
        "faixa_discussao_centavos": [0, 10000] if option_type == "formula" else None,
    }
    panel = {
        "versao": VERSION,
        "consolidado": {
            "painel_completo": True,
            "pedidos": [{"pedido_id": "RP01", "status": "necessita_informacao", "negociacao": negotiation}],
        },
    }
    return {
        "case_id": "0001",
        "versao": VERSION,
        "status": "termo_opcao_disponivel",
        "termo_opcao": "# Termo",
        "painel": json.dumps(panel),
    }


class FakeClient:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def write_contract(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return "0x" + "1" * 64


class FakeStudio:
    def __init__(self, error=None):
        self.account = SimpleNamespace(address="0x" + "a" * 40)
        self.chain_id = 61999
        self.endpoint = "https://studio.genlayer.com/api"
        self.client = FakeClient(error)
        self.before_send = None
        self.after_send = None


class Phase2Tests(unittest.TestCase):
    def test_strict_impression_distinguishes_range_and_broad_formula(self):
        valid = {"execucao_valida": True}
        self.assertEqual(classify_success(state_with("faixa"), valid)["label"],
                         "SATISFATORIO_AUTOMATICO")
        broad = classify_success(state_with("formula"), valid)
        self.assertEqual(broad["label"], "REVISAR_UTILIDADE")
        self.assertIn("FORMULA_COM_ENVELOPE_ZERO_A_CEM", broad["motivos"])
        retained = classify_success(state_with("faixa", "retida_pela_auditoria"), valid)
        self.assertEqual(retained["label"], "INSATISFATORIO_CONTEUDO")

    def test_uncertain_send_never_persists_remote_exception_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            manifest = {
                "account": "0x" + "a" * 40,
                "chain_id": 61999,
                "contract": "0x" + "b" * 40,
                "delay_seconds": 15,
                "send_attempts": 0,
                "next_send_at": 0,
                "cases": {"0001": {"state": "queued", "send_attempts": 0}},
            }
            write_json(out / "phase2.json", manifest)
            studio = FakeStudio(RuntimeError("node_config.private_key=DO_NOT_STORE"))
            campaign = Phase2(studio, out)
            with self.assertRaises(RuntimeError):
                campaign.submit("0001", campaign.m["cases"]["0001"])
            combined = (out / "phase2.json").read_text() + (out / "events.jsonl").read_text()
            self.assertNotIn("DO_NOT_STORE", combined)
            self.assertEqual(campaign.m["send_attempts"], 1)
            self.assertEqual(campaign.m["cases"]["0001"]["state"], "uncertain")
            with self.assertRaises(CycleError):
                campaign.submit("0001", campaign.m["cases"]["0001"])

    def test_case_id_is_sent_without_leading_zeroes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            manifest = {
                "account": "0x" + "a" * 40,
                "chain_id": 61999,
                "contract": "0x" + "b" * 40,
                "delay_seconds": 15,
                "send_attempts": 0,
                "next_send_at": 0,
                "cases": {"0005": {"state": "queued", "send_attempts": 0}},
            }
            write_json(out / "phase2.json", manifest)
            studio = FakeStudio()
            campaign = Phase2(studio, out)
            campaign.submit("0005", campaign.m["cases"]["0005"])
            self.assertEqual(studio.client.calls[0]["args"], ["5"])

    def test_report_counts_and_writes_per_case_impressions(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            manifest = {
                "version": VERSION,
                "contract": "0x" + "b" * 40,
                "case_ids": ["0001", "0002"],
            }
            base = {
                "origem": "ouro", "categoria": "teste", "version": VERSION,
                "transacao": {"status": "FINALIZED", "exec": "SUCCESS", "rotacoes": 0,
                              "diagnosticos": []},
                "termo": "terms/0001.md",
            }
            write_json(out / "results" / "0001.json", {
                **base, "id": "0001",
                "impressao": {"label": "SATISFATORIO_AUTOMATICO", "satisfatorio": True,
                               "motivos": [], "pedidos": 1, "status_pedidos": {},
                               "tipos_opcao": {}, "estados_negociacao": {}, "observacao": "teste"},
            })
            write_json(out / "results" / "0002.json", {
                **base, "id": "0002", "termo": None,
                "impressao": {"label": "INSATISFATORIO_TECNICO", "satisfatorio": False,
                               "motivos": ["TRANSACAO_SEM_FINALIZED_SUCCESS"], "pedidos": 0,
                               "status_pedidos": {}, "tipos_opcao": {},
                               "estados_negociacao": {}, "observacao": "teste"},
            })
            report = render_report(out, manifest)
            self.assertEqual(report["processed"], 2)
            self.assertEqual(report["labels"]["SATISFATORIO_AUTOMATICO"], 1)
            self.assertEqual(len((out / "impressions.jsonl").read_text().splitlines()), 2)
            self.assertIn("0002", (out / "report.md").read_text())


if __name__ == "__main__":
    unittest.main()
