import json
from pathlib import Path
import unittest

from analyze_v23_cases import ASSESSMENTS, CASE_IDS, render_html


class AnalyzeV23CasesTests(unittest.TestCase):
    def test_assessments_cover_the_frozen_selection(self):
        self.assertEqual(set(ASSESSMENTS), set(CASE_IDS))
        self.assertEqual(len(CASE_IDS), 20)

    def test_committed_analysis_is_complete_and_renderable(self):
        analysis = json.loads(
            Path("V23_CASE_BY_CASE_ANALYSIS.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(analysis["cases"]), 20)
        self.assertEqual(
            analysis["summary"]["majority_gained_cases"], ["0001", "0015"]
        )
        self.assertEqual(analysis["summary"]["majority_lost_cases"], [])
        self.assertEqual(
            analysis["summary"]["disagreement_diagnosis"]["technical"],
            ["0013", "0017", "0033", "0048"],
        )
        html = render_html(analysis)
        self.assertIn("v22 × v23.1", html)
        self.assertIn("13/20", html)
        self.assertIn("0050", html)
        self.assertIn("possível sobreposição", html)
        retries = analysis["summary"]["technical_retries"]
        self.assertEqual(retries["recovered_valid_panels"], ["0017", "0048"])
        self.assertEqual(retries["recovered_majorities"], ["0048"])
        self.assertEqual(retries["persistent_technical_failures"], ["0013", "0033"])
        self.assertIn("Repetição dirigida dos quatro casos técnicos", html)


if __name__ == "__main__":
    unittest.main()
