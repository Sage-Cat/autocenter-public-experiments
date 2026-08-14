#!/usr/bin/env python3
"""Publish a complete privacy-safe copy of a two-node adaptive CSI run.

The script verifies each collector's immutable checksum surface, streams both
finalized and process-interrupted CSI chunks, preserves failure timing, and
removes deployment identifiers and command/control details.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any


MAC = re.compile(r"(?i)(?<![0-9a-f])(?:[0-9a-f]{2}:){5}[0-9a-f]{2}(?![0-9a-f])")
IPV4 = re.compile(r"(?<![0-9])(?:10|127|169\.254|172\.(?:1[6-9]|2[0-9]|3[01])|192\.168)(?:\.[0-9]{1,3}){2}(?![0-9])")
LOCAL_PATH = re.compile(r"/(?:home|var/lib|etc|dev|usr(?:/local)?)/(?:[^\s'\"},\]]+)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def gzip_text_writer(path: Path) -> io.TextIOWrapper:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = path.open("wb")
    compressed = gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=6, mtime=0)
    return io.TextIOWrapper(compressed, encoding="utf-8", newline="\n")


def json_lines(path: Path, *, lenient: bool = False) -> Iterator[tuple[dict[str, Any], bool]]:
    try:
        stream_context = (
            gzip.open(path, "rt", encoding="utf-8")
            if ".gz" in path.name
            else path.open("r", encoding="utf-8")
        )
        with stream_context as stream:
            while True:
                try:
                    line = stream.readline()
                except (EOFError, OSError):
                    break
                if not line:
                    break
                if not line.strip():
                    continue
                recovered = False
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    if not lenient or "{" not in line:
                        continue
                    try:
                        value = json.loads(line[line.index("{"):])
                        recovered = True
                    except json.JSONDecodeError:
                        continue
                if isinstance(value, dict):
                    yield value, recovered
    except (EOFError, OSError):
        return


class PrivacyMap:
    def __init__(self, run_id: str, public_run_id: str) -> None:
        self.run_id = run_id
        self.public_run_id = public_run_id
        self.source = {"esp32-s3-a": "sensor-node-a", "esp32-s3-b": "sensor-node-b"}
        self.sessions: dict[tuple[str, str], str] = {}
        self.boots: dict[tuple[str, str], str] = {}
        self.macs: dict[str, str] = {}

    def source_id(self, value: str) -> str:
        return self.source.get(value, value)

    def session_id(self, node: str, value: str) -> str:
        key = (node, value)
        if key not in self.sessions:
            self.sessions[key] = f"collector-{node}-session-{len([k for k in self.sessions if k[0] == node]) + 1:03d}"
        return self.sessions[key]

    def boot_id(self, node: str, value: str) -> str:
        key = (node, value)
        if key not in self.boots:
            self.boots[key] = f"collector-{node}-boot-{len([k for k in self.boots if k[0] == node]) + 1:02d}"
        return self.boots[key]

    def mac(self, match: re.Match[str]) -> str:
        value = match.group(0).lower()
        if value not in self.macs:
            self.macs[value] = f"02:00:00:00:00:{len(self.macs) + 1:02x}"
        return self.macs[value]

    def text(self, value: str) -> str:
        value = value.replace(self.run_id, self.public_run_id)
        for private, public in self.source.items():
            value = value.replace(private, public)
        value = re.sub(r"(?i)cws-pi5-a(?:\.local)?", "collector-node-a", value)
        value = re.sub(r"(?i)cws-pi5-b(?:\.local)?", "collector-node-b", value)
        value = re.sub(r"(?i)prplos\.lan", "router-node", value)
        value = re.sub(r"(?m)^\s*SSID:\s*[^\n]+", "\tSSID: deployment-network", value)
        value = MAC.sub(self.mac, value)
        # A serial-line collision can concatenate a partial identifier with the
        # next record before it contains all six octets. Full MAC replacement
        # above cannot recognize that damaged shape.
        value = re.sub(
            r"(?i)(?<=bssid=)(?:[0-9a-f]{2}:){2,4}[0-9a-f]{2}(?=:(?:CSI_DATA|CWSLAB_))",
            "02:00:00:00:00:fe",
            value,
        )
        value = re.sub(
            r"(?i)(?<=station_mac=)(?:[0-9a-f]{2}:){2,4}[0-9a-f]{2}(?=:(?:CSI_DATA|CWSLAB_))",
            "02:00:00:00:00:fd",
            value,
        )
        value = IPV4.sub("private-ip", value)
        value = LOCAL_PATH.sub("<local-path>", value)
        return value


DROP_KEYS = {
    "argv", "device", "resolved_device", "resolved_address", "host", "hostname",
    "gateway", "interface", "raw", "stdout", "stderr", "error", "restore_error",
}


def sanitize(value: Any, privacy: PrivacyMap, *, node: str | None = None) -> Any:
    if isinstance(value, str):
        return privacy.text(value)
    if isinstance(value, list):
        return [sanitize(item, privacy, node=node) for item in value]
    if not isinstance(value, dict):
        return value
    result: dict[str, Any] = {}
    for key, item in value.items():
        if key in DROP_KEYS:
            continue
        public_key = privacy.source_id(str(key))
        if key == "source_id" and isinstance(item, str):
            result[key] = privacy.source_id(item)
        elif key == "run_id" and isinstance(item, str):
            result[key] = privacy.public_run_id
        elif key == "session_id" and isinstance(item, str) and node is not None:
            result[key] = privacy.session_id(node, item)
        elif key == "node_id":
            result[key] = "primary-prplos-ap-node"
        else:
            result[public_key] = sanitize(item, privacy, node=node)
    return result


def verify_node(run: Path) -> dict[str, Any]:
    final = json.loads((run / "final.json").read_text(encoding="utf-8"))
    if final.get("reason") != "duration-complete":
        raise ValueError(f"{run}: not duration-complete")
    failures = []
    checked = 0
    for line in (run / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = run / relative
        checked += 1
        if not path.is_file() or sha256(path) != expected:
            failures.append(relative)
    if failures:
        raise ValueError(f"{run}: source checksum failures: {failures}")
    return {"checked_files": checked, "reason": final["reason"]}


def node_manifest(run: Path, node: str, privacy: PrivacyMap) -> dict[str, Any]:
    source = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    config = source["config"]
    source_config = config["sources"][0]
    return {
        "schema_version": 1,
        "run_id": privacy.public_run_id,
        "collector_node": f"collector-node-{node}",
        "collector_version": source["collector_version"],
        "source_id": privacy.source_id(source_config["source_id"]),
        "started_at": source["started_at"],
        "target_end_at": source["target_end_at"],
        "duration_seconds": source["duration_seconds"],
        "collection_mode": config["collection_mode"],
        "network_policy": config["network_policy"],
        "chunk_seconds": config["chunk_seconds"],
        "health_seconds": config["health_seconds"],
        "sync_seconds": config["sync_seconds"],
        "serial_baud": source_config["baud"],
        "reconnect_seconds": source_config["reconnect_seconds"],
        "host_machine": source["host"]["machine"],
        "host_platform": source["host"]["platform"],
        "host_python": source["host"]["python"],
        "preflight_ok": source["preflight"]["ok"],
    }


def node_final(run: Path, node: str, privacy: PrivacyMap) -> dict[str, Any]:
    source = json.loads((run / "final.json").read_text(encoding="utf-8"))
    return sanitize(source, privacy, node=node)


def sanitize_chunks(run: Path, output: Path, node: str, privacy: PrivacyMap) -> dict[str, Any]:
    source_dirs = [path for path in (run / "sources").iterdir() if path.is_dir()]
    if len(source_dirs) != 1:
        raise ValueError(f"{run}: expected one CSI source directory")
    source_dir = source_dirs[0]
    original_ledger = {
        str(row["path"]): row for row, _ in json_lines(run / "chunks.ndjson", lenient=True)
    }
    ledger = []
    totals: Counter[str] = Counter()
    paths = sorted(source_dir.glob("*.ndjson.gz*"), key=lambda path: path.name)
    for source_path in paths:
        source_relative = str(source_path.relative_to(run))
        original = original_ledger.get(source_relative, {})
        target = output / "serial" / f"node-{node}" / "chunks" / source_path.name
        count = recovered = 0
        first_wall = last_wall = None
        with gzip_text_writer(target) as stream:
            for envelope, was_recovered in json_lines(source_path, lenient=True):
                public = dict(envelope)
                if "run_id" in public:
                    public["run_id"] = privacy.public_run_id
                if public.get("source_id"):
                    public["source_id"] = privacy.source_id(str(public["source_id"]))
                if public.get("session_id"):
                    public["session_id"] = privacy.session_id(node, str(public["session_id"]))
                public["raw"] = privacy.text(str(public.get("raw", "")))
                wall = int(public.get("ingest_wall_time_ns", 0))
                first_wall = wall if first_wall is None else min(first_wall, wall)
                last_wall = wall if last_wall is None else max(last_wall, wall)
                stream.write(json.dumps(public, sort_keys=True, separators=(",", ":")) + "\n")
                count += 1
                recovered += int(was_recovered)
        status = str(original.get("status", "complete"))
        totals[status] += 1
        ledger.append({
            "path": str(target.relative_to(output)),
            "source_id": privacy.source_id(source_dir.name),
            "session_id": privacy.session_id(node, str(original.get("session_id", "unknown"))),
            "status": status,
            "records": count,
            "recovered_json_lines": recovered,
            "first_ingest_wall_time_ns": first_wall,
            "last_ingest_wall_time_ns": last_wall,
            "compressed_bytes": target.stat().st_size,
            "sha256": sha256(target),
        })
    log = output / "logs" / f"node-{node}-chunks.ndjson"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in ledger),
        encoding="utf-8",
    )
    return {
        "chunks": len(ledger),
        "status_counts": dict(sorted(totals.items())),
        "records": sum(row["records"] for row in ledger),
    }


def write_jsonl_gzip(path: Path, values: Iterable[dict[str, Any]]) -> int:
    count = 0
    with gzip_text_writer(path) as stream:
        for value in values:
            stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
            count += 1
    return count


def sanitize_events(run: Path, output: Path, node: str, privacy: PrivacyMap) -> dict[str, Any]:
    recovered = 0

    def values() -> Iterator[dict[str, Any]]:
        nonlocal recovered
        for value, was_recovered in json_lines(run / "events.ndjson", lenient=True):
            recovered += int(was_recovered)
            yield sanitize(value, privacy, node=node)

    count = write_jsonl_gzip(output, values())
    return {"records": count, "recovered_prefixed_json_lines": recovered}


def sanitize_health(run: Path, output: Path, node: str, privacy: PrivacyMap) -> int:
    interface_names = {"eth0": "ethernet", "wlan0": "management-wifi", "lo": "loopback"}

    def values() -> Iterator[dict[str, Any]]:
        for value, _ in json_lines(run / "system-health.ndjson", lenient=True):
            public = dict(value)
            public["boot_id"] = privacy.boot_id(node, str(value.get("boot_id", "missing")))
            public["interfaces"] = {
                interface_names.get(name, f"interface-{index + 1}"): item
                for index, (name, item) in enumerate(sorted(value.get("interfaces", {}).items()))
            }
            yield public

    return write_jsonl_gzip(output, values())


def sampler_record(value: dict[str, Any], node: str, privacy: PrivacyMap) -> dict[str, Any]:
    stdout = str(value.get("stdout", ""))

    def number(pattern: str, kind: type[int] | type[float]) -> int | float | None:
        match = re.search(pattern, stdout)
        return kind(match.group(1)) if match else None

    return {
        "sampler_id": value.get("sampler_id"),
        "session_id": privacy.session_id(node, str(value.get("session_id", "unknown"))),
        "sequence": value.get("sequence"),
        "started_wall_time_ns": value.get("started_wall_time_ns"),
        "started_monotonic_ns": value.get("started_monotonic_ns"),
        "duration_ms": value.get("duration_ms"),
        "returncode": value.get("returncode"),
        "timed_out": value.get("timed_out"),
        "frequency_mhz": number(r"\bfreq:\s*([0-9.]+)", float),
        "signal_dbm": number(r"\bsignal:\s*(-?[0-9]+)\s+dBm", int),
        "rx_bytes": number(r"\bRX:\s*([0-9]+)\s+bytes", int),
        "rx_packets": number(r"\bRX:\s*[0-9]+\s+bytes\s+\(([0-9]+)\s+packets", int),
        "tx_bytes": number(r"\bTX:\s*([0-9]+)\s+bytes", int),
        "tx_packets": number(r"\bTX:\s*[0-9]+\s+bytes\s+\(([0-9]+)\s+packets", int),
        "rx_bitrate_mbps": number(r"\brx bitrate:\s*([0-9.]+)\s+MBit/s", float),
        "tx_bitrate_mbps": number(r"\btx bitrate:\s*([0-9.]+)\s+MBit/s", float),
    }


def sanitize_sampler(run: Path, output: Path, node: str, privacy: PrivacyMap) -> int:
    values = (
        sampler_record(value, node, privacy)
        for value, _ in json_lines(run / "samplers" / "wifi-link-context.ndjson", lenient=True)
    )
    return write_jsonl_gzip(output, values)


def public_method_config(path: Path, privacy: PrivacyMap) -> dict[str, Any]:
    source = json.loads(path.read_text(encoding="utf-8"))
    keep = {
        key: source[key] for key in (
            "schema_version", "decision_interval_seconds", "window_seconds", "freshness_seconds",
            "minimum_frames", "default_rate_hz", "rssi_std_scale_dbm", "motion_rssi_std_dbm",
            "motion_csi_cv", "context_max_age_seconds", "prpl_context_max_age_seconds",
            "timing_mode", "mode", "policy_variant", "aqmc", "sacm",
        )
    }
    keep["nodes"] = {privacy.source_id(key): {} for key in source["nodes"]}
    keep["router_role"] = "primary prplOS-compatible dual-band AP node; read-only context"
    return sanitize(keep, privacy)


def sanitize_firmware(path: Path, privacy: PrivacyMap) -> dict[str, Any]:
    source = json.loads(path.read_text(encoding="utf-8"))
    source["builds"] = {
        privacy.source_id(key): {
            name: value for name, value in item.items() if name.endswith("_sha256")
        }
        for key, item in source["builds"].items()
    }
    return source


def sanitize_campaign_ledger(path: Path, output: Path, privacy: PrivacyMap) -> int:
    return write_jsonl_gzip(
        output,
        (sanitize(value, privacy) for value, _ in json_lines(path, lenient=True)),
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--public-run-id", required=True)
    args = parser.parse_args()
    if args.bundle_dir.exists():
        raise FileExistsError(f"refusing to overwrite {args.bundle_dir}")

    private_run_id = json.loads(
        (args.package / "nodes" / "pi5-a" / "manifest.json").read_text(encoding="utf-8")
    )["run_id"]
    privacy = PrivacyMap(private_run_id, args.public_run_id)
    args.bundle_dir.mkdir(parents=True)
    result: dict[str, Any] = {"nodes": {}}
    for node in ("a", "b"):
        run = args.package / "nodes" / f"pi5-{node}"
        verification = verify_node(run)
        write_json(args.bundle_dir / "metadata" / f"node-{node}-manifest.json", node_manifest(run, node, privacy))
        write_json(args.bundle_dir / "metadata" / f"node-{node}-final.json", node_final(run, node, privacy))
        chunk_result = sanitize_chunks(run, args.bundle_dir, node, privacy)
        event_result = sanitize_events(
            run, args.bundle_dir / "logs" / f"node-{node}-collector-events.ndjson.gz", node, privacy
        )
        health = sanitize_health(
            run, args.bundle_dir / "logs" / f"node-{node}-host-health.ndjson.gz", node, privacy
        )
        sampler = sanitize_sampler(
            run, args.bundle_dir / "logs" / f"node-{node}-management-link.ndjson.gz", node, privacy
        )
        result["nodes"][node] = {
            "source_verification": verification,
            "chunks": chunk_result,
            "events": event_result,
            "host_health_records": health,
            "management_link_records": sampler,
        }

    controller = args.package / "controller"
    result["controller_decisions"] = write_jsonl_gzip(
        args.bundle_dir / "controller" / "decisions.ndjson.gz",
        (sanitize(value, privacy) for value, _ in json_lines(controller / "decisions.ndjson", lenient=True)),
    )
    result["network_context_records"] = write_jsonl_gzip(
        args.bundle_dir / "controller" / "network-context.ndjson.gz",
        (sanitize(value, privacy) for value, _ in json_lines(controller / "context.ndjson", lenient=True)),
    )
    result["prpl_context_records"] = write_jsonl_gzip(
        args.bundle_dir / "controller" / "prpl-context.ndjson.gz",
        (sanitize(value, privacy) for value, _ in json_lines(controller / "prpl-context.ndjson", lenient=True)),
    )
    result["hardware_reset_ledger_records"] = sanitize_campaign_ledger(
        controller / "hardware-reset-campaign-ledger.ndjson",
        args.bundle_dir / "controller" / "hardware-reset-campaign-ledger.ndjson.gz",
        privacy,
    )
    result["aborted_campaign_ledger_records"] = sanitize_campaign_ledger(
        controller / "failure-campaign-ledger.ndjson",
        args.bundle_dir / "controller" / "aborted-failure-campaign-ledger.ndjson.gz",
        privacy,
    )
    for source_name, target_name in (
        ("usb-power-campaign-aborted-20260813T174139Z.ndjson", "aborted-usb-power-campaign.ndjson.gz"),
        ("usb-host-campaign-relabelled-20260813T174410Z.ndjson", "relabelled-usb-host-campaign.ndjson.gz"),
    ):
        result[target_name] = sanitize_campaign_ledger(
            controller / source_name,
            args.bundle_dir / "controller" / target_name,
            privacy,
        )

    hardware = sanitize(
        json.loads((controller / "hardware-reset-campaign-summary.json").read_text(encoding="utf-8")),
        privacy,
    )
    hardware.pop("sources", None)
    write_json(args.bundle_dir / "analysis" / "hardware-reset-campaign-summary.json", hardware)
    method_blocks = sanitize(
        json.loads((controller / "method-blocks-20260813" / "manifest.json").read_text(encoding="utf-8")),
        privacy,
    )
    method_blocks["failure_classification"] = "precondition-failed-before-active-collection"
    write_json(args.bundle_dir / "analysis" / "failed-method-block-attempt.json", method_blocks)
    write_json(
        args.bundle_dir / "metadata" / "method-configuration.json",
        public_method_config(args.package / "configuration" / "pi5-a" / "cws-control" / "config.json", privacy),
    )
    write_json(
        args.bundle_dir / "metadata" / "firmware-manifest.json",
        sanitize_firmware(controller / "firmware-manifest-v1.3.1.json", privacy),
    )
    write_json(args.bundle_dir / "sanitization-accounting.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
