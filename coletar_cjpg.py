#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coleta sentenças públicas do Banco de Sentenças do TJSP (CJPG).
Uso:  python coletar_cjpg.py --saida sentencas.jsonl --por-categoria 25
Ritmo respeitoso: 1 requisição a cada DELAY segundos. Não abuse.
"""
import argparse, json, re, time, sys
import requests
from bs4 import BeautifulSoup

BASE = "https://esaj.tjsp.jus.br/cjpg"
DELAY = 3.0  # segundos entre requisições — seja educado com o tribunal

# Categorias "mediáveis" e suas buscas no CJPG
CATEGORIAS = {
    "locacao":      '"contrato de locação" caução "julgo"',
    "cobranca":     '"ação de cobrança" "prestação de serviços" "julgo procedente"',
    "consumo":      '"vício do produto" consumidor "julgo procedente"',
    "transito":     '"acidente de trânsito" colisão "danos materiais" "julgo"',
    "reforma":      '"contrato de empreitada" reforma vícios "julgo"',
    "vizinhanca":   '"direito de vizinhança" infiltração "julgo"',
    "condominio":   'condomínio "taxa condominial" cobrança "julgo"',
    "divida":       '"instrumento particular de confissão de dívida" "julgo"',
    "servicos":     '"má prestação de serviços" restituição "julgo"',
    "veiculo_venda":'"compra e venda de veículo" vício "julgo"',
}

UA = {"User-Agent": "Mozilla/5.0 (pesquisa acadêmica; contato: voce@exemplo.com)"}

def texto_limpo(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True))

def parse_pagina(html):
    """Extrai os resultados de uma página de listagem do CJPG."""
    soup = BeautifulSoup(html, "html.parser")
    resultados = []
    # Cada resultado fica numa <tr class="fundocinza1"> contendo uma tabela interna
    for tr in soup.select("tr.fundocinza1"):
        bloco = texto_limpo(tr)
        m = re.search(r"(\d{7}-\d{2}\.\d{4}\.8\.26\.\d{4})", bloco)
        if not m:
            continue
        item = {"processo": m.group(1)}
        for campo, rotulo in [("classe", "Classe:"), ("assunto", "Assunto:"),
                              ("magistrado", "Magistrado:"), ("comarca", "Comarca:"),
                              ("foro", "Foro:"), ("vara", "Vara:"),
                              ("data", "Data de Disponibilização:")]:
            mm = re.search(rotulo + r"\s*(.*?)(?=(Classe:|Assunto:|Magistrado:|Comarca:|Foro:|Vara:|Data de Disponibilização:|$))", bloco)
            if mm:
                item[campo] = mm.group(1).strip()
        # o corpo da sentença exibido na listagem (pode vir truncado)
        divs = tr.select("div[style*='display: none'], div.mensagemSemFormatacao, td div")
        corpo = max((texto_limpo(d) for d in divs), key=len, default="")
        item["texto"] = corpo if len(corpo) > 200 else bloco
        resultados.append(item)
    return resultados

def coletar(sess, consulta, max_docs):
    docs, pagina = [], 1
    r = sess.get(f"{BASE}/pesquisar.do", params={
        "dadosConsulta.pesquisaLivre": consulta,
        "dadosConsulta.tipoConsulta": "sentenca"}, headers=UA, timeout=60)
    while len(docs) < max_docs:
        novos = parse_pagina(r.text)
        if not novos:
            break
        docs.extend(novos)
        pagina += 1
        time.sleep(DELAY)
        r = sess.get(f"{BASE}/trocarDePagina.do", params={"pagina": pagina},
                     headers=UA, timeout=60)
    return docs[:max_docs]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default="sentencas.jsonl")
    ap.add_argument("--por-categoria", type=int, default=25)
    args = ap.parse_args()

    vistos = set()
    with open(args.saida, "w", encoding="utf-8") as out:
        for cat, consulta in CATEGORIAS.items():
            print(f"[{cat}] buscando: {consulta}")
            sess = requests.Session()
            try:
                docs = coletar(sess, consulta, args.por_categoria)
            except Exception as e:
                print(f"  ERRO em {cat}: {e}", file=sys.stderr)
                continue
            n = 0
            for d in docs:
                if d["processo"] in vistos or len(d.get("texto", "")) < 400:
                    continue
                vistos.add(d["processo"])
                d["categoria"] = cat
                out.write(json.dumps(d, ensure_ascii=False) + "\n")
                n += 1
            print(f"  {n} sentenças salvas")
            time.sleep(DELAY)
    print(f"Total: {len(vistos)} sentenças em {args.saida}")

if __name__ == "__main__":
    main()
