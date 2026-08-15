# AC03 quality-control summary

- Verdict: `claim-grade for endurance, integrity, and bounded policy-accounting scope only`
- Scheduled completion: passed on all three streams (`duration-complete`)
- Original source checksum verification: 247/247 S3-A, 248/248 S3-B, 222/222 C5-A
- Public/finalized/process-interrupted chunks: 697/696/1
- Public/finalized/process-interrupted envelopes: 6,298,362/6,290,250/8,112
- Structurally valid finalized CSI: 6,248,549
- Malformed finalized CSI candidates: 6, all on S3 streams
- Per-session collector source-sequence gaps/duplicates/regressions: 0/0/0
- CSI sequence-estimated missing values: 587
- ESP timestamp wraps/offline non-wrap regressions: 49/0
- Scheduled sensor-hours: 58.0
- Observed boot-epoch transitions: 1
- Pre/post-restart host wall-label overlap: 54.617 seconds, separated by
  collector session, host boot, and sensor boot epoch
- Planned or randomized fault trials: 0
- Live inferred resets disproved by serial order: 15/15
- Invalid-timing decisions admitted: 0
- Controller decisions/full-quorum decisions: 34,407/34,311
- Predicted AQ-MC budget violations: 0
- Successful actuator records: 0
- Valid bounded prplOS context records: 4,486
- Completed rate-sweep phases/method blocks: 0/0
- C5-B records: 0; no paired-C5 claim
- Human activity ground truth: absent by design
- Full compressed/uncompressed AC03 privacy scan: passed, 734 artifacts and 0 findings

## Claim gate

The bundle passes source integrity, scheduled completion, complete public
measurement-surface, rollover discrimination, per-session collector continuity,
multiband descriptive measurement, invalid-timing exclusion, policy-budget
accounting, read-only prplOS context, and privacy gates. It fails the live
inferred-reset precision, controlled-fault recall, successful-actuation,
completed-rate-sweep, completed-method-comparison, paired-C5, causal-QoS, and
activity-ground-truth gates. The final public checksum gate is recorded in
`SHA256SUMS`.
