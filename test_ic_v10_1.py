#!/usr/bin/env python3
"""Testes unitarios puros da consolidacao e equivalencia da v10.1."""

import unittest
import json
from pathlib import Path


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
        "valor_centavos": valor,
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


class V101Tests(unittest.TestCase):
    def test_fluxo_completo_aceita_objetos_e_json_textual(self):
        for textual in (False, True):
            respostas = [catalogo()] + [
                tese(nome, decisao("RP01", "conceder", 100000), decisao("RP02", "negar"))
                for nome, _ in IC["LENTES"]
            ]
            chamadas = []
            def pedir(prompt, **kwargs):
                self.assertEqual(kwargs, {"response_format": "json"})
                chamadas.append(prompt)
                obj = respostas.pop(0)
                return json.dumps(obj) if textual else obj
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
            return respostas.pop(0)
        resultado = IC["_tese_de"](pedir, "probatoria", "instrucao", "caso", catalogo())
        self.assertIn("RP01.comentario:TEXTO_1_A_240", prompts[1])
        self.assertEqual(resultado["pedidos"][0]["valor_centavos"], 100000)

    def test_erro_final_identifica_lente_pedido_campo_e_tentativas(self):
        ruim = tese("auditora", decisao("RP01", "conceder", 100000), decisao("RP02", "negar"))
        ruim["pedidos"][0]["valor_centavos"] = "100000"
        with self.assertRaisesRegex(ValueError, "LLM_INVALID_PANEL:lente=auditora:1=RP01.valor_centavos.*2=RP01.valor_centavos"):
            IC["_tese_de"](lambda *a, **k: ruim, "auditora", "instrucao", "caso", catalogo())

    def test_fontes_com_objetos_sao_rejeitadas_sem_typeerror(self):
        self.assertFalse(IC["_lista_fontes_valida"]([{"id": "DR"}]))
        self.assertFalse(IC["_lista_fontes_valida"]([["DR"]]))

    def test_falha_catalogo_interrompe_antes_das_lentes(self):
        chamadas = []
        def pedir(prompt, **kwargs):
            chamadas.append(prompt)
            return {"pedidos": []}
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
