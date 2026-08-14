# Timing-method ablation

Node-hours: 34.932; boot-epoch transitions: 14; timestamp wraps: 26.

| Method | TP | FP | FN | Precision | Recall | False resets/node-hour |
|---|---:|---:|---:|---:|---:|---:|
| failure-aware | 14 | 3 | 0 | 0.8235294117647058 | 1.0 | 0.0858805854482024 |
| naive-reset-on-regression | 12 | 29 | 2 | 0.2926829268292683 | 0.8571428571428571 | 0.8301789926659565 |
| rollover-aware | 12 | 3 | 2 | 0.8 | 0.8571428571428571 | 0.0858805854482024 |
