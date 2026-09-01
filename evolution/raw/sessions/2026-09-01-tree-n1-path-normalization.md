# Experience receipt: third tree n=1 scorer normalization defect

```yaml
id: exp-20260901-tree-n1-path-normalization
source_type: benchmark
source_pointer: benchmark-results/tree-delivery-n1-semantic-20260901-120715/results.jsonl
repository_family: practical-coding
task_family: quality
skill_commit: 31ba37c9c324ff5863ee237a8c89203f4405fbe9
model_harness: gpt-5.6-luna medium + benchmarks/tree_validation.py n=1 current-only on Windows
execution_depth: unknown
retrieval_depth: unknown
capability_path: []
outcome: indeterminate
quality_gates:
  correctness: unknown
  safety: pass
  build_reachability: unknown
cost:
  tokens: null
  seconds: null
  tool_calls: null
  loc: null
routing_observation: unknown
mechanism: manual reference enforcement failed to normalize Windows path separators, while focused-test scoring still required identifiers rather than the requested evidence act.
user_feedback: improve the general benchmark mechanism until delivery evidence is reliable; do not optimize runtime text for individual outputs.
candidate_lesson: normalize platform representations at the scorer boundary and encode required evidence acts independently from incidental repository filenames.
```

## Supporting evidence

- The run completed 106/106 determinate cells with valid routing traces and zero spontaneous manual activation.
- The failed manual answer had no missing evidence groups and loaded the absolute Windows `references\manual\decision.md` path; only separator-sensitive enforcement failed.
- The failed cancellation answer reported the focused suite as 9/9 and identified the absent post-encode test; only the filename-specific evidence group failed.

## Contradictions / uncertainty

- The candidate still requires a complete fresh rerun after the scorer changes.
- n=1 topology suggestions remain unstable and are not delivery or removal evidence.
