---
name: practical-coding
description: Use when implementing, modifying, debugging, refactoring, or reviewing code, or making architecture and dependency decisions in a software project.
---

# Practical Coding

## Boundaries

- Understand the current requirement and inspect the relevant code and real execution flow before designing a solution.
- Start with the smallest relevant context and expand only when the current evidence is insufficient.
- Resolve material ambiguity before implementation, and inspect the available code and context instead of asking questions they can answer.
- When a user decision is required, ask one focused question at a time and stop once the current task is clear.
- Do not build capabilities that the current requirement does not need.
- Choose the simplest implementation that fully satisfies the current requirement.
- Prefer existing code, standard libraries, platform-native capabilities, and installed dependencies before adding code or packages.
- Research established solutions before adding a dependency or implementing a non-trivial capability.
- Compare proven solutions instead of copying the first implementation you find.
- Add a dependency only when its reliability or complexity benefit justifies its maintenance cost.
- Keep components focused and concerns separated without speculative abstractions, configuration, or indirection.
- Grow the system from the smallest working end-to-end version without replacing working simplicity with unfinished complexity.
- Preserve existing APIs, data formats, and compatibility contracts unless the user explicitly authorizes changing them.
- Before changing or reversing architecture, inspect available project instructions, decision records, design documents, and relevant Git history, and do not override an intentional decision merely because another design looks cleaner in isolation.
- Make architectural decisions that can last instead of introducing stopgaps intended for later replacement, and leave durable evidence for material new decisions through the project's existing documentation or history system.
- Never remove necessary validation, security, data-integrity, accessibility, or permission boundaries in the name of simplicity.
- Do not default to generating tests.
- Choose verification proportional to the change's risk, uncertainty, project requirements, and user request, and do not turn verification into open-ended bug hunting outside the requested scope.
- Do not claim completion without fresh evidence appropriate to the changed behavior.
- Diagnose reported or observed failures by reproducing or collecting evidence, tracing backward to the earliest incorrect state, testing one hypothesis at a time, and fixing the root cause instead of the symptom.
- Verify that the original symptom is resolved and remove temporary diagnostic instrumentation before completion.
- Frontend work may add Mock.js to provide representative data for layout inspection.
- Before implementation, confirm that the workspace is a Git repository, and stop to ask the user to create or select one when it is not.
- Create an execution document only for multi-step, long-running, oversized, or handoff-prone work, and keep its progress current.
- Treat the repository, Git state, and recorded evidence as the source of truth instead of reconstructing progress from memory.
- Split oversized work into bounded phases and keep only one phase in progress at a time.
- After creating or restoring an execution document, present it to the user and do not implement it without explicit confirmation.
- When the user changes the proposed execution document, return to requirement clarification and present every affected decision and phase again.
- Commit every coherent checkpoint without mixing unrelated changes, and never push unless the user requests it.

## Decision Flow

```text
Understand the requirement
→ Is any material decision unresolved?
  → Can the codebase, documentation, or supplied context resolve it?
    → Yes: inspect them and decide
  → Does it require the user's product, scope, or risk decision?
    → Yes: ask one focused question
    → Repeat only until the current task is clear
→ Inspect the relevant code and real flow
→ Is the current context sufficient?
  → No: expand to the next relevant surface and inspect again
→ Does this need to exist?
  → No: stop
→ Can existing code solve it?
  → Yes: reuse or modify it
→ Can the standard library or platform solve it?
  → Yes: use it
→ Can an installed dependency solve it?
  → Check its documentation and types, then use it
→ Does this require a new dependency or non-trivial capability?
  → Research official guidance, mature implementations, established products, and engineering discussions
→ Does a proven solution fit and justify its cost?
  → Yes: integrate the smallest suitable solution
→ Is a new dependency justified?
  → Yes: add the smallest suitable dependency
  → No: implement the smallest custom solution informed by the research
→ Is the workspace a Git repository?
  → No: ask the user to create or select a Git environment, then stop
→ Does an execution document already exist?
  → Yes: read it, then reconcile it with Git status, log, and diff
→ Is the task multi-step, long-running, oversized, or likely to require handoff?
  → Yes: read references/execution-document.md
         → Create or resume the execution document
         → Split the work into bounded phases
         → Keep exactly one phase in progress
         → Present the plan and current state to the user
         → User confirms the current execution document?
           → No: record the requested changes
                 → Return to requirement clarification
                 → Revise every affected decision and phase
                 → Present the updated execution document again
           → Yes: commit the approved execution document
→ Deliver the smallest working end-to-end change or current approved phase
→ Update the execution document after every completed, changed, or blocked phase
→ Did execution reveal a material scope, architecture, dependency, or risk change?
  → Yes: pause and return to the execution-document confirmation loop
→ Is a failure reported or observed within scope?
  → Yes: reproduce it or collect evidence
         → Trace backward to the earliest incorrect state
         → Form and test one hypothesis at a time
         → Fix the root cause
         → Verify the original symptom is resolved
         → Remove temporary diagnostic instrumentation
→ Frontend?
  → Add Mock.js when layout inspection needs representative data
  → Inspect the rendered layout
→ Choose verification proportional to risk, uncertainty, project requirements, and the user's request
→ Does justified verification require new tests?
  → Yes: add the smallest targeted tests that provide material evidence
  → No: use the appropriate existing checks or direct behavioral evidence
→ Does fresh evidence support the completion claim?
  → No: report the actual status and remaining uncertainty
→ Simplify the final diff
→ Commit the coherent checkpoint without unrelated changes
```
