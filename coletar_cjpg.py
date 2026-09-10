#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coleta decisões públicas do CJPG/TJSP em lotes pequenos e retomáveis.

O coletor apenas baixa a fonte pública. Ele não chama LLM nem OpenRouter.
Por segurança, o corpo integral nunca é impresso no terminal ou no relatório.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

import requests


BASE = "https://esaj.tjsp.jus.br/cjpg"
DEFAULT_DELAY = 3.0
MAX_BATCH = 50
PROCESSO_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.8\.26\.\d{4}")

CATEGORIAS = {
    "locacao": '"contrato de locação" caução "julgo"',
    "cobranca": '"ação de cobrança" "prestação de serviços" "julgo procedente"',
    "consumo": '"vício do produto" consumidor "julgo procedente"',
    "transito": '"acidente de trânsito" colisão "danos materiais" "julgo"',
    "reforma": '"contrato de empreitada" reforma vícios "julgo"',
    "vizinhanca": '"direito de vizinhança" infiltração "julgo"',
    "condominio": 'condomínio "taxa condominial" cobrança "julgo"',
    "divida": '"instrumento particular de confissão de dívida" "julgo"',
    "servicos": '"má prestação de serviços" restituição "julgo"',
    "veiculo_venda": '"compra e venda de veículo" vício "julgo"',
}

LABELS = (
    ("classe", "Classe:"),
    ("assunto", "Assunto:"),
    ("magistrado", "Magistrado:"),
    ("comarca", "Comarca:"),
    ("foro", "Foro:"),
    ("vara", "Vara:"),
    ("data", "Data de Disponibilização:"),
)
LABEL_LOOKAHEAD = "|".join(re.escape(label) for _, label in LABELS)


