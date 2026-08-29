# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the Skill from [`SKILL.md`](SKILL.md).

Practical Coding is an adaptive-rigor system, not a task classifier. The Core always applies. Start from the cheapest sufficient action and add stricter reasoning only when a present blocker requires it.

## 1. Decision Gate

Before execution, determine whether a material unresolved choice blocks or materially changes the next safe action.

- If no, continue to execution.
- If yes, read [`references/decision.md`](references/decision.md) and resolve only that decision frontier.

A request-, repository-, or authority-settled choice is input, not a Decision. Cheap reversible choices use the project or platform default. Resolve discoverable facts before asking the user; only genuinely user-owned scope, compatibility, cost, preference, or risk choices should remain as questions.

After the choice is settled, continue with the Core. Do not assume the logical end of Decision removes `decision.md` from model context.

## 2. Execution Escalation

Direct is the default execution state: Core only.

| Present blocker | Extra rigor |
|---|---|
| Observed failure or regression still lacks an evidenced cause | [`references/debugging.md`](references/debugging.md) |
| Safe execution is blocked by an unknown contract/invariant, unresolved material risk boundary, or unresolved sufficient evidence for a risky claim | [`references/implementation.md`](references/implementation.md) |

Debugging and Implementation are escalation profiles, not sequential stages. Do not classify by task nouns, file count, code size, or apparent difficulty. A diagnosed bug can be Direct. A security, persistence, migration, concurrency, or compatibility edit can be Direct when the governing boundary, affected surface, and sufficient check are already established.

If one loaded profile resolves its blocker and a materially different blocker later appears, reassess from the Core. Do not accumulate another large reasoning reference in the root merely because the task continued; isolate substantial follow-up work when the context saved exceeds handoff cost.

## 3. Retrieval Policy

Retrieval is independent from Decision and execution rigor. Use the cheapest sufficient available path:

1. current context / known path / known symbol;
2. bounded or ranked source discovery, falling back to ordinary filename/text/symbol search;
3. an already-available structural index only for relationship-heavy questions where it materially reduces exploration;
4. current-source verification for material conclusions.

Read [`references/navigation.md`](references/navigation.md) only when broad retrieval itself is substantial enough to need the detailed procedure. Host-native ranked search, FFF-style retrieval, and `DeusData/codebase-memory-mcp` are optional capabilities, not project requirements. Missing capabilities fall back without installing tooling or changing project configuration solely for retrieval.

Retrieval levels are cost bounds rather than exact semantic labels. A cheap bounded search may be acceptable where a targeted read would also suffice; an unnecessary structural exploration is not.

## 4. Isolation Gate

The root owns user intent, authorization, repository state, integration, and the final completion claim. Keep the root to the Core plus at most one loaded reasoning reference at a time.

The root never reads [`references/delegation.md`](references/delegation.md). When isolation clearly saves more context than its handoff cost, dispatch one worker with `delegation.md` plus exactly one assigned reference and a compact capsule of settled choices, verified facts, scope, repository state, and success conditions.

Decision, Debugging, and Navigation workers are read-only. An Implementation worker may write only when explicitly assigned a bounded implementation scope and must be the sole writer there. Never use overlapping writers or worker pipelines. Treat a worker capsule as stale after relevant repository changes.
