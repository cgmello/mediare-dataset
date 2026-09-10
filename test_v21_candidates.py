#!/usr/bin/env python3
"""Deterministic regressions shared by the three isolated v21 candidates."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parent


def load_candidate(name):
    source = ROOT.joinpath(name).read_text(encoding="utf-8")
    source = source.split("class MediareCommitteeExperimental")[0]
    namespace = {}
    exec(compile(source.replace("from genlayer import *", ""), name, "exec"), namespace)
    return namespace


SCHEMA = load_candidate("ic_v21_schema.py")
CATALOG = load_candidate("ic_v21_catalog.py")
OPTIONS = load_candidate("ic_v21_options.py")


class V21SchemaTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {"pedidos": [{
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "pagar", "natureza": "principal",
            "valor_pedido_centavos": 100000, "descricao": "Restituicao do pagamento.",
        }]}

    def review(self, failures=None, catalog="completo"):
        return {"catalogo": catalog, "pedidos": [{"pedido_id": "RP01", "falhas": failures or []}]}

    def test_enum_schema_replaces_ambiguous_boolean_fields(self):
        self.assertEqual(SCHEMA["_erro_revisao"](self.review(), self.catalog), "")
        self.assertIn('"falhas":[]', SCHEMA["_prompt_revisao"]("{}", {"catalogo": self.catalog}))
        self.assertNotIn("pedido_fiel (", SCHEMA["_prompt_revisao"]("{}", {"catalogo": self.catalog}))

    def test_unknown_or_structured_failure_is_rejected(self):
        for failures in (["DESCONHECIDA"], [{"PEDIDO": True}], ["PEDIDO", "PEDIDO"]):
            with self.subTest(failures=failures):
                self.assertEqual(
                    SCHEMA["_erro_revisao"](self.review(failures), self.catalog),
                    "REVISAO_FALHAS_INVALIDAS",
                )

    def test_failure_codes_preserve_fail_closed_vote(self):
        leader = {"catalogo": self.catalog}
        with patch.dict(SCHEMA, {"_painel_valido": lambda _p: True,
                                 "_diag_consenso": lambda _code: None}):
            self.assertTrue(SCHEMA["_revisor_aprova"](leader, self.review()))
            self.assertFalse(SCHEMA["_revisor_aprova"](leader, self.review(["FONTES"])))
            self.assertFalse(SCHEMA["_revisor_aprova"](leader, self.review(catalog="incompleto")))


class V21CatalogTests(unittest.TestCase):
    def test_catalog_defines_material_request_identity(self):
        prompt = CATALOG["_prompt_catalogo"]("{}")
        self.assertIn("UNIDADE OBJETIVA DE PEDIDO", prompt)
        self.assertIn("nao cria RR", prompt)
        self.assertIn("Nao una providencias diferentes", prompt)

    def test_reviewer_ignores_style_but_not_omission(self):
        prompt = CATALOG["_prompt_revisao"]("{}", {"catalogo": {"pedidos": []}})
        self.assertIn("nao estilo ou sinonimos", prompt)
        self.assertIn("providencia expressa omitida", prompt)


class V21OptionsTests(unittest.TestCase):
    def test_declaratory_option_has_no_debtor_or_creditor(self):
        pedido = {
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "declarar", "natureza": "declaratoria",
            "valor_pedido_centavos": None, "descricao": "Responsabilidade pelos vicios.",
        }
        decisao = {
            "pedido_id": "RP01", "decisao": "necessita_informacao",
            "pagador": None, "beneficiario": None, "valor_centavos": None,
            "fontes_favoraveis": ["PR"], "fontes_contrarias": ["RR"],
            "comentario": "O nexo permanece controvertido.",
            "sustentado": "O dano foi relatado.", "controvertido": "A causa foi contestada.",
            "lacuna": {"dimensao": "nexo", "pergunta": "Qual foi a causa?",
                       "impacto": "A resposta define a responsabilidade."},
            "opcao": {
                "tipo": "nao_monetaria", "proposta": "AUTO", "premissa": "AUTO",
                "ressalva": "AUTO", "fontes": ["PR", "RR"], "pagador": "requerido",
                "beneficiario": "requerente", "base": None,
                "criterio": {"tipo": "sem_calculo", "min_bps": None, "max_bps": None,
                             "fonte": None, "trecho": None},
            },
        }
        thesis = {"lente": "jurisprudencial", "pedidos": [decisao]}
        body = json.dumps({"peticao_requerente": "Pedido declaratorio.",
                           "resposta_requerido": "Pedido contestado.",
                           "documentos_requerente": "Relato.", "documentos_requerido": "Relato."})
        OPTIONS["_normalizar_tese_modelo"](
            thesis, {"pedidos": [pedido]}, "jurisprudencial", body, []
        )
        option = thesis["pedidos"][0]["opcao"]
        self.assertEqual((option["pagador"], option["beneficiario"]), (None, None))
        self.assertIn("reconhecem", option["proposta"])
        self.assertNotIn("cumpr", option["proposta"].lower())
        self.assertEqual(OPTIONS["_erro_opcao"](option, pedido, decisao, body), "")

    def test_payment_and_source_safety_rules_remain_present(self):
        self.assertIn("DUPLA_CONTAGEM", OPTIONS["RISCOS"])
        self.assertIn("BASE_CITACAO_NAO_LOCALIZADA", OPTIONS["_erro_opcao"].__code__.co_consts)


class CandidateIdentityTests(unittest.TestCase):
    def test_versions_are_unique_and_v20_is_unchanged(self):
        self.assertEqual(SCHEMA["VERSAO"], "21.0.0-schema-experimental")
        self.assertEqual(CATALOG["VERSAO"], "21.0.0-catalog-experimental")
        self.assertEqual(OPTIONS["VERSAO"], "21.0.0-options-experimental")
        self.assertIn('VERSAO = "20.0.0-experimental"', ROOT.joinpath("ic_experimental.py").read_text())


if __name__ == "__main__":
    unittest.main()
