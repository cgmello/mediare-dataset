#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converte res_gab/gabaritos_v2.jsonl (vocabulario fechado) para o formato
gabaritos_norm.jsonl que o harness --relatorio le. Sem API.

  python3 usar_v2.py res_haiku          # escreve res_haiku/gabaritos_norm.jsonl

O total escrito e o total_patrimonial: principal + multa + outros. Danos
morais ficam de fora porque o IC os exclui de RUBRICAS - as duas pontas
precisam medir a mesma grandeza. Casos ilíquidos, incoerentes ou de
confianca baixa saem com total=None e nao pontuam.
"""
import json, os, sys

FONTE = "res_gab/gabaritos_v2.jsonl"

def main():
    saida_dir = sys.argv[1] if len(sys.argv) > 1 else "res_haiku"
    if not os.path.exists(FONTE):
        sys.exit(f"nao achei {FONTE} - rode regabaritar.py primeiro")
    ult = {}
    for l in open(FONTE, encoding="utf-8"):
        d = json.loads(l)
        ult[d["id"]] = d                      # ultima linha de cada id vence
    dest = os.path.join(saida_dir, "gabaritos_norm.jsonl")
    os.makedirs(saida_dir, exist_ok=True)
    usaveis = 0
    with open(dest, "w", encoding="utf-8") as f:
        for cid, n in sorted(ult.items()):
            ok = (n["coerente"] and n["confianca"] != "baixa"
                  and not n["iliquido"])
            if ok:
                usaveis += 1
            f.write(json.dumps({
                "id": cid,
                "total": n["total_patrimonial"] if ok else None,
                "chaves_somadas": [],          # ja e vocabulario fechado
                "classe": "fechado",
                "confiavel": ok,
                "obs": n["obs"][:120],
            }, ensure_ascii=False) + "\n")
    print(f"{len(ult)} gabaritos -> {dest}")
    print(f"utilizaveis (coerente, confianca>=media, liquido): {usaveis}")
    zeros = sum(1 for n in ult.values()
                if n["coerente"] and not n["iliquido"]
                and n["confianca"] != "baixa" and n["total_patrimonial"] == 0)
    print(f"  destes, com total ZERO: {zeros}  <- o comite precisa saber negar")

if __name__ == "__main__":
    main()
