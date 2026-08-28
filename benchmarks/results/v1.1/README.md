# Practical Coding v1.1 benchmark results

This release replaces the older Cursor report's Practical-current values with the latest affected-surface reruns. The model was `gpt-5.6-luna` at `medium` reasoning, with isolated workspaces, pinned upstream sources, and three executions per standard case.

| Suite | Current Practical | Headline |
|---|---:|---|
| Delivery | 27/27 (100%) | Correct, safe, and production-build evidence all passed. |
| Decision | 18/18 (100%) | All two-turn convergence contracts passed. |
| Debug | 29/30 (96.7%) | Correctness 30/30; one run missed a sibling caller, so safety was 29/30. |
| Router | 114/114 (100%) | Expanded five-route regression matrix passed. |
| Native behavior | 54/54 (100%) | Native Skill discovery and exact reference loading passed. |
| Applicable total | 242/243 (99.6%) | Combined from three affected-surface reruns, not one atomic manifest. |

Published evidence:

- [`release-summary.json`](release-summary.json): compact release-level facts and limitations;
- [`delivery-decision-summary.json`](delivery-decision-summary.json): 75 Delivery/Decision/Debug cells from the v1.8 quality run; only Delivery and Decision are authoritative here because Debug was rerun afterward;
- [`debug-summary.json`](debug-summary.json): authoritative 30-cell Debug v1.9 rerun;
- [`router-behavior-summary.json`](router-behavior-summary.json): authoritative 168-cell Router/Native Behavior run;
- [`transfer-stress-summary.json`](transfer-stress-summary.json): 10-run high-pressure transfer/sibling-caller sample;
- [`REPORT_ZH.md`](REPORT_ZH.md): full Chinese report replacing the older Cursor report's current-Practical interpretation;
- [`PRACTICAL_VS_PONYTAIL_ONLY_ZH.md`](PRACTICAL_VS_PONYTAIL_ONLY_ZH.md): detailed cross-run Ponytail-only comparison.

## Evidence boundary

The current Practical figures come from separate reruns of the affected surfaces. Historical comparator and 15-arm combo figures were produced by runner v1.6, while current Practical used runner v1.8/v1.9. They use the same model, reasoning level, cases, and `n=3`, but they are not a new paired scorecard. In particular, v1.8 prepared pinned frontend dependencies before the agent ran, and v1.9 clarified one shared configuration contract.

The 15-arm matrix prompt-inlined every non-empty combination of Practical, Ponytail, Superpowers, and grill-me. That is useful interference evidence, not a universal result and not an exact simulation of every host's plugin lifecycle. The public corpus is also a regression suite rather than a hidden generalization set.

Raw transcripts, workspaces, and manifests containing machine-specific absolute paths remain local. The compact summaries preserve the measured values and exact runner/bundle identities needed to interpret the release.
