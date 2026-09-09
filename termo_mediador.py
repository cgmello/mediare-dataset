#!/usr/bin/env python3
"""Transforma a resposta de get_case em Termos de Opção para o mediador.

O processamento é inteiramente off-chain. O script não chama o Studio, não
altera o Intelligent Contract e não decide o mérito do caso. Ele combina apenas
as opções que o painel já marcou como aptas para discussão.
"""

import argparse
from html import escape
import itertools
import json
from pathlib import Path
import re
import sys


SCHEMA_VERSION = 1
TIPOS_APROVADOS = {"faixa", "formula", "nao_monetaria", "diligencia"}
RISCO_PT = {
    "SEM_SUPORTE": "sem suporte",
    "VALOR_INVENTADO": "valor inventado",
    "DUPLA_CONTAGEM": "dupla contagem",
    "ESCOPO": "escopo",
    "POLO": "polo incorreto",
    "PREMISSA": "premissa",
    "OUTRO": "outro risco",
}
DECISAO_PT = {
    "conceder": "acolher o pedido",
    "negar": "negar o pedido",
    "necessita_informacao": "necessidade de informação adicional",
    "fora_de_escopo": "pedido fora do escopo",
}

# Vocabulário recorrente nos textos determinísticos das versões atuais do IC.
# Não tenta reescrever estilo ou mérito; apenas corrige grafias inequivocamente
# sem acento que podem aparecer nos campos textuais do painel.
ACENTOS = {
    "acao": "ação", "acoes": "ações", "aceitacao": "aceitação", "alem": "além",
    "analise": "análise", "apuracao": "apuração", "automatico": "automático",
    "calculo": "cálculo",
    "composicao": "composição", "condicao": "condição", "condicoes": "condições",
    "construcao": "construção", "contratacao": "contratação", "credito": "crédito",
    "conclusao": "conclusão", "conclusoes": "conclusões", "contribuicao": "contribuição",
    "criterio": "critério", "decisao": "decisão", "decisoes": "decisões",
    "debito": "débito", "declaracao": "declaração", "diligencia": "diligência",
    "diligencias": "diligências", "divida": "dívida", "documentacao": "documentação",
    "execucao": "execução", "extensao": "extensão",
    "formula": "fórmula", "formulas": "fórmulas", "informacao": "informação",
    "imovel": "imóvel", "indenizacao": "indenização", "infiltracao": "infiltração",
    "infiltracoes": "infiltrações", "informacoes": "informações",
    "juridica": "jurídica", "liquida": "líquida", "liquido": "líquido",
    "mediacao": "mediação", "merito": "mérito", "monetaria": "monetária",
    "monetario": "monetário", "nao": "não", "numero": "número", "numeros": "números",
    "obrigacao": "obrigação", "obrigacoes": "obrigações", "opcao": "opção",
    "opcoes": "opções", "orcamento": "orçamento", "participacao": "participação",
    "pericia": "perícia", "possivel": "possível", "premissa": "premissa",
    "proporcao": "proporção", "propria": "própria", "proprio": "próprio",
    "reparacao": "reparação", "responsabilizacao": "responsabilização",
    "tecnica": "técnica", "tecnico": "técnico", "ultima": "última", "ultimo": "último",
    "vicio": "vício", "vicios": "vícios", "vinculo": "vínculo",
}


class ErroTermoMediador(ValueError):
    """Entrada incompatível com o pós-processador."""


def _preservar_caixa(original, corrigida):
    if original.isupper():
        return corrigida.upper()
    if original[:1].isupper():
        return corrigida[:1].upper() + corrigida[1:]
    return corrigida


def corrigir_portugues(texto):
    """Corrige o vocabulário sem acento conhecido, preservando o conteúdo."""
    if not isinstance(texto, str):
        return ""
    palavras = "|".join(sorted(map(re.escape, ACENTOS), key=len, reverse=True))

    def substituir(match):
        original = match.group(0)
        return _preservar_caixa(original, ACENTOS[original.lower()])

    corrigido = re.sub(r"\b(?:" + palavras + r")\b", substituir, texto, flags=re.IGNORECASE)
    # Casos inequívocos do verbo ser. Não se troca "e" isoladamente porque ele
    # também pode ser a conjunção correta.
    corrigido = re.sub(r"\b([Qq]ual|[Oo] que|[Ii]sto|[Ee]le|[Ee]la) e\b", r"\1 é", corrigido)
    return corrigido


