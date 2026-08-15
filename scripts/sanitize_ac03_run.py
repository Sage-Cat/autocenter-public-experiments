#!/usr/bin/env python3
"""Publish the privacy-safe AC03 multiband endurance bundle.

AC03 combines a two-node ESP32-S3 run, an independently timed ESP32-C5 run,
and the bounded controller/prplOS context that overlaps the S3 run. Source
archives are verified before any public artifact is written.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterator
from collections import Counter
from pathlib import Path
from typing import Any

from sanitize_adaptive_run import (
    PrivacyMap,
    json_lines,
    node_final,
    node_manifest,
    public_method_config,
    sanitize,
    sanitize_chunks,
    sanitize_events,
    sanitize_health,
    sanitize_sampler,
    verify_node,
    write_json,
    write_jsonl_gzip,
)


class AC03PrivacyMap(PrivacyMap):
    """Extend the existing stable map to the independently started C5 run."""

    def __init__(
        self,
        s3_run_id: str,
        c5_run_id: str,
        public_run_id: str,
    ) -> None:
        super().__init__(s3_run_id, public_run_id)
        self.c5_run_id = c5_run_id
        self.source["esp32-c5-a"] = "sensor-node-c5-a"

    def text(self, value: str) -> str:
        value = super().text(value.replace(self.c5_run_id, self.public_run_id))
        value = re.sub(r"(?i)\bpi5-a\b", "collector-node-a", value)
        return re.sub(r"(?i)\bpi5-b\b", "collector-node-b", value)


def bounded_values(
    path: Path,
    privacy: PrivacyMap,
    start_ns: int,
    end_ns: int,
    time_key: str,
) -> Iterator[dict[str, Any]]:
    for value, _ in json_lines(path, lenient=True):
        try:
            wall_ns = int(value[time_key])
        except (KeyError, TypeError, ValueError):
            continue
        if start_ns <= wall_ns <= end_ns:
            yield sanitize(value, privacy)


def firmware_manifest(path: Path, privacy: PrivacyMap, source: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    build = value["builds"][source]
    return {
        "schema_version": value["schema_version"],
        "source_id": privacy.source_id(source),
        "target": value["target"],
        "firmware_version": value["firmware_version"],
        "esp_idf_version": value["esp_idf_version"],
        "probe_payload_bytes": value["probe_payload_bytes"],
        "runtime_rate_range_hz": value["runtime_rate_range_hz"],
        "binary_sha256": {
            key: item for key, item in build.items() if key.endswith("_sha256")
        },
    }


def rate_sweep_summary(path: Path, privacy: PrivacyMap) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    outcomes = []
    for phase in value.get("phases", []):
        for command in phase.get("commands", []):
            outcomes.append({
                "source_id": privacy.source_id(str(command.get("source_id"))),
                "requested_rate_hz": command.get("hz"),
                "status": command.get("status"),
                "returncode": command.get("returncode"),
                "acknowledgement": "timeout",
            })
    return {
        "schema_version": value.get("schema_version"),
        "experiment": value.get("experiment"),
        "started_at": value.get("started_at"),
        "ended_at": value.get("ended_at"),
        "planned_rates_hz": value.get("rates_hz"),
        "phase_seconds": value.get("phase_seconds"),
        "status": value.get("status"),
        "completed_rate_phases": 0,
        "command_outcomes": outcomes,
        "interpretation": (
            "The first 10 Hz commands timed out on both S3 sensors. No rate phase "
            "was completed and no runtime-rate comparison is claimed."
        ),
    }


def planned_method_blocks(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema_version": value.get("schema_version"),
        "seed": value.get("seed"),
        "repetitions": value.get("repetitions"),
        "phase_seconds": value.get("phase_seconds"),
        "cooldown_seconds": value.get("cooldown_seconds"),
        "require_prpl_context": value.get("require_prpl_context"),
        "prpl_wait_seconds": value.get("prpl_wait_seconds"),
        "status": "planned-not-executed",
        "claim_status": "not a result",
    }


def count_json_lines(path: Path) -> int:
    return sum(1 for _value, _recovered in json_lines(path, lenient=True))


def resume_source_accounting(
    bundle_dir: Path,
    runs: dict[str, Path],
    privacy: PrivacyMap,
) -> dict[str, Any]:
    """Rebuild accounting after all source artifacts were already emitted."""
    result: dict[str, Any] = {}
    for node, run in runs.items():
        ledger_path = bundle_dir / "logs" / f"node-{node}-chunks.ndjson"
        if not ledger_path.is_file():
            raise FileNotFoundError(f"resume source ledger is missing: {ledger_path}")
        ledger = [value for value, _ in json_lines(ledger_path, lenient=True)]
        statuses = Counter(str(value.get("status", "missing")) for value in ledger)
        # Re-emit the small event surface with the current privacy rules. Seed
        # session labels in the same order used by the initial source pass.
        final = json.loads((run / "final.json").read_text(encoding="utf-8"))
        privacy.session_id(node, str(final.get("session_id", "unknown")))
        source_dirs = [path for path in (run / "sources").iterdir() if path.is_dir()]
        original = {
            str(value["path"]): value
            for value, _ in json_lines(run / "chunks.ndjson", lenient=True)
        }
        for path in sorted(source_dirs[0].glob("*.ndjson.gz*"), key=lambda item: item.name):
            relative = str(path.relative_to(run))
            privacy.session_id(node, str(original.get(relative, {}).get("session_id", "unknown")))
        events_path = bundle_dir / "logs" / f"node-{node}-collector-events.ndjson.gz"
        event_result = sanitize_events(run, events_path, node, privacy)
        health_path = bundle_dir / "logs" / f"node-{node}-host-health.ndjson.gz"
        management_path = bundle_dir / "logs" / f"node-{node}-management-link.ndjson.gz"
        result[node] = {
            "source_verification": verify_node(run),
            "chunks": {
                "chunks": len(ledger),
                "status_counts": dict(sorted(statuses.items())),
                "records": sum(int(value.get("records") or 0) for value in ledger),
            },
            "events": event_result,
            "host_health_records": count_json_lines(health_path),
            "management_link_records": (
                count_json_lines(management_path) if management_path.is_file() else 0
            ),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s3-a-run", type=Path, required=True)
    parser.add_argument("--s3-b-run", type=Path, required=True)
    parser.add_argument("--c5-a-run", type=Path, required=True)
    parser.add_argument("--controller-dir", type=Path, required=True)
    parser.add_argument("--s3-firmware", type=Path, required=True)
    parser.add_argument("--c5-firmware", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--public-run-id", required=True)
    parser.add_argument(
        "--resume-after-sources",
        action="store_true",
        help="reuse a complete previously emitted source surface",
    )
    args = parser.parse_args()
    if args.bundle_dir.exists() and not args.resume_after_sources:
        raise FileExistsError(f"refusing to overwrite {args.bundle_dir}")

    s3_manifest = json.loads((args.s3_a_run / "manifest.json").read_text(encoding="utf-8"))
    c5_manifest = json.loads((args.c5_a_run / "manifest.json").read_text(encoding="utf-8"))
    privacy = AC03PrivacyMap(
        str(s3_manifest["run_id"]),
        str(c5_manifest["run_id"]),
        args.public_run_id,
    )
    args.bundle_dir.mkdir(parents=True, exist_ok=args.resume_after_sources)
    result: dict[str, Any] = {"sources": {}}
    runs = {
        "a": args.s3_a_run,
        "b": args.s3_b_run,
        "c5-a": args.c5_a_run,
    }
    if args.resume_after_sources:
        result["sources"] = resume_source_accounting(args.bundle_dir, runs, privacy)
    else:
        for node, run in runs.items():
            verification = verify_node(run)
            write_json(
                args.bundle_dir / "metadata" / f"node-{node}-manifest.json",
                node_manifest(run, node, privacy),
            )
            write_json(
                args.bundle_dir / "metadata" / f"node-{node}-final.json",
                node_final(run, node, privacy),
            )
            chunks = sanitize_chunks(run, args.bundle_dir, node, privacy)
            events = sanitize_events(
                run,
                args.bundle_dir / "logs" / f"node-{node}-collector-events.ndjson.gz",
                node,
                privacy,
            )
            health = sanitize_health(
                run,
                args.bundle_dir / "logs" / f"node-{node}-host-health.ndjson.gz",
                node,
                privacy,
            )
            management = 0
            if (run / "samplers" / "wifi-link-context.ndjson").is_file():
                management = sanitize_sampler(
                    run,
                    args.bundle_dir / "logs" / f"node-{node}-management-link.ndjson.gz",
                    node,
                    privacy,
                )
            result["sources"][node] = {
                "source_verification": verification,
                "chunks": chunks,
                "events": events,
                "host_health_records": health,
                "management_link_records": management,
            }

    s3_final = json.loads((args.s3_a_run / "final.json").read_text(encoding="utf-8"))
    # Exact controller bounds use the collectors' first and last archived
    # wall-clock values rather than a rounded manifest timestamp.
    ledgers = []
    for run in (args.s3_a_run, args.s3_b_run):
        ledgers.extend(value for value, _ in json_lines(run / "chunks.ndjson", lenient=True))
    timed_ledgers = [
        value for value in ledgers
        if value.get("first_ingest_wall_time_ns") is not None
        and value.get("last_ingest_wall_time_ns") is not None
    ]
    controller_start_ns = min(int(value["first_ingest_wall_time_ns"]) for value in timed_ledgers)
    controller_end_ns = max(int(value["last_ingest_wall_time_ns"]) for value in timed_ledgers)

    result["controller_decisions"] = write_jsonl_gzip(
        args.bundle_dir / "controller" / "decisions.ndjson.gz",
        bounded_values(
            args.controller_dir / "decisions.ndjson",
            privacy,
            controller_start_ns,
            controller_end_ns,
            "decision_wall_time_ns",
        ),
    )
    result["network_context_records"] = write_jsonl_gzip(
        args.bundle_dir / "controller" / "network-context.ndjson.gz",
        bounded_values(
            args.controller_dir / "context.ndjson",
            privacy,
            controller_start_ns,
            controller_end_ns,
            "sampled_wall_time_ns",
        ),
    )
    result["prpl_context_records"] = write_jsonl_gzip(
        args.bundle_dir / "controller" / "prpl-context.ndjson.gz",
        bounded_values(
            args.controller_dir / "prpl-context.ndjson",
            privacy,
            controller_start_ns,
            controller_end_ns,
            "sampled_wall_time_ns",
        ),
    )
    write_json(
        args.bundle_dir / "metadata" / "method-configuration.json",
        public_method_config(args.controller_dir / "config.apply-ac03.json", privacy),
    )
    write_json(
        args.bundle_dir / "metadata" / "firmware-s3-a.json",
        firmware_manifest(args.s3_firmware, privacy, "esp32-s3-a"),
    )
    write_json(
        args.bundle_dir / "metadata" / "firmware-s3-b.json",
        firmware_manifest(args.s3_firmware, privacy, "esp32-s3-b"),
    )
    write_json(
        args.bundle_dir / "metadata" / "firmware-c5-a.json",
        firmware_manifest(args.c5_firmware, privacy, "esp32-c5-a"),
    )
    write_json(
        args.bundle_dir / "analysis" / "failed-rate-sweep.json",
        rate_sweep_summary(args.controller_dir / "rate-sweep.json", privacy),
    )
    write_json(
        args.bundle_dir / "analysis" / "planned-method-blocks.json",
        planned_method_blocks(args.controller_dir / "method-blocks.json"),
    )
    result["controller_start_wall_time_ns"] = controller_start_ns
    result["controller_end_wall_time_ns"] = controller_end_ns
    result["source_final_reason"] = s3_final["reason"]
    write_json(args.bundle_dir / "sanitization-accounting.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
