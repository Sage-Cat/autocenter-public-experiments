# Architecture overview

The published experiments use ESP32 sensors as CSI sources and Raspberry Pi
collectors as autonomous storage and health-monitoring nodes. AC02 adds a
controller that consumes both sensing observations and read-only context from a
separate prplOS AP.

```text
ESP32 sensor(s) -> Raspberry Pi collector(s) -> timestamp/epoch validation
                                              -> evidence admission and fusion
prplOS read-only context --------------------> adaptive policy accounting
                                              -> sanitized audit dataset
```

The production Wi-Fi network remains operational and unchanged. It supplies
the RF and management environment but is not a controlled actuator. In AC02,
the prplOS device is a separate experimental context source; its raw snapshots
are private, while bounded parsed measurements are public.

The public datasets preserve enough source timing, epoch, health, link, and
decision information to reproduce the reported integrity and failure-aware
analyses. They do not expose the private deployment configuration.
