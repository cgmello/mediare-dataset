# diag.py
import os, sys, json, traceback
from anthropic import Anthropic

MODELO = sys.argv[1] if len(sys.argv) > 1 else "claude-sonnet-5"
cli = Anthropic()

print(f"modelo: {MODELO}\n" + "="*60)
try:
    r = cli.messages.create(model=MODELO, max_tokens=100,
                            messages=[{"role": "user", "content": "Responda so: {\"ok\": true}"}])
    print("CHAMADA OK")
    print("  blocos :", [b.type for b in r.content])
    print("  texto  :", repr(r.content[0].text[:200]) if hasattr(r.content[0], "text") else "<primeiro bloco NAO e texto>")
    print("  tokens :", r.usage.input_tokens, "in /", r.usage.output_tokens, "out")
    print("  stop   :", r.stop_reason)
except Exception as e:
    print("FALHOU:", type(e).__name__)
    print(traceback.format_exc()[-1500:])