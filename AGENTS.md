# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply [`SKILL.md`](SKILL.md).

The experimental architecture has two independent adaptive axes: **execution depth** and **retrieval depth**. Capability type branches inside execution. The default runtime starts at Core/E0.

## Runtime model

1. Apply the Core and start execution at the lowest sufficient depth: E0 Direct → E1 Probe → E2 capability root → E3 specialist leaf.
2. Start retrieval independently: R0 Target → R1 Local, then branch to R2 Structural, R2 External contract, or R3 bounded exhaustive repository discovery only when needed.
3. Source discovery belongs to Retrieval. Finding/reading callers, references, siblings, contracts, implementations, or configuration does not by itself raise execution depth.
4. Use E1 only for one cheap executable probe or focused falsification step. Escalate to E2 only if a structured execution blocker remains after sufficient retrieval.
5. Contract again as soon as the cause, boundary, relationship, or guarantee is localized.

## Manual-only modes

Requirements interviews (`grill-me`-style clarification), Decision, and similar user-interaction workflows are outside adaptive routing.

- Never activate them from inferred ambiguity, open choices, task importance, risk, or model preference.
- Load `references/manual/clarification.md` only when the user explicitly requests an interview/requirements-first interaction.
- Load `references/manual/decision.md` only when the user explicitly requests collaborative option selection before implementation.
- One manual mode cannot auto-route into another.
- A single unavoidable blocking question in an ordinary coding task is normal interaction, not manual-mode activation.

## Capability tree

E2 loads exactly one event root:

| Unresolved event | Root |
|---|---|
| Observed failure still lacks an evidenced cause after bounded retrieval/probe | [`references/debugging.md`](references/debugging.md) |
| Desired behavior is known but contract/invariant/ownership/change boundary remains unresolved | [`references/engineering.md`](references/engineering.md) |

E3 may add one evidence-triggered specialist leaf under `references/specialists/`: security, state, compatibility, performance, quality, or interface where valid for the active root.

Do not treat these leaves as a checklist. Keep the normal root context to Core + at most one root + one leaf for the current event.

## Retrieval tree

Retrieval is the only adaptive control for acquiring source/context. `references/navigation.md` is **not** a separate capability or execution phase; it is the deeper procedure for substantial R2 Structural mapping and bounded R3 coverage.

Routine target reading and local caller/reference/sibling/contract lookup stay in R0/R1 and do not need the Navigation reference.

## Context isolation

Already-read context cannot be unloaded. De-escalation means stop applying higher-depth behavior and narrow subsequent work.

If a second substantial adaptive event, specialist guarantee, or broad structural mapping effort would cost more in the root than a compact handoff, isolate it with [`references/delegation.md`](references/delegation.md). Manual-only interaction modes stay in the root conversation and are not worker-selected.

## Evolution discipline

`evolution/` is maintainer knowledge, not runtime context. Do not read it while solving ordinary coding tasks.

Maintenance should treat E0–E3, R0–R3, capability roots, specialist leaves, and their adaptive triggers as hypotheses. Benchmark minimum-sufficient depth/path and routing cost against no-skill and the accepted prior Practical Coding version.

When calibrating the axes, source discovery alone must never be labeled E1. `E0/R1` and `E0/R2` are valid outcomes; E1 requires an executable probe.

Manual-only modes are tested separately for explicit-activation value and zero spontaneous activation; they are not adaptive routing hypotheses.