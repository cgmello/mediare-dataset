#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confere resultados/normalizacao.csv: casos-teste + sanidade agregada."""
import csv, json, os, collections

ESPERADO = {   # casos onde eu sei a resposta certa; None = so exibir
    "0002": 600.0,      # total_principal, NAO somar as parcelas
    "0004": 18472.0,    # ignorar limite_seguradora
    "0006": 0.0,        # deferido=0; o 8000 era so o pedido
    "0018": 13625.0,    # a quota, nao o custo total
    "0008": None,       # tem bruto, liquido e caucao a deduzir
    "0011": None,       # tem deducao_caucao + valor_total_condenacao
}

rows = {r["id"]: r for r in csv.DictReader(open("resultados/normalizacao.csv", encoding="utf-8"))}
print(f"{len(rows)} linhas\n" + "=" * 78)

for cid in sorted(ESPERADO):
    r = rows.get(cid)
    if not r:
        print(f"{cid}: AUSENTE"); continue
    tot = float(r["total_apurado"]) if r["total_apurado"] not in ("", "None") else None
    exp = ESPERADO[cid]
    veredito = "  " if exp is None else ("OK  " if tot is not None and abs(tot-exp) < 0.01 else "ERRO")
    print(f"\n[{veredito}] {cid}  ({r['classe']})")
    print(f"   apurado : {tot}" + (f"   esperado: {exp}" if exp is not None else ""))
    print(f"   somou   : {r['chaves_somadas']}")
    print(f"   tinha   : {r['chaves_originais']}")
    print(f"   obs     : {r['obs'][:110]}")

print("\n" + "=" * 78 + "\nSANIDADE")
tots, nulos = [], 0
for r in rows.values():
    v = r["total_apurado"]
    if v in ("", "None"):
        nulos += 1
    else:
        tots.append(float(v))
tots.sort()
zeros = sum(1 for t in tots if t == 0)
print(f"  nulos (falha)        : {nulos}")
print(f"  total = 0            : {zeros}   (improcedentes; plausivel se ~5-15%)")
print(f"  mediana              : R$ {tots[len(tots)//2]:,.2f}")
print(f"  min / max            : R$ {tots[0]:,.2f}  /  R$ {tots[-1]:,.2f}")
gigantes = [(r['id'], float(r['total_apurado'])) for r in rows.values()
            if r['total_apurado'] not in ("", "None") and float(r['total_apurado']) > 1_000_000]
print(f"  acima de R$ 1 milhao : {len(gigantes)} {gigantes[:5]}")
susp = [r['id'] for r in rows.values()
        if r['total_apurado'] not in ("", "None") and float(r['total_apurado']) > 0
        and not r['chaves_somadas'].strip()]
print(f"  total>0 sem chaves   : {len(susp)} {susp[:8]}")
print("=" * 78)
