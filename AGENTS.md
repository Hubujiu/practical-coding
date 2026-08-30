# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply [`SKILL.md`](SKILL.md).

The experimental architecture separates **depth** from **capability type**.

## Runtime model

1. Apply the Core.
2. Use [`references/decision.md`](references/decision.md) only for a material genuinely-open user-owned choice.
3. Start execution at the lowest sufficient depth: E0 Direct → E1 Focused → E2 capability root → E3 specialist leaf.
4. Start retrieval independently: R0 Target → R1 Local, then branch to R2 Structural, R2 External contract, or R3 bounded exhaustive repository discovery only when needed.
5. Escalate only because a concrete unresolved event cannot be answered at the current depth.
6. Contract again as soon as the cause, boundary, relationship, or guarantee is localized.

## Capability tree

E2 loads exactly one event root:

| Unresolved event | Root |
|---|---|
| Observed failure still lacks an evidenced cause after bounded inspection | [`references/debugging.md`](references/debugging.md) |
| Desired behavior is known but contract/invariant/ownership/change boundary is unresolved | [`references/engineering.md`](references/engineering.md) |

E3 may add one evidence-triggered specialist leaf under `references/specialists/`: security, state, compatibility, performance, quality, or interface where valid for the active root.

Do not treat these leaves as a checklist. Keep the root context to Core + at most one root + one leaf for the current event.

Navigation is retrieval, not an execution phase. Read [`references/navigation.md`](references/navigation.md) only when structural or repository-wide retrieval becomes substantial.

## Context isolation

Already-read context cannot be unloaded. De-escalation means stop applying higher-depth behavior and narrow subsequent work.

If a second substantial event, specialist guarantee, or broad mapping effort would cost more in the root than a compact handoff, isolate it with [`references/delegation.md`](references/delegation.md). Do not use workers for ceremony or overlap writers.

## Evolution discipline

`evolution/` is maintainer knowledge, not runtime context. Do not read it while solving ordinary coding tasks.

Maintenance should treat E0–E3, R0–R3, capability roots, specialist leaves, and their triggers as hypotheses. Benchmark minimum-sufficient depth, capability paths, unnecessary/missed loads, and branch confusion against no-skill and the accepted prior Practical Coding version.

Real-project observations become experience receipts first, then consolidated wiki knowledge, then frozen experiments. Preserve rejected lessons so failed changes are not repeatedly rediscovered.
