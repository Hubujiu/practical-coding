# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the skill as follows.

Read [`SKILL.md`](SKILL.md) for the always-on core rules, then load only the reference modules whose trigger matches the current task:

| Trigger | Module |
|---|---|
| A material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations | [`references/decision.md`](references/decision.md) |
| Modifying code or project files | [`references/implementation.md`](references/implementation.md) |
| An observed failure, regression, incorrect behavior, or failed verification needs diagnosis | [`references/debugging.md`](references/debugging.md) |
| Risk or uncertainty makes the verification strategy itself a meaningful decision | [`references/verification.md`](references/verification.md) |
| Large or structurally complex codebase navigation, call-chain analysis, impact analysis, cross-service tracing, architecture discovery, or repeated multi-agent exploration where a graph would reduce repeated source scanning | [`references/codebase-memory.md`](references/codebase-memory.md) |

Modules are independent, imply no execution order, and a trivial task may need only one of them. Structured codebase memory is project-level and optional; respect `.practical-coding.yaml` when present, and do not install or index a provider without user consent.
