#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Separa 'chave invalida' de 'chave valida sem saldo/limite'. Nao imprime a
chave: so o sufixo, que e o que a lista do console tambem mostra.

  python3 diag_api.py
"""
import json, os, sys, urllib.request, urllib.error

K = os.environ.get("ANTHROPIC_API_KEY", "")
if not K:
    sys.exit("ANTHROPIC_API_KEY nao esta no ambiente")
print(f"chave: ...{K[-8:]}   comprimento={len(K)}   prefixo={K[:14]}...")
if not K.startswith("sk-ant-"):
    print("  !! nao parece uma chave de API da Anthropic")

INTERESSANTES = ("request-id", "anthropic-organization-id", "x-should-retry",
                 "anthropic-ratelimit-requests-limit",
                 "anthropic-ratelimit-input-tokens-limit",
                 "anthropic-ratelimit-output-tokens-limit")

def bater(metodo, url, corpo=None):
    req = urllib.request.Request(url, method=metodo,
        data=json.dumps(corpo).encode() if corpo else None,
        headers={"x-api-key": K, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read()[:400].decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()[:400].decode("utf-8","replace")
    except Exception as e:
        return 0, {}, f"{type(e).__name__}: {e}"

print("\n--- 1) GET /v1/models  (nao consome credito: testa se a CHAVE vale)")
st, h, b = bater("GET", "https://api.anthropic.com/v1/models?limit=1")
print(f"    HTTP {st}")
for k in INTERESSANTES:
    if k in {x.lower() for x in h}:
        v = next(vv for kk, vv in h.items() if kk.lower() == k)
        print(f"    {k}: {v}")
print(f"    corpo: {b[:220]}")

print("\n--- 2) POST /v1/messages  (1 token: testa SALDO/LIMITE)")
st, h, b = bater("POST", "https://api.anthropic.com/v1/messages",
                 {"model": "claude-haiku-4-5", "max_tokens": 1,
                  "messages": [{"role": "user", "content": "oi"}]})
print(f"    HTTP {st}")
for k in INTERESSANTES:
    if k in {x.lower() for x in h}:
        v = next(vv for kk, vv in h.items() if kk.lower() == k)
        print(f"    {k}: {v}")
print(f"    corpo: {b[:300]}")

print("""
--- leitura
  1 OK  e  2 OK   -> saldo existe; o erro anterior foi outra coisa
  1 OK  e  2 400  -> chave VALIDA, conta/workspace sem saldo ou no limite
                     (limite de gasto do workspace da exatamente isso)
  1 401           -> chave invalida ou revogada
  1 403           -> chave sem permissao nesse workspace
""")
