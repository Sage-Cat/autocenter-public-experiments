#!/usr/bin/env python3
"""Exhaustively scan public dataset artifacts for structured privacy findings."""

from __future__ import annotations

import argparse
import gzip
import os
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


PATTERNS = {
    "private_user_path": re.compile(rb"(?i)/(?:home|Users)/[^\s\"\\]+"),
    "private_ipv4": re.compile(
        rb"(?<![0-9])(?:10\.[0-9]{1,3}(?:\.[0-9]{1,3}){2}"
        rb"|192\.168(?:\.[0-9]{1,3}){2}"
        rb"|172\.(?:1[6-9]|2[0-9]|3[01])(?:\.[0-9]{1,3}){2})(?![0-9])"
    ),
    "email_address": re.compile(rb"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"),
    "secret_material": re.compile(
        rb"(?i)(?:BEGIN [A-Z ]*PRIVATE KEY"
        rb"|ssh-(?:rsa|ed25519)\s+[A-Za-z0-9+/]{40,}"
        rb"|github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+)"
    ),
    "private_device_path": re.compile(
        rb"(?i)/(?:dev/(?:tty|serial)|tmp|mnt|media)/[^\s\"\\]+"
    ),
    "exact_location_field": re.compile(
        rb"(?i)\"(?:latitude|longitude|street|postal_code|exact_address)\"\s*:"
    ),
    "credential_value": re.compile(
        rb"(?i)\"(?:password|passphrase|psk|private_key|api_key|access_token|secret)\""
        rb"\s*:\s*\"(?!\s*(?:redacted|excluded|absent|none|null)\s*\")"
    ),
    "concrete_ssid": re.compile(
        rb"(?i)\"ssid\"\s*:\s*\""
        rb"(?!\s*(?:redacted|deployment-network|excluded|absent|none|null)?\s*\")"
    ),
    "private_host": re.compile(
        rb"(?i)\"(?:host|hostname)\"\s*:\s*\""
        rb"(?!\s*(?:redacted|excluded|absent|none|null|router-node"
        rb"|node-[ab]|collector-node-[ab])\s*\")"
    ),
    "unrelated_series_identifier": re.compile(rb"(?:D11|D12|d11_c6|d12_c6)"),
}

MAC = re.compile(rb"(?i)(?<![0-9a-f])(?:[0-9a-f]{2}:){5}[0-9a-f]{2}(?![0-9a-f])")
PUBLIC_MAC = re.compile(rb"02:00:00:00:00:[0-9a-f]{2}", re.IGNORECASE)


def _is_gzip(path: Path) -> bool:
    return path.name.endswith(".gz") or path.name.endswith(".gz.incomplete")


def scan_file(path_text: str) -> tuple[str, tuple[str, ...]]:
    path = Path(path_text)
    findings: set[str] = set()
    opener = gzip.open if _is_gzip(path) else open
    try:
        with opener(path, "rb") as stream:
            carry = b""
            while data := stream.read(8 * 1024 * 1024):
                block = carry + data
                for name, pattern in PATTERNS.items():
                    if pattern.search(block):
                        findings.add(name)
                if any(not PUBLIC_MAC.fullmatch(value) for value in MAC.findall(block)):
                    findings.add("non_public_mac")
                carry = block[-1024:]
    except (EOFError, OSError):
        findings.add("unreadable_artifact")
    return path_text, tuple(sorted(findings))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path("datasets"))
    parser.add_argument(
        "--workers",
        type=int,
        default=min(12, os.cpu_count() or 1),
        help="parallel artifact scanners (default: up to 12)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = sorted(
        path
        for path in args.root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    )
    findings: list[tuple[str, tuple[str, ...]]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(scan_file, (str(path) for path in files)):
            if result[1]:
                findings.append(result)

    print(f"artifacts_scanned={len(files)}")
    if findings:
        for path, categories in findings:
            print(f"finding={','.join(categories)} path={path}")
        return 1
    print("privacy_findings=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
