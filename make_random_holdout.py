#!/usr/bin/env python3
"""Cria manifesto reproduzível de holdout a partir dos casos Mediare compatíveis."""

import argparse
import json
from pathlib import Path
import random


def ids_from_manifest(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    ids = value.get("case_ids")
    if not isinstance(ids, list) or any(not isinstance(cid, str) for cid in ids):
        raise ValueError(f"manifesto sem case_ids válido: {path}")
    return set(ids)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="casos")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    population = sorted(path.stem for path in Path(args.dataset).glob("[0-9][0-9][0-9][0-9].json"))
    excluded = set().union(*(ids_from_manifest(path) for path in args.exclude)) if args.exclude else set()
    eligible = [cid for cid in population if cid not in excluded]
    if args.count > len(eligible):
        raise SystemExit(f"amostra {args.count} excede população elegível {len(eligible)}")
    selected = random.Random(args.seed).sample(eligible, args.count)
    manifest = {
        "seed": args.seed,
        "population": f"{args.dataset}: {len(population)} casos Mediare compatíveis",
        "sampling": (
            f"{args.count} casos aleatórios sem reposição; excluídos {len(excluded)} IDs "
            "das amostras informadas"
        ),
        "excluded_manifests": args.exclude,
        "eligible_count": len(eligible),
        "case_ids": selected,
    }
    Path(args.output).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output, "eligible": len(eligible), "selected": len(selected)}, indent=2))


if __name__ == "__main__":
    main()
