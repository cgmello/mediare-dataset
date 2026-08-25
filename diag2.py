# diag2.py - roda UMA chamada de lente real e mostra tudo
import sys, json, traceback
from anthropic import Anthropic
import harness

MODELO = sys.argv[1] if len(sys.argv) > 1 else "claude-sonnet-5"
CASO   = sys.argv[2] if len(sys.argv) > 2 else "0001"
MAXTOK = int(sys.argv[3]) if len(sys.argv) > 3 else 4000

REGRAS, LENTES, SCHEMA, _ = harness.carregar_contrato("ic.py")
caso  = json.load(open(f"casos/{CASO}.json", encoding="utf-8"))
corpo = json.dumps(caso["documentos"], sort_keys=True, ensure_ascii=False)
nome, lente = LENTES[0]

p = ("Voce e um mediador extrajudicial brasileiro (Lei 13.140/2015).\n"
     + lente + "\n\n" + REGRAS
     + "\nResponda SOMENTE com este JSON, sem markdown:\n" + SCHEMA
     + "\n\nDOCUMENTOS DO CASO:\n" + corpo)

print(f"modelo={MODELO}  caso={CASO}  lente={nome}  max_tokens={MAXTOK}")
print(f"prompt: {len(p)} chars\n" + "=" * 66)
try:
    r = Anthropic().messages.create(model=MODELO, max_tokens=MAXTOK,
                                    messages=[{"role": "user", "content": p}])

    blocos = [getattr(b, "type", "?") for b in r.content]
    txt = "".join(b.text for b in r.content if getattr(b, "type", None) == "text")

    print(f"blocos      : {blocos}")
    print(f"stop_reason : {r.stop_reason}      <<< 'max_tokens' = truncou")
    print(f"tokens      : {r.usage.input_tokens} in / {r.usage.output_tokens} out")
    print(f"texto util  : {len(txt)} chars (~{len(txt)//4} tokens)")
    if "thinking" in blocos:
        pens = sum(len(getattr(b, "thinking", "")) for b in r.content
                   if getattr(b, "type", None) == "thinking")
        print(f"raciocinio  : ~{pens//4} tokens  <<< entra na conta de SAIDA")
    print("-" * 66)
    if not txt:
        print(">>> NENHUM bloco de texto na resposta <<<")
    else:
        print(txt[:600])
        if len(txt) > 900:
            print("\n   [...]\n")
            print(txt[-300:])
    print("-" * 66)
    try:
        o = harness.extrair_json(txt)
        print("PARSE OK ->", json.dumps(
            {k: o.get(k) for k in ("responsavel", "resultado", "valores")},
            ensure_ascii=False))
    except Exception as e:
        print("PARSE FALHOU:", type(e).__name__, e)

    ent, sai = r.usage.input_tokens, r.usage.output_tokens
    print("\n" + "=" * 66)
    print("CUSTO PROJETADO (3 lentes por caso)")
    for nm, pin, pout in [("Sonnet 5", 2, 10), ("Haiku 4.5", 1, 5)]:
        c = lambda n: n * 3 * (ent * pin + sai * pout) / 1e6
        print(f"  {nm:10s}  50 casos: US$ {c(50):6.2f}   |   500 casos: US$ {c(500):7.2f}")
    print("=" * 66)
except Exception as e:
    print("CHAMADA FALHOU:", type(e).__name__)
    print(traceback.format_exc()[-1500:])