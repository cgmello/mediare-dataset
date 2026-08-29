#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estado de uma transacao no Studio, sem SDK. So urllib.

  python3 estado.py 0xHASH [0xHASH ...]
  python3 estado.py --caso 0006 --out res_v8      (pega o hash do receipt)

O JSON-RPC cru devolve 'statusName' (camelCase) ou 'status' numerico; o SDK
devolve 'status_name'. Aceita os tres.
"""
import json, sys, os, urllib.request

RPC = os.environ.get("GL_RPC", "https://studio.genlayer.com/api")

NUM2NOME = {"0": "UNINITIALIZED", "1": "PENDING", "2": "PROPOSING",
            "3": "COMMITTING", "4": "REVEALING", "5": "ACCEPTED",
            "6": "UNDETERMINED", "7": "FINALIZED", "8": "CANCELED",
            "9": "APPEAL_REVEALING", "10": "APPEAL_COMMITTING",
            "11": "READY_TO_FINALIZE", "12": "VALIDATORS_TIMEOUT",
            "13": "LEADER_TIMEOUT"}
VIVOS = {"PENDING", "PROPOSING", "COMMITTING", "REVEALING",
         "APPEAL_REVEALING", "APPEAL_COMMITTING", "READY_TO_FINALIZE"}

def status_de(tx):
    for k in ("statusName", "status_name", "status"):
        v = tx.get(k)
        if v is not None:
            return NUM2NOME.get(str(v), str(v).upper())
    return "?"

def rpc(metodo, params):
    req = urllib.request.Request(
        RPC, data=json.dumps({"jsonrpc": "2.0", "method": metodo,
                              "params": params, "id": 1}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if "error" in d:
        sys.exit(f"RPC erro: {d['error']}")
    return d.get("result")

def rodadas(tx):
    h = tx.get("consensus_history") or tx.get("consensusHistory") or {}
    return len(h.get("consensus_results") or h.get("consensusResults") or [])

def main():
    a = sys.argv[1:]
    hashes = []
    if "--caso" in a:
        i = a.index("--caso")
        cid = a[i + 1].zfill(4)
        out = a[a.index("--out") + 1] if "--out" in a else "res_v8"
        p = os.path.join(out, "receipts", f"{cid}.json")
        if not os.path.exists(p):
            sys.exit(f"nao achei {p}")
        d = json.load(open(p, encoding="utf-8"))
        hashes = [d.get("hash") or d.get("tx_id")]
    else:
        hashes = [x for x in a if x.startswith("0x")]
    if not hashes:
        sys.exit(__doc__)

    algum_vivo = False
    for h in hashes:
        tx = rpc("eth_getTransactionByHash", [h])
        if not tx:
            print(f"{h[:12]}..  NAO ENCONTRADA"); continue
        st = status_de(tx)
        vivo = st in VIVOS
        algum_vivo |= vivo
        print(f"{h[:12]}..  {st:16} rodadas={rodadas(tx)}  "
              f"{'<< VIVA: trava o contrato' if vivo else 'encerrada'}")
        print(f"              contrato {tx.get('recipient') or tx.get('to')}"
              f"  criada {tx.get('created_at') or tx.get('createdAt')}")
    if algum_vivo:
        print("\nEnquanto uma transacao esta viva, qualquer outra no MESMO "
              "contrato fica em PENDING.\nOu espera, ou redeploya o IC num "
              "endereco novo.")

if __name__ == "__main__":
    main()
