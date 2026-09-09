#!/usr/bin/env python3
"""Gera o Termo Final de Mediação a partir de um Termo de Opção aceito.

O processamento é off-chain e determinístico. A geração falha se o cenário não
tiver aceite unânime, se percentual/valor permanecer aberto ou se faltarem dados
formais essenciais. O script não substitui a revisão jurídica do caso concreto.
"""

import argparse
from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from html import escape
import json
from pathlib import Path
import re
import sys

from termo_mediador import (
    ErroTermoMediador,
    _markdown_para_html_fragmento,
    carregar_resposta,
    corrigir_portugues,
    extrair_painel,
    gerar_termos,
)


SCHEMA_VERSION = 1
TIPOS_MONETARIOS = {"formula", "faixa"}


class ErroTermoAcordo(ValueError):
    """O acordo final não pode ser gerado com os dados recebidos."""


def _texto(objeto, campo):
    valor = objeto.get(campo) if isinstance(objeto, dict) else None
    if not isinstance(valor, str) or not valor.strip():
        raise ErroTermoAcordo(f"campo obrigatório ausente: {campo}")
    valor = valor.strip()
    if valor.upper().startswith("PREENCHER"):
        raise ErroTermoAcordo(f"campo obrigatório ainda não preenchido: {campo}")
    return valor


def _dados_ficticios(dados):
    """Substitui identidades por personagens inequivocamente fictícios."""
    simulados = deepcopy(dados)
    simulados["aceite"] = {
        **(simulados.get("aceite") if isinstance(simulados.get("aceite"), dict) else {}),
        "todos_concordam": True,
    }
    simulados["partes"] = {
        "requerente": {
            "nome": "Marina Alves de Souza",
            "cpf_cnpj": "000.000.000-00 (número fictício e inválido)",
            "qualificacao": "brasileira, arquiteta, solteira",
            "endereco": "Rua Exemplo, nº 100, Bairro Modelo, São Paulo/SP, CEP 00000-000 (endereço fictício)",
        },
        "requerido": {
            "nome": "Construtora Horizonte Azul Ltda.",
            "cpf_cnpj": "00.000.000/0000-00 (número fictício e inválido)",
            "qualificacao": "sociedade empresária limitada, representada por Carlos Lima",
            "endereco": "Avenida Demonstração, nº 200, Bairro Modelo, São Paulo/SP, CEP 00000-000 (endereço fictício)",
        },
    }
    simulados["mediador"] = {
        "nome": "Renata Oliveira",
        "qualificacao": "mediadora extrajudicial, registro demonstrativo nº MED-0000",
    }
    if not isinstance(simulados.get("resumo_conflito"), str) or simulados["resumo_conflito"].upper().startswith("PREENCHER"):
        simulados["resumo_conflito"] = (
            "Controvérsia simulada sobre reparação de danos no imóvel, usada exclusivamente para visualizar o modelo"
        )
    return simulados


def _decimal(valor, nome):
    texto = str(valor).strip().replace("%", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        resultado = Decimal(texto)
    except (InvalidOperation, ValueError) as exc:
        raise ErroTermoAcordo(f"{nome} deve ser um número") from exc
    if not resultado.is_finite():
        raise ErroTermoAcordo(f"{nome} deve ser finito")
    return resultado


def _mapear_argumentos(valores, nome, permite_abreviado=False):
    resultado = {}
    abreviado = None
    for bruto in valores or []:
        if "=" not in bruto:
            if not permite_abreviado or abreviado is not None:
                raise ErroTermoAcordo(f"use {nome} como PEDIDO=VALOR")
            abreviado = bruto
            continue
        pedido_id, valor = bruto.split("=", 1)
        pedido_id = pedido_id.strip()
        if not pedido_id or pedido_id in resultado:
            raise ErroTermoAcordo(f"{nome} contém ID vazio ou repetido")
        resultado[pedido_id] = valor.strip()
    return resultado, abreviado


def _centavos(valor, nome):
    decimal = _decimal(valor, nome)
    if decimal < 0:
        raise ErroTermoAcordo(f"{nome} não pode ser negativo")
    exato = decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(exato * 100)


def _brl(centavos):
    reais, cents = divmod(centavos, 100)
    return "R$ " + f"{reais:,}".replace(",", ".") + f",{cents:02d}"


_UNIDADES = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]
_DEZ_A_DEZENOVE = [
    "dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis",
    "dezessete", "dezoito", "dezenove",
]
_DEZENAS = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
_CENTENAS = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]
_ESCALAS = [("", ""), ("mil", "mil"), ("milhão", "milhões"), ("bilhão", "bilhões"), ("trilhão", "trilhões")]


