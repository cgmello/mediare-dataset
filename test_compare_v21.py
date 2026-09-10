import json
from pathlib import Path
import tempfile
import unittest

from compare_v21 import candidate_metrics, rank_key, render_html


class CompareV21Tests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
