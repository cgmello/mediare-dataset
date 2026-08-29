#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenera os gabaritos com VOCABULARIO FECHADO, lendo a sentenca original.

O dataset tem 530 chaves de valor distintas em texto livre
('danos_materiais_deferidos', 'valor_pedido_A_B_S_S', 'total_condenacao_
periodo_especificado'...). A regua heuristica (gold.py) so consegue confiar
em 308 de 500, e as exclusoes nao sao aleatorias: um gabarito "limpo" e o
marcador de um caso simples. Isso enviesa toda medicao para cima.

Aqui o modelo le a sentenca REDIGIDA (redigir.py) e devolve as MESMAS quatro
rubricas que o comite usa. Sem chave livre, sem 'pedido' misturado com
'deferido'.

  python3 regabaritar.py --estimar          # custo, sem chamar nada
  python3 regabaritar.py --amostra 5        # 5 casos + diff contra o gold atual
  python3 regabaritar.py                    # todos, resumivel
  python3 regabaritar.py --comparar         # quanto o dataset utilizavel cresceu

Precisa de ANTHROPIC_API_KEY.
"""
import argparse, json, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import harness, redigir

VOCAB = ("principal", "multa", "danos_morais", "outros")

ESQUEMA = (
    '{"resultado": "procedente|parcialmente procedente|improcedente|extinto", '
    '"responsavel": "requerente|requerido|ambos_culpa_concorrente|nenhum", '
    '"revel": false, '
    '"valores": {"principal": 0.0, "multa": 0.0, "danos_morais": 0.0, "outros": 0.0}, '
    '"iliquido": false, '
    '"confianca": "alta|media|baixa", '
    '"obs": "uma frase curta"}'
)

INSTRUCAO = """Voce le o DISPOSITIVO de uma sentenca civel brasileira (nomes ja
removidos). Extraia SOMENTE o que foi EFETIVAMENTE CONDENADO ou DEFERIDO.
NUNCA o que foi pedido: essa confusao e o defeito exato que estamos corrigindo.

(a) principal: obrigacao principal deferida - alugueis vencidos, restituicao,
    danos materiais, comissao, devolucao de caucao, reembolso.
(b) multa: multa contratual ou clausula penal deferida.
(c) danos_morais: indenizacao por dano moral deferida. Fica FORA do total
    patrimonial de proposito - o comite nao arbitra dano moral.
(d) outros: valor patrimonial deferido que nao caiba nas anteriores.
(e) NAO inclua juros, correcao monetaria, honorarios advocaticios, custas,
    nem o valor da causa. Sao acessorios que o comite nao apura.
(f) Pedido NEGADO vale 0.0. Sentenca improcedente: TODAS as rubricas 0.0.
(g) Se o dispositivo remeter o valor a liquidacao ou arbitramento futuro,
    marque "iliquido": true e ponha 0.0 no que depende disso.
(h) responsavel: quem foi condenado a pagar. Havendo compensacao reciproca,
    sucumbencia reciproca no merito ou culpa concorrente, use
    "ambos_culpa_concorrente". Improcedente sem condenacao: "nenhum".
(i) revel: true se a sentenca menciona revelia do requerido.
(j) confianca: "baixa" se o dispositivo for ambiguo ou o valor nao for
    apuravel do texto; "media" se voce teve que somar parcelas espalhadas;
    "alta" se o valor esta explicito no dispositivo.

Numeros em ponto decimal, sem separador de milhar, sem "R$"."""


def carregar_sentencas(path):
    s = {}
    for l in open(path, encoding="utf-8"):
        d = json.loads(l)
        s[d["processo"]] = d
    return s


def alvos(ds, sents):
    """gabaritos reais/ouro que tem sentenca -> (cid, sentenca, gabarito)"""
    out = []
    for f in sorted(os.listdir(os.path.join(ds, "gabaritos"))):
        if not f.endswith(".json"):
            continue
        g = json.load(open(os.path.join(ds, "gabaritos", f), encoding="utf-8"))
        p = g.get("processo_tjsp")
        if g.get("origem") in ("real", "ouro") and p in sents:
            out.append((g.get("id") or f[:-5], sents[p], g))
    return out


def prompt_de(sent):
    txt, _ = redigir.redigir(redigir.texto_da(sent),
                             extra=[sent.get("magistrado")])
    return (INSTRUCAO
            + "\n\nResponda SOMENTE com este JSON, sem markdown:\n" + ESQUEMA
            + "\n\nSENTENCA:\n" + txt)


def normalizar(o):
    """impoe o vocabulario fechado, custe o que custar"""
    ic = harness.carregar_contrato("ic.py")
    _num = ic["_num"]
    v = o.get("valores") or {}
    val = {k: round(_num(v.get(k, 0.0)), 2) for k in VOCAB}
    res = (o.get("resultado") or "").strip().lower()
    if res not in ("procedente", "parcialmente procedente", "improcedente",
                   "extinto"):
        res = None
    resp = (o.get("responsavel") or "").strip().lower()
    if resp not in ("requerente", "requerido", "ambos_culpa_concorrente",
                    "nenhum"):
        resp = None
    conf = (o.get("confianca") or "").strip().lower()
    return {"resultado": res, "responsavel": resp, "valores": val,
            "total_patrimonial": round(val["principal"] + val["multa"]
                                       + val["outros"], 2),
            "revel": bool(o.get("revel")),
            "iliquido": bool(o.get("iliquido")),
            "confianca": conf if conf in ("alta", "media", "baixa") else "baixa",
            "obs": str(o.get("obs") or "")[:200]}


def coerente(g):
    """o gabarito novo contradiz a si mesmo?"""
    t = g["total_patrimonial"] + g["valores"]["danos_morais"]
    if g["resultado"] == "improcedente" and t > 0.01:
        return False, "improcedente com valor"
    if g["resultado"] in ("procedente", "parcialmente procedente") \
            and t < 0.01 and not g["iliquido"]:
        return False, "procedente com tudo zero e liquido"
    if g["responsavel"] == "nenhum" and t > 0.01:
        return False, "sem responsavel mas com valor"
    return True, "ok"


# ------------------------------------------------------------------ modos
def modo_estimar(alvo_lista, modelo):
    ic = harness.carregar_contrato("ic.py")   # so para falhar cedo se faltar
    chars = sum(len(prompt_de(s)) for _, s, _ in alvo_lista)
    tin = chars / 3.6                          # ~3.6 chars por token em pt-BR
    tout = len(alvo_lista) * 260
    precos = {"claude-haiku-4-5": (1.0, 5.0),
              "claude-sonnet-4-5": (3.0, 15.0)}
    pi, po = precos.get(modelo, (1.0, 5.0))
    custo = tin / 1e6 * pi + tout / 1e6 * po
    print(f"casos            : {len(alvo_lista)}")
    print(f"chars de prompt  : {chars:,.0f}")
    print(f"tokens estimados : {tin:,.0f} in / {tout:,.0f} out")
    print(f"modelo           : {modelo}  (${pi}/${po} por MTok)")
    print(f"CUSTO ESTIMADO   : US$ {custo:.2f}")
    print("\n(estimativa de entrada e aproximada: conta 3.6 chars por token)")


def modo_rodar(alvo_lista, args):
    cli = harness.fazer_cliente()
    ic = harness.carregar_contrato("ic.py")
    path = os.path.join(args.out, "gabaritos_v2.jsonl")
    os.makedirs(args.out, exist_ok=True)
    feitos = harness.ja_feitos(path)
    fila = [(c, s, g) for c, s, g in alvo_lista if c not in feitos]
    if args.limite:
        fila = fila[:args.limite]
    if not fila:
        print("nada a fazer (tudo ja regerado)")
        return path
    print(f"regerando {len(fila)} gabaritos ({len(feitos)} ja feitos)")

    def um(t):
        cid, sent, _g = t
        txt, ti, to = harness.chamar(cli, args.modelo, prompt_de(sent),
                                     max_tokens=1200)
        o = ic["_json_do_modelo"](txt)
        if o is None:
            raise ValueError("modelo nao devolveu JSON")
        novo = normalizar(o)
        ok, motivo = coerente(novo)
        novo.update({"id": cid, "coerente": ok, "motivo": motivo,
                     "tokens_in": ti, "tokens_out": to})
        harness.gravar(path, novo)

    erros = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(um, t): t[0] for t in fila}
        for n, f in enumerate(as_completed(futs), 1):
            try:
                f.result()
            except Exception as e:
                erros.append((futs[f], f"{type(e).__name__}: {e}"))
                if len(erros) <= 3:
                    print(f"  ERRO {futs[f]}: {type(e).__name__}: {str(e)[:200]}",
                          flush=True)
                if n >= 5 and len(erros) == n:
                    sys.exit("\n>>> 5 erros em 5 tentativas. Abortando.")
            if n % 20 == 0:
                print(f"  {n}/{len(fila)}", flush=True)
    print(f"pronto. erros: {len(erros)}")
    return path


def modo_comparar(args, alvo_lista):
    import gold
    path = os.path.join(args.out, "gabaritos_v2.jsonl")
    if not os.path.exists(path):
        sys.exit(f"nao achei {path} - rode sem --comparar primeiro")
    novos = {}
    for l in open(path, encoding="utf-8"):
        d = json.loads(l)
        novos[d["id"]] = d
    gabs = harness.carregar_gabaritos(args.dataset)

    velho_ok = novo_ok = ambos = 0
    ganhos, divergem = [], []
    for cid, _s, _g in alvo_lista:
        n = novos.get(cid)
        if not n:
            continue
        vt, _u, vok, _m = gold.avaliar(gabs[cid])
        nok = n["coerente"] and n["confianca"] != "baixa" and not n["iliquido"]
        velho_ok += bool(vok); novo_ok += bool(nok)
        if vok and nok:
            ambos += 1
            if abs(vt - n["total_patrimonial"]) > max(1.0, 0.02 * max(vt, 1)):
                divergem.append((cid, vt, n["total_patrimonial"], n["obs"]))
        elif nok and not vok:
            ganhos.append((cid, n["total_patrimonial"], n["obs"]))

    n = len([1 for c, _, _ in alvo_lista if c in novos])
    print(f"\n{'='*74}\nGABARITOS REAIS/OURO COM SENTENCA: {n}\n{'='*74}")
    print(f"  utilizaveis pela regua heuristica (gold.py) : {velho_ok:4d}  "
          f"({100*velho_ok/n:.0f}%)")
    print(f"  utilizaveis pelo vocabulario fechado        : {novo_ok:4d}  "
          f"({100*novo_ok/n:.0f}%)")
    print(f"  utilizaveis pelos DOIS                      : {ambos:4d}")
    print(f"\n  ganhos (so o novo consegue): {len(ganhos)}")
    for cid, t, obs in ganhos[:10]:
        print(f"    {cid}  {t:>12,.2f}   {obs[:52]}")
    print(f"\n  DIVERGEM entre as duas reguas: {len(divergem)}"
          f"   <- olhar estes na mao")
    for cid, v, nv, obs in divergem[:15]:
        print(f"    {cid}  heuristica {v:>12,.2f}  vs  fechado {nv:>12,.2f}"
              f"   {obs[:38]}")
    print("=" * 74)


def modo_amostra(alvo_lista, args):
    import gold
    gabs = harness.carregar_gabaritos(args.dataset)
    cli = harness.fazer_cliente()
    ic = harness.carregar_contrato("ic.py")
    for cid, sent, g in alvo_lista[:args.amostra]:
        txt, ti, to = harness.chamar(cli, args.modelo, prompt_de(sent),
                                     max_tokens=1200)
        o = ic["_json_do_modelo"](txt)
        novo = normalizar(o) if o else None
        vt, _u, vok, vm = gold.avaliar(gabs[cid])
        print("=" * 74)
        print(f"caso {cid}")
        print(f"  gabarito ATUAL  : {json.dumps(gabs[cid]['valores'], ensure_ascii=False)[:110]}")
        print(f"  regua heuristica: {vt if vok else 'EXCLUIDO'}  ({vm})")
        if novo:
            ok, motivo = coerente(novo)
            print(f"  vocab FECHADO   : {json.dumps(novo['valores'], ensure_ascii=False)}")
            print(f"                    total_patrimonial={novo['total_patrimonial']}  "
                  f"resultado={novo['resultado']}  resp={novo['responsavel']}")
            print(f"                    confianca={novo['confianca']} "
                  f"iliquido={novo['iliquido']} coerente={ok} ({motivo})")
            print(f"                    obs: {novo['obs']}")
        else:
            print("  vocab FECHADO   : FALHOU (sem JSON)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=".")
    ap.add_argument("--fonte", default="sentencas.jsonl")
    ap.add_argument("--out", default="res_gab")
    ap.add_argument("--modelo", default="claude-haiku-4-5")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--estimar", action="store_true")
    ap.add_argument("--amostra", type=int, default=0)
    ap.add_argument("--comparar", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(a.fonte):
        sys.exit(f"nao achei {a.fonte} (fica fora do repo, por conter nomes reais)")
    sents = carregar_sentencas(a.fonte)
    lista = alvos(a.dataset, sents)
    if not lista:
        sys.exit("nenhum gabarito real/ouro casou com uma sentenca")

    if a.estimar:
        return modo_estimar(lista, a.modelo)
    if a.comparar:
        return modo_comparar(a, lista)
    if a.amostra:
        return modo_amostra(lista, a)
    modo_rodar(lista, a)
    print("\nagora: python3 regabaritar.py --comparar")


if __name__ == "__main__":
    main()