def _decodificar_json(valor, nome="entrada"):
    """Aceita objeto, JSON normal ou resposta JSON codificada como string."""
    atual = valor
    for _ in range(4):
        if not isinstance(atual, str):
            break
        try:
            atual = json.loads(atual)
        except json.JSONDecodeError as exc:
            # Um texto copiado do Studio pode trazer, depois da resposta, o nome
            # da próxima chamada exibida pela interface. Na entrada externa,
            # consome-se somente o primeiro valor JSON completo e ignora-se o
            # rodapé; dentro de painel, conteúdo excedente continua sendo erro.
            if nome == "entrada" and exc.msg == "Extra data":
                try:
                    atual, _fim = json.JSONDecoder().raw_decode(atual.lstrip())
                    continue
                except json.JSONDecodeError:
                    pass
            raise ErroTermoMediador(f"{nome} não contém JSON válido: {exc.msg}") from exc
    if not isinstance(atual, dict):
        raise ErroTermoMediador(f"{nome} deve resultar em um objeto JSON")
    return atual


def carregar_resposta(origem):
    if origem == "-":
        conteudo = sys.stdin.read()
    else:
        conteudo = Path(origem).read_text(encoding="utf-8")
    return _decodificar_json(conteudo)


def extrair_painel(resposta):
    resposta = _decodificar_json(resposta)
    painel = _decodificar_json(resposta.get("painel"), "painel")
    consolidado = painel.get("consolidado")
    pedidos = consolidado.get("pedidos") if isinstance(consolidado, dict) else None
    if not isinstance(pedidos, list) or not pedidos:
        raise ErroTermoMediador("painel não contém pedidos consolidados")
    ids = [item.get("pedido_id") for item in pedidos if isinstance(item, dict)]
    if (len(ids) != len(pedidos) or any(not isinstance(pid, str) or not pid for pid in ids)
            or len(ids) != len(set(ids))):
        raise ErroTermoMediador("pedidos consolidados devem ter IDs textuais únicos")
    case_id = resposta.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise ErroTermoMediador("resposta não contém case_id")
    versao = resposta.get("versao") or painel.get("versao")
    if not isinstance(versao, str) or not versao:
        raise ErroTermoMediador("resposta não contém versão")
    return case_id, versao, painel, pedidos


def _brl(centavos):
    if not isinstance(centavos, int) or isinstance(centavos, bool) or centavos < 0:
        return None
    reais, cents = divmod(centavos, 100)
    return "R$ " + f"{reais:,}".replace(",", ".") + f",{cents:02d}"


def _descricao(item):
    texto = item.get("descricao") or f"pedido {item.get('pedido_id', 'sem ID')}"
    return corrigir_portugues(str(texto)).strip().rstrip(".")


def _negociacao(item):
    valor = item.get("negociacao")
    return valor if isinstance(valor, dict) else {}


def _opcao_aprovada(item):
    negociacao = _negociacao(item)
    opcao = negociacao.get("opcao") or {}
    auditoria = negociacao.get("auditoria") or {}
    return (
        negociacao.get("estado") == "condicional"
        and opcao.get("tipo") in TIPOS_APROVADOS
        and auditoria.get("resultado") != "reformular"
    )


def _conflitos(item):
    auditoria = _negociacao(item).get("auditoria") or {}
    conflitos = auditoria.get("conflitos_com") or []
    return {str(valor) for valor in conflitos if isinstance(valor, str)}


def _combinacoes_validas(aprovados, maximo):
    if maximo < 1:
        raise ErroTermoMediador("max_combinations deve ser pelo menos 1")
    if not aprovados:
        return []
    ids = [item.get("pedido_id") for item in aprovados]
    resultado = []
    for escolhas in itertools.product((True, False), repeat=len(aprovados)):
        # Um documento sem nenhuma opção aceita não é um Termo de Opção útil.
        if not any(escolhas):
            continue
        aceitos = {ids[i] for i, escolha in enumerate(escolhas) if escolha}
        invalida = any(
            escolhas[i] and bool(_conflitos(item) & aceitos)
            for i, item in enumerate(aprovados)
        )
        if invalida:
            continue
        resultado.append(escolhas)
        if len(resultado) > maximo:
            raise ErroTermoMediador(
                f"o painel gera mais de {maximo} combinações; aumente --max-combinations conscientemente"
            )
    return resultado


