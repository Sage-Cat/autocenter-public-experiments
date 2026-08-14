# AC02 experiment report

## Result

Both autonomous collectors completed the scheduled 17.47-hour window. The
finalized two-node surface contains 5,024,463 envelopes and 4,999,475 valid CSI
records. Per-session collector sequence continuity is exact. Twenty-six ESP
microsecond timestamp wraps were correctly separated from reset behavior.

Across 34.932 node-hours and all readable chunks, failure-aware timing detected
all 14 boot-epoch transitions with three false events (precision 0.824, recall
1.000). Rollover-aware raw timestamps detected 12 with three false events
(precision 0.800, recall 0.857); naive regression detection also found 12 but
produced 29 false events (precision 0.293, recall 0.857). This is quantitative
evidence that explicit epoch evidence recovers resets that timestamp regression
misses, while rollover handling prevents ordinary 32-bit wraps from becoming
false resets.

The randomized ten-trial physical-reset campaign achieved 100% detection.
Median controller detection and timing recovery were 2.672 seconds, and median
full-quorum recovery was 6.670 seconds. No invalid-timing decision admitted the
failed source.

## Adaptive means and prplOS integration

The in-window stream contains 31,365 AQ-MC/SACM decisions, including 31,051
with full two-node quorum. The incumbent was held in 99.595% of decisions.
Mean predicted sensing airtime was 0.604%, and mean modeled QoS penalty was
0.124%; no predicted budget was exceeded. A read-only prplOS/pWHM context
adapter supplied 4,084 valid records, with channel utilization from 4% to 88%.

This demonstrates the software chain from multi-node CSI ingestion through
failure-aware timing, evidence admission, cooperative fusion, AQ-MC selection,
SACM maintenance, audit logging, and prplOS context consumption.

## Limitations

The main run was recommendation-oriented: only 32 in-window decisions were in
apply mode, and all 64 actuator records failed. No sensing rate or router
configuration was successfully applied. Two recommendation processes also
overlapped for 134.319 seconds after orchestration restart; derived analysis
sorts by wall time and discloses the overlap.

The failed method-block attempt, aborted mixed-fault campaign, absent rate
sweep, and absent C5 stream are retained for auditability but are not results.
Human activity was not labelled. The evidence therefore supports the timing,
failure, accounting, and read-only integration claims above, not successful
system-parameter improvement, method superiority, occupancy accuracy, 5 GHz
CSI behavior, or causal QoS benefit.
