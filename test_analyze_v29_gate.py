import unittest

from analyze_v29_gate import direction, expected_direction, percent


class AnalyzeV29GateTest(unittest.TestCase):
    def test_direction_maps_panel_tendencies(self):
        self.assertEqual(direction({"tendencia": "favoravel"}), "conceder")
        self.assertEqual(direction({"tendencia": "contraria"}), "negar")
        self.assertEqual(direction({"tendencia": "sem_maioria"}), "necessita_informacao")

    def test_indispensable_audit_requires_information(self):
        self.assertEqual(
            expected_direction({
                "suficiencia_entrada": "indispensavel_ausente",
                "direcao_segura": "negar",
            }),
            "necessita_informacao",
        )

    def test_avoidable_audit_uses_safe_direction(self):
        self.assertEqual(
            expected_direction({
                "suficiencia_entrada": "util_mas_nao_indispensavel",
                "direcao_segura": "conceder",
            }),
            "conceder",
        )

    def test_percent(self):
        self.assertEqual(percent(48, 98), 49.0)
        self.assertIsNone(percent(0, 0))


if __name__ == "__main__":
    unittest.main()
