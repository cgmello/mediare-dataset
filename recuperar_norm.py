#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstroi gabaritos_norm.jsonl a partir do normalizacao.csv. Nao usa API."""
import csv, json, sys, os

CSV  = sys.argv[1] if len(sys.argv) > 1 else "resultados/normalizacao.csv"
DEST = sys.argv[2] if len(sys.argv) > 2 else "res_haiku/gabaritos_norm.jsonl"

if not os.path.exists(CSV):
    sys.exit(f"nao achei {CSV}\n"
             "procure com:  find . -name 'normalizacao.csv' -o -name 'gabaritos_norm.jsonl'")

os.makedirs(os.path.dirname(DEST) or ".", exist_ok=True)
n = nulos = 0
with open(DEST, "w", encoding="utf-8") as out:
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        v = (r.get("total_apurado") or "").strip()
        if v in ("", "None"):
            total = None; nulos += 1
        else:
            total = round(float(v), 2)
        out.write(json.dumps({
            "id": r["id"],
            "total": total,
            "chaves_somadas": [k for k in (r.get("chaves_somadas") or "").split("|") if k],
            "classe": r.get("classe", ""),
            "obs": r.get("obs", ""),
        }, ensure_ascii=False) + "\n")
        n += 1
print(f"{n} linhas -> {DEST}   (sem total: {nulos})")