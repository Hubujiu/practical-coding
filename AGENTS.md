# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply [`SKILL.md`](SKILL.md).

The experimental v1.3 architecture uses two independent progressive ladders plus one Decision Gate.

## Runtime model

1. Apply the Core.
2. Resolve a material genuinely-open choice through [`references/decision.md`](references/decision.md) only when it changes the next action and is not already settled.
3. Start execution at the lowest sufficient rung: E0 Direct → E1 Guided → E2 Structured → E3 Assurance.
4. Independently start retrieval at the lowest sufficient rung: R0 Target → R1 Local → R2 Structural → R3 Repository → R4 External.
5. Escalate only when current evidence cannot answer the next material question or support the required claim.
6. Contract again as soon as the blocker or relevant boundary is localized.

Debugging and Implementation are capabilities, not levels:

| Evidence | Capability |
|---|---|
| Observed failure still lacks an evidenced cause after bounded local inspection | [`references/debugging.md`](references/debugging.md) |
| Safe execution is blocked by an unknown contract/invariant, unresolved material risk boundary, or insufficient evidence for a risky material claim | [`references/implementation.md`](references/implementation.md) |

E3 means deeper use of the already-selected capability; it does not load another reasoning module.

Navigation is not an execution branch. Read [`references/navigation.md`](references/navigation.md) only when substantial R2/R3 retrieval needs the detailed procedure. Routine known-target or local search stays in `SKILL.md`.

## Context discipline

Keep the root to the Core plus at most one reasoning reference. If a second substantial event or broad mapping effort would accumulate more context than a handoff costs, isolate it with a worker using [`references/delegation.md`](references/delegation.md) plus exactly one assigned reference. Do not use workers for ceremony.

A semantic return to a lower rung does not unload text already read. It means stop applying the higher-level procedure and narrow subsequent work.

## Evolution discipline

`evolution/` is maintainer knowledge, not runtime context. Do not read it while solving ordinary user coding tasks.

Benchmark-driven maintenance should treat E0–E3 and R0–R4 as hypotheses. Prefer evidence that moves boundaries, merges unused rungs, or splits overloaded rungs over prose edits made only from intuition. Preserve rejected experiments so the project does not repeatedly rediscover the same failed change.
