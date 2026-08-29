#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness de avaliacao do painel de lentes da Mediare (off-chain).

Os prompts NAO sao duplicados aqui: sao importados do proprio arquivo do
Intelligent Contract (ic.py), para que harness e contrato nunca divirjam.

Modos:
  --auditar     sem API. Normaliza 'responsavel', classifica os gabaritos por
                forma dos 'valores' e escreve auditoria_gabaritos.csv.
  --normalizar  com API. 1 chamada barata por gabarito -> total devido +
                as chaves que foram somadas (para voce conferir no CSV).
  --rodar       com API. 3 lentes por caso -> painel + consolidado.
  --relatorio   sem API. Tabela de acerto por lente e por caminho.

Todos os modos com API sao resumiveis: reexecutar pula o que ja foi feito.

Espera esta pasta: casos/  gabaritos/  manifest.json  ic.py  harness.py

  pip install anthropic
  export ANTHROPIC_API_KEY=...
  python3 harness.py --auditar
  python3 harness.py --normalizar
  python3 harness.py --rodar --limite 50
  python3 harness.py --relatorio
"""
import argparse, csv, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

MODELO_PADRAO = "claude-sonnet-4-5"
TOL = 0.15          # tolerancia relativa no total (15%, como sugerem os gabaritos)
LOCK = threading.Lock()

# ---------------------------------------------------------------- contrato
def carregar_contrato(path):
    """Executa o prefixo do IC (ate a classe) e devolve os prompts + _consolidar.
    Garante que o harness usa EXATAMENTE os prompts que estao no contrato."""
    if not os.path.exists(path):
        sys.exit(f"contrato nao encontrado: {path}\n"
                 "Salve nesta pasta o mesmo arquivo .py que voce deployou no Studio\n"
                 "(ex.: ic.py), ou aponte com --ic /caminho/do/contrato.py")
    src = open(path, encoding="utf-8").read()
    prefixo = src.split("class MediareCommittee")[0].replace("from genlayer import *", "")
    ns = {}
    exec(compile(prefixo, path, "exec"), ns)
    preciso = ("REGRAS", "LENTES", "SCHEMA", "_consolidar",
               "_painel_de", "_tese_de", "_json_do_modelo", "_num",
               "_painel2_de", "_consolidar2")
    faltando = [k for k in preciso if k not in ns]
    if faltando:
        sys.exit(f"contrato {path} nao expoe: {faltando}\n"
                 "O harness roda o MESMO codigo de painel do contrato; sem\n"
                 "essas funcoes a medicao off-chain nao diz nada sobre o\n"
                 "comportamento on-chain.")
    return ns


# ---------------------------------------------------------------- gabaritos
CHAVES_FECHADAS = {"principal", "multa", "danos_morais", "outros", "danos_materiais",
                   "multa_contratual", "restituicao", "lucros_cessantes", "total_devido"}
INDETERMINADOS = ("impossivel", "impossível", "nao determinado", "não determinado", "nenhum")


def norm_responsavel(r):
    r = (r or "").strip().lower()
    if any(t in r for t in INDETERMINADOS):
        return None                       # gabarito sem responsavel -> fora da amostra
    if r.startswith(("requerido", "requerida", "requeridos", "requeridas")):
        return "requerido"
    if r.startswith("requerente"):
        return "requerente"
    if r.startswith(("parcial", "ambos", "ambas")):
        return "parcial_ambos" if r.startswith("parcial") else "ambos_culpa_concorrente"
    return None


def classificar_valores(valores):
    """Como o total deste gabarito pode ser obtido."""
    ks = set(valores)
    if not ks:
        return "vazio"
    if any("pedid" in k for k in ks):
        return "ambiguo_pedido"            # mistura pedido com deferimento
    totais = [k for k in ks if k.startswith("total")]
    if totais and len(ks) > len(totais):
        return "total_mais_parcelas"       # risco de dupla contagem
    if totais:
        return "so_total"
    if ks <= CHAVES_FECHADAS:
        return "somavel"
    return "chaves_livres"


def carregar_gabaritos(ds):
    out = {}
    for f in sorted(os.listdir(os.path.join(ds, "gabaritos"))):
        if not f.endswith(".json"):
            continue
        g = json.load(open(os.path.join(ds, "gabaritos", f), encoding="utf-8"))
        pe = g.get("parecer_esperado", {}) or {}
        cid = g.get("id") or f[:-5]
        out[cid] = {
            "id": cid,
            "origem": g.get("origem", "?"),
            "responsavel_bruto": pe.get("responsavel"),
            "responsavel": norm_responsavel(pe.get("responsavel")),
            "resultado": (pe.get("resultado") or "").strip().lower() or None,
            "valores": pe.get("valores", {}) or {},
            "classe": classificar_valores(pe.get("valores", {}) or {}),
        }
    return out


# ---------------------------------------------------------------- jsonl
def ja_feitos(path, campo="id"):
    if not os.path.exists(path):
        return set()
    feitos = set()
    with open(path, encoding="utf-8") as fh:
        for l in fh:
            l = l.strip()
            if not l:
                continue
            try:
                feitos.add(json.loads(l)[campo])
            except Exception:
                pass
    return feitos


def gravar(path, obj):
    with LOCK:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def ler_jsonl(path):
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as fh:
        for l in fh:
            l = l.strip()
            if l:
                try:
                    o = json.loads(l)
                    out[o["id"]] = o
                except Exception:
                    pass
    return out


# ---------------------------------------------------------------- LLM
def fazer_cliente():
    try:
        from anthropic import Anthropic
    except ImportError as e:
        sys.exit(
            f"nao consegui importar 'anthropic': {e}\n\n"
            f"python3 em uso: {sys.executable}\n"
            f"versao        : {sys.version.split()[0]}\n\n"
            "Instale NO MESMO interpretador:\n"
            f"   {sys.executable} -m pip install anthropic\n\n"
            "Se der 'externally-managed-environment' (macOS/Debian), use venv:\n"
            "   python3 -m venv .venv && source .venv/bin/activate\n"
            "   pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("falta a chave:  export ANTHROPIC_API_KEY=sk-ant-...")
    return Anthropic()


def chamar(cli, modelo, prompt, max_tokens=4000, tentativas=4):
    ultimo = None
    for i in range(tentativas):
        try:
            r = cli.messages.create(model=modelo, max_tokens=max_tokens,
                                    messages=[{"role": "user", "content": prompt}])
        except Exception as e:                 # so a CHAMADA e reterritavel
            ultimo = e
            time.sleep(2 ** i)
            continue
        # daqui pra baixo o erro nao e transitorio: repetir so queima credito.
        # modelos com raciocinio devolvem um bloco 'thinking' antes do 'text'.
        txt = "".join(b.text for b in r.content
                      if getattr(b, "type", None) == "text")
        if not txt:
            raise RuntimeError(
                f"resposta sem bloco de texto: {[getattr(b,'type','?') for b in r.content]}")
        return txt, r.usage.input_tokens, r.usage.output_tokens
    raise ultimo


def extrair_json(txt):
    """Usado so pelo modo_normalizar (gabaritos), que nao passa pelo painel.
    O painel usa _json_do_modelo do proprio ic.py - ver carregar_contrato."""
    t = txt.strip()
    # remove cercas ```json ... ``` mesmo com preambulo antes
    if "```" in t:
        partes = [p for p in t.split("```") if "{" in p]
        if partes:
            t = max(partes, key=len).lstrip()
            if t.startswith("json"):
                t = t[4:]
    i = t.find("{")
    if i < 0:
        raise ValueError("sem JSON na resposta")
    obj, _ = json.JSONDecoder().raw_decode(t[i:])   # le UM objeto, ignora o resto
    return obj


# ---------------------------------------------------------------- modos
def modo_auditar(args, gabs):
    saida = os.path.join(args.out, "auditoria_gabaritos.csv")
    cont = {}
    with open(saida, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "origem", "classe", "responsavel_bruto", "responsavel_norm",
                    "resultado", "n_chaves", "chaves"])
        for cid, g in sorted(gabs.items()):
            cont[g["classe"]] = cont.get(g["classe"], 0) + 1
            w.writerow([cid, g["origem"], g["classe"], g["responsavel_bruto"],
                        g["responsavel"] or "", g["resultado"] or "",
                        len(g["valores"]), "|".join(sorted(g["valores"]))])
    sem_resp = sum(1 for g in gabs.values() if g["responsavel"] is None)
    print(f"{len(gabs)} gabaritos -> {saida}\n")
    print("classe dos 'valores':")
    for k, v in sorted(cont.items(), key=lambda x: -x[1]):
        print(f"  {v:4d}  {k}")
    print(f"\nresponsavel normalizado : {len(gabs)-sem_resp}/{len(gabs)}")
    print(f"sem responsavel utilizavel: {sem_resp} (saem da pontuacao)")
    somaveis = cont.get("somavel", 0) + cont.get("so_total", 0)
    print(f"\ntotal obtenivel sem LLM : {somaveis}")
    print(f"precisa de --normalizar : {len(gabs)-somaveis}")


PROMPT_NORM = """Abaixo esta o gabarito de um caso de mediacao (decisao ja proferida).
Diga qual e o VALOR TOTAL EM DINHEIRO que a parte responsavel foi condenada a pagar.

