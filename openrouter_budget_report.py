#!/usr/bin/env python3
"""Build the single concise ledger for the US$500 OpenRouter grant.

The key-level cumulative usage is the accounting control total. Per-campaign
receipts are used only for attribution, so concurrent campaigns cannot be
double-counted.
"""

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from html import escape
import json
from pathlib import Path
import time
from zoneinfo import ZoneInfo

from openrouter_runner import OpenRouterClient, atomic_json, atomic_text, call_stats


PROGRAM_BUDGET_USD = Decimal("500")
DEFAULT_REPORT = "OPENROUTER_BUDGET_REPORT.html"
DEFAULT_SNAPSHOT = "res_openrouter_budget/account_snapshot.json"
INITIAL_VALIDATION_COST = Decimal("0.000006452")
HISTORICAL_ANTHROPIC_ESTIMATE_USD = Decimal("20")
V23_DEVELOPMENT_DIRS = (
    "res_openrouter_v23_0001_0050",
    "res_openrouter_v23_0_1_0001_0050",
    "res_openrouter_v23_0_2_0001_0050",
    "res_openrouter_v23_1_targeted",
    "res_openrouter_v23_1_gate",
    "res_openrouter_v23_1_remaining",
    "res_openrouter_v23_1_sentinels",
    "res_openrouter_v23_1_technical_retries",
)
V23_2_DEVELOPMENT_DIRS = (
    "res_openrouter_v23_2_technical_gate",
    "res_openrouter_v23_2_1_control_0048",
)


