# Dataset policy

## Purpose

Publish reproducible AutoCenter operational measurements without disclosing
private infrastructure, credentials, exact site identity, or internal workflow
material. `datasets/manifest.json` is the authoritative per-bundle inclusion
record.

## Allowed public surface

A bundle may include sanitized measurement chunks, chunk ledgers, collector
lifecycle and health records, metadata, runbooks, operator notes, controller
decisions, parsed prplOS context, controlled-fault ledgers, and compact derived
evidence required to interpret the stated claims.

Derived evidence is allowed only when it is bounded, sanitized, self-contained,
listed in the manifest, and necessary to interpret the measured surface.

## Forbidden content

Do not publish credentials, keys, tokens, concrete SSIDs, addresses, MAC/BSSID
values, hostnames, board serials, device paths, exact building identity, raw
router snapshots, private command arguments, unlisted analysis trees, caches,
intermediate models, or internal planning material.

## Sanitization

- Replace private identifiers with stable functional labels where grouping is
  scientifically useful.
- Preserve measurement timestamps, sequences, boot and connection epochs,
  radio fields, CSI values, controller decisions, and event timing.
- Convert management and prplOS output into bounded parsed measurements; do
  not publish raw configuration snapshots.
- Record failed or aborted attempts only when they are needed for auditability,
  and explicitly exclude them from positive claims.

## Claim boundary

Every bundle must state what its data support and what they do not support.
Unlabelled natural human activity is environmental context, not ground truth.
Modeled budget compliance is not proof of causal QoS improvement. Read-only
prplOS integration is not successful actuation. Missing radio bands or devices
must be stated rather than inferred.

## Integrity

Every bundle includes `SHA256SUMS`, generated after public sanitization and
identifier assignment. The manifest, metadata, reports, and actual file surface
must agree before publication.
