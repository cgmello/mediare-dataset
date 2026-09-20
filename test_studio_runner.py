#!/usr/bin/env python3
"""Proteções locais do runner de lotes do Studio."""

import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
