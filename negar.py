#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O comite sabe NEGAR? Separa o acerto entre casos cuja condenacao
patrimonial e ZERO e os demais. Sem API.

Hipotese levantada on-chain (0006: pedido 8000/deferido 0, o comite deu 8000;
0021: parcelas todas 0, o comite deu 3526): o painel concede quando deveria
negar. Com o vocabulario fechado ha 49 casos de total zero para testar.

  python3 negar.py [res_haiku]
"""
import json, os, sys

def ler(p):
    d = {}
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            if l.strip():
                o = json.loads(l); d[o["id"]] = o
    return d

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "res_haiku"
    pain = ler(os.path.join(out, "paineis.jsonl"))
    norm = ler(os.path.join(out, "gabaritos_norm.jsonl"))
    TOL = 0.15

    grupos = {"ZERO": {"n": 0, "contem": 0, "acerto": 0, "dado": []},
              "POSITIVO": {"n": 0, "contem": 0, "acerto": 0, "dado": []}}
    for cid, p in sorted(pain.items()):
        o = norm.get(cid)
        if not o or o.get("total") is None:
            continue
        c = (p.get("consolidado") or {})
        f = c.get("faixa_total")
        if not f:
            continue
        g = float(o["total"])
        k = "ZERO" if g == 0 else "POSITIVO"
        grupos[k]["n"] += 1
        if f[0] <= g <= f[1]:
            grupos[k]["contem"] += 1
        lo, hi = f
        meio = (lo + hi) / 2
        if abs(meio - g) <= max(TOL * max(g, 1), 0.01):
            grupos[k]["acerto"] += 1
        grupos[k]["dado"].append((cid, g, f))

    print(f"\n{'='*70}\nO COMITE SABE NEGAR?\n{'='*70}")
    for k, v in grupos.items():
        if not v["n"]:
            continue
        print(f"\n  gabarito {k}  (n={v['n']})")
        print(f"    faixa contem o gabarito : {v['contem']:3d}  "
              f"({100*v['contem']/v['n']:.0f}%)")
        print(f"    centro dentro de +/-15% : {v['acerto']:3d}  "
              f"({100*v['acerto']/v['n']:.0f}%)")

    z = grupos["ZERO"]
    if z["n"]:
        print(f"\n  nos {z['n']} casos de condenacao ZERO, o que o comite propos:")
        conc = [(c, g, f) for c, g, f in z["dado"] if f[1] > 0.01]
        print(f"    propos algum valor > 0 : {len(conc)}/{z['n']}  "
              f"({100*len(conc)/z['n']:.0f}%)")
        for cid, g, f in sorted(conc, key=lambda x: -x[2][1])[:12]:
            print(f"      {cid}  gabarito 0.00  comite [{f[0]:,.2f} .. {f[1]:,.2f}]")
    print("=" * 70)

if __name__ == "__main__":
    main()
