# Practical Coding v1.2 benchmark evidence

This directory publishes the compact evidence for the v1.2 Retrieval refactor. It uses benchmark runner **v2.0** with `gpt-5.6-luna` at `medium` reasoning and three determinate repetitions per case.

## Final results

| Surface | Result | Interpretation |
|---|---:|---|
| Reasoning classification | 114/114 | `NONE` plus the three reasoning routes were classified correctly in every Router cell. |
| Retrieval classification | 106/114 | Eight cells disagreed only on `NONE` / `TARGETED` / `BOUNDED` / `STRUCTURAL` granularity. |
| Native behavior | 54/54 | Skill discovery, reasoning-reference isolation, structural source fallback, and Direct risk-boundary behavior passed. |
| Delivery | 27/27 | All selected implementation and build cells passed. |
| Decision | 18/18 | All selected two-turn decision cells converged. |
| Debug | 30/30 | All selected correctness and sibling-safety cells passed. |

The Router and Native Behavior results come from one 168-cell atomic run. Delivery, Decision, and Debug come from a separate 75-cell atomic Practical-only regression run. Both passed the stability gate with `n=3` and zero indeterminate cells.

## Artifacts

- [`release-summary.json`](release-summary.json): compact identities, scores, failures, and evidence limits.
- [`router-behavior-summary.json`](router-behavior-summary.json) and [`router-behavior-report.md`](router-behavior-report.md): 168-cell final Router/Native Behavior run.
- [`capability-regression-summary.json`](capability-regression-summary.json) and [`capability-regression-report.md`](capability-regression-report.md): 75-cell Delivery/Decision/Debug regression run.

## Evidence boundary

- v1.2 Router scores are not comparable with v1.1's five-way classifier: runner v2.0 records reasoning and Retrieval as independent dimensions.
- The capability regression includes only the current Practical arm. It verifies regression behavior but is not a new paired comparison against Ponytail, Superpowers, or `grilling`.
- Structural source fallback was exercised. A graph-specific cost/quality claim still requires the separately provisioned Navigation ablation.
- Raw transcripts and workspaces remain local because they are large and contain machine-specific paths.
