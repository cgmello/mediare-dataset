#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Matriz de confusao de 'responsavel'. Nao usa API."""
import json, sys, collections, os
import harness

OUT = sys.argv[1] if len(sys.argv) > 1 else "res_haiku"
gabs = harness.carregar_gabaritos(".")
paineis = harness.ler_jsonl(os.path.join(OUT, "paineis.jsonl"))

CLASSES = ["requerido", "requerente", "parcial_ambos", "ambos_culpa_concorrente", "divergente"]
mat = collections.defaultdict(collections.Counter)      # gabarito -> painel
por_lente = {l: collections.defaultdict(collections.Counter) for l in
             ("ampla", "estrita", "jurisprudencial")}
erros_req = []

for cid, p in sorted(paineis.items()):
    g = gabs.get(cid)
    if not g or not g["responsavel"]:
        continue
    real = g["responsavel"]
    prev = p["consolidado"]["responsavel_majoritario"]
    mat[real][prev] += 1
    if real == "requerido" and prev != "requerido":
        erros_req.append((cid, prev, [t["responsavel"] for t in p["teses"]]))
    for t in p["teses"]:
        if t["lente"] in por_lente:
            por_lente[t["lente"]][real][t["responsavel"]] += 1

n = sum(sum(v.values()) for v in mat.values())
print(f"MATRIZ DE CONFUSAO - responsavel  (n={n})")
print("linha = gabarito | coluna = painel (moda)\n")
larg = 26
print(" " * larg + "".join(f"{c[:11]:>13s}" for c in CLASSES) + f"{'total':>8s}")
for real in CLASSES[:-1]:
    if not mat[real]:
        continue
    tot = sum(mat[real].values())
    linha = f"{real:{larg}s}"
    for prev in CLASSES:
        v = mat[real][prev]
        linha += f"{(str(v) if v else '.'):>13s}"
    print(linha + f"{tot:>8d}")

print("\n" + "-" * 70)
print("ACERTO POR CLASSE (recall)")
for real in CLASSES[:-1]:
    tot = sum(mat[real].values())
    if tot:
        print(f"  {real:26s} {100*mat[real][real]/tot:5.1f}%  ({mat[real][real]}/{tot})")

print("\n" + "-" * 70)
print("SOBRE-PREVISAO (o painel disse X quantas vezes vs quantas X existe)")
for c in CLASSES[:-1]:
    prev_n = sum(mat[r][c] for r in CLASSES[:-1])
    real_n = sum(mat[c].values())
    if real_n or prev_n:
        sinal = "+" if prev_n > real_n else " "
        print(f"  {c:26s} previsto {prev_n:3d} | real {real_n:3d}  {sinal}{prev_n-real_n:+d}")
div = sum(mat[r]["divergente"] for r in CLASSES[:-1])
print(f"  {'divergente (lentes empataram)':26s} {div:3d}")

print("\n" + "-" * 70)
print(f"CASOS 'requerido' QUE O PAINEL ERROU ({len(erros_req)}):")
for cid, prev, teses in erros_req[:20]:
    print(f"  {cid}: painel={prev:24s} lentes={teses}")
if len(erros_req) > 20:
    print(f"  ... e mais {len(erros_req)-20}")

print("\n" + "-" * 70)
print("ACERTO POR LENTE E POR CLASSE")
print(f"{'lente':16s}" + "".join(f"{c[:11]:>14s}" for c in CLASSES[:-1]))
for l, m in por_lente.items():
    linha = f"{l:16s}"
    for real in CLASSES[:-1]:
        tot = sum(m[real].values())
        linha += f"{(f'{100*m[real][real]/tot:.0f}% ({tot})' if tot else '-'):>14s}"
    print(linha)