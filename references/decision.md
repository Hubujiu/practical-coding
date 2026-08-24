# Decision

Load this module only when a material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations remains open. Its output is a choice that changes the next action, not a design essay.

## Resolve

1. State the exact decision and constraints that distinguish acceptable options.
2. Check, in order: established project pattern, standard library, platform/framework, installed dependency, then mature maintained external implementation.
3. Keep at most three viable options. Compare only material fit, correctness, compatibility, operational, maintenance, and migration differences.
4. Select the smallest option that fully satisfies current requirements. Do not create an abstraction, dependency, wrapper, or extension point without a present need.

Research only when local evidence cannot resolve a lasting choice or an external dependency is being considered. Prefer official and maintained sources; verify API fit, maintenance, license, and known constraints. Integrate a fitting mature surface instead of cloning it, and isolate only a demonstrated compatibility patch.

Ask the user only when the remaining choice is product scope, compatibility, risk tolerance, or preference that materially changes the result. Otherwise decide and proceed.

## Durable Decisions

Record the decision only if its reason is not evident in code, future maintainers will likely reconsider it, and the project already has an appropriate mechanism or the user requested one. Do not document facts reconstructable from code or Git.
