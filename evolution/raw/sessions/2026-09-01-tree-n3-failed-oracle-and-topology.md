# Receipt — paired n=3 failed release gate

## Immutable input

- Candidate commit: `eca9a090d04492addaf4e2bb6d8dbec3e61bc0d0`
- Frozen baseline: `ba4058b4ef47a42bf79c9963b25678a2389897c1`
- Raw output: `benchmark-results/tree-final-eca9a09-20260901`
- Matrix: 15 tasks, 408/408 determinate cells, three repetitions per comparable arm/capability cell

## Result

- Adaptive: 40/45, 88.9%, 12 stable tasks
- Frozen v1.5: 44/45, 97.8%, 14 stable tasks
- No-skill: 41/45, 91.1%, 13 stable tasks
- Adaptive trace validity: 45/45
- Explicit manual Decision adherence: 6/6
- Spontaneous manual activation: 0/39 automatic cells
- Release quality gate: **FAIL**

This artifact is diagnostic evidence only and must not be presented as a delivery comparison.

## Failure classification

Five adaptive failures were deterministic-oracle mismatches: three rejected `Decision: choose` recommendations (one also used `cost` for the downside), one rejected an exact blocked focused-test outcome, and one required `EditorShell` despite an authoritative `exportCover` cancellation/download-boundary diagnosis.

Separately, repeated capability ablation found no depth-2 staged node in any minimum-sufficient set. That topology observation is deferred until the scorer correction completes a fresh n=1 iteration.
