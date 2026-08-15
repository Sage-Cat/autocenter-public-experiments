# Public operator notes

- Both S3 endpoints remained fixed in a naturally used retail passage at
  approximately 1.2 m height and 17 m endpoint separation.
- The existing Wi-Fi network remained enabled and unchanged throughout the
  run. It is treated as natural interference.
- Customers and staff could use the area normally, but no person, count, or
  activity timeline was recorded as ground truth.
- S3 nodes A and B collected 2.4 GHz CSI. C5 node A independently collected
  5 GHz CSI on the collector at endpoint A.
- A second C5 board remained powered at endpoint B but did not enumerate as a
  USB data device, so no C5-B stream exists and no paired-C5 claim is made.
- The endpoint-B collector host was manually restarted during C5-B setup
  troubleshooting. The restart and resulting S3 boot-epoch transition are
  retained, but the immediate technical cause is unconfirmed.
- Its interrupted pre-restart chunk and first post-restart chunk have
  overlapping host wall-clock labels after clock correction. Their distinct
  host boots, collector sessions, and sensor epochs prevent them from being
  interpreted as simultaneous measurements.
- The controller was started only after that restart. No deliberate fault was
  injected during the controller window.
- All three available streams stopped normally at their scheduled endpoints.
- The exact site identity, photographs, production-network identifiers,
  machine names, addresses, device paths, and credentials are private.
