# Provenance and privacy disclosure

## Research independence

The AutoCenter experiments were designed, installed, operated, analyzed, and
published by an independent individual researcher. The work was self-funded.
There were no sponsors, grants, commercial funders, sponsor-directed research
questions, or sponsor approval rights. Product and project names identify
technical components only; they do not indicate endorsement or sponsorship.

## Operational setting and people

Measurements were performed with permission in an operational retail area.
People could naturally pass through the radio environment, but they were not
recruited, assigned participant identifiers, counted, interviewed, or given
activity labels. No attempt is made to identify a person or connect a radio
observation to an individual.

The collection contains no camera images, video, audio, names, demographic
attributes, questionnaires, user-device identifiers, or network payloads. The
public claim surface treats natural human activity only as unlabelled
environmental variability. It does not support person identification,
participant-level analysis, or occupancy-classification accuracy.

## Infrastructure privacy

The public bundles exclude the exact site identity and address, photographs,
credentials, concrete SSIDs, IP addresses, original MAC/BSSID values,
hostnames, board serials, device paths, private command arguments, SSH
material, and raw router configuration snapshots. Stable grouping uses locally
administered synthetic identifiers in the `02:00:00:00:00:xx` namespace.
Values ending in `fd` or `fe` are documented sentinels for damaged partial
identifiers created by serial-line collisions; they are not device addresses.

The author name and email in Git commit metadata are intentionally public
publication metadata and are not embedded in the measured datasets.

## Audit record

Before publication, every plain and gzip-compressed dataset artifact was read
and checked for:

- credentials, private-key or access-token signatures;
- email addresses and user-specific filesystem paths;
- private IPv4 addresses and concrete device paths;
- populated SSID, host, or credential fields;
- exact-location fields;
- MAC-like values outside the documented synthetic namespace;
- identifiers belonging to the unrelated CWS Lab dataset series.

Candidate matches were manually classified by their structured field and
context. They were measurement numerics or documented synthetic sentinels, not
private values. The final structured audit reports no privacy findings. Bundle
checksums are regenerated after any metadata change and verified before push.

This is a technical data-minimization statement, not a legal determination for
every jurisdiction or every possible downstream use. Reusers must respect the
published claim boundaries and must not attempt to infer or re-identify people.
