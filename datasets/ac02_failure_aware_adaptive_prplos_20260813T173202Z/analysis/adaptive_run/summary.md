# AC02 adaptive two-node analysis

## Result

The two collectors completed the scheduled 17.47-hour run with 5,024,463
finalized envelopes, including 4,999,475 structurally valid CSI records. Both
collector streams have exact per-session source-sequence continuity. The
finalized CSI contains 26 valid 32-bit microsecond timestamp wraps and four
malformed CSI candidates.

The timing ablation uses every readable finalized and process-interrupted
chunk: 34.932 node-hours, 14 observed boot-epoch transitions, and 26 timestamp
wraps. Failure-aware timing detected all 14 transitions with three false reset
events (precision 0.824, recall 1.000). Rollover-aware handling detected 12
with three false events (precision 0.800, recall 0.857). Naive regression
handling detected 12 but produced 29 false events (precision 0.293, recall
0.857). The failure-aware envelope therefore recovers transitions that raw
timestamp regression alone misses while correctly distinguishing all wraps.

## Controlled failures

The randomized physical-reset campaign completed ten trials, five per node.
All ten were detected. Median controller detection and timing recovery were
2.672 seconds, and median full two-node quorum recovery was 6.670 seconds.
Maximum detection was 2.882 seconds; maximum quorum recovery was 6.861
seconds. No decision admitted a source with invalid timing.

## Adaptive policy and prplOS context

The scheduled window contains 31,365 AQ-MC/SACM decisions. Full two-node
quorum was available in 31,051 decisions. SACM held its incumbent in 99.595%
of decisions. Mean predicted sensing airtime was 0.604% and mean modeled QoS
penalty was 0.124%, with no predicted budget violation.

The read-only prplOS adapter supplied 4,084 valid context records. Its measured
channel utilization averaged 10.54% and ranged from 4% to 88%. These values
were policy inputs; the experiment did not alter the production network.

## Quality and claim boundary

The raw controller append stream contains three process segments; two
recommendation processes overlapped for 134.319 seconds after orchestration
restart. Derived temporal analysis sorts decisions by wall time and reports
the overlap. Six NUL-prefixed auxiliary records and one text-prefixed operator
event were recoverable with no JSON loss; immutable private bytes are retained.

Only 32 in-window decisions were in apply mode, producing 64 failed actuator
records and no successful actuation. A planned mixed-fault campaign was
aborted before collection became active, and a planned method-block comparison
failed its precondition. No C5 data or 5 GHz CSI was captured, and no human
activity was labelled. This dataset therefore supports timing, failure,
policy-accounting, and read-only prplOS-integration claims—not successful
configuration improvement, method superiority, activity accuracy, or causal
QoS improvement.