def _resumo_decisorio(item):
    decisoes = item.get("decisoes_por_lente") or {}
    pares = []
    for lente in ("probatoria", "jurisprudencial"):
        decisao = (decisoes.get(lente) or {}).get("decisao")
        if decisao:
            pares.append((lente, decisao))
    valores = {decisao for _, decisao in pares}
    if len(pares) == 2 and len(valores) == 1:
        decisao = DECISAO_PT.get(next(iter(valores)), corrigir_portugues(next(iter(valores))))
        return f"As lentes probatória e jurisprudencial convergiram em {decisao}."
    if pares:
        partes = [f"{lente}: {DECISAO_PT.get(decisao, corrigir_portugues(decisao))}" for lente, decisao in pares]
        if len(pares) == 1:
            return "Somente uma lente decisória foi registrada (" + partes[0] + ")."
        return "Não houve consenso entre as lentes decisórias (" + "; ".join(partes) + ")."
    status = DECISAO_PT.get(item.get("status"), corrigir_portugues(str(item.get("status") or "indefinido")))
    return "O painel registrou " + status + "."


def _texto_opcao_aceita(item):
    pedido_id = item.get("pedido_id", "sem ID")
    negociacao = _negociacao(item)
    opcao = negociacao.get("opcao") or {}
    tipo = opcao.get("tipo")
    faixa = negociacao.get("faixa_discussao_centavos") or negociacao.get("faixa_centavos")
    faixa_texto = None
    if isinstance(faixa, list) and len(faixa) == 2:
        minimo, maximo = _brl(faixa[0]), _brl(faixa[1])
        if minimo and maximo:
            faixa_texto = f"{minimo} a {maximo}"

    if tipo == "formula":
        base = _brl((opcao.get("base") or {}).get("valor_centavos"))
        complemento = f", usando a base de {base} e percentual (%) a definir" if base else ""
        if faixa_texto:
            complemento += f", dentro da faixa de {faixa_texto}"
        return f"As partes aceitam negociar o {pedido_id}{complemento}."
    if tipo == "faixa":
        complemento = f", na faixa de {faixa_texto}" if faixa_texto else ""
        return f"As partes aceitam compor o {pedido_id}{complemento}."
    if tipo == "nao_monetaria":
        return f"As partes aceitam discutir uma solução não monetária para o {pedido_id}."
    pergunta = (((item.get("analises") or {}).get("probatoria") or {}).get("lacuna") or {}).get("pergunta")
    detalhe = ": " + corrigir_portugues(pergunta).strip().rstrip(".") if pergunta else ""
    return f"As partes aceitam realizar a diligência necessária ao {pedido_id}{detalhe}."


def _texto_opcao_rejeitada(item):
    return (
        f"As partes não adotam, neste cenário, a opção referente ao {item.get('pedido_id', 'sem ID')}. "
        "O pedido permanece sem composição."
    )


def _fontes_opcao(item):
    fontes = ((_negociacao(item).get("opcao") or {}).get("fontes") or [])
    return ", ".join(str(fonte) for fonte in fontes) or "não informadas"


def _identificacao_pedido(item):
    pedido_id = item.get("pedido_id", "sem ID")
    partes = [
        f"**{pedido_id}** identifica o pedido relativo a: {_descricao(item)}.",
        _resumo_decisorio(item),
    ]
    if _opcao_aprovada(item):
        partes.append("Há uma opção condicional disponível para discussão.")
    else:
        negociacao = _negociacao(item)
        auditoria = negociacao.get("auditoria") or {}
        riscos = [
            RISCO_PT.get(risco, corrigir_portugues(str(risco)).lower())
            for risco in auditoria.get("riscos") or []
        ]
        if riscos:
            partes.append("A alternativa foi retida pela auditoria por: " + ", ".join(riscos) + ".")
        partes.append("Por isso, nenhuma opção de Termo é apresentada para este pedido.")
    return " ".join(partes)


