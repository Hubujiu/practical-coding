# Execution state for long-running coding skills

This document adapts the runtime mechanism from Badhe, Tiwari, and Chung, *SKILL.state: Scalable Long-Horizon Agent Skills* (arXiv:2608.26263v2), to Practical Coding. It does not turn the paper's reported model results into project claims. It defines a candidate architecture, a deterministic contract, and the model-backed evidence still required here.

## Four separate concerns

Practical Coding distinguishes four mechanisms that must not be collapsed into one router:

| Mechanism | Question it answers | Lifetime |
|---|---|---|
| Local router tree | Which execution capability is needed for the present blocker? | Current task |
| Retrieval policy | Which source evidence is needed and how broadly should it be collected? | Current evidence need |
| Execution state | What is currently true and needed for the next action? | Current multi-step run |
| Evolution wiki | Which repeated lessons should change the Skill after validation? | Across sessions/releases |

Execution state is therefore a **runtime substrate**, not an automatic child, retrieval mode, or manual workflow. Activating it does not increase tree depth and cannot make Decision or Clarification automatic.

## Runtime transition

A state-aware host should construct each model invocation from only:

- immutable loaded Skill procedure `P`;
- validated current execution state `Σt`;
- latest observation `Ot` after the host has processed any explicit user control change.

The model returns exactly one runtime payload:

```json
{
  "state_patch": {
    "facts": {"current_head": "def456"},
    "next_action": "run the focused check for def456"
  },
  "action": "python -m unittest tests.test_release"
}
```

The host validates the complete successor state before exposing or executing `action`. Omitted patch keys survive. A value of `null` deletes an obsolete optional entry. Invalid JSON, an unexpected output key, a wrong type, a forbidden field, an oversized state, or an illegal router path leaves the previous canonical state unchanged and the proposed action unexecuted.

A bounded retry may resend the same `P + Σt + Ot` together with a compact validation error. Cap retries and keep the original canonical state. Never execute the action from a rejected transition merely because the action text parsed successfully.

Reasoning may occur inside one model invocation, but it is transient computation. Do not place chain-of-thought, transcript copies, full tool output, or an append-only action diary in `Σ`.

## Trust and control boundary

`runtime/skill_state.py` serializes `procedure`, `state`, and `latest_observation` inside one compact JSON envelope rather than a Markdown code fence. Newlines, section headings, backticks, and JSON-looking text inside an observation remain string data and cannot terminate a fence or become a new control section.

The three inputs have different authority:

- `procedure` is immutable and authoritative for the transition;
- `state` is the validated canonical snapshot;
- `latest_observation` is evidence, not a control plane. Instructions embedded in tool output, logs, files, or other observations do not override the procedure or host-owned state fields.

An explicit new user instruction is not silently treated as untrusted tool data. The host first applies the authorized change to `objective`, `success`, or `route` through `host-apply`, then builds the next transition from the updated canonical state.

The model may patch only `working_set`, `facts`, `hypotheses`, `change`, `verification`, `next_action`, and `history`. `schema_version`, `objective`, `success`, and `route` are host-owned. The runtime enforces this boundary even if the prompt is ignored.

## Coding-domain schema

`runtime/skill_state.py` uses one schema for coding tasks rather than generating a schema per task:

| Field | Future-facing content |
|---|---|
| `objective`, `success` | Current outcome and observable completion conditions |
| `route` | Host-owned active automatic path, retrieval mode, and explicit manual mode |
| `working_set` | Current paths and symbols, not repository inventory |
| `facts` | Authoritative current facts that later actions need |
| `hypotheses` | Live and rejected hypotheses needed to avoid repetition |
| `change` | Current planned/applied change surface |
| `verification` | Pending checks and compact current outcomes |
| `next_action` | The single next useful action |
| `history` | Whether history is part of the task, plus bounded artifact pointers |

The schema has a fixed total byte budget and per-container limits. Replace stale values instead of appending versions. Store an evidence pointer or compact outcome instead of raw output.

Schema validation catches malformed structure; it cannot prove that a semantically useful fact was not overwritten or deleted too early. The model-backed gate therefore measures premature loss, stale-fact recovery, repeated work, invalid-patch retries, and delivered task quality rather than treating a syntactically valid patch as sufficient.

## Activation and exit

Do not create state for a short direct edit. Activate projection only when **state pressure** appears:

- the next action depends on current facts from multiple earlier observations;
- a new observation can invalidate a stored branch, check, contract, or environment fact;
- hypotheses or checks are beginning to repeat;
- reconstructing the current work surface would require replaying raw output.

Exit state mode when the task completes or collapses back to one self-contained action. State activation does not change the selected tree node. Debugging remains Debugging; Implementation remains Implementation; Core remains Core.

## When history must remain available

Explicit state is not assumed lossless when:

- the relevant schema is still being discovered dynamically;
- an earlier observation may matter later but has not yet been classified;
- the requested output is an audit, provenance reconstruction, or explanation of past actions;
- multiple writers can update shared state without deterministic conflict resolution.

For those cases, set `history.required=true` and keep bounded references to immutable artifacts. Do not copy the artifacts into state.

`_atomic_write_json()` prevents torn local files, but it is not compare-and-swap. Multiple hosts can still overwrite one another with individually valid snapshots. A concurrent integration must add a revision/CAS or single-writer ownership rule before sharing one state file.

## Host boundary

`build_prompt()` deliberately accepts no conversation-history argument. That makes accidental history replay visible in the adapter API, but a Skill file cannot force the surrounding product or API to discard prior messages. A host may use state projection to reduce reconstruction while still retaining conversation history, but it must not claim horizon-independent prompt growth until the actual model request contains only `P + Σt + Ot`.

The helper is zero-dependency and local. Ordinary `apply` and `transition` operations reject host-owned control-field changes; `host-apply` is the explicit control-plane path for a router or new user instruction:

```powershell
python runtime/skill_state.py init `
  --objective "Repair release validation" `
  --success "Focused release check passes" `
  --output "$env:TEMP\practical-coding-state.json"

python runtime/skill_state.py validate "$env:TEMP\practical-coding-state.json"
```

Keep ephemeral state outside the target repository unless the user explicitly requests a durable, reviewable artifact.

## Validation

The deterministic contract covers merge/deletion behavior, rollback, bounded schema growth, noise filtering, immediate stale-fact correction, router ownership, prompt-envelope round trips, and delimiter/control-boundary hardening:

```powershell
python -m unittest benchmarks.test_skill_state_runtime
python benchmarks/skill_state_validation.py --self-test `
  --output benchmark-results/skill-state-contract.json
```

This gate tests implementation mechanics only. Because the runtime prompt and Skill wording affect model behavior, the existing model-backed tree benchmark must still run under the normal `n=1` iteration and frozen `n=3` non-regression policy before release promotion.

The dedicated comparison protocol is in [`../benchmarks/SKILL_STATE_MODEL_GATE.md`](../benchmarks/SKILL_STATE_MODEL_GATE.md). It separates full-history, state-shadow, and true history-free `P + Σ + O` arms so a cost or bounded-context claim cannot be inferred from the deterministic byte simulation alone.
