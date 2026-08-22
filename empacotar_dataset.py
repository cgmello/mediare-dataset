#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empacota os casos (ouro, reais e sintéticos) em JSONs canônicos para o
repositório público mediare-dataset.

Estrutura gerada:
  mediare-dataset/
    casos/0001.json ...      <- SÓ os documentos de entrada (o que o contrato lê)
    gabaritos/0001.json ...  <- gabarito separado (avaliação)
    manifest.json            <- índice com id, categoria, origem e sha256 de cada caso
    README.md

Uso: coloque este script na pasta que contém casos_ouro/, casos_sinteticos/ e
     casos_reais/, e rode:  python3 empacotar_dataset.py
"""
import glob, hashlib, json, os, re

SAIDA = "mediare-dataset"

def ler(pasta, prefixo):
    """Lê o arquivo 0N_*.md da pasta (tolera variações de nome)."""
    achados = sorted(glob.glob(os.path.join(pasta, prefixo + "*.md")))
    return open(achados[0], encoding="utf-8").read().strip() if achados else ""

def coletar():
    fontes = []
    # ouro (curados) — na raiz ou dentro de casos_ouro/
    for p in sorted(glob.glob("caso_0*")) + sorted(glob.glob("casos_ouro/caso_0*")):
        if os.path.isdir(p) and os.path.exists(f"{p}/gabarito.json"):
            fontes.append((p, "ouro"))
    # reais (pipeline CJPG)
    for p in sorted(glob.glob("casos_reais/caso_real_*")):
        if os.path.exists(f"{p}/gabarito.json"):
            fontes.append((p, "real"))
    # sintéticos
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
        print("Nenhuma pasta de caso encontrada. Rode na pasta que contém casos_reais/ etc.")
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
                          "estruturado: parte responsável, resultado, valores por rubrica "
                          "(0.0 quando negada), obrigações de fazer (se houver) e 3 a 6 "
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
        # nº do processo TJSP (casos reais e ouro; None para sintéticos)
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

Benchmark de casos de mediação extrajudicial para avaliação de comitês de IA.
Total: **{len(manifest)} casos** ({cnt.get('ouro',0)} ouro · {cnt.get('real',0)} derivados
de sentenças públicas do TJSP · {cnt.get('sintetico',0)} sintéticos).

- `casos/NNNN.json` — documentos de entrada das duas partes (o que o modelo/contrato lê)
- `gabaritos/NNNN.json` — desfecho esperado + critérios de equivalência (avaliação)
- `manifest.json` — índice com categoria, origem e SHA-256 de cada caso

## Uso com Intelligent Contracts (GenLayer)

Passe ao contrato a URL **fixada em um commit** (imutável — nunca use `main`):