# Experience receipt: explicit WikiSkill maintenance loop

```yaml
id: exp-20260901-wikiskill-maintenance
source_type: real-project
source_pointer: current 2026-09-01 Practical Coding maintenance session; transcript intentionally not stored
repository_family: practical-coding
task_family: quality
skill_commit: 118acd81cb0e26f4f8087555c3bd89cbf45c9d30
model_harness: ChatGPT maintenance session + repository benchmark harness
execution_depth: unknown
retrieval_depth: unknown
capability_path: []
outcome: success
quality_gates:
  correctness: unknown
  safety: pass
  build_reachability: n/a
cost:
  tokens: null
  seconds: null
  tool_calls: null
  loc: null
routing_observation: none
mechanism: maintenance experience should compile into a persistent wiki, while wiki-informed Skill changes remain separate reversible candidates accepted only after a frozen benchmark shows no required score regression.
user_feedback: add two explicitly triggered maintenance skills—current-session to wiki, and wiki-informed skill evolution with a new benchmark and rerun before accepting any update.
candidate_lesson: keep these capabilities outside the automatic coding router tree and validate their maintenance contract independently.
```

## Evidence summary

The session explicitly referenced WikiSkill and requested a maintenance loop with two user-triggered capabilities. No secrets, private code, or full conversation transcript are stored here.

## Supporting observations

- Current branch already treats `evolution/` as maintenance-time knowledge unavailable to ordinary runtime agents.
- The requested completion condition is objective: add benchmark coverage, rerun, and do not finalize a Skill update when required scores are worse.

## Contradictions / uncertainty

- No model-backed evolution benchmark has yet established that these maintenance skills improve downstream runtime coding quality; they are maintenance orchestration capabilities, not promoted automatic runtime nodes.
