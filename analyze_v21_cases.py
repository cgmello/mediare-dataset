#!/usr/bin/env python3
"""Compara, caso a caso, a v20 com cada candidata v21 do OpenRouter."""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
from html import escape
import json
from pathlib import Path


BASELINE = ("v20", "res_openrouter_v20_0001_0050")
CANDIDATES = (
    ("v21-schema", "res_openrouter_v21_schema_0001_0050"),
    ("v21-catalog", "res_openrouter_v21_catalog_0001_0050"),
    ("v21-options", "res_openrouter_v21_options_0001_0050"),
)
USEFUL_LABELS = {"APTO_INTEGRAL", "APTO_PARCIAL_COM_RETENCOES"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def result_paths(folder: Path) -> list[Path]:
    return [folder / "results" / f"{case_id:04d}.json" for case_id in range(1, 51)]


def reviewer_counts(row: dict) -> tuple[int, int]:
    invalid = 0
    substantive = 0
    for review in row.get("reviewers") or []:
        if review.get("vote") == "agree":
            continue
        diagnostic = str(review.get("diagnostic") or "")
        if diagnostic.startswith("LLM_INVALID_PANEL"):
            invalid += 1
        elif diagnostic.startswith("REVISOR_"):
            substantive += 1
    return invalid, substantive


def studio_match(row: dict) -> bool | None:
    baseline = row.get("studio_baseline") or {}
    if not baseline.get("consensus"):
        return None
    return (row.get("local_consensus") == "LOCAL_MAJORITY_AGREE") == (
        baseline.get("consensus") == "MAJORITY_AGREE"
    )


def error_origin(value: object) -> str | None:
    if not value:
        return None
    text = str(value)
    stage = "painel"
    if "lente=" in text:
        stage = text.split("lente=", 1)[1].split(":", 1)[0]
    transient = any(token in text for token in (
        "CHAMADA_RunnerError", "JSON_INVALIDO", "OPENROUTER_",
    ))
    rule = any(token in text for token in (
        ".auditoria:", "COERENCIA_", "valor_centavos:", "RISCOS_INVALIDOS",
    ))
    kind = "mista" if transient and rule else "geração/API" if transient else "regra local"
    return f"{stage}/{kind}"


def panel_details(row: dict) -> dict:
    impression = row.get("leader_impression") or {}
    invalid_reviews, substantive_reviews = reviewer_counts(row)
    label = impression.get("label")
    panel = row.get("leader_panel") or {}
    requests = (panel.get("consolidado") or {}).get("pedidos") or []
    option_types = Counter()
    status_counts = Counter()
    declaratory_options = 0
    declaratory_neutral_parties = 0
    documentary_bases = 0
    for request in requests:
        status_counts[str(request.get("status") or "sem_status")] += 1
        option = (request.get("negociacao") or {}).get("opcao") or {}
        option_type = str(option.get("tipo") or "sem_tipo")
        option_types[option_type] += 1
        if request.get("modalidade") == "declarar" and option_type == "nao_monetaria":
            declaratory_options += 1
            if option.get("pagador") is None and option.get("beneficiario") is None:
                declaratory_neutral_parties += 1
        base = option.get("base") or {}
        if base.get("fonte") in {"DR", "DD"}:
            documentary_bases += 1
    return {
        "valid": row.get("leader_error") is None,
        "leader_error": row.get("leader_error"),
        "error_origin": error_origin(row.get("leader_error")),
        "label": label,
        "useful": label in USEFUL_LABELS,
        "local_majority_agree": row.get("local_consensus") == "LOCAL_MAJORITY_AGREE",
        "studio_match": studio_match(row),
        "reviewer_agree": int(row.get("reviewer_agree") or 0),
        "reviewer_total": int(row.get("reviewer_total") or 0),
        "reviewer_invalid": invalid_reviews,
        "reviewer_substantive": substantive_reviews,
        "requests": len(requests),
        "option_types": dict(sorted(option_types.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "declaratory_options": declaratory_options,
        "declaratory_neutral_parties": declaratory_neutral_parties,
        "documentary_bases": documentary_bases,
        "case_api_calls": int(row.get("case_api_calls") or 0),
        "total_tokens": int(row.get("total_tokens") or 0),
        "case_cost_usd": str(row.get("case_cost_usd") or "0"),
    }


def transition(base: dict, candidate: dict) -> dict:
    positive = []
    negative = []
    factual = []

    def binary(
        gain: str,
        loss: str,
        left: bool | None,
        right: bool | None,
    ) -> None:
        if left is right:
            return
        if right is True:
            positive.append(gain)
        elif left is True:
            negative.append(loss)

    binary("painel válido recuperado", "painel válido perdido", base["valid"], candidate["valid"])
    binary("saída útil recuperada", "saída útil perdida", base["useful"], candidate["useful"])
    binary(
        "maioria local conquistada",
        "maioria local perdida",
        base["local_majority_agree"],
        candidate["local_majority_agree"],
    )
    binary(
        "alinhamento com Studio conquistado",
        "alinhamento com Studio perdido",
        base["studio_match"],
        candidate["studio_match"],
    )
    if candidate["reviewer_invalid"] < base["reviewer_invalid"]:
        positive.append(
            f"erros de formato do revisor {base['reviewer_invalid']}→{candidate['reviewer_invalid']}"
        )
    elif candidate["reviewer_invalid"] > base["reviewer_invalid"]:
        negative.append(
            f"erros de formato do revisor {base['reviewer_invalid']}→{candidate['reviewer_invalid']}"
        )
    if candidate["requests"] != base["requests"]:
        factual.append(f"pedidos {base['requests']}→{candidate['requests']}")
    if candidate["label"] != base["label"]:
        factual.append(f"rótulo {base['label'] or 'erro'}→{candidate['label'] or 'erro'}")
    if candidate["option_types"] != base["option_types"]:
        factual.append("composição das opções mudou")
    if positive and negative:
        verdict = "misto"
    elif positive:
        verdict = "melhora"
    elif negative:
        verdict = "regressão"
    elif factual:
        verdict = "alterado"
    else:
        verdict = "estável"
    return {
        "verdict": verdict,
        "positive": positive,
        "negative": negative,
        "factual": factual,
    }


def compact(details: dict) -> str:
    valid = "válido" if details["valid"] else f"erro ({details['error_origin']})"
    useful = "útil" if details["useful"] else "retido"
    consensus = "Agree" if details["local_majority_agree"] else "Disagree"
    match = "alinha Studio" if details["studio_match"] else "diverge Studio"
    if details["studio_match"] is None:
        match = "Studio n/d"
    return (
        f"{valid}; {useful}; {consensus}; {match}; "
        f"{details['requests']} pedidos; revisores {details['reviewer_agree']}/{details['reviewer_total']}"
    )


def aggregate(name: str, rows: list[dict], summary: dict, baseline_summary: dict) -> dict:
    comparisons = [row["comparisons"][name] for row in rows]
    details = [row["versions"][name] for row in rows]
    baseline_details = [row["versions"]["v20"] for row in rows]
    outcomes = Counter(item["verdict"] for item in comparisons)
    return {
        "name": name,
        "completed": int(summary.get("completed") or 0),
        "valid": int(summary.get("valid_leader_panels") or 0),
        "valid_delta": int(summary.get("valid_leader_panels") or 0) - int(baseline_summary.get("valid_leader_panels") or 0),
        "useful": int(summary.get("useful_leader_outputs") or 0),
        "useful_delta": int(summary.get("useful_leader_outputs") or 0) - int(baseline_summary.get("useful_leader_outputs") or 0),
        "majority": int(summary.get("local_majority_agree") or 0),
        "majority_delta": int(summary.get("local_majority_agree") or 0) - int(baseline_summary.get("local_majority_agree") or 0),
        "studio_matches": int(summary.get("studio_consensus_matches") or 0),
        "studio_delta": int(summary.get("studio_consensus_matches") or 0) - int(baseline_summary.get("studio_consensus_matches") or 0),
        "reviewer_invalid": sum(item["reviewer_invalid"] for item in details),
        "reviewer_invalid_delta": sum(item["reviewer_invalid"] for item in details) - sum(item["reviewer_invalid"] for item in baseline_details),
        "reviewer_substantive": sum(item["reviewer_substantive"] for item in details),
        "outcomes": dict(outcomes),
        "validity_recovered_cases": [row["case_id"] for row in rows if not row["versions"]["v20"]["valid"] and row["versions"][name]["valid"]],
        "validity_lost_cases": [row["case_id"] for row in rows if row["versions"]["v20"]["valid"] and not row["versions"][name]["valid"]],
        "usefulness_gained_cases": [row["case_id"] for row in rows if not row["versions"]["v20"]["useful"] and row["versions"][name]["useful"]],
        "usefulness_lost_cases": [row["case_id"] for row in rows if row["versions"]["v20"]["useful"] and not row["versions"][name]["useful"]],
        "majority_gained_cases": [row["case_id"] for row in rows if not row["versions"]["v20"]["local_majority_agree"] and row["versions"][name]["local_majority_agree"]],
        "majority_lost_cases": [row["case_id"] for row in rows if row["versions"]["v20"]["local_majority_agree"] and not row["versions"][name]["local_majority_agree"]],
        "declaratory_neutral_parties": sum(item["declaratory_neutral_parties"] for item in details),
        "declaratory_options": sum(item["declaratory_options"] for item in details),
        "documentary_bases": sum(item["documentary_bases"] for item in details),
        "requests": sum(item["requests"] for item in details),
        "requests_delta": sum(item["requests"] for item in details) - sum(item["requests"] for item in baseline_details),
        "api_calls": int(summary.get("api_calls") or 0),
        "tokens": int(summary.get("total_tokens") or 0),
        "cost_usd": str(summary.get("cost_usd") or "0"),
    }


def build_analysis(root: Path) -> dict:
    folders = {BASELINE[0]: root / BASELINE[1]}
    folders.update({name: root / relative for name, relative in CANDIDATES})
    loaded = {
        name: {path.stem: read_json(path) for path in result_paths(folder)}
        for name, folder in folders.items()
    }
    rows = []
    for number in range(1, 51):
        case_id = f"{number:04d}"
        versions = {name: panel_details(cases[case_id]) for name, cases in loaded.items()}
        rows.append({
            "case_id": case_id,
            "category": loaded["v20"][case_id].get("category") or "—",
            "versions": versions,
            "comparisons": {
                name: transition(versions["v20"], versions[name])
                for name, _ in CANDIDATES
            },
        })
    summaries = {name: read_json(folder / "summary.json") for name, folder in folders.items()}
    aggregates = [
        aggregate(name, rows, summaries[name], summaries["v20"])
        for name, _ in CANDIDATES
    ]
    baseline_details = [row["versions"]["v20"] for row in rows]
    baseline = {
        "name": "v20",
        "completed": 50,
        "valid": int(summaries["v20"].get("valid_leader_panels") or 0),
        "useful": int(summaries["v20"].get("useful_leader_outputs") or 0),
        "majority": int(summaries["v20"].get("local_majority_agree") or 0),
        "studio_matches": int(summaries["v20"].get("studio_consensus_matches") or 0),
        "reviewer_invalid": sum(item["reviewer_invalid"] for item in baseline_details),
        "reviewer_substantive": sum(item["reviewer_substantive"] for item in baseline_details),
        "declaratory_neutral_parties": sum(item["declaratory_neutral_parties"] for item in baseline_details),
        "declaratory_options": sum(item["declaratory_options"] for item in baseline_details),
        "documentary_bases": sum(item["documentary_bases"] for item in baseline_details),
        "requests": sum(item["requests"] for item in baseline_details),
        "api_calls": int(summaries["v20"].get("api_calls") or 0),
        "tokens": int(summaries["v20"].get("total_tokens") or 0),
        "cost_usd": str(summaries["v20"].get("cost_usd") or "0"),
    }
    return {
        "method": "paired operational comparison over the same 50 cases; no legal-merit ground truth",
        "baseline": baseline,
        "candidates": aggregates,
        "cases": rows,
    }


def delta(value: int) -> str:
    return f"{value:+d}"


def case_list(values: list[str]) -> str:
    return ", ".join(values) if values else "nenhum"


def render_html(analysis: dict) -> str:
    baseline = analysis["baseline"]
    score_rows = []
    detail_blocks = []
    for candidate in analysis["candidates"]:
        outcomes = candidate["outcomes"]
        score_rows.append(
            "<tr>"
            f"<td><strong>{escape(candidate['name'])}</strong></td>"
            f"<td>{candidate['valid']} ({delta(candidate['valid_delta'])})</td>"
            f"<td>{candidate['useful']} ({delta(candidate['useful_delta'])})</td>"
            f"<td>{candidate['majority']} ({delta(candidate['majority_delta'])})</td>"
            f"<td>{candidate['studio_matches']} ({delta(candidate['studio_delta'])})</td>"
            f"<td>{candidate['reviewer_invalid']} ({delta(candidate['reviewer_invalid_delta'])})</td>"
            f"<td>{candidate['requests']} ({delta(candidate['requests_delta'])})</td>"
            f"<td>{outcomes.get('melhora', 0)} / {outcomes.get('regressão', 0)} / {outcomes.get('misto', 0)}</td>"
            f"<td>{candidate['api_calls']:,}</td><td>{candidate['tokens']:,}</td>"
            f"<td>US$ {Decimal(candidate['cost_usd']):.4f}</td>"
            "</tr>"
        )
        detail_blocks.append(
            f"<section><h3>{escape(candidate['name'])} × v20</h3>"
            f"<p><strong>Validade recuperada:</strong> {case_list(candidate['validity_recovered_cases'])}. "
            f"<strong>Validade perdida:</strong> {case_list(candidate['validity_lost_cases'])}.</p>"
            f"<p><strong>Utilidade ganha:</strong> {case_list(candidate['usefulness_gained_cases'])}. "
            f"<strong>Utilidade perdida:</strong> {case_list(candidate['usefulness_lost_cases'])}.</p>"
            f"<p><strong>Maioria ganha:</strong> {case_list(candidate['majority_gained_cases'])}. "
            f"<strong>Maioria perdida:</strong> {case_list(candidate['majority_lost_cases'])}.</p>"
            f"<p>Opções declaratórias com polos neutros: {candidate['declaratory_neutral_parties']}/"
            f"{candidate['declaratory_options']}; bases documentais DR/DD usadas: {candidate['documentary_bases']}; "
            f"pedidos catalogados: {candidate['requests']} ({delta(candidate['requests_delta'])}).</p>"
            "</section>"
        )
    case_rows = []
    for row in analysis["cases"]:
        cells = []
        for name, _ in CANDIDATES:
            item = row["comparisons"][name]
            details = row["versions"][name]
            signals = []
            if item["positive"]:
                signals.append("+ " + "; ".join(item["positive"]))
            if item["negative"]:
                signals.append("− " + "; ".join(item["negative"]))
            if item["factual"]:
                signals.append("Δ " + "; ".join(item["factual"]))
            signal_text = "<br>".join(escape(value) for value in signals) or "sem mudança medida"
            cells.append(
                f'<td><span class="badge {escape(item["verdict"])}">{escape(item["verdict"])}</span>'
                f"<div>{escape(compact(details))}</div><small>{signal_text}</small></td>"
            )
        case_rows.append(
            "<tr>"
            f"<td>{escape(row['case_id'])}</td><td>{escape(row['category'])}</td>"
            f"<td>{escape(compact(row['versions']['v20']))}</td>"
            + "".join(cells)
            + "</tr>"
        )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mediare — análise caso a caso v20 × v21</title>
<style>
:root{{--ink:#172235;--muted:#607086;--blue:#315efb;--line:#dce3ef;--pale:#eef3ff;font-family:Inter,Arial,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:var(--ink);line-height:1.45}}main{{width:min(1500px,calc(100% - 28px));margin:28px auto;background:#fff;padding:42px}}h1{{margin:.2rem 0}}h2{{margin-top:34px;border-bottom:2px solid var(--line);padding-bottom:7px}}h3{{margin-bottom:6px}}.eyebrow{{color:var(--blue);font-weight:700;text-transform:uppercase;letter-spacing:.07em}}.note{{background:var(--pale);border-left:5px solid var(--blue);padding:14px 18px}}.caution{{background:#fff4cc;border-left:5px solid #c08a00;padding:14px 18px}}table{{border-collapse:collapse;width:100%;font-size:.86rem}}th,td{{border:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}}th{{background:var(--pale);position:sticky;top:0}}small{{color:var(--muted)}}.badge{{display:inline-block;border-radius:999px;padding:2px 8px;margin-bottom:5px;font-weight:700}}.melhora{{background:#dff6e8;color:#19653a}}.regressão{{background:#ffe2e0;color:#8b211b}}.misto{{background:#fff0c9;color:#725000}}.alterado{{background:#e6ecff;color:#2947a8}}.estável{{background:#edf0f4;color:#4d5968}}section{{border-bottom:1px solid var(--line)}}@media(max-width:900px){{main{{padding:24px 14px}}table{{display:block;overflow:auto}}}}@media print{{body{{background:#fff}}main{{margin:0;padding:0;width:auto}}th{{position:static}}}}
</style></head><body><main>
<div class="eyebrow">Experimento pareado · 50 casos</div><h1>v20 × candidatas v21</h1>
<p>Esta análise compara resultados operacionais obtidos sobre os mesmos casos. Ela mede validade do painel, utilidade para mediação, votação local, alinhamento com o resultado observado no Studio e robustez do formato do revisor. Não é um gabarito jurídico de mérito.</p>
<div class="note"><strong>Conclusão preliminar.</strong> A v21-schema é a melhor fundação técnica porque eliminou 35 falhas de formato dos revisores sem piora agregada observada de validade e utilidade. A v21-options comprovou a correção de opções declaratórias em 26/26 ocorrências e trouxe o melhor sinal de consenso. A v21-catalog mostrou consolidações úteis, mas ainda exige revisão de fidelidade nos casos alterados. Se for obrigatório escolher uma candidata intacta, escolha schema; o melhor próximo experimento é uma híbrida schema + correção declaratória de options.</div>
<div class="caution"><strong>Limite causal.</strong> As execuções usam os mesmos casos e modelos, mas as respostas das LLMs não são determinísticas. A mudança schema ocorre somente depois da geração do painel; portanto, seus três painéis recuperados e três perdidos são variação de execução, não efeito possível do novo formato do revisor. Na options, quatro dos cinco painéis perdidos falharam na lente probatória, antes da etapa alterada. Os deltas de validade abaixo são observações, não causalidade automática.</div>
<h2>Placar agregado</h2>
<p>Referência v20: {baseline['valid']} painéis válidos, {baseline['useful']} úteis, {baseline['majority']} maiorias, {baseline['studio_matches']} alinhamentos com Studio, {baseline['reviewer_invalid']} falhas de formato de revisor e {baseline['requests']} pedidos catalogados.</p>
<table><thead><tr><th>Candidata</th><th>Válidos (Δ)</th><th>Úteis (Δ)</th><th>Maiorias (Δ)</th><th>Studio (Δ)</th><th>Falhas formato (Δ)</th><th>Pedidos (Δ)</th><th>Melhora / regressão / misto</th><th>Chamadas</th><th>Tokens</th><th>Custo</th></tr></thead><tbody>{''.join(score_rows)}</tbody></table>
<h2>Leitura das mudanças isoladas</h2>
<ul><li><strong>Schema:</strong> reduziu falhas de formato dos revisores de 35 para zero. As rejeições substantivas subiram de 32 para 75, indicando que os revisores conseguiram responder ao protocolo e passaram a apontar problemas de conteúdo; isso explica por que mais robustez não virou automaticamente mais Agree.</li><li><strong>Catalog:</strong> produziu 146 pedidos contra 192 na v20. Nos casos inspecionados 0015, 0017, 0018, 0023 e 0048, a redução removeu duplicações, componentes internos de cálculo e contestações tratadas como contrapedidos. Como o conjunto não tem gabarito jurídico de pedidos, todos os casos com catálogo alterado continuam sujeitos a revisão humana.</li><li><strong>Options:</strong> todas as 26 opções declaratórias observadas ficaram corretamente sem pagador e beneficiário, contra 0/17 na v20. Houve +7 maiorias e +7 alinhamentos com Studio. A ampliação de bases documentais não demonstrou ganho agregado: foram 22 bases DR/DD, contra 27 na v20.</li></ul>
<h2>Transições relevantes</h2>{''.join(detail_blocks)}
<h2>Análise dos 50 casos</h2>
<p><span class="badge melhora">melhora</span> só há sinais positivos; <span class="badge regressão">regressão</span> só negativos; <span class="badge misto">misto</span> há ganho e perda simultâneos; “alterado” registra mudança de conteúdo sem mudança nos indicadores; “estável” não mudou nos indicadores medidos.</p>
<table><thead><tr><th>Caso</th><th>Categoria</th><th>v20</th><th>v21-schema × v20</th><th>v21-catalog × v20</th><th>v21-options × v20</th></tr></thead><tbody>{''.join(case_rows)}</tbody></table>
<h2>Recomendação</h2>
<ol><li>Usar <strong>v21-schema</strong> como fundação do protocolo de revisão.</li><li>Incorporar somente a correção comprovada de opções declaratórias da <strong>v21-options</strong>; não promover ainda a ampliação de bases documentais.</li><li>Avaliar as consolidações da <strong>v21-catalog</strong> nos casos alterados e incorporar apenas as regras que não omitirem providências expressas.</li><li>Rodar a híbrida primeiro nos casos que perderam validade/utilidade e nos que ganharam maioria; somente depois repetir os 50.</li><li>Se preservar pelo menos 42 painéis válidos e 38 úteis e mantiver parte do ganho de consenso, promovê-la ao Studio nos casos 101–150.</li></ol>
</main></body></html>"""


def main() -> int:
    root = Path(".")
    analysis = build_analysis(root)
    Path("V21_CASE_BY_CASE_ANALYSIS.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    Path("V21_CASE_BY_CASE_ANALYSIS.html").write_text(
        render_html(analysis), encoding="utf-8"
    )
    print(json.dumps({row["name"]: row["outcomes"] for row in analysis["candidates"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
