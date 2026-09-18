#!/usr/bin/env python3
"""Proteções locais do runner de lotes do Studio."""

import unittest

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


if __name__ == "__main__":
    unittest.main()
