#!/usr/bin/env python3
"""Pseudonimiza decisões públicas com dois detectores LLM e aplicação local.

As LLMs identificam substrings; elas nunca reescrevem a decisão. O Python cria
IDs internos, iniciais, substituições, auditoria, cache retomável e orçamento.
Prompts e respostas com entidades permanecem somente sob uma pasta ``res_*``
ignorada pelo Git. Nada sensível é impresso no terminal.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import time

from openrouter_runner import OpenRouterClient, RunnerError, decimal_cost


SCHEMA_VERSION = 1
VALID_KINDS = {
    "person",
    "private_organization",
    "case_number",
    "document_identifier",
    "address",
    "email",
    "phone",
    "vehicle_identifier",
    "other_identifier",
}
PARTICLES = {"a", "as", "da", "das", "de", "do", "dos", "e"}
CASE_RE = re.compile(r"\b\d{7}[- ]?\d{2}\.\d{4}\.8\.26\.\d{4}\b")
CPF_RE = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
CNPJ_RE = re.compile(r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[- ]?\d{4}(?!\d)")
DATE_RE = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
ROLE_RE = re.compile(
    r"\b(Requerente|Requerido|Autor(?:a)?|Ré|Réu|Juíza? de Direito|Relator\(a\)):\s*"
    r"([^\n:]{3,160}?)(?=\s+(?:Requerente|Requerido|Autor(?:a)?|Ré|Réu|Juíza? de Direito|"
    r"Justiça Gratuita|VISTOS?\.?|Classe\s*-\s*Assunto)\b|\n|$)",
    re.I,
)


DETECT_PROMPT = """You are a high-recall privacy entity detector for a Brazilian court decision.
Return exactly one JSON object and no prose:
{"entities":[{"text":"exact substring copied from INPUT","kind":"person|private_organization|case_number|document_identifier|address|email|phone|vehicle_identifier|other_identifier"}]}

Find every identifying substring belonging to the current dispute, including:
- names of natural persons: parties, judges, lawyers, experts, witnesses and professionals;
- names or trade names of private companies and associations;
- every judicial case number, CPF, CNPJ, RG, professional registration, email,
  phone, street address, vehicle plate, bank/account identifier or similar ID.

Rules:
- Copy each value exactly as it occurs. Do not invent, normalize or rewrite it.
- Include repeated entities once; include both an abbreviated name and its full form if both occur.
- Do not mark monetary values, dates, statutes, generic roles, court names, city,
  comarca, foro or vara merely because they are specific.
- Public institutions such as TJSP, STJ, IMESC and a named court are not private organizations.
- When uncertain whether a named natural person or private entity identifies someone, include it.

