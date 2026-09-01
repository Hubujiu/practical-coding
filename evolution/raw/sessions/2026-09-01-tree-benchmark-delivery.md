# Experience receipt: tree benchmark delivery loop

```yaml
id: exp-20260901-tree-benchmark-delivery
source_type: benchmark
source_pointer: benchmark-results/tree-delivery-*; current maintenance session transcript intentionally not stored
repository_family: practical-coding
task_family: quality
skill_commit: 31ba37c9c324ff5863ee237a8c89203f4405fbe9
model_harness: Codex CLI + benchmarks/tree_validation.py
execution_depth: unknown
retrieval_depth: unknown
capability_path: []
outcome: indeterminate
quality_gates:
  correctness: unknown
  safety: unknown
  build_reachability: unknown
cost:
  tokens: null
  seconds: null
  tool_calls: null
  loc: null
routing_observation: unknown
mechanism: delivery requires n=1 mechanism iteration with preserved full artifacts, followed only after a frozen candidate by a same-contract n=3 comparison against the frozen v1.5 and no-skill arms.
user_feedback: wait for each benchmark process to finish before reading its complete report, continuously consolidate reusable evidence into the wiki, and deliver only when comparable benchmark evidence improves on the previous report.
candidate_lesson: treat delivered quality and historical comparability as gates; topology diagnostics and a favorable single repetition are not delivery evidence.
```

## Evidence selected before the first run

- The checkout is the clean `experiment/evolvable-router-tree` branch at `31ba37c`.
- The active runner has 15 frozen tasks across three repositories, including two explicit manual Decision tasks.
- The topology stages four depth-2 children whose independent lift over their parents is not yet established.
- The frozen comparable baseline is v1.5 at `ba4058b4ef47a42bf79c9963b25678a2389897c1`.

## Contradictions / uncertainty

- `benchmarks/NEXT_VALIDATION.md` still describes the older event-router restoration branch and is not the active tree final gate.
- No fresh current-candidate model-backed result exists yet, so this receipt remains indeterminate until benchmark artifacts are appended through new receipts or wiki log entries; this immutable receipt will not be rewritten.
