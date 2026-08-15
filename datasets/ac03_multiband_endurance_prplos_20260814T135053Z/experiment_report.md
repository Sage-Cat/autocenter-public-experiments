# AC03 multiband endurance and prplOS policy report

## Result

All three available streams completed their scheduled autonomous windows. The
two 2.4 GHz ESP32-S3 nodes ran for 20 hours each and produced 5,790,272 valid
CSI records. The independent 5 GHz ESP32-C5 node ran for 18 hours and produced
458,277 valid CSI records. Across 58 scheduled sensor-hours, the bundle contains
6,290,250 finalized envelopes, 6,248,549 structurally valid finalized CSI
records, six malformed S3 CSI candidates, and exact per-session collector
source-sequence continuity. The complete public surface additionally retains
8,112 readable envelopes from one process-interrupted S3-B chunk; they are
auditable but excluded from finalized-run statistics.

The C5 stream is the first completed 5 GHz surface in this series. It remained
on channel 36 with one boot epoch, 15 ordinary 32-bit microsecond-clock wraps,
zero non-wrap regressions, and no transport reconnect. Its measured valid-CSI
yield was 7.0722 frames/s despite a nominal 40 Hz probe setting. First-to-last
heartbeat counters differ by 458,276 CSI frames and 137 output drops; these
counters and the 43 CSI-sequence-estimated missing values are separate
observations and are not added together.

## Failure-aware timing result

Offline serial-order analysis found 49 normal ESP timestamp wraps and zero
non-wrap timestamp regressions. One operator-initiated collector-host restart
during setup troubleshooting changed S3 node B's reported boot epoch and
created a 146.003-second maximum CSI gap. Its immediate technical cause was not
recorded, so it is an observed restart, not a randomized fault trial.

The retained interrupted pre-restart chunk and the first post-restart chunk
overlap by 54.617 seconds in host wall-clock labels, while their host boots,
collector sessions, source sequences, and sensor boot epochs differ. Host
health records also contain one wall/monotonic regression at this boundary.
This is restart-time clock correction, not evidence that both sensor epochs
were concurrently active. Finalized continuity is evaluated across explicit
session/boot boundaries rather than merging those wall-clock labels.

The live controller began after that restart and therefore did not detect it.
During its later window, it emitted 15 `inferred-clock-reset` events for node B,
even though the matching immutable serial records have strictly increasing
device timestamps, CSI sequences, and collector source sequences. Eleven of
the false events arrived in one short burst; event-to-decision lag ranged from
0.253 to 11.549 seconds. This identifies delayed or reordered UDP delivery as a
failure mode in the current live timing validator. The controller rejected the
source in both decisions where timing was invalid, so no invalid-timing source
was admitted, but one full-quorum decision was lost during the burst.

This is a useful negative validation result: a raw timestamp regression must
not create a new boot epoch until records are ordered by per-session source
sequence or pass through a bounded reorder buffer. Reported boot epoch,
profile/uptime reset evidence, and source-session boundaries should remain the
authoritative reset evidence.

## Adaptive means and prplOS context

The bounded controller surface contains 34,407 AQ-MC/SACM decisions over
19.114 hours. All were in recommendation mode; 34,311 had full two-node quorum,
34,328 held the incumbent configuration, 64 accepted a proposal, and 15 used
fallback. Every modeled budget was feasible. Mean predicted sensing airtime
was 0.6059%, and mean modeled QoS penalty was 0.1220%.

The read-only prplOS adapter supplied 4,486 valid channel-36 context records.
Maximum radio utilization ranged from 8% to 67% with an 11.645% mean. The
production Wi-Fi network was not reconfigured. The controller made no actuator
call, the attempted runtime-rate sweep failed at its first 10 Hz commands, and
the planned method blocks were not executed. The C5 stream was collected
independently and was not fused by this S3-only controller version.

The evidence therefore validates autonomous collection, cooperative S3 policy
accounting, budget guardrails, invalid-timing exclusion, multiband observation,
and read-only prplOS context consumption. It does not demonstrate actual system
parameter improvement or causal QoS benefit.

## Signal and continuity summary

| Source | Band/channel | Valid CSI | Mean RSSI | RSSI SD | Clock wraps | Non-wrap regressions | Longest CSI gap |
|---|---|---:|---:|---:|---:|---:|---:|
| S3 node A | 2.4 GHz / 2 | 2,893,507 | -66.540 dBm | 0.649 dB | 17 | 0 | 12.863 s |
| S3 node B | 2.4 GHz / 2 | 2,896,765 | -85.295 dBm | 1.411 dB | 17 | 0 | 146.003 s |
| C5 node A | 5 GHz / 36 | 458,277 | -78.304 dBm | 4.439 dB | 15 | 0 | 1.592 s |

The signal differences are descriptive properties of three different links;
they are not a controlled band comparison. Human activity was not labelled and
cannot be inferred as ground truth from CSI variation.

Collector A remained on one host boot with synchronized system time throughout
both overlapping captures; its maximum observed host temperature was 67.75 C.
Collector B's health stream contains the documented restart and two host boot
epochs; after recovery it completed the run, with a maximum observed host
temperature of 60.6 C. Sensor temperature ranges were 54.4–57.4 C for S3-A,
44.8–51.8 C for S3-B, and 46.6–48.6 C for C5-A.

## Claim boundary

AC03 is claim-grade for autonomous multiband endurance, archive integrity,
serial-order rollover discrimination, descriptive continuity/signal results,
invalid-timing admission safety, AQ-MC/SACM budget accounting, and read-only
prplOS integration. It is not claim-grade for live inferred-reset precision,
controlled-fault recall, successful actuation, rate adaptation, method
superiority, paired-C5 cooperation, causal QoS improvement, or occupancy and
activity accuracy.
