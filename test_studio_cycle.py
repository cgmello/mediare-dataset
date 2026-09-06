"""Controle do ciclo: testes sem rede, contas reais ou chamadas LLM."""
import base64
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

import studio_cycle as sc
from test_ic_experimental import fixture, IC


HASH = "0x" + "1" * 64
ADDR = "0x" + "2" * 40


def receipt(status="FINALIZED", execution="SUCCESS"):
    return {"statusName": status, "data": {"contract_address": ADDR},
            "consensus_data": {"leader_receipt": [{"execution_result": execution}]}}


class CycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.studio = SimpleNamespace(account=SimpleNamespace(address=ADDR), chain_id=61999,
                                      endpoint=sc.RPC, receipt=Mock(return_value=receipt()),
                                      recover_hash=Mock(return_value=HASH), before_send=None, after_send=None)
        self.c = sc.Cycle(self.studio, self.temp.name, poll=15, timeout=15)
        self.c.m = {"account": ADDR, "chain_id": 61999, "deadline": time.time() + 100,
                    "send_attempts": 0, "max_calls": 3, "max_versions": 1,
                    "contract": ADDR, "versions": [], "ops": []}
        self.c.save()

    def test_success_requires_receipt_and_finality(self):
        self.assertTrue(sc.successful(receipt()))
        for tx in (receipt("ACCEPTED"), receipt(execution="ERROR"), {"status": 7, "result_name": "MAJORITY_AGREE"}):
            self.assertFalse(sc.successful(tx))

    def test_extract_deploy_address_unambiguous(self):
        self.assertEqual(sc.contract_address(receipt()), ADDR)
        tx = receipt()
        tx["data"]["other"] = {"contract_address": "0x" + "3" * 40}
        with self.assertRaises(sc.CycleError):
            sc.contract_address(tx)

    def test_uncertain_send_never_resubmitted(self):
        op = self.c.operation("deploy")
        send = Mock(side_effect=TimeoutError)
        with self.assertRaises(TimeoutError):
            self.c.submit(op, send)
        with self.assertRaises(sc.CycleError):
            self.c.submit(op, send)
        with self.assertRaises(sc.CycleError):
            self.c.wait(op)
        self.assertEqual(send.call_count, 1)
        self.assertEqual(self.c.m["send_attempts"], 1)
        with self.assertRaises(sc.CycleError):
            self.c.operation("upgrade", "10.2.1-experimental")

    def test_recover_hash_then_wait_no_new_send(self):
        op = self.c.operation("deploy")
        def send():
            self.studio.before_send()
            self.studio.after_send(HASH)
            raise TimeoutError()
        with self.assertRaises(TimeoutError):
            self.c.submit(op, send)
        self.assertTrue(sc.successful(self.c.wait(op)))
        self.studio.recover_hash.assert_called_once_with(HASH)
        self.assertEqual(op["state"], "done")
        self.assertEqual(self.c.m["send_attempts"], 1)
        self.assertGreaterEqual(self.c.m["next_send_at"], time.time() + 14)

    def test_delay_is_after_execution(self):
        op = self.c.operation("deploy")
        self.c.m["next_send_at"] = time.time() + 15
        with patch("studio_cycle.time.sleep") as sleep:
            self.c.submit(op, lambda: HASH)
            self.assertGreater(sleep.call_args.args[0], 14)

    def test_budgets_and_clock_expiry(self):
        op = self.c.operation("deploy")
        send = Mock(return_value=HASH)
        self.c.m["send_attempts"] = 3
        with self.assertRaises(sc.CycleError):
            self.c.submit(op, send)
        self.c.m.update(send_attempts=0, deadline=0)
        with self.assertRaises(sc.CycleError):
            self.c.submit(op, send)
        send.assert_not_called()

    def test_timeout_keeps_pending_and_blocks_next(self):
        op = self.c.operation("deploy")
        self.c.submit(op, lambda: HASH)
        self.studio.receipt.return_value = receipt("PROPOSING")
        with patch("studio_cycle.time.monotonic", side_effect=[0, 20]):
            with self.assertRaises(sc.CycleError):
                self.c.wait(op)
        self.assertEqual(op["state"], "pending")
        with self.assertRaises(sc.CycleError):
            self.c.operation("upgrade", "10.2.1-experimental")

    def test_snapshot_and_version_contract(self):
        code = Path("ic_experimental.py").read_bytes()
        self.assertEqual(sc.version_of(code), IC["VERSAO"])
        self.c.stage("candidate.py", code)
        with self.assertRaises(sc.CycleError):
            self.c.stage("candidate.py", b"other")
        with self.assertRaises(sc.CycleError):
            sc.version_of(code.replace(b"    painel: str", b"    outro: str"))
        with self.assertRaises(sc.CycleError):
            sc.version_of(code.replace(b"def upgrade(", b"def no_upgrade("))

    def test_version_limit_before_network(self):
        self.c.m["versions"] = [{"version": "10.1.9-experimental", "finished": True}]
        with self.assertRaisesRegex(sc.CycleError, "Limite de versoes"):
            self.c.run("ic_experimental.py")

    def test_mismatched_remote_hash_prevents_analysis(self):
        code = Path("ic_experimental.py").read_bytes()
        row = {"version": IC["VERSAO"], "snapshot": "v.py", "sha256": sc.sha(code)}
        self.c.stage("v.py", code)
        op = self.c.operation("upgrade", IC["VERSAO"])
        self.c.submit(op, lambda: HASH)
        self.c.wait(op)
        self.studio.read = Mock(side_effect=[IC["VERSAO"], "wrong hash"])
        with self.assertRaisesRegex(sc.CycleError, "hash remoto"):
            self.c.continue_round(row)
        self.assertEqual(len(self.c.m["ops"]), 1)

    def test_evaluation_does_not_certify_legal_merit(self):
        p = fixture()
        state = {"versao": IC["VERSAO"], "case_id": "0005", "status": "termo_opcao_disponivel",
                 "termo_opcao": IC["_render_termo_opcao"]("0005", p), "painel": json.dumps(p)}
        result = sc.evaluate(state, IC["VERSAO"], "0005")
        self.assertEqual(result["merito"], "PENDENTE_REVISAO")
        self.assertEqual(result["pedidos"][0]["tipo"], "formula")
        with self.assertRaises(sc.CycleError):
            sc.evaluate(state, "10.2.999-experimental", "0005")

    def test_summary_only_stored_leader_errors(self):
        tx = receipt(execution="ERROR")
        tx["consensus_data"]["leader_receipt"][0]["result"] = base64.b64encode(b"\x01LLM_INVALID_PANEL").decode()
        self.assertEqual(sc.summary(tx)["erros"], ["LLM_INVALID_PANEL"])
        self.assertIsNone(sc.summary(tx)["custo_monetario"])

    def test_extract_only_fixed_diagnostic_format(self):
        tx = receipt()
        tx["consensus_history"] = {"validator_results": [{"mode": "validator", "vote": "disagree",
            "genvm_result": {"stdout": "texto privado\nMEDIARE_DIAG:OPCOES\nMEDIARE_DIAG:valor privado\n"}}]}
        self.assertEqual(sc.summary(tx)["diagnosticos"], [{"mode": "validator", "vote": "disagree", "codes": ["OPCOES"]}])

    def test_account_binding(self):
        self.studio.account.address = "0x" + "3" * 40
        with self.assertRaises(sc.CycleError):
            sc.Cycle(self.studio, self.temp.name)

    def test_bootstrap_upgrade_owner_and_storage_preserved(self):
        class Code(bytearray):
            def truncate(self):
                self.clear()
            def slot(self):
                return self
            def read(self, offset, size):
                self.assert_offset = offset
                return bytes(memoryview(self)[:size])
        code, owners = Code(b"initial"), []
        root = SimpleNamespace(code=SimpleNamespace(get=lambda: code), upgraders=SimpleNamespace(get=lambda: owners))
        gl = SimpleNamespace(Contract=object, public=SimpleNamespace(write=lambda f: f, view=lambda f: f),
                             storage=SimpleNamespace(Root=SimpleNamespace(get=lambda: root)),
                             message=SimpleNamespace(sender_address=ADDR), vm=SimpleNamespace(UserError=ValueError))
        for source, name in (("studio_bootstrap.py", "MediareStudioBootstrap"), ("ic_experimental.py", "MediareCommitteeExperimental")):
            ns = {"gl": gl}
            exec(compile(Path(source).read_text().replace("from genlayer import *", ""), source, "exec"), ns)
            c = ns[name]()
            c.case_id, c.painel, c.termo_opcao = "0005", "previous panel", "previous term"
            c.upgrade(b"replacement")
            self.assertEqual(c.get_code_hash(), sc.sha(b"replacement"))
            self.assertEqual(code.assert_offset, 4)
            self.assertEqual((c.case_id, c.painel, c.termo_opcao), ("0005", "previous panel", "previous term"))
            with self.assertRaisesRegex(ValueError, "CODIGO_VAZIO"):
                c.upgrade(b"")
            gl.message.sender_address = "unauthorized"
            self.assertFalse(c.can_upgrade())
            with self.assertRaisesRegex(ValueError, "UPGRADE_NAO_AUTORIZADO"):
                c.upgrade(b"malicious")
            self.assertEqual(bytes(code), b"replacement")
            gl.message.sender_address = ADDR

    def test_skip_requires_no_analysis_no_pending(self):
        row = {"version": IC["VERSAO"], "finished": False}
        self.c.m["versions"] = [row]
        op = self.c.operation("upgrade", IC["VERSAO"])
        with self.assertRaises(sc.CycleError):
            self.c.skip("read failure")
        self.c.submit(op, lambda: HASH)
        self.c.wait(op)
        self.c.skip("Hash getter timed out; replace with bulk read")
        self.assertEqual(row["result"], "SKIPPED_BEFORE_ANALYSIS")
        row["finished"] = False
        self.c.m["ops"].append({"kind": "analyze_case", "version": IC["VERSAO"], "state": "done"})
        with self.assertRaises(sc.CycleError):
            self.c.skip("must not hide results")

    def test_receipt_secrets_redacted_before_persistence(self):
        obj = {"node_config": [{"private_key": "sensitive", "apiKey": "sensitive", "address": ADDR}]}
        sc.write_json(Path(self.temp.name) / "secret-test.json", obj)
        saved = (Path(self.temp.name) / "secret-test.json").read_text()
        self.assertNotIn("sensitive", saved)
        self.assertIn(ADDR, saved)

    def test_rollback_uses_recorded_snapshot_and_no_analysis(self):
        code = Path("ic_experimental.py").read_bytes()
        self.c.stage("milestone.py", code)
        self.c.m["versions"] = [{"version": IC["VERSAO"], "snapshot": "milestone.py", "sha256": sc.sha(code), "finished": True}]
        self.c.check_upgrade = Mock()
        self.studio.client = SimpleNamespace(write_contract=Mock(return_value=HASH))
        self.studio.read = Mock(side_effect=[IC["VERSAO"], sc.sha(code)])
        self.c.rollback(IC["VERSAO"], "Regressao medida na revisao posterior")
        self.studio.client.write_contract.assert_called_once()
        call = self.studio.client.write_contract.call_args.kwargs
        self.assertEqual(call["function_name"], "upgrade")
        self.assertEqual(call["args"], [code])
        self.assertEqual(self.c.m["ops"][0]["restore_result"], "VERIFIED")
        self.assertEqual(len(self.c.m["ops"]), 1)

    def test_rollback_refuses_pending_or_unregistered(self):
        with self.assertRaises(sc.CycleError):
            self.c.rollback("11.0.0-experimental", "x")
        self.c.operation("analyze_case", "11.0.0-experimental")
        with self.assertRaises(sc.CycleError):
            self.c.rollback("11.0.0-experimental", "x")


if __name__ == "__main__":
    unittest.main()
