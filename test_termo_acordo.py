import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from termo_acordo import (
    ErroTermoAcordo,
    gerar_acordo,
    main,
    renderizar_html,
    valor_por_extenso,
)


def resposta(tipo="formula"):
    opcao = {
        "tipo": tipo,
        "pagador": "requerido",
        "beneficiario": "requerente",
        "fontes": ["DR"],
    }
    negociacao = {
        "estado": "condicional",
        "opcao": opcao,
        "auditoria": {"resultado": "apta", "riscos": [], "conflitos_com": []},
    }
    if tipo == "formula":
        opcao["base"] = {"valor_centavos": 6473488}
        negociacao["faixa_discussao_centavos"] = [0, 6473488]
    elif tipo == "faixa":
        negociacao["faixa_centavos"] = [3000000, 5000000]
    painel = {
        "versao": "20.0.0-experimental",
        "consolidado": {"pedidos": [{
            "pedido_id": "RP01",
            "descricao": "Ressarcimento do reparo do imóvel.",
            "status": "necessita_informacao",
            "decisoes_por_lente": {},
            "negociacao": negociacao,
        }]},
    }
    return {"case_id": "0005", "versao": "20.0.0-experimental", "painel": json.dumps(painel)}


def dados(aceite=True):
    return {
        "aceite": {"termo_opcao_id": "TO-001", "todos_concordam": aceite},
        "partes": {
            "requerente": {"nome": "Ana", "cpf_cnpj": "111", "qualificacao": "brasileira", "endereco": "Rua A"},
            "requerido": {"nome": "Empresa B", "cpf_cnpj": "222", "qualificacao": "sociedade empresária", "endereco": "Rua B"},
        },
        "mediador": {"nome": "Mediador C", "qualificacao": "mediador extrajudicial"},
        "local": "São Paulo/SP",
        "data_assinatura": "2026-09-09",
        "resumo_conflito": "Discussão sobre danos no imóvel",
        "pagamentos": {"RP01": {"vencimento": "2026-10-09", "forma": "PIX"}},
        "assinatura": {"partes_e_mediador": True, "duas_testemunhas": True},
        "confidencialidade": True,
    }


