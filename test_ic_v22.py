#!/usr/bin/env python3
"""Regressões determinísticas da composição híbrida v22."""

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


V22 = load_contract("ic_v22.py")


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


class V22CompositionTests(unittest.TestCase):
    def test_identity_and_excluded_documentary_expansion(self):
        self.assertEqual(V22["VERSAO"], "22.0.0-experimental")
        self.assertNotIn("Uma base tambem pode vir de DR ou DD", V22["REGRAS_OPCAO"])
        self.assertIn("FALHAS_REVISAO", V22)

    def test_manifest_hash_and_regression_first_selection(self):
        manifest = json.loads(ROOT.joinpath("v22_candidate.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256(ROOT.joinpath("ic_v22.py").read_bytes()).hexdigest()
        self.assertEqual(manifest["source_sha256"], digest)
        selection = json.loads(ROOT.joinpath("v22_cases.json").read_text(encoding="utf-8"))
        self.assertEqual(len(selection["case_ids"]), 50)
        self.assertEqual(len(set(selection["case_ids"])), 50)
        self.assertEqual(selection["targeted_checkpoint"], 20)
        self.assertEqual(set(selection["case_ids"]), {f"{case:04d}" for case in range(1, 51)})

    def test_snapshot_is_accepted_by_local_and_studio_runners(self):
        source = ROOT.joinpath("ic_v22.py")
        self.assertEqual(load_runner_contract(source)["VERSAO"], "22.0.0-experimental")
        self.assertEqual(version_of(source.read_bytes()), "22.0.0-experimental")
        self.assertEqual(len(load_selection(ROOT / "v22_cases.json")), 50)

    def test_closed_reviewer_schema_remains_fail_closed(self):
        catalog = {"pedidos": [{
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "pagar", "natureza": "principal",
            "valor_pedido_centavos": 100000, "descricao": "Restituicao.",
        }]}
        valid = {
            "catalogo": "completo",
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        self.assertEqual(V22["_erro_revisao"](valid, catalog), "")
        invalid = {
            "catalogo": "completo",
            "pedidos": [{"pedido_id": "RP01", "falhas": ["DESCONHECIDA"]}],
        }
        self.assertEqual(
            V22["_erro_revisao"](invalid, catalog),
            "REVISAO_FALHAS_INVALIDAS",
        )

    def test_catalog_rules_merge_duplicates_without_omitting_remedies(self):
        prompt = V22["_prompt_catalogo"]("{}")
        self.assertIn("UNIDADE OBJETIVA DE PEDIDO", prompt)
        self.assertIn("Nao una providencias diferentes", prompt)
        self.assertIn("resultados autonomos", prompt)
        self.assertIn("nao cria RR", prompt)
        review = V22["_prompt_revisao"]("{}", {"catalogo": {"pedidos": []}})
        self.assertIn("providencia expressa omitida", review)
        self.assertIn("nao estilo ou sinonimos", review)

    def test_declaratory_option_is_neutral_and_has_specific_wording(self):
        pedido, decisao = declaratory_fixture()
        body = json.dumps({
            "peticao_requerente": "Pedido declaratorio.",
            "resposta_requerido": "Pedido contestado.",
            "documentos_requerente": "Relato.",
            "documentos_requerido": "Relato.",
        })
        thesis = {"lente": "jurisprudencial", "pedidos": [decisao]}
        V22["_normalizar_tese_modelo"](
            thesis, {"pedidos": [pedido]}, "jurisprudencial", body, []
        )
        option = thesis["pedidos"][0]["opcao"]
        self.assertEqual((option["pagador"], option["beneficiario"]), (None, None))
        self.assertIn("reconhecem, por consenso", option["proposta"])
        self.assertNotIn("cumpr", option["proposta"].lower())
        self.assertEqual(V22["_erro_opcao"](option, pedido, decisao, body), "")

    def test_non_declaratory_options_keep_operational_parties(self):
        fazer = {
            "autor": "requerente", "contra": "requerido", "modalidade": "fazer",
        }
        pagar = {
            "autor": "requerido", "contra": "requerente", "modalidade": "pagar",
        }
        self.assertEqual(
            V22["_partes_opcao"](fazer, "nao_monetaria"),
            ("requerido", "requerente"),
        )
        self.assertEqual(
            V22["_partes_opcao"](pagar, "formula"),
            ("requerente", "requerido"),
        )


if __name__ == "__main__":
    unittest.main()
