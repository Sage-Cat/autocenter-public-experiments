# AC01 experiment report

## Result

The autonomous single-node system completed a full 24-hour natural-operation
capture with 2,878,787 preserved envelopes and exact collector-envelope
sequence continuity. Of 2,861,509 CSI candidates, 2,861,493 were structurally
valid; 16 were malformed (0.000559%). The CSI sequence implied 621 missing
values (0.021697%), while the firmware output-drop counter increased by 1,199
(0.041894% of its CSI-count increase). These are distinct observations and are
not summed.

The timing surface contained 20 legitimate 32-bit microsecond timestamp wraps
and zero non-wrap regressions. One 2.008-second serial interruption reconnected
without changing the firmware boot epoch. The longest CSI-only gap was 32.618
seconds, but the longest gap across all envelopes was 6.767 seconds because
heartbeats continued through part of the sensing silence. This directly
supports failure-class separation between CSI-path silence, serial transport
failure, timestamp rollover, and node reboot.

The Raspberry Pi collector retained one boot identity, synchronized system
time in every one of 8,613 samples, continuous management Wi-Fi, no timestamp
regressions, a mean temperature of 55.79 C, and a maximum of 60.6 C. This is
strong evidence that the 24-hour data loss characteristics were not caused by
collector reboot, thermal instability, or clock loss.

## Radio observations

All valid CSI was collected on 2.4 GHz channel 2 from one pseudonymized AP.
RSSI averaged -75.660 dBm with 1.074 dB standard deviation and a -96 to -69 dBm
range. The firmware-reported noise floor remained fixed at -99 dBm and is not
treated as a useful time-varying interference covariate. Sampled CSI mean
amplitude averaged 14.279 and sampled RMS amplitude averaged 17.196.

## Evidence boundary

The scene was naturally occupied during normal operation, but no people or
activities were labelled. Hourly signal and amplitude changes therefore show
real operational RF variability only. They cannot be attributed to human
presence, customer count, or a particular activity. The dataset is claim-grade
for the stated stability and failure-aware timing results, not for sensing
classification accuracy or cooperative multi-node benefit.
