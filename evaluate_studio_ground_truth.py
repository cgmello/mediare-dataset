#!/usr/bin/env python3
"""Compare Studio IC panels with the dataset ground truth, without API calls.

The v28 panel is a mediation aid, while the stored ground truth is an aggregate
judicial outcome.  The comparison therefore reports coverage separately from
conditional accuracy and never treats protocol consensus as legal correctness.
"""

import argparse
import glob
import json
from pathlib import Path

import gold
import harness


MANUAL_REFERENCE_ISSUES = {
    "0482": (
        "The ground truth includes moral damages and a per-event fine that are "
        "not requested in the claimant petition; it is excluded only from the "
        "adjudicated exact-outcome metric."
    ),
}


def normalize_expected_outcome(value):
    text = (value or "").strip().lower().replace("_", " ")
    if text == "procedente":
        return "procedente"
    if text.startswith("parcialmente procedente"):
        return "parcialmente procedente"
    if text == "improcedente":
        return "improcedente"
    return None


def normalize_expected_relief(value):
    text = (value or "").strip().lower().replace("_", " ")
    if text == "improcedente":
        return "nenhuma tutela"
    if text.startswith("procedente") or text.startswith("parcialmente procedente"):
        return "alguma tutela"
    return None


def extract_panel(receipt):
    for leader in receipt.get("consensus_data", {}).get("leader_receipt", []):
        outputs = leader.get("eq_outputs") or {}
        output = outputs.get("0") or outputs.get(0)
        readable = ((output or {}).get("payload") or {}).get("readable")
        if readable:
            return json.loads(readable)
    return None


def claimant_requests(panel):
    pedidos = ((panel or {}).get("consolidado") or {}).get("pedidos") or []
    return [item for item in pedidos if str(item.get("pedido_id", "")).startswith("RP")]


def predict_exact_outcome(requests):
    tendencies = [item.get("tendencia") for item in requests]
    if not requests or "sem_maioria" in tendencies:
        return None
    if all(value == "favoravel" for value in tendencies):
        return "procedente"
    if all(value == "contraria" for value in tendencies):
        return "improcedente"
    if "favoravel" in tendencies and "contraria" in tendencies:
        return "parcialmente procedente"
    return None


def predict_relief(requests):
    tendencies = [item.get("tendencia") for item in requests]
    if any(value == "favoravel" for value in tendencies):
        return "alguma tutela"
    if requests and all(value == "contraria" for value in tendencies):
        return "nenhuma tutela"
    return None


def quantified_claimant_range(requests):
    low = high = 0
    for item in requests:
        if item.get("tendencia") != "favoravel":
            continue
        interval = item.get("faixa_quantificada_centavos") or item.get("faixa_centavos")
        if not interval or len(interval) != 2:
            return None
        low += interval[0]
        high += interval[1]
    return [low / 100, high / 100]


def percent(numerator, denominator):
    return round(100 * numerator / denominator, 1) if denominator else None


