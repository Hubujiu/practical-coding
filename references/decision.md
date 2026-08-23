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
6. Research mature, maintained implementations and official guidance for the non-trivial capability.
7. If a mature implementation fits, integrate or adapt it instead of building a parallel replacement.
8. Add custom code only for requirements, integration boundaries, or confirmed defects the mature implementation does not cover.
9. If no suitable mature implementation exists, build the smallest custom solution informed by the research.

Package size, local disk use, or implementation ownership are not reasons to prefer a weaker custom solution when the capability is optional and the mature implementation materially improves correctness, token efficiency, reliability, or maintenance.

## Mature Implementation First

- Prefer official, actively maintained, production-used implementations with strong tests and clear licenses.
- Treat a mature implementation as the default baseline, not merely inspiration for rewriting the same capability.
- Before replacing or partially cloning a mature implementation, identify the concrete reason direct integration is insufficient.
- Prefer using the mature project's supported API, CLI, protocol, library, binary, or package surface over copying internal code when that preserves upstream fixes and reduces maintenance divergence.
- If an upstream defect blocks the requirement, first check whether a fixed release or maintained fork already exists. Only then add the narrowest local compatibility shim or patch necessary.
- Keep local patches isolated and attributable so they can be removed when upstream fixes the issue.
- Do not preemptively fork an entire mature project just to gain control over code that already works.

## Research

- Research before adding a dependency or building a non-trivial capability that likely has mature prior art.
- Prefer official documentation, maintained libraries, mature implementations, and credible engineering discussions.
- Compare meaningful alternatives when the choice has lasting cost; do not research simple local edits for ceremony.
- Check fit, maintenance state, known issues, release activity, operational constraints, and license before adopting a solution.
- Reuse does not mean blindly accepting upstream behavior: verify the mature implementation against the current requirement and patch only demonstrated gaps.

## Design Boundaries

- Choose the simplest implementation that fully satisfies the current requirement.
- Prefer one end-to-end working path over speculative extensibility.
- Every abstraction earns its place with a current use, every configuration option with a real user, every wrapper with behavior beyond delegation, and every layer with a real boundary it enforces.
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
