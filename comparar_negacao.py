#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compara DUAS execucoes do harness caso a caso, separando os gabaritos de
condenacao ZERO dos POSITIVOS. Sem API.

  python3 comparar_negacao.py res_haiku res_v9son

A pergunta: o painel sabe negar? E a mudanca de prompt mexeu nisso, ou mexeu
em tudo? Sem o grupo POSITIVO de controle nao da para saber se uma melhora na
negacao veio de discernimento ou de o painel simplesmente ficar mais avaro.
"""
import json, os, sys

GEMEOS = {"0014": "0001", "0030": "0002", "0062": "0004",
          "0079": "0005", "0103": "0006"}   # mesmo processo TJSP, id diferente

def ler(p):
    d = {}
    if not os.path.exists(p):
        sys.exit(f"nao achei {p}")
    for l in open(p, encoding="utf-8"):
        if l.strip():
            o = json.loads(l)
            d[o["id"]] = o
    return d

def faixas(out):
    pain = ler(os.path.join(out, "paineis.jsonl"))
    r = {}
    for cid, p in pain.items():
        c = p.get("consolidado") or {}
        f = c.get("faixa_total")
        if f:
            r[cid] = (f, bool(c.get("unanime")))
    return r

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    a_dir, b_dir = sys.argv[1], sys.argv[2]
    A, B = faixas(a_dir), faixas(b_dir)
    norm = ler(os.path.join(b_dir, "gabaritos_norm.jsonl"))

    comuns = [c for c in sorted(set(A) & set(B)) if c not in GEMEOS]
    if not comuns:
        sys.exit("nenhum caso em comum")

    grupos = {"ZERO": [], "POSITIVO": []}
    for cid in comuns:
        o = norm.get(cid)
        if not o or o.get("total") is None:
            continue
        g = float(o["total"])
        grupos["ZERO" if g == 0 else "POSITIVO"].append((cid, g))

    print(f"\n{'='*76}\nPAREADO  {a_dir}  ->  {b_dir}   ({len(comuns)} casos em comum)\n{'='*76}")
    for nome, itens in grupos.items():
        if not itens:
            continue
        n = len(itens)
        ca = cb = pa = pb = 0
        larg_a = larg_b = 0.0
        mudou = []
        for cid, g in itens:
            fa, _ = A[cid]; fb, _ = B[cid]
            ca += fa[0] <= g <= fa[1]; cb += fb[0] <= g <= fb[1]
            pa += fa[1] > 0.01;        pb += fb[1] > 0.01
            larg_a += fa[1] - fa[0];   larg_b += fb[1] - fb[0]
            if (fa[1] > 0.01) != (fb[1] > 0.01):
                mudou.append((cid, fa, fb))
        print(f"\n  {nome}  (n={n})")
        print(f"    contem o gabarito : {ca:3d} ({100*ca/n:3.0f}%)  ->"
              f" {cb:3d} ({100*cb/n:3.0f}%)")
        print(f"    propos valor > 0  : {pa:3d} ({100*pa/n:3.0f}%)  ->"
              f" {pb:3d} ({100*pb/n:3.0f}%)")
        print(f"    largura media     : {larg_a/n:12,.2f}  -> {larg_b/n:12,.2f}")
        for cid, fa, fb in mudou:
            seta = "concedeu -> NEGOU" if fb[1] <= 0.01 else "NEGOU -> concedeu"
            print(f"      {cid}  [{fa[0]:,.0f} .. {fa[1]:,.0f}]  =>  "
                  f"[{fb[0]:,.0f} .. {fb[1]:,.0f}]   {seta}")

    z, p = grupos["ZERO"], grupos["POSITIVO"]
    if z and p:
        def taxa(itens, R):
            return sum(1 for cid, _ in itens if R[cid][0][1] > 0.01) / len(itens)
        dz = taxa(z, A) - taxa(z, B)
        dp = taxa(p, A) - taxa(p, B)
        print(f"\n{'-'*76}")
        print(f"  queda na taxa de conceder:  ZERO {dz*100:+.0f} pts   "
              f"POSITIVO {dp*100:+.0f} pts")
        print("  Se as duas cairem junto, o painel so ficou mais avaro.")
        print("  Se so a ZERO cair, ele ganhou discernimento - que e o objetivo.")
    print("=" * 76)

if __name__ == "__main__":
    main()
