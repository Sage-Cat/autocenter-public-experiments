# AC03 multiband endurance with prplOS context

- Bundle: `ac03_multiband_endurance_prplos_20260814T135053Z`
- Series/experiment: `AutoCenter / AC03`
- Condition: unchanged production Wi-Fi during natural retail operation
- S3 duration: 72,000 seconds per node, two nodes, autonomous
- C5-A duration: 64,800 seconds, autonomous and independently timed
- S3 operating point: 2.4 GHz channel 2, nominal 40 Hz probes
- C5 operating point: 5 GHz channel 36, nominal 40 Hz probes
- Sensing topology: two Raspberry Pi 5 collectors, two ESP32-S3 nodes, one
  data-producing ESP32-C5 node
- Network policy: production network observe-only; no production Wi-Fi changes
- prplOS role: read-only context from a primary prplOS-compatible dual-band AP
- Ground truth: one documented operator restart; natural human activity unlabelled

## Public measurement surface

`serial/node-{a,b,c5-a}/chunks/` contains every readable finalized and
process-interrupted measurement chunk. Each NDJSON envelope retains ingest wall
and monotonic time, connection epoch, per-session source sequence, public
source/session labels, and sanitized serial text. CSI IQ, RSSI, rate, channel,
ESP local timestamp, firmware counters, and timing heartbeats are preserved.
`logs/node-*-chunks.ndjson` is the authoritative public chunk ledger.

The bundle also preserves sanitized collector events and host-health records.
Management-link measurements exist for the two S3 collectors. Concrete SSID,
BSSID/MAC, IP address, hostname, serial path, board identifier, and credentials
are absent.

## Controller and prplOS surface

`controller/decisions.ndjson.gz` is bounded to the S3 collection interval. The
controller started about 53 minutes after sensing began, so its actual decision
span is 19.114 hours. Parsed network and prplOS context are bounded to the same
interval and published without raw router snapshots.

`metadata/method-configuration.json` records the AQ-MC, SACM, timing, budget,
and cadence parameters. The three firmware metadata files preserve targets,
versions, and binary hashes without firmware images or credential-bearing build
configuration. Failed and planned-only activities are retained in `analysis/`
and explicitly excluded from results.

## Reproduction

`scripts/sanitize_ac03_run.py` verifies all three immutable collector checksum
surfaces, streams every measurement envelope, pseudonymizes stable identifiers,
normalizes auxiliary records, removes private command/control fields, and
selects bounded controller context. `SHA256SUMS` is the integrity surface for
the independently generated public bundle.

Use `analysis/source-summary.json` for machine-readable measurement results,
`analysis/controller-summary.json` for policy/context accounting, and
`analysis/live-false-reset-audit.csv` for the serial-order cross-check of every
live false reset. `analysis/design-corrections.md` translates the findings into
the minimum daemon changes needed before an apply-mode experiment.

## Interpretation boundary

This run supports endurance, integrity, rollover, descriptive multiband,
invalid-timing exclusion, policy accounting, and read-only prplOS-context
claims. It contains no controlled fault campaign, successful actuation,
completed rate sweep, completed method comparison, paired C5 stream, or human
activity ground truth.