def _renderizar_termo(numero, case_id, versao, pedidos, aprovados, escolhas):
    escolhidos = {id(item): escolhas[i] for i, item in enumerate(aprovados)}
    aceitos = [item for item in aprovados if escolhidos[id(item)]]
    rejeitados = [item for item in aprovados if not escolhidos[id(item)]]

    linhas = [
        f"# Termo de Opção Nr. {numero}", "",
        f"**Caso:** {case_id}  ",
        f"**Versão de origem:** {versao}  ",
        "**Finalidade:** cenário objetivo para discussão pelo mediador.",
        "", "## Identificação dos pedidos", "",
    ]
    for item in pedidos:
        linhas.append("- " + _identificacao_pedido(item))
    linhas.extend(["", "## Cenário", ""])
    if aceitos:
        for item in aceitos:
            linhas.append("- " + _texto_opcao_aceita(item))
    if rejeitados:
        for item in rejeitados:
            linhas.append("- " + _texto_opcao_rejeitada(item))
    linhas.extend(["", "## Valores e condições das opções aceitas", ""])
    for item in aceitos:
        negociacao = _negociacao(item)
        opcao = negociacao.get("opcao") or {}
        linhas.append(f"### {item.get('pedido_id')}")
        linhas.append("")
        linhas.append("- " + _texto_opcao_aceita(item))
        if opcao.get("tipo") == "formula":
            linhas.append("- O percentual (%) será definido pelas partes; a faixa é um limite de discussão, não um valor devido.")
        elif opcao.get("tipo") == "faixa":
            linhas.append("- O valor final deverá permanecer dentro da faixa indicada.")
        auditoria = negociacao.get("auditoria") or {}
        conflitos = auditoria.get("conflitos_com") or []
        if auditoria.get("resultado") == "apta_com_ressalva" and conflitos:
            linhas.append("- Esta opção é alternativa e não pode ser somada a: " + ", ".join(conflitos) + ".")
        linhas.append("- Fontes indicadas no painel: " + _fontes_opcao(item) + ".")
        linhas.append("")

    linhas.extend([
        "## Registro da sessão de mediação", "",
        "- [ ] Cenário selecionado pelas partes",
        "- [ ] Cenário rejeitado pelas partes",
        "- [ ] Necessita de nova proposta",
        "", "**Observações do mediador:** ________________________________________________",
    ])
    texto = "\n".join(linhas).rstrip() + "\n"
    return {
        "id": f"TO-{numero:03d}",
        "titulo": f"Termo de Opção Nr. {numero}",
        "escolhas": [
            {"pedido_id": item.get("pedido_id"), "decisao": "aceitar" if escolhidos[id(item)] else "não aceitar"}
            for item in aprovados
        ],
        "texto_markdown": texto,
    }


def gerar_termos(resposta, max_combinations=256):
    case_id, versao, _painel, pedidos = extrair_painel(resposta)
    aprovados = [item for item in pedidos if _opcao_aprovada(item)]
    combinacoes = _combinacoes_validas(aprovados, max_combinations)
    termos = [
        _renderizar_termo(i, case_id, versao, pedidos, aprovados, escolhas)
        for i, escolhas in enumerate(combinacoes, 1)
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "tipo": "termos_opcao_mediador",
        "case_id": case_id,
        "versao_origem": versao,
        "opcoes_aprovadas": [item.get("pedido_id") for item in aprovados],
        "combinacoes_total": len(termos),
        "status": "termos_disponiveis" if termos else "sem_termo_valido",
        "motivo_sem_termo": None if termos else "nenhuma_opcao_aprovada",
        "termos": termos,
    }


def renderizar_markdown(resultado):
    if not resultado["termos"]:
        return "# Nenhum Termo de Opção disponível\n\nO painel não contém opção aprovada para composição.\n"
    return "\n\n---\n\n".join(termo["texto_markdown"].rstrip() for termo in resultado["termos"]) + "\n"


def _html_inline(texto):
    """Renderiza o subconjunto inline produzido pelo próprio script."""
    seguro = escape(texto, quote=True)
    seguro = re.sub(r"`([^`]+)`", r"<code>\1</code>", seguro)
    seguro = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", seguro)
    return seguro