def _grupo_por_extenso(numero):
    if numero == 100:
        return "cem"
    partes = []
    centena, resto = divmod(numero, 100)
    if centena:
        partes.append(_CENTENAS[centena])
    if 10 <= resto <= 19:
        partes.append(_DEZ_A_DEZENOVE[resto - 10])
    else:
        dezena, unidade = divmod(resto, 10)
        if dezena:
            partes.append(_DEZENAS[dezena])
        if unidade:
            partes.append(_UNIDADES[unidade])
    return " e ".join(partes)


def _inteiro_por_extenso(numero):
    if numero == 0:
        return "zero"
    if numero < 0 or numero >= 10 ** 15:
        raise ErroTermoAcordo("valor fora do limite para escrita por extenso")
    grupos = []
    indice = 0
    while numero:
        numero, grupo = divmod(numero, 1000)
        if grupo:
            singular, plural = _ESCALAS[indice]
            if indice == 1:
                texto = "mil" if grupo == 1 else f"{_grupo_por_extenso(grupo)} mil"
            elif indice >= 2:
                texto = f"{_grupo_por_extenso(grupo)} {singular if grupo == 1 else plural}"
            else:
                texto = _grupo_por_extenso(grupo)
            grupos.append((grupo, texto))
        indice += 1
    grupos.reverse()
    saida = grupos[0][1]
    for grupo, texto in grupos[1:]:
        conector = " e " if grupo < 100 or grupo % 100 == 0 else " "
        saida += conector + texto
    return saida


def valor_por_extenso(centavos):
    reais, cents = divmod(centavos, 100)
    real = "real" if reais == 1 else "reais"
    de = " de" if reais >= 1_000_000 and reais % 1_000_000 == 0 else ""
    resultado = f"{_inteiro_por_extenso(reais)}{de} {real}"
    if cents:
        cent = "centavo" if cents == 1 else "centavos"
        resultado += f" e {_inteiro_por_extenso(cents)} {cent}"
    return resultado


def _data_br(data_iso, nome):
    try:
        valor = date.fromisoformat(data_iso)
    except (TypeError, ValueError) as exc:
        raise ErroTermoAcordo(f"{nome} deve usar AAAA-MM-DD") from exc
    return valor.strftime("%d/%m/%Y")


def _selecionar_termo(resposta, termo_id, limite):
    termos = gerar_termos(resposta, limite)["termos"]
    if not termos:
        raise ErroTermoAcordo("o painel não gerou Termo de Opção válido")
    if termo_id is None:
        if len(termos) != 1:
            raise ErroTermoAcordo("há mais de um cenário; informe --termo TO-NNN")
        return termos[0]
    for termo in termos:
        if termo["id"] == termo_id:
            return termo
    raise ErroTermoAcordo(f"Termo de Opção inexistente: {termo_id}")


def _validar_pessoa(partes, papel):
    pessoa = partes.get(papel) if isinstance(partes, dict) else None
    if not isinstance(pessoa, dict):
        raise ErroTermoAcordo(f"dados das partes não contêm {papel}")
    return {
        "nome": _texto(pessoa, "nome"),
        "cpf_cnpj": _texto(pessoa, "cpf_cnpj"),
        "qualificacao": _texto(pessoa, "qualificacao"),
        "endereco": _texto(pessoa, "endereco"),
    }


def _rotulo_percentual(valor):
    normalizado = format(valor.normalize(), "f")
    return normalizado.replace(".", ",") + "%"


