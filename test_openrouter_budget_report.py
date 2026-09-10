import json
from pathlib import Path
import tempfile
import unittest

from openrouter_budget_report import build_ledger, render_html


def write_summary(root, directory, **values):
    path = Path(root) / directory
    path.mkdir(parents=True, exist_ok=True)
    (path / "summary.json").write_text(json.dumps(values), encoding="utf-8")


class OpenRouterBudgetReportTests(unittest.TestCase):
    def test_ledger_uses_key_total_and_does_not_sum_overlapping_deltas(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_summary(
                root, "res_openrouter_v20_0001_0050", completed=50, total=50,
                api_calls=500, cost_usd="10", itemized_cost_usd="9.5",
                key_usage_delta_usd="10",
            )
            write_summary(
                root, "res_openrouter_v21_schema_0001_0050", completed=10, total=50,
                api_calls=100, cost_usd="7", itemized_cost_usd="2",
                key_usage_delta_usd="7",
            )
            write_summary(root, "res_pseudonymization_0501_1000", completed=5, total=500,
                          api_calls=10, cost_usd="0.1", status="in_progress")
            account = {"key_usage_usd": "12.5", "captured_at": "2026-09-10T00:00:00Z"}
            ledger = build_ledger(root, account)
            self.assertEqual(ledger["spent"], 12.5)
            # The v21 key delta of 7 is ignored; only its $2 receipts count.
            schema = next(row for row in ledger["rows"] if row["activity"] == "v21-schema candidate")
            self.assertEqual(schema["cost"], 2)
            self.assertGreater(ledger["reconciliation"], 0)
            self.assertEqual(ledger["remaining"], 487.5)
            self.assertEqual(ledger["historical_external_estimate"], 20)
            self.assertEqual(ledger["total_project_cost"], 32.5)
            historical = next(row for row in ledger["rows"] if "Anthropic" in row["activity"])
            self.assertFalse(historical["grant_scope"])

    def test_ledger_falls_back_to_newer_local_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_summary(root, "res_openrouter_v21_schema_0001_0050", completed=2,
                          total=50, api_calls=4, itemized_cost_usd="3")
            ledger = build_ledger(root, {"key_usage_usd": "1"})
            self.assertGreater(ledger["spent"], 3)
            self.assertTrue(ledger["snapshot_lag"])

    def test_html_is_concise_and_contains_budget_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            write_summary(
                directory, "res_pseudonymization_0501_1000", completed=500,
                accepted=491, needs_review=9, total=500, api_calls=1035,
                total_tokens=4660192, cost_usd="15.91735175", status="complete",
            )
            ledger = build_ledger(directory, {
                "key_usage_usd": "12.53",
                "captured_at": "2026-09-10T00:00:00Z",
                "account_available_balance_usd": "7.47",
            })
            html = render_html(ledger)
            self.assertIn("US$500 Grant Ledger", html)
            self.assertIn("v21-schema candidate", html)
            self.assertIn("Collection of 500 public decisions", html)
            self.assertIn("How the project reached v20", html)
            self.assertIn("v1 prototype", html)
            self.assertIn("Earlier Anthropic API cost", html)
            self.assertIn("estimated, outside the grant", html)
            self.assertIn("491 accepted; 9 need review", html)
            self.assertIn("<th>Tokens</th>", html)
            self.assertIn("4,660,192", html)
            self.assertNotIn("<th>Funding scope</th>", html)
            self.assertIn('<td colspan="3">TOTAL</td>', html)
            self.assertIn('<tr class="historical-external">', html)
            self.assertIn("Total refers only to the US$500 OpenRouter budget", html)
            self.assertIn("the US$20 pre-grant estimate is excluded", html)
            self.assertIn("<td>US$ 15.9174</td>", html)
            self.assertEqual(
                ledger["total_api_calls"],
                sum(row["calls"] or 0 for row in ledger["rows"]),
            )
            self.assertEqual(
                ledger["total_tokens"],
                sum(row["tokens"] or 0 for row in ledger["rows"]),
            )
            self.assertEqual(
                ledger["total_openrouter_cost"],
                sum((row["cost"] for row in ledger["rows"] if row["grant_scope"]), start=0),
            )
            self.assertIn("single consolidated OpenRouter grant-cost report", html)
            self.assertNotIn("Anthropic Usage and Cost API", html)
            self.assertNotIn("platform.claude.com/docs/en/manage-claude/usage-cost-api", html)
            self.assertLess(len(html), 15000)


if __name__ == "__main__":
    unittest.main()
