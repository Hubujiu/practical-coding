# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the skill as follows.

Read [`SKILL.md`](SKILL.md) for the route-agnostic shortest-path Core, the three-branch Event Router, and the Retrieval Policy. The Core always applies. Ordinary well-specified work stays Direct with no reasoning reference and no worker.

The Event Router handles only unresolved blockers that change how the task must be reasoned about:

| Trigger | Reasoning module |
|---|---|
| An observed failure, regression, or incorrect behavior still lacks an evidenced cause | [`references/debugging.md`](references/debugging.md) |
| A material unresolved user-owned choice about architecture, whether or which external dependency/implementation to adopt, APIs, data models, or compatibility would change the next action | [`references/decision.md`](references/decision.md) |
| An unknown contract/invariant, an unresolved material risk boundary (security/permissions, irreversible side effects, persistence/migration, concurrency/transactions, compatibility), or insufficient evidence for a risky material claim blocks safe execution | [`references/implementation.md`](references/implementation.md) |

Load exactly one first-match reasoning module in addition to the Core. A choice already settled by the request or repository is input, not a Decision event. A security, persistence, migration, concurrency, or compatibility noun is not itself an Implementation event when the governing boundary, affected surface, and sufficient check are already established. Do not treat file count, task nouns, search needs, or the existence of another library as routing evidence. If a different blocker appears later, reassess it without accumulating another reasoning reference in the root; use the Core when sufficient or isolate substantial follow-up work when the saved context exceeds handoff cost.

Navigation is not a fourth Event Router branch. Code retrieval follows the cheapest sufficient available path: known source first, then bounded/ranked source discovery, then an already-available structural index only when relationship queries materially reduce exploration, followed by current-source verification for material claims. Routine targeted lookup needs no Navigation reference.

Read [`references/navigation.md`](references/navigation.md) only when broad retrieval itself is substantial enough to need the detailed procedure. Host-native ranked search, FFF-style retrieval, and `DeusData/codebase-memory-mcp` are optional capabilities, not project requirements. Use them only when already available; otherwise fall back to ordinary source search without installing tooling or changing project configuration solely for retrieval. An already-integrated structural backend may maintain or refresh its own index as part of normal use.

For a substantial triggered event, prefer an isolated no-history worker only when its context savings exceed handoff cost; otherwise load the one selected reasoning reference in the root agent. Keep the root to the Core plus at most one loaded reasoning reference for the task. If broad mapping becomes expensive while another reasoning reference is already resident, prefer a read-only Navigation worker rather than loading a second large reference into the root.

The root agent owns user intent, authorization, repository state, routing, integration, and the final completion claim. A worker reads [`references/delegation.md`](references/delegation.md) plus exactly one assigned reference and returns a compact capsule. Decision, Debugging, and Navigation workers are read-only. An Implementation worker may write only when its assignment explicitly includes implementation, must have a bounded scope, and must be the sole writer there. Treat a capsule as stale after relevant repository changes.
