#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seleciona o subconjunto de gabaritos CONFIAVEIS e escreve gabaritos_norm.jsonl
so com eles. Casos ambiguos ficam com total=None e saem da pontuacao. Sem API."""
import json, re, sys, os, collections
import harness

DEST = sys.argv[1] if len(sys.argv) > 1 else "res_haiku/gabaritos_norm.jsonl"

RE_TOTAL   = re.compile(r"total|valor_bruto|valor_liquido|valor_final|condenacao|debito_total")
RE_IGNORAR = re.compile(r"pedid|limite|teto|saldo|nao_cobrad|rejeitad|negad|arbitramento|liquidar")
RE_DEDUZIR = re.compile(r"deducao|deduzir|abatimento|desconto|compensacao")
RE_MORAL   = re.compile(r"moral")
RE_ACESSORIO = re.compile(r"juros|correcao|corrigid|honorario|sucumben|custas|atualiza")

def avaliar(g):
    """-> (total, chaves_usadas, confiavel, motivo)"""
    v = {k: float(x) for k, x in g["valores"].items() if isinstance(x, (int, float))}
    res = (g["resultado"] or "").lower().replace("_", " ")
    if not v:
        return None, [], False, "sem valores numericos"
    if any(x < 0 for x in v.values()):
        return None, [], False, "tem valor negativo"
    if any(RE_IGNORAR.search(k) for k in v):
        return None, [], False, "tem chave ambigua (pedido/limite/arbitramento)"

    totais = [k for k in v if RE_TOTAL.search(k)]
    parcelas = [k for k in v if k not in totais]

    if not totais:
        if len(v) > 4:
            return None, [], False, f"{len(v)} rubricas soltas, sem total"
        soma = sum(-abs(v[k]) if RE_DEDUZIR.search(k) else v[k] for k in v)
        total, usadas = round(soma, 2), sorted(v)
    elif len(totais) == 1:
        t = v[totais[0]]
        soma_p = sum(-abs(v[k]) if RE_DEDUZIR.search(k) else v[k] for k in parcelas)
        # so confia se o total BATE com as parcelas: prova que entendemos a semantica
        if parcelas and abs(t - soma_p) > max(1.0, 0.01 * max(abs(t), 1)):
            return None, [], False, f"total {t:,.0f} nao fecha com parcelas {soma_p:,.0f}"
        total, usadas = round(t, 2), [totais[0]]
    else:
        return None, [], False, f"{len(totais)} chaves de total"

    # coerencia entre resultado e valores
    if total == 0 and res and "improcedente" not in res and "extin" not in res:
        return None, [], False, f"'{res}' mas total zero"
    if total > 0 and res == "improcedente":
        return None, [], False, "improcedente mas total > 0"

    # o painel calcula principal/multa/outros; nao calcula juros, correcao nem
    # honorarios. Se o total do gabarito os inclui, desconta para comparar igual.
    # Seguro: ja verificamos acima que o total fecha com as parcelas.
    acess = sum(v[k] for k in v if RE_ACESSORIO.search(k) and v[k] > 0)
    if acess:
        total = round(total - acess, 2)
        if total < 0:
            return None, [], False, "acessorios maiores que o total"
    return total, usadas, True, "ok"

gabs = harness.carregar_gabaritos(".")
motivos = collections.Counter()
conf_ids = []
os.makedirs(os.path.dirname(DEST) or ".", exist_ok=True)
with open(DEST, "w", encoding="utf-8") as out:
    for cid, g in sorted(gabs.items()):
        total, usadas, ok, motivo = avaliar(g)
        motivos[motivo if not ok else "CONFIAVEL"] += 1
        if ok:
            conf_ids.append(cid)
        out.write(json.dumps({"id": cid, "total": total if ok else None,
                              "chaves_somadas": usadas, "classe": g["classe"],
                              "confiavel": ok, "obs": motivo}, ensure_ascii=False) + "\n")

print(f"{len(gabs)} gabaritos -> {DEST}\n")
for m, n in motivos.most_common(12):
    print(f"  {n:4d}  {m}")
p95 = [c for c in conf_ids if c in sorted(gabs)[:95]]
print(f"\nCONFIAVEIS no total : {len(conf_ids)}/500")
print(f"CONFIAVEIS nos 95   : {len(p95)}/95   -> {p95}")

print("\nCONFERENCIA (resposta conhecida):")
for cid, esp in (("0002",600.0), ("0004",18472.0), ("0006",0.0), ("0011",51806.28), ("0008",30888.0)):
    t, u, ok, m = avaliar(gabs[cid])
    if not ok:
        print(f"  [fora] {cid}  excluido: {m}   (esperado {esp})")
    else:
        v = "OK  " if abs(t-esp) < 1 else "ERRO"
        print(f"  [{v}] {cid}  apurado={t}  esperado={esp}  usou={u}")