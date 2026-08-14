#!/usr/bin/env python3
"""Create a complete, sanitized public copy of an autonomous CSI run."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def verify_source(run_dir: Path) -> None:
    final = json.loads((run_dir / "final.json").read_text(encoding="utf-8"))
    if final.get("reason") != "duration-complete":
        raise ValueError("source run is not finalized with duration-complete")
    failures = []
    for line in (run_dir / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = run_dir / relative
        if not path.is_file() or sha256(path) != expected:
            failures.append(relative)
    if failures:
        raise ValueError(f"source checksum failures: {failures}")


def gzip_text_writer(path: Path) -> io.TextIOWrapper:
    raw = path.open("wb")
    compressed = gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=6, mtime=0)
    return io.TextIOWrapper(compressed, encoding="utf-8", newline="\n")


def redact(value: str, replacements: dict[str, str]) -> str:
    for private, public in replacements.items():
        value = re.sub(re.escape(private), public, value, flags=re.IGNORECASE)
    return value


def public_envelope(
    envelope: dict[str, Any], public_source: str, public_session: str,
    replacements: dict[str, str],
) -> dict[str, Any]:
    result = dict(envelope)
    result["source_id"] = public_source
    result["session_id"] = public_session
    result["raw"] = redact(str(result.get("raw", "")), replacements)
    return result


def write_jsonl_gzip(path: Path, values: Iterable[dict[str, Any]]) -> int:
    count = 0
    with gzip_text_writer(path) as stream:
        for value in values:
            stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
            count += 1
    return count


def sanitize_events(
    run_dir: Path, output: Path, public_source: str, public_session: str,
) -> int:
    def values() -> Iterable[dict[str, Any]]:
        for line in (run_dir / "events.ndjson").read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            event = json.loads(line)
            event.pop("device", None)
            event.pop("resolved_device", None)
            if "source_id" in event:
                event["source_id"] = public_source
            if "session_id" in event:
                event["session_id"] = public_session
            yield event

    return write_jsonl_gzip(output, values())


def sanitize_health(run_dir: Path, output: Path) -> int:
    boot_ids: dict[str, str] = {}
    interface_names = {"eth0": "ethernet", "wlan0": "management_wifi", "lo": "loopback"}

    def values() -> Iterable[dict[str, Any]]:
        for line in (run_dir / "system-health.ndjson").read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            record = json.loads(line)
            private_boot = str(record.get("boot_id", "missing"))
            if private_boot not in boot_ids:
                boot_ids[private_boot] = f"collector-boot-{len(boot_ids) + 1}"
            record["boot_id"] = boot_ids[private_boot]
            interfaces = record.get("interfaces", {})
            record["interfaces"] = {
                interface_names.get(name, f"interface-{index + 1}"): value
                for index, (name, value) in enumerate(sorted(interfaces.items()))
            }
            yield record

    return write_jsonl_gzip(output, values())


def parse_replacements(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        private, separator, public = value.partition("=")
        if not separator or not private or not public:
            raise ValueError("--replace values must use PRIVATE=PUBLIC")
        result[private] = public
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--public-source", default="sensor-node-b")
    parser.add_argument("--public-session", default="public-session-20260812")
    parser.add_argument("--replace", action="append", default=[])
    args = parser.parse_args()

    verify_source(args.run_dir)
    replacements = parse_replacements(args.replace)
    source_dirs = [path for path in (args.run_dir / "sources").iterdir() if path.is_dir()]
    if len(source_dirs) != 1:
        raise ValueError(f"expected one source, found {len(source_dirs)}")

    chunks_dir = args.bundle_dir / "serial" / "chunks"
    logs_dir = args.bundle_dir / "logs"
    if chunks_dir.exists() or logs_dir.exists():
        raise FileExistsError("refusing to overwrite an existing public measurement surface")
    chunks_dir.mkdir(parents=True)
    logs_dir.mkdir(parents=True)

    ledger = []
    total_records = 0
    for source_chunk in sorted(source_dirs[0].glob("*.ndjson.gz")):
        target = chunks_dir / source_chunk.name
        first_wall = last_wall = None
        records = 0
        with gzip.open(source_chunk, "rt", encoding="utf-8") as source, gzip_text_writer(target) as output:
            for line in source:
                envelope = public_envelope(
                    json.loads(line), args.public_source, args.public_session, replacements
                )
                wall = int(envelope["ingest_wall_time_ns"])
                first_wall = wall if first_wall is None else first_wall
                last_wall = wall
                output.write(json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n")
                records += 1
        total_records += records
        ledger.append({
            "compressed_bytes": target.stat().st_size,
            "first_ingest_wall_time_ns": first_wall,
            "last_ingest_wall_time_ns": last_wall,
            "path": str(target.relative_to(args.bundle_dir)),
            "records": records,
            "session_id": args.public_session,
            "sha256": sha256(target),
            "source_id": args.public_source,
            "status": "complete",
        })

    with (logs_dir / "chunks.ndjson").open("w", encoding="utf-8", newline="\n") as stream:
        for entry in ledger:
            stream.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")
    event_records = sanitize_events(
        args.run_dir, logs_dir / "collector_events.ndjson.gz", args.public_source, args.public_session
    )
    health_records = sanitize_health(args.run_dir, logs_dir / "collector_host_health.ndjson.gz")
    print(json.dumps({
        "chunks": len(ledger),
        "measurement_envelopes": total_records,
        "event_records": event_records,
        "health_records": health_records,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
