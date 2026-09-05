# Receipt — leaf candidate paired n=3 failed

## Immutable input

- Candidate commit: `67f2f5c72d5db3ef461fb60e6a60a77351b1a8a9`
- Frozen baseline: `ba4058b4ef47a42bf79c9963b25678a2389897c1`
- Artifact: `benchmark-results/tree-final-67f2f5c-20260901`
- Completeness: 252/252 cells, three repetitions per comparable arm/capability cell

## Result

- Adaptive: 41/45, 91.1%
- Frozen v1.5: 44/45, 97.8%
- No-skill: 45/45, 100%
- Core ceiling: 38/39
- Debugging ceiling: 35/39
- Implementation ceiling: 36/39
- Trace validity: 44/45
- Explicit manual success: 5/6
- Spontaneous manual activation: 0
- Delivery decision: **Rejected**

The analyzer then crashed on the already-invalid retired node `state-concurrency`; the raw matrix and `report.json` remain complete, while `analysis.json` was not produced. This artifact is diagnostic only.

## Classification

Three failures are general evidence-identity/oracle defects. One is a real runtime isolation defect: a retired depth-2 reference remained discoverable and was loaded despite the active leaf topology. Both classes require new n=1 hypotheses; this result cannot be rescored into delivery evidence.
