#!/usr/bin/env python3

import json
import unittest

import evaluate_studio_ground_truth as evaluation


def request(tendency, interval=None):
    return {
        "pedido_id": "RP01",
        "tendencia": tendency,
        "faixa_quantificada_centavos": interval,
        "faixa_centavos": interval,
    }


class GroundTruthEvaluationTests(unittest.TestCase):
    def test_exact_outcome_requires_all_requests_resolved(self):
        self.assertEqual(
            evaluation.predict_exact_outcome([request("favoravel")]),
            "procedente",
        )
        self.assertEqual(
            evaluation.predict_exact_outcome([request("contraria")]),
            "improcedente",
        )
        self.assertEqual(
            evaluation.predict_exact_outcome([request("favoravel"), request("contraria")]),
            "parcialmente procedente",
        )
        self.assertIsNone(
            evaluation.predict_exact_outcome([request("favoravel"), request("sem_maioria")])
        )

    def test_binary_relief_is_conservative(self):
        self.assertEqual(
            evaluation.predict_relief([request("favoravel"), request("sem_maioria")]),
            "alguma tutela",
        )
        self.assertEqual(
            evaluation.predict_relief([request("contraria"), request("contraria")]),
            "nenhuma tutela",
        )
        self.assertIsNone(evaluation.predict_relief([request("sem_maioria")]))

    def test_quantified_range_sums_only_favorable_claims(self):
        self.assertEqual(
            evaluation.quantified_claimant_range([
                request("favoravel", [10000, 12000]),
                request("favoravel", [5000, 5000]),
                request("contraria", [0, 0]),
            ]),
            [150.0, 170.0],
        )
        self.assertIsNone(
            evaluation.quantified_claimant_range([request("favoravel", None)])
        )

    def test_extracts_only_embedded_panel(self):
        panel = {"catalogo": {"pedidos": []}, "consolidado": {"pedidos": []}}
        receipt = {
            "consensus_data": {
                "leader_receipt": [{
                    "eq_outputs": {
                        "0": {"payload": {"readable": json.dumps(panel)}}
                    }
                }]
            }
        }
        self.assertEqual(evaluation.extract_panel(receipt), panel)


if __name__ == "__main__":
    unittest.main()
