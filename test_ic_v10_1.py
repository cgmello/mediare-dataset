#!/usr/bin/env python3
"""Testes unitarios puros da consolidacao e equivalencia da v10.1."""

import unittest
import json
from pathlib import Path
from types import SimpleNamespace


def carregar():
    src = Path(__file__).with_name("ic_v10_1.py").read_text(encoding="utf-8")
    prefixo = src.split("class MediareCommitteeV101")[0]
    prefixo = prefixo.replace("from genlayer import *", "")
    ns = {}
    exec(compile(prefixo, "ic_v10_1.py", "exec"), ns)
    return ns


IC = carregar()


def catalogo():
    return {
        "pedidos": [
            {
                "id": "RP01",
                "autor": "requerente",
                "contra": "requerido",
                "modalidade": "pagar",
                "natureza": "principal",
                "valor_pedido_centavos": 120000,
                "descricao": "ressarcimento do reparo",
            },
            {
                "id": "RP02",
                "autor": "requerente",
                "contra": "requerido",
                "modalidade": "pagar",
                "natureza": "multa",
                "valor_pedido_centavos": 50000,
                "descricao": "multa contratual",
            },
        ]
    }


def decisao(pid, decisao, valor=0, comentario="Conclusao fundamentada."):
    conceder = decisao == "conceder"
    return {
        "pedido_id": pid,
        "decisao": decisao,
        "pagador": "requerido" if conceder else None,
        "beneficiario": "requerente" if conceder else None,
        "valor_centavos": None if decisao in ("necessita_informacao", "fora_de_escopo") else valor,
        "fontes_favoraveis": ["DR"] if conceder else [],
        "fontes_contrarias": ["DD"] if not conceder else [],
        "comentario": comentario,
    }


def tese(nome, p1, p2):
    return {"lente": nome, "pedidos": [p1, p2]}


def painel(cat, teses):
    return {
        "versao": IC["VERSAO"],
        "catalogo": cat,
        "teses": teses,
        "consolidado": IC["_consolidar"](cat, teses),
    }


def contrato_simulado(pedir, validar=False):
    """Executa o wrapper com gl simulado; nao substitui um teste no Studio."""
    contagem = {"ep": 0}
    class Retorno:
        def __init__(self, obj):
            self.calldata = obj
    def run_nondet(lider, validador):
        contagem["ep"] += 1
        obj = lider()
        transportado = json.loads(json.dumps(obj))
        if validar and not validador(Retorno(transportado)):
            raise RuntimeError("DISAGREE_SIMULADO")
        return transportado
    gl = SimpleNamespace(
        Contract=object,
        public=SimpleNamespace(write=lambda f: f, view=lambda f: f),
        vm=SimpleNamespace(UserError=ValueError, Return=Retorno, run_nondet_unsafe=run_nondet),
        nondet=SimpleNamespace(
            exec_prompt=pedir,
            web=SimpleNamespace(get=lambda url: SimpleNamespace(body=b'{"documentos": {}}')),
        ),
    )
    src = Path(__file__).with_name("ic_v10_1.py").read_text(encoding="utf-8")
    ns = {"gl": gl}
    exec(compile(src.replace("from genlayer import *", ""), "ic_v10_1.py", "exec"), ns)
    return ns["MediareCommitteeV101"](), contagem


