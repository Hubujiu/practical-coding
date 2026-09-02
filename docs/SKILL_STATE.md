# Execution state for long-running coding skills

This document adapts the runtime mechanism from Badhe, Tiwari, and Chung, *SKILL.state: Scalable Long-Horizon Agent Skills* (arXiv:2608.26263v2), to Practical Coding. It does not turn the paper's results into project claims; it defines the candidate architecture and the limits that must be validated here.

## Four separate concerns

Practical Coding now distinguishes four mechanisms that must not be collapsed into one router:

| Mechanism | Question it answers | Lifetime |
|---|---|---|
| Local router tree | Which execution capability is needed for the present blocker? | Current task |
| Retrieval policy | Which source evidence is needed and how broadly should it be collected? | Current evidence need |
| Execution state | What is currently true and needed for the next action? | Current multi-step run |
| Evolution wiki | Which repeated lessons should change the Skill after validation? | Across sessions/releases |

Execution state is therefore a **runtime substrate**, not an automatic child, retrieval mode, or manual workflow.

## Runtime transition

A state-aware host should construct each model invocation from only:

- immutable loaded Skill procedure `P`;
- validated current execution state `Σt`;
- latest user/tool/environment observation `Ot`.

The model returns one runtime payload:

```json
{
  "state_patch": {
    "facts": {"current_head": "def456"},
    "next_action": "run the focused check for def456"
  },
  "action": "python -m unittest tests.test_release"
}
```

The host validates the patch before mutation. Omitted keys survive. A value of `null` deletes an obsolete key. Invalid JSON, unknown required structure, wrong types, forbidden narrative fields, or an oversized result leave the previous canonical state unchanged.

Reasoning may occur inside one model invocation, but it is transient computation. Do not place chain-of-thought, transcript copies, full tool output, or an action diary in `Σ`.

## Coding-domain schema

`runtime/skill_state.py` uses one schema for coding tasks rather than generating a schema per task:

| Field | Future-facing content |
|---|---|
| `objective`, `success` | Current outcome and observable completion conditions |
| `route` | Active automatic path, retrieval mode, and explicit manual mode |
| `working_set` | Current paths and symbols, not repository inventory |
| `facts` | Authoritative current facts that later actions need |
| `hypotheses` | Live and rejected hypotheses needed to avoid repetition |
| `change` | Current planned/applied change surface |
| `verification` | Pending checks and compact current outcomes |
| `next_action` | The single next useful action |
| `history` | Whether history is part of the task, plus bounded artifact pointers |

The schema has a fixed total byte budget and per-container limits. Replace stale values instead of appending versions. Store an evidence pointer or compact outcome instead of raw output.

## Activation and exit

Do not create state for a short direct edit. Activate projection only when **state pressure** appears: the next action depends on multiple earlier observations, external drift can invalidate a stored fact, hypotheses/checks are beginning to repeat, or reconstructing the work surface would require replaying raw output.

Exit state mode when the task completes or collapses back to one self-contained action. State activation does not change the selected tree node. Debugging remains Debugging; Implementation remains Implementation; Core remains Core.

## When history must remain available

Explicit state is not assumed lossless when:

- the relevant schema is still being discovered dynamically;
- an earlier observation may matter later but has not yet been classified;
- the requested output is an audit, provenance reconstruction, or explanation of past actions;
- multiple writers can update shared state without deterministic conflict resolution.

For those cases, set `history.required=true` and keep bounded references to immutable artifacts. Do not copy the artifacts into state.

## Host boundary

`build_prompt()` deliberately accepts no conversation-history argument. That makes accidental history replay visible in the adapter API, but a Skill file cannot force the surrounding product or API to discard prior messages. A host may use the state projection to reduce reconstruction while still retaining conversation history, but it must not claim horizon-independent prompt growth until the host-level request actually contains only `P + Σt + Ot`.

The helper is zero-dependency and local:

```powershell
python runtime/skill_state.py init `
  --objective "Repair release validation" `
  --success "Focused release check passes" `
  --output "$env:TEMP\practical-coding-state.json"

python runtime/skill_state.py validate "$env:TEMP\practical-coding-state.json"
```

Keep ephemeral state outside the target repository unless the user explicitly requests a durable, reviewable artifact.

## Validation

The deterministic contract gate covers merge/deletion behavior, rollback, bounded schema growth, noise filtering, and immediate stale-fact correction:

```powershell
python -m unittest benchmarks.test_skill_state_runtime
python benchmarks/skill_state_validation.py --self-test `
  --output benchmark-results/skill-state-contract.json
```

This gate tests implementation mechanics only. Because `SKILL.md` runtime wording changes model behavior, the existing model-backed tree benchmark must still run under the normal `n=1` iteration and frozen `n=3` non-regression policy before release promotion.
