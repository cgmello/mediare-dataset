#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compara total do painel x total do gabarito, caso a caso. Sem API."""
import json, sys, os
import harness

OUT = sys.argv[1] if len(sys.argv) > 1 else "res_haiku"
N   = int(sys.argv[2]) if len(sys.argv) > 2 else 20

gabs    = harness.carregar_gabaritos(".")
paineis = harness.ler_jsonl(os.path.join(OUT, "paineis.jsonl"))
norm    = harness.ler_jsonl(os.path.join(OUT, "gabaritos_norm.jsonl"))

linhas = []
for cid, p in paineis.items():
    g, o = gabs.get(cid), norm.get(cid)
    if not g or not o or o.get("total") is None:
        continue
    gt = float(o["total"])
    for k in o.get("chaves_somadas", []):
        if "moral" in k.lower():
            gt -= float(g["valores"].get(k, 0.0) or 0.0)
    lo, hi = p["consolidado"]["faixa_total"]
    dentro = lo - 0.01 <= gt <= hi + 0.01
    ref = max(abs(gt), abs(hi), 1.0)
    linhas.append((abs((lo + hi) / 2 - gt) / ref, cid, lo, hi, round(gt, 2), dentro,
                   g["classe"], len(g["valores"]),
                   "|".join(o.get("chaves_somadas", []))[:60]))

linhas.sort(reverse=True)
print(f"{len(linhas)} casos comparaveis | {sum(1 for l in linhas if l[5])} dentro da faixa\n")
print(f"{'id':6s}{'faixa do painel':>26s}{'gabarito':>14s}  {'ok':3s} {'classe':20s} chaves somadas")
print("-" * 118)
for _, cid, lo, hi, gt, dentro, classe, nk, chaves in linhas[:N]:
    faixa = f"[{lo:,.0f} - {hi:,.0f}]"
    print(f"{cid:6s}{faixa:>26s}{gt:>14,.0f}  {'sim' if dentro else 'NAO':3s} "
          f"{classe:20s} ({nk}) {chaves}")

print("\n--- os que MAIS batem ---")
for _, cid, lo, hi, gt, dentro, classe, nk, chaves in linhas[-8:]:
    print(f"{cid:6s}[{lo:,.0f} - {hi:,.0f}]  gab={gt:,.0f}  {'sim' if dentro else 'NAO'}  {classe}")