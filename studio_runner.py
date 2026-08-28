#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roda analyze_case(case_id) no GenLayer Studio direto da sua maquina, coletando
o recibo completo de cada transacao — a metade on-chain que nunca foi medida:
taxa de consenso, rotacoes, UNDETERMINED, e em qual bloco (EP0/EP1) cada
validador rejeitou.

Requisitos:
  Python >= 3.12 (o pacote usa collections.abc.Buffer)
  pip install genlayer-py

Uso:
  python3 studio_runner.py --contrato 0xSEU_ENDERECO                    # 30 casos (padrao)
  python3 studio_runner.py --contrato 0xA --contrato 0xB --limite 60   # 2 instancias em paralelo
  python3 studio_runner.py --contrato 0xA --casos 0002,0004,0006
  python3 studio_runner.py --contrato 0xA --relatorio                  # so o resumo, sem rodar

IMPORTANTE: transacoes no MESMO contrato enfileiram. O script espera cada uma
terminar antes de enviar a proxima ao mesmo endereco. Para paralelizar, faca
deploy do MESMO ic.py N vezes no Studio e passe os N enderecos.

Tempo observado por transacao: ~100s (aceita em 1 rodada) a ~525s (UNDETERMINED
apos 3 rotacoes). 30 casos em 1 contrato: 1h a 4h30. Os 500: 17h a 73h.
Resumivel: re-executar pula o que ja foi coletado.
"""
import argparse, base64, json, os, sys, threading, time, queue

# ---------------------------------------------------------------- decoder
def decode_eq(v) -> str:
    """eq_outputs: base64(tipo + varint LEB128 do tamanho + utf-8).
    O SDK embrulha em {'raw': <b64>} no leader_receipt e entrega string
    pura no consensus_history — aceita os dois."""
    if isinstance(v, dict):
        v = v.get("raw") or v.get("payload", {}).get("raw")
    if isinstance(v, (list, bytes, bytearray)):
        raw = bytes(v)
    else:
        raw = base64.b64decode(v)
    i, shift, length = 1, 0, 0
    while True:
        b = raw[i]; i += 1
        length |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return raw[i:i + length].decode("utf-8")

def como_dict(x):
    """O SDK pode devolver dict ou objeto; normaliza via json."""
    if isinstance(x, dict):
        return x
    try:
        return json.loads(json.dumps(x, default=lambda o: getattr(o, "__dict__", str(o))))
    except Exception:
        return {"_raw": str(x)}


TERMINAIS = {"FINALIZED", "ACCEPTED", "UNDETERMINED", "CANCELED"}

NUM2NOME = {"0": "UNINITIALIZED", "1": "PENDING", "2": "PROPOSING",
            "3": "COMMITTING", "4": "REVEALING", "5": "ACCEPTED",
            "6": "UNDETERMINED", "7": "FINALIZED", "8": "CANCELED",
            "9": "APPEAL_REVEALING", "10": "APPEAL_COMMITTING",
            "11": "READY_TO_FINALIZE", "12": "VALIDATORS_TIMEOUT",
            "13": "LEADER_TIMEOUT"}


def status_de(tx: dict) -> str:
    for k in ("status_name", "statusName", "status"):
        v = tx.get(k)
        if v is None:
            continue
        return NUM2NOME.get(str(v), str(v).upper())
    return "?"

# ---------------------------------------------------------------- metricas
def extrair_metricas(cid: str, tx: dict, dur: float) -> dict:
    m = {"id": cid, "hash": tx.get("hash") or tx.get("tx_id"),
         "status": status_de(tx), "result_name": tx.get("result_name"),
         "rounds": int(tx.get("num_of_rounds") or 0),
         "rotacoes": int(tx.get("rotation_count") or 0),
         "duracao_s": round(dur, 1)}
    cd = tx.get("consensus_data") or {}
    votos = cd.get("votes") or {}
    m["votos"] = sorted(v.lower() for v in votos.values())

    # em qual bloco cada validador da rodada final rejeitou (0=parecer, 1=termo)
    ep0 = ep1 = 0
    for v in (cd.get("validators") or []):
        nd = v.get("nondet_disagree")
        if nd == 0: ep0 += 1
        elif nd == 1: ep1 += 1
    m["disagree_ep0"], m["disagree_ep1"] = ep0, ep1

    # EP0 do lider da rodada final: consolidado do painel
    try:
        lr = (cd.get("leader_receipt") or [{}])[0]
        painel = json.loads(decode_eq(lr["eq_outputs"]["0"]))
        cons = painel.get("consolidado", {})
        m["faixa_total"] = cons.get("faixa_total")
        m["unanime"] = cons.get("unanime")
        m["responsavel"] = cons.get("responsavel_majoritario")
        nc = lr.get("node_config") or {}
        m["lider_modelo"] = (nc.get("primary_model") or {}).get("model") or nc.get("model")
    except Exception as e:
        m["erro_decode"] = str(e)[:120]

    # historico de rotacao: um consolidado por lider que tentou
    hist = []
    for r in ((tx.get("consensus_history") or {}).get("consensus_results") or []):
        try:
            lr = (r.get("leader_result") or [{}])[0]
            p = json.loads(decode_eq(lr["eq_outputs"]["0"]))
            hist.append({"faixa": p["consolidado"].get("faixa_total"),
                         "unanime": p["consolidado"].get("unanime")})
        except Exception:
            hist.append(None)
    if hist:
        m["rodadas"] = hist
    return m


# ---------------------------------------------------------------- worker
def rodar_caso(cli, conta, contrato, cid, args):
    ini = time.time()
    txh = cli.write_contract(address=contrato, function_name="analyze_case",
                             args=[cid], account=conta)
    txh_hex = txh.hex() if hasattr(txh, "hex") else str(txh)
    if not txh_hex.startswith("0x"):
        txh_hex = "0x" + txh_hex
    print(f"    {cid}: tx enviada {txh_hex}", flush=True)
    ultimo = None
    while True:
        time.sleep(args.poll)
        tx = como_dict(cli.get_transaction(transaction_hash=txh_hex))
        st = status_de(tx)
        if st != ultimo:
            print(f"    {cid}: {st}  ({time.time()-ini:.0f}s)", flush=True)
            ultimo = st
        if st in TERMINAIS:
            return tx, time.time() - ini
        if time.time() - ini > args.timeout:
            tx["_timeout"] = True
            return tx, time.time() - ini

def worker(nome, cli, conta, contrato, fila, args, lock):
    while True:
        try:
            cid = fila.get_nowait()
        except queue.Empty:
            return
        try:
            tx, dur = rodar_caso(cli, conta, contrato, cid, args)
            met = extrair_metricas(cid, tx, dur)
            met["contrato"] = contrato
            with lock:
                with open(os.path.join(args.out, "chain.jsonl"), "a", encoding="utf-8") as f:
                    f.write(json.dumps(met, ensure_ascii=False) + "\n")
                json.dump(tx, open(os.path.join(args.out, "receipts", f"{cid}.json"),
                                   "w", encoding="utf-8"), ensure_ascii=False, default=str)
                print(f"[{nome}] {cid}: {met['status']:12s} {met.get('result_name') or '':16s} "
                      f"rodadas={met['rounds']} rot={met['rotacoes']} {met['duracao_s']:.0f}s "
                      f"faixa={met.get('faixa_total')}", flush=True)
        except Exception as e:
            with lock:
                with open(os.path.join(args.out, "chain.jsonl"), "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id": cid, "status": "ERRO_SCRIPT",
                                        "erro": str(e)[:300]}, ensure_ascii=False) + "\n")
                print(f"[{nome}] {cid}: ERRO {type(e).__name__}: {str(e)[:160]}", flush=True)


# ---------------------------------------------------------------- resumo
def resumo(args):
    path = os.path.join(args.out, "chain.jsonl")
    if not os.path.exists(path):
        sys.exit("nada coletado ainda")
    linhas = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    vistos = {}
    for l in linhas:
        vistos[l["id"]] = l          # ultima tentativa de cada caso vale
    ls = list(vistos.values())
    n = len(ls)
    from collections import Counter
    st = Counter(l["status"] for l in ls)
    print(f"\n{'='*62}\nCONSENSO ON-CHAIN — {n} casos\n{'='*62}")
    for k, v in st.most_common():
        print(f"  {k:14s} {v:4d}  ({100*v/n:.0f}%)")
    ok = [l for l in ls if l["status"] in ("FINALIZED", "ACCEPTED")]
    und = [l for l in ls if l["status"] == "UNDETERMINED"]
    if ok:
        r1 = sum(1 for l in ok if l.get("rounds", 1) <= 1)
        print(f"\naceitos em 1 rodada       : {r1}/{len(ok)}")
        print(f"duracao media (aceitos)   : {sum(l['duracao_s'] for l in ok)/len(ok):.0f}s")
        u = sum(1 for l in ok if l.get("unanime"))
        print(f"unanimes entre os aceitos : {u}/{len(ok)}")
    if und:
        print(f"duracao media (undeterm.) : {sum(l['duracao_s'] for l in und)/len(und):.0f}s")
    e0 = sum(l.get("disagree_ep0", 0) for l in ls)
    e1 = sum(l.get("disagree_ep1", 0) for l in ls)
    print(f"\nrejeicoes por bloco: EP0 (parecer) = {e0}   EP1 (termo/pauta) = {e1}")
    rot = Counter(l.get("rotacoes", 0) for l in ls)
    print("rotacoes:", dict(sorted(rot.items())))
    print("=" * 62)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contrato", action="append", required=True,
                    help="endereco 0x... do ic.py deployado (repita p/ paralelizar)")
    ap.add_argument("--dataset", default=".")
    ap.add_argument("--out", default="res_studio")
    ap.add_argument("--casos", default="", help="lista explicita: 0002,0004")
    ap.add_argument("--desde", default="")
    ap.add_argument("--limite", type=int, default=30)
    ap.add_argument("--timeout", type=int, default=900, help="seg por transacao")
    ap.add_argument("--poll", type=int, default=10)
    ap.add_argument("--relatorio", action="store_true")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.out, "receipts"), exist_ok=True)
    if args.relatorio:
        resumo(args); return

    from genlayer_py import create_client, create_account
    from genlayer_py.chains import studionet

    # conta persistida: mesma chave entre execucoes
    kpath = os.path.join(args.out, "conta.key")
    if os.path.exists(kpath):
        conta = create_account(open(kpath).read().strip())
    else:
        conta = create_account()
        open(kpath, "w").write(conta.key.hex())
        os.chmod(kpath, 0o600)
    print(f"conta: {conta.address}")

    if args.casos:
        ids = [c.strip().zfill(4) for c in args.casos.split(",") if c.strip()]
    else:
        ids = sorted(f[:-5] for f in os.listdir(os.path.join(args.dataset, "casos"))
                     if f.endswith(".json"))
        if args.desde:
            ids = [c for c in ids if c >= args.desde]
    feitos = set()
    ch = os.path.join(args.out, "chain.jsonl")
    if os.path.exists(ch):
        for l in open(ch, encoding="utf-8"):
            try:
                o = json.loads(l)
                if o.get("status") in TERMINAIS:
                    feitos.add(o["id"])
            except Exception:
                pass
    ids = [c for c in ids if c not in feitos][:args.limite]
    if not ids:
        print("nada a fazer (tudo ja coletado)"); resumo(args); return

    ncon = len(args.contrato)
    est_lo, est_hi = len(ids) * 100 / ncon / 60, len(ids) * 525 / ncon / 60
    print(f"{len(ids)} casos, {ncon} contrato(s) -> estimativa {est_lo:.0f} a {est_hi:.0f} min")
    print(f"({len(feitos)} ja coletados; resumivel com Ctrl-C)\n")

    fila = queue.Queue()
    for c in ids:
        fila.put(c)
    lock = threading.Lock()
    ths = []
    for i, addr in enumerate(args.contrato):
        cli = create_client(chain=studionet)
        t = threading.Thread(target=worker, args=(f"C{i}", cli, conta, addr, fila, args, lock),
                             daemon=True)
        t.start(); ths.append(t)
    try:
        for t in ths:
            t.join()
    except KeyboardInterrupt:
        print("\ninterrompido — o que terminou esta salvo; re-execute para continuar")
        return
    resumo(args)


if __name__ == "__main__":
    main()
