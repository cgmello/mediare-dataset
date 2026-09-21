#!/usr/bin/env python3
"""Recupera transações Studio já enviadas sem jamais reenviá-las."""

import argparse
import json
from pathlib import Path
import time

from studio_runner import TERMINAIS, como_dict, extrair_metricas, redact, status_de


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--tx", action="append", required=True, help="CASE_ID=0xHASH")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--poll", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    from genlayer_py import create_client
    from genlayer_py.chains import studionet

    client = create_client(chain=studionet)
    out = Path(args.out)
    (out / "receipts").mkdir(parents=True, exist_ok=True)
    chain = out / "chain.jsonl"
    done = {}
    if chain.exists():
        for line in chain.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("status") in TERMINAIS:
                    done[row.get("id")] = row

    for spec in args.tx:
        cid, tx_hash = spec.split("=", 1)
        cid = cid.zfill(4)
        if cid in done:
            print(json.dumps({"case": cid, "status": "already_terminal"}))
            continue
        started = time.time()
        last = None
        errors = 0
        while True:
            if time.time() - started > args.timeout:
                raise SystemExit(f"timeout recuperando {cid}; hash preservado: {tx_hash}")
            try:
                tx = como_dict(client.get_transaction(transaction_hash=tx_hash))
                state = status_de(tx)
                errors = 0
                if state != last:
                    print(json.dumps({"case": cid, "hash": tx_hash, "status": state}))
                    last = state
                if state in TERMINAIS:
                    metrics = extrair_metricas(cid, tx, time.time() - started)
                    metrics["contrato"] = args.contract
                    metrics["recovered"] = True
                    with chain.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(metrics, ensure_ascii=False) + "\n")
                    (out / "receipts" / f"{cid}.json").write_text(
                        json.dumps(redact(tx), ensure_ascii=False, default=str), encoding="utf-8"
                    )
                    break
            except Exception as exc:
                errors += 1
                print(json.dumps({"case": cid, "status": "rpc_retry", "error_type": type(exc).__name__, "attempt": errors}))
            time.sleep(args.poll)


if __name__ == "__main__":
    main()
