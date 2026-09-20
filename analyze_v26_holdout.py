#!/usr/bin/env python3
"""Gera a auditoria qualitativa pareada da v26 sobre os 50 holdouts do Studio."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "res_openrouter_v26_studio_holdout50" / "results"
STUDIO_LOG = ROOT / "res_studio_v26_random50" / "chain.jsonl"
OUTPUT = ROOT / "V26_HOLDOUT_QUALITATIVE_ANALYSIS.md"


# A classificação é deliberadamente explícita e versionável. Ela resulta da
# leitura do pedido/resposta de cada caso e do painel/revisões persistidos pelo
# runner; não é uma nova decisão de LLM.
ADJUDICATION = {
    "0026": ("adequado", "Catálogo coerente com rescisão, desocupação e aluguéis vencidos/vincendos."),
    "0028": ("defeito_material", "Omitiu a alternativa expressa de rescisão amigável com desocupação; condições de pagamento são dependentes e não exigem RP próprio."),
    "0036": ("variacao_revisor", "O valor de R$ 13.000,00 é pedido literal; juros são acessórios do mesmo crédito. A inconsistência com o pagamento anterior pertence ao mérito, não ao catálogo."),
    "0053": ("adequado", "Pedido único de ressarcimento material, com valor literal e sem duplicação."),
    "0060": ("adequado", "Danos emergentes, lucros cessantes e danos morais foram separados como resultados autônomos."),
    "0068": ("adequado", "Danos materiais e morais foram separados com valores literais."),
    "0071": ("adequado", "Pedido único de danos morais, fiel ao texto-fonte."),
    "0084": ("adequado", "Parcela contratual e serviços adicionais são créditos autônomos e literais."),
    "0086": ("adequado", "Quatro resultados materiais distintos foram preservados sem cálculo novo."),
    "0101": ("adequado", "Danos materiais, morais e obrigação de cessar risco são resultados autônomos; objeção minoritária não demonstrou duplicação."),
    "0105": ("adequado", "Obrigações de fazer, dano moral e contrapedido afirmativo foram corretamente separados."),
    "0110": ("adequado", "Catálogo amplo, mas cada providência possui objeto negociável próprio."),
    "0119": ("falha_tecnica", "A auditora repetiu risco fora do enum em três tentativas; o mérito do painel não chegou ao gate local."),
    "0122": ("adequado", "Reparação, despesa técnica e dano moral foram preservados sem remédio processual."),
    "0124": ("defeito_material", "O líder omitiu o pedido expresso de restituição de valores cobrados indevidamente; quatro revisores convergiram na omissão."),
    "0131": ("adequado", "As multas descritas formam uma cobrança agregada coerente com o pedido literal."),
    "0136": ("defeito_material", "CR01 apenas limita defensivamente a responsabilidade pelo RP; não é contrapedido afirmativo autônomo."),
    "0154": ("adequado", "Rescisão, restituição e dano moral são resultados autônomos e expressos."),
    "0160": ("adequado", "O catálogo preservou os resultados principal e subsidiário sem fundi-los."),
    "0169": ("adequado", "O próprio pedido agrega dano material e lucros cessantes em R$ 20.000,00; separá-los seria rigor excessivo."),
    "0178": ("adequado", "Restituição principal, restituição subsidiária e dano moral estão corretamente separados."),
    "0184": ("adequado", "Parcelas e multa contratual são resultados monetários expressos e autônomos."),
    "0193": ("adequado", "Pedido único de reparação material, com valor literal."),
    "0197": ("adequado", "Ressarcimento e drenagem são providências autônomas de pagar e fazer."),
    "0203": ("adequado", "Pedido único de reparos, fiel ao texto-fonte."),
    "0240": ("defeito_material", "CR01 é pedido dependente de parcelamento do próprio débito; deve ser condição de negociação do RP, não contrapedido."),
    "0280": ("adequado", "Reparo e lucros cessantes são resultados autônomos com valores literais."),
    "0281": ("adequado", "Pedido único de reparação material, fiel ao texto-fonte."),
    "0286": ("falha_tecnica", "A auditora apontou conflito de dupla contagem com ID inválido e não convergiu após três correções."),
    "0311": ("adequado", "Pedido único de reparação do veículo com base literal."),
    "0313": ("defeito_material", "Calculou R$ 8.200,00 por subtração e criou conclusão da obra sem pedido expresso suficiente."),
    "0317": ("adequado", "Pedido único de reparação material, com valor literal."),
    "0336": ("adequado", "Pedido único de reparação material, com valor literal."),
    "0345": ("adequado", "Cotas, multa e juros pertencem à mesma cobrança; a objeção de separação foi rigor excessivo."),
    "0347": ("defeito_material", "CR01 apenas afirma a legitimidade defensiva da retenção e não pede providência autônoma contra o requerente."),
    "0354": ("defeito_material", "Duplicou o mesmo dano material em reparos e ressarcimento, embora o texto descreva uma única recomposição."),
    "0359": ("adequado", "Pedido único de reparos, fiel ao texto-fonte."),
    "0368": ("defeito_material", "Inventou devolução do preço do veículo; o texto só quantifica o reparo do motor."),
    "0375": ("adequado", "Ressarcimento e drenagem são providências autônomas."),
    "0380": ("defeito_material", "CR01 é mera defesa da retenção; devolução e multa do requerente permanecem autônomas."),
    "0390": ("adequado", "A providência de conserto é diretamente identificável e não recebeu valor inventado."),
    "0424": ("adequado", "Pedido único de ressarcimento, com valor literal."),
    "0434": ("defeito_material", "CR01 é mera justificativa defensiva da retenção, não contrapedido; o desconto integra a negociação do RP."),
    "0459": ("adequado", "O total não foi calculado; aluguéis e compensação com caução permaneceram em um único resultado."),
    "0468": ("defeito_material", "Calculou R$ 25.000,00 por subtração e acrescentou conclusão da obra sem pedido expresso suficiente."),
    "0472": ("falha_tecnica", "O líder devolveu catálogo vazio três vezes; o schema v26 exige ao menos um pedido e não tratou a cessação implicitamente pedida."),
    "0479": ("defeito_material", "Calculou R$ 13.600,00 e separou a compensação com caução, que é condição do mesmo débito."),
    "0488": ("defeito_material", "Calculou R$ 9.300,00; a fonte informa 3 × R$ 3.100,00, portanto o valor final deve permanecer nulo."),
    "0491": ("adequado", "Parcelas e multa contratual foram preservadas como resultados expressos."),
    "0495": ("adequado", "Pedido único de ressarcimento, com valor literal."),
}

LABELS = {
    "adequado": "Adequado",
    "variacao_revisor": "Variação do revisor",
    "defeito_material": "Defeito material",
    "falha_tecnica": "Falha técnica",
}


def load_results() -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in RESULTS.glob("*.json")}


def load_studio() -> dict[str, dict]:
    rows = [json.loads(line) for line in STUDIO_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {row["id"]: row for row in rows}


def main() -> None:
    results = load_results()
    studio = load_studio()
    expected = set(ADJUDICATION)
    if set(results) != expected or set(studio) != expected:
        raise SystemExit("Os 50 casos adjudicados não coincidem com os resultados OpenRouter/Studio.")

    counts = Counter(kind for kind, _ in ADJUDICATION.values())
    def local_status(result: dict) -> str:
        value = result.get("local_consensus", "")
        return value.get("status", "") if isinstance(value, dict) else str(value)

    local_agree = sum(local_status(r) == "LOCAL_MAJORITY_AGREE" for r in results.values())
    studio_agree = sum(r.get("status") == "ACCEPTED" and r.get("result_name") == "MAJORITY_AGREE" for r in studio.values())
    technical = sorted(cid for cid, (kind, _) in ADJUDICATION.items() if kind == "falha_tecnica")
    material = sorted(cid for cid, (kind, _) in ADJUDICATION.items() if kind == "defeito_material")

    lines = [
        "# Auditoria qualitativa pareada — v26 · 50 casos",
        "",
        "## Resultado executivo",
        "",
        f"A campanha foi concluída em **50/50 casos**. No Studio, **{studio_agree}/50** chegaram a `ACCEPTED / MAJORITY_AGREE`; no OpenRouter, **{local_agree}/50** obtiveram maioria local. A diferença não é contradição: o Studio mede consenso real do protocolo, enquanto o runner local preserva objeções individuais e permite inspecionar o conteúdo.",
        "",
        f"A leitura humana do texto-fonte, catálogo do líder e objeções dos revisores classificou **{counts['adequado']} casos sem defeito material**, **{counts['variacao_revisor']} caso de variação/excesso do revisor**, **{counts['defeito_material']} casos com defeito material** e **{counts['falha_tecnica']} falhas técnicas**.",
        "",
        "> Conclusão: a v26 é tecnicamente forte no Studio, mas a inspeção local revela padrões suficientemente repetidos para justificar uma v27 conservadora. Consenso de protocolo não deve ser confundido com perfeição semântica do painel.",
        "",
        "## Padrões que justificam a v27",
        "",
        "1. **CR meramente defensivo** — casos 0136, 0240, 0347, 0380 e 0434 transformaram limitação, parcelamento ou legitimidade da retenção em contrapedido autônomo.",
        "2. **Valor aritmético não literal** — casos 0313, 0468, 0479 e 0488 calcularam subtrações ou multiplicações que deveriam permanecer como fórmula com valor nulo.",
        "3. **Granularidade/omissão** — houve omissão material em 0028 e 0124, duplicação em 0354 e remédio inventado em 0368.",
        "4. **Estabilidade mecânica** — 0119 e 0286 falharam por enum/ID da auditoria; 0472 não conseguiu representar um pedido não monetário diretamente implícito no bloco intitulado ‘Fatos e pedidos’.",
        "",
        "## Limites da correção",
        "",
        "A v27 não deve relaxar o quórum local nem ensinar respostas específicas dos casos. As correções seguras são: validar deterministicamente que valores do catálogo aparecem literalmente na fonte; ampliar apenas marcadores inequívocos de defesa/condição dependente; normalizar riscos e IDs inválidos da auditoria em modo fail-closed; e esclarecer a regra de pedidos não monetários diretamente implícitos, sem inventar indenização, valor ou obrigação adicional.",
        "",
        "## Análise caso a caso",
        "",
        "| Caso | Studio | OpenRouter | Adjudicação | Observação |",
        "|---:|---|---|---|---|",
    ]
    for cid in sorted(expected):
        result = results[cid]
        local = local_status(result) or "—"
        srow = studio[cid]
        stext = f"{srow['result_name']} · {srow['rounds']} rodada(s)"
        kind, note = ADJUDICATION[cid]
        lines.append(f"| {cid} | {stext} | `{local}` | **{LABELS[kind]}** | {note} |")

    lines.extend([
        "",
        "## Casos prioritários para regressão",
        "",
        "- Defeitos materiais: " + ", ".join(material) + ".",
        "- Falhas técnicas: " + ", ".join(technical) + ".",
        "- Controle contra excesso do revisor: 0036.",
        "- Controles positivos sem alteração esperada: 0060, 0105, 0178, 0197 e 0459.",
        "",
        "## Critério de promoção sugerido",
        "",
        "A v27 só deve ir ao Studio depois de: (a) eliminar as três falhas técnicas; (b) corrigir os padrões determinísticos de CR defensivo e valor inferido; (c) não piorar os controles positivos; e (d) repetir estes 50 casos no OpenRouter para comparação pareada. Somente então faz sentido sortear 100 novos casos para o Studio.",
        "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "counts": counts,
        "studio_majority_agree": studio_agree,
        "local_majority_agree": local_agree,
    }, ensure_ascii=False, default=dict, indent=2))


if __name__ == "__main__":
    main()
