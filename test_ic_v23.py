#!/usr/bin/env python3
"""Regressões determinísticas do catálogo material auditável da v23."""

import hashlib
import json
from pathlib import Path
import unittest

from openrouter_runner import load_contract as load_runner_contract, load_selection
from studio_cycle import version_of


ROOT = Path(__file__).parent


def load_contract(path):
    source = ROOT.joinpath(path).read_text(encoding="utf-8")
    source = source.split("class MediareCommitteeExperimental", 1)[0]
    namespace = {}
    exec(compile(source.replace("from genlayer import *", ""), path, "exec"), namespace)
    return namespace


V23 = load_contract("ic_v23.py")


def declaratory_fixture():
    pedido = {
        "id": "RP01", "autor": "requerente", "contra": "requerido",
        "modalidade": "declarar", "natureza": "declaratoria",
        "valor_pedido_centavos": None,
        "descricao": "Responsabilidade pelos vicios construtivos.",
    }
    decisao = {
        "pedido_id": "RP01", "decisao": "necessita_informacao",
        "pagador": None, "beneficiario": None, "valor_centavos": None,
        "fontes_favoraveis": ["PR"], "fontes_contrarias": ["RR"],
        "comentario": "O nexo permanece controvertido.",
        "sustentado": "O dano foi relatado.",
        "controvertido": "A causa foi contestada.",
        "lacuna": {
            "dimensao": "nexo", "pergunta": "Qual foi a causa?",
            "impacto": "A resposta define o alcance da declaracao.",
        },
        "opcao": {
            "tipo": "nao_monetaria", "proposta": "AUTO", "premissa": "AUTO",
            "ressalva": "AUTO", "fontes": ["PR", "RR"],
            "pagador": "requerido", "beneficiario": "requerente", "base": None,
            "criterio": {
                "tipo": "sem_calculo", "min_bps": None, "max_bps": None,
                "fonte": None, "trecho": None,
            },
        },
    }
    return pedido, decisao


