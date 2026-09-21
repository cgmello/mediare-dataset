#!/usr/bin/env python3
"""Proteções locais do runner de lotes do Studio."""

import unittest
from unittest.mock import patch
from types import SimpleNamespace
from pathlib import Path
import tempfile

import studio_runner as sr


class StudioRunnerSafetyTests(unittest.TestCase):
    def test_redact_removes_nested_credentials_but_keeps_public_metadata(self):
        value = {
            "node_config": [{
                "private_key": "remote-secret",
                "apiKey": "provider-secret",
                "address": "0x1234",
            }],
            "result": {"authorization": "bearer-secret", "status": "ok"},
        }
        clean = sr.redact(value)
        self.assertEqual(clean["node_config"][0]["private_key"], "[REDACTED]")
        self.assertEqual(clean["node_config"][0]["apiKey"], "[REDACTED]")
        self.assertEqual(clean["result"]["authorization"], "[REDACTED]")
        self.assertEqual(clean["node_config"][0]["address"], "0x1234")
        self.assertEqual(clean["result"]["status"], "ok")

    def test_native_genvm_ep_is_not_reported_as_json_decode_error(self):
        tx = {
            "status": 5,
            "result_name": "MAJORITY_AGREE",
            "num_of_rounds": "1",
            "rotation_count": 0,
            "consensus_data": {
                "votes": {"a": "agree", "b": "agree", "c": "agree"},
                "leader_receipt": [{
                    "execution_result": "SUCCESS",
                    "eq_outputs": {"0": {"raw": "ignored"}},
                    "node_config": {},
                }],
            },
        }
        with patch.object(sr, "decode_eq", return_value="\x26\x08catalogo"):
            metric = sr.extrair_metricas("0124", tx, 10)
        self.assertEqual(metric["painel_ep0_formato"], "objeto_genvm")
        self.assertNotIn("erro_decode", metric)
        self.assertEqual(metric["exec"], "SUCCESS")

    def test_poll_rpc_error_retries_same_hash_and_persists_terminal_state(self):
        class Client:
            calls = 0

            def write_contract(self, **_kwargs):
                return bytes.fromhex("12" * 32)

            def get_transaction(self, **_kwargs):
                self.calls += 1
                if self.calls == 1:
                    raise ValueError("upstream returned HTML")
                return {"hash": "0x" + "12" * 32, "status": 5}

        with tempfile.TemporaryDirectory() as tmp, patch.object(sr.time, "sleep", return_value=None):
            args = SimpleNamespace(out=tmp, poll=0, timeout=10, timeout_duro=100)
            tx, _duration = sr.rodar_caso(
                Client(), object(), "0x" + "34" * 20, "0404", args,
            )
            self.assertEqual(sr.status_de(tx), "ACCEPTED")
            pending = Path(tmp, "pending", "0404.json")
            self.assertTrue(pending.exists())
            state = __import__("json").loads(pending.read_text(encoding="utf-8"))
            self.assertEqual(state["state"], "terminal")
            self.assertEqual(state["hash"], "0x" + "12" * 32)


if __name__ == "__main__":
    unittest.main()
