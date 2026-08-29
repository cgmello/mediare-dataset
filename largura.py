#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cruza as faixas obtidas on-chain (res_*/chain.jsonl) com os gabaritos e mede
a LARGURA das faixas aceitas. A pergunta: o consenso veio de precisao ou de
vagueza? Uma faixa [0, tudo] passa em qualquer validacao e nao serve de pauta.

  python3 largura.py res_v8 [res_v7 ...]

Sem API. Usa gold.avaliar como regua (so casos confiaveis pontuam).
"""
import json, os, sys
import harness, gold

# largura relativa = (max-min)/max. Acima disso a faixa nao orienta negociacao.
LIMITE_UTIL = 0.30

def carregar(out):
    p = os.path.join(out, "chain.jsonl")
    if not os.path.exists(p):
        sys.exit(f"nao achei {p}")
    linhas = {}
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        d = json.loads(l)
        linhas[d["id"]] = d          # ultima execucao do caso vence
    return linhas

def rel(faixa):
    lo, hi = faixa
    if hi == 0:
        return 0.0 if lo == 0 else None
    return (hi - lo) / hi

def main():
    outs = sys.argv[1:] or ["res_v8"]
    gabs = harness.carregar_gabaritos(".")

    for out in outs:
        linhas = carregar(out)
        print(f"\n{'='*78}\n{out}   ({len(linhas)} casos)\n{'='*78}")
        print(f"{'caso':5} {'status':13} {'rot':>3} {'faixa':>26} {'larg':>6} "
              f"{'gabarito':>12} {'contem':>7}")
        print("-" * 78)

        aceitos = larguras = contidos = pontuais = uteis = confiaveis = 0
        for cid in sorted(linhas):
            d = linhas[cid]
            st = d.get("status", "?")
            f  = d.get("faixa_total")
            rot = d.get("rotacoes")
            g = gabs.get(cid)
            alvo, _, ok, motivo = gold.avaliar(g) if g else (None, [], False, "sem gabarito")

            fs = f"[{f[0]:,.2f} .. {f[1]:,.2f}]" if f else "-"
            r  = rel(f) if f else None
            rs = f"{r*100:.0f}%" if r is not None else "-"
            gs = f"{alvo:,.2f}" if ok and alvo is not None else f"({motivo[:10]})"
            cont = "-"
            if f and ok and alvo is not None:
                cont = "sim" if f[0] <= alvo <= f[1] else "NAO"

            print(f"{cid:5} {st:13} {rot!s:>3} {fs:>26} {rs:>6} {gs:>12} {cont:>7}")

            if d.get("exec") == "ERROR":
                print(f"      ^ contrato estourou excecao: nao conta "
                      f"({d.get('erro_traceback','')[:60]})")
                continue
            if st != "ACCEPTED" and st != "FINALIZED":
                continue
            aceitos += 1
            if f is None:
                continue
            larguras += 1
            if f[0] == f[1]:
                pontuais += 1
            if r is not None and r <= LIMITE_UTIL:
                uteis += 1
            if ok and alvo is not None:
                confiaveis += 1
                if f[0] <= alvo <= f[1]:
                    contidos += 1

        print("-" * 78)
        print(f"aceitos/finalizados      : {aceitos}")
        print(f"  com faixa legivel      : {larguras}")
        print(f"  faixa pontual (min=max): {pontuais}"
              + (f"  ({pontuais/larguras*100:.0f}%)" if larguras else ""))
        print(f"  largura util (<= {LIMITE_UTIL*100:.0f}%)  : {uteis}"
              + (f"  ({uteis/larguras*100:.0f}%)" if larguras else ""))
        print(f"  gabarito confiavel     : {confiaveis}")
        print(f"  contem o gabarito      : {contidos}"
              + (f"  ({contidos/confiaveis*100:.0f}%)" if confiaveis else ""))

if __name__ == "__main__":
    main()
