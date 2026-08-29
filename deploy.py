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

NUM2NOME = {"0": "UNINITIALIZED", "1": "PENDING", "2": "PROPOSING",
            "3": "COMMITTING", "4": "REVEALING", "5": "ACCEPTED",
            "6": "UNDETERMINED", "7": "FINALIZED", "8": "CANCELED",
            "9": "APPEAL_REVEALING", "10": "APPEAL_COMMITTING",
            "11": "READY_TO_FINALIZE", "12": "VALIDATORS_TIMEOUT",
            "13": "LEADER_TIMEOUT"}
# para um deploy, ACCEPTED ja basta: o endereco existe e aceita chamadas.
BONS = {"ACCEPTED", "FINALIZED"}
RUINS = {"UNDETERMINED", "CANCELED", "VALIDATORS_TIMEOUT", "LEADER_TIMEOUT"}

def status_de(tx):
    for k in ("status_name", "statusName", "status"):
        v = tx.get(k)
        if v is not None:
            return NUM2NOME.get(str(v), str(v).upper())
    return "?"

def esperar(cli, txh, timeout, poll):
    """polling proprio: o wait_for_transaction_receipt do SDK exige o enum
    TransactionStatus e estoura AttributeError ao montar a mensagem de erro."""
    ini, ultimo = time.time(), None
    while True:
        tx = como_dict(cli.get_transaction(transaction_hash=txh))
        st = status_de(tx)
        if st != ultimo:
            print(f"      {st}  ({time.time()-ini:.0f}s)", flush=True)
            ultimo = st
        if st in BONS:
            return tx, st
        if st in RUINS:
            sys.exit(f"  deploy terminou em {st} - nao da para usar")
        if time.time() - ini > timeout:
            sys.exit(f"  deploy nao decidiu em {timeout}s (ultimo: {st})\n"
                     f"  hash {txh}\n"
                     f"  consulte depois: python3 estado.py {txh}\n"
                     f"  e, se tiver virado ACCEPTED, pegue o endereco com:\n"
                     f"    python3 deploy.py --tx {txh}")
        time.sleep(poll)

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

def registrar(out, addr):
    """acumula enderecos em <out>/contratos.txt, sem repetir"""
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, "contratos.txt")
    atuais = [l.strip() for l in open(p, encoding="utf-8")] if os.path.exists(p) else []
    if addr not in atuais:
        with open(p, "a", encoding="utf-8") as f:
            f.write(addr + "\n")
    return p

def conhecidos(out):
    p = os.path.join(out, "contratos.txt")
    return [l.strip() for l in open(p, encoding="utf-8")] if os.path.exists(p) else []

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
    ap.add_argument("--timeout", type=int, default=600, help="seg por deploy")
    ap.add_argument("--poll", type=int, default=5)
    ap.add_argument("--tx", default="", help="so resolve o endereco de um deploy ja enviado")
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

    if a.tx:
        rec, st = esperar(cli, a.tx, a.timeout, a.poll)
        addr = cava_endereco(rec)
        if addr:
            registrar(a.out, addr)
        print(f"\n{a.tx}  {st}  ->  {addr or 'ENDERECO NAO ENCONTRADO'}")
        if not addr:
            json.dump(rec, open(os.path.join(a.out, "deploy_tx.json"), "w"),
                      ensure_ascii=False, default=str, indent=2)
            print(f"receipt em {a.out}/deploy_tx.json - me mande as chaves")
        return

    enderecos = []
    for i in range(a.n):
        ini = time.time()
        txh = cli.deploy_contract(code=codigo, args=[], account=conta)
        txh = txh.hex() if hasattr(txh, "hex") else str(txh)
        if not txh.startswith("0x"):
            txh = "0x" + txh
        print(f"[{i+1}/{a.n}] tx {txh}  aguardando...", flush=True)
        rec, st = esperar(cli, txh, a.timeout, a.poll)
        addr = cava_endereco(rec)
        if not addr:
            print("  nao achei o endereco no receipt. Chaves de topo:",
                  list(rec)[:20])
            json.dump(rec, open(os.path.join(a.out, f"deploy_{i}.json"), "w"),
                      ensure_ascii=False, default=str, indent=2)
            sys.exit(f"  receipt salvo em {a.out}/deploy_{i}.json - me mande as chaves")
        enderecos.append(addr)
        registrar(a.out, addr)
        print(f"  -> {addr}   ({time.time()-ini:.0f}s)\n", flush=True)

    todos = conhecidos(a.out) or enderecos
    print("=" * 70)
    print(f"enderecos em {a.out}/contratos.txt ({len(todos)}):")
    for e in todos:
        print("  " + e)
    print("\nrodar:")
    args_c = " ".join(f"--contrato {e}" for e in todos)
    print(f"  python3 studio_runner.py {args_c} \\\n"
          f"    --casos 0002,0003,0004,0016,0021,0028,0029,0033,0039,0040,0043,0046,0048 \\\n"
          f"    --out {a.out} --timeout 900 --timeout-duro 2400")

if __name__ == "__main__":
    main()