class V23CatalogTests(unittest.TestCase):
    def test_identity_and_excluded_documentary_expansion(self):
        self.assertEqual(V23["VERSAO"], "23.1.0-experimental")
        self.assertNotIn("Uma base tambem pode vir de DR ou DD", V23["REGRAS_OPCAO"])
        self.assertIn("FALHAS_REVISAO", V23)
        self.assertIn("FALHAS_CATALOGO", V23)

    def test_manifest_hash_and_regression_first_selection(self):
        manifest = json.loads(ROOT.joinpath("v23_candidate.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256(ROOT.joinpath("ic_v23.py").read_bytes()).hexdigest()
        self.assertEqual(manifest["source_sha256"], digest)
        selection = json.loads(ROOT.joinpath("v23_cases.json").read_text(encoding="utf-8"))
        self.assertEqual(selection["case_ids"][:13], [
            "0008", "0017", "0023", "0026", "0029", "0033", "0035",
            "0001", "0015", "0018", "0020", "0024", "0031",
        ])
        self.assertEqual(len(selection["case_ids"]), 50)
        self.assertEqual(len(set(selection["case_ids"])), 50)
        self.assertEqual(selection["correction_cases"], 7)
        self.assertEqual(selection["preservation_cases"], 6)

    def test_snapshot_is_accepted_by_local_and_studio_runners(self):
        source = ROOT.joinpath("ic_v23.py")
        self.assertEqual(load_runner_contract(source)["VERSAO"], "23.1.0-experimental")
        self.assertEqual(version_of(source.read_bytes()), "23.1.0-experimental")
        self.assertEqual(len(load_selection(ROOT / "v23_cases.json")), 50)
        targeted = load_selection(ROOT / "v23_1_cases.json")
        self.assertEqual(targeted[:3], ["0033", "0024", "0001"])
        remainder = load_selection(ROOT / "v23_1_remaining_cases.json")
        self.assertEqual(remainder[:4], ["0018", "0020", "0024", "0031"])

    def test_closed_reviewer_schema_remains_fail_closed(self):
        catalog = {"pedidos": [{
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "pagar", "natureza": "principal",
            "valor_pedido_centavos": 100000, "descricao": "Restituicao.",
        }]}
        valid = {
            "catalogo": "completo",
            "catalogo_falhas": [],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        self.assertEqual(V23["_erro_revisao"](valid, catalog), "")
        invalid = {
            "catalogo": "completo",
            "catalogo_falhas": [],
            "pedidos": [{"pedido_id": "RP01", "falhas": ["DESCONHECIDA"]}],
        }
        self.assertEqual(
            V23["_erro_revisao"](invalid, catalog),
            "REVISAO_FALHAS_INVALIDAS",
        )

    def test_catalog_dissent_requires_source_anchored_material_defect(self):
        catalog = {"pedidos": [{
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "pagar", "natureza": "principal",
            "valor_pedido_centavos": 100000, "descricao": "Restituicao.",
        }]}
        bare = {
            "catalogo": "incompleto", "catalogo_falhas": [],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        self.assertEqual(
            V23["_erro_revisao"](bare, catalog),
            "REVISAO_CATALOGO_INCOMPLETO_EXIGE_FALHA",
        )
        anchored = {
            "catalogo": "incompleto",
            "catalogo_falhas": [{
                "tipo": "VALOR_INFERIDO", "pedido_id": "RP01", "fonte": "PR",
                "evidencia": "doze parcelas de R$ 100,00",
                "correcao": "Usar null no valor final e preservar a formula.",
            }],
            "pedidos": [{"pedido_id": "RP01", "falhas": ["PEDIDO"]}],
        }
        self.assertEqual(V23["_erro_revisao"](anchored, catalog), "")
        literal = json.loads(json.dumps(anchored))
        literal["catalogo_falhas"][0]["evidencia"] = "Total literalmente pedido: R$ 1.000,00"
        self.assertEqual(
            V23["_erro_revisao"](literal, catalog),
            "REVISAO_CATALOGO_VALOR_INFERIDO_CONTRADITO_PELA_EVIDENCIA",
        )
        V23["_normalizar_revisao_modelo"](literal, catalog)
        self.assertEqual(literal["catalogo"], "completo")
        self.assertEqual(literal["catalogo_falhas"], [])
        self.assertEqual(literal["pedidos"][0]["falhas"], [])
        anchored["catalogo_falhas"][0]["pedido_id"] = "RP01"
        catalog["pedidos"][0]["valor_pedido_centavos"] = None
        self.assertEqual(
            V23["_erro_revisao"](anchored, catalog),
            "REVISAO_CATALOGO_VALOR_INFERIDO_EXIGE_VALOR_NUMERICO",
        )
        V23["_normalizar_revisao_modelo"](anchored, catalog)
        self.assertEqual(anchored, {
            "catalogo": "completo", "catalogo_falhas": [],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        })
        self.assertEqual(V23["_erro_revisao"](anchored, catalog), "")

    def test_new_catalog_uses_rp_then_cr_and_rejects_legacy_rr(self):
        pedido = lambda pid, autor, contra: {
            "id": pid, "autor": autor, "contra": contra,
            "modalidade": "pagar", "natureza": "principal",
            "valor_pedido_centavos": None, "descricao": "Providencia autonoma.",
        }
        valid = {"pedidos": [
            pedido("RP01", "requerente", "requerido"),
            pedido("CR01", "requerido", "requerente"),
        ]}
        self.assertEqual(V23["_erro_catalogo"](valid), "")
        legacy = {"pedidos": [pedido("RR01", "requerido", "requerente")]}
        self.assertIn("FORMATO_RP01_OU_CR01", V23["_erro_catalogo"](legacy))

    def test_catalog_rules_merge_duplicates_without_omitting_remedies(self):
        prompt = V23["_prompt_catalogo"]("{}")
        self.assertIn("UNIDADE MATERIAL E NEGOCIAVEL DE PEDIDO", prompt)
        self.assertIn("Nao una providencias diferentes", prompt)
        self.assertIn("NAO criam CR", prompt)
        self.assertIn("MONTANTE FINAL LITERALMENTE EXPRESSO", prompt)
        self.assertIn("Pericia, prova", prompt)
        self.assertIn("manter a retencao integral", prompt)
        self.assertIn("ajuste/recalculo", prompt)
        review = V23["_prompt_revisao"]("{}", {"catalogo": {"pedidos": []}})
        self.assertIn("providencia expressa omitida", review)
        self.assertIn("nao estilo ou sinonimos", review)
        self.assertIn("catalogo_falhas", review)
        self.assertIn("VALOR_INFERIDO", review)
        self.assertIn("contraditorio", review)

    def test_declaratory_option_is_neutral_and_has_specific_wording(self):
        pedido, decisao = declaratory_fixture()
        body = json.dumps({
            "peticao_requerente": "Pedido declaratorio.",
            "resposta_requerido": "Pedido contestado.",
            "documentos_requerente": "Relato.",
            "documentos_requerido": "Relato.",
        })
        thesis = {"lente": "jurisprudencial", "pedidos": [decisao]}
        V23["_normalizar_tese_modelo"](
            thesis, {"pedidos": [pedido]}, "jurisprudencial", body, []
        )
        option = thesis["pedidos"][0]["opcao"]
        self.assertEqual((option["pagador"], option["beneficiario"]), (None, None))
        self.assertIn("reconhecem, por consenso", option["proposta"])
        self.assertNotIn("cumpr", option["proposta"].lower())
        self.assertEqual(V23["_erro_opcao"](option, pedido, decisao, body), "")

    def test_non_declaratory_options_keep_operational_parties(self):
        fazer = {
            "autor": "requerente", "contra": "requerido", "modalidade": "fazer",
        }
        pagar = {
            "autor": "requerido", "contra": "requerente", "modalidade": "pagar",
        }
        self.assertEqual(
            V23["_partes_opcao"](fazer, "nao_monetaria"),
            ("requerido", "requerente"),
        )
        self.assertEqual(
            V23["_partes_opcao"](pagar, "formula"),
            ("requerente", "requerido"),
        )


if __name__ == "__main__":
    unittest.main()
