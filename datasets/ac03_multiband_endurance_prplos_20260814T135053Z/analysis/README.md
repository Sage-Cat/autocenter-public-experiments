# AC03 analysis methods

## Measurement parsing

S3 CSI records use the 25-field firmware schema. Structural validation requires
CSV parsing, numeric control fields, a bracketed IQ vector, and equality between
the declared and observed vector length. C5 records use the 15-field C5 schema;
the same vector-length rule applies at the C5-specific indices. A serial line
that begins with firmware log text rather than `CSI_DATA,` is retained as an
auxiliary record and is not repaired into a CSI frame.

All envelope and CSI counts use finalized readable chunks. The retained
process-interrupted S3-B chunk is part of public artifact accounting but is not
silently treated as finalized. Collector source-sequence continuity is measured
within each collector session. CSI sequence changes across a reported boot
boundary are reported separately from within-session loss.

Signal mean and population standard deviation use every structurally valid CSI
record. Longest gaps use ingest wall time between consecutive valid CSI records
in source order. The reported rate is valid CSI divided by the observed span;
the nominal probe rate is configuration, not an observed CSI yield.

## Clock and restart classification

ESP local timestamps are interpreted as unsigned 32-bit microseconds. A
regression is a wrap only when the prior value is above 75% and the new value is
below 25% of the 32-bit range. Reported boot epochs and collector-session
boundaries are analyzed independently. Natural wraps, explicit boot changes,
transport loss, and collector-host restart are not collapsed into one event.
Host wall time is not assumed monotonic across a host reboot. The 54.617-second
wall-label overlap at the S3-B restart is partitioned by host boot, collector
session, and sensor boot epoch; the interrupted chunk is not merged into the
finalized post-restart stream.

The live false-reset audit joins each controller event to the immutable serial
envelope by `ingest_wall_time_ns`. It then compares the event frame with its
immediate serial predecessor. All 15 matched pairs have increasing raw device
timestamp and increasing collector source sequence, disproving a source-clock
reset at those points. Decision lag is controller decision wall time minus the
matched envelope's ingest wall time.

## Controller accounting

Controller, network-context, and prplOS-context artifacts are bounded to the S3
collection wall-time interval. Decision counts, quorum, SACM action, load, and
AQ-MC budget fields are direct aggregations. prplOS utilization uses only parsed
records marked valid; raw device snapshots are excluded.

The controller started after the observed S3-B restart. Consequently, the run
contains no positive live reset trial from which controller recall can be
estimated. The 15 disproved inferences are a defect-finding result, not a
controlled failure-detection benchmark.

## Reuse boundary

The three RF links differ in endpoint hardware and link geometry. Their signal
statistics must not be used as a controlled band comparison. Human activity is
unlabelled, and CSI variation must not be converted into occupancy or activity
ground truth.
