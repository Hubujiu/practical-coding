# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the skill as follows.

Read [`SKILL.md`](SKILL.md) for the route-agnostic shortest-path Core and the Event Router. The Core always applies and contains only universal coding rules. The Router may add exactly one module for the current unresolved blocker; module-specific triggers belong to the Router, and module-specific procedures belong to the selected reference. If no trigger matches, use the Core alone on the Direct Path with no reference and no worker.

| Trigger | Module |
|---|---|
| An observed failure, regression, or incorrect behavior still lacks an evidenced cause | [`references/debugging.md`](references/debugging.md) |
| A material unresolved user-owned choice about architecture, whether or which external dependency/implementation to adopt, APIs, data models, or compatibility would change the next action | [`references/decision.md`](references/decision.md) |
| An unknown contract/invariant, a material risk boundary (security/permissions, irreversible side effects, persistence/migration, concurrency/transactions, compatibility), or unresolved sufficient evidence for a risky material claim blocks safe execution | [`references/implementation.md`](references/implementation.md) |
| Broad structural mapping is itself necessary before another safe action is known | [`references/navigation.md`](references/navigation.md) |

Modules are independent and imply no execution order. Load exactly one first-match module in addition to the Core, resolve that event, and route again only if a different blocker appears. A choice already settled by the request or repository is input, not a Decision event.

For a substantial triggered event, prefer an isolated no-history worker only when its context savings exceed handoff cost; otherwise load the one selected reference in the root agent. The root agent owns user intent, authorization, repository state, routing, integration, and the final completion claim. A selected module worker reads [`references/delegation.md`](references/delegation.md) plus exactly one assigned module and returns a compact capsule. Workers are read-only by default; an implementation worker may write only when its assignment includes implementation, must have explicit scope, and must be the sole writer there. Treat a capsule as stale after relevant repository changes.

Structured Codebase Memory is a Navigation-selected opt-in backend backed directly by the mature `DeusData/codebase-memory-mcp` implementation. It is used only when `.practical-coding.yaml` explicitly sets `codebase_memory.enabled: true`; false or missing configuration uses ordinary source search without prompting.

When enabled, prefer an existing `codebase-memory-mcp` executable. Otherwise, when `npx` is available, the Skill may use `npx --yes codebase-memory-mcp@latest` as a lazy official launcher. Use upstream CLI mode; do not automatically run its `install` command or add a duplicate MCP/Skill integration. If the upstream engine cannot be launched, keep the project preference unchanged, continue with ordinary source search, and explicitly report that Codebase Memory was not used for the task.