def as_decimal(value, default="0"):
    try:
        result = Decimal(str(default if value is None else value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)
    return result if result.is_finite() and result >= 0 else Decimal(default)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {} if default is None else default


def campaign_summary(root, directory):
    return read_json(Path(root) / directory / "summary.json")


def aggregate_call_receipts(root, directories):
    totals = {
        "api_calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
        "total_tokens": 0, "cost_usd": Decimal("0"), "completed": 0,
    }
    for directory in directories:
        path = Path(root) / directory
        stats = call_stats(path)
        totals["api_calls"] += int(stats.get("http_requests") or 0)
        totals["prompt_tokens"] += int(stats.get("prompt_tokens") or 0)
        totals["completion_tokens"] += int(stats.get("completion_tokens") or 0)
        totals["total_tokens"] += int(stats.get("total_tokens") or 0)
        totals["cost_usd"] += as_decimal(stats.get("cost_usd"))
        totals["completed"] += len(list((path / "results").glob("[0-9][0-9][0-9][0-9].json")))
    return totals


def latest_stored_account(root):
    candidates = []
    local = read_json(Path(root) / DEFAULT_SNAPSHOT)
    if local:
        candidates.append(local)
    for path in Path(root).glob("res_openrouter_*/campaign.json"):
        campaign = read_json(path)
        for key in ("account_latest", "account_start"):
            value = campaign.get(key)
            if isinstance(value, dict) and value.get("key_usage_usd") is not None:
                candidates.append(value)
    if not candidates:
        return {}
    return max(candidates, key=lambda row: as_decimal(row.get("key_usage_usd")))


def build_ledger(root, account=None):
    root = Path(root)
    account = account or latest_stored_account(root)
    v20 = campaign_summary(root, "res_openrouter_v20_0001_0050")
    schema = campaign_summary(root, "res_openrouter_v21_schema_0001_0050")
    catalog = campaign_summary(root, "res_openrouter_v21_catalog_0001_0050")
    options = campaign_summary(root, "res_openrouter_v21_options_0001_0050")
    v22 = campaign_summary(root, "res_openrouter_v22_0001_0050")
    v23 = aggregate_call_receipts(root, V23_DEVELOPMENT_DIRS)
    v23_2 = aggregate_call_receipts(root, V23_2_DEVELOPMENT_DIRS)
    pseudo = campaign_summary(root, "res_pseudonymization_0501_1000")
    pseudo_completed = int(pseudo.get("completed") or 0)
    pseudo_accepted = int(pseudo.get("accepted") or 0)
    pseudo_review = int(pseudo.get("needs_review") or 0)
    pseudo_state = str(pseudo.get("status") or "not started").replace("_", " ")
    if pseudo_completed:
        pseudo_state += f" — {pseudo_accepted} accepted; {pseudo_review} need review"

    def eval_row(label, summary, date, status=None, reconciled=False, target_override=None):
        completed = int(summary.get("completed") or 0)
        total = int(target_override if target_override is not None else (summary.get("total") or 50))
        cost_field = "cost_usd" if reconciled else "itemized_cost_usd"
        cost = as_decimal(summary.get(cost_field))
        if not cost and not reconciled:
            cost = as_decimal(summary.get("cost_usd"))
        return {
            "date": date,
            "activity": label,
            "tests": completed,
            "target": total,
            "calls": int(summary.get("api_calls") or 0),
            "tokens": int(summary.get("total_tokens") or 0),
            "cost": cost,
            "status": status or ("complete" if completed == total and total else "in progress"),
            "grant_scope": True,
        }

    rows = [
        {
            "date": "2026-08-22/09-08",
            "activity": "v1–v20 early experiments — Anthropic API",
            "tests": 0,
            "target": 0,
            "calls": None,
            "tokens": None,
            "cost": HISTORICAL_ANTHROPIC_ESTIMATE_USD,
            "status": "user estimate; Admin API verification unavailable",
            "grant_scope": False,
        },
        {
            "date": "2026-09-09",
            "activity": "Initial API-key validation",
            "tests": 0,
            "target": 0,
            "calls": 1,
            "tokens": None,
            "cost": INITIAL_VALIDATION_COST,
            "status": "complete",
            "grant_scope": True,
        },
        eval_row("v20 baseline", v20, "2026-09-09/10", reconciled=True),
        {
            "date": "2026-09-10",
            "activity": "Collection of 500 public decisions",
            "tests": 500,
            "target": 500,
            "calls": 0,
            "tokens": 0,
            "cost": Decimal("0"),
            "status": "complete — offline scraper",
            "grant_scope": True,
        },
        eval_row("v21-schema candidate", schema, "2026-09-10"),
        eval_row("v21-catalog candidate", catalog, "2026-09-10"),
        eval_row("v21-options candidate", options, "2026-09-10"),
        eval_row(
            "v22 hybrid sentinel", v22, "2026-09-11",
            status="complete — planned 20-case sentinel sample", target_override=20,
        ),
        {
            "date": "2026-09-11",
            "activity": "v23 catalog development, gates, and sentinel validation",
            "tests": v23["completed"],
            "target": v23["completed"],
            "calls": v23["api_calls"],
            "tokens": v23["total_tokens"],
            "cost": v23["cost_usd"],
            "status": "complete — gates passed; 20/20 sentinels; four technical retries included",
            "grant_scope": True,
        },
        {
            "date": "2026-09-11",
            "activity": "v23.2 technical hardening and controls",
            "tests": v23_2["completed"],
            "target": v23_2["completed"],
            "calls": v23_2["api_calls"],
            "tokens": v23_2["total_tokens"],
            "cost": v23_2["cost_usd"],
            "status": "complete — five-case gate plus clean 0048 control",
            "grant_scope": True,
        },
        {
            "date": "2026-09-10+",
            "activity": "Dual-model pseudonymization (IDs 0501–1000)",
            "tests": pseudo_completed,
            "target": int(pseudo.get("total") or 500),
            "calls": int(pseudo.get("api_calls") or 0),
            "tokens": int(pseudo.get("total_tokens") or 0),
            "cost": as_decimal(pseudo.get("cost_usd")),
            "status": pseudo_state,
            "grant_scope": True,
        },
    ]

    control_total = as_decimal(account.get("key_usage_usd"))
    attributed = sum((row["cost"] for row in rows if row["grant_scope"]), Decimal("0"))
    reconciliation = max(Decimal("0"), control_total - attributed)
    if reconciliation:
        rows.append({
            "date": "2026-09-09+",
            "activity": "API settlement and attribution reconciliation",
            "tests": 0,
            "target": 0,
            "calls": 0,
            "tokens": None,
            "cost": reconciliation,
            "status": "tracked — allocated as receipts settle",
            "grant_scope": True,
        })
    # If the latest stored account snapshot lags local receipts, keep the
    # report arithmetically honest and mark the control total as provisional.
    effective_total = max(control_total, attributed)
    remaining = max(Decimal("0"), PROGRAM_BUDGET_USD - effective_total)
    total_api_calls = sum(row["calls"] or 0 for row in rows)
    total_tokens = sum(row["tokens"] or 0 for row in rows)
    return {
        "rows": rows,
        "account": account,
        "control_total": control_total,
        "attributed": attributed,
        "reconciliation": reconciliation,
        "spent": effective_total,
        "remaining": remaining,
        "historical_external_estimate": HISTORICAL_ANTHROPIC_ESTIMATE_USD,
        "total_project_cost": effective_total + HISTORICAL_ANTHROPIC_ESTIMATE_USD,
        "total_openrouter_cost": effective_total,
        "total_api_calls": total_api_calls,
        "total_tokens": total_tokens,
        "snapshot_lag": attributed > control_total,
    }


def money(value, places=4):
    return "US$ " + f"{as_decimal(value):,.{places}f}"


def render_html(ledger):
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(ZoneInfo("America/Sao_Paulo"))
    spent = ledger["spent"]
    remaining = ledger["remaining"]
    pct = spent / PROGRAM_BUDGET_USD * 100
    account = ledger["account"]
    rows = []
    for row in ledger["rows"]:
        row_class = ' class="historical-external"' if not row["grant_scope"] else ""
        progress = "—" if not row["target"] else f"{row['tests']}/{row['target']}"
        tokens = "—" if row["tokens"] is None else f"{row['tokens']:,}"
        average = "—" if not row["tests"] or not row["cost"] else money(row["cost"] / row["tests"])
        rows.append(
            f"<tr{row_class}>"
            f"<td>{escape(row['date'])}</td>"
            f"<td>{escape(row['activity'])}</td>"
            f"<td>{progress}</td><td>{row['calls'] if row['calls'] is not None else '—'}</td>"
            f"<td>{tokens}</td>"
            f"<td>{money(row['cost'])}</td><td>{average}</td>"
            f"<td>{escape(row['status'])}</td>"
            "</tr>"
        )
    snapshot_note = (
        "The authenticated account snapshot is older than some local receipts; "
        "the larger locally itemized total is shown provisionally."
        if ledger["snapshot_lag"] else
        "The authenticated key-usage total is the accounting control total."
    )
    live_balance = account.get("account_available_balance_usd")
    live_text = money(live_balance) if live_balance is not None else "not available"
    captured = escape(str(account.get("captured_at") or "not available"))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mediare — OpenRouter US$500 Grant Ledger</title>
<style>
:root{{--ink:#172235;--muted:#607086;--blue:#315efb;--line:#dce3ef;--pale:#eef3ff;font-family:Inter,Arial,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:var(--ink);line-height:1.45}}main{{width:min(1120px,calc(100% - 28px));margin:28px auto;background:#fff;padding:44px 52px;box-shadow:0 8px 28px #17223512}}
h1{{margin:.15rem 0;font-size:2rem}}h2{{margin-top:32px;border-bottom:2px solid var(--line);padding-bottom:7px}}.eyebrow{{color:var(--blue);font-weight:700;text-transform:uppercase;letter-spacing:.07em}}.muted,footer{{color:var(--muted)}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}}.card{{border:1px solid var(--line);border-radius:10px;padding:16px}}.card strong{{display:block;font-size:1.55rem}}table{{width:100%;border-collapse:collapse;font-size:.92rem}}th,td{{border:1px solid var(--line);padding:9px;text-align:left;vertical-align:top}}th{{background:var(--pale)}}.historical-external td{{background:#fff4cc;color:#66510d}}tfoot td{{background:var(--pale);font-weight:700}}.note{{background:var(--pale);border-left:4px solid var(--blue);padding:13px 16px}}footer{{margin-top:34px;border-top:1px solid var(--line);padding-top:14px;font-size:.86rem}}@media(max-width:880px){{.cards{{grid-template-columns:1fr 1fr}}}}@media(max-width:720px){{main{{padding:28px 18px}}.cards{{grid-template-columns:1fr}}table{{display:block;overflow:auto}}}}@media print{{body{{background:#fff}}main{{margin:0;padding:0;width:auto;box-shadow:none}}}}
</style></head><body><main>
<div class="eyebrow">Consolidated cost report · GenLayer-sponsored OpenRouter budget</div>
<h1>US$500 Grant Ledger</h1>
<p class="muted">Updated {now_local:%Y-%m-%d %H:%M:%S} America/Sao_Paulo ({now_utc:%Y-%m-%d %H:%M:%S} UTC)</p>
<h2>How the project reached v20</h2>
<p>Mediare progressed from a first v1 prototype on 22 August 2026 to the v20 baseline through short empirical cycles: deploy or run the IC in GenLayer Studio, inspect consensus and operational failures, refine one bounded behavior, and retest. Early iterations also used direct Anthropic API calls; from v20 onward, the local OpenRouter runner added reproducible per-model diagnostics and cost receipts, while Studio remained the authority for real protocol consensus.</p>
<div class="cards"><div class="card">Authorized OpenRouter budget<strong>{money(PROGRAM_BUDGET_USD, 2)}</strong></div><div class="card">OpenRouter spent to date<strong>{money(spent)}</strong><span>{pct:.2f}% of budget</span></div><div class="card">OpenRouter budget remaining<strong>{money(remaining)}</strong></div><div class="card">Earlier Anthropic API cost<strong>{money(ledger['historical_external_estimate'], 2)}</strong><span>estimated, outside the grant</span></div></div>
<p class="note"><strong>Accounting rule.</strong> {escape(snapshot_note)} Campaign attribution uses per-call receipts, never overlapping campaign-level key deltas. Any difference is retained as reconciliation until OpenRouter settlement and local receipts align.</p>
<h2>Spend ledger</h2>
<table><thead><tr><th>Date</th><th>Version / activity</th><th>Completed</th><th>API calls</th><th>Tokens</th><th>Total cost</th><th>Cost per completed unit</th><th>Status</th></tr></thead><tbody>{''.join(rows)}</tbody><tfoot><tr><td colspan="3">TOTAL</td><td>{ledger['total_api_calls']:,}</td><td>{ledger['total_tokens']:,}</td><td>{money(ledger['total_openrouter_cost'])}</td><td>—</td><td>Total refers only to the US$500 OpenRouter budget; the US$20 pre-grant estimate is excluded</td></tr></tfoot></table>
<p class="muted">Account snapshot: {captured}. Live account cash balance: {live_text}. The account auto-top-up and the US$500 key authorization are different controls; this report measures consumption against the authorized US$500 project budget.</p>
<p class="muted">The earlier Anthropic amount is the user's approximate estimate for direct API experiments during v1–v20. An automated check was attempted on 10 September 2026, but the available OAuth session lacked Admin API access. Anthropic documents that organization cost reporting requires an Admin credential; the estimate can be replaced by a Console Usage CSV export. Estimated total project API cost including that pre-grant amount: <strong>{money(ledger['total_project_cost'])}</strong>.</p>
<h2>Current plan for the remaining budget</h2>
<table><thead><tr><th>Priority</th><th>Control</th></tr></thead><tbody>
<tr><td>Validate v23.2.1 on the 20 sentinels</td><td>The five-case technical gate passed; the next checkpoint measures regression risk on the frozen paired sample.</td></tr>
<tr><td>Preserve semantic and technical separation</td><td>Keep RP/CR rules frozen; track model availability, reviewer schema, and substantive objections as separate metrics.</td></tr>
<tr><td>Review the nine pseudonymized decisions held for inspection</td><td>No additional API cost unless a targeted repair is approved.</td></tr>
<tr><td>Reserve the unspent balance for holdouts, robustness and new cases</td><td>Every new paid campaign must have a persisted ceiling and appear in this same ledger.</td></tr>
</tbody></table>
<p>No cost is omitted because it is small or unsuccessful. Failed/billed calls and delayed settlement remain included through the key-level control total.</p>
<footer>Prepared for GenLayer. This file is the single consolidated OpenRouter grant-cost report and is regenerated as campaigns progress.</footer>
</main></body></html>"""


def refresh_account(root, api_key_file):
    key = Path(api_key_file).read_text(encoding="utf-8").strip()
    if not key:
        raise ValueError("OpenRouter API key file is empty")
    client = OpenRouterClient(key, provider={}, delay=0)
    snapshot = client.account_snapshot()
    atomic_json(Path(root) / DEFAULT_SNAPSHOT, snapshot)
    return snapshot


def render(root, output, api_key_file=None, refresh=False):
    account = None
    if refresh:
        if not api_key_file:
            raise ValueError("--api-key-file is required with --refresh-account")
        account = refresh_account(root, api_key_file)
    ledger = build_ledger(root, account)
    atomic_text(Path(root) / output, render_html(ledger))
    return ledger


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("render", "watch"), nargs="?", default="render")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=DEFAULT_REPORT)
    parser.add_argument("--api-key-file")
    parser.add_argument("--refresh-account", action="store_true")
    parser.add_argument("--interval", type=float, default=60)
    parser.add_argument("--account-interval", type=float, default=900)
    args = parser.parse_args(argv)
    if args.action == "render":
        ledger = render(args.root, args.output, args.api_key_file, args.refresh_account)
        print(json.dumps({"spent_usd": str(ledger["spent"]), "remaining_usd": str(ledger["remaining"])}))
        return 0
    if not args.api_key_file:
        parser.error("watch requires --api-key-file")
    last_account = 0.0
    while True:
        now = time.monotonic()
        refresh = now - last_account >= max(args.interval, args.account_interval)
        try:
            render(args.root, args.output, args.api_key_file, refresh)
            if refresh:
                last_account = now
        except Exception as exc:
            # Keep watching local receipts after a transient account-read error.
            render(args.root, args.output)
            print(f"budget report warning: {type(exc).__name__}", flush=True)
        time.sleep(max(15, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
