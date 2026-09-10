#!/usr/bin/env python3
"""Executa as três campanhas v21 em sequência e para antes da promoção."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time


CAMPAIGNS = (
    ("schema", "res_openrouter_v21_schema_0001_0050", "OPENROUTER_V21_SCHEMA_REPORT.html"),
    ("catalog", "res_openrouter_v21_catalog_0001_0050", "OPENROUTER_V21_CATALOG_REPORT.html"),
    ("options", "res_openrouter_v21_options_0001_0050", "OPENROUTER_V21_OPTIONS_REPORT.html"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def completed(out: Path) -> bool:
    summary = read_json(out / "summary.json")
    return bool(summary and summary.get("completed") == summary.get("total") == 50)


def external_runner_active(out_name: str) -> bool:
    patterns = (
        f"openrouter_runner.py run --out {out_name}",
        f"openrouter_runner.py resume --out {out_name}",
    )
    for pattern in patterns:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            return True
    return False


def write_status(path: Path, **values) -> None:
    payload = {"updated_at": utc_now(), **values}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def ensure_itemized_cost_basis(out: Path) -> None:
    """Keep shared-key activity from contaminating a candidate's ceiling."""
    path = out / "campaign.json"
    manifest = read_json(path)
    if not manifest or manifest.get("cost_basis") == "itemized_receipts":
        return
    manifest["cost_basis"] = "itemized_receipts"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-key-file", default=".openrouter.key")
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--state-dir", default="res_v21_pipeline")
    args = parser.parse_args()
    if args.poll_seconds < 10:
        parser.error("--poll-seconds deve ser pelo menos 10")

    state = Path(args.state_dir)
    status_path = state / "status.json"
    log_path = state / "orchestrator.log"
    state.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as log:
        for name, out_name, report in CAMPAIGNS:
            out = Path(out_name)
            ensure_itemized_cost_basis(out)
            while not completed(out) and external_runner_active(out_name):
                summary = read_json(out / "summary.json")
                write_status(
                    status_path,
                    status="waiting_for_existing_runner",
                    candidate=name,
                    completed=summary.get("completed", 0),
                    total=50,
                )
                time.sleep(args.poll_seconds)

            if not completed(out):
                write_status(
                    status_path, status="running", candidate=name,
                    completed=read_json(out / "summary.json").get("completed", 0), total=50,
                )
                command = [
                    ".venv/bin/python", "-u", "openrouter_runner.py", "resume",
                    "--out", out_name,
                    "--report", report,
                    "--api-key-file", args.api_key_file,
                    "--timeout", "300",
                ]
                result = subprocess.run(command, stdout=log, stderr=log, check=False)
                log.flush()
                if result.returncode != 0 or not completed(out):
                    write_status(
                        status_path, status="failed", candidate=name,
                        exit_code=result.returncode,
                        completed=read_json(out / "summary.json").get("completed", 0), total=50,
                    )
                    return result.returncode or 2

            write_status(status_path, status="candidate_complete", candidate=name, completed=50, total=50)

        comparison = subprocess.run(
            [".venv/bin/python", "compare_v21.py"],
            stdout=log,
            stderr=log,
            check=False,
        )
        log.flush()
        if comparison.returncode != 0:
            write_status(status_path, status="comparison_failed", exit_code=comparison.returncode)
            return comparison.returncode
        write_status(
            status_path,
            status="awaiting_manual_selection",
            candidates_complete=3,
            next_step="inspect changed cases, choose candidate, then run Studio 0101-0150",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
