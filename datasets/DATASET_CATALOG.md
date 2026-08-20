# Record-Level Dataset Catalog

All three AutoCenter bundles already contain downloadable, measured,
record-level CSI/RSSI data. CSI is stored inside the `raw` field of each
gzip-compressed NDJSON measurement envelope; it is not withheld behind a
request form or private archive.

| Bundle | Valid full-vector CSI records | Direct data path | Notes |
| --- | ---: | --- | --- |
| AC01 | 2,861,493 | [`serial/chunks/`](ac01_natural_operation_baseline_20260812T142321Z/serial/chunks/) | One ESP32-S3 stream; 16 malformed CSI candidates are disclosed in the analysis. |
| AC02 | 4,999,475 | [`serial/node-a/chunks/`](ac02_failure_aware_adaptive_prplos_20260813T173202Z/serial/node-a/chunks/) and [`serial/node-b/chunks/`](ac02_failure_aware_adaptive_prplos_20260813T173202Z/serial/node-b/chunks/) | Two ESP32-S3 streams; four malformed candidates in finalized data. |
| AC03 | 6,248,549 | [`serial/`](ac03_multiband_endurance_prplos_20260814T135053Z/serial/) | Two 2.4 GHz ESP32-S3 streams and one 5 GHz ESP32-C5 stream; six malformed candidates disclosed. |

The counts come from the published bundle analyses and refer to validated CSI
records, not all envelopes. Each `raw` value is the original sanitized
`CSI_DATA,...` record and includes the complete signed I/Q vector: 256 values
for the S3 capture profiles and 106 values for the C5 profile. The surrounding
envelope retains public source/session aliases, sequence and connection-epoch
fields, and host/device timing needed for integrity and continuity analysis.

Run `sha256sum -c SHA256SUMS` inside a bundle before analysis. The repository
uses ordinary Git objects rather than a gated dataset service; individual
chunk files can be downloaded directly from GitHub, or the whole repository
can be cloned.
