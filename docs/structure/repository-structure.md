# Repository structure

```text
datasets/
  manifest.json
  ac01_.../
  ac02_.../
docs/
  architecture/
  dataset-policy/
  structure/
scripts/
  sanitize_autonomous_run.py
  sanitize_adaptive_run.py
  sanitize_json.py
```

Each dataset bundle contains `metadata.json`, `runbook.md`, `operator_notes.md`,
`SHA256SUMS`, the complete approved measurement surface, and only the compact
derived evidence listed in `datasets/manifest.json`.

New experiments receive the next `ACNN` identifier. Topology and condition are
described in metadata and are not encoded using identifiers from another
experiment series. Additions must update the manifest and repository README,
pass checksum and JSON validation, and satisfy the dataset policy.
