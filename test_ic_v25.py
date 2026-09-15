#!/usr/bin/env python3
"""Regressões da v25, com a semântica RP/CR protegida."""

import json
import hashlib
from pathlib import Path
import unittest

from openrouter_runner import load_contract
from studio_cycle import version_of


ROOT = Path(__file__).parent
V231 = load_contract(ROOT / "ic_v23.py")
V24 = load_contract(ROOT / "ic_v24.py")
V25 = load_contract(ROOT / "ic_v25.py")


def catalog():
    return {"pedidos": [{
        "id": "RP01", "autor": "requerente", "contra": "requerido",
        "modalidade": "pagar", "natureza": "principal",
        "valor_pedido_centavos": 3806419,
        "descricao": "Pagamento dos serviços hospitalares.",
    }]}


class V25TechnicalTests(unittest.TestCase):
    def test_version_and_runner_compatibility(self):
        source = ROOT / "ic_v25.py"
        self.assertEqual(V25["VERSAO"], "25.0.0-experimental")
        self.assertEqual(version_of(source.read_bytes()), "25.0.0-experimental")
        candidate = json.loads((ROOT / "v25_candidate.json").read_text(encoding="utf-8"))
        self.assertEqual(candidate["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(candidate["scope"], "technical-only")

    def test_rp_cr_catalog_semantics_are_byte_equivalent_at_prompt_boundary(self):
        body = json.dumps({
            "peticao_requerente": "Pedido de pagamento.",
            "resposta_requerido": "Contestação sem contrapedido.",
            "documentos_requerente": "Recibo.",
            "documentos_requerido": "Nenhum.",
        }, ensure_ascii=False)
        self.assertEqual(V25["_prompt_catalogo"](body), V24["_prompt_catalogo"](body))
        self.assertEqual(V25["_erro_catalogo"](catalog()), V24["_erro_catalogo"](catalog()))

    def test_double_count_without_conflicting_id_remains_fail_closed(self):
        thesis = {"lente": "auditora", "pedidos": [{
            "pedido_id": "RP01",
            "auditoria": {
                "resultado": "apta_com_ressalva",
                "riscos": ["DUPLA_CONTAGEM"],
                "motivo": "A cobertura alegada pode afastar a cobrança.",
                "conflitos_com": [],
            },
        }]}
        V25["_normalizar_tese_modelo"](thesis, catalog(), "auditora", "{}", [{}, {"pedidos": []}])
        audit = thesis["pedidos"][0]["auditoria"]
        self.assertEqual(audit["resultado"], "reformular")
        self.assertEqual(audit["riscos"], ["PREMISSA"])
        self.assertEqual(audit["conflitos_com"], [])
        self.assertEqual(V25["_erro_auditoria"](audit, {}, catalog(), catalog()["pedidos"][0]), "")

    def test_reformular_keeps_other_risks_and_drops_unanchored_double_count(self):
        thesis = {"lente": "auditora", "pedidos": [{
            "pedido_id": "RP01",
            "auditoria": {
                "resultado": "reformular",
                "riscos": ["DUPLA_CONTAGEM", "ESCOPO", "PREMISSA"],
                "motivo": "A base pode estar fora do escopo negociado.",
                "conflitos_com": [],
            },
        }]}
        V25["_normalizar_tese_modelo"](thesis, catalog(), "auditora", "{}", [{}, {"pedidos": []}])
        self.assertEqual(thesis["pedidos"][0]["auditoria"]["riscos"], ["ESCOPO", "PREMISSA"])

    def test_bare_pedido_objection_requires_structured_catalog_evidence(self):
        review = {
            "catalogo": "completo", "catalogo_falhas": [],
            "pedidos": [{"pedido_id": "RP01", "falhas": ["PEDIDO"]}],
        }
        self.assertEqual(
            V25["_erro_revisao"](review, catalog()),
            "REVISAO_PEDIDO_EXIGE_FALHA_CATALOGO_EVIDENCIADA",
        )
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [{
                "tipo": "GRANULARIDADE", "pedido_id": "RP01", "fonte": "PR",
                "evidencia": "Pagamento dos serviços hospitalares.",
                "correcao": "Separar providências materialmente autônomas.",
            }],
            "pedidos": [{"pedido_id": "RP01", "falhas": ["PEDIDO"]}],
        }
        self.assertEqual(V25["_erro_revisao"](review, catalog()), "")

    def test_normalized_impossible_value_objection_removes_only_pedido_code(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [{
                "tipo": "VALOR_INFERIDO", "pedido_id": "RP01", "fonte": "PR",
                "evidencia": "Total literalmente pedido: R$ 38.064,19",
                "correcao": "Remover o valor.",
            }],
            "pedidos": [{
                "pedido_id": "RP01", "falhas": ["PEDIDO", "CONCLUSAO"],
            }],
        }
        V25["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "completo")
        self.assertEqual(review["catalogo_falhas"], [])
        self.assertEqual(review["pedidos"][0]["falhas"], ["CONCLUSAO"])
        self.assertEqual(V25["_erro_revisao"](review, catalog()), "")

    def test_v25_keeps_the_v24_local_model_controls(self):
        config = json.loads((ROOT / "openrouter_models_v25.json").read_text(encoding="utf-8"))
        self.assertEqual(
            config["model_options"]["deepseek/deepseek-v4-pro"]["reasoning"],
            {"effort": "none"},
        )
        self.assertEqual(
            config["model_options"]["z-ai/glm-5.3"]["reasoning"],
            {"effort": "low"},
        )
        self.assertEqual(config["model_options"]["z-ai/glm-5.3"]["max_tokens"], 20000)

    def test_defensive_counterclaims_are_removed_but_restitution_is_kept(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 10000, "descricao": "Pagamento do débito."},
            {"id": "CR01", "autor": "requerido", "contra": "requerente", "modalidade": "declarar", "natureza": "declaratoria", "valor_pedido_centavos": None, "descricao": "Declaração de que a caução não foi paga."},
            {"id": "CR02", "autor": "requerido", "contra": "requerente", "modalidade": "pagar", "natureza": "outros", "valor_pedido_centavos": 5000, "descricao": "Restituição do saldo pago a maior."},
            {"id": "CR03", "autor": "requerido", "contra": "requerente", "modalidade": "declarar", "natureza": "declaratoria", "valor_pedido_centavos": None, "descricao": "Aplicação do índice correto no recálculo da dívida."},
        ]}
        V25["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01", "CR02"])

    def test_dependent_installment_request_is_removed(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 10000, "descricao": "Pagamento do débito."},
            {"id": "RP02", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": None, "descricao": "Subsidiariamente, parcelamento do débito."},
        ]}
        V25["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01"])


if __name__ == "__main__":
    unittest.main()
