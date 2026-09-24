#!/usr/bin/env python3
"""Offline paired analysis of the v28 Studio baseline and v29 OpenRouter gate."""

import argparse
from collections import Counter
import json
from pathlib import Path

import harness
from evaluate_studio_ground_truth import (
    extract_panel,
    normalize_expected_outcome,
    normalize_expected_relief,
    predict_exact_outcome,
    predict_relief,
)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def requests(panel, claimant_only=False):
    values = ((panel or {}).get("consolidado") or {}).get("pedidos") or []
    if claimant_only:
        return [item for item in values if str(item.get("pedido_id", "")).startswith("RP")]
    return values


def direction(item):
    tendency = item.get("tendencia")
    return {
        "favoravel": "conceder",
        "contraria": "negar",
        "sem_maioria": "necessita_informacao",
    }.get(tendency, item.get("status"))


def expected_direction(audit):
    if audit["suficiencia_entrada"] == "indispensavel_ausente":
        return "necessita_informacao"
    return audit["direcao_segura"]


def percent(value, total):
    return round(100 * value / total, 1) if total else None


def analyze(args):
    manifest = read(args.selection)
    case_ids = manifest["case_ids"]
    group_sizes = manifest["groups"]
    boundaries = []
    cursor = 0
    for name, size in group_sizes.items():
        boundaries.append((name, set(case_ids[cursor:cursor + size])))
        cursor += size

    audit_rows = read(args.audit_rows)
    audits = {(row["case_id"], row["pedido_id"]): row for row in audit_rows}
    ground_truth = harness.carregar_gabaritos(args.dataset)
    rows = []
    reviewer_diagnostics = Counter()
    invalid_reasons = []
    audit_checks = []

    for case_id in case_ids:
        group = next(name for name, ids in boundaries if case_id in ids)
        result = read(Path(args.results) / f"{case_id}.json")
        receipt = read(Path(args.receipts) / f"{case_id}.json")
        baseline_panel = extract_panel(receipt)
        candidate_panel = result.get("leader_panel")
        baseline_requests = requests(baseline_panel)
        candidate_requests = requests(candidate_panel)
        baseline_by_id = {item["pedido_id"]: item for item in baseline_requests}
        candidate_by_id = {item["pedido_id"]: item for item in candidate_requests}

        for reviewer in result.get("reviewers") or []:
            reviewer_diagnostics[reviewer.get("diagnostic") or "UNKNOWN"] += 1
        if result.get("leader_error"):
            invalid_reasons.append({"case_id": case_id, "error": result["leader_error"]})

        for key, audit in audits.items():
            if key[0] != case_id:
                continue
            candidate = candidate_by_id.get(key[1])
            observed = direction(candidate) if candidate else "pedido_ausente"
            expected = expected_direction(audit)
            audit_checks.append({
                "case_id": case_id,
                "pedido_id": key[1],
                "group": group,
                "sufficiency": audit["suficiencia_entrada"],
                "expected": expected,
                "observed": observed,
                "match": expected == observed,
                "description": (candidate or baseline_by_id.get(key[1]) or {}).get("descricao"),
            })

        reference = ground_truth.get(case_id) or {}
        expected_exact = normalize_expected_outcome(reference.get("resultado"))
        expected_relief = normalize_expected_relief(reference.get("resultado"))
        base_rp = requests(baseline_panel, claimant_only=True)
        cand_rp = requests(candidate_panel, claimant_only=True)
        base_exact = predict_exact_outcome(base_rp)
        cand_exact = predict_exact_outcome(cand_rp)
        base_relief = predict_relief(base_rp)
        cand_relief = predict_relief(cand_rp)

        rows.append({
            "case_id": case_id,
            "group": group,
            "local_consensus": result.get("local_consensus"),
            "leader_valid": candidate_panel is not None,
            "leader_useful": bool((result.get("leader_impression") or {}).get("satisfatorio")),
            "reviewer_agree": result.get("reviewer_agree", 0),
            "reviewer_total": result.get("reviewer_total", 0),
            "baseline_request_count": len(baseline_requests),
            "candidate_request_count": len(candidate_requests),
            "baseline_unresolved": sum(direction(item) == "necessita_informacao" for item in baseline_requests),
            "candidate_unresolved": sum(direction(item) == "necessita_informacao" for item in candidate_requests),
            "catalog_ids_equal": set(baseline_by_id) == set(candidate_by_id),
            "expected_exact": expected_exact,
            "baseline_exact": base_exact,
            "candidate_exact": cand_exact,
            "baseline_exact_match": expected_exact == base_exact if expected_exact and base_exact else None,
            "candidate_exact_match": expected_exact == cand_exact if expected_exact and cand_exact else None,
            "expected_relief": expected_relief,
            "baseline_relief": base_relief,
            "candidate_relief": cand_relief,
            "baseline_relief_match": expected_relief == base_relief if expected_relief and base_relief else None,
            "candidate_relief_match": expected_relief == cand_relief if expected_relief and cand_relief else None,
        })

    group_summary = {}
    for name, ids in boundaries:
        selected = [row for row in rows if row["group"] == name]
        checks = [row for row in audit_checks if row["group"] == name]
        group_summary[name] = {
            "cases": len(selected),
            "local_majority_agree": sum(row["local_consensus"] == "LOCAL_MAJORITY_AGREE" for row in selected),
            "valid_leader_panels": sum(row["leader_valid"] for row in selected),
            "useful_leader_outputs": sum(row["leader_useful"] for row in selected),
            "baseline_unresolved": sum(row["baseline_unresolved"] for row in selected),
            "candidate_unresolved": sum(row["candidate_unresolved"] for row in selected),
            "audit_checks": len(checks),
            "audit_matches": sum(row["match"] for row in checks),
        }

    exact_base = [row for row in rows if row["baseline_exact_match"] is not None]
    exact_cand = [row for row in rows if row["candidate_exact_match"] is not None]
    relief_base = [row for row in rows if row["baseline_relief_match"] is not None]
    relief_cand = [row for row in rows if row["candidate_relief_match"] is not None]
    summary = {
        "cases": len(rows),
        "local_majority_agree": sum(row["local_consensus"] == "LOCAL_MAJORITY_AGREE" for row in rows),
        "valid_leader_panels": sum(row["leader_valid"] for row in rows),
        "useful_leader_outputs": sum(row["leader_useful"] for row in rows),
        "baseline_unresolved": sum(row["baseline_unresolved"] for row in rows),
        "candidate_unresolved": sum(row["candidate_unresolved"] for row in rows),
        "catalog_ids_equal_cases": sum(row["catalog_ids_equal"] for row in rows),
        "audit_checks": len(audit_checks),
        "audit_matches": sum(row["match"] for row in audit_checks),
        "audit_match_rate": percent(sum(row["match"] for row in audit_checks), len(audit_checks)),
        "exact_baseline": {"coverage": len(exact_base), "correct": sum(row["baseline_exact_match"] for row in exact_base)},
        "exact_candidate": {"coverage": len(exact_cand), "correct": sum(row["candidate_exact_match"] for row in exact_cand)},
        "relief_baseline": {"coverage": len(relief_base), "correct": sum(row["baseline_relief_match"] for row in relief_base)},
        "relief_candidate": {"coverage": len(relief_cand), "correct": sum(row["candidate_relief_match"] for row in relief_cand)},
        "reviewer_diagnostics": dict(reviewer_diagnostics),
        "invalid_panels": invalid_reasons,
        "groups": group_summary,
    }
    return {"summary": summary, "audit_checks": audit_checks, "cases": rows}


