#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empacota os casos (ouro, reais e sinteticos) em JSONs canonicos, gravando
NA RAIZ da pasta atual (que e o repositorio mediare-dataset):

  casos/0001.json ...      <- SO os documentos de entrada (o que o contrato le)
  gabaritos/0001.json ...  <- gabarito separado (avaliacao)
  manifest.json            <- indice com id, categoria, origem e sha256 de cada caso
  README.md                <- em ingles
  .gitignore               <- impede publicar as fontes brutas e o sentencas.jsonl

Uso: rode na pasta que contem casos_ouro/, casos_sinteticos/ e casos_reais/:
     python3 empacotar_dataset.py
"""
import glob, hashlib, json, os, re

SAIDA = "."

def ler(pasta, prefixo):
    """Le o arquivo 0N_*.md da pasta (tolera variacoes de nome)."""
    achados = sorted(glob.glob(os.path.join(pasta, prefixo + "*.md")))
    return open(achados[0], encoding="utf-8").read().strip() if achados else ""

def coletar():
    fontes = []
    # ouro (curados) - na raiz ou dentro de casos_ouro/
    for p in sorted(glob.glob("caso_0*")) + sorted(glob.glob("casos_ouro/caso_0*")):
        if os.path.isdir(p) and os.path.exists(f"{p}/gabarito.json"):
            fontes.append((p, "ouro"))
    # reais (pipeline CJPG)
    for p in sorted(glob.glob("casos_reais/caso_real_*")):
        if os.path.exists(f"{p}/gabarito.json"):
            fontes.append((p, "real"))
    # sinteticos
    for p in sorted(glob.glob("casos_sinteticos/caso_sint_*")):
        if os.path.exists(f"{p}/gabarito.json"):
            fontes.append((p, "sintetico"))
    return fontes

def main():
    os.makedirs(f"{SAIDA}/casos", exist_ok=True)
    os.makedirs(f"{SAIDA}/gabaritos", exist_ok=True)
    manifest = []
    fontes = coletar()
    if not fontes:
        print("Nenhuma pasta de caso encontrada. Rode na pasta que contem casos_reais/ etc.")
        return
    for i, (pasta, origem) in enumerate(fontes, start=1):
        cid = f"{i:04d}"
        gab = json.load(open(f"{pasta}/gabarito.json", encoding="utf-8"))
        categoria = re.sub(r"^(sint|real|ouro)-?\d*-?", "", gab.get("caso", "")) or origem
        caso = {
            "id": cid,
            "origem": origem,
            "categoria": categoria,
            "instrucao": ("Analise os documentos das duas partes e produza um parecer "
                          "estruturado: parte responsavel, resultado, valores por rubrica "
                          "(0.0 quando negada), obrigacoes de fazer (se houver) e 3 a 6 "
                          "fundamentos objetivos."),
            "documentos": {
                "peticao_requerente":     ler(pasta, "01_"),
                "documentos_requerente":  ler(pasta, "02_"),
                "resposta_requerido":     ler(pasta, "03_"),
                "documentos_requerido":   ler(pasta, "04_"),
            },
        }
        blob = json.dumps(caso, ensure_ascii=False, indent=2, sort_keys=True)
        open(f"{SAIDA}/casos/{cid}.json", "w", encoding="utf-8").write(blob + "\n")
        sha = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        # numero do processo TJSP (casos reais e ouro; None para sinteticos)
        mproc = re.search(r"(\d{7}-\d{2}\.\d{4}\.8\.26\.\d{4})", gab.get("fonte", ""))
        processo = mproc.group(1) if mproc else None
        gab_out = {"id": cid, "origem": origem, "processo_tjsp": processo,
                   "sha256_caso": sha, **gab}
        json.dump(gab_out, open(f"{SAIDA}/gabaritos/{cid}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        manifest.append({"id": cid, "origem": origem, "categoria": categoria,
                         "processo_tjsp": processo, "sha256": sha,
                         "url_relativa": f"casos/{cid}.json"})
    json.dump({"dataset": "mediare-dataset", "versao": "1.0.0",
               "total": len(manifest), "casos": manifest},
              open(f"{SAIDA}/manifest.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    from collections import Counter
    cnt = Counter(m["origem"] for m in manifest)
    open(f"{SAIDA}/README.md", "w", encoding="utf-8").write(f"""# Mediare Dataset

Benchmark of Brazilian extrajudicial mediation cases for evaluating AI committees.
Total: **{len(manifest)} cases** ({cnt.get('ouro',0)} gold, {cnt.get('real',0)} derived
from public court decisions (TJSP/Brazil), {cnt.get('sintetico',0)} synthetic).

- `casos/NNNN.json` - input documents from both parties (what the model/contract reads)
- `gabaritos/NNNN.json` - expected outcome + equivalence criteria (evaluation ground truth)
- `manifest.json` - index with category, origin, TJSP case number and SHA-256 of each case

All content is in Brazilian Portuguese, the language of the underlying disputes.

## Usage with Intelligent Contracts (GenLayer)

Pass the contract a URL pinned to a commit (immutable - never use `main`):

    https://raw.githubusercontent.com/cgmello/mediare-dataset/<COMMIT_SHA>/casos/0001.json

Verify integrity by comparing the content's SHA-256 against `manifest.json`.

## Notes

- "real" cases were reconstructed from public court decisions (CJPG/TJSP), with
  party names pseudonymized (LGPD compliance). "sintetico" cases contain no real data.
- Gold cases were manually curated; real cases were generated via LLM and should be
  sample-reviewed before use as evaluation ground truth.
- For honest evaluation of web-browsing models, consider keeping `gabaritos/`
  in a private repository during test runs.
""")
    open(".gitignore", "w", encoding="utf-8").write(
        "# fontes brutas - nao publicar\n"
        "casos_ouro/\n"
        "casos_reais/\n"
        "casos_sinteticos/\n"
        "sentencas.jsonl\n"
        ".venv/\n"
        ".DS_Store\n"
        "__pycache__/\n"
    )
    print(f"OK: {len(manifest)} casos empacotados em ./{SAIDA}/  ({dict(cnt)})")

if __name__ == "__main__":
    main()