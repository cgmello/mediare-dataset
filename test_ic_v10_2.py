#!/usr/bin/env python3
"""Regressoes locais v10.2. LLM, transporte e gl simulados; nao e teste on-chain."""
import copy
import json
import unittest
from pathlib import Path
from types import SimpleNamespace


def carregar(gl=None):
    src = Path(__file__).with_name("ic_v10_2.py").read_text(encoding="utf-8")
    if gl is None:
        src = src.split("class MediareCommitteeV102")[0]
    ns = {"gl": gl}
    exec(compile(src.replace("from genlayer import *", ""), "ic_v10_2.py", "exec"), ns)
    return ns


IC = carregar()
DOCS = {
    "peticao_requerente": "Pedido de reparacao de R$ 1.000,00.",
    "resposta_requerido": "Defesa contesta a proporcao de responsabilidade.",
    "documentos_requerente": "Orcamento do reparo: R$ 1.000,00. Laudo estima participacao de 40% a 60%.",
    "documentos_requerido": "Fotos da intervencao posterior.",
}
CORPO = json.dumps(DOCS, ensure_ascii=False)


def fixture(tipo="formula", decisao="necessita_informacao", modalidade="pagar", bloqueada=False):
    cat = {"pedidos": [{"id": "RP01", "autor": "requerente", "contra": "requerido",
                        "modalidade": modalidade, "natureza": "principal" if modalidade == "pagar" else "declaratoria",
                        "valor_pedido_centavos": 100000 if modalidade == "pagar" else None,
                        "descricao": "Reparacao"}]}
    l = {"dimensao": "proporcao", "pergunta": "Que parcela do reparo cada parte admite assumir?",
         "impacto": "A parcela aceita define p; sem acordo sobre ela nao existe quantia definida."}
    criterio = {"tipo": "proporcao_a_negociar", "min_bps": None, "max_bps": None, "fonte": None, "trecho": None}
    base = {"valor_centavos": 100000, "natureza": "orcamento", "fonte": "DR", "trecho": "Orcamento do reparo: R$ 1.000,00."}
    if tipo == "faixa":
        criterio.update(tipo="proporcao_documentada", min_bps=4000, max_bps=6000, fonte="DR",
                        trecho="Laudo estima participacao de 40% a 60%.")
    elif tipo != "formula":
        criterio["tipo"] = "sem_calculo"
        base = None
    o = {"tipo": tipo, "proposta": "Discutir a composicao sem reconhecimento automatico de divida.",
         "premissa": "Depende de concordancia sobre a base e as responsabilidades.",
         "ressalva": "Nao somar com outros pedidos relativos ao mesmo reparo.",
         "fontes": ["DR", "RR"], "pagador": "requerido", "beneficiario": "requerente", "base": base, "criterio": criterio}
    if tipo in ("diligencia", "sem_opcao"):
        o.update(pagador=None, beneficiario=None)
    if tipo == "sem_opcao":
        o["fontes"] = []
    teses = []
    for nome, _ in IC["LENTES"]:
        d = {"pedido_id": "RP01", "decisao": decisao,
             "valor_centavos": None if decisao in ("necessita_informacao", "fora_de_escopo") else
                                100000 if decisao == "conceder" and modalidade == "pagar" else 0,
             "pagador": "requerido" if decisao == "conceder" else None,
             "beneficiario": "requerente" if decisao == "conceder" else None,
             "fontes_favoraveis": ["DR"], "fontes_contrarias": ["RR"], "comentario": "Ha suporte, mas a proporcao e discutida.",
             "sustentado": "O resumo contem orcamento de reparo.", "controvertido": "A proporcao atribuivel a cada parte.",
             "lacuna": copy.deepcopy(l)}
        if nome == "jurisprudencial":
            d["opcao"] = o
        if nome == "auditora":
            d["auditoria"] = {"resultado": "reformular" if bloqueada else "apta", "riscos": ["PREMISSA"] if bloqueada else [],
                              "motivo": "A premissa deve ser esclarecida." if bloqueada else "Opcao explicitamente condicional com base identificada."}
        teses.append({"lente": nome, "pedidos": [d]})
    return {"versao": IC["VERSAO"], "catalogo": cat, "teses": teses,
            "consolidado": IC["_consolidar"](cat, teses)}


