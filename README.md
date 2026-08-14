# autocenter-public-experiments

Public measured data from operational Wi-Fi sensing experiments conducted in
the AutoCenter retail building. This is an independent experiment series; its
identifiers use the `AC` prefix and are not part of the CWS Lab `D` series.

The repository publishes sanitized measurements, integrity ledgers, bounded
analysis, and the sanitizers needed to reconstruct the public representation
from an authorized private archive. The existing production Wi-Fi network was
observed as natural interference and was not reconfigured for these runs.

## Repository map

- [Dataset manifest](datasets/manifest.json): authoritative publication index.
- [Datasets](datasets/): complete sanitized experiment bundles.
- [Dataset policy](docs/dataset-policy/policy.md): inclusion, privacy, and
  claim-boundary rules.
- [Architecture](docs/architecture/overview.md): measured system and data flow.
- [Structure](docs/structure/repository-structure.md): repository layout.
- [Scripts](scripts/): deterministic public sanitizers.

## Published experiments

### AC01 — 24-hour natural-operation baseline

- [Dataset](datasets/ac01_natural_operation_baseline_20260812T142321Z/)
- Duration: 24 hours.
- Topology: one Raspberry Pi 5 collector and one ESP32-S3 CSI sensor.
- Surface: 2,878,787 envelopes in 288 finalized chunks, collector events,
  host-health records, and timing/stability analysis.
- Supported evidence: long-run continuity, integrity, 32-bit ESP timestamp
  rollover handling, transport-failure discrimination, and natural RF
  variability.
- Boundary: no human-presence or activity labels; this is not occupancy or
  classification-accuracy evidence.

### AC02 — failure-aware adaptive sensing with prplOS context

- [Dataset](datasets/ac02_failure_aware_adaptive_prplos_20260813T173202Z/)
- Duration: 17.47 hours; 34.93 aggregate node-hours.
- Topology: two Raspberry Pi 5 collectors, two ESP32-S3 CSI sensors, and
  read-only context from a separate prplOS AP.
- Surface: 5,076,207 public envelopes, controller decisions, health and link
  records, parsed prplOS context, and a ten-trial physical-reset ledger.
- Supported evidence: multi-node timing/failure discrimination, controlled
  reset detection and recovery, cooperative admission, policy-budget
  accounting, and read-only prplOS integration.
- Boundary: the run contains no successful configuration actuation, causal QoS
  improvement, completed method-block comparison, C5/5 GHz CSI, or labelled
  human activity.

## Identifier convention

- `ACNN`: AutoCenter operational experiment number.
- `YYYYMMDDThhmmssZ`: UTC collection-start suffix.

Identifiers describe this repository only. Detailed topology and condition are
recorded in each bundle's `metadata.json` rather than encoded in the folder
name.

## Evidence and privacy boundary

Included data preserve timestamps, sequence and epoch fields, channel/rate/RSSI
measurements, CSI values, controller decisions, and event timing. Credentials,
concrete SSIDs, IP/MAC/BSSID values, hostnames, board serials, device paths,
exact site identity, and private control arguments are excluded or replaced by
stable public labels. See the dataset policy and each bundle's claim boundary
before using the data in a publication.