def _markdown_para_html_fragmento(markdown):
    """Converte somente o Markdown determinístico acima, sempre escapando dados."""
    saida = []
    lista_aberta = False
    item_aberto = False

    def fechar_lista():
        nonlocal lista_aberta, item_aberto
        if item_aberto:
            saida.append("</li>")
            item_aberto = False
        if lista_aberta:
            saida.append("</ul>")
            lista_aberta = False

    for linha in markdown.splitlines():
        if not linha.strip():
            fechar_lista()
            continue
        titulo = re.match(r"^(#{1,3})\s+(.+)$", linha)
        if titulo:
            fechar_lista()
            nivel = len(titulo.group(1))
            saida.append(f"<h{nivel}>{_html_inline(titulo.group(2))}</h{nivel}>")
            continue
        if linha == "---":
            fechar_lista()
            saida.append('<hr class="separador">')
            continue
        if linha.startswith("- "):
            if not lista_aberta:
                saida.append("<ul>")
                lista_aberta = True
            if item_aberto:
                saida.append("</li>")
            conteudo = linha[2:]
            if conteudo.startswith("[ ] "):
                conteudo = '<span class="caixa" aria-hidden="true">☐</span> ' + _html_inline(conteudo[4:])
            else:
                conteudo = _html_inline(conteudo)
            saida.append("<li>" + conteudo)
            item_aberto = True
            continue
        if linha.startswith("  ") and item_aberto:
            saida.append('<div class="nota-item">' + _html_inline(linha.strip()) + "</div>")
            continue
        fechar_lista()
        saida.append("<p>" + _html_inline(linha.rstrip()) + "</p>")
    fechar_lista()
    return "\n".join(saida)


def renderizar_html(resultado):
    """Gera HTML único, autocontido, seguro e preparado para impressão A4."""
    artigos = "\n".join(
        '<article class="termo">\n'
        + _markdown_para_html_fragmento(termo["texto_markdown"])
        + "\n</article>"
        for termo in resultado["termos"]
    )
    if not artigos:
        artigos = (
            '<section class="termo aviso">\n'
            '<h1>Nenhum Termo de Opção disponível</h1>\n'
            '<p>O painel não contém opção aprovada para composição.</p>\n'
            '</section>'
        )
    titulo = escape(f"Termos de Opção — Caso {resultado['case_id']}", quote=True)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titulo}</title>
  <style>
    :root {{ color-scheme: light; font-family: Arial, Helvetica, sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #eef2f6; color: #1f2937; line-height: 1.5; }}
    main {{ width: min(900px, calc(100% - 32px)); margin: 32px auto; }}
    .termo {{ background: #fff; margin: 0 0 32px; padding: 48px 56px;
              border: 1px solid #d8e0e8; border-radius: 8px;
              box-shadow: 0 8px 24px rgba(15, 35, 55, .08); }}
    h1 {{ margin: 0 0 24px; padding-bottom: 14px; color: #17324d;
          font-size: 1.8rem; border-bottom: 2px solid #2f6f8f; }}
    h2 {{ margin: 30px 0 12px; color: #234a65; font-size: 1.25rem; }}
    h3 {{ margin: 22px 0 10px; color: #315c75; font-size: 1.05rem; }}
    p {{ margin: 8px 0; }}
    ul {{ margin: 8px 0 16px; padding-left: 24px; }}
    li {{ margin: 8px 0; }}
    .nota-item {{ margin-top: 4px; color: #4b5563; }}
    .caixa {{ display: inline-block; width: 1.2em; font-size: 1.15em; }}
    code {{ padding: .08em .3em; border-radius: 3px; background: #edf2f7;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .separador {{ border: 0; border-top: 1px solid #ccd5de; margin: 32px 0; }}
    @page {{ size: A4; margin: 18mm; }}
    @media print {{
      body {{ background: #fff; }}
      main {{ width: auto; margin: 0; }}
      .termo {{ margin: 0; padding: 0; border: 0; border-radius: 0;
                box-shadow: none; break-after: page; page-break-after: always; }}
      .termo:last-child {{ break-after: auto; page-break-after: auto; }}
    }}
  </style>
</head>
<body>
<main>
{artigos}
</main>
</body>
</html>
"""


def escrever_saida(conteudo, destino):
    if destino == "-":
        sys.stdout.write(conteudo)
        return
    path = Path(destino)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(conteudo, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="arquivo com a resposta JSON de get_case, ou - para stdin")
    parser.add_argument("--output", "-o", default="-", help="arquivo de saída, ou - para stdout")
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument("--max-combinations", type=int, default=256)
    args = parser.parse_args(argv)
    try:
        resultado = gerar_termos(carregar_resposta(args.entrada), args.max_combinations)
        if args.format == "markdown":
            conteudo = renderizar_markdown(resultado)
        elif args.format == "html":
            conteudo = renderizar_html(resultado)
        else:
            conteudo = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        escrever_saida(conteudo, args.output)
    except (ErroTermoMediador, OSError) as exc:
        parser.exit(2, f"erro: {exc}\n")


if __name__ == "__main__":
    main()
