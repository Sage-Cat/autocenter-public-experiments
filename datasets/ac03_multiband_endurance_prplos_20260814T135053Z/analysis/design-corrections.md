# Design corrections derived from AC03

AC03 validates the data plane and policy-accounting path but exposes three
implementation gaps that must be resolved before an apply-mode experiment.

## 1. Make timing validation source-order aware

The controller currently mutates timing state in UDP arrival order. AC03 proves
that this can manufacture clock resets: all 15 inferred resets correspond to
frames that are monotonic in the collector's immutable serial order.

The ingestion layer should maintain `last_committed_source_sequence` per
collector session. A late frame whose sequence is not newer may be counted as a
transport-ordering event but must not enter the affine clock estimator or
change boot epoch. A bounded reorder queue may wait briefly for small sequence
gaps; records that arrive after the bound are excluded from timing-state
mutation. Reset confirmation should require one of:

- a changed firmware-reported boot epoch;
- a new collector session plus profile/uptime evidence;
- a sustained clock regression on newly ordered records, corroborated by
  uptime or sequence restart.

Required audit counters are late frames, maximum reorder depth/time, discarded
timing updates, reported epoch changes, inferred resets, and corroboration
reason. Tests must replay the AC03 controller arrival order and assert zero
inferred resets for these 15 cases while preserving invalid-timing exclusion.

## 2. Add a C5 schema adapter before fusion

The controller parser accepts only the 25-field S3 schema. AC03's valid 5 GHz
C5 stream uses a 15-field schema with C5-specific gain and format fields. It was
therefore collected independently and cannot be claimed as cooperative input.

A canonical observation adapter should map both schemas to shared fields
(source/session/sequence, ingest clocks, local clock, RSSI, noise, channel, IQ,
boot epoch, freshness and validity) while retaining model-specific metadata.
The 7.0722-frame/s measured C5 yield, not the 40 Hz probe setting, must drive
expected-frame and reliability calculations until a controlled rate study
establishes a different model.

## 3. Require acknowledged, verified parameter transactions

Both first 10 Hz runtime-rate commands timed out, so no rate phase completed.
The controller must not treat command transmission as actuation. An apply path
needs pre-state capture, command acknowledgement, observed post-state/heartbeat
verification, timeout classification, and rollback. The same transaction rule
applies to future prplOS sensing parameters.

The next experiment should first replay AC03 offline, then run a short
controlled matrix with ordered ingestion, both S3 sources, one C5 source,
randomized source restarts, and confirmed rate transitions. prplOS and QoS
remain read-only until the sensing actuator path passes acknowledgement and
rollback gates.

## Publication consequence

The developed means can currently be described as an observe/recommend daemon
that performs multi-source admission, failure-aware timing, AQ-MC selection,
SACM maintenance, budget checks, and read-only prplOS context consumption.
AC03 does not support describing it as a closed-loop optimizer that improved
system parameters. The corrections above define the minimum evidence needed
for that stronger claim.
