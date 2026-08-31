# Experience receipt schema

Use this schema to capture a benchmark observation or real-project experience without injecting the full trace into Skill-maintenance context.

```yaml
id: exp-YYYYMMDD-short-name
source_type: benchmark | real-project
source_pointer: path/to/artifact-or-stable-reference
repository_family: optional coarse repository/domain label
task_family: diagnosis | localized-change | cross-contract | security | state | compatibility | performance | quality | interface | retrieval
skill_commit: commit sha or version
model_harness: model + harness when known
execution_depth: E0 | E1 | E2 | E3 | unknown
retrieval_depth: R0 | R1 | R2 | R3 | unknown
capability_path: [] # e.g. [diagnosis, state]
outcome: success | failure | mixed | indeterminate
quality_gates:
  correctness: pass | fail | unknown
  safety: pass | fail | unknown
  build_reachability: pass | fail | n/a | unknown
cost:
  tokens: optional
  seconds: optional
  tool_calls: optional
  loc: optional
routing_observation: exact | over-escalation | under-escalation | unnecessary-leaf | missed-leaf | branch-confusion | none | unknown
mechanism: one sentence describing what actually caused the result
user_feedback: optional concise correction/preference relevant to the mechanism
candidate_lesson: optional; not yet a runtime rule
```

## Rules

- `mechanism` describes causal structure, not benchmark-specific wording.
- Real-project receipts may guide calibration but do not become held-out benchmark proof.
- Do not store secrets, private code, or sensitive user content. Use coarse descriptions and evidence pointers.
- Multiple receipts that share a mechanism should be consolidated into one wiki entry rather than copied into `SKILL.md`.
