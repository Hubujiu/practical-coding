# Practical Coding benchmark report

- Model: `gpt-5.6-luna` / `medium`
- Profile: `standard`
- Runs: `3`
- Suite elapsed: `1176.8s`

## Results

| Suite | Case | Arm | n | Indeterminate | Pass | Correct | Safe | Build | LOC median | Tokens median | Uncached median | Time median |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| behavior | native-debug-over-decision | practical-native | 3 | 0 | 100.0% | — | — | — | — | 123378 | 11476 | 65.4s |
| behavior | native-debug-persistent-corruption | practical-native | 3 | 0 | 100.0% | — | — | — | — | 126806 | 11932 | 62.4s |
| behavior | native-debugging | practical-native | 3 | 0 | 100.0% | — | — | — | — | 105533 | 11047 | 43.1s |
| behavior | native-decision | practical-native | 3 | 0 | 100.0% | — | — | — | — | 63415 | 7543 | 26.3s |
| behavior | native-decision-migration-policy | practical-native | 3 | 0 | 100.0% | — | — | — | — | 63818 | 6008 | 27.0s |
| behavior | native-direct | practical-native | 3 | 0 | 100.0% | — | — | — | — | 60159 | 7746 | 18.6s |
| behavior | native-direct-diagnosed | practical-native | 3 | 0 | 100.0% | — | — | — | — | 87711 | 9380 | 32.2s |
| behavior | native-direct-known-compatibility | practical-native | 3 | 0 | 100.0% | — | — | — | — | 129597 | 9778 | 48.4s |
| behavior | native-direct-known-permission | practical-native | 3 | 0 | 100.0% | — | — | — | — | 125231 | 11060 | 47.2s |
| behavior | native-direct-known-transaction | practical-native | 3 | 0 | 100.0% | — | — | — | — | 144451 | 10346 | 54.5s |
| behavior | native-direct-settled-choice | practical-native | 3 | 0 | 100.0% | — | — | — | — | 120194 | 12553 | 59.6s |
| behavior | native-exploration | practical-native | 3 | 0 | 100.0% | — | — | — | — | 48627 | 5808 | 24.9s |
| behavior | native-implementation | practical-native | 3 | 0 | 100.0% | — | — | — | — | 175941 | 14305 | 80.3s |
| behavior | native-implementation-local-persistence | practical-native | 3 | 0 | 100.0% | — | — | — | — | 173804 | 14730 | 68.1s |
| behavior | native-implementation-local-transaction | practical-native | 3 | 0 | 100.0% | — | — | — | — | 317674 | 29152 | 151.4s |
| behavior | native-implementation-one-line-irreversible | practical-native | 3 | 0 | 100.0% | — | — | — | — | 91586 | 17046 | 39.6s |
| behavior | native-implementation-security | practical-native | 3 | 0 | 100.0% | — | — | — | — | 78355 | 9035 | 34.5s |
| behavior | native-structural-capability-fallback | practical-native | 3 | 0 | 100.0% | — | — | — | — | 87918 | 13508 | 33.2s |
| router | debug-flaky-retry | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12740 | 3761 | 6.1s |
| router | debug-named-function | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12769 | 3751 | 5.8s |
| router | debug-over-decision | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12735 | 3756 | 4.8s |
| router | debug-performance-regression | practical-current | 3 | 0 | 66.7% | — | — | — | — | 12735 | 3756 | 5.6s |
| router | debug-persistence-corruption | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12813 | 3771 | 7.1s |
| router | debug-security-symptom | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12903 | 3767 | 7.9s |
| router | debug-symptom | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12729 | 3750 | 4.8s |
| router | decision-auth | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12758 | 3747 | 5.8s |
| router | decision-dependency | practical-current | 3 | 0 | 66.7% | — | — | — | — | 12752 | 3748 | 5.3s |
| router | decision-job-runner | practical-current | 3 | 0 | 66.7% | — | — | — | — | 13144 | 3999 | 7.8s |
| router | decision-migration-policy-open | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12779 | 3769 | 5.6s |
| router | decision-schema | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12721 | 3744 | 5.1s |
| router | decision-webhook-compat | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12741 | 3764 | 5.1s |
| router | direct-artifact | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12731 | 3753 | 5.4s |
| router | direct-compat-known-adapter | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12785 | 3770 | 5.4s |
| router | direct-default | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12818 | 3751 | 6.3s |
| router | direct-existing-prop | practical-current | 3 | 0 | 33.3% | — | — | — | — | 12809 | 3759 | 6.1s |
| router | direct-known-local | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12724 | 3747 | 6.9s |
| router | direct-multifile-known | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12735 | 3758 | 4.8s |
| router | direct-persistence-known-helper | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12792 | 3770 | 5.6s |
| router | direct-private-dto | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12850 | 3766 | 6.9s |
| router | direct-security-known-guard | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12800 | 3774 | 6.1s |
| router | exploration-auth-context | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12744 | 3767 | 4.9s |
| router | exploration-broad | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12772 | 3753 | 6.1s |
| router | exploration-cbm-off | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12964 | 3762 | 9.1s |
| router | exploration-plugin-loading | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12795 | 3756 | 6.1s |
| router | implementation-contract | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12814 | 3747 | 6.8s |
| router | implementation-event-tenant | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12821 | 3765 | 6.4s |
| router | implementation-known-callers | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12735 | 3758 | 4.9s |
| router | implementation-not-files | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12721 | 3744 | 4.8s |
| router | implementation-one-line-irreversible | practical-current | 3 | 0 | 33.3% | — | — | — | — | 12839 | 3778 | 6.4s |
| router | implementation-security-local-boundary | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12782 | 3770 | 5.1s |
| router | implementation-single-file-persistence | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12800 | 3778 | 6.1s |
| router | implementation-sqlite-transaction-unknown | practical-current | 3 | 0 | 66.7% | — | — | — | — | 12843 | 3782 | 6.6s |
| router | verification-known | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12788 | 3756 | 5.8s |
| router | verification-payment-retry | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12887 | 3757 | 7.8s |
| router | verification-performance-claim | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12919 | 3759 | 8.3s |
| router | verification-risk | practical-current | 3 | 0 | 100.0% | — | — | — | — | 12806 | 3756 | 6.1s |

## Suite rollups

| Suite | Arm | Cells | Indeterminate | Pass | Correct | Safe | Tokens median | Time median |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| behavior | practical-native | 54 | 0 | 100.0% | — | — | 105354 | 43.8s |
| router | practical-current | 114 | 0 | 93.0% | — | — | 12790 | 5.9s |

## Interpretation

Correctness, safety, and build pass before LOC/tokens/time. Infrastructure, timeout, and capture failures are indeterminate and excluded from pass-rate denominators. Token totals include cached input; use uncached and output columns to interpret cost. Repeated-run standard deviations are in `summary.json`. A smoke profile is not a stable ranking.
