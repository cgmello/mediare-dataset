import json
from pathlib import Path
import tempfile
import unittest

from compare_v21 import candidate_metrics, is_structural_diagnostic, rank_key, render_html
from v21_campaign_orchestrator import completed, ensure_itemized_cost_basis


class CompareV21Tests(unittest.TestCase):
    def test_invalid_panel_diagnostic_is_structural(self):
        self.assertTrue(is_structural_diagnostic(
            "LLM_INVALID_PANEL:revisao_compacta:1=REVISAO_BOOLEANO_INVALIDO"
        ))

    def test_metrics_count_structural_failures_and_useful_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "campaign"
            (out / "results").mkdir(parents=True)
            (out / "campaign.json").write_text(json.dumps({
                "version": "test", "case_ids": ["0001"],
            }), encoding="utf-8")
            (out / "summary.json").write_text(json.dumps({"cost_usd": "1.25"}))
            (out / "results" / "0001.json").write_text(json.dumps({
                "leader_error": None,
                "leader_impression": {"label": "APTO_INTEGRAL"},
                "local_consensus": "LOCAL_MAJORITY_DISAGREE",
                "reviewers": [{
                    "vote": "disagree", "diagnostic": "REVISAO_FALHAS_INVALIDAS",
                }],
            }), encoding="utf-8")
            row = candidate_metrics(root, "candidate", "campaign")
            self.assertEqual(row["valid_leader_panels"], 1)
            self.assertEqual(row["useful_leader_outputs"], 1)
            self.assertEqual(row["reviewer_structural_failures"], 1)
            self.assertFalse(row["automatic_gates_pass"])

    def test_rank_prioritizes_gates_and_html_does_not_auto_promote_incomplete(self):
        passed = {
            "name": "passed", "status": "complete", "automatic_gates_pass": True,
            "valid_leader_panels": 45, "useful_leader_outputs": 40,
            "local_majority_agree": 20, "reviewer_structural_failures": 0,
            "completed": 50, "total": 50,
        }
        failed = {
            "name": "failed", "status": "complete", "automatic_gates_pass": False,
            "valid_leader_panels": 50, "useful_leader_outputs": 50,
            "local_majority_agree": 50, "reviewer_structural_failures": 1,
            "completed": 50, "total": 50,
        }
        self.assertGreater(rank_key(passed), rank_key(failed))
        html = render_html([{**passed, "status": "in_progress"}, failed])
        self.assertIn("No candidate is eligible yet", html)

    def test_html_reports_complete_campaigns_that_miss_gates(self):
        failed = {
            "name": "failed", "status": "complete", "automatic_gates_pass": False,
            "valid_leader_panels": 42, "useful_leader_outputs": 38,
            "local_majority_agree": 20, "reviewer_structural_failures": 0,
            "completed": 50, "total": 50,
        }
        html = render_html([failed])
        self.assertIn("All campaigns are complete", html)
        self.assertIn("V21_CASE_BY_CASE_ANALYSIS.html", html)

    def test_orchestrator_requires_exactly_fifty_complete_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "summary.json").write_text(json.dumps({
                "completed": 49, "total": 50,
            }), encoding="utf-8")
            self.assertFalse(completed(out))
            (out / "summary.json").write_text(json.dumps({
                "completed": 50, "total": 50,
            }), encoding="utf-8")
            self.assertTrue(completed(out))

    def test_orchestrator_marks_v21_campaign_for_shared_key_accounting(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "campaign.json").write_text(json.dumps({
                "version": "21.0.0-test", "max_cost_usd": "15",
            }), encoding="utf-8")
            ensure_itemized_cost_basis(out)
            manifest = json.loads((out / "campaign.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["cost_basis"], "itemized_receipts")


if __name__ == "__main__":
    unittest.main()