def render(result):
    summary = result["summary"]
    groups = summary["groups"]
    invalid = "\n".join(f"- `{row['case_id']}`: `{row['error']}`" for row in summary["invalid_panels"]) or "- None."
    mismatches = [row for row in result["audit_checks"] if not row["match"]]
    mismatch_lines = "\n".join(
        f"| {row['case_id']} | {row['pedido_id']} | {row['sufficiency']} | `{row['expected']}` | `{row['observed']}` |"
        for row in mismatches
    ) or "| — | — | — | — | — |"
    case_lines = "\n".join(
        f"| {row['case_id']} | {row['group']} | {row['local_consensus'].replace('LOCAL_MAJORITY_', '')} | "
        f"{'yes' if row['leader_valid'] else 'no'} | {'yes' if row['leader_useful'] else 'no'} | "
        f"{row['baseline_unresolved']} → {row['candidate_unresolved']} | "
        f"{row['baseline_exact'] or '—'} → {row['candidate_exact'] or '—'} |"
        for row in result["cases"]
    )
    group_lines = "\n".join(
        f"| {name} | {row['cases']} | {row['local_majority_agree']} | {row['valid_leader_panels']} | "
        f"{row['useful_leader_outputs']} | {row['baseline_unresolved']} → {row['candidate_unresolved']} | "
        f"{row['audit_matches']}/{row['audit_checks']} |"
        for name, row in groups.items()
    )
    return f"""# v29 OpenRouter gate — paired analysis against v28

This report compares the same 50 cases. The v28 baseline is the accepted Studio
panel; v29 is an off-chain five-model OpenRouter simulation and is not protocol
consensus. Ground truth is used only for post-run evaluation.

## Executive result

- Local majority: **{summary['local_majority_agree']}/{summary['cases']}**
- Structurally valid leader panels: **{summary['valid_leader_panels']}/{summary['cases']}**
- Operationally useful leader outputs: **{summary['useful_leader_outputs']}/{summary['cases']}**
- Requests left unresolved: **{summary['baseline_unresolved']} in v28 → {summary['candidate_unresolved']} in v29**
- Agreement with the independent abstention audit: **{summary['audit_matches']}/{summary['audit_checks']} ({summary['audit_match_rate']}%)**
- Catalog ID sets unchanged: **{summary['catalog_ids_equal_cases']}/{summary['cases']} cases**
- Exact-outcome resolved/correct: v28 **{summary['exact_baseline']['coverage']}/{summary['exact_baseline']['correct']}**, v29 **{summary['exact_candidate']['coverage']}/{summary['exact_candidate']['correct']}**
- Binary-relief resolved/correct: v28 **{summary['relief_baseline']['coverage']}/{summary['relief_baseline']['correct']}**, v29 **{summary['relief_candidate']['coverage']}/{summary['relief_candidate']['correct']}**

## Balanced groups

| Group | Cases | Agree | Valid | Useful | Unresolved v28 → v29 | Audit matches |
|---|---:|---:|---:|---:|---:|---:|
{group_lines}

## Invalid leader panels

{invalid}

## Audit mismatches requiring qualitative review

| Case | Request | Audit sufficiency | Expected | v29 observed |
|---:|---|---|---|---|
{mismatch_lines}

## Every case

| Case | Group | Vote | Valid | Useful | Unresolved v28 → v29 | Exact outcome v28 → v29 |
|---:|---|---|---|---|---:|---|
{case_lines}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=".")
    parser.add_argument("--selection", default="v29_gate50.json")
    parser.add_argument("--results", default="res_openrouter_v29_gate50/results")
    parser.add_argument("--receipts", default="res_studio_v28_random100/receipts")
    parser.add_argument("--audit-rows", default="res_openrouter_v28_abstention_audit/audit_rows.json")
    parser.add_argument("--json", default="V29_GATE50_ANALYSIS.json")
    parser.add_argument("--markdown", default="V29_GATE50_ANALYSIS.md")
    args = parser.parse_args()
    result = analyze(args)
    Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown).write_text(render(result), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
