#!/usr/bin/env python3
"""Maintain private pointers to the latest local Studio/OpenRouter run logs.

The registry contains paths and non-secret run metadata only.  It lives under
`.local_runs/`, which is intentionally excluded from Git together with `res_*`.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / ".local_runs" / "latest.json"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _relative(path):
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def read_registry():
    if not REGISTRY.exists():
        return {"schema_version": 1, "runs": {}}
    try:
        value = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        value = {"schema_version": 1, "runs": {}}
    if not isinstance(value, dict) or not isinstance(value.get("runs"), dict):
        return {"schema_version": 1, "runs": {}}
    return value


def register_run(kind, output_directory, status, metadata=None):
    if kind not in {"studio", "openrouter"}:
        raise ValueError("kind must be studio or openrouter")
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    registry = read_registry()
    previous = registry["runs"].get(kind, {})
    registry["runs"][kind] = {
        "output_directory": _relative(output),
        "status": status,
        "first_registered_at": previous.get("first_registered_at", now())
        if previous.get("output_directory") == _relative(output) else now(),
        "updated_at": now(),
        "metadata": metadata or {},
    }
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".latest-", dir=REGISTRY.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(registry, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, REGISTRY)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return registry["runs"][kind]


def resolved_runs():
    value = read_registry()
    for item in value["runs"].values():
        path = Path(item["output_directory"])
        item["resolved_output_directory"] = str(path if path.is_absolute() else ROOT / path)
        item["exists"] = Path(item["resolved_output_directory"]).is_dir()
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("show", "register"))
    parser.add_argument("--kind", choices=("studio", "openrouter"))
    parser.add_argument("--out")
    parser.add_argument("--status", default="preserved")
    args = parser.parse_args()
    if args.action == "register":
        if not args.kind or not args.out:
            parser.error("register requires --kind and --out")
        register_run(args.kind, args.out, args.status)
    print(json.dumps(resolved_runs(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
