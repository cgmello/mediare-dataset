#!/usr/bin/env python3
"""Regressões da v28 para objetos autônomos e honorários contratuais."""

import json
import hashlib
from pathlib import Path
import unittest

from openrouter_runner import load_contract
from studio_cycle import version_of


ROOT = Path(__file__).parent
V231 = load_contract(ROOT / "ic_v23.py")
V24 = load_contract(ROOT / "ic_v24.py")
V28 = load_contract(ROOT / "ic_v28.py")


def catalog():
    return {"pedidos": [{
        "id": "RP01", "autor": "requerente", "contra": "requerido",
        "modalidade": "pagar", "natureza": "principal",
        "valor_pedido_centavos": 3806419,
        "descricao": "Pagamento dos serviços hospitalares.",
    }]}


class V28TechnicalTests(unittest.TestCase):
    def test_declaratory_concession_allows_null_poles(self):
        pedido = {
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "declarar", "natureza": "declaratoria",
            "valor_pedido_centavos": None, "descricao": "Declaração de rescisão.",
        }
        decisao = {
            "pedido_id": "RP01", "decisao": "conceder",
            "pagador": None, "beneficiario": None, "valor_centavos": 0,
            "fontes_favoraveis": ["PR"], "fontes_contrarias": [],
            "comentario": "A declaração é compatível com os fatos documentados.",
            "sustentado": "A rescisão foi comunicada.",
            "controvertido": "Nenhum identificado.",
            "lacuna": {"dimensao": "nenhuma", "pergunta": None, "impacto": None},
        }
        self.assertTrue(V28["_decisao_valida"](decisao, pedido))

    def test_monetary_concession_still_requires_poles(self):
        pedido = catalog()["pedidos"][0]
        decisao = {
            "pedido_id": "RP01", "decisao": "conceder",
            "pagador": None, "beneficiario": None, "valor_centavos": 1000,
            "fontes_favoraveis": ["PR"], "fontes_contrarias": [],
            "comentario": "Há suporte documental para o pagamento.",
            "sustentado": "O valor foi comprovado.",
            "controvertido": "Nenhum identificado.",
            "lacuna": {"dimensao": "nenhuma", "pergunta": None, "impacto": None},
        }
        self.assertFalse(V28["_decisao_valida"](decisao, pedido))

    def test_out_of_scope_may_have_no_follow_up_lacuna(self):
        pedido = {
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "fazer", "natureza": "obrigacao_fazer",
            "valor_pedido_centavos": None, "descricao": "Desocupação do imóvel.",
        }
        decisao = {
            "pedido_id": "RP01", "decisao": "fora_de_escopo",
            "pagador": None, "beneficiario": None, "valor_centavos": None,
            "fontes_favoraveis": ["RR"], "fontes_contrarias": [],
            "comentario": "O pedido já foi cumprido.",
            "sustentado": "A desocupação ocorreu.",
            "controvertido": "Nenhum identificado.",
            "lacuna": {"dimensao": "escopo", "pergunta": None, "impacto": None},
        }
        self.assertTrue(V28["_decisao_valida"](decisao, pedido))

    def test_version_and_runner_compatibility(self):
        source = ROOT / "ic_v28.py"
        self.assertEqual(V28["VERSAO"], "28.0.0-experimental")
        self.assertEqual(version_of(source.read_bytes()), "28.0.0-experimental")
        candidate = json.loads((ROOT / "v28_candidate.json").read_text(encoding="utf-8"))
        self.assertEqual(candidate["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(candidate["scope"], "autonomous charges and contractual fees")

    def test_catalog_prompt_excludes_procedural_relief_and_keeps_civil_penalty(self):
        body = json.dumps({
            "peticao_requerente": "Pedido de pagamento.",
            "resposta_requerido": "Contestação sem contrapedido.",
            "documentos_requerente": "Recibo.",
            "documentos_requerido": "Nenhum.",
        }, ensure_ascii=False)
        prompt = V28["_prompt_catalogo"](body)
        self.assertIn("expedicao de oficio", prompt)
        self.assertIn("multa civil ou contratual", prompt)
        self.assertIn("Em RP, objeto, valor, percentual e base devem vir da PR", prompt)
        self.assertIn("use necessita_informacao em vez de negar", V28["REGRAS_GERAIS"])
        self.assertIn("nao conceda um total parcial", V28["REGRAS_GERAIS"])
        self.assertEqual(V28["_erro_catalogo"](catalog()), V24["_erro_catalogo"](catalog()))

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
        V28["_normalizar_tese_modelo"](thesis, catalog(), "auditora", "{}", [{}, {"pedidos": []}])
        audit = thesis["pedidos"][0]["auditoria"]
        self.assertEqual(audit["resultado"], "reformular")
        self.assertEqual(audit["riscos"], ["PREMISSA"])
        self.assertEqual(audit["conflitos_com"], [])
        self.assertEqual(V28["_erro_auditoria"](audit, {}, catalog(), catalog()["pedidos"][0]), "")

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
        V28["_normalizar_tese_modelo"](thesis, catalog(), "auditora", "{}", [{}, {"pedidos": []}])
        self.assertEqual(thesis["pedidos"][0]["auditoria"]["riscos"], ["ESCOPO", "PREMISSA"])

    def test_bare_pedido_objection_requires_structured_catalog_evidence(self):
        review = {
            "catalogo": "completo", "catalogo_falhas": [],
            "pedidos": [{"pedido_id": "RP01", "falhas": ["PEDIDO"]}],
        }
        self.assertEqual(
            V28["_erro_revisao"](review, catalog()),
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
        self.assertEqual(V28["_erro_revisao"](review, catalog()), "")

    def test_normalizer_removes_pedido_code_not_anchored_to_same_id(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [{
                "tipo": "OMISSAO", "pedido_id": None, "fonte": "PR",
                "evidencia": "Restituição dos valores cobrados indevidamente.",
                "correcao": "Incluir pedido autônomo de restituição.",
            }],
            "pedidos": [{"pedido_id": "RP01", "falhas": ["PEDIDO"]}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "incompleto")
        self.assertEqual(len(review["catalogo_falhas"]), 1)
        self.assertEqual(review["pedidos"][0]["falhas"], [])
        self.assertEqual(V28["_erro_revisao"](review, catalog()), "")

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
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "completo")
        self.assertEqual(review["catalogo_falhas"], [])
        self.assertEqual(review["pedidos"][0]["falhas"], ["CONCLUSAO"])
        self.assertEqual(V28["_erro_revisao"](review, catalog()), "")

    def test_v28_keeps_the_v24_local_model_controls(self):
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
            {"id": "CR04", "autor": "requerido", "contra": "requerente", "modalidade": "declarar", "natureza": "declaratoria", "valor_pedido_centavos": None, "descricao": "Reconhecimento da inexigibilidade do débito."},
        ]}
        V28["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01", "CR02"])

    def test_dependent_installment_request_is_removed(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 10000, "descricao": "Pagamento do débito."},
            {"id": "RP02", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": None, "descricao": "Subsidiariamente, parcelamento do débito."},
        ]}
        V28["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01"])

    def test_accessories_of_same_monetary_claim_are_consolidated(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 576443, "descricao": "Quitação do débito de R$ 5.764,43 referente à venda da bomba."},
            {"id": "RP02", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": None, "descricao": "Pagamento do valor devido acrescido de correção monetária e juros."},
            {"id": "CR01", "autor": "requerido", "contra": "requerente", "modalidade": "pagar", "natureza": "outros", "valor_pedido_centavos": 83400, "descricao": "Restituição da diferença do reparo."},
        ]}
        V28["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01", "CR01"])

    def test_distinct_fine_utilities_and_future_rent_survive_consolidation(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 300000, "descricao": "Pagamento de três aluguéis vencidos, com multa moratória e juros."},
            {"id": "RP02", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "multa", "valor_pedido_centavos": None, "descricao": "Pagamento da multa contratual prevista na cláusula 11."},
            {"id": "RP03", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "outros", "valor_pedido_centavos": None, "descricao": "Pagamento dos encargos de CPFL, SAAE e IPTU."},
            {"id": "RP04", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": None, "descricao": "Pagamento dos aluguéis e encargos vincendos até a desocupação."},
        ]}
        V28["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01", "RP02", "RP03", "RP04"])

    def test_contractual_fees_survive_but_judicial_fees_are_removed(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "outros", "valor_pedido_centavos": 10578313, "descricao": "Pagamento de honorários advocatícios contratuais de 20% sobre o débito."},
            {"id": "RP02", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "outros", "valor_pedido_centavos": None, "descricao": "Pagamento de honorários advocatícios sucumbenciais fixados pelo juízo."},
        ]}
        V28["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01"])

    def test_reviewer_keeps_contractual_fee_omission(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [
                {"tipo": "OMISSAO", "pedido_id": None, "fonte": "PR", "evidencia": "Pagamento de honorários advocatícios contratuais.", "correcao": "Incluir a verba contratual autônoma."},
                {"tipo": "OMISSAO", "pedido_id": None, "fonte": "PR", "evidencia": "Honorários sucumbenciais fixados pelo juízo.", "correcao": "Incluir a verba judicial."},
            ],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "incompleto")
        self.assertEqual(len(review["catalogo_falhas"]), 1)
        self.assertIn("contratuais", review["catalogo_falhas"][0]["evidencia"])

    def test_reviewer_drops_defensive_adjustments_as_counterclaims(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [
                {"tipo": "OMISSAO", "pedido_id": None, "fonte": "RR", "evidencia": "Que eventual retenção seja limitada a patamar justo.", "correcao": "Incluir limitação da retenção."},
                {"tipo": "OMISSAO", "pedido_id": None, "fonte": "RR", "evidencia": "Que as multas contratuais sejam afastadas.", "correcao": "Incluir afastamento das multas."},
                {"tipo": "OMISSAO", "pedido_id": None, "fonte": "RR", "evidencia": "Que a taxa de ocupação, se devida, tenha valor razoável.", "correcao": "Incluir fixação da taxa de ocupação."},
            ],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "completo")
        self.assertEqual(review["catalogo_falhas"], [])

    def test_reviewer_drops_omission_with_invented_calculated_anchor(self):
        body = json.dumps({
            "peticao_requerente": "Parcela anual de R$ 100.000,00 e mensal de R$ 15.000,00. Buscamos a rescisão.",
            "resposta_requerido": "Contestação sem contrapedido.",
            "documentos_requerente": "Contrato.",
            "documentos_requerido": "Nenhum.",
        }, ensure_ascii=False)
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [{
                "tipo": "OMISSAO", "pedido_id": None, "fonte": "PR",
                "evidencia": "Pagamento de R$ 115.000,00 em parcelas vencidas.",
                "correcao": "Incluir pagamento calculado das parcelas.",
            }],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog(), None, body)
        self.assertEqual(review["catalogo"], "completo")
        self.assertEqual(review["catalogo_falhas"], [])

    def test_reviewer_drops_non_actionable_granularity_objections(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [
                {"tipo": "GRANULARIDADE", "pedido_id": "RP01", "fonte": "PR", "evidencia": "Pagamento do débito e encargos.", "correcao": "Separar acessórios ou consolidar explicitamente."},
                {"tipo": "GRANULARIDADE", "pedido_id": "RP01", "fonte": "PR", "evidencia": "Pagamento do débito.", "correcao": "Clarificar a fração de responsabilidade do requerente."},
            ],
            "pedidos": [{"pedido_id": "RP01", "falhas": ["PEDIDO"]}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "completo")
        self.assertEqual(review["catalogo_falhas"], [])
        self.assertEqual(review["pedidos"][0]["falhas"], [])

    def test_contractual_fee_with_listed_contract_becomes_information_gap(self):
        body = json.dumps({
            "peticao_requerente": "Pagamento de honorários contratuais.",
            "resposta_requerido": "Contesto a incidência da verba.",
            "documentos_requerente": "Contrato de locação e memória de cálculo.",
            "documentos_requerido": "Nenhum.",
        }, ensure_ascii=False)
        cat = {"pedidos": [{
            "id": "RP01", "autor": "requerente", "contra": "requerido",
            "modalidade": "pagar", "natureza": "outros", "valor_pedido_centavos": 10000,
            "descricao": "Pagamento de honorários advocatícios contratuais.",
        }]}
        thesis = {"lente": "probatoria", "pedidos": [{
            "pedido_id": "RP01", "decisao": "negar", "pagador": None,
            "beneficiario": None, "valor_centavos": 0,
            "fontes_favoraveis": ["PR", "DR"], "fontes_contrarias": ["RR"],
            "comentario": "A verba não é devida.", "sustentado": "Há alegação.",
            "controvertido": "A incidência é contestada.",
            "lacuna": {"dimensao": "nenhuma", "pergunta": None, "impacto": None},
        }]}
        V28["_normalizar_tese_modelo"](thesis, cat, "probatoria", body, [])
        decision = thesis["pedidos"][0]
        self.assertEqual(decision["decisao"], "necessita_informacao")
        self.assertIsNone(decision["valor_centavos"])
        self.assertEqual(decision["lacuna"]["dimensao"], "escopo")

    def test_defensive_omission_is_not_a_new_counterclaim(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [{
                "tipo": "OMISSAO", "pedido_id": None, "fonte": "RR",
                "evidencia": "Reconhecimento da inexigibilidade do débito.",
                "correcao": "Incluir contrapedido de inexigibilidade.",
            }],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "completo")
        self.assertEqual(review["catalogo_falhas"], [])

    def test_defensive_compensation_omission_is_not_a_counterclaim(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [{
                "tipo": "OMISSAO", "pedido_id": None, "fonte": "RR",
                "evidencia": "Compensação do valor devido com o gasto de reparo.",
                "correcao": "Incluir pedido contraposto autônomo de compensação/abatimento do débito.",
            }],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "completo")
        self.assertEqual(review["catalogo_falhas"], [])

    def test_procedural_requests_are_removed_but_party_relief_and_penalty_remain(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "multa", "valor_pedido_centavos": 50000, "descricao": "Pagamento de multa civil expressamente requerida."},
            {"id": "RP02", "autor": "requerente", "contra": "requerido", "modalidade": "fazer", "natureza": "obrigacao_fazer", "valor_pedido_centavos": None, "descricao": "Expedição de ofícios ao Ministério Público e ao CRECI."},
            {"id": "CR01", "autor": "requerido", "contra": "requerente", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 10000, "descricao": "Liberação do valor depositado em favor do requerido."},
            {"id": "CR02", "autor": "requerido", "contra": "requerente", "modalidade": "pagar", "natureza": "outros", "valor_pedido_centavos": None, "descricao": "Condenação por litigância de má-fé, custas processuais e honorários advocatícios."},
        ]}
        V28["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01", "CR01"])

    def test_procedural_omission_is_ignored_but_civil_penalty_omission_remains(self):
        review = {
            "catalogo": "incompleto",
            "catalogo_falhas": [
                {"tipo": "OMISSAO", "pedido_id": None, "fonte": "PR", "evidencia": "Expedição de ofícios ao MP e ao CRECI.", "correcao": "Incluir expedição de ofícios."},
                {"tipo": "OMISSAO", "pedido_id": None, "fonte": "PR", "evidencia": "Pagamento da multa civil.", "correcao": "Incluir a multa civil como pedido autônomo."},
            ],
            "pedidos": [{"pedido_id": "RP01", "falhas": []}],
        }
        V28["_normalizar_revisao_modelo"](review, catalog())
        self.assertEqual(review["catalogo"], "incompleto")
        self.assertEqual(len(review["catalogo_falhas"]), 1)
        self.assertIn("multa civil", review["catalogo_falhas"][0]["evidencia"].casefold())

    def test_catalog_nulls_arithmetic_value_but_keeps_literal_value(self):
        body = json.dumps({
            "peticao_requerente": "Contrato de R$ 20.500,00; adiantamento de R$ 12.300,00.",
            "resposta_requerido": "Sem contrapedido.",
        }, ensure_ascii=False)
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 820000, "descricao": "Restituição do saldo calculado."},
            {"id": "RP02", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 1230000, "descricao": "Restituição do adiantamento literal."},
        ]}
        V28["_normalizar_catalogo"](value, body)
        self.assertIsNone(value["pedidos"][0]["valor_pedido_centavos"])
        self.assertEqual(value["pedidos"][1]["valor_pedido_centavos"], 1230000)

    def test_catalog_accepts_dot_decimal_literal_from_synthetic_cases(self):
        body = json.dumps({
            "peticao_requerente": "Caução de R$ 6000.00 e multa de R$ 11000.00.",
            "resposta_requerido": "Sem contrapedido.",
        }, ensure_ascii=False)
        self.assertEqual(V28["_valores_monetarios_catalogo"](body, "RP01"), {600000, 1100000})

    def test_defensive_retention_and_dependent_installment_are_removed(self):
        value = {"pedidos": [
            {"id": "RP01", "autor": "requerente", "contra": "requerido", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": 600000, "descricao": "Devolução da caução."},
            {"id": "CR01", "autor": "requerido", "contra": "requerente", "modalidade": "declarar", "natureza": "declaratoria", "valor_pedido_centavos": None, "descricao": "Reconhecimento da legitimidade da retenção da caução."},
            {"id": "CR02", "autor": "requerido", "contra": "requerente", "modalidade": "pagar", "natureza": "principal", "valor_pedido_centavos": None, "descricao": "Parcelamento do débito em razão de dificuldades financeiras."},
        ]}
        V28["_normalizar_catalogo"](value)
        self.assertEqual([p["id"] for p in value["pedidos"]], ["RP01"])

    def test_audit_unknown_risk_and_invalid_conflict_fail_closed(self):
        thesis = {"lente": "auditora", "pedidos": [{
            "pedido_id": "RP01",
            "auditoria": {
                "resultado": "reformular", "riscos": ["RISCO_INVENTADO", "DUPLA_CONTAGEM"],
                "motivo": "A opção precisa ser revista.", "conflitos_com": ["RP99"],
            },
        }]}
        V28["_normalizar_tese_modelo"](thesis, catalog(), "auditora", "{}", [{}, {"pedidos": []}])
        audit = thesis["pedidos"][0]["auditoria"]
        self.assertEqual(audit["resultado"], "reformular")
        self.assertEqual(audit["riscos"], ["OUTRO"])
        self.assertEqual(audit["conflitos_com"], [])
        self.assertEqual(V28["_erro_auditoria"](audit, {}, catalog(), catalog()["pedidos"][0]), "")


if __name__ == "__main__":
    unittest.main()