def _dados_monetarios(item, percentuais, valores, pagamentos):
    pedido_id = item["pedido_id"]
    negociacao = item.get("negociacao") or {}
    opcao = negociacao.get("opcao") or {}
    tipo = opcao.get("tipo")
    if tipo == "formula":
        if pedido_id not in percentuais:
            raise ErroTermoAcordo(f"falta --percentual {pedido_id}=VALOR")
        percentual = _decimal(percentuais.pop(pedido_id), f"percentual de {pedido_id}")
        if percentual < 0 or percentual > 100:
            raise ErroTermoAcordo(f"percentual de {pedido_id} deve ficar entre 0 e 100")
        base = (opcao.get("base") or {}).get("valor_centavos")
        if not isinstance(base, int) or isinstance(base, bool) or base < 0:
            raise ErroTermoAcordo(f"{pedido_id} não contém base monetária válida")
        centavos = int((Decimal(base) * percentual / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        faixa = negociacao.get("faixa_discussao_centavos")
        if (isinstance(faixa, list) and len(faixa) == 2
                and all(isinstance(v, int) and not isinstance(v, bool) for v in faixa)
                and not faixa[0] <= centavos <= faixa[1]):
            raise ErroTermoAcordo(f"resultado da fórmula de {pedido_id} está fora da faixa aprovada")
        criterio = f"{_rotulo_percentual(percentual)} da base de {_brl(base)}"
    elif tipo == "faixa":
        if pedido_id not in valores:
            raise ErroTermoAcordo(f"falta --valor {pedido_id}=REAIS")
        centavos = _centavos(valores.pop(pedido_id), f"valor de {pedido_id}")
        faixa = negociacao.get("faixa_discussao_centavos") or negociacao.get("faixa_centavos")
        if (not isinstance(faixa, list) or len(faixa) != 2
                or not all(isinstance(v, int) and not isinstance(v, bool) for v in faixa)):
            raise ErroTermoAcordo(f"{pedido_id} não contém faixa válida")
        if not faixa[0] <= centavos <= faixa[1]:
            raise ErroTermoAcordo(f"valor de {pedido_id} está fora da faixa aprovada")
        criterio = "valor certo escolhido dentro da faixa aprovada"
    else:
        raise ErroTermoAcordo(f"tipo monetário desconhecido em {pedido_id}")
    pagamento = pagamentos.get(pedido_id) if isinstance(pagamentos, dict) else None
    if not isinstance(pagamento, dict):
        raise ErroTermoAcordo(f"dados formais não contêm pagamentos.{pedido_id}")
    pagador = opcao.get("pagador")
    beneficiario = opcao.get("beneficiario")
    if pagador not in {"requerente", "requerido"} or beneficiario not in {"requerente", "requerido"}:
        raise ErroTermoAcordo(f"{pedido_id} não define pagador e beneficiário válidos")
    if pagador == beneficiario:
        raise ErroTermoAcordo(f"{pedido_id} define a mesma parte como pagador e beneficiário")
    return {
        "pedido_id": pedido_id,
        "descricao": corrigir_portugues(str(item.get("descricao") or pedido_id)).strip().rstrip("."),
        "tipo": tipo,
        "centavos": centavos,
        "valor": _brl(centavos),
        "valor_por_extenso": valor_por_extenso(centavos),
        "criterio": criterio,
        "vencimento": _data_br(_texto(pagamento, "vencimento"), f"pagamentos.{pedido_id}.vencimento"),
        "forma": _texto(pagamento, "forma"),
        "pagador": pagador,
        "beneficiario": beneficiario,
    }


def gerar_acordo(
    resposta, dados, percentuais=None, valores=None, termo_id=None,
    max_combinations=256, rascunho=False,
):
    if not isinstance(dados, dict):
        raise ErroTermoAcordo("dados formais devem ser um objeto JSON")
    if rascunho:
        dados = _dados_ficticios(dados)
    aceite = dados.get("aceite")
    if not isinstance(aceite, dict) or aceite.get("todos_concordam") is not True:
        raise ErroTermoAcordo("o acordo exige aceite.todos_concordam=true")
    termo_config = aceite.get("termo_opcao_id")
    if termo_id and termo_config and termo_id != termo_config:
        raise ErroTermoAcordo("--termo diverge de aceite.termo_opcao_id")
    termo = _selecionar_termo(resposta, termo_id or termo_config, max_combinations)
    case_id, versao, _painel, pedidos = extrair_painel(resposta)
    por_id = {item["pedido_id"]: item for item in pedidos}
    aceitos = [e["pedido_id"] for e in termo["escolhas"] if e["decisao"] == "aceitar"]
    if not aceitos:
        raise ErroTermoAcordo("o cenário selecionado não contém opção aceita")

    partes = {
        "requerente": _validar_pessoa(dados.get("partes"), "requerente"),
        "requerido": _validar_pessoa(dados.get("partes"), "requerido"),
    }
    mediador_dados = dados.get("mediador")
    if not isinstance(mediador_dados, dict):
        raise ErroTermoAcordo("dados formais não contêm mediador")
    mediador = {"nome": _texto(mediador_dados, "nome"), "qualificacao": _texto(mediador_dados, "qualificacao")}
    local = _texto(dados, "local")
    data_assinatura = _data_br(_texto(dados, "data_assinatura"), "data_assinatura")
    resumo = _texto(dados, "resumo_conflito")
    assinatura = dados.get("assinatura")
    if not isinstance(assinatura, dict) or assinatura.get("partes_e_mediador") is not True:
        raise ErroTermoAcordo("assinatura.partes_e_mediador deve ser true")

    percentuais = dict(percentuais or {})
    valores = dict(valores or {})
    obrigacoes = []
    for pedido_id in aceitos:
        item = por_id[pedido_id]
        tipo = ((item.get("negociacao") or {}).get("opcao") or {}).get("tipo")
        if tipo in TIPOS_MONETARIOS:
            obrigacoes.append(_dados_monetarios(item, percentuais, valores, dados.get("pagamentos")))
        else:
            info = (dados.get("obrigacoes") or {}).get(pedido_id)
            if not isinstance(info, dict):
                raise ErroTermoAcordo(f"dados formais não contêm obrigacoes.{pedido_id}")
            obrigacoes.append({
                "pedido_id": pedido_id,
                "descricao": corrigir_portugues(str(item.get("descricao") or pedido_id)).strip().rstrip("."),
                "tipo": tipo,
                "responsavel": _texto(info, "responsavel"),
                "prestacao": _texto(info, "prestacao"),
                "prazo": _texto(info, "prazo"),
            })
    if percentuais:
        raise ErroTermoAcordo("percentual informado para pedido não aceito ou não existente: " + ", ".join(percentuais))
    if valores:
        raise ErroTermoAcordo("valor informado para pedido não aceito ou não existente: " + ", ".join(valores))

    inadimplemento = dados.get("inadimplemento")
    if inadimplemento is not None and not isinstance(inadimplemento, dict):
        raise ErroTermoAcordo("inadimplemento deve ser objeto JSON")
    resultado = {
        "schema_version": SCHEMA_VERSION,
        "tipo": "termo_final_mediacao",
        "case_id": case_id,
        "versao_origem": versao,
        "termo_opcao_id": termo["id"],
        "partes": partes,
        "mediador": mediador,
        "local": local,
        "data_assinatura": data_assinatura,
        "resumo_conflito": resumo,
        "obrigacoes": obrigacoes,
        "confidencialidade": dados.get("confidencialidade") is True,
        "inadimplemento": inadimplemento or {},
        "foro": dados.get("foro") if isinstance(dados.get("foro"), str) else None,
        "duas_testemunhas": assinatura.get("duas_testemunhas") is True,
        "advogados": dados.get("advogados") if isinstance(dados.get("advogados"), list) else [],
        "rascunho": bool(rascunho),
    }
    resultado["texto_markdown"] = renderizar_markdown(resultado)
    return resultado


def _nome_papel(resultado, papel):
    return resultado["partes"].get(papel, {}).get("nome", papel)


def renderizar_markdown(resultado):
    req = resultado["partes"]["requerente"]
    rdo = resultado["partes"]["requerido"]
    linhas = []
    if resultado["rascunho"]:
        linhas.extend([
            "# RASCUNHO — SIMULAÇÃO SEM VALIDADE", "",
            "> **DADOS FICTÍCIOS. NÃO ASSINAR. ESTE DOCUMENTO NÃO CONSTITUI ACORDO NEM TÍTULO EXECUTIVO.**", "",
        ])
    linhas.extend([
        "# TERMO FINAL DE MEDIAÇÃO E ACORDO EXTRAJUDICIAL", "",
        f"**Caso de referência:** {resultado['case_id']}  ",
        f"**Cenário aceito:** {resultado['termo_opcao_id']}  ",
        f"**Local e data:** {resultado['local']}, {resultado['data_assinatura']}", "",
        "## 1. Partes e mediador", "",
        f"**REQUERENTE:** {req['nome']}, {req['qualificacao']}, inscrito(a) no CPF/CNPJ sob nº {req['cpf_cnpj']}, com endereço em {req['endereco']}.", "",
        f"**REQUERIDO:** {rdo['nome']}, {rdo['qualificacao']}, inscrito(a) no CPF/CNPJ sob nº {rdo['cpf_cnpj']}, com endereço em {rdo['endereco']}.", "",
        f"**MEDIADOR:** {resultado['mediador']['nome']}, {resultado['mediador']['qualificacao']}.", "",
        "As partes acima identificadas declaram que participaram voluntariamente da mediação, compreenderam seus termos e, por livre manifestação de vontade, celebram o presente acordo.", "",
        "## 2. Resumo e objeto do conflito", "", resultado["resumo_conflito"].rstrip(".") + ".", "",
        "O acordo limita-se aos seguintes pedidos:", "",
    ])
    for ob in resultado["obrigacoes"]:
        linhas.append(f"- **{ob['pedido_id']}:** {ob['descricao']}.")
    linhas.extend(["", "## 3. Obrigações assumidas", ""])
    for numero, ob in enumerate(resultado["obrigacoes"], 1):
        if ob["tipo"] in TIPOS_MONETARIOS:
            pagador = _nome_papel(resultado, ob["pagador"])
            beneficiario = _nome_papel(resultado, ob["beneficiario"])
            linhas.extend([
                f"### 3.{numero}. {ob['pedido_id']}", "",
                f"{pagador} pagará a {beneficiario} o valor certo de **{ob['valor']} ({ob['valor_por_extenso']})**, definido por {ob['criterio']}, com vencimento em **{ob['vencimento']}**, por meio de {ob['forma']}.", "",
            ])
        else:
            linhas.extend([
                f"### 3.{numero}. {ob['pedido_id']}", "",
                f"{ob['responsavel']} obriga-se a {ob['prestacao']}, no prazo de {ob['prazo']}.", "",
            ])
    inad = resultado["inadimplemento"]
    if inad:
        termos = []
        if inad.get("multa_percentual") is not None:
            termos.append(f"multa de {_rotulo_percentual(_decimal(inad['multa_percentual'], 'multa_percentual'))}")
        if inad.get("juros_mensais_percentual") is not None:
            termos.append(f"juros de {_rotulo_percentual(_decimal(inad['juros_mensais_percentual'], 'juros_mensais_percentual'))} ao mês")
        if inad.get("correcao_indice"):
            termos.append("correção monetária pelo índice " + str(inad["correcao_indice"]).strip())
        if termos:
            linhas.extend(["## 4. Inadimplemento", "", "O atraso no pagamento acarretará " + ", ".join(termos) + ".", ""])
    linhas.extend([
        "## 5. Quitação", "",
        "A quitação será concedida somente após o cumprimento integral das obrigações deste Termo e ficará restrita aos pedidos expressamente relacionados na cláusula 2, sem alcançar matérias estranhas ao seu objeto.", "",
    ])
    if resultado["confidencialidade"]:
        linhas.extend([
            "## 6. Confidencialidade", "",
            "As partes manterão a confidencialidade das informações da mediação, ressalvadas as hipóteses legais e a divulgação necessária ao cumprimento ou à execução deste acordo.", "",
        ])
    linhas.extend([
        "## 7. Declarações finais", "",
        "As partes afirmam que o texto foi lido, compreendido e aceito, que as obrigações estão descritas de forma clara e que tiveram oportunidade de buscar orientação jurídica.", "",
        "Este Termo encerra a mediação quanto ao objeto acordado. Uma vez devidamente assinado, constitui título executivo extrajudicial nos termos do art. 20, parágrafo único, da Lei nº 13.140/2015, sem prejuízo de outros requisitos legais aplicáveis ao caso concreto.", "",
    ])
    if resultado["foro"]:
        linhas.extend(["## 8. Foro", "", f"Para as medidas judiciais cabíveis, fica indicado o foro de {resultado['foro'].strip()}, observadas as regras legais de competência.", ""])
    linhas.extend([
        "E, por estarem de acordo, assinam o presente Termo.", "",
        f"{resultado['local']}, {resultado['data_assinatura']}.", "",
    ])
    if resultado["rascunho"]:
        linhas.extend([
            "## Assinaturas", "",
            "**Campos de assinatura suprimidos no modo rascunho. Gere novamente sem `--rascunho`, após preencher e conferir os dados reais.**", "",
        ])
    else:
        linhas.extend([
            "---", f"**{req['nome']}**  ", "Requerente", "",
            "---", f"**{rdo['nome']}**  ", "Requerido", "",
            "---", f"**{resultado['mediador']['nome']}**  ", "Mediador", "",
        ])
        for advogado in resultado["advogados"]:
            if isinstance(advogado, dict) and advogado.get("nome") and advogado.get("oab"):
                linhas.extend(["---", f"**{advogado['nome']} — {advogado['oab']}**  ", "Advogado(a)", ""])
        if resultado["duas_testemunhas"]:
            linhas.extend([
                "## Testemunhas", "",
                "1. ____________________________________  ", "Nome:  ", "CPF:", "",
                "2. ____________________________________  ", "Nome:  ", "CPF:", "",
            ])
    return "\n".join(linhas).rstrip() + "\n"


def renderizar_html(resultado):
    corpo = _markdown_para_html_fragmento(resultado["texto_markdown"])
    titulo = escape(f"Termo Final de Mediação — Caso {resultado['case_id']}", quote=True)
    classe = ' class="rascunho"' if resultado["rascunho"] else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titulo}</title>
  <style>
    :root {{ font-family: Georgia, "Times New Roman", serif; color: #222; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #edf1f4; line-height: 1.55; }}
    main {{ width: min(900px, calc(100% - 32px)); margin: 32px auto; padding: 52px 64px; background: white; box-shadow: 0 8px 28px #0001; }}
    h1 {{ text-align: center; font-size: 1.35rem; letter-spacing: .06em; margin: 0 0 30px; }}
    h2 {{ font-size: 1.05rem; text-transform: uppercase; margin: 28px 0 10px; }}
    h3 {{ font-size: 1rem; margin: 20px 0 8px; }}
    p, li {{ text-align: justify; }}
    hr {{ border: 0; border-top: 1px solid #555; margin: 42px 0 5px; width: 55%; }}
    .rascunho main {{ border: 5px solid #a61b1b; }}
    .rascunho h1:first-child, .rascunho blockquote {{ color: #8b1111; }}
    .rascunho::before {{ content: "RASCUNHO · DADOS FICTÍCIOS"; position: fixed; inset: 45% auto auto 8%; z-index: 2; color: rgba(139, 17, 17, .09); font: bold 4rem Arial, sans-serif; transform: rotate(-24deg); pointer-events: none; }}
    blockquote {{ margin: 18px 0 30px; padding: 14px 18px; border: 2px solid #a61b1b; background: #fff4f4; }}
    @page {{ size: A4; margin: 18mm; }}
    @media print {{ body {{ background: white; }} main {{ width: auto; margin: 0; padding: 0; box-shadow: none; }} }}
  </style>
</head>
<body{classe}><main>{corpo}</main></body>
</html>
"""


def carregar_dados(caminho):
    try:
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ErroTermoAcordo(f"não foi possível ler dados formais: {exc}") from exc
    if not isinstance(dados, dict):
        raise ErroTermoAcordo("dados formais devem ser um objeto JSON")
    return dados


def escrever_saida(conteudo, destino):
    if destino == "-":
        sys.stdout.write(conteudo)
    else:
        path = Path(destino)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(conteudo, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="resposta JSON de get_case")
    parser.add_argument("--dados", required=True, help="JSON com aceite e dados formais")
    parser.add_argument("--termo", help="ID do cenário, por exemplo TO-001")
    parser.add_argument("--percentual", action="append", default=[], help="PEDIDO=PERCENTUAL; pode repetir")
    parser.add_argument("--valor", action="append", default=[], help="PEDIDO=REAIS para opção de faixa; pode repetir")
    parser.add_argument(
        "--rascunho", action="store_true",
        help="simula identidades fictícias, marca a saída sem validade e suprime assinaturas",
    )
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument("--output", "-o", default="-", help="arquivo de saída, ou - para stdout")
    parser.add_argument("--max-combinations", type=int, default=256)
    args = parser.parse_args(argv)
    try:
        percentuais, percentual_unico = _mapear_argumentos(args.percentual, "--percentual", True)
        valores, _ = _mapear_argumentos(args.valor, "--valor")
        resposta = carregar_resposta(args.entrada)
        if percentual_unico is not None:
            _case, _versao, _painel, pedidos = extrair_painel(resposta)
            formulas = [
                p["pedido_id"] for p in pedidos
                if (((p.get("negociacao") or {}).get("opcao") or {}).get("tipo") == "formula")
            ]
            if len(formulas) != 1:
                raise ErroTermoAcordo("percentual abreviado exige exatamente uma fórmula no painel")
            percentuais[formulas[0]] = percentual_unico
        resultado = gerar_acordo(
            resposta, carregar_dados(args.dados), percentuais, valores,
            termo_id=args.termo, max_combinations=args.max_combinations,
            rascunho=args.rascunho,
        )
        if args.format == "markdown":
            conteudo = resultado["texto_markdown"]
        elif args.format == "html":
            conteudo = renderizar_html(resultado)
        else:
            conteudo = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        escrever_saida(conteudo, args.output)
    except (ErroTermoAcordo, ErroTermoMediador, OSError) as exc:
        parser.exit(2, f"erro: {exc}\n")


if __name__ == "__main__":
    main()