Regras:
- Some apenas rubricas DEFERIDAS. Ignore valores meramente PEDIDOS ou NEGADOS.
- Ignore limites, tetos e saldos de apolice: sao materia de execucao, nao condenacao.
- Se houver uma chave que ja represente o total (total_devido, total_condenacao,
  total_principal...), use ELA e nao some as parcelas junto.
- Se nada foi deferido, o total e 0.

Responda SO este JSON:
{"total": <numero>, "chaves_somadas": ["..."], "obs": "<uma frase>"}

GABARITO:
<<G>>
"""


def modo_normalizar(args, gabs):
    cli = fazer_cliente()
    path = os.path.join(args.out, "gabaritos_norm.jsonl")
    feitos = ja_feitos(path)
    alvo = [g for cid, g in sorted(gabs.items()) if cid not in feitos]
    if args.limite:
        alvo = alvo[:args.limite]
    print(f"normalizando {len(alvo)} gabaritos ({len(feitos)} ja feitos)")

    def um(g):
        p = PROMPT_NORM.replace("<<G>>", json.dumps(
            {"responsavel": g["responsavel_bruto"], "resultado": g["resultado"],
             "valores": g["valores"]}, ensure_ascii=False, indent=1))
        try:
            txt, ti, to = chamar(cli, args.modelo, p, max_tokens=1000)
            o = extrair_json(txt)
            gravar(path, {"id": g["id"], "total": round(float(o["total"]), 2),
                          "chaves_somadas": o.get("chaves_somadas", []),
                          "obs": o.get("obs", ""), "classe": g["classe"],
                          "tokens_in": ti, "tokens_out": to})
            return None
        except Exception as e:
            gravar(path, {"id": g["id"], "total": None, "erro": str(e)[:200],
                          "classe": g["classe"]})
            return g["id"]

    erros = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(um, g): g["id"] for g in alvo}
        for n, f in enumerate(as_completed(futs), 1):
            e = f.result()
            if e:
                erros.append(e)
            if n % 25 == 0:
                print(f"  {n}/{len(alvo)}", flush=True)
    print(f"pronto. erros: {len(erros)}")
    # CSV de conferencia
    norm = ler_jsonl(path)
    csvp = os.path.join(args.out, "normalizacao.csv")
    with open(csvp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "classe", "total_apurado", "chaves_somadas", "chaves_originais", "obs"])
        for cid in sorted(norm):
            o = norm[cid]
            w.writerow([cid, o.get("classe"), o.get("total"),
                        "|".join(o.get("chaves_somadas", [])),
                        "|".join(sorted(gabs[cid]["valores"])) if cid in gabs else "",
                        o.get("obs", o.get("erro", ""))])
    print(f"confira -> {csvp}")


def modo_rodar(args, gabs):
    ic = carregar_contrato(args.ic)
    LENTES = ic["LENTES"]
    if args.estagios == 2:
        _painel_de = ic["_painel2_de"]
        print("painel de DOIS estagios (merito primeiro, valor depois)")
    else:
        _painel_de = ic["_painel_de"]
    cli = fazer_cliente()
    path = os.path.join(args.out, "paineis.jsonl")
    feitos = ja_feitos(path)
    if args.casos:
        bruto = args.casos
        if bruto.startswith("@"):          # lista num arquivo, um por linha ou csv
            bruto = open(bruto[1:], encoding="utf-8").read()
        ids = [c.strip().zfill(4) for c in bruto.replace("\n", ",").split(",")
               if c.strip()]
        ids = [c for c in ids if c not in feitos]
    else:
        ids = [c for c in sorted(gabs) if c not in feitos and c >= args.desde]
        if args.limite:
            ids = ids[:args.limite]
    print(f"rodando {len(ids)} casos x {len(LENTES)} lentes ({len(feitos)} ja feitos)")

    def um(cid):
        caso = json.load(open(os.path.join(args.dataset, "casos", f"{cid}.json"),
                              encoding="utf-8"))
        corpo = json.dumps(caso["documentos"], sort_keys=True, ensure_ascii=False)
        uso = {"in": 0, "out": 0}

        def pedir(p):
            """o que o contrato faz com gl.nondet.exec_prompt"""
            txt, ti, to = chamar(cli, args.modelo, p, max_tokens=4000)
            uso["in"] += ti; uso["out"] += to
            return txt

        # MESMA funcao que o contrato executa on-chain: prompt, parse,
        # normalizacao, descarte de lente e consolidacao. So a chamada ao
        # modelo muda. Se o painel quebrar aqui, quebra la.
        painel = _painel_de(pedir, corpo)
        gravar(path, {"id": cid, **painel,
                      "tokens_in": uso["in"], "tokens_out": uso["out"],
                      "modelo": args.modelo})

    erros = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(um, c): c for c in ids}
        for n, f in enumerate(as_completed(futs), 1):
            try:
                f.result()
            except Exception as e:
                erros.append((futs[f], f"{type(e).__name__}: {e}"))
                if len(erros) <= 3:            # mostra os primeiros na hora
                    print(f"  ERRO {futs[f]}: {type(e).__name__}: {str(e)[:300]}",
                          flush=True)
                if n >= 5 and len(erros) == n:  # tudo falhando: nao queime credito
                    sys.exit("\n>>> 5 erros em 5 tentativas. Abortando.")
            if n % 5 == 0:
                print(f"  {n}/{len(ids)}  erros={len(erros)}", flush=True)
    print(f"pronto. erros: {len(erros)}")
    for cid, e in erros[:10]:
        print(f"  {cid}: {e}")


def _perto(a, b, tol=TOL):
    if a is None or b is None:
        return None
    if abs(a) < 0.01 and abs(b) < 0.01:
        return True
    if abs(a) < 0.01 or abs(b) < 0.01:
        return False
    return abs(a - b) <= tol * max(abs(a), abs(b))


def modo_relatorio(args, gabs):
    paineis = ler_jsonl(os.path.join(args.out, "paineis.jsonl"))
    norm = ler_jsonl(os.path.join(args.out, "gabaritos_norm.jsonl"))
    if not paineis:
        sys.exit("rode --rodar antes")

    lentes = sorted({t["lente"] for p in paineis.values() for t in p["teses"]})
    acc = {l: {"resp_ok": 0, "resp_n": 0, "tot_ok": 0, "tot_n": 0} for l in lentes}
    maioria = {"resp_ok": 0, "resp_n": 0}
    faixa = {"contem": 0, "n": 0}
    unanime = {"n": 0, "certo": 0, "avaliavel": 0}
    divergente = {"n": 0, "faixa_contem": 0, "avaliavel": 0}
    custo_in = custo_out = 0

    for cid, p in sorted(paineis.items()):
        g = gabs.get(cid)
        if not g:
            continue
        custo_in += p.get("tokens_in", 0); custo_out += p.get("tokens_out", 0)
        cons = p["consolidado"]
        gtot = None
        o = norm.get(cid)
        if o and o.get("total") is not None:
            gtot = float(o["total"])
            # o IC ignora danos morais em RUBRICAS; o gabarito precisa ignorar tambem,
            # senao todo caso com dano moral marca a lente como errada sem ser.
            for k in o.get("chaves_somadas", []):
                if "moral" in k.lower():
                    gtot -= float(g["valores"].get(k, 0.0) or 0.0)
            gtot = round(gtot, 2)
        elif o is None and g["classe"] in ("somavel", "so_total"):
            v = g["valores"]
            tks = [k for k in v if k.startswith("total")]
            gtot = float(v[tks[0]]) if tks else round(sum(float(x or 0) for x in v.values()), 2)

        # responsavel
        if g["responsavel"]:
            maioria["resp_n"] += 1
            if cons["responsavel_majoritario"] == g["responsavel"]:
                maioria["resp_ok"] += 1
            for t in p["teses"]:
                a = acc[t["lente"]]
                a["resp_n"] += 1
                if t["responsavel"] == g["responsavel"]:
                    a["resp_ok"] += 1
        # totais
        if gtot is not None:
            lo, hi = cons["faixa_total"]
            faixa["n"] += 1
            if lo - 0.01 <= gtot <= hi + 0.01:
                faixa["contem"] += 1
            for t in p["teses"]:
                a = acc[t["lente"]]
                tot = round(sum(float(t["valores"].get(k, 0)) for k in
                                ["principal", "multa", "outros"]), 2)
                a["tot_n"] += 1
                if _perto(tot, gtot):
                    a["tot_ok"] += 1
        # caminhos
        if cons["unanime"]:
            unanime["n"] += 1
            if gtot is not None:
                unanime["avaliavel"] += 1
                if _perto(cons["faixa_total"][0], gtot) and \
                   cons["responsavel_majoritario"] == g["responsavel"]:
                    unanime["certo"] += 1
        else:
            divergente["n"] += 1
            if gtot is not None:
                divergente["avaliavel"] += 1
                lo, hi = cons["faixa_total"]
                if lo - 0.01 <= gtot <= hi + 0.01:
                    divergente["faixa_contem"] += 1

    def pct(a, b):
        return f"{100*a/b:5.1f}%  ({a}/{b})" if b else "     -"

    n = len(paineis)
    print(f"\n{'='*66}\nAMOSTRA: {n} casos | modelo: {args.modelo}")
    print(f"tokens: {custo_in:,} in / {custo_out:,} out"
          f"   ({custo_in/max(n,1):.0f} / {custo_out/max(n,1):.0f} por caso)")
    print(f"\n{'-'*66}\nACERTO POR LENTE (contra o gabarito)")
    print(f"{'lente':18s} {'responsavel':>20s} {f'total (+/-{TOL:.0%})':>22s}")
    for l in lentes:
        a = acc[l]
        print(f"{l:18s} {pct(a['resp_ok'],a['resp_n']):>20s} {pct(a['tot_ok'],a['tot_n']):>22s}")
    print(f"{'MAIORIA (moda)':18s} {pct(maioria['resp_ok'],maioria['resp_n']):>20s} {'-':>22s}")
    print(f"\n{'-'*66}\nO MEDIADOR VERIA A RESPOSTA CERTA?")
    print(f"  faixa_total contem o gabarito : {pct(faixa['contem'], faixa['n'])}")
    print(f"\n{'-'*66}\nCAMINHOS")
    print(f"  unanime  (vira Termo automatico): {pct(unanime['n'], n)}")
    print(f"     desses, CERTOS              : {pct(unanime['certo'], unanime['avaliavel'])}")
    print(f"     >>> os errados viram Termo sem revisao humana <<<")
    print(f"  divergente (vira Pauta)         : {pct(divergente['n'], n)}")
    print(f"     desses, faixa contem gabarito: {pct(divergente['faixa_contem'], divergente['avaliavel'])}")
    print("=" * 66)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=".")
    ap.add_argument("--ic", default="ic.py")
    ap.add_argument("--estagios", type=int, default=1, choices=(1, 2),
                    help="2 = merito primeiro, valor depois")
    ap.add_argument("--out", default="resultados")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--desde", default="")
    ap.add_argument("--casos", default="",
                    help="lista explicita 0005,0018 ou @arquivo.txt")
    ap.add_argument("--workers", type=int, default=4)
    for m in ("auditar", "normalizar", "rodar", "relatorio"):
        ap.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    gabs = carregar_gabaritos(a.dataset)
    if a.auditar:      modo_auditar(a, gabs)
    elif a.normalizar: modo_normalizar(a, gabs)
    elif a.rodar:      modo_rodar(a, gabs)
    elif a.relatorio:  modo_relatorio(a, gabs)
    else:              ap.print_help()


if __name__ == "__main__":
    main()