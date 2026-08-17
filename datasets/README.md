# Datasets

This directory contains the independent AutoCenter (`AC`) measured series.
`manifest.json` is the authoritative publication index.

Each bundle contains sanitized metadata, a runbook, operator notes, complete
published measurement chunks, integrity checksums, and only the bounded derived
evidence listed in the manifest. Long-running bundles may also contain
collector lifecycle and health records. Adaptive bundles may contain sanitized
controller decisions, parsed prplOS context, and controlled-fault ledgers.
Multiband bundles may combine independently timed sensor streams only when each
stream's timing and topology are explicit; coexistence does not imply paired or
cooperative operation.

Concrete credentials, SSIDs, addresses, MAC/BSSID values, hostnames, device
paths, board identifiers, exact site identity, raw router snapshots, and
private workflow material are excluded. Measurement timing, sequence and epoch
fields, radio measurements, CSI values, and event timing are preserved.

Verify a bundle from inside its directory with:

```sh
sha256sum -c SHA256SUMS
```

See [the dataset policy](../docs/dataset-policy/policy.md) for the complete
publication and claim-boundary rules.

Original published data, metadata, and reports are available under CC BY 4.0;
see [the repository license and attribution terms](../LICENSE.md).
