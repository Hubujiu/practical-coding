# Experience receipt: second tree n=1 semantic oracle defect

```yaml
id: exp-20260901-tree-n1-semantic-oracle
source_type: benchmark
source_pointer: benchmark-results/tree-delivery-n1-oraclefix-20260901-111838/results.jsonl
repository_family: practical-coding
task_family: quality
skill_commit: 31ba37c9c324ff5863ee237a8c89203f4405fbe9
model_harness: gpt-5.6-luna medium + benchmarks/tree_validation.py n=1 current-only
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
mechanism: lexical evidence groups remained language- and identifier-dependent after the first scorer correction, rejecting semantically complete answers.
user_feedback: optimize the general mechanism until the benchmark is deliverable; do not tune runtime wording to a case.
candidate_lesson: evidence alternatives should encode semantic obligations and equivalent languages, while separate groups preserve the required diagnosis/test/decision structure.
```

## Supporting evidence

- The rerun completed 106/106 determinate cells, with 15/15 valid traces, 0 spontaneous manual activations, and valid manual loading in both explicit Decision tasks.
- One Chinese Decision answer recommended summary compression and explicitly named its strongest “权衡” and “代价”, but the English-only `Recommendation:` and `trade-off` groups failed.
- The cancellation answer identified `abort()` at the worker-success handoff, the unconditional `link.click()` side effect, existing cancellation coverage, and one falsifying test; only exact signal/type and filename groups failed.

## Contradictions / uncertainty

- n=1 topology suggestions are unstable across the first two runs and do not justify removing automatic nodes.
- This scorer correction invalidates the second model-backed artifact for delivery acceptance; a full fresh rerun is required.
