#!/usr/bin/env python3
"""Run the frozen Mediare v20 committee locally through OpenRouter.

The runner reuses the exact prompts, parsing, normalization, repair, audit and
review functions from the deployed IC snapshot. It adds observability and model
control, but it does not reproduce or claim GenLayer protocol consensus.
"""

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from html import escape
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time

from studio_cycle import evaluate
from studio_phase2 import classify_success, load_case


DEFAULT_OUT = "res_openrouter_v20_0001_0050"
DEFAULT_REPORT = "OPENROUTER_V20_INVESTOR_REPORT.html"
DEFAULT_SOURCE = "res_canary_v20/20.0.0-experimental.py"
DEFAULT_SELECTION = "canary_v20.json"
DEFAULT_MODELS = "openrouter_models_v20.json"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY_URL = "https://openrouter.ai/api/v1/key"
OPENROUTER_CREDITS_URL = "https://openrouter.ai/api/v1/credits"
SCHEMA_VERSION = 1


class RunnerError(RuntimeError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".openrouter-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_json(path, value):
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def append_jsonl(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def safe_name(value):
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", value).strip("_")


def load_contract(path):
    source = Path(path).read_text(encoding="utf-8")
    marker = "class MediareCommitteeExperimental"
    if source.count(marker) != 1:
        raise RunnerError("source must contain exactly one MediareCommitteeExperimental class")
    prefix = source.split(marker, 1)[0].replace("from genlayer import *", "")
    # The prefix contains a guarded diagnostic helper that checks whether the
    # GenLayer module exists before printing a fixed code. A truthy sentinel
    # preserves that safe diagnostic locally without loading the contract SDK.
    namespace = {"gl": object()}
    exec(compile(prefix, str(path), "exec"), namespace)
    required = (
        "VERSAO", "_painel_de", "_revisao_de", "_revisor_aprova",
        "_render_termo_opcao", "_painel_valido",
    )
    missing = [name for name in required if name not in namespace]
    if missing:
        raise RunnerError("IC snapshot missing functions: " + ", ".join(missing))
    return namespace


def load_selection(path):
    value = read_json(path)
    ids = value.get("case_ids") if isinstance(value, dict) else value
    if (not isinstance(ids, list) or len(ids) != 50 or len(set(ids)) != 50
            or any(not isinstance(cid, str) or not re.fullmatch(r"\d{4}", cid) for cid in ids)):
        raise RunnerError("selection must contain exactly 50 unique four-digit case IDs")
    return ids


def load_models(path):
    value = read_json(path)
    models = value.get("models") if isinstance(value, dict) else None
    quorum = value.get("reviewer_quorum") if isinstance(value, dict) else None
    provider = value.get("provider") if isinstance(value, dict) else None
    model_options = value.get("model_options", {}) if isinstance(value, dict) else None
    if (not isinstance(models, list) or len(models) < 3 or len(set(models)) != len(models)
            or any(not isinstance(model, str) or "/" not in model for model in models)):
        raise RunnerError("model config must contain at least three unique OpenRouter slugs")
    if not isinstance(quorum, int) or not 1 <= quorum <= len(models) - 1:
        raise RunnerError("reviewer_quorum must fit the reviewer count")
    if not isinstance(provider, dict):
        raise RunnerError("model config must contain provider preferences")
    if not isinstance(model_options, dict) or any(
        model not in models or not isinstance(options, dict)
        for model, options in model_options.items()
    ):
        raise RunnerError("model_options must map configured models to objects")
    return models, quorum, provider, model_options


def key_from(args):
    value = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if args.api_key_file:
        value = Path(args.api_key_file).read_text(encoding="utf-8").strip()
    if not value:
        raise RunnerError(
            "OpenRouter key unavailable; set OPENROUTER_API_KEY or use --api-key-file"
        )
    return value


def decimal_cost(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise RunnerError("OpenRouter returned an invalid usage cost") from exc
    if not result.is_finite() or result < 0:
        raise RunnerError("OpenRouter returned an invalid usage cost")
    return result


class OpenRouterClient:
    def __init__(self, api_key, provider, model_options=None, delay=1.0, timeout=300):
        try:
            import requests
        except ImportError as exc:
            raise RunnerError("requests is required in the active Python environment") from exc
        self.requests = requests
        self.session = requests.Session()
        self.headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "X-OpenRouter-Title": "Mediare IC v20 local evaluation",
        }
        self.provider = provider
        self.model_options = model_options or {}
        self.delay = max(0.0, float(delay))
        self.timeout = timeout
        self.last_request = 0.0
        self.fatal_error = None
        self.last_error = None
        self.last_error_metadata = {}
        self.request_attempts = 0

    def _get_json(self, url):
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
        except Exception as exc:
            raise RunnerError("OPENROUTER_TRANSPORT_" + type(exc).__name__) from None
        if response.status_code >= 400:
            raise RunnerError("OPENROUTER_HTTP_" + str(response.status_code))
        try:
            value = response.json()
        except Exception:
            raise RunnerError("OPENROUTER_INVALID_JSON") from None
        return value.get("data") if isinstance(value, dict) else None

    def account_snapshot(self):
        """Return only non-secret aggregate limit and credit fields."""
        key = self._get_json(OPENROUTER_KEY_URL)
        credits = self._get_json(OPENROUTER_CREDITS_URL)
        if not isinstance(key, dict) or not isinstance(credits, dict):
            raise RunnerError("OPENROUTER_ACCOUNT_SCHEMA")
        total = decimal_cost(credits.get("total_credits"))
        usage = decimal_cost(credits.get("total_usage"))
        return {
            "captured_at": utc_now(),
            "key_limit_usd": str(key.get("limit")) if key.get("limit") is not None else None,
            "key_limit_remaining_usd": (
                str(key.get("limit_remaining"))
                if key.get("limit_remaining") is not None else None
            ),
            "key_usage_usd": str(key.get("usage")) if key.get("usage") is not None else None,
            "account_total_credits_usd": format(total, "f"),
            "account_total_usage_usd": format(usage, "f"),
            "account_available_balance_usd": format(max(Decimal("0"), total - usage), "f"),
        }

    def complete(self, model, prompt, max_tokens):
        self.last_error = None
        self.last_error_metadata = {}
        attempts_before = self.request_attempts
        request_started = time.monotonic()
        remaining = self.delay - (time.monotonic() - self.last_request)
        if remaining > 0:
            time.sleep(remaining)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "provider": self.provider,
        }
        payload.update(self.model_options.get(model, {}))
        last_code = None
        for attempt in range(4):
            started = time.monotonic()
            try:
                self.request_attempts += 1
                response = self.session.post(
                    OPENROUTER_URL, headers=self.headers, json=payload, timeout=self.timeout,
                )
                self.last_request = time.monotonic()
                last_code = response.status_code
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < 3:
                        time.sleep(min(2 ** attempt, 8))
                        continue
                    self.last_error = "OPENROUTER_HTTP_" + str(response.status_code)
                    raise RunnerError(self.last_error)
                if response.status_code >= 400:
                    error = "OPENROUTER_HTTP_" + str(response.status_code)
                    self.last_error = error
                    if response.status_code in (401, 402, 403):
                        self.fatal_error = error
                    raise RunnerError(error)
                body = response.json()
            except RunnerError:
                raise
            except Exception as exc:
                self.last_request = time.monotonic()
                if attempt < 3:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                self.last_error = "OPENROUTER_TRANSPORT_" + type(exc).__name__
                raise RunnerError(self.last_error) from None
            choices = body.get("choices") if isinstance(body, dict) else None
            message = choices[0].get("message") if isinstance(choices, list) and choices else None
            text = message.get("content") if isinstance(message, dict) else None
            usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
            metadata = {
                "request_id": str(body.get("id") or ""),
                "served_model": str(body.get("model") or model),
                "provider": str(body.get("provider") or "not_reported"),
                "prompt_tokens": int(usage.get("prompt_tokens") or 0),
                "completion_tokens": int(usage.get("completion_tokens") or 0),
                "total_tokens": int(usage.get("total_tokens") or 0),
                "cost_usd": (
                    format(decimal_cost(usage["cost"]), "f")
                    if usage.get("cost") is not None else "0"
                ),
            }
            if not isinstance(text, str) or not text.strip():
                self.last_error = "OPENROUTER_EMPTY_TEXT"
                self.last_error_metadata = metadata
                raise RunnerError(self.last_error)
            if usage.get("cost") is None:
                self.last_error = "OPENROUTER_COST_MISSING"
                self.last_error_metadata = metadata
                raise RunnerError(self.last_error)
            self.last_error = None
            return {
                "text": text,
                "request_id": metadata["request_id"],
                "requested_model": model,
                "served_model": metadata["served_model"],
                "provider": metadata["provider"],
                "prompt_tokens": metadata["prompt_tokens"],
                "completion_tokens": metadata["completion_tokens"],
                "total_tokens": metadata["total_tokens"],
                "cost_usd": metadata["cost_usd"],
                "duration_seconds": round(time.monotonic() - request_started, 3),
                "http_status": response.status_code,
                "http_attempts": self.request_attempts - attempts_before,
            }
        raise RunnerError("OPENROUTER_HTTP_" + str(last_code or "UNKNOWN"))


def total_cost(out):
    total = Decimal("0")
    count = 0
    for directory in ("calls", "call-errors"):
        for path in (Path(out) / directory).glob("*/*.jsonl"):
            for row in load_jsonl(path):
                total += decimal_cost(row.get("cost_usd", "0"))
                count += int(row.get("http_attempts") or 1)
    return total, count


def call_stats(out, case_id=None):
    root = Path(out) / "calls"
    paths = root.glob(f"{case_id}/*.jsonl") if case_id else root.glob("*/*.jsonl")
    rows = [row for path in paths for row in load_jsonl(path)]
    error_root = Path(out) / "call-errors"
    error_paths = (
        error_root.glob(f"{case_id}/*.jsonl") if case_id
        else error_root.glob("*/*.jsonl")
    )
    errors = [row for path in error_paths for row in load_jsonl(path)]
    completed = []
    started = []
    for row in rows + errors:
        try:
            end = datetime.fromisoformat(row["completed_at"].replace("Z", "+00:00"))
            completed.append(end)
            started.append(end.timestamp() - float(row.get("duration_seconds") or 0))
        except (KeyError, TypeError, ValueError):
            pass
    wall = 0.0
    if completed and started:
        wall = max(end.timestamp() for end in completed) - min(started)
    return {
        "successful_responses": len(rows),
        "failed_logical_calls": len(errors),
        "http_requests": (
            sum(int(row.get("http_attempts") or 1) for row in rows)
            + sum(int(row.get("http_attempts") or 1) for row in errors)
        ),
        "cost_usd": format(sum((decimal_cost(row.get("cost_usd", 0)) for row in rows + errors), Decimal("0")), "f"),
        "prompt_tokens": sum(int(row.get("prompt_tokens") or 0) for row in rows + errors),
        "completion_tokens": sum(int(row.get("completion_tokens") or 0) for row in rows + errors),
        "total_tokens": sum(int(row.get("total_tokens") or 0) for row in rows + errors),
        "api_duration_seconds": round(sum(float(row.get("duration_seconds") or 0) for row in rows + errors), 3),
        "wall_seconds": round(max(0.0, wall), 3),
    }


class ReplayCaller:
    def __init__(self, client, out, case_id, role, model, budget, max_tokens=10000):
        self.client = client
        self.out = Path(out)
        self.case_id = case_id
        self.role = role
        self.model = model
        self.budget = Decimal(str(budget))
        self.max_tokens = max_tokens
        self.path = self.out / "calls" / case_id / (safe_name(role + "-" + model) + ".jsonl")
        self.history = load_jsonl(self.path)
        self.index = 0

    def __call__(self, prompt, *, response_format=None):
        if response_format not in (None, "text"):
            raise RunnerError("UNSUPPORTED_RESPONSE_FORMAT")
        digest = sha256(prompt.encode("utf-8"))
        if self.index < len(self.history):
            row = self.history[self.index]
            if row.get("prompt_sha256") != digest or row.get("requested_model") != self.model:
                raise RunnerError("cached call does not match frozen prompt/model")
            text = (self.out / row["response_file"]).read_text(encoding="utf-8")
            self.index += 1
            return text
        spent, _ = total_cost(self.out)
        if spent >= self.budget:
            raise RunnerError("LOCAL_BUDGET_LIMIT_REACHED")
        attempts_before = self.client.request_attempts
        call_started = time.monotonic()
        try:
            result = self.client.complete(self.model, prompt, self.max_tokens)
        except RunnerError as exc:
            append_jsonl(
                self.out / "call-errors" / self.case_id
                / (safe_name(self.role + "-" + self.model) + ".jsonl"),
                {
                    "case_id": self.case_id,
                    "role": self.role,
                    "requested_model": self.model,
                    "prompt_sha256": digest,
                    "error_code": str(exc),
                    "http_attempts": self.client.request_attempts - attempts_before,
                    "duration_seconds": round(time.monotonic() - call_started, 3),
                    "completed_at": utc_now(),
                    **self.client.last_error_metadata,
                },
            )
            raise
        number = self.index + 1
        response_path = (
            self.out / "responses" / self.case_id
            / (safe_name(self.role + "-" + self.model) + f"-{number:02d}.txt")
        )
        atomic_text(response_path, result.pop("text"))
        row = {
            "case_id": self.case_id,
            "role": self.role,
            "call_number": number,
            "prompt_sha256": digest,
            "prompt_characters": len(prompt),
            "response_file": str(response_path.relative_to(self.out)),
            "completed_at": utc_now(),
            **result,
        }
        append_jsonl(self.path, row)
        self.history.append(row)
        self.index += 1
        return response_path.read_text(encoding="utf-8")


def diagnostic_from_stdout(text):
    found = re.findall(r"MEDIARE_DIAG:([A-Z0-9_]+)", text)
    return found[-1] if found else "REVIEWER_NO_DIAGNOSTIC"


def studio_baseline(dataset, case_id):
    path = Path(dataset) / "res_canary_v20" / "results" / (case_id + ".json")
    if not path.exists():
        return None
    value = read_json(path)
    transaction = value.get("transacao") or {}
    impression = value.get("impressao") or {}
    return {
        "consensus": transaction.get("result_name"),
        "label": impression.get("label"),
    }


def process_case(manifest, out, client, ic, dataset, case_id):
    position = manifest["case_ids"].index(case_id)
    models = manifest["models"]
    leader_model = models[position % len(models)]
    reviewer_models = [model for model in models if model != leader_model]
    case = load_case(dataset, case_id)
    body = json.dumps(case["documentos"], sort_keys=True, ensure_ascii=False)
    started = time.monotonic()
    leader = None
    leader_error = None
    try:
        leader_caller = ReplayCaller(
            client, out, case_id, "leader", leader_model,
            manifest["max_cost_usd"], manifest["max_tokens"],
        )
        leader = ic["_painel_de"](leader_caller, body)
        if not isinstance(leader, dict) or not ic["_painel_valido"](leader):
            raise RunnerError("LOCAL_LEADER_INVALID_PANEL")
    except Exception as exc:
        leader_error = str(exc)[:500] if isinstance(exc, (RunnerError, ValueError)) else type(exc).__name__
        if client.last_error:
            leader_error += "|client=" + client.last_error
    if client.fatal_error:
        raise RunnerError(client.fatal_error)
    spent_after_leader, _ = total_cost(out)
    if spent_after_leader >= Decimal(manifest["max_cost_usd"]):
        raise RunnerError("LOCAL_BUDGET_LIMIT_REACHED")

    reviews = []
    if leader is not None:
        for model in reviewer_models:
            try:
                caller = ReplayCaller(
                    client, out, case_id, "reviewer", model,
                    manifest["max_cost_usd"], manifest["max_tokens"],
                )
                review = ic["_revisao_de"](caller, body, leader)
                captured = io.StringIO()
                with redirect_stdout(captured):
                    approved = bool(ic["_revisor_aprova"](leader, review))
                reviews.append({
                    "model": model,
                    "vote": "agree" if approved else "disagree",
                    "diagnostic": diagnostic_from_stdout(captured.getvalue()),
                    "review": review,
                })
            except Exception as exc:
                diagnostic = str(exc)[:500] if isinstance(exc, (RunnerError, ValueError)) else type(exc).__name__
                if client.last_error:
                    diagnostic += "|client=" + client.last_error
                reviews.append({
                    "model": model,
                    "vote": "error",
                    "diagnostic": diagnostic,
                    "review": None,
                })
            if client.fatal_error:
                raise RunnerError(client.fatal_error)
            spent_after_review, _ = total_cost(out)
            if spent_after_review >= Decimal(manifest["max_cost_usd"]):
                raise RunnerError("LOCAL_BUDGET_LIMIT_REACHED")

    agree = sum(row["vote"] == "agree" for row in reviews)
    local_consensus = (
        "LOCAL_MAJORITY_AGREE"
        if leader is not None and agree >= manifest["reviewer_quorum"]
        else "LOCAL_MAJORITY_DISAGREE"
    )
    impression = None
    term = None
    if leader is not None:
        term = ic["_render_termo_opcao"](case_id, leader)
        state = {
            "case_id": case_id,
            "status": "termo_opcao_disponivel",
            "versao": manifest["version"],
            "painel": json.dumps(leader, ensure_ascii=False, sort_keys=True),
            "termo_opcao": term,
        }
        impression = classify_success(state, evaluate(state, manifest["version"], case_id))
    spent, call_count = total_cost(out)
    case_stats = call_stats(out, case_id)
    result = {
        "case_id": case_id,
        "origin": case.get("origem"),
        "category": case.get("categoria"),
        "leader_model": leader_model,
        "leader_error": leader_error,
        "leader_panel": leader,
        "leader_impression": impression,
        "reviewers": reviews,
        "reviewer_agree": agree,
        "reviewer_total": len(reviews),
        "reviewer_quorum": manifest["reviewer_quorum"],
        "local_consensus": local_consensus,
        "studio_baseline": studio_baseline(dataset, case_id),
        # This is active execution time for the current invocation. Historical
        # API latency remains in the immutable per-call metadata after a resume.
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "api_duration_seconds": case_stats["api_duration_seconds"],
        "case_cost_usd": case_stats["cost_usd"],
        "case_api_calls": case_stats["http_requests"],
        "prompt_tokens": case_stats["prompt_tokens"],
        "completion_tokens": case_stats["completion_tokens"],
        "total_tokens": case_stats["total_tokens"],
        "cumulative_cost_usd": format(spent, "f"),
        "cumulative_api_calls": call_count,
        "completed_at": utc_now(),
    }
    result_path = Path(out) / "results" / (case_id + ".json")
    atomic_json(result_path, result)
    if term is not None:
        atomic_text(Path(out) / "terms" / (case_id + ".md"), term)
    return result


def all_results(out):
    return [read_json(path) for path in sorted((Path(out) / "results").glob("[0-9][0-9][0-9][0-9].json"))]


def money(value):
    return "$" + f"{Decimal(str(value)):,.4f}"


def reconciled_campaign_cost(manifest, itemized):
    start = manifest.get("account_start") or {}
    latest = manifest.get("account_latest") or {}
    try:
        key_delta = (
            Decimal(str(latest["key_usage_usd"]))
            - Decimal(str(start["key_usage_usd"]))
        )
    except (KeyError, InvalidOperation, TypeError, ValueError):
        key_delta = Decimal("0")
    return max(Decimal(str(itemized)), key_delta, Decimal("0")), max(key_delta, Decimal("0"))


def render_report(manifest, out, report_path):
    results = all_results(out)
    itemized_spent, _ = total_cost(out)
    spent, key_usage_delta = reconciled_campaign_cost(manifest, itemized_spent)
    completed = len(results)
    total_seconds = sum(Decimal(str(row.get("elapsed_seconds") or 0)) for row in results)
    avg_cost = spent / completed if completed else Decimal("0")
    avg_time = total_seconds / completed if completed else Decimal("0")
    aggregate_calls = call_stats(out)
    calls = aggregate_calls["http_requests"]
    avg_http_cost = spent / calls if calls else Decimal("0")
    projected_50 = avg_cost * 50
    projected_500 = avg_cost * 500
    projected_remaining_campaign = avg_cost * (len(manifest["case_ids"]) - completed)
    budget = Decimal(str(manifest["program_credit_usd"]))
    remaining = max(Decimal("0"), budget - spent)
    local_agree = sum(row["local_consensus"] == "LOCAL_MAJORITY_AGREE" for row in results)
    leader_valid = sum(row.get("leader_error") is None for row in results)
    useful = sum(
        ((row.get("leader_impression") or {}).get("label") in {"APTO_INTEGRAL", "APTO_PARCIAL_COM_RETENCOES"})
        for row in results
    )
    comparable = [row for row in results if row.get("studio_baseline")]
    consensus_matches = sum(
        (row["local_consensus"] == "LOCAL_MAJORITY_AGREE")
        == (row["studio_baseline"].get("consensus") == "MAJORITY_AGREE")
        for row in comparable
    )
    label_matches = sum(
        (row.get("leader_impression") or {}).get("label") == row["studio_baseline"].get("label")
        for row in comparable
    )
    completed_word = (
        "Complete" if completed == len(manifest["case_ids"])
        else "Pilot checkpoint" if completed == 10
        else "In progress"
    )
    account_start = manifest.get("account_start") or {}
    account_end = manifest.get("account_latest") or account_start
    live_balance = Decimal(str(account_end.get("account_available_balance_usd", 0)))
    continuation_headroom = live_balance - projected_remaining_campaign
    allocations = [
        ("Targeted reproduction and v21 candidate development", Decimal("0.25")),
        ("Cross-model and repeated-run robustness checks", Decimal("0.25")),
        ("Regression testing across cases 0001–0100", Decimal("0.20")),
        ("Untouched holdouts beginning with cases 0101–0150", Decimal("0.15")),
        ("Adversarial, malformed-output and safety testing", Decimal("0.10")),
        ("Contingency for provider or model changes", Decimal("0.05")),
    ]

    def pct(numerator, denominator):
        return "—" if not denominator else f"{100 * numerator / denominator:.1f}%"

    rows = []
    for row in results:
        baseline = row.get("studio_baseline") or {}
        impression = row.get("leader_impression") or {}
        reviewer = f"{row['reviewer_agree']}/{row['reviewer_total']} agree"
        if row.get("leader_error"):
            observation = "No valid leader panel: " + str(row["leader_error"])
        else:
            exceptions = [
                f"{item['model']}: {item['diagnostic']}"
                for item in row.get("reviewers", []) if item.get("vote") != "agree"
            ]
            observation = (
                f"Valid {impression.get('label') or 'unclassified'} leader output; "
                f"{reviewer}."
                + (" Exceptions: " + "; ".join(exceptions) if exceptions else "")
            )
        rows.append(
            "<tr>"
            f"<td>{escape(row['case_id'])}</td><td>{escape(str(row.get('category') or '—'))}</td>"
            f"<td>{escape(row['leader_model'])}</td><td>{'valid' if not row.get('leader_error') else 'error'}</td>"
            f"<td>{escape(reviewer)}</td><td>{escape(row['local_consensus'])}</td>"
            f"<td>{escape(str(impression.get('label') or '—'))}</td>"
            f"<td>{escape(str(baseline.get('consensus') or '—'))}</td>"
            f"<td>{int(row.get('case_api_calls') or 0)}</td>"
            f"<td>{money(row.get('case_cost_usd') or 0)}</td>"
            f"<td>{float(row.get('elapsed_seconds') or 0):.1f}s</td>"
            f"<td>{escape(observation)}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="12">The OpenRouter campaign has not started yet.</td></tr>')
    model_rows = []
    for model in manifest["models"]:
        successful = []
        failed = []
        for path in (Path(out) / "calls").glob("*/*.jsonl"):
            successful.extend(row for row in load_jsonl(path) if row.get("requested_model") == model)
        for path in (Path(out) / "call-errors").glob("*/*.jsonl"):
            failed.extend(row for row in load_jsonl(path) if row.get("requested_model") == model)
        model_cost = sum(
            (decimal_cost(row.get("cost_usd", 0)) for row in successful + failed), Decimal("0")
        )
        model_requests = sum(int(row.get("http_attempts") or 1) for row in successful + failed)
        model_tokens = sum(int(row.get("total_tokens") or 0) for row in successful + failed)
        model_rows.append(
            f"<tr><td><code>{escape(model)}</code></td><td>{model_requests}</td>"
            f"<td>{len(successful)}</td><td>{len(failed)}</td><td>{model_tokens:,}</td>"
            f"<td>{money(model_cost)}</td></tr>"
        )
    allocation_rows = "".join(
        f"<tr><td>{escape(label)}</td><td>{share * 100:.0f}%</td><td>{money(remaining * share)}</td></tr>"
        for label, share in allocations
    )
    model_list = "".join(f"<li><code>{escape(model)}</code></li>" for model in manifest["models"])
    generated = utc_now()
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mediare v20 — OpenRouter Experimental Evaluation</title>
  <style>
    :root {{ --ink:#172235; --muted:#5b6778; --blue:#315efb; --pale:#eef3ff; --line:#dce3ef; font-family:Inter,Arial,sans-serif; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:#f3f6fa; color:var(--ink); line-height:1.55; }}
    main {{ width:min(1120px,calc(100% - 32px)); margin:32px auto; background:white; padding:56px 64px; box-shadow:0 10px 36px #17223512; }}
    h1 {{ font-size:2.15rem; line-height:1.14; margin:0 0 10px; }} h2 {{ margin-top:42px; border-bottom:2px solid var(--line); padding-bottom:8px; }}
    h3 {{ margin-top:28px; }} .eyebrow {{ color:var(--blue); font-weight:700; letter-spacing:.08em; text-transform:uppercase; }}
    .subtitle,.note {{ color:var(--muted); }} .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:24px 0; }}
    .card {{ border:1px solid var(--line); border-radius:10px; padding:18px; background:#fff; }} .card strong {{ display:block; font-size:1.55rem; }}
    table {{ width:100%; border-collapse:collapse; margin:18px 0; font-size:.91rem; }} th,td {{ border:1px solid var(--line); padding:9px 10px; text-align:left; vertical-align:top; }}
    th {{ background:var(--pale); }} code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em; }}
    .status {{ display:inline-block; border-radius:999px; padding:5px 11px; background:var(--pale); color:var(--blue); font-weight:700; }}
    .callout {{ border-left:5px solid var(--blue); background:var(--pale); padding:16px 20px; margin:22px 0; }}
    footer {{ margin-top:48px; padding-top:18px; border-top:1px solid var(--line); color:var(--muted); font-size:.88rem; }}
    @media(max-width:760px) {{ main {{ padding:32px 22px; }} .cards {{ grid-template-columns:1fr 1fr; }} table {{ display:block; overflow-x:auto; }} }}
    @media print {{ body {{ background:white; }} main {{ width:auto; margin:0; padding:0; box-shadow:none; }} }}
  </style>
</head>
<body><main>
  <div class="eyebrow">Investor technical report · GenLayer-sponsored API credit</div>
  <h1>Mediare v20: Local OpenRouter Evaluation and Studio Complementarity</h1>
  <p class="subtitle">Generated {escape(generated)} · Status: <span class="status">{completed_word} — {completed}/50 cases</span></p>

  <h2>Executive summary</h2>
  <p>GenLayer provided US$500 in OpenRouter API credits to expand the empirical evaluation of the Mediare Intelligent Contract. The local campaign does not replace Studio or claim protocol consensus. Its purpose is to expose intermediate model behavior that Studio correctly keeps outside chain state, accelerate controlled comparisons, and reserve Studio for authoritative protocol validation.</p>
  <div class="cards">
    <div class="card"><span>Cases completed</span><strong>{completed}/50</strong></div>
    <div class="card"><span>Actual API spend</span><strong>{money(spent)}</strong></div>
    <div class="card"><span>Average per case</span><strong>{money(avg_cost)}</strong></div>
    <div class="card"><span>Average wall time</span><strong>{float(avg_time):.1f}s</strong></div>
  </div>

  <h2>Why OpenRouter adds experimental value</h2>
  <p>Studio tests the real GenLayer execution environment: leader selection, validator voting, quorum, rotation, nondeterministic execution and final state commitment. That is indispensable. However, validators persist only an agree/disagree decision, not their private alternative panels or full review reasoning. A local runner can retain those intermediate artifacts and repeat controlled experiments.</p>
  <table>
    <thead><tr><th>Capability</th><th>GenLayer Studio</th><th>Local OpenRouter runner</th></tr></thead>
    <tbody>
      <tr><td>Real protocol consensus</td><td>Yes — authoritative</td><td>No — explicitly simulated</td></tr>
      <tr><td>Final leader panel</td><td>Available after accepted execution</td><td>Available for every valid leader run</td></tr>
      <tr><td>Panel/output produced by each model</td><td>Not persisted by the protocol</td><td>Retained locally for diagnosis</td></tr>
      <tr><td>Individual reviewer criteria</td><td>Vote only</td><td>Per-request booleans and failure code</td></tr>
      <tr><td>Raw response before parsing</td><td>Not available as campaign evidence</td><td>Stored locally with prompt hash</td></tr>
      <tr><td>Controlled v20/v21 A/B comparison</td><td>Slow and subject to validator allocation</td><td>Repeatable with a frozen model matrix</td></tr>
      <tr><td>Model and provider control</td><td>Studio policy set</td><td>Explicit OpenRouter model slugs and routing policy</td></tr>
      <tr><td>Token, latency and USD accounting</td><td>Partial execution telemetry; no campaign USD charge</td><td>Per API call and per case</td></tr>
      <tr><td>High-volume targeted experiments</td><td>Possible but operationally slow</td><td>Designed for resumable local iteration</td></tr>
    </tbody>
  </table>
  <div class="callout"><strong>Interpretation boundary:</strong> a local pass is evidence about prompt behavior and cross-model review stability. It is never evidence that GenLayer consensus will finalize the same proposal.</div>

  <h2>Methodology</h2>
  <p>The runner imports the exact v20 source snapshot (<code>{escape(manifest['source_sha256'])}</code>) and executes its own catalog, three lenses, validation, one-shot repair, consolidation, deterministic Term rendering, compact reviewer prompt and reviewer decision functions. Benchmark answers are not included in model prompts.</p>
  <p>One model leads each case in round-robin order; the other four review the same proposal. Local acceptance requires {manifest['reviewer_quorum']} reviewer approvals. Requests use free-form model output so that the same IC parser and correction loop are exercised; strict structured output is intentionally not used in the fidelity run. GLM 5.3 uses explicit low reasoning effort because its mandatory default maximum reasoning exhausted the completion budget during the pilot and returned billed responses without final text.</p>
  <ul>{model_list}</ul>
  <p>OpenRouter requests deny provider data collection where supported by routing policy. Each persisted call contains model identity, prompt hash, token counts, reported USD cost and latency. API credentials are never written to campaign logs.</p>

  <h2>Results and calibration</h2>
  <div class="cards">
    <div class="card"><span>Valid leader panels</span><strong>{leader_valid}/{completed}</strong></div>
    <div class="card"><span>Local majority agree</span><strong>{local_agree}/{completed}</strong></div>
    <div class="card"><span>Operationally useful leader outputs</span><strong>{useful}/{completed}</strong></div>
    <div class="card"><span>API calls</span><strong>{calls}</strong></div>
  </div>
  <p>Against the stored Studio v20 baseline, local consensus classification currently matches {consensus_matches}/{len(comparable)} cases ({pct(consensus_matches,len(comparable))}); the operational output label matches {label_matches}/{len(comparable)} ({pct(label_matches,len(comparable))}). These are calibration metrics, not legal-accuracy scores.</p>
  <div class="callout"><strong>Pilot reading:</strong> cases 0001–0006 matched the Studio consensus and operational class. Cases 0007–0008 produced useful leader options but failed the local reviewer quorum, exposing source and reviewer-schema concerns. Cases 0009–0010 failed during leader construction even though their stored Studio runs finalized successfully. This makes the local runner valuable as a diagnostic complement, while also demonstrating why it cannot substitute for protocol execution.</div>

  <h3>Per-case observations</h3>
  <table>
    <thead><tr><th>Case</th><th>Category</th><th>Leader</th><th>Panel</th><th>Reviewers</th><th>Local result</th><th>Local utility</th><th>Studio v20</th><th>HTTP calls</th><th>Cost</th><th>Time</th><th>Observation</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>

  <h3>Model-level telemetry</h3>
  <table>
    <thead><tr><th>Requested model</th><th>HTTP requests</th><th>Reusable responses</th><th>Failed logical calls</th><th>Itemized tokens</th><th>Itemized cost</th></tr></thead>
    <tbody>{''.join(model_rows)}</tbody>
  </table>

  <h2>Time and cost</h2>
  <p>The {completed} completed executions consumed {calls} HTTP model requests and {aggregate_calls['total_tokens']:,} itemized tokens ({aggregate_calls['prompt_tokens']:,} prompt and {aggregate_calls['completion_tokens']:,} completion), with {float(total_seconds):.1f} aggregate active case-seconds. Successful and metadata-bearing responses itemize {money(itemized_spent)}; the key-level usage delta is {money(key_usage_delta)}. The report conservatively uses the greater value, <strong>{money(spent)}</strong>, as actual campaign spend because providers may charge an empty response that has no reusable model text.</p>
  <p>The observed averages are <strong>{money(avg_cost)} per case</strong>, <strong>{money(avg_http_cost)} per HTTP request</strong>, and <strong>{float(avg_time):.1f} seconds per case</strong>. At the same model mix, the projected cost is {money(projected_50)} for 50 cases and {money(projected_500)} for 500 cases. These projections are directional: repair retries, provider routing and case complexity change token use.</p>
  <p>The remaining {len(manifest['case_ids']) - completed} cases in this 50-case campaign are projected to cost {money(projected_remaining_campaign)}. Against the current live account balance of {money(live_balance)}, this leaves projected headroom of {money(max(Decimal('0'), continuation_headroom))}{' and no immediate funding shortfall' if continuation_headroom >= 0 else ' with a projected funding shortfall of ' + money(-continuation_headroom)}.</p>

  <h2>Proposed use of the remaining GenLayer-sponsored credit</h2>
  <p>Announced program credit: {money(budget)}. Measured campaign spend: {money(spent)}. Planning balance against the announced grant: <strong>{money(remaining)}</strong>. This planning balance is not the same as the live account balance. The pilot campaign also has a separate persisted safety ceiling of {money(manifest.get('max_cost_usd', 0))}; increasing it requires an explicit decision after this checkpoint.</p>
  <p>At the latest authenticated snapshot, the API reported an account balance of <strong>{money(account_end.get('account_available_balance_usd', 0))}</strong>, from {money(account_end.get('account_total_credits_usd', 0))} in historical credits minus {money(account_end.get('account_total_usage_usd', 0))} in historical usage. The API key itself reported a remaining spending limit of {money(account_end.get('key_limit_remaining_usd', 0))}. A key limit controls authorization; it does not fund the account. Therefore, the allocation below is contingent on the sponsored balance being available or replenished.</p>
  <table><thead><tr><th>Experiment class</th><th>Share</th><th>Provisional allocation</th></tr></thead><tbody>{allocation_rows}</tbody></table>
  <p>Every future run should have a durable cost ceiling, stop after repeated authentication/provider failures, preserve a frozen IC and model configuration, and produce a comparable report. Studio confirmation remains mandatory before promoting any candidate IC version.</p>

  <h2>Limitations</h2>
  <ul>
    <li>OpenRouter models, provider endpoints and sampling may differ from Studio validator policies.</li>
    <li>The local reviewer quorum is an analytical convention, not a reconstruction of GenLayer consensus.</li>
    <li>Operational usefulness does not certify Brazilian-law correctness or fairness.</li>
    <li>Cases are summarized and anonymized; the evaluation cannot recover unavailable original evidence.</li>
    <li>The first 50 cases are calibration data. Later v21 validation must use untouched cases.</li>
  </ul>

  <h2>Sources</h2>
  <ul>
    <li><a href="https://openrouter.ai/docs/api_reference/overview">OpenRouter API reference</a></li>
    <li><a href="https://openrouter.ai/docs/guides/routing/provider-selection">OpenRouter provider routing</a></li>
    <li><a href="https://openrouter.ai/docs/guides/features/structured-outputs">OpenRouter structured outputs</a></li>
    <li><a href="https://openrouter.ai/docs/guides/best-practices/reasoning-tokens">OpenRouter reasoning-token controls</a></li>
    <li><a href="https://openrouter.ai/docs/api/api-reference/api-keys/get-current-key">OpenRouter current-key limits</a></li>
    <li><a href="https://openrouter.ai/docs/api/api-reference/credits/get-credits">OpenRouter account credits</a></li>
  </ul>
  <footer>Prepared for GenLayer as the sponsor of the US$500 OpenRouter evaluation credit. Mediare v20 remains experimental.</footer>
</main></body></html>
"""
    atomic_text(report_path, html)
    summary = {
        "updated_at": generated,
        "completed": completed,
        "total": len(manifest["case_ids"]),
        "api_calls": calls,
        "cost_usd": format(spent, "f"),
        "itemized_cost_usd": format(itemized_spent, "f"),
        "key_usage_delta_usd": format(key_usage_delta, "f"),
        "average_cost_usd": format(avg_cost, "f"),
        "average_time_seconds": float(avg_time),
        "prompt_tokens": aggregate_calls["prompt_tokens"],
        "completion_tokens": aggregate_calls["completion_tokens"],
        "total_tokens": aggregate_calls["total_tokens"],
        "local_majority_agree": local_agree,
        "valid_leader_panels": leader_valid,
        "useful_leader_outputs": useful,
        "studio_consensus_matches": consensus_matches,
        "studio_comparable": len(comparable),
    }
    atomic_json(Path(out) / "summary.json", summary)
    return summary


def initialize(args):
    out = Path(args.out)
    manifest_path = out / "campaign.json"
    if manifest_path.exists():
        raise RunnerError("campaign already initialized")
    source = Path(args.source).read_bytes()
    ic = load_contract(args.source)
    ids = load_selection(args.selection)
    models, quorum, provider, model_options = load_models(args.models)
    for cid in ids:
        load_case(args.dataset, cid)
    out.mkdir(parents=True, exist_ok=True)
    snapshot = out / "snapshot.py"
    atomic_text(snapshot, source.decode("utf-8"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "kind": "openrouter-local-simulation",
        "version": ic["VERSAO"],
        "source": str(Path(args.source)),
        "source_sha256": sha256(source),
        "dataset": str(Path(args.dataset).resolve()),
        "selection": str(Path(args.selection)),
        "case_ids": ids,
        "models": models,
        "reviewer_quorum": quorum,
        "provider": provider,
        "model_options": model_options,
        "max_cost_usd": format(Decimal(str(args.max_cost)), "f"),
        "program_credit_usd": format(Decimal(str(args.program_credit)), "f"),
        "max_tokens": args.max_tokens,
        "delay_seconds": args.delay,
        "started_at": utc_now(),
    }
    atomic_json(manifest_path, manifest)
    render_report(manifest, out, args.report)
    return manifest


def run_campaign(args):
    out = Path(args.out)
    manifest = read_json(out / "campaign.json")
    snapshot = out / "snapshot.py"
    if sha256(snapshot.read_bytes()) != manifest["source_sha256"]:
        raise RunnerError("frozen source snapshot changed")
    if args.max_cost is not None and Decimal(str(args.max_cost)) != Decimal(manifest["max_cost_usd"]):
        raise RunnerError("--max-cost differs from initialized campaign")
    ic = load_contract(snapshot)
    api_key = key_from(args)
    client = OpenRouterClient(
        api_key, manifest["provider"], manifest.get("model_options"),
        delay=manifest["delay_seconds"], timeout=args.timeout,
    )
    snapshot = client.account_snapshot()
    if "account_start" not in manifest:
        manifest["account_start"] = snapshot
    manifest["account_latest"] = snapshot
    atomic_json(out / "campaign.json", manifest)
    complete = {row["case_id"] for row in all_results(out)}
    run_completed = 0
    for case_id in manifest["case_ids"]:
        if case_id in complete:
            continue
        if args.case_limit is not None and run_completed >= args.case_limit:
            break
        itemized_spent, _ = total_cost(out)
        spent, _ = reconciled_campaign_cost(manifest, itemized_spent)
        if spent >= Decimal(manifest["max_cost_usd"]):
            raise RunnerError("LOCAL_BUDGET_LIMIT_REACHED")
        append_jsonl(out / "events.jsonl", {"event": "case_started", "case_id": case_id, "at": utc_now()})
        result = process_case(manifest, out, client, ic, manifest["dataset"], case_id)
        append_jsonl(out / "events.jsonl", {
            "event": "case_completed", "case_id": case_id,
            "local_consensus": result["local_consensus"], "at": utc_now(),
        })
        manifest["account_latest"] = client.account_snapshot()
        atomic_json(out / "campaign.json", manifest)
        summary = render_report(manifest, out, args.report)
        print(json.dumps({
            "case": case_id, "completed": summary["completed"],
            "cost_usd": summary["cost_usd"], "local_consensus": result["local_consensus"],
        }), flush=True)
        run_completed += 1
    manifest["account_latest"] = client.account_snapshot()
    atomic_json(out / "campaign.json", manifest)
    return render_report(manifest, out, args.report)


def raise_budget(args):
    if args.max_cost is None:
        raise RunnerError("set-budget requires --max-cost")
    out = Path(args.out)
    manifest_path = out / "campaign.json"
    manifest = read_json(manifest_path)
    previous = Decimal(str(manifest["max_cost_usd"]))
    requested = Decimal(str(args.max_cost))
    if requested <= previous:
        raise RunnerError("new budget must be greater than current budget")
    if requested > Decimal(str(manifest["program_credit_usd"])):
        raise RunnerError("new budget exceeds announced program credit")
    manifest["max_cost_usd"] = format(requested, "f")
    atomic_json(manifest_path, manifest)
    append_jsonl(out / "events.jsonl", {
        "event": "budget_raised",
        "previous_max_cost_usd": format(previous, "f"),
        "new_max_cost_usd": format(requested, "f"),
        "at": utc_now(),
    })
    return render_report(manifest, out, args.report)


def parser():
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument(
        "action", choices=("init", "run", "resume", "status", "report", "set-budget")
    )
    value.add_argument("--out", default=DEFAULT_OUT)
    value.add_argument("--source", default=DEFAULT_SOURCE)
    value.add_argument("--selection", default=DEFAULT_SELECTION)
    value.add_argument("--models", default=DEFAULT_MODELS)
    value.add_argument("--dataset", default=".")
    value.add_argument("--report", default=DEFAULT_REPORT)
    value.add_argument("--api-key-file")
    value.add_argument("--max-cost", type=Decimal, default=None)
    value.add_argument("--program-credit", type=Decimal, default=Decimal("500"))
    value.add_argument("--max-tokens", type=int, default=10000)
    value.add_argument("--delay", type=float, default=1.0)
    value.add_argument("--timeout", type=int, default=300)
    value.add_argument(
        "--case-limit", type=int,
        help="process at most this many new cases in the current invocation",
    )
    return value


def main(argv=None):
    args = parser().parse_args(argv)
    if args.max_cost is not None and args.max_cost <= 0:
        raise RunnerError("--max-cost must be positive")
    if args.case_limit is not None and args.case_limit <= 0:
        raise RunnerError("--case-limit must be positive")
    if args.action == "init":
        if args.max_cost is None:
            args.max_cost = Decimal("50")
        result = initialize(args)
    elif args.action in {"run", "resume"}:
        result = run_campaign(args)
    elif args.action == "set-budget":
        result = raise_budget(args)
    else:
        manifest = read_json(Path(args.out) / "campaign.json")
        result = render_report(manifest, args.out, args.report)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except RunnerError as exc:
        print("OPENROUTER_RUNNER_ERROR:" + str(exc), file=sys.stderr)
        raise SystemExit(2)
    except KeyboardInterrupt:
        print("OPENROUTER_RUNNER_INTERRUPTED", file=sys.stderr)
        raise SystemExit(130)
    except BaseException as exc:
        # Never print SDK/HTTP exception details: upstream metadata may contain secrets.
        print("OPENROUTER_RUNNER_UNEXPECTED:" + type(exc).__name__, file=sys.stderr)
        raise SystemExit(3)
