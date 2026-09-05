# Experience receipt: first tree n=1 oracle defects

```yaml
id: exp-20260901-tree-n1-oracle-defects
source_type: benchmark
source_pointer: benchmark-results/tree-delivery-n1-20260901-103036/results.jsonl
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
mechanism: deterministic evidence groups produced false failures by requiring punctuation and non-authoritative filenames that the frozen prompts did not require.
user_feedback: optimize general benchmark and Skill mechanisms rather than tuning to a test case, and wait for complete reports before changing them.
candidate_lesson: invalidate and rerun model-backed evidence whenever a scorer contract changes; preserve the original artifact as evidence of the oracle defect.
```

## Supporting evidence

- The run completed 106/106 determinate cells and reported adaptive 12/15 before oracle review.
- Both explicit manual answers loaded `references/manual/decision.md`, emitted `manual=decision`, recommended one option, and described its strongest trade-off; only the exact group `Trade-off:` was missing.
- The cancellation diagnosis named the real `exportCover` download side-effect boundary and the existing cancellation test `src/lib/avifEncoder.test.ts`; the frozen repository confirms this test exercises `AbortController.abort()` and worker termination.
- The task prompt did not require `exportProgress.test.ts` or `ExportProgressModal.test.tsx`, although the scorer did.

## Contradictions / uncertainty

- This receipt does not establish that all three answers would repeat at n=3.
- The run's topology lift and removal suggestions remain provisional n=1 diagnostics and are not accepted while the scorer changes.
