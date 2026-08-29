#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove identificadores pessoais de uma sentenca do TJSP antes de qualquer
chamada de API. sentencas.jsonl tem nomes reais e esta no .gitignore; a
extracao de valores nao precisa deles.

Estrategia: em vez de tentar adivinhar o que e nome, PEGA os nomes onde a
sentenca os declara (Requerente:/Requerido:/Juiz(a):, e os campos do JSON) e
substitui todas as ocorrencias - inclusive a versao em caixa alta e cada
sobrenome isolado. Depois passa um pente em CPF/CNPJ/RG/OAB, numero do
processo, CEP e enderecos.

  python3 redigir.py --amostra 3      # mostra antes/depois, sem chamar nada
"""
import argparse, json, re, sys, unicodedata

ROTULOS = [
    (r"Requerente", "[REQUERENTE]"), (r"Requerido\(?a?\)?", "[REQUERIDO]"),
    (r"Autor(?:a|es)?", "[REQUERENTE]"), (r"R[ée](?:u|s)?", "[REQUERIDO]"),
    (r"Exequente", "[REQUERENTE]"), (r"Executado\(?a?\)?", "[REQUERIDO]"),
    (r"Embargante", "[REQUERENTE]"), (r"Embargado\(?a?\)?", "[REQUERIDO]"),
]

# palavras que aparecem em caixa alta e NAO sao nome de parte
BOILERPLATE = {
    "SENTENCA", "SENTENÇA", "VISTOS", "RELATEI", "DECIDO", "JULGO", "ACAO",
    "AÇÃO", "PEDIDO", "TUTELA", "ANTECIPADA", "PROCESSO", "DIGITAL", "CLASSE",
    "ASSUNTO", "JUIZ", "DIREITO", "PROCEDENTE", "IMPROCEDENTE", "EXTINTO",
    "CPC", "CDC", "LTDA", "ME", "EPP", "SA", "S", "A", "DE", "DA", "DO",
    "DOS", "DAS", "E", "EM", "COM", "POR", "PARA", "FACE", "CONTRA",
    "DESPEJO", "COBRANCA", "COBRANÇA", "INDENIZACAO", "INDENIZAÇÃO",
    "RESCISAO", "RESCISÃO", "CONTRATUAL", "DANOS", "MORAIS", "MATERIAIS",
    "REVELIA", "HOMOLOGO", "CONDENO", "ANTE", "EXPOSTO", "ISSO", "POSTO",
}

RUIDO = [
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF]"),
    (re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"), "[CNPJ]"),
    (re.compile(r"\b\d{7}-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b"), "[PROCESSO]"),
    (re.compile(r"\bOAB[/\s]*[A-Z]{2}\s*n?[.º°]*\s*\d+\b", re.I), "[OAB]"),
    (re.compile(r"\b\d{5}-?\d{3}\b"), "[CEP]"),
    (re.compile(r"\b(?:Rua|Avenida|Av\.|Alameda|Travessa|Praca|Praça|Estrada|"
                r"Rodovia)\s+[^,;.\n]{3,60}", re.I), "[ENDERECO]"),
    (re.compile(r"\bn[.º°]?\s*\d+(?:/\d+)?\b"), "[NUM]"),
]

def _sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")

def nomes_declarados(texto, extra=()):
    """Nomes que a propria sentenca rotula, + os campos do JSON."""
    achados = []
    for rot, tag in ROTULOS:
        for m in re.finditer(rot + r"\s*:\s*([^\n]{3,120}?)(?=\s{2,}|\n|$|"
                             r"\s+(?:Juiz|Classe|Assunto|Requerid|Requerent))",
                             texto):
            achados.append((m.group(1).strip(" .:-"), tag))
    for e in extra:
        if e and len(e) > 4:
            achados.append((e.strip(), "[PESSOA]"))
    return achados

def _tokens_de(nome):
    """tokens do nome que valem substituir isoladamente (Ferro, Souza, Rosa)"""
    fora = {"de", "da", "do", "dos", "das", "e", "ltda", "me", "epp", "sa",
            "s", "a", "eireli", "cia", "filho", "junior", "neto"}
    for t in re.split(r"[\s,./-]+", nome):
        if len(t) >= 4 and _sem_acento(t).lower() not in fora:
            yield t

def redigir(texto, extra=()):
    """-> (texto_redigido, quantos_nomes_encontrados)"""
    achados = nomes_declarados(texto, extra)
    for nome, tag in sorted(achados, key=lambda x: -len(x[0])):
        if len(nome) < 4:
            continue
        texto = re.sub(re.escape(nome), tag, texto, flags=re.I)
        for tok in _tokens_de(nome):
            texto = re.sub(r"\b" + re.escape(tok) + r"\b", tag, texto,
                           flags=re.I)
    # sobras em caixa alta: 2+ palavras maiusculas seguidas que nao sao jargao
    def caps(m):
        bloco = m.group()
        pals = [p for p in re.split(r"\s+", bloco) if p]
        if all(_sem_acento(p).upper() in BOILERPLATE for p in pals):
            return bloco
        if len(pals) < 2:
            return bloco
        return "[NOME]"
    texto = re.sub(r"\b[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}){1,6}\b",
                   caps, texto)
    for pat, tag in RUIDO:
        texto = pat.sub(tag, texto)
    return texto, len(achados)

def texto_da(s):
    return ((s.get("data") or "") + "\n" + (s.get("texto") or "")).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--amostra", type=int, default=2)
    ap.add_argument("--chars", type=int, default=1200)
    ap.add_argument("--fonte", default="sentencas.jsonl")
    a = ap.parse_args()
    n = 0
    for l in open(a.fonte, encoding="utf-8"):
        if n >= a.amostra:
            break
        s = json.loads(l)
        t = texto_da(s)
        r, k = redigir(t, extra=[s.get("magistrado")])
        n += 1
        print("=" * 78)
        print(f"processo {s.get('processo')}  |  {k} nome(s) declarado(s) achado(s)")
        print("-" * 78)
        print(r[:a.chars])
        print()

if __name__ == "__main__":
    main()
