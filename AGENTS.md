# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the skill as follows.

Read [`SKILL.md`](SKILL.md) for the shortest-path core and event router. Local, well-specified tasks use the Direct Path with no reference and no worker. Task complexity determines escalation; there is no low/smart/high mode. For a substantial triggered event, prefer an isolated no-history worker when its context savings exceed handoff cost; use multiple workers only for genuinely independent, non-overlapping scopes when parallelism clearly wins; otherwise load only that reference in the root agent:

| Trigger | Module |
|---|---|
| A material choice about architecture, introducing a new external dependency, surveying a mature external implementation, APIs, data models, compatibility, or multiple plausible implementations | [`references/decision.md`](references/decision.md) |
| An unmapped contract/invariant, a material risk boundary (security/permissions, irreversible side effects, persistence/migration, concurrency/transactions, compatibility), or unresolved sufficient evidence for a risky change | [`references/implementation.md`](references/implementation.md) |
| An observed failure, regression, incorrect behavior, or failed verification needs diagnosis | [`references/debugging.md`](references/debugging.md) |
| Broad navigation of a large or structurally complex codebase; project configuration selects ordinary search or Codebase Memory | [`references/navigation.md`](references/navigation.md) |

Modules are independent and imply no execution order.

The root agent owns user intent, authorization, repository state, routing, integration, and the final completion claim. A selected module worker reads [`references/delegation.md`](references/delegation.md) plus exactly one assigned module and returns a compact capsule. Workers are read-only by default; an implementation worker may write only when its assignment includes implementation, must have explicit scope, and must be the sole writer there. Treat a capsule as stale after relevant repository changes.

Core stays on project code, stdlib, native/environment features, and already-installed packages. Adopting a new external dependency or surveying a mature external implementation is a Decision event and waits for the user; do not do that work on the Direct Path.

Structured Codebase Memory is a Navigation-selected opt-in backend backed directly by the mature `DeusData/codebase-memory-mcp` implementation. It is used only when `.practical-coding.yaml` explicitly sets `codebase_memory.enabled: true`; false or missing configuration uses ordinary source search without prompting.

When enabled, prefer an existing `codebase-memory-mcp` executable. Otherwise, when `npx` is available, the Skill may use `npx --yes codebase-memory-mcp@latest` as a lazy official launcher. Use upstream CLI mode; do not automatically run its `install` command or add a duplicate MCP/Skill integration. If the upstream engine cannot be launched, keep the project preference unchanged, continue with ordinary source search, and explicitly report that Codebase Memory was not used for the task.