class TermoAcordoTests(unittest.TestCase):
    def test_formula_calcula_valor_final_e_redige_documento(self):
        resultado = gerar_acordo(resposta(), dados(), {"RP01": "60"})
        self.assertEqual(resultado["obrigacoes"][0]["centavos"], 3884093)
        texto = resultado["texto_markdown"]
        self.assertIn("R$ 38.840,93", texto)
        self.assertIn("trinta e oito mil oitocentos e quarenta reais e noventa e três centavos", texto)
        self.assertIn("60% da base de R$ 64.734,88", texto)
        self.assertIn("09/10/2026", texto)
        self.assertIn("## Testemunhas", texto)
        self.assertIn("quitação será concedida somente após o cumprimento integral", texto)

    def test_recusa_sem_aceite_unanime(self):
        with self.assertRaisesRegex(ErroTermoAcordo, "aceite.todos_concordam"):
            gerar_acordo(resposta(), dados(False), {"RP01": "60"})

    def test_recusa_percentual_em_aberto_e_fora_do_limite(self):
        with self.assertRaisesRegex(ErroTermoAcordo, "falta --percentual"):
            gerar_acordo(resposta(), dados())
        with self.assertRaisesRegex(ErroTermoAcordo, "entre 0 e 100"):
            gerar_acordo(resposta(), dados(), {"RP01": "101"})

    def test_faixa_exige_valor_exato_dentro_da_faixa(self):
        with self.assertRaisesRegex(ErroTermoAcordo, "fora da faixa"):
            gerar_acordo(resposta("faixa"), dados(), valores={"RP01": "29.999,99"})
        resultado = gerar_acordo(resposta("faixa"), dados(), valores={"RP01": "40.000,00"})
        self.assertEqual(resultado["obrigacoes"][0]["centavos"], 4000000)

    def test_dados_formais_obrigatorios(self):
        incompleto = dados()
        del incompleto["partes"]["requerente"]["cpf_cnpj"]
        with self.assertRaisesRegex(ErroTermoAcordo, "cpf_cnpj"):
            gerar_acordo(resposta(), incompleto, {"RP01": "60"})

    def test_recusa_marcador_nao_preenchido(self):
        incompleto = dados()
        incompleto["partes"]["requerente"]["nome"] = "PREENCHER: nome"
        with self.assertRaisesRegex(ErroTermoAcordo, "ainda não preenchido"):
            gerar_acordo(resposta(), incompleto, {"RP01": "60"})

    def test_rascunho_substitui_identidades_marca_saida_e_remove_assinaturas(self):
        modelo = dados()
        modelo["partes"]["requerente"]["nome"] = "PREENCHER: nome"
        modelo["mediador"]["nome"] = "PREENCHER: mediador"
        resultado = gerar_acordo(resposta(), modelo, {"RP01": "60"}, rascunho=True)
        self.assertTrue(resultado["rascunho"])
        self.assertEqual(resultado["partes"]["requerente"]["nome"], "Marina Alves de Souza")
        texto = resultado["texto_markdown"]
        self.assertIn("RASCUNHO — SIMULAÇÃO SEM VALIDADE", texto)
        self.assertIn("DADOS FICTÍCIOS. NÃO ASSINAR", texto)
        self.assertIn("Campos de assinatura suprimidos", texto)
        self.assertNotIn("## Testemunhas", texto)
        self.assertNotIn("____________________________________", texto)

    def test_rascunho_html_tem_marcacao_visual(self):
        resultado = gerar_acordo(resposta(), dados(), {"RP01": "60"}, rascunho=True)
        html = renderizar_html(resultado)
        self.assertIn('<body class="rascunho">', html)
        self.assertIn("border: 5px solid #a61b1b", html)
        self.assertIn("DADOS FICTÍCIOS", html)

    def test_opcao_nao_monetaria_exige_prestacao_responsavel_e_prazo(self):
        entrada = dados()
        entrada["pagamentos"] = {}
        entrada["obrigacoes"] = {
            "RP01": {"responsavel": "Empresa B", "prestacao": "refazer a impermeabilização", "prazo": "30 dias"}
        }
        resultado = gerar_acordo(resposta("nao_monetaria"), entrada)
        self.assertIn("Empresa B obriga-se a refazer a impermeabilização, no prazo de 30 dias", resultado["texto_markdown"])

    def test_html_escapa_dados_e_e_imprimivel(self):
        entrada = dados()
        entrada["resumo_conflito"] = "Dano <script>alert(1)</script>"
        resultado = gerar_acordo(resposta(), entrada, {"RP01": "60"})
        html = renderizar_html(resultado)
        self.assertIn("@media print", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>alert", html)

    def test_cli_aceita_percentual_unico_abreviado(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "get-case.json"
            formais = Path(tmp) / "dados.json"
            entrada.write_text(json.dumps(resposta()), encoding="utf-8")
            formais.write_text(json.dumps(dados()), encoding="utf-8")
            saida = io.StringIO()
            with patch("sys.stdout", saida):
                main([str(entrada), "--dados", str(formais), "--percentual", "60", "--format", "json"])
            self.assertEqual(json.loads(saida.getvalue())["obrigacoes"][0]["centavos"], 3884093)

    def test_cli_rascunho_aceita_arquivo_modelo_nao_preenchido(self):
        modelo = dados()
        modelo["partes"]["requerente"]["nome"] = "PREENCHER: nome"
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "get-case.json"
            formais = Path(tmp) / "dados.json"
            entrada.write_text(json.dumps(resposta()), encoding="utf-8")
            formais.write_text(json.dumps(modelo), encoding="utf-8")
            saida = io.StringIO()
            with patch("sys.stdout", saida):
                main([
                    str(entrada), "--dados", str(formais), "--percentual", "60",
                    "--rascunho", "--format", "html",
                ])
            self.assertIn("SIMULAÇÃO SEM VALIDADE", saida.getvalue())

    def test_valores_por_extenso(self):
        self.assertEqual(valor_por_extenso(100), "um real")
        self.assertEqual(valor_por_extenso(101), "um real e um centavo")
        self.assertEqual(valor_por_extenso(100000000), "um milhão de reais")


if __name__ == "__main__":
    unittest.main()
