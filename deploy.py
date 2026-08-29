#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deploy do ic.py no Studio e devolve o endereco novo.

  python3 deploy.py                 # deploya ic.py, 1 instancia
  python3 deploy.py --n 3           # 3 enderecos para rodar em paralelo
  python3 deploy.py --ic ic.py --out res_v8b

Reusa a mesma conta de res_*/conta.key quando existe, para nao espalhar chaves.
Um endereco novo vem com fila limpa: e o jeito de destravar um contrato preso
por uma transacao que nao resolve (ver estado.py).
"""
import argparse, json, os, sys, time

def cava_endereco(o, visto=None):
    """procura recursivamente qualquer chave de endereco de contrato"""
    if isinstance(o, dict):
        for k, v in o.items():
            if "contract" in k.lower() and "address" in k.lower() and isinstance(v, str) \
               and v.startswith("0x") and len(v) == 42:
                return v
        for v in o.values():
            r = cava_endereco(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = cava_endereco(v)
            if r:
                return r
    return None

def como_dict(o):
    if isinstance(o, dict):
        return o
    for attr in ("model_dump", "dict", "_asdict"):
        if hasattr(o, attr):
            try:
                return getattr(o, attr)()
            except Exception:
                pass
    return json.loads(json.dumps(o, default=lambda x: getattr(x, "__dict__", str(x))))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ic", default="ic.py")
    ap.add_argument("--n", type=int, default=1, help="quantos enderecos deployar")
    ap.add_argument("--out", default="res_novo", help="pasta da conta.key")
    a = ap.parse_args()

    if not os.path.exists(a.ic):
        sys.exit(f"nao achei {a.ic}")
    codigo = open(a.ic, "rb").read()

    from genlayer_py import create_client, create_account
    from genlayer_py.chains import studionet

    os.makedirs(a.out, exist_ok=True)
    kpath = os.path.join(a.out, "conta.key")
    if os.path.exists(kpath):
        conta = create_account(open(kpath).read().strip())
    else:
        conta = create_account()
        open(kpath, "w").write(conta.key.hex())
        os.chmod(kpath, 0o600)
    print(f"conta   : {conta.address}")
    print(f"contrato: {a.ic}  ({len(codigo)} bytes)\n")

    cli = create_client(chain=studionet)
    enderecos = []
    for i in range(a.n):
        ini = time.time()
        txh = cli.deploy_contract(code=codigo, args=[], account=conta)
        txh = txh.hex() if hasattr(txh, "hex") else str(txh)
        if not txh.startswith("0x"):
            txh = "0x" + txh
        print(f"[{i+1}/{a.n}] tx {txh}  aguardando...", flush=True)
        rec = como_dict(cli.wait_for_transaction_receipt(
            transaction_hash=txh, status="FINALIZED"))
        addr = cava_endereco(rec)
        if not addr:
            print("  nao achei o endereco no receipt. Chaves de topo:",
                  list(rec)[:20])
            json.dump(rec, open(os.path.join(a.out, f"deploy_{i}.json"), "w"),
                      ensure_ascii=False, default=str, indent=2)
            sys.exit(f"  receipt salvo em {a.out}/deploy_{i}.json - me mande as chaves")
        enderecos.append(addr)
        print(f"  -> {addr}   ({time.time()-ini:.0f}s)\n", flush=True)

    print("=" * 70)
    print("enderecos:", " ".join(enderecos))
    print("\nrodar:")
    args_c = " ".join(f"--contrato {e}" for e in enderecos)
    print(f"  python3 studio_runner.py {args_c} \\\n"
          f"    --casos 0002,0003,0004,0016,0021,0028,0029,0033,0039,0040,0043,0046,0048 \\\n"
          f"    --out {a.out} --timeout 900 --timeout-duro 2400")

if __name__ == "__main__":
    main()