INPUT JSON:
<<INPUT>>
"""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def append_jsonl(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def initials(value: str) -> str:
    words = re.findall(r"[^\W\d_]+", value, flags=re.UNICODE)
    kept = [word for word in words if word.casefold() not in PARTICLES]
    return "".join(word[0].upper() + "." for word in kept)


def clean_date(value: object) -> object:
    if not isinstance(value, str):
        return value
    match = DATE_RE.search(value)
    return match.group(0) if match else value[:40]


def load_source(path: Path, start_line: int, count: int) -> list[tuple[int, dict]]:
    selected = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if line_number < start_line:
                continue
            if len(selected) >= count:
                break
            value = json.loads(line)
            if not isinstance(value, dict) or not isinstance(value.get("texto"), str):
                raise RunnerError("SOURCE_RECORD_INVALID")
            selected.append((line_number, value))
    if len(selected) != count:
        raise RunnerError("SOURCE_RANGE_INCOMPLETE")
    return selected


def source_digest(rows: list[tuple[int, dict]]) -> str:
    canonical = "\n".join(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for _, value in rows
    )
    return sha256_bytes(canonical.encode("utf-8"))


def _parse_detector(value: str, source: str, drop_invalid: bool) -> tuple[list[dict[str, str]], int]:
    stripped = value.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped, flags=re.I)
    try:
        root = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise RunnerError("DETECTOR_JSON_INVALID") from exc
    if not isinstance(root, dict) or set(root) != {"entities"} or not isinstance(root["entities"], list):
        raise RunnerError("DETECTOR_SCHEMA_INVALID")
    result = []
    seen = set()
    dropped = 0
    for item in root["entities"]:
        if not isinstance(item, dict) or set(item) != {"text", "kind"}:
            if drop_invalid:
                dropped += 1
                continue
            raise RunnerError("DETECTOR_ENTITY_INVALID")
        text = item["text"]
        kind = item["kind"]
        if (
            not isinstance(text, str) or not 2 <= len(text) <= 300
            or not isinstance(kind, str) or kind not in VALID_KINDS
            or text.casefold() not in source.casefold()
        ):
            if drop_invalid:
                dropped += 1
                continue
            raise RunnerError("DETECTOR_ENTITY_INVALID")
        key = (text.casefold(), kind)
        if key not in seen:
            seen.add(key)
            result.append({"text": text, "kind": kind})
    return result, dropped


def parse_detector(value: str, source: str) -> list[dict[str, str]]:
    return _parse_detector(value, source, False)[0]


def local_entities(record: dict) -> list[dict[str, str]]:
    result = []
    process = record.get("processo")
    magistrate = record.get("magistrado")
    if isinstance(process, str) and process:
        result.append({"text": process, "kind": "case_number"})
    if isinstance(magistrate, str) and magistrate:
        result.append({"text": magistrate, "kind": "person"})
    text = record.get("texto", "")
    for match in ROLE_RE.finditer(text):
        candidate = match.group(2).strip(" .,;-")
        if 2 <= len(candidate) <= 160:
            kind = "private_organization" if re.search(
                r"\b(LTDA|S/?A|EIRELI|CL[IÍ]NICA|EMPRESA|ASSOCIA[CÇ][AÃ]O)\b", candidate, re.I
            ) else "person"
            result.append({"text": candidate, "kind": kind})
    for pattern, kind in (
        (CASE_RE, "case_number"), (CPF_RE, "document_identifier"),
        (CNPJ_RE, "document_identifier"), (EMAIL_RE, "email"), (PHONE_RE, "phone"),
    ):
        for match in pattern.finditer(text):
            result.append({"text": match.group(0), "kind": kind})
    return result


def merged_entities(groups: list[list[dict[str, str]]]) -> list[dict[str, str]]:
    by_text: dict[str, dict[str, str]] = {}
    priority = {"case_number": 9, "document_identifier": 8, "email": 8, "phone": 8,
                "vehicle_identifier": 8, "address": 7, "person": 6,
                "private_organization": 5, "other_identifier": 4}
    for group in groups:
        for item in group:
            key = item["text"].casefold()
            previous = by_text.get(key)
            if previous is None or priority[item["kind"]] > priority[previous["kind"]]:
                by_text[key] = item
    return sorted(by_text.values(), key=lambda item: (-len(item["text"]), item["text"].casefold()))


def replacement_map(entities: list[dict[str, str]], original_process: str, internal_id: str) -> list[dict]:
    precedent = 0
    result = []
    for item in entities:
        text, kind = item["text"], item["kind"]
        if kind == "case_number":
            if re.sub(r"\D", "", text) == re.sub(r"\D", "", original_process):
                replacement = internal_id
            else:
                precedent += 1
                replacement = f"PRECEDENTE-{precedent:03d}"
        elif kind in {"person", "private_organization"}:
            replacement = initials(text)
            if len(replacement) < 2:
                replacement = "[ENTIDADE]"
        else:
            replacement = "[DADO_REMOVIDO]"
        result.append({**item, "replacement": replacement})
    return result


def replace_all(value: str, replacements: list[dict]) -> str:
    result = value
    for item in replacements:
        result = re.sub(re.escape(item["text"]), lambda _: item["replacement"], result, flags=re.I)
    # Fail-safe deterministic sweep for identifiers both models may have missed.
    result = CASE_RE.sub("PRECEDENTE-REMOVIDO", result)
    result = CPF_RE.sub("[DADO_REMOVIDO]", result)
    result = CNPJ_RE.sub("[DADO_REMOVIDO]", result)
    result = EMAIL_RE.sub("[DADO_REMOVIDO]", result)
    return result


def detector_agreement(first: list[dict], second: list[dict]) -> float:
    a = {item["text"].casefold() for item in first}
    b = {item["text"].casefold() for item in second}
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def audit_output(record: dict, original: dict, replacements: list[dict]) -> list[str]:
    combined = "\n".join(str(record.get(field, "")) for field in ("processo", "magistrado", "texto"))
    failures = []
    if CASE_RE.search(combined):
        failures.append("CASE_NUMBER_REMAINED")
    if CPF_RE.search(combined) or CNPJ_RE.search(combined) or EMAIL_RE.search(combined):
        failures.append("DIRECT_IDENTIFIER_REMAINED")
    for item in replacements:
        if len(item["text"]) >= 4 and item["text"].casefold() in combined.casefold():
            failures.append("DETECTED_ENTITY_REMAINED")
            break
    if record.get("processo") == original.get("processo"):
        failures.append("INTERNAL_ID_NOT_APPLIED")
    return sorted(set(failures))


def safe_slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", model)


def cached_detection(client, out: Path, internal_id: str, model: str, prompt: str, max_tokens: int, source: str):
    cache_path = out / "cache" / internal_id / (safe_slug(model) + ".json")
    prompt_hash = sha256_bytes(prompt.encode("utf-8"))
    if cache_path.exists():
        cached = read_json(cache_path)
        if cached.get("prompt_sha256") != prompt_hash:
            raise RunnerError("CACHE_PROMPT_CHANGED")
        return cached["entities"], cached["metadata"]
    active_prompt = prompt
    for attempt in range(1, 4):
        response = client.complete(model, active_prompt, max_tokens)
        raw = response.pop("text")
        try:
            entities = parse_detector(raw, source)
        except RunnerError as exc:
            if attempt == 3 and str(exc) == "DETECTOR_ENTITY_INVALID":
                # A syntactically valid detector response may contain one
                # normalized or hallucinated entity among otherwise exact
                # substrings. Keep only exact entities, flag the record for
                # human review, and let the independent detector plus local
                # deterministic sweep protect the output.
                entities, dropped = _parse_detector(raw, source, True)
                response["detector_partial"] = True
                response["invalid_entities_dropped"] = dropped
                payload = {"prompt_sha256": prompt_hash, "entities": entities, "metadata": response}
                atomic_json(cache_path, payload)
                return entities, response
            append_jsonl(
                out / "call-errors" / internal_id / (safe_slug(model) + ".jsonl"),
                {
                    "attempt": attempt,
                    "error": str(exc),
                    "metadata": response,
                    "response_sha256": sha256_bytes(raw.encode("utf-8")),
                },
            )
            if attempt == 3:
                raise
            active_prompt = prompt + (
                "\nCORRECTION: Your prior response did not satisfy the exact JSON schema. "
                "Return only the required object, with exact substrings from INPUT."
            )
            continue
        payload = {"prompt_sha256": prompt_hash, "entities": entities, "metadata": response}
        atomic_json(cache_path, payload)
        return entities, response
    raise RunnerError("DETECTOR_RETRY_EXHAUSTED")


def total_cost(out: Path) -> Decimal:
    cost = Decimal("0")
    for path in (out / "cache").glob("*/*.json"):
        cost += decimal_cost(read_json(path).get("metadata", {}).get("cost_usd", 0))
    for path in (out / "call-errors").glob("*/*.jsonl"):
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                value = json.loads(line)
                cost += decimal_cost(value.get("metadata", {}).get("cost_usd", 0))
    return cost


def total_calls(out: Path) -> int:
    calls = 0
    for path in (out / "cache").glob("*/*.json"):
        calls += int(read_json(path).get("metadata", {}).get("http_attempts") or 1)
    for path in (out / "call-errors").glob("*/*.jsonl"):
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                value = json.loads(line)
                calls += int(value.get("metadata", {}).get("http_attempts") or 1)
    return calls


def rebuild_jsonl(out: Path) -> None:
    rows = []
    for path in sorted((out / "results").glob("*.json")):
        value = read_json(path)
        if value.get("status") == "accepted":
            rows.append(json.dumps(value["record"], ensure_ascii=False, sort_keys=True))
    target = out / "pseudonymized.jsonl"
    temporary = target.with_suffix(".tmp")
    temporary.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    temporary.replace(target)


def initialize(args) -> dict:
    out = Path(args.out)
    if (out / "campaign.json").exists():
        raise RunnerError("CAMPAIGN_ALREADY_INITIALIZED")
    source_path = Path(args.input)
    rows = load_source(source_path, args.start_line, args.count)
    config = read_json(Path(args.models))
    models = config.get("models")
    provider = config.get("provider")
    if not isinstance(models, list) or len(models) != 2 or len(set(models)) != 2:
        raise RunnerError("MODEL_CONFIG_INVALID")
    if not isinstance(provider, dict) or provider.get("zdr") is not True or provider.get("data_collection") != "deny":
        raise RunnerError("PRIVACY_CONFIG_INVALID")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "initialized",
        "input": str(source_path.resolve()),
        "input_digest": source_digest(rows),
        "start_line": args.start_line,
        "count": args.count,
        "first_internal_id": args.first_id,
        "models": models,
        "provider": provider,
        "max_tokens": int(config.get("max_tokens") or 3500),
        "max_cost_usd": format(args.max_cost, "f"),
        "created_at": int(time.time()),
    }
    out.mkdir(parents=True, exist_ok=True)
    atomic_json(out / "campaign.json", manifest)
    atomic_json(out / "id_map.json", {"mapping": {}})
    return manifest


def status(out: Path) -> dict:
    manifest = read_json(out / "campaign.json")
    results = [read_json(path) for path in (out / "results").glob("*.json")]
    value = {
        "status": "complete" if len(results) == manifest["count"] else "in_progress",
        "completed": len(results),
        "accepted": sum(row.get("status") == "accepted" for row in results),
        "needs_review": sum(row.get("status") == "needs_review" for row in results),
        "total": manifest["count"],
        "api_calls": total_calls(out),
        "cost_usd": format(total_cost(out), "f"),
    }
    atomic_json(out / "summary.json", value)
    return value


def run(args) -> dict:
    out = Path(args.out)
    manifest = read_json(out / "campaign.json")
    rows = load_source(Path(manifest["input"]), manifest["start_line"], manifest["count"])
    if source_digest(rows) != manifest["input_digest"]:
        raise RunnerError("SOURCE_CHANGED")
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if args.api_key_file:
        key = Path(args.api_key_file).read_text(encoding="utf-8").strip()
    if not key:
        raise RunnerError("OPENROUTER_KEY_UNAVAILABLE")
    client = OpenRouterClient(
        key, manifest["provider"], delay=args.delay, timeout=args.timeout,
        evaluation_title="Mediare public-decision pseudonymization",
    )
    id_map_path = out / "id_map.json"
    id_map = read_json(id_map_path)
    completed = {path.stem for path in (out / "results").glob("*.json")}
    processed_now = 0
    for offset, (_, original) in enumerate(rows):
        internal_id = f"{manifest['first_internal_id'] + offset:04d}"
        if internal_id in completed:
            continue
        if args.case_limit is not None and processed_now >= args.case_limit:
            break
        if total_cost(out) >= Decimal(manifest["max_cost_usd"]):
            raise RunnerError("LOCAL_BUDGET_LIMIT_REACHED")
        source = json.dumps(original, ensure_ascii=False, sort_keys=True)
        prompt = DETECT_PROMPT.replace("<<INPUT>>", source)
        detections = []
        metadata = []
        for model in manifest["models"]:
            entities, call = cached_detection(
                client, out, internal_id, model, prompt, manifest["max_tokens"], source
            )
            detections.append(entities)
            metadata.append(call)
        entities = merged_entities([local_entities(original), *detections])
        original_process = str(original.get("processo") or "")
        replacements = replacement_map(entities, original_process, internal_id)
        record = dict(original)
        record["processo"] = internal_id
        record["data"] = clean_date(record.get("data"))
        if isinstance(record.get("magistrado"), str):
            record["magistrado"] = replace_all(record["magistrado"], replacements)
        record["texto"] = replace_all(record["texto"], replacements)
        failures = audit_output(record, original, replacements)
        if any(call.get("detector_partial") for call in metadata):
            failures.append("DETECTOR_PARTIAL_OUTPUT")
        agreement = detector_agreement(detections[0], detections[1])
        state = "accepted" if not failures else "needs_review"
        record["pseudonimizacao"] = {
            "versao": SCHEMA_VERSION,
            "id_interno": internal_id,
            "modelos": manifest["models"],
            "entidades_substituidas": len(replacements),
            "concordancia_detectores": round(agreement, 4),
            "status": state,
        }
        atomic_json(out / "results" / (internal_id + ".json"), {
            "status": state,
            "audit_failures": failures,
            "record": record,
            "replacement_count": len(replacements),
            "model_entity_counts": [len(group) for group in detections],
            "model_metadata": metadata,
        })
        id_map["mapping"][original_process] = internal_id
        atomic_json(id_map_path, id_map)
        rebuild_jsonl(out)
        current = status(out)
        print(json.dumps({
            "internal_id": internal_id,
            "completed": current["completed"],
            "status": state,
            "cost_usd": current["cost_usd"],
        }), flush=True)
        processed_now += 1
    return status(out)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("action", choices=("init", "run", "resume", "status"))
    value.add_argument("--input", default="sentencas.jsonl")
    value.add_argument("--start-line", type=int, default=245)
    value.add_argument("--count", type=int, default=500)
    value.add_argument("--first-id", type=int, default=501)
    value.add_argument("--out", default="res_pseudonymization_0501_1000")
    value.add_argument("--models", default="pseudonymization_models.json")
    value.add_argument("--api-key-file")
    value.add_argument("--max-cost", type=Decimal, default=Decimal("30"))
    value.add_argument("--case-limit", type=int)
    value.add_argument("--delay", type=float, default=1.0)
    value.add_argument("--timeout", type=int, default=300)
    return value


def main(argv=None) -> None:
    args = parser().parse_args(argv)
    if args.count < 1 or args.first_id < 1 or args.start_line < 1:
        raise RunnerError("RANGE_INVALID")
    if args.max_cost <= 0 or (args.case_limit is not None and args.case_limit < 1):
        raise RunnerError("LIMIT_INVALID")
    if args.action == "init":
        result = initialize(args)
    elif args.action in {"run", "resume"}:
        result = run(args)
    else:
        result = status(Path(args.out))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except RunnerError as exc:
        print("PSEUDONYMIZER_ERROR:" + str(exc), file=os.sys.stderr)
        raise SystemExit(2)
    except KeyboardInterrupt:
        print("PSEUDONYMIZER_INTERRUPTED", file=os.sys.stderr)
        raise SystemExit(130)
    except BaseException as exc:
        print("PSEUDONYMIZER_UNEXPECTED:" + type(exc).__name__, file=os.sys.stderr)
        raise SystemExit(3)
