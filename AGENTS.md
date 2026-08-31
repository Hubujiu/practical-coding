# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply [`SKILL.md`](SKILL.md).

The experimental architecture separates **execution depth**, **retrieval depth**, and **capability type**. The default runtime starts at Core/E0.

## Runtime model

1. Apply the Core and start execution at the lowest sufficient depth: E0 Direct → E1 Focused → E2 capability root → E3 specialist leaf.
2. Start retrieval independently: R0 Target → R1 Local, then branch to R2 Structural, R2 External contract, or R3 bounded exhaustive repository discovery only when needed.
3. Escalate only because a concrete execution/retrieval event cannot be answered at the current depth.
4. Contract again as soon as the cause, boundary, relationship, or guarantee is localized.

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
| Observed failure still lacks an evidenced cause after bounded inspection | [`references/debugging.md`](references/debugging.md) |
| Desired behavior is known but contract/invariant/ownership/change boundary is unresolved | [`references/engineering.md`](references/engineering.md) |

E3 may add one evidence-triggered specialist leaf under `references/specialists/`: security, state, compatibility, performance, quality, or interface where valid for the active root.

Do not treat these leaves as a checklist. Keep the normal root context to Core + at most one root + one leaf for the current event.

Navigation is retrieval, not an execution phase. Read [`references/navigation.md`](references/navigation.md) only when structural or repository-wide retrieval becomes substantial.

## Context isolation

Already-read context cannot be unloaded. De-escalation means stop applying higher-depth behavior and narrow subsequent work.

If a second substantial adaptive event, specialist guarantee, or broad mapping effort would cost more in the root than a compact handoff, isolate it with [`references/delegation.md`](references/delegation.md). Manual-only interaction modes stay in the root conversation and are not worker-selected.

## Evolution discipline

`evolution/` is maintainer knowledge, not runtime context. Do not read it while solving ordinary coding tasks.

Maintenance should treat E0–E3, R0–R3, capability roots, specialist leaves, and their adaptive triggers as hypotheses. Benchmark minimum-sufficient depth/path and routing cost against no-skill and the accepted prior Practical Coding version.

Manual-only modes are tested separately for explicit-activation value and zero spontaneous activation; they are not adaptive routing hypotheses.