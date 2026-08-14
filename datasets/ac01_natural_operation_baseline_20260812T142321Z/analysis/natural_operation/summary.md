# AC01 natural-operation CSI run: 24-hour analysis

Run `run-20260812t142321z-shop-natural-occupancy-24h` completed normally and spans 23.9999 observed hours.
Before sanitization, all 294 source-archive checksum entries verified; the
archive contains 288 finalized chunks and no partial chunks. The public bundle
has independently regenerated chunks, ledger hashes, and `SHA256SUMS`.

## Core results

- Envelopes: 2,878,787; structurally valid CSI: 2,861,493; malformed CSI candidates: 16 (0.000559%).
- ESP timestamp wraps: 20; non-wrap regressions: 0.
- CSI sequence-estimated missing frames: 621; duplicates: 0; regressions: 0.
- RSSI: mean -75.660 dBm, standard deviation 1.074 dB, range -96..-69 dBm.
- Longest valid-CSI ingestion gap: 32.617820 s.
- Serial transport disconnects: 1; duration 2.007604 s.
- Firmware counters between first/last heartbeats: CSI delta 2,861,995; output-drop delta 1,199.

## Archive and collector-host validation

- Chunk ledger: 288 entries, 288 complete, 288 unique paths; ledger and parsed-envelope counts differ by 0.
- Host health: 8,613 samples; 1 boot ID; clock synchronized in 8,613/8,613 samples; wall/monotonic regressions 0/0.
- Pi temperature: mean 55.79 C, maximum 60.60 C; maximum health-sample gap 12.588 s.
- Pi one-minute load: mean 0.218, maximum 1.058; minimum free storage 22.71 GiB.
- Wi-Fi interface stayed up in 8,613/8,613 samples; Ethernet stayed down in 8,613/8,613 samples.

## Failure-aware interpretation

- The 20 ESP 32-bit microsecond-clock wraps with zero non-wrap regressions are a natural-run validation of rollover handling, not reboot events.
- The sole 2.008-second transport interruption reconnected without changing the firmware boot epoch; it is therefore a serial-path failure, not evidence of an ESP reboot.
- The longest CSI-only silence was 32.618 seconds, while the longest gap across every envelope was 6.767 seconds. Heartbeats continued through part of the CSI silence, allowing sensing-path loss to be distinguished from complete node loss.
- Collector source-sequence continuity is exact. CSI sequence gaps and the firmware output-drop counter are separate observations and must not be added as though they identify the same lost frames.
- The reported noise floor is invariant, so it is retained for provenance but is not a useful time-varying interference covariate in this run.

## Hourly signal summary

| Local hour | Valid CSI | Malformed | Mean CSI/s | Mean RSSI (dBm) | RSSI SD | Sampled mean amplitude |
|---|---:|---:|---:|---:|---:|---:|
| 2026-08-12T17:00:00+03:00 | 68252 | 1 | 18.959 | -75.957 | 0.962 | 14.405 |
| 2026-08-12T18:00:00+03:00 | 102492 | 0 | 28.470 | -76.022 | 0.147 | 14.139 |
| 2026-08-12T19:00:00+03:00 | 118536 | 0 | 32.927 | -75.986 | 0.475 | 14.167 |
| 2026-08-12T20:00:00+03:00 | 128199 | 0 | 35.611 | -75.668 | 0.471 | 14.106 |
| 2026-08-12T21:00:00+03:00 | 128414 | 1 | 35.671 | -75.416 | 0.493 | 14.119 |
| 2026-08-12T22:00:00+03:00 | 129929 | 1 | 36.091 | -75.226 | 0.419 | 14.241 |
| 2026-08-12T23:00:00+03:00 | 131523 | 0 | 36.534 | -75.228 | 0.420 | 14.234 |
| 2026-08-13T00:00:00+03:00 | 132674 | 0 | 36.854 | -75.217 | 0.412 | 14.220 |
| 2026-08-13T01:00:00+03:00 | 127459 | 0 | 35.405 | -75.273 | 0.445 | 14.010 |
| 2026-08-13T02:00:00+03:00 | 126616 | 0 | 35.171 | -75.293 | 0.455 | 14.165 |
| 2026-08-13T03:00:00+03:00 | 125378 | 0 | 34.827 | -75.288 | 0.453 | 14.196 |
| 2026-08-13T04:00:00+03:00 | 127925 | 0 | 35.535 | -75.260 | 0.439 | 14.201 |
| 2026-08-13T05:00:00+03:00 | 125628 | 0 | 34.897 | -75.379 | 0.485 | 14.060 |
| 2026-08-13T06:00:00+03:00 | 123039 | 0 | 34.178 | -75.346 | 0.476 | 14.129 |
| 2026-08-13T07:00:00+03:00 | 124548 | 0 | 34.597 | -75.363 | 0.481 | 14.099 |
| 2026-08-13T08:00:00+03:00 | 118307 | 0 | 32.863 | -75.607 | 1.110 | 14.140 |
| 2026-08-13T09:00:00+03:00 | 82628 | 0 | 22.952 | -76.788 | 0.777 | 13.600 |
| 2026-08-13T10:00:00+03:00 | 89510 | 0 | 24.864 | -76.531 | 0.791 | 13.910 |
| 2026-08-13T11:00:00+03:00 | 95672 | 0 | 26.576 | -76.820 | 0.618 | 14.155 |
| 2026-08-13T12:00:00+03:00 | 92231 | 1 | 25.620 | -77.378 | 0.542 | 13.756 |
| 2026-08-13T13:00:00+03:00 | 102512 | 2 | 28.476 | -76.859 | 1.452 | 13.890 |
| 2026-08-13T14:00:00+03:00 | 97327 | 4 | 27.035 | -77.184 | 1.199 | 13.827 |
| 2026-08-13T15:00:00+03:00 | 162478 | 4 | 45.133 | -74.849 | 1.007 | 14.711 |
| 2026-08-13T16:00:00+03:00 | 144445 | 1 | 40.124 | -73.920 | 0.495 | 14.060 |
| 2026-08-13T17:00:00+03:00 | 55771 | 1 | 15.492 | -77.244 | 1.724 | 21.961 |

## Interpretation boundary

This is an unlabelled natural-operation RF/CSI dataset. It supports stability, continuity, timing-wrap, signal-variation, and data-quality claims; it does not establish human occupancy or activity-classification accuracy.
The hourly edge bins are partial clock hours, so their nominal per-hour rates are not comparable to complete middle hours without duration normalization.
CSI amplitude features are computed from a deterministic 1-in-100 envelope sample; RSSI, continuity, timing, and validity statistics use every archived record.
