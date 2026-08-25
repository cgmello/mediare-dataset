#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normaliza os gabaritos SEM API, por regras deterministicas.
Substituto de emergencia do --normalizar. Escreve gabaritos_norm.jsonl."""
import json, sys, os
import harness

DEST = sys.argv[1] if len(sys.argv) > 1 else "res_haiku/gabaritos_norm.jsonl"

IGNORAR  = ("pedid", "limite", "teto", "saldo", "nao_cobrad", "rejeitad", "negad")
SUBTRAIR = ("deducao", "deduzir", "abatimento", "desconto", "compensacao", "a_deduzir")

def total_de(valores):
    itens = {k: v for k, v in valores.items() if isinstance(v, (int, float))}
    if not itens:
        return None, [], "sem valores numericos"
    # 1) se existe chave de total, ela manda
    totais = [k for k in itens if k.startswith("total")]
    if totais:
        k = max(totais, key=lambda x: abs(float(itens[x])))
        return round(float(itens[k]), 2), [k], "usou chave de total"
    soma, usadas, obs = 0.0, [], []
    for k, v in sorted(itens.items()):
        kl = k.lower()
        if any(t in kl for t in IGNORAR):
            obs.append(f"-{k}"); continue
        if "moral" in kl:
            obs.append(f"moral:{k}")          # marcado; o relatorio desconta
        if any(t in kl for t in SUBTRAIR):
            soma -= abs(float(v)); usadas.append(k); continue
        soma += float(v); usadas.append(k)
    return round(soma, 2), usadas, "; ".join(obs)[:120]

gabs = harness.carregar_gabaritos(".")
os.makedirs(os.path.dirname(DEST) or ".", exist_ok=True)
with open(DEST, "w", encoding="utf-8") as out:
    for cid, g in sorted(gabs.items()):
        t, usadas, obs = total_de(g["valores"])
        out.write(json.dumps({"id": cid, "total": t, "chaves_somadas": usadas,
                              "classe": g["classe"], "obs": obs}, ensure_ascii=False) + "\n")
print(f"{len(gabs)} gabaritos -> {DEST}")

CONHECIDOS = {"0002": 600.0, "0004": 18472.0, "0006": 0.0, "0018": 0.0}
print("\nCONFERENCIA nos casos de resposta conhecida:")
for cid, esperado in CONHECIDOS.items():
    t, usadas, obs = total_de(gabs[cid]["valores"])
    ok = "OK  " if t is not None and abs(t - esperado) < 0.01 else "ERRO"
    print(f"  [{ok}] {cid}  apurado={t}  esperado={esperado}  somou={usadas}")