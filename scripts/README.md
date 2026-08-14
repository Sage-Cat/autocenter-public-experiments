# Public sanitizers

- `sanitize_autonomous_run.py` creates the AC01-style public surface from an
  authorized finalized single-collector archive.
- `sanitize_adaptive_run.py` creates the AC02-style two-node, controller, and
  prplOS-context public surface.
- `sanitize_json.py` provides shared streaming normalization helpers.
- `audit_public_privacy.py` exhaustively scans plain and gzip-compressed
  dataset artifacts for structured privacy violations without printing matched
  values.

The scripts intentionally require explicit source and destination arguments.
Private identifier mappings are publication inputs and are never committed.
Run them only on an authorized archive, then validate every generated checksum,
JSON/NDJSON record, and privacy rule before publication.

Run the public privacy gate with:

```sh
python3 scripts/audit_public_privacy.py datasets
```
