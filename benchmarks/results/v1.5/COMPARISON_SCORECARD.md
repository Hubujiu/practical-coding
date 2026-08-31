# v1.5 unified release scorecard

Release gate: **FAIL**

All rows use common cases and the active scorer. Lower token, time, tool, and LOC values are better.

| Suite | Arm | Pass | Correct | Safe | Build | Uncached input median | Output median | Total tokens median | Time median | Tools median | LOC median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| delivery | current | 54/54 (100.0%) | 100.0% | 100.0% | 100.0% | 20,601.5 | 2,708.0 | 205,214.5 | 74.6s | 8.0 | 21.0 |
| delivery | previous | 54/54 (100.0%) | 100.0% | 100.0% | 100.0% | 21,578.5 | 2,495.5 | 176,889.5 | 71.1s | 7.5 | 19.5 |
| delivery | baseline | 54/54 (100.0%) | 100.0% | 100.0% | 100.0% | 17,483.5 | 2,704.0 | 197,269.0 | 73.5s | 8.0 | 24.5 |
| delivery | ponytail | 53/54 (98.1%) | 100.0% | 100.0% | 94.4% | 20,521.0 | 2,332.5 | 188,596.0 | 59.4s | 8.0 | 19.0 |
| debug | current | 40/42 (95.2%) | 100.0% | 95.2% | — | 10,082.5 | 1,424.0 | 94,801.5 | 37.3s | 6.0 | 1.5 |
| debug | previous | 39/42 (92.9%) | 100.0% | 92.9% | — | 9,583.0 | 1,243.0 | 91,712.5 | 35.1s | 6.0 | 1.0 |
| debug | superpowers | 36/42 (85.7%) | 100.0% | 85.7% | — | 22,313.5 | 3,220.5 | 277,643.5 | 79.7s | 14.0 | 1.0 |
| decision | current | 29/30 (96.7%) | — | — | — | 9,369.5 | 792.0 | 41,158.5 | 17.5s | 0.0 | — |
| decision | previous | 30/30 (100.0%) | — | — | — | 10,193.0 | 775.5 | 41,964.5 | 17.4s | 0.0 | — |
| decision | grilling | 29/30 (96.7%) | — | — | — | 7,197.5 | 942.0 | 37,072.5 | 20.3s | 0.0 | — |
| router | current | 107/114 (93.9%) | — | — | — | 4,025.5 | 78.5 | 13,070.5 | 6.2s | 0.0 | — |
| router | previous | 96/114 (84.2%) | — | — | — | 4,013.0 | 112.0 | 13,087.5 | 6.8s | 0.0 | — |
| behavior | current | 53/54 (98.1%) | — | — | — | 10,338.0 | 1,421.5 | 98,591.0 | 39.6s | 6.0 | — |
| behavior | previous | 53/54 (98.1%) | — | — | — | 9,896.0 | 1,465.5 | 102,874.5 | 40.2s | 7.0 | — |

## Current vs previous gate

- delivery: **FAIL**
  - output_tokens_median: 2708.000 > 2495.500
  - total_tokens_median: 205214.500 > 176889.500
  - duration_seconds_median: 74.552 > 71.118
  - tool_calls_median: 8.000 > 7.500
  - total_loc_median: 21.000 > 19.500
- debug: **FAIL**
  - uncached_input_tokens_median: 10082.500 > 9583.000
  - output_tokens_median: 1424.000 > 1243.000
  - total_tokens_median: 94801.500 > 91712.500
  - duration_seconds_median: 37.290 > 35.147
  - total_loc_median: 1.500 > 1.000
- decision: **FAIL**
  - pass_rate: 0.966667 < 1.000000
  - output_tokens_median: 792.000 > 775.500
  - duration_seconds_median: 17.485 > 17.398
- router: **FAIL**
  - uncached_input_tokens_median: 4025.500 > 4013.000
- behavior: **FAIL**
  - uncached_input_tokens_median: 10338.000 > 9896.000

## Evidence boundary

- Model executions are cross-run; scoring is current and common-case only.
- Historical workspaces and transcripts are read-only and are not overwritten.
- Stored build outcomes are reused; model execution and builds are not rerun.
- External arms are contextual comparisons and do not control the current-vs-previous release gate.
