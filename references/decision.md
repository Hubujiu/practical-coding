# Decision

Load this module only when the task contains a material engineering choice.

## Clarify Only What Matters

- Resolve questions from code, project instructions, documentation, types, configuration, and history before asking the user.
- Ask the user only for product, scope, compatibility, risk, or preference decisions that materially change the implementation.
- Do not turn straightforward implementation into a design interview.

## Solution Ladder

Stop at the first option that fully satisfies the requirement:

1. Does the requested capability need to exist?
2. Can existing project code or an established project pattern solve it?
3. Can the standard library solve it?
4. Can the platform or framework solve it natively?
5. Can an already-installed dependency solve it cleanly?
6. For a non-trivial capability or new dependency, research established solutions and official guidance.
7. If a proven solution fits, integrate the smallest suitable one.
8. Add a new dependency only when its reliability, maintenance, or complexity benefit justifies its cost.
9. Otherwise implement the smallest custom solution informed by the research.

## Research

- Research before adding a dependency or building a non-trivial capability that likely has mature prior art.
- Prefer official documentation, maintained libraries, mature implementations, and credible engineering discussions.
- Compare meaningful alternatives when the choice has lasting cost; do not research simple local edits for ceremony.
- Do not copy the first implementation found without checking fit, maintenance state, constraints, and license when relevant.

## Design Boundaries

- Choose the simplest implementation that fully satisfies the current requirement.
- Prefer one end-to-end working path over speculative extensibility.
- Avoid abstractions with no current second use, configuration nobody needs, wrappers that only delegate, and layers that do not enforce a real boundary.
- Preserve intentional APIs, data formats, architecture, and compatibility contracts unless the requirement authorizes changing them.
- Before reversing an intentional architecture decision, inspect available decision records, documentation, and relevant history.
- Prefer durable choices over knowingly temporary architecture that creates a second migration without a concrete need.

## Durable Decisions

Record a concise decision only when all are true:

- the choice is material;
- its reason is not obvious from the resulting code;
- future maintainers or agents are likely to reconsider it;
- the project already has an appropriate documentation or history mechanism, or the user requested one.

Do not document reconstructable facts such as file locations, call relationships, changed files, task progress, or information Git and code already preserve.
