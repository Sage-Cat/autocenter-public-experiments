# AC01 quality-control summary

- Verdict: `usable as a claim-grade 24-hour stability/timing baseline`
- Scheduled completion: passed (`duration-complete`)
- Finalized chunks: 288/288
- Unique chunk paths: 288/288
- Public ledger versus parsed-envelope difference: 0
- Measurement envelopes: 2,878,787
- Envelope JSON errors: 0
- Valid CSI records: 2,861,493
- Malformed CSI candidates: 16 (0.000559%)
- Estimated missing CSI sequence values: 621 (0.021697%)
- Collector source-sequence gaps/duplicates/regressions: 0/0/0
- CSI duplicates/regressions: 0/0
- ESP timestamp wraps/non-wrap regressions: 20/0
- Serial transport disconnects: one, 2.007604 seconds
- Firmware boot epochs: one
- Collector boot IDs: one
- Collector clock synchronized: 8,613/8,613 health samples
- Collector wall/monotonic regressions: 0/0
- Collector maximum temperature: 60.6 C
- Feature samples: 28,595; IQ parse errors: 0
- Public identifier/privacy scan: passed

## Claim gate

The bundle passes the integrity, continuity, long-run hardware, rollover, and
transport-failure evidence gates. It fails by design any occupancy/activity
accuracy gate because it has no human ground-truth labels. It is single-node
evidence and is not a cooperative multi-node performance comparison.
