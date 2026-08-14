# AC01 24-hour natural-operation baseline

- Bundle: `ac01_natural_operation_baseline_20260812T142321Z`
- Series/experiment/topology: `AutoCenter / AC01 / single sensor and collector`
- Condition: unchanged production Wi-Fi during natural retail operation
- Duration: 24 hours, autonomous
- Sensor: one live ESP32-S3 CSI node
- Collector: one Raspberry Pi 5
- Operating point: 2.4 GHz, channel 2, unchanged production Wi-Fi
- Scene: naturally occupied operational retail environment
- Ground truth: none; occupancy and activity were not labelled

## Public measurement surface

The complete public record stream is split into 288 finalized five-minute gzip
chunks under `serial/chunks/`. Each line is a JSON envelope containing public
source/session labels, ingest wall and monotonic timestamps, connection epoch,
source sequence, and the preserved serial record. CSI IQ values, RSSI, channel,
rate, local ESP timestamp, firmware counters, and event timing are retained.

`logs/chunks.ndjson` is the authoritative public chunk ledger and records every
chunk's record count, time bounds, byte size, and SHA-256. The bundle also
retains all six collector lifecycle/transport events and all 8,613 collector
health samples as compressed NDJSON.

## Analysis

`analysis/natural_operation/summary.json` contains complete machine-readable
statistics. `summary.md` is the compact interpretation, `hourly.csv` contains
local-clock aggregates, and `malformed_examples.ndjson` preserves bounded
examples of all malformed-record classes.

The analysis structurally checked every CSI record and computed RSSI,
continuity, timing, and validity statistics from the full stream. IQ amplitude
features use a deterministic one-in-100 envelope sample. Source-archive hashes
were verified before sanitization; `SHA256SUMS` verifies the independently
generated public bundle.

## Reproduction and interpretation

Use `scripts/sanitize_autonomous_run.py` to create the public measurement
layout from an authorized finalized collector archive. The source archive must
finish with `duration-complete` and pass its original checksums. Private-to-
public identifier mappings are supplied at publication time and are not stored
in this repository.

This bundle supports long-run stability, timestamp rollover, data integrity,
serial reconnect, sensing-path continuity, and natural RF-variation analyses.
It does not support occupancy classification, activity recognition, or causal
claims about people because no operator ground-truth timeline exists.
