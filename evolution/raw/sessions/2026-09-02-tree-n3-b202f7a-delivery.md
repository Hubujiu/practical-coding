# Receipt — evolvable leaf tree paired n=3 delivery

- Candidate commit: `b202f7a165ae3ea4404d404bb1235ebf4270cbfb`
- Frozen baseline: `ba4058b4ef47a42bf79c9963b25678a2389897c1`
- Artifact: `benchmark-results/tree-final-b202f7a-20260902`
- Model/reasoning: `gpt-5.6-luna` / `medium`
- Repositories/tasks/runs: 3 / 15 / 3
- Completeness: 252/252 determinate cells
- Adaptive/frozen-v1.5/no-skill quality: 45/45, 44/45, 44/45
- Core/Debugging/Implementation ceilings: 39/39 each
- Adaptive trace: 45/45
- Explicit manual contract: 6/6
- Spontaneous manual activation: 0/39 automatic cells
- Adaptive mean tokens/duration/tools: 258,061.64 / 76.82s / 8.42
- v1.5 mean tokens/duration/tools: 217,460.96 / 72.20s / 7.24
- Release quality gate: PASS

Baseline missed one `sa-memory-strategy-manual-decision` repetition by omitting the SlidingWindow alternative. No-skill missed one `ca-cancel-download` repetition by omitting focused-test evidence. Adaptive passed every repetition. Raw paths and full transcripts remain only in the ignored local artifact.
