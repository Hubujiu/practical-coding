# Execution state for long-running coding skills

This document adapts the runtime mechanism from Badhe, Tiwari, and Chung, *SKILL.state: Scalable Long-Horizon Agent Skills* (arXiv:2608.26263v2), to Practical Coding. It does not turn the paper's reported model results into project claims. It defines a candidate architecture, deterministic state and host contracts, and the model-backed evidence still required here.

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
- latest observation `Ot` after the host has processed any explicit user control change;
- one bounded host validation error only when retrying a rejected transition.

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

The runtime validates the complete successor state before releasing `action` to the host. Omitted patch keys survive, and `null` deletes an obsolete optional entry. Malformed JSON, duplicate object keys, `NaN`/infinity, invalid UTF-8, an oversized input or state, an unexpected output key, a wrong type, a forbidden field, or an illegal router path rejects the whole transition. Rejection leaves the caller-owned canonical state unchanged, and the CLI does not overwrite its output file or print the proposed action.

A validated state transition does **not** authorize the action. The helper never executes it; it only returns or prints a proposal after state validation. The surrounding host must independently validate the tool, arguments, permissions, working directory, and side effects before execution. A bounded retry resends the same `P + Σt + Ot` with a compact validation error, remains capped, and starts from the original canonical state.

Reasoning may occur inside one model invocation, but it is transient computation. Do not place chain-of-thought, transcript copies, full tool output, or an append-only action diary in `Σ`.

## Trust and control boundary

`runtime/skill_state.py` serializes `procedure`, an isolated validated state snapshot, and `latest_observation` inside one compact JSON envelope rather than a Markdown code fence. Newlines, section headings, backticks, and JSON-looking text inside an observation remain JSON string data and cannot structurally terminate the envelope or create a second prompt section.

That framing is a structural boundary, not a semantic prompt-injection proof. Observation text can still influence a model, and a model can still propose an unsafe action. The three inputs therefore have different intended authority:

- `procedure` is host-supplied and authoritative for the transition;
- `state` is an isolated validated snapshot of the canonical current state;
- `latest_observation` is untrusted evidence, not a control plane.

An explicit new user instruction is not silently treated as untrusted tool data. The host first applies the authorized change to `objective`, `success`, or `route` through `host-apply`, then builds the next transition from the updated canonical state.

The model may patch only `working_set`, `facts`, `hypotheses`, `change`, `verification`, `next_action`, and `history`. `schema_version`, `objective`, `success`, and `route` are host-owned. Runtime validation enforces this state-field boundary even if the prompt is ignored. It cannot prove that the model followed `procedure`, classified evidence correctly, or proposed a safe action; those remain model-quality and host-policy responsibilities.

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

Schema validation catches malformed structure; it cannot prove that a semantically useful fact was not overwritten or deleted too early, that an `artifacts` string resolves to immutable evidence, or that a user-required audit trail remains sufficient. A host with a hard provenance requirement must enforce that requirement outside model-controlled state as well. The model-backed gate therefore measures premature loss, stale-fact recovery, repeated work, invalid-patch retries, and delivered task quality rather than treating a syntactically valid patch as sufficient.

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

For those cases, set `history.required=true` and keep bounded references to immutable artifacts. Do not copy the artifacts into state. The validator checks only the bounded JSON shape; the host or artifact store must establish immutability, authorization, retention, and successful resolution of each pointer.

`_atomic_write_json()` prevents partial replacement of one local JSON file, but it is not compare-and-swap. Multiple hosts can still overwrite one another with individually valid snapshots. `build_prompt()` deep-copies and validates one isolated snapshot before serialization, but that snapshot is not a lock or revision check. A concurrent integration must add a revision/CAS or single-writer ownership rule before sharing one state file.

## Audited history-free host boundary

`build_prompt()` deliberately accepts no conversation-history argument, but that local API shape alone cannot prove what the surrounding SDK or product sends. `runtime/skill_state_host.py` adds an explicit transport-facing boundary for the `state history-free` arm.

A prepared request places the frozen procedure and transition contract in the
current top-level `instructions` field. Its single current user input contains
only canonical JSON for validated state, latest observation, and optional bounded
validation feedback. This separates the authoritative procedure from untrusted
evidence at the request-role boundary. The host rejects:

- `previous_response_id` and equivalent parent/response handles;
- `conversation`, thread, session, or context-management handles;
- prompt references or server-managed prompt state;
- prior assistant or tool input items;
- nested option fields that can import previous context.

It also explicitly fixes `store=false`, `stream=false`, `background=false`, and `truncation="disabled"`; freezes the model, procedure, tools, options, limits, and request contract in a self-digested manifest; and applies hard limits to every variable request component and the final canonical request body.