def opcao(p):
    return p["teses"][1]["pedidos"][0]["opcao"]


def erro_opcao(p, corpo=CORPO):
    return IC["_erro_opcao"](opcao(p), p["catalogo"]["pedidos"][0], p["teses"][1]["pedidos"][0], corpo)


def reconsolidar(p):
    p["consolidado"] = IC["_consolidar"](p["catalogo"], p["teses"])
    return p


def contrato_simulado(respostas, validar=True, alterar_lider=None, docs=DOCS):
    cont = {"ep": 0, "llm": 0, "web": 0, "prompts": []}
    class Retorno:
        def __init__(self, obj):
            self.calldata = obj
    def pedir(prompt, **kwargs):
        assert kwargs == {"response_format": "text"}
        cont["llm"] += 1
        cont["prompts"].append(prompt)
        return json.dumps(respostas.pop(0), ensure_ascii=False)
    def web(url):
        cont["web"] += 1
        assert url.endswith("/casos/0005.json")
        return SimpleNamespace(body=json.dumps({"documentos": docs}).encode())
    def run(lider, validador):
        cont["ep"] += 1
        obj = json.loads(json.dumps(lider()))
        if alterar_lider:
            alterar_lider(obj)
        if validar and not validador(Retorno(obj)):
            raise RuntimeError("DISAGREE_SIMULADO")
        return obj
    gl = SimpleNamespace(Contract=object, public=SimpleNamespace(write=lambda f: f, view=lambda f: f),
                         vm=SimpleNamespace(UserError=ValueError, Return=Retorno, run_nondet_unsafe=run),
                         nondet=SimpleNamespace(exec_prompt=pedir, web=SimpleNamespace(get=web)))
    return carregar(gl)["MediareCommitteeV102"](), cont


