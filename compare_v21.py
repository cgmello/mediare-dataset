#!/usr/bin/env python3
"""Compara campanhas OpenRouter das candidatas v21 sem escolher às cegas."""

from __future__ import annotations

import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path


CANDIDATES = {
    "v21-schema": "res_openrouter_v21_schema_0001_0050",
    "v21-catalog": "res_openrouter_v21_catalog_0001_0050",
    "v21-options": "res_openrouter_v21_options_0001_0050",
}
STRUCTURAL_DIAGNOSTICS = {
    "REVISAO_JSON_INVALIDO",
    "REVISAO_RAIZ_INVALIDA",
    "REVISAO_CAMPOS_INVALIDOS",
    "REVISAO_CATALOGO_INVALIDO",
    "REVISAO_PEDIDOS_INVALIDOS",
    "REVISAO_ITEM_INVALIDO",
    "REVISAO_PEDIDO_ID_INVALIDO",
    "REVISAO_FALHAS_INVALIDAS",
    "REVISAO_FALHA_DESCONHECIDA",
}


def is_structural_diagnostic(diagnostic: str) -> bool:
    return diagnostic in STRUCTURAL_DIAGNOSTICS or diagnostic.startswith(
        "LLM_INVALID_PANEL:"
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_metrics(root: Path, name: str, relative: str) -> dict:
    folder = root / relative
    manifest_path = folder / "campaign.json"
    result_paths = sorted((folder / "results").glob("*.json"))
    if not manifest_path.exists():
        return {
            "name": name,
            "path": relative,
            "status": "not_initialized",
            "completed": 0,
            "total": 50,
        }
    manifest = read_json(manifest_path)
    results = [read_json(path) for path in result_paths]
    diagnostic_counts = Counter(
        review.get("diagnostic") or "REVIEWER_NO_DIAGNOSTIC"
        for row in results
        for review in row.get("reviewers", [])
        if review.get("vote") != "agree"
    )
    useful = sum(
        (row.get("leader_impression") or {}).get("label")
        in {"APTO_INTEGRAL", "APTO_PARCIAL_COM_RETENCOES"}
        for row in results
    )
    metrics = {
        "name": name,
        "path": relative,
        "version": manifest.get("version"),
        "status": "complete" if len(results) == len(manifest["case_ids"]) else "in_progress",
        "completed": len(results),
        "total": len(manifest["case_ids"]),
        "valid_leader_panels": sum(not row.get("leader_error") for row in results),
        "useful_leader_outputs": useful,
        "local_majority_agree": sum(
            row.get("local_consensus") == "LOCAL_MAJORITY_AGREE" for row in results
        ),
        "reviewer_structural_failures": sum(
            count
            for diagnostic, count in diagnostic_counts.items()
            if is_structural_diagnostic(diagnostic)
        ),
        "cost_usd": (read_json(folder / "summary.json").get("cost_usd")
                     if (folder / "summary.json").exists() else "0"),
        "diagnostics": dict(diagnostic_counts.most_common()),
    }
    metrics["automatic_gates_pass"] = bool(
        metrics["completed"] == metrics["total"]
        and metrics["valid_leader_panels"] >= 45
        and metrics["useful_leader_outputs"] >= 40
        and metrics["reviewer_structural_failures"] == 0
    )
    return metrics


def rank_key(row: dict) -> tuple:
    return (
        int(row.get("automatic_gates_pass", False)),
        row.get("valid_leader_panels", 0),
        row.get("useful_leader_outputs", 0),
        row.get("local_majority_agree", 0),
        -row.get("reviewer_structural_failures", 0),
    )


def render_html(rows: list[dict]) -> str:
    ordered = sorted(rows, key=rank_key, reverse=True)
    complete = all(row.get("status") == "complete" for row in rows)
    best = ordered[0]["name"] if complete and ordered[0].get("automatic_gates_pass") else None
    body = []
    for row in ordered:
        body.append(
            "<tr>"
            f"<td>{escape(row['name'])}</td>"
            f"<td>{row.get('completed', 0)}/{row.get('total', 50)}</td>"
            f"<td>{row.get('valid_leader_panels', 0)}</td>"
            f"<td>{row.get('useful_leader_outputs', 0)}</td>"
            f"<td>{row.get('local_majority_agree', 0)}</td>"
            f"<td>{row.get('reviewer_structural_failures', 0)}</td>"
            f"<td>US$ {escape(str(row.get('cost_usd', '0')))}</td>"
            f"<td>{'pass' if row.get('automatic_gates_pass') else 'pending/fail'}</td>"
            "</tr>"
        )
    if best:
        decision = (
            f"Provisional metric winner: <strong>{escape(best)}</strong>. "
            "Promotion still requires manual inspection of changed cases and Studio validation."
        )
    elif complete:
        decision = (
            "All campaigns are complete, but no candidate passed every automatic gate. "
            "Inspect the paired case-by-case analysis before composing the next candidate."
        )
    else:
        decision = (
            "No candidate is eligible yet. Complete all campaigns and inspect changed cases "
            "before promotion."
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Mediare v21 comparison</title>
<style>body{{font:16px/1.5 Arial,sans-serif;color:#172235;max-width:1100px;margin:40px auto;padding:0 20px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #dce3ef;padding:10px;text-align:left}}th{{background:#eef3ff}}.callout{{margin:24px 0;padding:16px;border-left:5px solid #315efb;background:#eef3ff}}</style>
</head><body><h1>Mediare v21 OpenRouter candidate comparison</h1>
<p>All candidates use the same 50 cases, five-model rotation, reviewer quorum and cost accounting. Automatic gates are necessary but not sufficient.</p>
<table><thead><tr><th>Candidate</th><th>Completed</th><th>Valid leaders</th><th>Useful outputs</th><th>Local majorities</th><th>Structural failures</th><th>Cost</th><th>Gates</th></tr></thead><tbody>{''.join(body)}</tbody></table>
<div class="callout">{decision}</div>
<p><a href="V21_CASE_BY_CASE_ANALYSIS.html">Open the paired v20 × v21 analysis for all 50 cases.</a></p>
<p>Selection priority: safety gates, valid leader panels, useful outputs, local majorities, structural failures, then cost. Local majority is diagnostic and does not reproduce GenLayer consensus.</p>
</body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", default="V21_OPENROUTER_COMPARISON.json")
    parser.add_argument("--html", default="V21_OPENROUTER_COMPARISON.html")
    args = parser.parse_args()
    root = Path(args.root)
    rows = [candidate_metrics(root, name, path) for name, path in CANDIDATES.items()]
    Path(args.json).write_text(
        json.dumps({"candidates": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    Path(args.html).write_text(render_html(rows), encoding="utf-8")
    print(json.dumps({row["name"]: row["status"] for row in rows}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