The audit records hashes and byte sizes for the exact request body, procedure, state, observation, tools, and options. `audit_wire_request_against_manifest()` rejects any drift. A manifest-free audit validates only one body and is not eligible for a trajectory-level bound; the manifest-matched audit supports only a **client-visible serialized-request-body** claim. A caller must send the prepared bytes unchanged. If an SDK rebuilds the body, or the transport attaches a context-bearing header, cookie, proxy session, or other state out of band, the final outbound request must be captured and rechecked; otherwise the run is state shadow, not demonstrated history-free execution.

The host can bound `latest_observation` but cannot prove that it is truly the latest observation rather than a relabeled history dump. The benchmark must freeze and identify the observation injector and retain the per-step observation hash.

The history-free boundary is about model context composition, not data-retention or privacy guarantees. `store=false` means this request does not ask the Responses API to store the generated response for later retrieval; provider logging, abuse monitoring, and retention policies are separate concerns.

On a rejected model transition, the host retries from the unchanged original state with the same procedure and latest observation plus one bounded deterministic validation error. It does not append the rejected response. On acceptance, the successor must be durably persisted before the action proposal is returned. Persistence success is still not action authorization; the product's ordinary tool and side-effect policy remains mandatory.

See [`SKILL_STATE_HOST.md`](SKILL_STATE_HOST.md) for the full request schema, limits, CLI, integration example, manifest contract, and benchmark handoff.

## What “bounded” may mean

With the default hard caps, each client request has a fixed byte ceiling composed of bounded procedure, state, latest observation, validation feedback, tools, options, and wrapper overhead. The ceiling does not depend on the number of preceding task steps. This supports the statement:

> The captured client-visible input for each audited history-free step is bounded with respect to task horizon.

It does **not** support these stronger statements without further evidence:

- total token use for an entire `T`-step task is constant;
- provider-internal context is known or bounded by the client audit;
- state always preserves every future-relevant fact;
- state reduces tokens or latency on real tasks.

Even when every step is bounded, cumulative input over `T` steps is still expected to grow with `T`. Actual provider-reported tokens and end-to-end time must be measured in the paired model gate.

## Host boundary CLI

The state helper remains the canonical schema/transition CLI:

```powershell
python runtime/skill_state.py init `
  --objective "Repair release validation" `
  --success "Focused release check passes" `
  --output "$env:TEMP\practical-coding-state.json"

python runtime/skill_state.py validate "$env:TEMP\practical-coding-state.json"
```

The history-free helper can build and re-audit an offline request, but never sends it:

```powershell
python runtime/skill_state_host.py build `
  --model "gpt-5.6-luna" `
  --procedure procedure.txt `
  --state "$env:TEMP\practical-coding-state.json" `
  --observation observation.txt `
  --request-output request.json `
  --audit-output request-audit.json `
  --manifest-output host-manifest.json

python runtime/skill_state_host.py audit request.json `
  --manifest host-manifest.json `
  --output request-reaudit.json
```

Keep ephemeral state and raw request/response artifacts outside the target repository unless the user explicitly requests a durable, reviewable artifact.

## Validation

The deterministic checks cover parser strictness, isolated snapshots, merge/deletion mechanics, rollback, schema and input budgets, router ownership, JSON-envelope round trips, the rule that a rejected CLI transition does not expose its action or overwrite its output, and the audited one-current-input/no-history host boundary.

The existing synthetic contract demonstrates bounded state under one fixed hand-authored update schedule and that the merge mechanism permits an immediate stale-value replacement. The host tests demonstrate request shape, manifest identity, retry rollback, and persistence-before-release. Neither demonstrates that a model will ignore distractor telemetry, detect a corrective observation, retain every future-relevant fact, resist semantic prompt injection, or choose an authorized action.

```powershell
python -m py_compile runtime/skill_state.py runtime/skill_state_host.py
python -m unittest tests.test_skill_state_hardening tests.test_skill_state_host
python -m unittest benchmarks.test_skill_state_runtime
python benchmarks/skill_state_validation.py --self-test `
  --output benchmark-results/skill-state-contract.json
```

Because the runtime prompt and Skill wording affect model behavior, the existing model-backed tree benchmark must still run under the normal `n=1` iteration and frozen `n=3` non-regression policy before release promotion.

The dedicated comparison protocol is in [`../benchmarks/SKILL_STATE_MODEL_GATE.md`](../benchmarks/SKILL_STATE_MODEL_GATE.md). It separates full-history, state-shadow, and true history-free `P + Σ + O` arms so a cost or bounded-context claim cannot be inferred from deterministic byte limits alone.
