# AC02 failure-aware adaptive sensing with prplOS context

- Bundle: `ac02_failure_aware_adaptive_prplos_20260813T173202Z`
- Series/experiment/topology: `AutoCenter / AC02 / two sensing nodes plus prplOS context`
- Condition: unchanged production Wi-Fi during natural retail operation
- Scheduled duration: 62,879 seconds (17.47 hours), autonomous
- Sensing topology: two Raspberry Pi 5 collectors with two ESP32-S3 nodes
- Sensing operating point: 2.4 GHz channel 2
- Endpoint separation/reference height: approximately 17.0 m / 1.2 m
- Network policy: production network observe-only; no production Wi-Fi changes
- prplOS role: read-only pWHM/TR-181 context from a separate dual-band AP
- Ground truth: controlled reset ledger only; natural human activity unlabelled

## Public measurement surface

`serial/node-{a,b}/chunks/` contains every readable finalized and
process-interrupted measurement chunk. Each NDJSON envelope retains ingest wall
and monotonic time, connection epoch, per-session source sequence, public
source/session labels, and the sanitized serial record. CSI IQ, RSSI, rate,
channel, ESP local timestamp, boot epoch, firmware counters, and timing markers
are preserved. `logs/node-*-chunks.ndjson` is the authoritative public ledger.

The bundle also preserves sanitized collector events, host-health records, and
parsed management-link measurements. Concrete SSID, BSSID/MAC, IP address,
hostname, serial path, board identifier, and credentials are absent.

## Controller and prplOS surface

`controller/decisions.ndjson.gz` contains the complete sanitized append log,
including orchestration margins outside the scheduled run. The compact
analysis selects the scheduled window by wall time. Parsed network and prplOS
context are published without raw device snapshots. The physical-reset ledger
and failed/aborted campaign ledgers are retained with command paths and private
infrastructure removed.

`metadata/method-configuration.json` records the AQ-MC, SACM, timing, budget,
and cadence parameters. `metadata/firmware-manifest.json` preserves target,
firmware version, and image hashes, but no firmware image or credential-bearing
build configuration.

## Reproduction

`scripts/sanitize_adaptive_run.py` verifies both original collector checksum
surfaces, streams every measurement envelope, pseudonymizes stable identifiers,
normalizes auxiliary records, removes private command/control fields, and
generates deterministic gzip output. `SHA256SUMS` is the integrity surface for
this independently generated public bundle.

Use `analysis/adaptive_run/summary.json` for the bounded machine-readable
results and `summary.md` for interpretation. Controlled reset distributions
are in `analysis/hardware-reset-campaign-summary.json`.

## Interpretation boundary

This run supports multi-node timing/failure discrimination, controlled-reset
detection/recovery, AQ-MC/SACM accounting, and read-only prplOS context
integration. It contains no successful configuration actuation, no completed
method-block comparison or rate sweep, no C5/5 GHz CSI, and no occupancy labels.
