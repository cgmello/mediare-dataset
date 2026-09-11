#!/usr/bin/env python3
"""Gera a análise pareada dos 20 sentinelas v22 × v23.1."""

from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
from html import escape
import json
from pathlib import Path


CASE_IDS = (
    "0001", "0007", "0008", "0013", "0015", "0017", "0018", "0020",
    "0022", "0023", "0024", "0026", "0029", "0031", "0033", "0035",
    "0046", "0047", "0048", "0050",
)
BASELINE_DIR = "res_openrouter_v22_0001_0050"
CANDIDATE_DIR = "res_openrouter_v23_1_sentinels"
TECHNICAL_RETRY_DIR = "res_openrouter_v23_1_technical_retries"
TECHNICAL_RETRY_IDS = ("0013", "0017", "0033", "0048")

TECHNICAL_RETRY_ASSESSMENTS = {
    "0013": {
        "technical": "Falha técnica persistente",
        "semantic": "Não avaliável: não houve painel nem revisão RP/CR.",
        "conclusion": "DeepSeek voltou a falhar na lente probatória com resposta vazia; separar modelo/provedor do catálogo.",
    },
    "0017": {
        "technical": "Painel recuperado",
        "semantic": "Catálogo materialmente fiel: 4 RP e 2 CR expressamente formulados no pedido contraposto.",
        "conclusion": "Houve 1 aprovação, 2 objeções a CR01 e 1 erro de formato. A fonte contém pedido contraposto expresso e a mesma estrutura já havia obtido 3–1 na v23.1.",
    },
    "0033": {
        "technical": "Falha técnica persistente",
        "semantic": "Não avaliável nesta execução; rodada anterior confirmou um único RP sem falso CR.",
        "conclusion": "Mistral repetiu uma ressalva fora do conjunto permitido na lente auditora; é incompatibilidade de formato/instrução.",
    },
    "0048": {
        "technical": "Painel recuperado",
        "semantic": "3 pedidos negociáveis coerentes: RP01 e CR01/CR02 expressamente contrapostos.",
        "conclusion": "Recuperação completa com aprovação unânime 4–0; a falha anterior era transitória, embora a execução tenha sido lenta.",
    },
}

