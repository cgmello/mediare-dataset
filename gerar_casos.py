#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transforma sentenças coletadas (sentencas.jsonl) em casos de teste da Mediare.
Com RETOMADA: detecta casos já gerados e continua de onde parou.
Uso normal:      python gerar_casos.py --limite 200
Retomar de erro: python gerar_casos.py --limite 200 --pular-ate 1002460-98.2025.8.26.0637
"""
import argparse, json, os, re, sys
from anthropic import Anthropic

MODELO = "claude-sonnet-4-5"   # ajuste para o modelo disponível na sua conta
RE_PROC = r"(\d{7}-\d{2}\.\d{4}\.8\.26\.\d{4})"

PROMPT = """Você monta casos de teste para uma plataforma de mediação extrajudicial.
A partir da SENTENÇA abaixo (pública, do TJSP), produza um JSON com este schema exato:

{
 "aproveitavel": true/false,          // false se relatório pobre, segredo de justiça, réu revel sem defesa, ou parte for banco/INSS/Fazenda
 "peticao_requerente_md": "...",      // pedido de mediação da parte autora, reconstruído SÓ com fatos do relatório, nomes PSEUDONIMIZADOS (iniciais)
 "documentos_requerente_md": "...",   // lista plausível de documentos comprobatórios coerente com o relatório
 "resposta_requerido_md": "...",      // versão da parte ré conforme a contestação relatada (incluir pedido contraposto se houver)
 "documentos_requerido_md": "...",
 "gabarito": {
   "responsavel": "...",              // requerente | requerido | ambos_culpa_concorrente | parcial_ambos
   "resultado": "...",                // procedente | improcedente | parcialmente procedente
   "valores": { ... },                // cada rubrica decidida, em números (0.0 quando negada)
   "obrigacoes_de_fazer": { ... },    // se houver
   "pedidos_rejeitados": [ ... ],
   "fundamentos": [ ... ]             // 3 a 6 fundamentos objetivos da decisão
 },
 "criterios_equivalencia": {          // como comparar respostas de IAs neste caso
   "responsavel": "match exato",
   "valores": "tolerância ±15% por rubrica; rubricas negadas devem ser 0",
   "fundamentos": "mínimo 2 fundamentos centrais em comum"
 }
}

Regras: use APENAS fatos presentes na sentença; NUNCA copie nomes reais (pseudonimize);
escreva as peças em 1ª pessoa, tom leigo-formal; responda SÓ o JSON.

SENTENÇA (<<PROCESSO>> — <<CLASSE>> / <<ASSUNTO>>):
<<TEXTO>>
"""

def ja_gerados(saida_dir):
    """Retorna (processos já gerados, maior número de caso existente)."""
    feitos, maxn = set(), 0
    if os.path.isdir(saida_dir):
        for nome in os.listdir(saida_dir):
            m = re.match(r"caso_real_(\d+)$", nome)
            g = os.path.join(saida_dir, nome, "gabarito.json")
            if m and os.path.exists(g):
                maxn = max(maxn, int(m.group(1)))
                try:
                    mm = re.search(RE_PROC, json.load(open(g)).get("fonte", ""))
                    if mm:
                        feitos.add(mm.group(1))
                except Exception:
                    pass
    return feitos, maxn

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default="sentencas.jsonl")
    ap.add_argument("--limite", type=int, default=200, help="total de casos desejado (contando os já existentes)")
    ap.add_argument("--saida-dir", default="casos_reais")
    ap.add_argument("--pular-ate", default=None, help="pula linhas até DEPOIS deste nº de processo (inclusive)")
    args = ap.parse_args()

    cli = Anthropic()
    os.makedirs(args.saida_dir, exist_ok=True)

    feitos, n_ok = ja_gerados(args.saida_dir)
    log_path = os.path.join(args.saida_dir, "processados.txt")
    if os.path.exists(log_path):
        feitos |= {l.strip().split()[0] for l in open(log_path) if l.strip()}
    log = open(log_path, "a")

    print(f"Retomando: {n_ok} casos já existem; {len(feitos)} processos serão pulados.")
    pulando = args.pular_ate is not None
    n_skip = 0

    with open(args.entrada, encoding="utf-8") as f:
        for linha in f:
            if n_ok >= args.limite:
                break
            s = json.loads(linha)
            if pulando:
                if s["processo"] == args.pular_ate:
                    pulando = False
                continue
            if s["processo"] in feitos:
                continue
            prompt = (PROMPT.replace("<<PROCESSO>>", s["processo"])
                             .replace("<<CLASSE>>", s.get("classe", ""))
                             .replace("<<ASSUNTO>>", s.get("assunto", ""))
                             .replace("<<TEXTO>>", s["texto"][:12000]))
            try:
                r = cli.messages.create(model=MODELO, max_tokens=4000,
                                        messages=[{"role": "user", "content": prompt}])
                bruto = r.content[0].text
                m = re.search(r"\{.*\}", bruto, re.S)
                caso = json.loads(m.group(0))
            except Exception as e:
                print(f"  [{s['processo']}] erro: {e}", file=sys.stderr)
                continue  # erro NÃO entra no log -> será tentado de novo na próxima rodada
            if not caso.get("aproveitavel"):
                n_skip += 1
                log.write(f"{s['processo']} skip\n"); log.flush()
                continue
            n_ok += 1
            log.write(f"{s['processo']} ok\n"); log.flush()
            d = os.path.join(args.saida_dir, f"caso_real_{n_ok:03d}")
            os.makedirs(d, exist_ok=True)
            open(f"{d}/README.md", "w").write(
                f"# Caso real {n_ok:03d} — {s.get('categoria','')}\n\n"
                f"Fonte: CJPG/TJSP — proc. {s['processo']} — {s.get('vara','')}, "
                f"{s.get('comarca','')} — {s.get('data','')}\n"
                f"Peças reconstruídas do Relatório da sentença; nomes pseudonimizados (LGPD).\n")
            open(f"{d}/01_peticao_requerente.md", "w").write(caso["peticao_requerente_md"])
            open(f"{d}/02_documentos_requerente.md", "w").write(caso["documentos_requerente_md"])
            open(f"{d}/03_resposta_requerido.md", "w").write(caso["resposta_requerido_md"])
            open(f"{d}/04_documentos_requerido.md", "w").write(caso["documentos_requerido_md"])
            json.dump({"caso": f"real-{n_ok:03d}-{s.get('categoria','')}",
                       "fonte": f"Sentenca TJSP - CJPG - proc. {s['processo']}",
                       "parecer_esperado": caso["gabarito"],
                       "criterios_equivalencia_sugeridos": caso["criterios_equivalencia"]},
                      open(f"{d}/gabarito.json", "w"), ensure_ascii=False, indent=2)
            print(f"[{n_ok}] {s['processo']} ({s.get('categoria','')})")
    print(f"Concluído: {n_ok} casos no total, {n_skip} sentenças descartadas nesta rodada.")

if __name__ == "__main__":
    main()