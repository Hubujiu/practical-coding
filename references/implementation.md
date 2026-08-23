# Implementation

Load this module when changing code or project files.

## Work Locally

- Start from the exact behavior, component, function, file, or path involved in the request.
- Read callers, dependencies, types, configuration, or surrounding code only when they affect the change.
- Match established project conventions unless there is a concrete reason not to.
- Make the smallest coherent diff that fully implements the requested behavior.
- Do not mix unrelated cleanup, modernization, formatting, or refactoring into the change.

## Keep Code Small

- Reuse existing helpers and patterns before adding new ones.
- Remove accidental complexity exposed by the change when doing so is local and clearly safe, but do not expand the task into a cleanup project.
- Do not create interfaces, factories, adapters, wrappers, configuration switches, extension points, or generic utilities for hypothetical future needs.
- Do not add comments or documentation that merely restate what readable code already says.

## Avoid Defensive Bloat

- Handle failures that are required by an actual external boundary, invariant, security rule, data-integrity requirement, or observed behavior.
- Do not add retries, fallbacks, duplicate validation, broad exception swallowing, null guards, compatibility layers, or recovery paths solely for imagined possibilities.
- Keep necessary validation at the narrowest authoritative boundary instead of duplicating it across layers.
- Never remove required safety or integrity checks in the name of fewer lines.

## Existing Tools and State

- Use Git diff, status, log, or blame when they provide useful evidence or project history.
- A Git repository is not a prerequisite for implementation, and commits or branches are not mandatory unless the user or project requires them.
- Use representative data for UI inspection when real data is unavailable and the layout cannot be judged meaningfully without it; do not introduce a specific mocking library by default.

## Escalate Only When Triggered

- If a material architecture, dependency, API, data, or compatibility choice appears, load `decision.md`.
- If behavior fails or verification exposes an error, load `debugging.md`.
- If verification strategy becomes non-trivial, load `verification.md`.
