import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from termo_mediador import (
    ErroTermoMediador,
    carregar_resposta,
    corrigir_portugues,
    gerar_termos,
    main,
    renderizar_html,
    renderizar_markdown,
)


def item(pedido_id, tipo="formula", estado="condicional", auditoria="apta", conflitos=None):
    monetaria = tipo in {"formula", "faixa"}
    return {
        "pedido_id": pedido_id,
        "descricao": "Reparacao e responsabilizacao por infiltracao.",
        "status": "necessita_informacao",
        "decisoes_por_lente": {
            "probatoria": {"decisao": "necessita_informacao"},
            "jurisprudencial": {"decisao": "necessita_informacao"},
        },
        "analises": {
            "probatoria": {"lacuna": {"pergunta": "Qual e a contribuicao de cada parte?"}},
        },
        "negociacao": {
            "estado": estado,
            "faixa_centavos": [4000, 6000] if tipo == "faixa" else None,
            "faixa_discussao_centavos": [0, 10000] if tipo == "formula" else None,
            "opcao": {
                "tipo": tipo,
                "fontes": ["PR"],
                "base": {"valor_centavos": 10000} if monetaria else None,
            },
            "auditoria": {
                "resultado": auditoria,
                "riscos": ["DUPLA_CONTAGEM"] if auditoria == "apta_com_ressalva" else [],
                "conflitos_com": conflitos or [],
            },
        },
    }


def resposta(*pedidos):
    painel = {"versao": "20.0.0-experimental", "consolidado": {"pedidos": list(pedidos)}}
    return {
        "case_id": "0005",
        "versao": "20.0.0-experimental",
        "status": "termo_opcao_disponivel",
        "painel": json.dumps(painel, ensure_ascii=False),
        "termo_opcao": "texto on-chain não utilizado pelo pós-processador",
    }