def texto_limpo(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class _CjpgListParser(HTMLParser):
    """Captura apenas linhas de resultado e os divs que podem conter a decisão."""

    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.result_depth: int | None = None
        self.parts: list[str] = []
        self.captures: list[dict] = []
        self.capture_stack: list[dict] = []
        self.rows: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in self.VOID_TAGS:
            self.depth += 1
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if tag == "tr" and "fundocinza1" in classes and self.result_depth is None:
            self.result_depth = self.depth
            self.parts = []
            self.captures = []
            self.capture_stack = []
        if self.result_depth is not None and tag == "div":
            style = (attributes.get("style") or "").casefold()
            if "mensagemSemFormatacao" in classes or "display: none" in style:
                capture = {"depth": self.depth, "parts": []}
                self.captures.append(capture)
                self.capture_stack.append(capture)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Elementos autocontidos não alteram a profundidade da linha ativa.
        return None

    def handle_data(self, data: str) -> None:
        if self.result_depth is None:
            return
        self.parts.append(data)
        for capture in self.capture_stack:
            capture["parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.VOID_TAGS:
            return
        if tag == "div" and self.capture_stack:
            capture = self.capture_stack[-1]
            if capture["depth"] == self.depth:
                self.capture_stack.pop()
        if tag == "tr" and self.result_depth == self.depth:
            self.rows.append(
                (
                    texto_limpo(" ".join(self.parts)),
                    [texto_limpo(" ".join(item["parts"])) for item in self.captures],
                )
            )
            self.result_depth = None
            self.parts = []
            self.captures = []
            self.capture_stack = []
        self.depth = max(0, self.depth - 1)


def _metadata(bloco: str, label: str) -> str | None:
    match = re.search(
        re.escape(label) + rf"\s*(.*?)(?=(?:{LABEL_LOOKAHEAD})|$)",
        bloco,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    value = match.group(1).strip()
    # Uma listagem malformada pode misturar o corpo da sentença ao último campo.
    # Metadados longos são descartados, nunca truncados e aceitos silenciosamente.
    if not value or len(value) > 300:
        return None
    return value


def parse_pagina(html: str) -> list[dict]:
    """Extrai decisões da listagem sem registrar texto em logs."""
    parser = _CjpgListParser()
    parser.feed(html)
    resultados: list[dict] = []
    for bloco, candidatos in parser.rows:
        processo = PROCESSO_RE.search(bloco)
        if not processo:
            continue
        item: dict[str, str] = {"processo": processo.group(0)}
        for campo, rotulo in LABELS:
            value = _metadata(bloco, rotulo)
            if value is not None:
                item[campo] = value

        corpo = max(candidatos, key=len, default="")
        # O bloco inteiro é último recurso; ele permanece apenas no arquivo privado.
        item["texto"] = corpo if len(corpo) > 200 else bloco
        resultados.append(item)
    return resultados


def carregar_processos(paths: Iterable[Path]) -> set[str]:
    vistos: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    processo = json.loads(line).get("processo")
                except (json.JSONDecodeError, AttributeError):
                    continue
                if isinstance(processo, str) and PROCESSO_RE.fullmatch(processo):
                    vistos.add(processo)
    return vistos


def _request(session: requests.Session, path: str, params: dict, headers: dict) -> str:
    response = session.get(f"{BASE}/{path}", params=params, headers=headers, timeout=60)
    response.raise_for_status()
    return response.text


def coletar_categoria(
    session: requests.Session,
    consulta: str,
    headers: dict,
    delay: float,
    max_pages: int,
):
    html = _request(
        session,
        "pesquisar.do",
        {
            "dadosConsulta.pesquisaLivre": consulta,
            "dadosConsulta.tipoConsulta": "sentenca",
        },
        headers,
    )
    for pagina in range(1, max_pages + 1):
        docs = parse_pagina(html)
        if not docs:
            return
        yield pagina, docs
        if pagina == max_pages:
            return
        time.sleep(delay)
        html = _request(session, "trocarDePagina.do", {"pagina": pagina + 1}, headers)


def escrever_relatorio(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", default="sentencas.jsonl")
    parser.add_argument(
        "--dedupe-from",
        action="append",
        default=[],
        help="JSONL adicional cujos processos também devem ser ignorados",
    )
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--report", default="dataset_expansion_collection.json")
    parser.add_argument(
        "--contact",
        default="research@mediare.example",
        help="contato incluído no User-Agent",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="confirma a coleta real; sem esta opção apenas valida os parâmetros",
    )
    args = parser.parse_args()

    if not 1 <= args.batch_size <= MAX_BATCH:
        parser.error(f"--batch-size deve ficar entre 1 e {MAX_BATCH}")
    if args.delay < DEFAULT_DELAY:
        parser.error(f"--delay deve ser pelo menos {DEFAULT_DELAY:g} segundos")
    if args.max_pages < 1:
        parser.error("--max-pages deve ser positivo")

    output = Path(args.saida)
    report = Path(args.report)
    dedupe_paths = [output, *(Path(value) for value in args.dedupe_from)]
    vistos = carregar_processos(dedupe_paths)
    if not args.execute:
        print(
            f"Validação concluída: {len(vistos)} processos conhecidos; "
            f"lote máximo de {args.batch_size}. Use --execute para coletar."
        )
        return 0

    headers = {
        "User-Agent": (
            "MediareDatasetResearch/1.0 "
            f"(+public-interest legal research; contact={args.contact})"
        )
    }
    novos: list[dict] = []
    por_categoria: Counter[str] = Counter()
    erros: list[dict[str, str]] = []

    for categoria, consulta in CATEGORIAS.items():
        if len(novos) >= args.batch_size:
            break
        print(f"[{categoria}] procurando decisões ainda não coletadas")
        session = requests.Session()
        try:
            for pagina, docs in coletar_categoria(
                session, consulta, headers, args.delay, args.max_pages
            ):
                aceitos_pagina = 0
                for doc in docs:
                    processo = doc["processo"]
                    texto = doc.get("texto", "")
                    if processo in vistos or len(texto) < 400:
                        continue
                    if "segredo de justiça" in texto.casefold():
                        continue
                    vistos.add(processo)
                    doc["categoria"] = categoria
                    novos.append(doc)
                    por_categoria[categoria] += 1
                    aceitos_pagina += 1
                    if len(novos) >= args.batch_size:
                        break
                print(
                    f"  página {pagina}: {aceitos_pagina} novos; "
                    f"lote {len(novos)}/{args.batch_size}"
                )
                if len(novos) >= args.batch_size:
                    break
        except requests.RequestException as exc:
            erros.append({"categoria": categoria, "erro": type(exc).__name__})
            print(f"  erro de rede em {categoria}: {type(exc).__name__}", file=sys.stderr)
        finally:
            session.close()
        if len(novos) < args.batch_size:
            time.sleep(args.delay)

    if novos:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("a", encoding="utf-8") as stream:
            for doc in novos:
                stream.write(json.dumps(doc, ensure_ascii=False) + "\n")

    payload = {
        "status": "complete" if len(novos) == args.batch_size else "partial",
        "requested": args.batch_size,
        "collected": len(novos),
        "known_after": len(vistos),
        "by_category": dict(sorted(por_categoria.items())),
        "errors": erros,
        "output": str(output),
        "contains_raw_decision_text": True,
        "llm_calls": 0,
    }
    escrever_relatorio(report, payload)
    print(f"Lote encerrado: {len(novos)} novas decisões; relatório em {report}.")
    return 0 if len(novos) == args.batch_size else 2


if __name__ == "__main__":
    raise SystemExit(main())