class V102Tests(unittest.TestCase):
    def test_cinco_tipos_validos_e_tres_lentes_sequenciais(self):
        for p in (fixture(), fixture("faixa"), fixture("nao_monetaria", modalidade="declarar"),
                  fixture("diligencia"), fixture("sem_opcao", "negar")):
            with self.subTest(tipo=opcao(p)["tipo"]):
                self.assertTrue(IC["_painel_valido"](p))
                for i, t in enumerate(p["teses"]):
                    self.assertEqual(IC["_erro_tese"](t, p["catalogo"], t["lente"], p["teses"][:i], CORPO), "")

    def test_indeterminado_pode_ter_formula_sem_virar_divida(self):
        p = fixture()
        c = p["consolidado"]
        self.assertIsNone(c["faixa_total_centavos"])
        self.assertIsNone(c["total_negociacao_centavos"])
        n = c["pedidos"][0]["negociacao"]
        self.assertEqual(n["estado"], "condicional")
        self.assertIsNone(n["faixa_centavos"])
        termo = IC["_render_termo_opcao"]("0005", p)
        self.assertIn("R$ 1.000,00 x p / 100", termo)
        self.assertIn("NAO definida pelo comite", termo)
        self.assertNotIn("R$ 0,00", termo)
        self.assertNotIn("sem maioria", termo)
        self.assertEqual(termo.count("# TERMO DE OPCAO"), 1)

    def test_faixa_calculada_nao_altera_conclusao(self):
        p = fixture("faixa")
        n = p["consolidado"]["pedidos"][0]["negociacao"]
        self.assertEqual(n["faixa_centavos"], [40000, 60000])
        self.assertIsNone(p["consolidado"]["faixa_total_centavos"])
        self.assertIn("Faixa condicional de negociacao: R$ 400,00 a R$ 600,00", IC["_render_termo_opcao"]("0005", p))

    def test_valor_documentado_condicional_e_arredondamento(self):
        p = fixture("faixa")
        o = opcao(p)
        o["criterio"].update(tipo="valor_documentado", min_bps=10000, max_bps=10000, fonte=None, trecho=None)
        self.assertEqual(erro_opcao(p), "")
        self.assertEqual(IC["_faixa_opcao"](o), [100000, 100000])
        o["base"]["valor_centavos"] = 101
        o["criterio"].update(tipo="proporcao_documentada", min_bps=5000, max_bps=5000)
        self.assertEqual(IC["_faixa_opcao"](o), [51, 51])

    def test_citacao_e_valor_devem_existir_na_fonte_real(self):
        for alterar, esperado in (
            (lambda o: o["base"].update(trecho="R$ 999,00"), "BASE_CITACAO_NAO_LOCALIZADA"),
            (lambda o: o["base"].update(valor_centavos=99900), "BASE_VALOR_NAO_CONSTA_NO_TRECHO"),
            (lambda o: o["base"].update(fonte="RR"), "BASE_CITACAO_NAO_LOCALIZADA"),
            (lambda o: o["base"].update(valor_centavos=True), "BASE_VALOR_OU_NATUREZA_INVALIDOS"),
            (lambda o: o["base"].update(valor_centavos="100000"), "BASE_VALOR_OU_NATUREZA_INVALIDOS"),
        ):
            p = fixture()
            alterar(opcao(p))
            self.assertEqual(erro_opcao(p), esperado)

    def test_percentual_inventado_ou_fora_da_fonte_e_rejeitado(self):
        p = fixture("faixa")
        opcao(p)["criterio"]["min_bps"] = 5000
        self.assertEqual(erro_opcao(p), "PROPORCAO_NAO_CONSTA_NO_TRECHO")
        opcao(p)["criterio"].update(min_bps=4000, fonte="RR")
        self.assertEqual(erro_opcao(p), "PROPORCAO_CITACAO_NAO_LOCALIZADA")

    def test_regex_monetario_e_percentual_nao_muda_unidades(self):
        self.assertEqual(IC["_valores_citados"]("R$ 64.734,88 e R$ 1234,56"), [6473488, 123456])
        self.assertEqual(IC["_valores_citados"]("-10,00 e 10.25"), [])
        self.assertEqual(IC["_percentuais_citados"]("12,5% e 100% e 0,25%"), [1250, 10000, 25])
        self.assertEqual(IC["_percentuais_citados"]("-10% e 1000%"), [])

    def test_formula_nao_aceita_percentual_oculto_no_campo_numerico(self):
        p = fixture()
        for campo, valor in (("min_bps", 4000), ("max_bps", 6000), ("fonte", "DR"), ("trecho", "50%")):
            q = copy.deepcopy(p)
            opcao(q)["criterio"][campo] = valor
            self.assertEqual(erro_opcao(q), "CRITERIO_SEM_NUMEROS_EXIGE_NULL")
        opcao(p)["faixa_centavos"] = [40000, 60000]
        self.assertEqual(erro_opcao(p), "SCHEMA_INVALIDO")

    def test_limites_de_proporcao_e_ordenacao(self):
        for mn, mx in ((True, 6000), (4000.0, 6000), (-1, 6000), (4000, 10001), (6000, 4000), (0, 0)):
            p = fixture("faixa")
            opcao(p)["criterio"].update(min_bps=mn, max_bps=mx)
            self.assertNotEqual(erro_opcao(p), "")

    def test_partes_e_modalidade_da_opcao(self):
        p = fixture()
        opcao(p).update(pagador="requerente", beneficiario="requerido")
        self.assertEqual(erro_opcao(p), "PARTES_INCOMPATIVEIS_COM_PEDIDO")
        self.assertEqual(erro_opcao(fixture("faixa", modalidade="declarar")), "PEDIDO_NAO_MONETARIO")
        self.assertEqual(erro_opcao(fixture("nao_monetaria")), "NAO_MONETARIA_EXIGE_MODALIDADE_COMPATIVEL")

    def test_fora_de_escopo_e_sem_opcao_nao_sao_escape(self):
        self.assertEqual(erro_opcao(fixture("sem_opcao")), "SEM_OPCAO_NAO_PERMITIDA_PARA_INDETERMINADO_OU_CONCESSAO")
        self.assertEqual(erro_opcao(fixture("formula", "fora_de_escopo")), "FORA_DE_ESCOPO_NAO_GERA_OPCAO")
        self.assertEqual(erro_opcao(fixture("sem_opcao", "fora_de_escopo")), "")

    def test_lacuna_exige_pergunta_e_impacto_concretos_no_schema(self):
        p = fixture()
        d = p["teses"][0]["pedidos"][0]
        for campo in ("pergunta", "impacto"):
            q = copy.deepcopy(d)
            q["lacuna"][campo] = None
            self.assertNotEqual(IC["_erro_analise"](q), "")
        d["lacuna"] = {"dimensao": "nenhuma", "pergunta": None, "impacto": None}
        self.assertNotEqual(IC["_erro_analise"](d), "")

    def test_formula_e_diligencia_exigem_lacuna_mesmo_com_concessao(self):
        for tipo in ("formula", "diligencia"):
            p = fixture(tipo, "conceder")
            p["teses"][1]["pedidos"][0]["lacuna"] = {"dimensao": "nenhuma", "pergunta": None, "impacto": None}
            self.assertEqual(erro_opcao(p), "PERGUNTA_E_IMPACTO_OBRIGATORIOS")

    def test_auditoria_retida_nao_expoe_faixa_como_opcao(self):
        p = fixture("faixa", bloqueada=True)
        self.assertTrue(IC["_painel_valido"](p))
        self.assertIsNone(p["consolidado"]["pedidos"][0]["negociacao"]["faixa_centavos"])
        termo = IC["_render_termo_opcao"]("0005", p)
        self.assertIn("Opcao retida", termo)
        self.assertIn("A premissa deve ser esclarecida.", termo)
        self.assertIn("Pergunta — auditora", termo)
        self.assertNotIn("Faixa condicional de negociacao:", termo)

    def test_auditoria_invalida_nao_passa(self):
        for resultado, riscos in (("apta", ["PREMISSA"]), ("reformular", []), ("apta", [{"risco": "PREMISSA"}])):
            p = fixture()
            d = p["teses"][2]["pedidos"][0]
            d["auditoria"].update(resultado=resultado, riscos=riscos)
            self.assertNotEqual(IC["_erro_auditoria"](d["auditoria"], d), "")
        p = fixture()
        d = p["teses"][2]["pedidos"][0]
        d["decisao"] = "fora_de_escopo"
        self.assertIn("FORA_DE_ESCOPO", IC["_erro_tese"](p["teses"][2], p["catalogo"], "auditora", p["teses"][:2], CORPO))

    def test_termo_mostra_fontes_premissas_e_efeito_das_respostas(self):
        termo = IC["_render_termo_opcao"]("0005", fixture())
        for texto in ("Premissa:", "Ressalva:", "Base discutida, nao divida:", "Trecho-base [DR]",
                      "favoraveis: DR; contrarias: RR", "O que muda com a resposta:", "Nao somar as opcoes"):
            self.assertIn(texto, termo)
        self.assertEqual(termo, IC["_render_termo_opcao"]("0005", fixture()))

    def test_render_independe_da_ordem_das_chaves_no_transporte(self):
        p = fixture()
        transportado = json.loads(json.dumps(p, sort_keys=True))
        self.assertEqual(IC["_render_termo_opcao"]("0005", p), IC["_render_termo_opcao"]("0005", transportado))

    def test_nao_monetaria_nao_recebe_faixa_ou_valor_zero(self):
        p = fixture("nao_monetaria", modalidade="declarar")
        termo = IC["_render_termo_opcao"]("0005", p)
        self.assertNotIn("Formula condicional:", termo)
        self.assertNotIn("R$ 0,00", termo)
        self.assertIn("pedido nao monetario", termo)

    def test_alterar_consolidado_auditoria_ou_faixa_invalida_painel(self):
        for alterar in (
            lambda p: p["consolidado"].update(total_negociacao_centavos=50000),
            lambda p: p["consolidado"]["pedidos"][0]["negociacao"].update(faixa_centavos=[1, 2]),
            lambda p: p["consolidado"]["pedidos"][0]["negociacao"].update(estado="retida_pela_auditoria"),
        ):
            p = fixture("faixa")
            alterar(p)
            self.assertFalse(IC["_painel_valido"](p))

    def test_painel_identico_nao_precisa_de_llm_semantica(self):
        p = fixture()
        self.assertTrue(IC["_paineis_equivalentes"](p, copy.deepcopy(p)))

    def test_premissas_diferentes_exigem_comparacao_semantica(self):
        a, b = fixture(), fixture()
        opcao(b)["premissa"] = "Depende de reconhecimento integral de responsabilidade."
        reconsolidar(b)
        self.assertFalse(IC["_paineis_equivalentes"](a, b))
        chamadas = []
        def pedir(prompt, **kwargs):
            chamadas.append(prompt)
            self.assertEqual(kwargs, {"response_format": "text"})
            return '{"equivalentes": false, "motivo": "Premissa materialmente diferente."}'
        self.assertFalse(IC["_paineis_equivalentes"](a, b, pedir))
        self.assertEqual(len(chamadas), 1)
        self.assertIn("mesma faixa numerica", chamadas[0])
        self.assertIn("DADOS NAO CONFIAVEIS", chamadas[0])

    def test_parafrase_pode_passar_com_booleano_semantico(self):
        a, b = fixture(), fixture()
        opcao(b)["proposta"] = "Debater uma composicao condicional sem reconhecer divida."
        reconsolidar(b)
        self.assertTrue(IC["_paineis_equivalentes"](a, b, lambda *a, **k: '{"equivalentes": true, "motivo": "Parafrase."}'))
        self.assertFalse(IC["_paineis_equivalentes"](a, b, lambda *a, **k: '{"equivalentes": "true", "motivo": "Texto."}'))

    def test_estrutura_divergente_rejeita_antes_do_llm(self):
        for alterar in (
            lambda p: opcao(p)["base"].update(natureza="pedido"),
            lambda p: p["teses"][0]["pedidos"][0]["lacuna"].update(dimensao="nexo"),
            lambda p: p["teses"][2]["pedidos"][0]["auditoria"].update(resultado="reformular", riscos=["PREMISSA"]),
        ):
            a, b = fixture(), fixture()
            alterar(b)
            reconsolidar(b)
            def nao_chamar(*args, **kwargs):
                self.fail("A divergencia estrutural deveria bloquear antes do LLM")
            self.assertFalse(IC["_paineis_equivalentes"](a, b, nao_chamar))

    def test_zero_indeterminado_e_valor_positivo_continuam_distintos(self):
        ps = [fixture("diligencia", d) for d in ("negar", "necessita_informacao", "conceder")]
        for i in range(3):
            for j in range(3):
                if i != j:
                    self.assertFalse(IC["_paineis_equivalentes"](ps[i], ps[j], lambda *a, **k: '{"equivalentes":true,"motivo":"x"}'))

    def test_pipeline_real_do_wrapper_simulado_um_ep_e_getters(self):
        p = fixture()
        respostas = copy.deepcopy(([p["catalogo"]] + p["teses"]) * 2)
        contrato, c = contrato_simulado(respostas)
        contrato.analyze_case("5")
        res = json.loads(contrato.get_case())
        self.assertEqual(c["ep"], 1)
        self.assertEqual(c["llm"], 8)
        self.assertEqual(c["web"], 2)
        self.assertEqual(res["versao"], "10.2-experimental")
        self.assertEqual(res["status"], "termo_opcao_disponivel")
        self.assertEqual(contrato.get_termo_opcao(), res["termo_opcao"])
        self.assertIn("Formula condicional:", res["termo_opcao"])
        self.assertIn('"lente": "probatoria"', c["prompts"][2])
        self.assertIn('"opcao":', c["prompts"][3])
        self.assertEqual(respostas, [])

    def test_validador_checa_citacao_lider_na_fonte_real(self):
        p = fixture()
        respostas = copy.deepcopy([p["catalogo"]] + p["teses"])
        def adulterar(obj):
            opcao(obj)["base"]["trecho"] = "Base falsa: R$ 1.000,00."
            reconsolidar(obj)
        contrato, c = contrato_simulado(respostas, alterar_lider=adulterar)
        with self.assertRaisesRegex(RuntimeError, "DISAGREE_SIMULADO"):
            contrato.analyze_case("5")
        self.assertEqual(c["llm"], 4)
        self.assertEqual(contrato.status, "vazio")

    def test_wrapper_consulta_semantica_quando_redacao_local_muda(self):
        a, b = fixture(), fixture()
        opcao(b)["ressalva"] = "Evitar somar pedidos sobrepostos para o mesmo reparo."
        reconsolidar(b)
        respostas = copy.deepcopy([a["catalogo"]] + a["teses"] + [b["catalogo"]] + b["teses"])
        respostas.append({"equivalentes": True, "motivo": "Mesmas condicoes, redacao diferente."})
        contrato, c = contrato_simulado(respostas)
        contrato.analyze_case("5")
        self.assertEqual(c["llm"], 9)
        self.assertEqual(c["ep"], 1)
        self.assertEqual(respostas, [])
        self.assertNotIn('"consolidado":', c["prompts"][-1])
        self.assertEqual(json.loads(contrato.get_case())["painel"], json.dumps(a, ensure_ascii=False, sort_keys=True))

    def test_erro_semantico_ou_false_nao_grava_estado(self):
        for resposta in ({"equivalentes": False, "motivo": "Premissa diferente."}, {"equivalentes": "sim", "motivo": "x"}):
            a, b = fixture(), fixture()
            opcao(b)["premissa"] = "Exige que o requerido reconheca toda a responsabilidade."
            reconsolidar(b)
            respostas = copy.deepcopy([a["catalogo"]] + a["teses"] + [b["catalogo"]] + b["teses"] + [resposta, resposta])
            contrato, c = contrato_simulado(respostas)
            with self.assertRaisesRegex(RuntimeError, "DISAGREE_SIMULADO"):
                contrato.analyze_case("5")
            self.assertEqual(contrato.get_termo_opcao(), "")
            self.assertEqual(contrato.status, "vazio")
            self.assertLessEqual(c["llm"], 10)

    def test_retry_da_opcao_nao_muda_merito_e_nao_expoe_fonte(self):
        p = fixture()
        ruim = copy.deepcopy(p["teses"][1])
        ruim["pedidos"][0]["opcao"]["base"]["trecho"] = "citacao privada inexistente R$ 1.000,00"
        respostas = [ruim, p["teses"][1]]
        prompts = []
        def pedir(prompt, **kwargs):
            prompts.append(prompt)
            return json.dumps(respostas.pop(0))
        res = IC["_tese_de"](pedir, "jurisprudencial", "instrucao", CORPO, p["catalogo"], p["teses"][:1])
        self.assertEqual(res, p["teses"][1])
        self.assertIn("RP01.opcao:BASE_CITACAO_NAO_LOCALIZADA", prompts[1])
        self.assertNotIn("citacao privada inexistente", prompts[1])
        self.assertIn("Nao mude o merito", prompts[1])

    def test_pedidos_relacionados_nao_somam_opcoes_automaticamente(self):
        p = fixture("faixa")
        cat = copy.deepcopy(p["catalogo"]["pedidos"][0])
        cat.update(id="RP02", modalidade="declarar", natureza="declaratoria", valor_pedido_centavos=None)
        p["catalogo"]["pedidos"].append(cat)
        segundo = fixture("nao_monetaria", modalidade="declarar")
        for t, outra in zip(p["teses"], segundo["teses"]):
            d = copy.deepcopy(outra["pedidos"][0])
            d["pedido_id"] = "RP02"
            t["pedidos"].append(d)
        reconsolidar(p)
        self.assertTrue(IC["_painel_valido"](p))
        self.assertIsNone(p["consolidado"]["total_negociacao_centavos"])
        self.assertEqual(p["consolidado"]["pedidos"][0]["negociacao"]["faixa_centavos"], [40000, 60000])
        self.assertIsNone(p["consolidado"]["pedidos"][1]["negociacao"]["faixa_centavos"])
        self.assertIn("Nao somar", IC["_render_termo_opcao"]("0005", p))

    def test_pedido_contraposto_preserva_polos_e_rejeita_inversao(self):
        p = fixture("faixa", "conceder")
        pedido = p["catalogo"]["pedidos"][0]
        pedido.update(id="RR01", autor="requerido", contra="requerente")
        for t in p["teses"]:
            t["pedidos"][0].update(pedido_id="RR01", pagador="requerente", beneficiario="requerido")
        opcao(p).update(pagador="requerente", beneficiario="requerido")
        self.assertTrue(IC["_painel_valido"](reconsolidar(p)))
        p["teses"][0]["pedidos"][0].update(pagador="requerido", beneficiario="requerente")
        self.assertFalse(IC["_painel_valido"](reconsolidar(p)))

    def test_schema_nao_relaxa_fontes_textos_ou_opcao_obrigatoria(self):
        for alterar in (
            lambda d: d.update(fontes_favoraveis=[{"id": "DR"}]),
            lambda d: d.update(sustentado="x" * 801),
            lambda d: d.update(comentario="x" * 1201),
            lambda d: d.pop("opcao"),
            lambda d: d.update(auditoria={"resultado": "apta"}),
        ):
            p = fixture()
            alterar(p["teses"][1]["pedidos"][0])
            self.assertNotEqual(IC["_erro_tese"](p["teses"][1], p["catalogo"], "jurisprudencial", p["teses"][:1], CORPO), "")

    def test_falha_da_auditoria_nao_grava_termo(self):
        p = fixture()
        ruim = copy.deepcopy(p["teses"][2])
        del ruim["pedidos"][0]["auditoria"]
        respostas = copy.deepcopy([p["catalogo"]] + p["teses"][:2] + [ruim, ruim])
        contrato, c = contrato_simulado(respostas, validar=False)
        with self.assertRaisesRegex(ValueError, "LLM_INVALID_PANEL:lente=auditora"):
            contrato.analyze_case("5")
        self.assertEqual(c["llm"], 5)
        self.assertEqual(contrato.termo_opcao, "")

    def test_schema_nao_aceita_catalogo_com_null_omitido(self):
        p = fixture()
        del p["catalogo"]["pedidos"][0]["valor_pedido_centavos"]
        self.assertFalse(IC["_catalogo_valido"](p["catalogo"]))

    def test_caso_0005_base_real_sem_inventar_rateio(self):
        caso = json.loads(Path(__file__).with_name("casos").joinpath("0005.json").read_text())
        corpo = json.dumps(caso["documentos"], ensure_ascii=False)
        p = fixture()
        b = opcao(p)["base"]
        b.update(valor_centavos=6473488, trecho="3. Orçamentos de reparação (impermeabilização + acabamentos): R$ 64.734,88.")
        self.assertEqual(erro_opcao(p, corpo), "")
        termo = IC["_render_termo_opcao"]("0005", reconsolidar(p))
        self.assertIn("R$ 64.734,88 x p / 100", termo)
        self.assertNotIn("R$ 32.367,44", termo)
        opcao(p)["tipo"] = "faixa"
        opcao(p)["criterio"].update(tipo="proporcao_documentada", min_bps=5000, max_bps=5000, fonte="DR", trecho="Rateio 50%.")
        self.assertEqual(erro_opcao(p, corpo), "PROPORCAO_CITACAO_NAO_LOCALIZADA")

    def test_limites_textuais_e_null_preservados(self):
        for n in (240, 241, 1200):
            p = fixture()
            for t in p["teses"]:
                t["pedidos"][0]["comentario"] = "á" * n
            self.assertTrue(IC["_painel_valido"](reconsolidar(p)))
        bruto = '{"valor":null,"zero":0}'
        self.assertEqual(IC["_ler_objeto_json"](lambda *a, **k: bruto, "caso"), {"valor": None, "zero": 0})
        for bruto in ('{} {}', '{"x":NaN}', '```json\n{}\n```'):
            with self.assertRaises(ValueError):
                IC["_ler_objeto_json"](lambda *a, **k: bruto, "caso")


if __name__ == "__main__":
    unittest.main()
