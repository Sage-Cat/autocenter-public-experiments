# AC02 quality-control summary

- Verdict: `claim-grade for timing/failure and policy-accounting scope only`
- Scheduled completion: passed on both collectors (`duration-complete`)
- Original source checksum verification: 222/222 files per collector
- Finalized chunks: 208 per node, 416 total
- Retained process-interrupted chunks: 7 per node, 14 total
- Finalized envelopes: 5,024,463
- Structurally valid finalized CSI: 4,999,475
- Malformed finalized CSI candidates: 4
- Per-session collector source-sequence gaps/duplicates/regressions: 0/0/0 on both nodes
- CSI sequence-estimated missing values: 476
- ESP timestamp wraps/non-wrap regressions: 26/6 in finalized chunks
- Low-level timing-ablation node-hours: 34.932
- Observed boot-epoch transitions: 14
- Controlled physical resets detected: 10/10
- Invalid-timing controller decisions admitted during controlled resets: 0
- In-window controller decisions/full-quorum decisions: 31,365/31,051
- Predicted AQ-MC budget violations: 0
- Successful/failed actuator records: 0/64
- Valid in-window prplOS context records: 4,084/4,084
- Recovered/unrecovered auxiliary JSON damage: 7/0
- Controller process overlap: 134.319 seconds, explicitly reported
- Full compressed/uncompressed identifier and private-network privacy scan: passed

## Claim gate

The bundle passes source integrity, complete-public-surface, rollover,
boot-epoch transition, controlled reset detection/recovery, cooperative quorum,
policy-budget accounting, and read-only prplOS context gates. It fails the
successful-actuation gate and, by design, the occupancy/activity accuracy,
C5/5 GHz CSI, completed method-comparison, and causal QoS-improvement gates.