class V101Tests(unittest.TestCase):
    def painel_simples(self, tipos, valores=None, modalidade="pagar"):
        cat = catalogo()
        cat["pedidos"] = cat["pedidos"][:1]
        cat["pedidos"][0]["modalidade"] = modalidade
        if modalidade == "declarar":
            cat["pedidos"][0]["natureza"] = "declaratoria"
        valores = valores or [0, 0, 0]
        teses = [
            {"lente": nome, "pedidos": [decisao("RP01", tipo, valor)]}
            for (nome, _), tipo, valor in zip(IC["LENTES"], tipos, valores)
        ]
        return painel(cat, teses)

    def test_tres_abstencoes_nao_produzem_faixa_zero(self):
        p = self.painel_simples(["necessita_informacao"] * 3)
        self.assertTrue(IC["_painel_valido"](p))
        c = p["consolidado"]
        self.assertIsNone(c["faixa_total_centavos"])
        self.assertEqual(c["estado_valor_total"], "indeterminado")
        self.assertTrue(all(v is None for v in c["totais_por_lente_centavos"].values()))
        self.assertIsNone(c["pedidos"][0]["faixa_centavos"])
        termo = IC["_render_termo_opcao"]("0005", p)
        self.assertIn("valor indeterminado", termo)
        self.assertNotIn("R$ 0,00", termo)

    def test_tres_negacoes_continuam_com_zero_real(self):
        p = self.painel_simples(["negar"] * 3)
        self.assertEqual(p["consolidado"]["faixa_total_centavos"], [0, 0])
        self.assertIn("R$ 0,00 a R$ 0,00", IC["_render_termo_opcao"]("0005", p))

    def test_abstencao_nao_vira_zero_entre_concessoes(self):
        p = self.painel_simples(["conceder", "necessita_informacao", "conceder"], [100000, 0, 120000])
        c = p["consolidado"]
        item = c["pedidos"][0]
        self.assertIsNone(item["faixa_centavos"])
        self.assertEqual(item["faixa_quantificada_centavos"], [100000, 120000])
        self.assertNotIn("ZERO_VERSUS_POSITIVO", item["flags"])
        self.assertIsNone(c["faixa_total_centavos"])
        self.assertEqual(c["totais_por_lente_centavos"]["probatoria"], 100000)
        termo = IC["_render_termo_opcao"]("0005", p)
        self.assertIn("parciais; nao formam faixa completa", termo)
        self.assertNotIn("R$ 0,00", termo)

    def test_zero_e_positivo_reais_preservam_flag_com_abstencao(self):
        p = self.painel_simples(["conceder", "necessita_informacao", "negar"], [100000, 0, 0])
        self.assertIn("ZERO_VERSUS_POSITIVO", p["consolidado"]["pedidos"][0]["flags"])

    def test_ep_distingue_abstencao_negacao_e_concessao(self):
        info = self.painel_simples(["necessita_informacao"] * 3)
        zero = self.painel_simples(["negar"] * 3)
        positivo = self.painel_simples(["conceder"] * 3, [100000] * 3)
        self.assertTrue(IC["_paineis_equivalentes"](info, info))
        for a, b in ((info, zero), (info, positivo), (zero, positivo)):
            self.assertFalse(IC["_paineis_equivalentes"](a, b))
            self.assertFalse(IC["_paineis_equivalentes"](b, a))
        self.assertFalse(IC["_faixas_equivalentes"](None, [0, 0]))

    def test_ep_compara_valores_parciais_mesmo_com_total_indeterminado(self):
        a = self.painel_simples(["conceder", "necessita_informacao", "conceder"], [100000, 0, 100000])
        b = self.painel_simples(["conceder", "necessita_informacao", "conceder"], [200000, 0, 200000])
        self.assertFalse(IC["_paineis_equivalentes"](a, b))

    def test_declaratorio_pendente_nao_invalida_total_monetario(self):
        cat = catalogo()
        cat["pedidos"][1].update(modalidade="declarar", natureza="declaratoria")
        teses = [tese(nome, decisao("RP01", "conceder", 100000), decisao("RP02", "necessita_informacao"))
                 for nome, _ in IC["LENTES"]]
        p = painel(cat, teses)
        self.assertTrue(IC["_painel_valido"](p))
        self.assertEqual(p["consolidado"]["faixa_total_centavos"], [100000, 100000])
        self.assertEqual(p["consolidado"]["pedidos"][1]["estado_valor"], "nao_monetario")

    def test_fora_de_escopo_e_pedido_nao_monetario_nao_sao_faixa_zero(self):
        for p in (
            self.painel_simples(["fora_de_escopo"] * 3),
            self.painel_simples(["conceder"] * 3, modalidade="declarar"),
        ):
            self.assertTrue(IC["_painel_valido"](p))
            self.assertIsNone(p["consolidado"]["faixa_total_centavos"])
            self.assertNotIn("R$ 0,00", IC["_render_termo_opcao"]("0005", p))

    def test_schema_rejeita_zero_para_indeterminado_e_null_para_negado(self):
        pedido = catalogo()["pedidos"][0]
        for tipo, valor in (("necessita_informacao", 0), ("fora_de_escopo", 0), ("negar", None), ("conceder", None)):
            d = decisao("RP01", tipo)
            d["valor_centavos"] = valor
            self.assertFalse(IC["_decisao_valida"](d, pedido))
        d = decisao("RP01", "necessita_informacao")
        del d["valor_centavos"]
        self.assertFalse(IC["_decisao_valida"](d, pedido))

    def test_pipeline_de_abstencoes_gera_termo_em_quatro_chamadas(self):
        p = self.painel_simples(["necessita_informacao"] * 3)
        respostas = [p["catalogo"]] + p["teses"]
        def pedir(*args, **kwargs):
            return json.dumps(respostas.pop(0))
        resultado = IC["_painel_de"](pedir, "caso resumido")
        self.assertTrue(IC["_painel_valido"](resultado))
        self.assertEqual(respostas, [])
        self.assertNotIn("R$ 0,00", IC["_render_termo_opcao"]("0005", resultado))

    def test_fluxo_completo_exige_transporte_textual_em_todas_as_chamadas(self):
        for prefixo, sufixo in (("", ""), (" \n", "\n ")):
            respostas = [catalogo()] + [
                tese(nome, decisao("RP01", "conceder", 100000), decisao("RP02", "negar"))
                for nome, _ in IC["LENTES"]
            ]
            chamadas = []
            def pedir(prompt, **kwargs):
                self.assertEqual(kwargs, {"response_format": "text"})
                self.assertIn("sem cercas Markdown", prompt)
                chamadas.append(prompt)
                obj = respostas.pop(0)
                return prefixo + json.dumps(obj) + sufixo
            resultado = IC["_painel_de"](pedir, "resumos anonimizados")
            self.assertTrue(IC["_painel_valido"](resultado))
            self.assertEqual(len(chamadas), 4)

    def test_retry_informa_campo_e_preserva_valor_da_nova_resposta(self):
        boa = tese("probatoria", decisao("RP01", "conceder", 100000), decisao("RP02", "negar"))
        ruim = json.loads(json.dumps(boa))
        ruim["pedidos"][0]["comentario"] = "x" * 241
        respostas = [ruim, boa]
        prompts = []
        def pedir(prompt, **kwargs):
            prompts.append(prompt)
            return json.dumps(respostas.pop(0))
        resultado = IC["_tese_de"](pedir, "probatoria", "instrucao", "caso", catalogo())
        self.assertIn("RP01.comentario:TEXTO_1_A_240", prompts[1])
        self.assertEqual(resultado["pedidos"][0]["valor_centavos"], 100000)

    def test_erro_final_identifica_lente_pedido_campo_e_tentativas(self):
        ruim = tese("auditora", decisao("RP01", "conceder", 100000), decisao("RP02", "negar"))
        ruim["pedidos"][0]["valor_centavos"] = "100000"
        with self.assertRaisesRegex(ValueError, "LLM_INVALID_PANEL:lente=auditora:1=RP01.valor_centavos.*2=RP01.valor_centavos"):
            IC["_tese_de"](lambda *a, **k: json.dumps(ruim), "auditora", "instrucao", "caso", catalogo())

    def test_fontes_com_objetos_sao_rejeitadas_sem_typeerror(self):
        self.assertFalse(IC["_lista_fontes_valida"]([{"id": "DR"}]))
        self.assertFalse(IC["_lista_fontes_valida"]([["DR"]]))

    def test_falha_catalogo_interrompe_antes_das_lentes(self):
        chamadas = []
        def pedir(prompt, **kwargs):
            chamadas.append(prompt)
            return '{"pedidos": []}'
        with self.assertRaisesRegex(ValueError, "LLM_INVALID_PANEL:catalogo:1=pedidos:QUANTIDADE"):
            IC["_painel_de"](pedir, "caso")
        self.assertEqual(len(chamadas), 2)

    def test_erro_provedor_preserva_tipo_sem_expor_mensagem(self):
        def pedir(*args, **kwargs):
            raise RuntimeError("mensagem privada do provedor")
        with self.assertRaises(ValueError) as ctx:
            IC["_catalogo_de"](pedir, "caso")
        self.assertIn("CHAMADA_RuntimeError", str(ctx.exception))
        self.assertNotIn("mensagem privada", str(ctx.exception))

    def test_json_quebrado_nao_e_reparado_ou_transformado_em_zero(self):
        with self.assertRaisesRegex(ValueError, "JSON_INVALIDO"):
            IC["_catalogo_de"](lambda *a, **k: '{"pedidos":', "caso")

    def test_leitura_preserva_null_explicito_e_ausencia_sem_coercao(self):
        obj = IC["_ler_objeto_json"](
            lambda *a, **k: '{"nulo": null, "zero": 0, "texto": "null", "itens": [null]}',
            "caso",
        )
        self.assertIn("nulo", obj)
        self.assertIsNone(obj["nulo"])
        self.assertNotIn("ausente", obj)
        self.assertEqual(obj["zero"], 0)
        self.assertEqual(obj["texto"], "null")
        self.assertEqual(obj["itens"], [None])

    def test_leitura_rejeita_objetos_ja_convertidos_pelo_transporte(self):
        for valor in ({"campo": None}, [], None, 123, True):
            with self.subTest(valor=valor), self.assertRaisesRegex(ValueError, "RESPOSTA_DEVE_SER_TEXTO"):
                IC["_ler_objeto_json"](lambda *a, **k: valor, "caso")

    def test_leitura_rejeita_raizes_que_nao_sao_objetos(self):
        for bruto in ('null', '[]', 'true', '0', '"texto"'):
            with self.subTest(bruto=bruto), self.assertRaisesRegex(ValueError, "RAIZ_DEVE_SER_OBJETO"):
                IC["_ler_objeto_json"](lambda *a, **k: bruto, "caso")

    def test_leitura_nao_remove_markdown_nem_aceita_json_nao_padrao(self):
        for bruto in ('```json\n{}\n```', 'Resposta: {}', '{} {}',
                      '{"valor": NaN}', '{"valor": Infinity}', '{"valor": -Infinity}'):
            with self.subTest(bruto=bruto), self.assertRaisesRegex(ValueError, "JSON_INVALIDO"):
                IC["_ler_objeto_json"](lambda *a, **k: bruto, "caso")

    def test_diagnostico_distingue_ausencia_tipo_e_incompatibilidade(self):
        for tipo, valor, esperado in (
            ("necessita_informacao", 0, "ESPERADO_NULL;decisao=necessita_informacao;recebido=INTEIRO"),
            ("fora_de_escopo", "null", "ESPERADO_NULL;decisao=fora_de_escopo;recebido=TEXTO"),
            ("negar", None, "ESPERADO_INTEIRO;decisao=negar;recebido=NULL"),
            ("negar", 1, "NEGACAO_EXIGE_ZERO;decisao=negar;recebido=INTEIRO"),
            ("conceder", "123", "ESPERADO_INTEIRO;decisao=conceder;recebido=TEXTO"),
            ("conceder", True, "ESPERADO_INTEIRO;decisao=conceder;recebido=BOOLEANO"),
            ("conceder", 123.0, "ESPERADO_INTEIRO;decisao=conceder;recebido=DECIMAL"),
            ("conceder", -1, "FORA_DO_LIMITE_0_A_1000000000000;decisao=conceder;recebido=INTEIRO"),
            ("conceder", 1_000_000_000_001, "FORA_DO_LIMITE_0_A_1000000000000;decisao=conceder;recebido=INTEIRO"),
        ):
            with self.subTest(tipo=tipo, valor=valor):
                d = decisao("RP01", tipo)
                d["valor_centavos"] = valor
                obj = tese("probatoria", d, decisao("RP02", "negar"))
                self.assertEqual(IC["_erro_tese"](obj, catalogo(), "probatoria"), "RP01.valor_centavos:" + esperado)
                self.assertFalse(IC["_decisao_valida"](d, catalogo()["pedidos"][0]))
        for tipo in IC["DECISOES"]:
            d = decisao("RP01", tipo)
            del d["valor_centavos"]
            self.assertEqual(IC["_erro_valor_decisao"](d), "CAMPO_AUSENTE;decisao=" + tipo)

    def test_diagnostico_identifica_valor_incompativel_com_modalidade(self):
        for modalidade, valor, erro in (
            ("pagar", 0, "CONCESSAO_MONETARIA_EXIGE_POSITIVO"),
            ("declarar", 100, "CONCESSAO_NAO_MONETARIA_EXIGE_ZERO"),
        ):
            cat = catalogo()
            cat["pedidos"][0]["modalidade"] = modalidade
            obj = tese("probatoria", decisao("RP01", "conceder", valor), decisao("RP02", "negar"))
            self.assertEqual(IC["_erro_tese"](obj, cat, "probatoria"), "RP01.valor_centavos:" + erro)

    def test_retry_corrige_ausencia_para_null_sem_mudar_decisao(self):
        boa = tese("probatoria", decisao("RP01", "necessita_informacao"), decisao("RP02", "negar"))
        ruim = json.loads(json.dumps(boa))
        del ruim["pedidos"][0]["valor_centavos"]
        respostas = [ruim, boa]
        prompts = []
        def pedir(prompt, **kwargs):
            prompts.append(prompt)
            return json.dumps(respostas.pop(0))
        resultado = IC["_tese_de"](pedir, "probatoria", "instrucao", "caso", catalogo())
        self.assertIn("RP01.valor_centavos:CAMPO_AUSENTE;decisao=necessita_informacao", prompts[1])
        self.assertIn("Nao mude o merito", prompts[1])
        self.assertEqual(resultado, boa)

    def test_rollback_nao_expoe_valor_bruto_nem_texto_privado(self):
        segredo = "conteudo privado do caso"
        ruim = tese("probatoria", decisao("RP01", "conceder", segredo), decisao("RP02", "negar"))
        with self.assertRaises(ValueError) as ctx:
            IC["_tese_de"](lambda *a, **k: json.dumps(ruim), "probatoria", "instrucao", segredo, catalogo())
        erro = str(ctx.exception)
        self.assertNotIn(segredo, erro)
        self.assertIn("recebido=TEXTO", erro)
        self.assertIn("1=RP01.valor_centavos:", erro)
        self.assertIn("2=RP01.valor_centavos:", erro)

    def test_transporte_simulado_perde_null_apenas_em_modo_objeto(self):
        # Regressao simulada da hipotese de transporte, nao execucao real do SDK.
        p = self.painel_simples(["necessita_informacao", "fora_de_escopo", "negar"])
        p["catalogo"]["pedidos"][0]["valor_pedido_centavos"] = None
        respostas = [p["catalogo"]] + p["teses"]
        chamadas = []
        def omitir_nulos(obj):
            if isinstance(obj, dict):
                return {k: omitir_nulos(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, list):
                return [omitir_nulos(v) for v in obj]
            return obj
        self.assertNotIn("valor_centavos", omitir_nulos(p["teses"][0])["pedidos"][0])
        def pedir(prompt, response_format):
            chamadas.append(response_format)
            obj = respostas.pop(0)
            return json.dumps(obj) if response_format == "text" else omitir_nulos(obj)
        resultado = IC["_painel_de"](pedir, "resumos anonimizados")
        self.assertEqual(chamadas, ["text"] * 4)
        self.assertTrue(IC["_painel_valido"](resultado))
        self.assertIsNone(resultado["catalogo"]["pedidos"][0]["valor_pedido_centavos"])
        self.assertIn("valor_centavos", resultado["teses"][0]["pedidos"][0])
        self.assertIsNone(resultado["teses"][0]["pedidos"][0]["valor_centavos"])
        self.assertIsNone(resultado["consolidado"]["faixa_total_centavos"])
        self.assertIn("valor indeterminado", IC["_render_termo_opcao"]("0005", resultado))

    def test_analyze_e_get_case_simulados_preservam_termo_com_um_ep(self):
        p = self.painel_simples(["necessita_informacao"] * 3)
        respostas = ([p["catalogo"]] + p["teses"]) * 2  # lider e validador
        def pedir(prompt, **kwargs):
            self.assertEqual(kwargs, {"response_format": "text"})
            return json.dumps(respostas.pop(0))
        contrato, contagem = contrato_simulado(pedir, validar=True)
        contrato.analyze_case("5")
        estado = json.loads(contrato.get_case())
        self.assertEqual(contagem["ep"], 1)
        self.assertEqual(respostas, [])
        self.assertEqual(estado["case_id"], "0005")
        self.assertEqual(estado["versao"], "10.1.3-experimental")
        self.assertEqual(estado["status"], "termo_opcao_disponivel")
        self.assertIsNone(json.loads(estado["painel"])["consolidado"]["faixa_total_centavos"])
        self.assertIn("valor indeterminado", estado["termo_opcao"])
        self.assertNotIn("R$ 0,00", estado["termo_opcao"])

    def test_falha_de_formato_simulada_nao_grava_termo(self):
        p = self.painel_simples(["necessita_informacao"] * 3)
        ruim = p["teses"][0]
        del ruim["pedidos"][0]["valor_centavos"]
        respostas = [p["catalogo"], ruim, ruim]
        contrato, contagem = contrato_simulado(lambda *a, **k: json.dumps(respostas.pop(0)))
        with self.assertRaisesRegex(ValueError, "LLM_INVALID_PANEL:lente=probatoria:1=RP01.valor_centavos:CAMPO_AUSENTE"):
            contrato.analyze_case("5")
        self.assertEqual(contagem["ep"], 1)
        self.assertEqual(respostas, [])
        estado = json.loads(contrato.get_case())
        self.assertEqual(estado["status"], "vazio")
        self.assertEqual(estado["termo_opcao"], "")
        self.assertEqual(estado["painel"], "")

    def test_consolida_passou_e_controvertido_sem_esconder_zero(self):
        cat = catalogo()
        teses = [
            tese("probatoria", decisao("RP01", "conceder", 100000), decisao("RP02", "negar")),
            tese("jurisprudencial", decisao("RP01", "conceder", 120000), decisao("RP02", "conceder", 50000)),
            tese("auditora", decisao("RP01", "conceder", 110000), decisao("RP02", "negar")),
        ]
        cons = IC["_consolidar"](cat, teses)
        self.assertEqual(cons["pedidos"][0]["status"], "passou")
        self.assertEqual(cons["pedidos"][0]["faixa_centavos"], [100000, 120000])
        self.assertEqual(cons["pedidos"][1]["status"], "controvertido")
        self.assertEqual(cons["pedidos"][1]["faixa_centavos"], [0, 50000])
        self.assertIn("ZERO_VERSUS_POSITIVO", cons["pedidos"][1]["flags"])

    def test_concessao_monetaria_sem_fonte_e_invalida(self):
        cat = catalogo()
        d = decisao("RP01", "conceder", 100000)
        d["fontes_favoraveis"] = []
        self.assertFalse(IC["_decisao_valida"](d, cat["pedidos"][0]))

    def test_zero_e_positivo_nunca_sao_proximos(self):
        self.assertFalse(IC["_perto"](0, 1))
        self.assertFalse(IC["_faixas_equivalentes"]([0, 0], [0, 100000]))

    def test_valores_positivos_dentro_de_15_porcento_sao_proximos(self):
        self.assertTrue(IC["_perto"](100000, 110000))
        self.assertFalse(IC["_perto"](100000, 130000))

    def test_paineis_proximos_sao_equivalentes(self):
        cat_a = catalogo()
        cat_b = catalogo()
        cat_b["pedidos"][0]["descricao"] = "mesmo pedido com outra redacao"
        teses_a = [
            tese("probatoria", decisao("RP01", "conceder", 100000), decisao("RP02", "negar")),
            tese("jurisprudencial", decisao("RP01", "conceder", 110000), decisao("RP02", "negar")),
            tese("auditora", decisao("RP01", "conceder", 105000), decisao("RP02", "negar")),
        ]
        teses_b = [
            tese("probatoria", decisao("RP01", "conceder", 105000), decisao("RP02", "negar")),
            tese("jurisprudencial", decisao("RP01", "conceder", 115000), decisao("RP02", "negar")),
            tese("auditora", decisao("RP01", "conceder", 110000), decisao("RP02", "negar")),
        ]
        self.assertTrue(IC["_paineis_equivalentes"](
            painel(cat_a, teses_a), painel(cat_b, teses_b)
        ))

    def test_paineis_zero_e_positivo_nao_sao_equivalentes(self):
        cat = catalogo()
        teses_zero = [
            tese(nome, decisao("RP01", "negar"), decisao("RP02", "negar"))
            for nome in ("probatoria", "jurisprudencial", "auditora")
        ]
        teses_positivo = [
            tese(nome, decisao("RP01", "conceder", 100000), decisao("RP02", "negar"))
            for nome in ("probatoria", "jurisprudencial", "auditora")
        ]
        self.assertFalse(IC["_paineis_equivalentes"](
            painel(cat, teses_zero), painel(cat, teses_positivo)
        ))

    def test_lider_nao_pode_adulterar_o_consolidado(self):
        cat = catalogo()
        teses = [
            tese(nome, decisao("RP01", "conceder", 100000), decisao("RP02", "negar"))
            for nome in ("probatoria", "jurisprudencial", "auditora")
        ]
        legitimo = painel(cat, teses)
        adulterado = painel(cat, teses)
        adulterado["consolidado"]["pedidos"][0]["status"] = "nao_passou"
        self.assertFalse(IC["_painel_valido"](adulterado))
        self.assertFalse(IC["_paineis_equivalentes"](adulterado, legitimo))

    def test_termo_e_deterministico_e_expoe_status(self):
        cat = catalogo()
        teses = [
            tese("probatoria", decisao("RP01", "conceder", 100000), decisao("RP02", "negar")),
            tese("jurisprudencial", decisao("RP01", "conceder", 120000), decisao("RP02", "negar")),
            tese("auditora", decisao("RP01", "conceder", 110000), decisao("RP02", "negar")),
        ]
        termo = IC["_render_termo_opcao"]("0001", painel(cat, teses))
        self.assertIn("TERMO DE OPCAO", termo)
        self.assertIn("Status: passou", termo)
        self.assertIn("Status: nao passou", termo)
        self.assertIn("R$ 1.000,00 a R$ 1.200,00", termo)


if __name__ == "__main__":
    unittest.main()
