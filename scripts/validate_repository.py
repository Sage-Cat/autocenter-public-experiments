#!/usr/bin/env python3
"""Validate the lightweight repository and publication metadata surface."""

from __future__ import annotations

import fnmatch
import json
import posixpath
import re
import subprocess
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]


def tracked_paths() -> set[str]:
    output = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    return {item.decode("utf-8") for item in output.split(b"\0") if item}


def expand_braces(pattern: str) -> list[str]:
    match = re.search(r"\{([^{}]+)\}", pattern)
    if match is None:
        return [pattern]
    return [
        pattern[: match.start()] + choice + pattern[match.end() :]
        for choice in match.group(1).split(",")
    ]


def validate_manifest(paths: set[str]) -> None:
    manifest = json.loads((ROOT / "datasets" / "manifest.json").read_text(encoding="utf-8"))
    bundle_ids: set[str] = set()
    program_ids: set[str] = set()
    for bundle in manifest["datasets"]:
        bundle_id = bundle["bundle_id"]
        program_id = bundle["program_id"]
        if bundle_id in bundle_ids or program_id in program_ids:
            raise ValueError(f"duplicate dataset identity: {bundle_id} / {program_id}")
        bundle_ids.add(bundle_id)
        program_ids.add(program_id)

        prefix = f"datasets/{bundle_id}/"
        actual = {path.removeprefix(prefix) for path in paths if path.startswith(prefix)}
        patterns = [
            expanded
            for declared in bundle["included_surfaces"]
            for expanded in expand_braces(declared)
        ]
        for pattern in patterns:
            if not any(fnmatch.fnmatchcase(path, pattern) for path in actual):
                raise ValueError(f"{bundle_id}: inclusion matches no file: {pattern}")
        for path in actual:
            if not any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns):
                raise ValueError(f"{bundle_id}: tracked file is not in manifest: {path}")


def validate_markdown_links(paths: set[str]) -> None:
    for relative in sorted(path for path in paths if path.endswith(".md")):
        document = ROOT / relative
        if not document.is_file():
            continue
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            raw_target = target.split("#", 1)[0]
            normalized = posixpath.normpath(
                str(PurePosixPath(relative).parent.joinpath(raw_target))
            )
            if normalized in paths or any(path.startswith(normalized.rstrip("/") + "/") for path in paths):
                continue
            raise ValueError(f"{relative}: broken local link: {target}")


def main() -> int:
    paths = tracked_paths()
    validate_manifest(paths)
    validate_markdown_links(paths)
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    print("repository_validation=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