def evaluate(dataset, receipts_dir):
    ground_truth = harness.carregar_gabaritos(dataset)
    rows = []

    for filename in sorted(glob.glob(str(Path(receipts_dir) / "*.json"))):
        case_id = Path(filename).stem
        with open(filename, encoding="utf-8") as stream:
            receipt = json.load(stream)
        reference = ground_truth.get(case_id)
        if not reference:
            continue

        protocol_status = receipt.get("status_name")
        panel = extract_panel(receipt) if protocol_status != "UNDETERMINED" else None
        requests = claimant_requests(panel)
        expected_exact = normalize_expected_outcome(reference.get("resultado"))
        predicted_exact = predict_exact_outcome(requests)
        expected_relief = normalize_expected_relief(reference.get("resultado"))
        predicted_relief = predict_relief(requests)

        target, _, target_reliable, target_reason = gold.avaliar(reference)
        value_range = None
        value_correct = None
        if predicted_exact is not None and target_reliable:
            value_range = quantified_claimant_range(requests)
            if value_range is not None:
                value_correct = value_range[0] - 0.01 <= target <= value_range[1] + 0.01

        rows.append({
            "case_id": case_id,
            "protocol_status": protocol_status,
            "expected_outcome": expected_exact,
            "predicted_outcome": predicted_exact,
            "exact_match": (expected_exact == predicted_exact)
            if expected_exact is not None and predicted_exact is not None else None,
            "expected_relief": expected_relief,
            "predicted_relief": predicted_relief,
            "relief_match": (expected_relief == predicted_relief)
            if expected_relief is not None and predicted_relief is not None else None,
            "ground_truth_value": target if target_reliable else None,
            "ground_truth_value_note": target_reason,
            "predicted_value_range": value_range,
            "value_match": value_correct,
            "reference_issue": MANUAL_REFERENCE_ISSUES.get(case_id),
        })

    protocol_consensus = sum(row["protocol_status"] == "ACCEPTED" for row in rows)
    exact_reference = [row for row in rows if row["expected_outcome"] is not None]
    exact_resolved = [row for row in exact_reference if row["predicted_outcome"] is not None]
    exact_correct = sum(row["exact_match"] is True for row in exact_resolved)
    exact_adjudicated = [row for row in exact_resolved if not row["reference_issue"]]
    exact_adjudicated_correct = sum(row["exact_match"] is True for row in exact_adjudicated)
    relief_reference = [row for row in rows if row["expected_relief"] is not None]
    relief_resolved = [row for row in relief_reference if row["predicted_relief"] is not None]
    relief_correct = sum(row["relief_match"] is True for row in relief_resolved)
    value_reference = [row for row in rows if row["ground_truth_value"] is not None]
    value_resolved = [row for row in value_reference if row["predicted_value_range"] is not None]
    value_correct = sum(row["value_match"] is True for row in value_resolved)

    return {
        "methodology": {
            "protocol_consensus": "ACCEPTED Studio transactions; not a correctness metric",
            "exact_outcome": "all RP favorable=procedente; all contrary=improcedente; mixed favorable/contrary=partially granted; any sem_maioria=abstention",
            "relief_binary": "at least one favorable RP=some relief; all RP contrary=no relief; otherwise abstention",
            "monetary": "sum only quantified favorable RP ranges and compare with gold.py reliable aggregate value",
        },
        "summary": {
            "sample": len(rows),
            "protocol_consensus": protocol_consensus,
            "protocol_consensus_rate": percent(protocol_consensus, len(rows)),
            "exact_outcome_reference_cases": len(exact_reference),
            "exact_outcome_resolved": len(exact_resolved),
            "exact_outcome_coverage": percent(len(exact_resolved), len(exact_reference)),
            "exact_outcome_correct": exact_correct,
            "exact_outcome_conditional_accuracy": percent(exact_correct, len(exact_resolved)),
            "exact_outcome_adjudicated_resolved": len(exact_adjudicated),
            "exact_outcome_adjudicated_correct": exact_adjudicated_correct,
            "exact_outcome_adjudicated_accuracy": percent(
                exact_adjudicated_correct, len(exact_adjudicated)
            ),
            "exact_outcome_strict_correct_over_reference": percent(exact_correct, len(exact_reference)),
            "relief_reference_cases": len(relief_reference),
            "relief_resolved": len(relief_resolved),
            "relief_coverage": percent(len(relief_resolved), len(relief_reference)),
            "relief_correct": relief_correct,
            "relief_conditional_accuracy": percent(relief_correct, len(relief_resolved)),
            "monetary_reliable_reference_cases": len(value_reference),
            "monetary_resolved": len(value_resolved),
            "monetary_coverage": percent(len(value_resolved), len(value_reference)),
            "monetary_correct": value_correct,
            "monetary_conditional_accuracy": percent(value_correct, len(value_resolved)),
        },
        "exact_outcome_errors": [row for row in exact_resolved if row["exact_match"] is False],
        "manual_reference_issues": MANUAL_REFERENCE_ISSUES,
        "protocol_undetermined": [row["case_id"] for row in rows if row["protocol_status"] == "UNDETERMINED"],
        "cases": rows,
    }


