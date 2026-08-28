# Contributing

Contributions should preserve Practical Coding as one compact skill with independently loadable modules.

- Keep `SKILL.md` as a small shortest-path core plus event router. Task complexity determines escalation; do not add routing intensity modes unless a mature cross-agent mechanism exists and materially improves evidence.
- Do not retune Core or module wording from a failed benchmark cell, and do not add case-specific bans named after Delivery or Debug tasks.
- Put conditional behavior in focused files under `references/` and state an exact trigger for loading each file.
- Keep modules independent; do not create a mandatory chain where loading one module automatically requires the others.
- Preserve the Direct Path: simple, well-specified work must not require a reference or subagent.
- Preserve event-driven isolation: a module worker reads only its assigned reference, receives bounded context, and returns a compact capsule. Subagents are an optimization for substantial context, not a mandatory stage.
- Keep shared-workspace workers read-only by default. An Implementation worker may write only when the assignment includes implementation, and there must be one explicit writer per bounded implementation scope.
- Prefer strengthening an existing module over adding a new module. Verification is not a separate module: choosing sufficient evidence for a risky change is Implementation. Do not restore `verification.md` as a sixth route.
- Add a new module only when it represents a distinct, reusable decision surface that would otherwise pollute unrelated tasks.
- Do not introduce mandatory plans, execution documents, Git workflows, tests, reviews, documentation, or tool-specific ceremony as universal gates.
- Preserve reuse-before-invention, risk-proportional verification, evidence-driven debugging, and resistance to speculative code and defensive bloat. Mature-implementation-first belongs in Decision, not Core: Core does not survey or adopt new external implementations.
- Keep optional heavy capabilities outside the default Agent context; optional package size or disk use is acceptable when the capability materially reduces token use, repeated work, or correctness risk.
- Avoid scripts, dependencies, configuration, and generated project files unless they solve a demonstrated need.

## Mature implementation first

This policy applies after Decision has selected an external implementation, and when contributing to Practical Coding itself. It is not a Core/Direct-Path obligation.

For any non-trivial capability with credible prior art:

1. Inspect maintained mature implementations first.
2. Prefer the mature project's supported public integration surface — API, CLI, protocol, package, library, or binary — over copying internals or rebuilding the same subsystem.
3. Verify fit, maintenance state, known issues, release activity, operational constraints, and license.
4. Add local code only for concrete gaps or confirmed upstream defects.
5. Keep local patches narrow, attributable, and removable when upstream fixes the issue.

A local implementation should not exist merely because it is smaller, simpler to own, or avoids an optional dependency. Correctness, token efficiency, reliability, and maintenance can justify a larger optional dependency.

## Codebase Memory

Structured Codebase Memory is backed directly by [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp).

- Do not reintroduce a Practical Coding parser, graph database, call resolver, language grammar set, incremental indexer, project lock, semantic engine, or other parallel code-intelligence implementation when upstream already provides it.
- Prefer upstream CLI mode for Practical Coding because it exposes the mature engine on demand without automatically installing a second persistent MCP/Skill integration into the agent.
- Before adding any Codebase Memory compatibility code, check the latest stable upstream release and existing upstream issues/fixes.
- If upstream has a blocking defect without a released fix, add only the narrowest compatibility shim needed and record the affected version/issue.
- Remove the shim after upstream fixes the defect.
- Keep attribution and license notices when upstream code or substantial implementation material is ever vendored or copied; see `THIRD_PARTY_NOTICES.md`.

A change is moving in the wrong direction if a trivial local edit must load or execute more process after the change than before it, or if Practical Coding starts maintaining a weaker duplicate of a mature subsystem.