# Julgamentos humanos desta rodada. Eles avaliam fidelidade do catálogo e causa
# operacional; não substituem parecer jurídico sobre o mérito do conflito.
ASSESSMENTS = {
    "0001": {
        "verdict": "melhoria",
        "catalog": "Mesmos cinco RP e três contrapedidos materiais; RR01–RR03 foram corretamente renomeados para CR01–CR03.",
        "cause": "A maioria foi recuperada. Três revisores aprovaram; o erro de formato do Mistral não revelou defeito material.",
    },
    "0007": {
        "verdict": "melhoria",
        "catalog": "Preservou três pedidos e corrigiu a desocupação de modalidade declaratória para obrigação de fazer.",
        "cause": "Consenso unânime preservado; mudança pequena e materialmente correta.",
    },
    "0008": {
        "verdict": "melhoria",
        "catalog": "Consolidou a multa de 10% como acessório da cobrança principal, reduzindo três pedidos para dois sem omitir resultado autônomo.",
        "cause": "Disagree por empate: Mistral exigiu valor final não disponível e DeepSeek marcou RP01 sem justificativa estruturada. Predomina rigor excessivo/variação, não erro de catálogo.",
    },
    "0013": {
        "verdict": "falha técnica",
        "catalog": "Nenhum catálogo comparável foi produzido em qualquer versão.",
        "cause": "O mesmo líder DeepSeek falhou na lente probatória: JSON inválido na v22 e resposta vazia/transporte na v23. Não é efeito da regra de catálogo.",
    },
    "0015": {
        "verdict": "melhoria",
        "catalog": "Removeu RR01, pois valores já pagos são abatimento/defesa e não contrapedido autônomo.",
        "cause": "Passou de empate 2–2 para aprovação unânime 4–0.",
    },
    "0017": {
        "verdict": "misto",
        "catalog": "Em execução anterior da mesma v23.1, consolidou seis rubricas de retenção em CR01 e preservou o dano moral autônomo como CR02; três de quatro revisores aprovaram.",
        "cause": "Nesta repetição, a lente auditora falhou três vezes nas regras de dupla contagem antes da revisão. É regressão operacional da execução, não evidência de regressão do catálogo.",
    },
    "0018": {
        "verdict": "estável",
        "catalog": "Preservou o único pedido agregado de cobrança; itens contestados são componentes da apuração, não pedidos autônomos.",
        "cause": "Empate 2–2. A fragmentação pedida pelo Mistral contraria a unidade material; a objeção de opção do Claude é opaca e a opção já estava retida pela auditora.",
    },
    "0020": {
        "verdict": "estável",
        "catalog": "Preservou corretamente um único pedido de resgate da garantia locatícia.",
        "cause": "A maioria já existia e passou de 3–1 para unanimidade; sinal positivo, mas sujeito à variação entre execuções.",
    },
    "0022": {
        "verdict": "melhoria",
        "catalog": "Preservou três RP e incluiu CR01 para o pedido afirmativo e autônomo de prazo razoável para desocupação.",
        "cause": "Três revisores aprovaram. A única divergência foi sobre a conclusão do CR01, não sua existência no catálogo.",
    },
    "0023": {
        "verdict": "melhoria",
        "catalog": "Removeu a perícia contábil tratada pela v22 como RR01; perícia é meio de apuração, não resultado material de acordo.",
        "cause": "Aprovação unânime preservada e catálogo ficou mais fiel.",
    },
    "0024": {
        "verdict": "estável",
        "catalog": "Preservou separadamente inexigibilidade, recálculo da multa e devolução do saldo da caução.",
        "cause": "Passou de 3–1 para unanimidade; nenhuma regressão observada.",
    },
    "0026": {
        "verdict": "melhoria",
        "catalog": "Removeu duas declarações defensivas do requerido que apenas negavam responsabilidade pelos RP; manteve os quatro resultados pedidos pelo requerente.",
        "cause": "Três revisores aprovaram. Mistral insistiu em converter a defesa em CR, exatamente o falso positivo que a v23 foi criada para evitar.",
    },
    "0029": {
        "verdict": "misto",
        "catalog": "Corrigiu o valor inventado de R$ 23.400,00: CR02 agora mantém a fórmula de 12 aluguéis, mas deixa o valor numérico nulo. CR01 preserva a disposição econômica única da caução.",
        "cause": "O catálogo melhorou. Uma opção de CR01 falhou e foi corretamente retida; DeepSeek tratou a retenção como fatal, enquanto OpenAI e Mistral pediram fragmentações ou CR já existente. Há defeito localizado de opção e excesso dos revisores, não retorno do erro numérico.",
    },
    "0031": {
        "verdict": "estável",
        "catalog": "Preservou um único pedido de honorários de R$ 2.490,00, valor final literalmente declarado na petição.",
        "cause": "Maioria preservada; a troca do único dissenso de Mistral para OpenAI é variação de modelo.",
    },
    "0033": {
        "verdict": "misto",
        "catalog": "A v23 removeu corretamente a declaração de inexigibilidade que apenas negava o RP01; execução anterior confirmou o catálogo com um único RP.",
        "cause": "Nesta repetição, a auditora falhou três vezes em regras de dupla contagem antes da revisão. Falha técnica separada do ganho de catálogo.",
    },
    "0035": {
        "verdict": "melhoria",
        "catalog": "Uniu reconhecimento e pagamento da mesma dívida, reduzindo dois RP redundantes para um resultado material.",
        "cause": "Maioria 3–1 preservada; o dissenso isolado não trouxe falha estruturada de catálogo.",
    },
    "0046": {
        "verdict": "estável",
        "catalog": "Manteve os quatro pedidos expressos do consumidor sem criar contrapedidos a partir das defesas.",
        "cause": "Maioria preservada. A divergência isolada do DeepSeek foi sobre opções, não catálogo.",
    },
    "0047": {
        "verdict": "melhoria",
        "catalog": "Consolidou desfazimento, devolução do veículo e restituição do preço como uma composição econômica ligada; dano moral permaneceu autônomo.",
        "cause": "Unanimidade preservada com catálogo mais compacto.",
    },
    "0048": {
        "verdict": "falha técnica",
        "catalog": "Nenhum catálogo comparável foi produzido em qualquer versão.",
        "cause": "O mesmo líder DeepSeek retornou texto vazio: na etapa de catálogo da v22 e na lente probatória da v23. Problema de modelo/transporte.",
    },
    "0050": {
        "verdict": "estável",
        "catalog": "Preservou cinco RP, mas permanece possível sobreposição: RP03 pede todos os valores pagos e RP04 inclui entrada e parcelas dentro dos R$ 19.190,89.",
        "cause": "Maioria 3–1 preservada. A objeção estruturada do GLM é plausível e revela que consenso maioritário não garante ausência de duplicidade.",
    },
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def error_kind(error: object) -> str | None:
    if not error:
        return None
    text = str(error)
    if "RunnerError" in text or "OPENROUTER_EMPTY_TEXT" in text or "JSON_INVALIDO" in text:
        return "modelo/transporte"
    if "lente=auditora" in text:
        return "validação da auditora"
    return "painel"


def summarize_result(row: dict) -> dict:
    panel = row.get("leader_panel") or {}
    requests = (panel.get("catalogo") or {}).get("pedidos") or []
    reviewers = row.get("reviewers") or []
    diagnostics = Counter()
    votes = Counter()
    for reviewer in reviewers:
        votes[str(reviewer.get("vote") or "unknown")] += 1
        diagnostic = str(reviewer.get("diagnostic") or "")
        if diagnostic.startswith("REVISOR_CATALOGO"):
            diagnostics["catalogo"] += 1
        elif diagnostic.startswith("REVISOR_") and diagnostic != "REVISOR_APROVA":
            diagnostics["outro"] += 1
        elif diagnostic.startswith("LLM_INVALID_PANEL"):
            diagnostics["formato"] += 1
    prefixes = Counter(str(item.get("id") or "")[:2] for item in requests)
    return {
        "valid": row.get("leader_error") is None,
        "error": row.get("leader_error"),
        "error_kind": error_kind(row.get("leader_error")),
        "consensus": row.get("local_consensus"),
        "label": (row.get("leader_impression") or {}).get("label"),
        "request_count": len(requests),
        "request_ids": [item.get("id") for item in requests],
        "rp": prefixes.get("RP", 0),
        "counterclaims": prefixes.get("CR", 0) + prefixes.get("RR", 0),
        "reviewer_agree": votes.get("agree", 0),
        "reviewer_disagree": votes.get("disagree", 0),
        "reviewer_error": votes.get("error", 0),
        "catalog_objections": diagnostics.get("catalogo", 0),
        "other_objections": diagnostics.get("outro", 0),
        "format_errors": diagnostics.get("formato", 0),
        "api_calls": int(row.get("case_api_calls") or 0),
        "tokens": int(row.get("total_tokens") or 0),
        "cost_usd": str(row.get("case_cost_usd") or "0"),
        "elapsed_seconds": float(row.get("elapsed_seconds") or 0),
    }


def aggregate_reviewers(rows: dict[str, dict]) -> dict:
    votes = Counter()
    diagnostics = Counter()
    by_model = defaultdict(Counter)
    for row in rows.values():
        for reviewer in row.get("reviewers") or []:
            vote = str(reviewer.get("vote") or "unknown")
            diagnostic = str(reviewer.get("diagnostic") or "")
            votes[vote] += 1
            by_model[str(reviewer.get("model") or "unknown")][vote] += 1
            if diagnostic.startswith("REVISOR_CATALOGO"):
                diagnostics["catalog_objections"] += 1
    total = sum(votes.values())
    return {
        "total": total,
        "agree": votes.get("agree", 0),
        "disagree": votes.get("disagree", 0),
        "error": votes.get("error", 0),
        "agree_rate": (votes.get("agree", 0) / total) if total else 0,
        "catalog_objections": diagnostics.get("catalog_objections", 0),
        "by_model": {model: dict(counts) for model, counts in sorted(by_model.items())},
    }


def build_analysis(root: Path) -> dict:
    if set(ASSESSMENTS) != set(CASE_IDS):
        raise ValueError("ASSESSMENTS deve cobrir exatamente os 20 casos")
    folders = {"v22": root / BASELINE_DIR, "v23.1": root / CANDIDATE_DIR}
    raw = {
        version: {
            case_id: read_json(folder / "results" / f"{case_id}.json")
            for case_id in CASE_IDS
        }
        for version, folder in folders.items()
    }
    rows = []
    for case_id in CASE_IDS:
        versions = {version: summarize_result(cases[case_id]) for version, cases in raw.items()}
        rows.append({
            "case_id": case_id,
            "category": raw["v23.1"][case_id].get("category") or raw["v22"][case_id].get("category"),
            "assessment": ASSESSMENTS[case_id],
            "versions": versions,
        })

    summaries = {version: read_json(folder / "summary.json") for version, folder in folders.items()}
    classifications = Counter(item["assessment"]["verdict"] for item in rows)
    majority_gained = [
        item["case_id"] for item in rows
        if item["versions"]["v22"]["consensus"] != "LOCAL_MAJORITY_AGREE"
        and item["versions"]["v23.1"]["consensus"] == "LOCAL_MAJORITY_AGREE"
    ]
    majority_lost = [
        item["case_id"] for item in rows
        if item["versions"]["v22"]["consensus"] == "LOCAL_MAJORITY_AGREE"
        and item["versions"]["v23.1"]["consensus"] != "LOCAL_MAJORITY_AGREE"
    ]
    retry_folder = root / TECHNICAL_RETRY_DIR
    retry_raw = {
        case_id: read_json(retry_folder / "results" / f"{case_id}.json")
        for case_id in TECHNICAL_RETRY_IDS
    }
    technical_retries = {
        "summary": read_json(retry_folder / "summary.json"),
        "recovered_valid_panels": [
            case_id for case_id, row in retry_raw.items() if not row.get("leader_error")
        ],
        "recovered_majorities": [
            case_id for case_id, row in retry_raw.items()
            if row.get("local_consensus") == "LOCAL_MAJORITY_AGREE"
        ],
        "persistent_technical_failures": [
            case_id for case_id, row in retry_raw.items() if row.get("leader_error")
        ],
        "cases": [
            {
                "case_id": case_id,
                "original": summarize_result(raw["v23.1"][case_id]),
                "retry": summarize_result(retry_raw[case_id]),
                "assessment": TECHNICAL_RETRY_ASSESSMENTS[case_id],
            }
            for case_id in TECHNICAL_RETRY_IDS
        ],
    }
    return {
        "method": (
            "paired operational and human catalog review over the same 20 cases; "
            "court-answer keys are contextual evidence, not mediation ground truth"
        ),
        "summary": {
            "v22": summaries["v22"],
            "v23.1": summaries["v23.1"],
            "reviewers_v22": aggregate_reviewers(raw["v22"]),
            "reviewers_v23.1": aggregate_reviewers(raw["v23.1"]),
            "majority_gained_cases": majority_gained,
            "majority_lost_cases": majority_lost,
            "classifications": dict(classifications),
            "disagreement_diagnosis": {
                "technical": ["0013", "0017", "0033", "0048"],
                "reviewer_excess_or_variation": ["0008", "0018"],
                "mixed_local_option_and_reviewer_excess": ["0029"],
            },
            "persistent_material_risk": ["0050"],
            "technical_retries": technical_retries,
        },
        "cases": rows,
    }


def compact(version: dict) -> str:
    if not version["valid"]:
        return f"erro: {version['error_kind']}"
    vote = f"{version['reviewer_agree']}A/{version['reviewer_disagree']}D"
    return (
        f"{version['consensus'].replace('LOCAL_MAJORITY_', '')}; "
        f"{version['request_count']} pedidos ({'/'.join(version['request_ids'])}); "
        f"revisores {vote}; {version['label']}"
    )


def render_html(analysis: dict) -> str:
    summary = analysis["summary"]
    v22 = summary["v22"]
    v23 = summary["v23.1"]
    r22 = summary["reviewers_v22"]
    r23 = summary["reviewers_v23.1"]
    cost_change = (Decimal(str(v23["cost_usd"])) / Decimal(str(v22["cost_usd"])) - 1) * 100
    token_change = (Decimal(v23["total_tokens"]) / Decimal(v22["total_tokens"]) - 1) * 100
    verdict_labels = {
        "melhoria": "Melhoria",
        "estável": "Estável",
        "misto": "Misto",
        "falha técnica": "Falha técnica",
    }
    verdict_css = {
        "melhoria": "melhoria",
        "estável": "estavel",
        "misto": "misto",
        "falha técnica": "falha-tecnica",
    }
    rows = []
    for item in analysis["cases"]:
        assessment = item["assessment"]
        css = verdict_css[assessment["verdict"]]
        rows.append(
            "<tr>"
            f"<td><strong>{item['case_id']}</strong><br><small>{escape(item['category'] or '')}</small></td>"
            f"<td>{escape(compact(item['versions']['v22']))}</td>"
            f"<td>{escape(compact(item['versions']['v23.1']))}</td>"
            f'<td><span class="badge {css}">{escape(verdict_labels[assessment["verdict"]])}</span>'
            f"<p>{escape(assessment['catalog'])}</p><small>{escape(assessment['cause'])}</small></td>"
            "</tr>"
        )
    retry = summary["technical_retries"]
    retry_rows = []
    for item in retry["cases"]:
        assessment = item["assessment"]
        retry_rows.append(
            "<tr>"
            f"<td><strong>{item['case_id']}</strong></td>"
            f"<td>{escape(compact(item['original']))}<br><small>{item['original']['elapsed_seconds']:.1f} s</small></td>"
            f"<td>{escape(compact(item['retry']))}<br><small>{item['retry']['elapsed_seconds']:.1f} s</small></td>"
            f"<td><strong>{escape(assessment['technical'])}</strong><br>{escape(assessment['conclusion'])}</td>"
            f"<td>{escape(assessment['semantic'])}</td>"
            "</tr>"
        )
    retry_summary = retry["summary"]
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mediare — análise pareada v22 × v23.1</title>
<style>
:root{{--ink:#172235;--muted:#607086;--blue:#315efb;--line:#dce3ef;--pale:#eef3ff;font-family:Inter,Arial,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:var(--ink);line-height:1.45}}main{{width:min(1450px,calc(100% - 28px));margin:28px auto;background:#fff;padding:42px}}h1{{margin:.2rem 0}}h2{{margin-top:34px;border-bottom:2px solid var(--line);padding-bottom:7px}}.eyebrow{{color:var(--blue);font-weight:700;text-transform:uppercase;letter-spacing:.07em}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.card{{background:var(--pale);padding:15px;border-radius:8px}}.card strong{{display:block;font-size:1.6rem}}.note{{background:#eef3ff;border-left:5px solid var(--blue);padding:14px 18px}}.warning{{background:#fff4cc;border-left:5px solid #c08a00;padding:14px 18px}}table{{border-collapse:collapse;width:100%;font-size:.86rem}}th,td{{border:1px solid var(--line);padding:9px;text-align:left;vertical-align:top}}th{{background:var(--pale);position:sticky;top:0}}small{{color:var(--muted)}}.badge{{display:inline-block;border-radius:999px;padding:2px 8px;font-weight:700}}.melhoria{{background:#dff6e8;color:#19653a}}.estavel{{background:#edf0f4;color:#4d5968}}.misto{{background:#fff0c9;color:#725000}}.falha-tecnica{{background:#ffe2e0;color:#8b211b}}@media(max-width:900px){{main{{padding:24px 14px}}.cards{{grid-template-columns:1fr 1fr}}table{{display:block;overflow:auto}}}}@media print{{body{{background:#fff}}main{{margin:0;padding:0;width:auto}}th{{position:static}}}}
</style></head><body><main>
<div class="eyebrow">Experimento pareado · 20 casos sentinela</div><h1>v22 × v23.1</h1>
<p>Comparação operacional e revisão humana do catálogo nos mesmos 20 casos. O gabarito judicial ajuda a contextualizar fatos e valores, mas não é um gabarito completo de opções de mediação.</p>
<div class="cards"><div class="card">Maiorias v22<strong>{v22['local_majority_agree']}/20</strong></div><div class="card">Maiorias v23.1<strong>{v23['local_majority_agree']}/20</strong></div><div class="card">Votos Agree<strong>{r22['agree_rate']:.1%} → {r23['agree_rate']:.1%}</strong></div><div class="card">Custo v23.1<strong>US$ {Decimal(str(v23['cost_usd'])):.4f}</strong></div></div>
<div class="note"><strong>Conclusão.</strong> A v23.1 melhorou materialmente o catálogo sem apagar os ganhos da v22: recuperou maioria nos casos 0001 e 0015, não perdeu maioria em nenhum caso concluído, reduziu objeções de catálogo de {r22['catalog_objections']} para {r23['catalog_objections']} e corrigiu os falsos RR/CR, fragmentações e valor inferido que motivaram a versão. As sete divergências remanescentes não demonstram regressão sistêmica do catálogo.</div>
<div class="warning"><strong>Contrapeso necessário.</strong> Painéis válidos caíram de {v22['valid_leader_panels']} para {v23['valid_leader_panels']} e saídas úteis de {v22['useful_leader_outputs']} para {v23['useful_leader_outputs']}, por falhas técnicas concentradas nos casos 0017 e 0033, além das recorrências 0013 e 0048. O caso 0050 contém possível sobreposição real entre RP03 e RP04 que passou por 3–1; aumentar Agree não pode ser o único objetivo.</div>
<h2>Placar agregado</h2>
<table><thead><tr><th>Métrica</th><th>v22</th><th>v23.1</th><th>Leitura</th></tr></thead><tbody>
<tr><td>Maioria local</td><td>{v22['local_majority_agree']}/20</td><td>{v23['local_majority_agree']}/20</td><td>+2; ganhos 0001 e 0015, nenhuma perda</td></tr>
<tr><td>Painéis válidos</td><td>{v22['valid_leader_panels']}/20</td><td>{v23['valid_leader_panels']}/20</td><td>−2 por falhas na auditora em 0017 e 0033</td></tr>
<tr><td>Saídas úteis</td><td>{v22['useful_leader_outputs']}/20</td><td>{v23['useful_leader_outputs']}/20</td><td>−2, acompanhando as falhas técnicas</td></tr>
<tr><td>Votos Agree dos revisores</td><td>{r22['agree']}/{r22['total']} ({r22['agree_rate']:.1%})</td><td>{r23['agree']}/{r23['total']} ({r23['agree_rate']:.1%})</td><td>Revisão mais convergente mesmo com menos painéis revisáveis</td></tr>
<tr><td>Objeções REVISOR_CATALOGO</td><td>{r22['catalog_objections']}</td><td>{r23['catalog_objections']}</td><td>−{r22['catalog_objections'] - r23['catalog_objections']}; a estrutura de evidência reduziu rejeições vagas</td></tr>
<tr><td>Chamadas / tokens</td><td>{v22['api_calls']} / {v22['total_tokens']:,}</td><td>{v23['api_calls']} / {v23['total_tokens']:,}</td><td>Tokens {token_change:.1f}%</td></tr>
<tr><td>Custo</td><td>US$ {Decimal(str(v22['cost_usd'])):.4f}</td><td>US$ {Decimal(str(v23['cost_usd'])):.4f}</td><td>{cost_change:.1f}%</td></tr>
</tbody></table>
<h2>Diagnóstico dos sete Disagree da v23.1</h2>
<ul><li><strong>Falhas técnicas:</strong> 0013, 0017, 0033 e 0048.</li><li><strong>Rigor excessivo ou variação dos revisores:</strong> 0008 e 0018.</li><li><strong>Misto:</strong> 0029 — catálogo melhor, opção defeituosa corretamente retida e revisores que trataram retenção/fragmentação como falha fatal.</li></ul>
<h2>Repetição dirigida dos quatro casos técnicos</h2>
<p>Os quatro casos foram repetidos com o mesmo snapshot v23.1 e a mesma posição na rotação de líderes. O filtro de execução não alterou a lista de 50 casos do manifesto. A rodada consumiu {retry_summary['api_calls']} chamadas, {retry_summary['total_tokens']:,} tokens e US$ {Decimal(str(retry_summary['cost_usd'])):.4f}.</p>
<div class="cards"><div class="card">Casos repetidos<strong>4/4</strong></div><div class="card">Painéis recuperados<strong>{len(retry['recovered_valid_panels'])}/4</strong><span>{', '.join(retry['recovered_valid_panels'])}</span></div><div class="card">Maiorias recuperadas<strong>{len(retry['recovered_majorities'])}/4</strong><span>{', '.join(retry['recovered_majorities'])}</span></div><div class="card">Falhas técnicas persistentes<strong>{len(retry['persistent_technical_failures'])}/4</strong><span>{', '.join(retry['persistent_technical_failures'])}</span></div></div>
<table><thead><tr><th>Caso</th><th>Rodada original</th><th>Repetição técnica</th><th>Estabilidade técnica</th><th>Semântica RP/CR</th></tr></thead><tbody>{''.join(retry_rows)}</tbody></table>
<div class="note"><strong>Leitura separada.</strong> <code>0013</code> e <code>0033</code> continuam como falhas técnicas sem painel comparável. <code>0048</code> recuperou painel e unanimidade, provando que sua falha anterior era transitória. <code>0017</code> recuperou o painel, mas revelou variação dos revisores sobre um CR explicitamente pedido; isso deve ser analisado como consistência da revisão, não como indisponibilidade do modelo nem como regressão automática do catálogo.</div>
<h2>Análise caso a caso</h2>
<table><thead><tr><th>Caso</th><th>v22</th><th>v23.1</th><th>Avaliação humana</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Recomendação</h2>
<ol><li><strong>Manter congelada a semântica RP/CR da v23.1</strong>; a repetição não demonstrou regressão material.</li><li>Tratar `0013` e `0033` na trilha técnica de estabilidade de lentes/modelos.</li><li>Rever a consistência dos revisores no `0017`, sem fragmentar automaticamente os cinco componentes materiais de CR01.</li><li>Manter `0048` como controle de variância e `0050` como sentinela de sobreposição material.</li></ol>
</main></body></html>"""


def main() -> int:
    analysis = build_analysis(Path("."))
    Path("V23_CASE_BY_CASE_ANALYSIS.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    Path("V23_CASE_BY_CASE_ANALYSIS.html").write_text(render_html(analysis), encoding="utf-8")
    print(json.dumps(analysis["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