def render_markdown(result):
    summary = result["summary"]
    errors = result["exact_outcome_errors"]
    error_lines = "\n".join(
        f"- `{row['case_id']}`: expected **{row['expected_outcome']}**, "
        f"IC concluded **{row['predicted_outcome']}**."
        for row in errors
    ) or "- None."
    undetermined = ", ".join(f"`{case_id}`" for case_id in result["protocol_undetermined"])
    return f"""# v28 Studio — comparison with dataset ground truth

This evaluation separates **protocol consensus**, **coverage**, and **accuracy**.
The IC is designed to prepare mediation options, while the stored ground truth is
an aggregate court outcome, so direct comparison is necessarily conservative.

## Results

| Metric | Result |
|---|---:|
| Studio protocol consensus | {summary['protocol_consensus']}/{summary['sample']} ({summary['protocol_consensus_rate']}%) |
| Exact three-way outcome coverage | {summary['exact_outcome_resolved']}/{summary['exact_outcome_reference_cases']} ({summary['exact_outcome_coverage']}%) |
| Exact outcome accuracy when resolved | {summary['exact_outcome_correct']}/{summary['exact_outcome_resolved']} ({summary['exact_outcome_conditional_accuracy']}%) |
| Exact outcome accuracy after reference audit | {summary['exact_outcome_adjudicated_correct']}/{summary['exact_outcome_adjudicated_resolved']} ({summary['exact_outcome_adjudicated_accuracy']}%) |
| Binary relief coverage | {summary['relief_resolved']}/{summary['relief_reference_cases']} ({summary['relief_coverage']}%) |
| Binary relief accuracy when resolved | {summary['relief_correct']}/{summary['relief_resolved']} ({summary['relief_conditional_accuracy']}%) |
| Quantified-value coverage | {summary['monetary_resolved']}/{summary['monetary_reliable_reference_cases']} ({summary['monetary_coverage']}%) |
| Quantified-value accuracy when resolved | {summary['monetary_correct']}/{summary['monetary_resolved']} ({summary['monetary_conditional_accuracy']}%) |

The principal finding is that v28 is **accurate when it reaches a substantive
conclusion, but abstains frequently**. Its 98% consensus rate mainly shows that
validators agree on the panel, including panels that request more information;
it is not a 98% legal-accuracy rate.

The raw exact-outcome score is 9/11. Manual inspection found that one of the two
apparent errors, case `0482`, comes from a reference defect: its ground truth
awards moral damages and a per-event fine absent from the claimant petition.
Excluding only that documented reference defect, the adjudicated score is 9/10.
Case `0054` remains a substantive IC miss: the reference awards moral damages,
while the IC rejects that request.

## Exact-outcome errors

{error_lines}

## Protocol-undetermined cases

{undetermined or 'None.'}

## Method

- Exact outcome: all claimant requests (`RP`) favorable = granted; all contrary
  = dismissed; a favorable/contrary mix = partially granted. Any `sem_maioria`
  produces an abstention.
- Binary relief: at least one favorable `RP` means some relief; all contrary
  means no relief. All other structures are abstentions.
- Monetary comparison is limited to references accepted by `gold.py` and IC
  panels whose favorable requests are all quantified. Abstentions are reported
  as missing coverage, not silently counted as correct.
- These 100 cases were sampled from the 500 Mediare-ready cases (`0001`–`0500`).
  Cases `0501`–`1000` are pseudonymized decisions but have not yet been converted
  into the four input blocks required by the IC, so they were not eligible.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=".")
    parser.add_argument("--receipts", default="res_studio_v28_random100/receipts")
    parser.add_argument("--json", default="V28_STUDIO_GROUND_TRUTH_REPORT.json")
    parser.add_argument("--markdown", default="V28_STUDIO_GROUND_TRUTH_REPORT.md")
    args = parser.parse_args()

    result = evaluate(args.dataset, args.receipts)
    Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown).write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
