# v1.5 unified release scorecard

Release gate: **FAIL**

All rows use common cases and the active scorer. Lower token, time, tool, and LOC values are better.

| Suite | Arm | Pass | Correct | Safe | Build | Uncached input median | Output median | Total tokens median | Time median | Tools median | LOC median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| delivery | current | 18/18 (100.0%) | 100.0% | 100.0% | 100.0% | 20,395.0 | 2,128.0 | 171,643.0 | 64.1s | 8.0 | 19.5 |
| delivery | previous | 54/54 (100.0%) | 100.0% | 100.0% | 100.0% | 21,578.5 | 2,495.5 | 176,889.5 | 71.1s | 7.5 | 19.5 |
| delivery | baseline | 54/54 (100.0%) | 100.0% | 100.0% | 100.0% | 17,483.5 | 2,704.0 | 197,269.0 | 73.5s | 8.0 | 24.5 |
| delivery | ponytail | 53/54 (98.1%) | 100.0% | 100.0% | 94.4% | 20,521.0 | 2,332.5 | 188,596.0 | 59.4s | 8.0 | 19.0 |
| debug | current | 14/14 (100.0%) | 100.0% | 100.0% | — | 11,134.0 | 1,170.0 | 86,159.5 | 34.3s | 5.0 | 1.5 |
| debug | previous | 39/42 (92.9%) | 100.0% | 92.9% | — | 9,583.0 | 1,243.0 | 91,712.5 | 35.1s | 6.0 | 1.0 |
| debug | superpowers | 36/42 (85.7%) | 100.0% | 85.7% | — | 22,313.5 | 3,220.5 | 277,643.5 | 79.7s | 14.0 | 1.0 |
| decision | current | 10/10 (100.0%) | — | — | — | 9,644.5 | 727.0 | 40,323.5 | 18.0s | 0.0 | — |
| decision | previous | 30/30 (100.0%) | — | — | — | 10,193.0 | 775.5 | 41,964.5 | 17.4s | 0.0 | — |
| decision | grilling | 29/30 (96.7%) | — | — | — | 7,197.5 | 942.0 | 37,072.5 | 20.3s | 0.0 | — |
| router | current | 34/38 (89.5%) | — | — | — | 3,765.5 | 76.5 | 12,811.0 | 6.3s | 0.0 | — |
| router | previous | 96/114 (84.2%) | — | — | — | 4,013.0 | 112.0 | 13,087.5 | 6.8s | 0.0 | — |
| behavior | current | 18/18 (100.0%) | — | — | — | 9,873.5 | 1,259.0 | 101,176.5 | 37.1s | 6.5 | — |
| behavior | previous | 53/54 (98.1%) | — | — | — | 9,896.0 | 1,465.5 | 102,874.5 | 40.2s | 7.0 | — |

## Current vs previous gate

- delivery: **FAIL**
  - tool_calls_median: 8.000 > 7.500
- debug: **FAIL**
  - uncached_input_tokens_median: 11134.000 > 9583.000
  - total_loc_median: 1.500 > 1.000
- decision: **FAIL**
  - duration_seconds_median: 18.015 > 17.398
- router: **PASS**
- behavior: **PASS**

## Evidence boundary

- Model executions are cross-run; scoring is current and common-case only.
- Historical workspaces and transcripts are read-only and are not overwritten.
- Stored build outcomes are reused; model execution and builds are not rerun.
- External arms are contextual comparisons and do not control the current-vs-previous release gate.