class TermoMediadorTests(unittest.TestCase):
    def test_uma_opcao_aprovada_gera_aceite_e_nao_aceite(self):
        resultado = gerar_termos(resposta(item("RP01")))
        self.assertEqual(resultado["combinacoes_total"], 2)
        self.assertEqual(resultado["termos"][0]["escolhas"][0]["decisao"], "aceitar")
        self.assertEqual(resultado["termos"][1]["escolhas"][0]["decisao"], "não aceitar")
        texto = renderizar_markdown(resultado)
        self.assertIn("Termo de Opção 1", texto)
        self.assertIn("R$ 0,00 a R$ 100,00", texto)
        self.assertIn("percentual (%) a definir", texto)
        self.assertIn("O percentual (%) será definido pelas partes", texto)
        self.assertNotIn("percentual `p`", texto)
        self.assertIn("convergiram em necessidade de informação adicional", texto)

    def test_pedido_e_explicado_uma_vez_antes_do_cenario(self):
        texto = gerar_termos(resposta(item("RP01")))["termos"][0]["texto_markdown"]
        descricao = "Reparação e responsabilização por infiltração"
        self.assertLess(texto.index("## Identificação dos pedidos"), texto.index("## Cenário"))
        self.assertIn(f"**RP01** identifica o pedido relativo a: {descricao}.", texto)
        self.assertEqual(texto.count(descricao), 1)
        self.assertIn("As partes aceitam negociar o RP01, usando", texto)
        self.assertNotIn("RP01 —", texto)

    def test_duas_opcoes_independentes_geram_quatro_combinacoes(self):
        resultado = gerar_termos(resposta(item("RP01"), item("RP02", "nao_monetaria")))
        self.assertEqual(resultado["combinacoes_total"], 4)
        self.assertEqual(
            [[e["decisao"] for e in termo["escolhas"]] for termo in resultado["termos"]],
            [
                ["aceitar", "aceitar"],
                ["aceitar", "não aceitar"],
                ["não aceitar", "aceitar"],
                ["não aceitar", "não aceitar"],
            ],
        )

    def test_opcoes_nao_cumulativas_nao_geram_combinacao_invalida(self):
        a = item("RP01", auditoria="apta_com_ressalva", conflitos=["RP02"])
        b = item("RP02", auditoria="apta_com_ressalva", conflitos=["RP01"])
        resultado = gerar_termos(resposta(a, b))
        self.assertEqual(resultado["combinacoes_total"], 3)
        self.assertNotIn(["aceitar", "aceitar"], [
            [e["decisao"] for e in termo["escolhas"]] for termo in resultado["termos"]
        ])

    def test_retida_nao_vira_escolha_e_aparece_com_riscos(self):
        retida = item("RP02", "nao_monetaria", "retida_pela_auditoria", "reformular")
        retida["negociacao"]["auditoria"]["riscos"] = ["ESCOPO", "PREMISSA"]
        resultado = gerar_termos(resposta(item("RP01"), retida))
        self.assertEqual(resultado["opcoes_aprovadas"], ["RP01"])
        self.assertEqual(resultado["combinacoes_total"], 2)
        texto = resultado["termos"][0]["texto_markdown"]
        self.assertIn("retida pela auditoria; riscos: escopo, premissa", texto)
        self.assertIn("As lentes probatória e jurisprudencial convergiram", texto)

    def test_sem_opcao_aprovada_gera_um_documento_explicativo(self):
        resultado = gerar_termos(resposta(item("RP01", "sem_opcao", "sem_opcao")))
        self.assertEqual(resultado["combinacoes_total"], 1)
        self.assertEqual(resultado["opcoes_aprovadas"], [])
        self.assertIn("não contém opção aprovada", resultado["termos"][0]["texto_markdown"])

    def test_correcao_de_portugues_preserva_caixa(self):
        self.assertEqual(
            corrigir_portugues("OPCAO de composicao; Nao reconhecer divida."),
            "OPÇÃO de composição; Não reconhecer dívida.",
        )

    def test_carrega_json_duplamente_codificado(self):
        objeto = resposta(item("RP01"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "get-case.json"
            path.write_text(
                json.dumps(json.dumps(objeto, ensure_ascii=False), ensure_ascii=False) + "\n\nget_code_hash\n",
                encoding="utf-8",
            )
            self.assertEqual(carregar_resposta(path)["case_id"], "0005")

    def test_limite_recusa_saida_parcial(self):
        with self.assertRaisesRegex(ErroTermoMediador, "mais de 2 combinações"):
            gerar_termos(resposta(item("RP01"), item("RP02")), max_combinations=2)

    def test_ids_de_pedido_devem_ser_unicos(self):
        with self.assertRaisesRegex(ErroTermoMediador, "IDs textuais únicos"):
            gerar_termos(resposta(item("RP01"), item("RP01")))

    def test_uma_lente_ausente_nao_e_descrita_como_convergencia(self):
        unico = item("RP01")
        del unico["decisoes_por_lente"]["jurisprudencial"]
        texto = gerar_termos(resposta(unico))["termos"][0]["texto_markdown"]
        self.assertIn("Somente uma lente decisória foi registrada", texto)
        self.assertNotIn("lentes probatória e jurisprudencial convergiram", texto)

    def test_cli_pode_ler_stdin_e_emitir_json_unicode(self):
        entrada = json.dumps(resposta(item("RP01")), ensure_ascii=False)
        saida = io.StringIO()
        with patch("sys.stdin", io.StringIO(entrada)), patch("sys.stdout", saida):
            main(["-", "--format", "json"])
        objeto = json.loads(saida.getvalue())
        self.assertEqual(objeto["combinacoes_total"], 2)
        self.assertIn("Opção", objeto["termos"][0]["titulo"])

    def test_html_e_autocontido_imprimivel_e_escapa_dados_do_painel(self):
        malicioso = item("RP01")
        malicioso["descricao"] = "Reparação <script>alert('x')</script>"
        resultado = gerar_termos(resposta(malicioso))
        pagina = renderizar_html(resultado)
        self.assertTrue(pagina.startswith("<!doctype html>"))
        self.assertIn('<html lang="pt-BR">', pagina)
        self.assertIn('<meta charset="utf-8">', pagina)
        self.assertIn("@media print", pagina)
        self.assertEqual(pagina.count('<article class="termo">'), 2)
        self.assertIn("R$ 0,00 a R$ 100,00", pagina)
        self.assertIn("&lt;script&gt;", pagina)
        self.assertNotIn("<script>alert", pagina)

    def test_cli_emite_html(self):
        entrada = json.dumps(resposta(item("RP01")), ensure_ascii=False)
        saida = io.StringIO()
        with patch("sys.stdin", io.StringIO(entrada)), patch("sys.stdout", saida):
            main(["-", "--format", "html"])
        self.assertIn("<title>Termos de Opção — Caso 0005</title>", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
