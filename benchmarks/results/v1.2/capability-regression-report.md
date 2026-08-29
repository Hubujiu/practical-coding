# Practical Coding benchmark report

- Model: `gpt-5.6-luna` / `medium`
- Profile: `standard`
- Runs: `3`
- Suite elapsed: `1258.9s`

## Results

| Suite | Case | Arm | n | Indeterminate | Pass | Correct | Safe | Build | LOC median | Tokens median | Uncached median | Time median |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| debug | security-path-containment | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 9 | 92718 | 8892 | 48.6s |
| debug | security-tenant-authorization | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 4 | 104539 | 9051 | 38.6s |
| debug | trace-amount | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 10 | 99204 | 10010 | 38.7s |
| debug | trace-cache-tenant | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 1 | 77867 | 7720 | 29.3s |
| debug | trace-config-bool | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 1 | 64469 | 6679 | 26.0s |
| debug | trace-duration-units | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 4 | 120340 | 10633 | 49.6s |
| debug | trace-header-normalize | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 1 | 77244 | 9305 | 28.0s |
| debug | trace-page-window | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 1 | 90488 | 8236 | 33.0s |
| debug | trace-transfer | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 21 | 103432 | 11019 | 52.2s |
| debug | trace-url-join | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 1 | 77287 | 7156 | 29.3s |
| decision | api-auth | practical-current | 3 | 0 | 100.0% | — | — | — | — | 40794 | 9903 | 19.4s |
| decision | api-migration | practical-current | 3 | 0 | 100.0% | — | — | — | — | 40383 | 9772 | 16.1s |
| decision | event-delivery | practical-current | 3 | 0 | 100.0% | — | — | — | — | 40599 | 9845 | 17.1s |
| decision | file-storage | practical-current | 3 | 0 | 100.0% | — | — | — | — | 40466 | 9791 | 17.4s |
| decision | pagination-contract | practical-current | 3 | 0 | 100.0% | — | — | — | — | 40482 | 9878 | 17.9s |
| decision | service-boundary | practical-current | 3 | 0 | 100.0% | — | — | — | — | 40514 | 9826 | 16.7s |
| delivery | cache | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 11 | 51910 | 6136 | 22.5s |
| delivery | critic-email | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 15 | 117069 | 10266 | 58.4s |
| delivery | reuse-money | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 9 | 80523 | 9366 | 32.1s |
| delivery | reuse-slug | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 21 | 66760 | 6777 | 30.2s |
| delivery | safe-path | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 12 | 85756 | 8642 | 51.6s |
| delivery | tmpl-be-count | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | — | 13 | 330078 | 28178 | 92.7s |
| delivery | tmpl-fe-command | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | 100.0% | 122 | 446361 | 31923 | 142.4s |
| delivery | tmpl-fe-datepicker | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | 100.0% | 53 | 415107 | 29615 | 112.2s |
| delivery | tmpl-fe-dropzone | practical-current | 3 | 0 | 100.0% | 100.0% | 100.0% | 100.0% | 87 | 415117 | 41642 | 113.8s |

## Suite rollups

| Suite | Arm | Cells | Indeterminate | Pass | Correct | Safe | Tokens median | Time median |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| debug | practical-current | 30 | 0 | 100.0% | 100.0% | 100.0% | 90924 | 37.3s |
| decision | practical-current | 18 | 0 | 100.0% | — | — | 40509 | 17.4s |
| delivery | practical-current | 27 | 0 | 100.0% | 100.0% | 100.0% | 117069 | 58.4s |

## Interpretation

Correctness, safety, and build pass before LOC/tokens/time. Infrastructure, timeout, and capture failures are indeterminate and excluded from pass-rate denominators. Token totals include cached input; use uncached and output columns to interpret cost. Repeated-run standard deviations are in `summary.json`. A smoke profile is not a stable ranking.
