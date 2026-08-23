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
- Remove accidental complexity exposed by the change when doing so is local and clearly safe, but keep the task's scope; cleanup beyond the change is a separate task.
- Create an interface, factory, adapter, wrapper, configuration switch, extension point, or generic utility only when the current task demonstrates the need for it.
- Write comments and documentation for intent, constraints, and reasons the code cannot express; readable code carries the rest.

## Match Error Handling to Real Boundaries

- Every failure path in the code corresponds to an actual external boundary, invariant, security rule, data-integrity requirement, or observed behavior.
- A retry, fallback, broad catch, null guard, compatibility layer, or recovery path responds to a concrete, documented, or observed failure mode; name that failure mode when adding one.
- Necessary validation lives once, at the narrowest authoritative boundary.
- Required safety and integrity checks stay in place even when trimming code.

## Existing Tools and State

- Use Git diff, status, log, or blame when they provide useful evidence or project history.
- A Git repository is not a prerequisite for implementation, and commits or branches are not mandatory unless the user or project requires them.
- Use representative data for UI inspection when real data is unavailable and the layout cannot be judged meaningfully without it; do not introduce a specific mocking library by default.

## Escalate Only When Triggered

- If a material architecture, dependency, API, data, or compatibility choice appears, load `decision.md`.
- If behavior fails or verification exposes an error, load `debugging.md`.
- If verification strategy becomes non-trivial, load `verification.md`.
