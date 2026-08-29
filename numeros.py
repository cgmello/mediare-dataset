#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Todos os numeros do relatorio, de uma vez, com intervalo de confianca.
Sem API.

  python3 numeros.py res_v9son

Cada taxa vem com IC95 por Wilson, porque proporcao com n pequeno e cauda
assimetrica: 9/18 nao e "50% +/- alguma coisa simetrica".
"""
import json, math, os, sys

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    m = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (p, max(0.0, c-m), min(1.0, c+m))

def pct(k, n):
    p, lo, hi = wilson(k, n)
    return f"{100*p:5.1f}%  [{100*lo:4.1f} .. {100*hi:4.1f}]  ({k}/{n})"

def ler(p):
    d = {}
    if not os.path.exists(p):
        sys.exit(f"nao achei {p}")
    for l in open(p, encoding="utf-8"):
        if l.strip():
            o = json.loads(l); d[o["id"]] = o
    return d

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "res_v9son"
    pain = ler(os.path.join(out, "paineis.jsonl"))
    norm = ler(os.path.join(out, "gabaritos_norm.jsonl"))
    TOL = 0.15

    linhas = []
    for cid, p in sorted(pain.items()):
        o = norm.get(cid)
        if not o or o.get("total") is None:
            continue
        c = p.get("consolidado") or {}
        f = c.get("faixa_total")
        if not f:
            continue
        linhas.append({
            "id": cid, "g": float(o["total"]), "f": f,
            "unanime": bool(c.get("unanime")),
            "teses": p.get("teses", []),
            "in": p.get("tokens_in", 0), "out": p.get("tokens_out", 0),
        })
    n = len(linhas)
    if not n:
        sys.exit("nada avaliavel")
    zero = [l for l in linhas if l["g"] == 0]
    pos = [l for l in linhas if l["g"] > 0]

    def contem(ls):
        return sum(1 for l in ls if l["f"][0] - 0.01 <= l["g"] <= l["f"][1] + 0.01)
    def util(ls):   # faixa estreita o bastante para orientar negociacao
        k = 0
        for l in ls:
            lo, hi = l["f"]
            if hi <= 0.01:
                k += l["g"] == 0
            elif (hi - lo) / hi <= 0.30:
                k += 1
        return k

    print(f"\n{'='*72}\nAMOSTRA: {n} casos avaliaveis  ({len(zero)} zero / {len(pos)} positivos)")
    print(f"tokens: {sum(l['in'] for l in linhas):,} in / {sum(l['out'] for l in linhas):,} out")
    print("=" * 72)
    print("\nO MEDIADOR VERIA A RESPOSTA CERTA?")
    print(f"  faixa contem o gabarito   : {pct(contem(linhas), n)}")
    print(f"    so os positivos         : {pct(contem(pos), len(pos))}")
    print(f"    so os zero              : {pct(contem(zero), len(zero))}")
    print("\nA FAIXA SERVE DE PAUTA? (largura relativa <= 30%)")
    print(f"  faixa util                : {pct(util(linhas), n)}")

    print("\nO COMITE SABE NEGAR?")
    conc = sum(1 for l in zero if l["f"][1] > 0.01)
    print(f"  propos valor > 0 em caso de condenacao ZERO:")
    print(f"                              {pct(conc, len(zero))}")
    graves = [l for l in zero if l["f"][0] > 0.01 and l["unanime"]]
    print(f"  UNANIME e sem sobrepor zero (viraria Termo automatico errado):")
    print(f"                              {pct(len(graves), len(zero))}")
    for l in sorted(graves, key=lambda x: -x["f"][1])[:8]:
        print(f"      {l['id']}  [{l['f'][0]:,.2f} .. {l['f'][1]:,.2f}]")

    print("\nUNANIMIDADE E SINAL DE ACERTO?")
    u = [l for l in linhas if l["unanime"]]
    d = [l for l in linhas if not l["unanime"]]
    print(f"  unanimes                  : {pct(len(u), n)}")
    if u:
        print(f"    desses, faixa contem    : {pct(contem(u), len(u))}")
    if d:
        print(f"    divergentes, contem     : {pct(contem(d), len(d))}")
    print("  (se os dois intervalos se sobrepoem, unanimidade nao informa nada)")

    print("\nACERTO POR LENTE (centro da propria tese, +/-15%)")
    lentes = sorted({t["lente"] for l in linhas for t in l["teses"]})
    for lente in lentes:
        ok = tot = 0
        for l in linhas:
            for t in l["teses"]:
                if t["lente"] != lente:
                    continue
                v = round(sum(float(t["valores"].get(k, 0) or 0)
                              for k in ("principal", "multa", "outros")), 2)
                tot += 1
                ok += abs(v - l["g"]) <= max(TOL * max(l["g"], 1), 0.01)
        print(f"  {lente:16} {pct(ok, tot)}")
    print("=" * 72)

if __name__ == "__main__":
    main()
