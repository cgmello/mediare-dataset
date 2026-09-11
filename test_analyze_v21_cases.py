import unittest

from analyze_v21_cases import error_origin, panel_details, transition


def row(*, valid=True, label="APTO_INTEGRAL", agree=True, studio="MAJORITY_AGREE", diagnostic=None):
    return {
        "leader_error": None if valid else "LLM_INVALID_PANEL",
        "leader_impression": {"label": label} if valid else None,
        "leader_panel": {"consolidado": {"pedidos": []}} if valid else None,
        "local_consensus": "LOCAL_MAJORITY_AGREE" if agree else "LOCAL_MAJORITY_DISAGREE",
        "studio_baseline": {"consensus": studio},
        "reviewer_agree": 3 if diagnostic is None else 2,
        "reviewer_total": 4,
        "reviewers": [] if diagnostic is None else [{"vote": "disagree", "diagnostic": diagnostic}],
    }


class AnalyzeV21CasesTests(unittest.TestCase):
    def test_error_origin_separates_generation_from_local_rule(self):
        self.assertEqual(
            error_origin("LLM_INVALID_PANEL:lente=probatoria:1=CHAMADA_RunnerError"),
            "probatoria/geração/API",
        )
        self.assertEqual(
            error_origin("LLM_INVALID_PANEL:lente=auditora:1=RP01.auditoria:RISCOS_INVALIDOS"),
            "auditora/regra local",
        )

    def test_recovered_panel_is_improvement(self):
        base = panel_details(row(valid=False, agree=False))
        candidate = panel_details(row(valid=True, agree=True))
        result = transition(base, candidate)
        self.assertEqual(result["verdict"], "melhora")
        self.assertIn("painel válido recuperado", result["positive"])

    def test_gain_and_loss_is_mixed(self):
        base = panel_details(row(diagnostic="LLM_INVALID_PANEL:review"))
        candidate = panel_details(row(agree=False))
        result = transition(base, candidate)
        self.assertEqual(result["verdict"], "misto")
        self.assertTrue(any("erros de formato" in value for value in result["positive"]))
        self.assertIn("maioria local perdida", result["negative"])

    def test_declaratory_option_tracks_neutral_parties(self):
        value = row()
        value["leader_panel"]["consolidado"]["pedidos"] = [{
            "status": "passou",
            "modalidade": "declarar",
            "negociacao": {"opcao": {
                "tipo": "nao_monetaria", "pagador": None, "beneficiario": None,
            }},
        }]
        details = panel_details(value)
        self.assertEqual(details["declaratory_options"], 1)
        self.assertEqual(details["declaratory_neutral_parties"], 1)


if __name__ == "__main__":
    unittest.main()
