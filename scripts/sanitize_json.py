#!/usr/bin/env python3
"""Recursively replace private identifiers in JSON or NDJSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_replacements(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        private, separator, public = value.partition("=")
        if not separator or not private or not public:
            raise ValueError("--replace values must use PRIVATE=PUBLIC")
        result[private] = public
    return result


def sanitize(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for private, public in replacements.items():
            value = value.replace(private, public).replace(private.upper(), public)
        return value
    if isinstance(value, list):
        return [sanitize(item, replacements) for item in value]
    if isinstance(value, dict):
        return {
            sanitize(str(key), replacements): sanitize(item, replacements)
            for key, item in value.items()
        }
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ndjson", action="store_true")
    parser.add_argument("--replace", action="append", default=[])
    args = parser.parse_args()
    replacements = parse_replacements(args.replace)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.ndjson:
        with args.output.open("w", encoding="utf-8", newline="\n") as stream:
            for line in args.input.read_text(encoding="utf-8").splitlines():
                if line:
                    stream.write(json.dumps(sanitize(json.loads(line), replacements), sort_keys=True) + "\n")
    else:
        value = sanitize(json.loads(args.input.read_text(encoding="utf-8")), replacements)
        args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
