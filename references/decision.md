# Decision

Load this module only when a material unresolved choice blocks or materially changes the next safe action. Its output is a settled choice and the constraints needed for execution, not a design essay, option dump, or mandatory interview.

Do not load this module when the request, repository, authoritative constraint, or a cheap reversible default already settles the choice. The existence of another package, library, service, architecture, or implementation is not by itself a Decision Gate.

## Decision Frontier

Resolve discoverable facts from the repository and authoritative sources before asking the user. Keep a compact ledger of verified facts, constraints, assumptions, settled choices, and unresolved choices. Work only on the current frontier: choices whose prerequisites are already known. Do not ask about a downstream choice while an upstream answer could invalidate it.

Research is part of resolving an open Decision. Compare viable mature implementations when external evidence is necessary; do not ask the user merely for permission to research. Ask only about user-owned scope, compatibility policy, risk tolerance, cost, or preference when at least two plausible answers lead to materially different next actions and choosing the wrong default costs more than one interaction.

Ask every independent user-owned decision on the current frontier in the same round; dependent questions wait for a later round. For every question:

- explain briefly why the decision matters now;
- recommend one option and give the reason;
- name the strongest material trade-off or alternative;
- number it so the user can answer the whole round compactly.

Use this compact shape so the recommendation is not hidden inside an option list:

```text
Q<n> — Decision: <one consequential question>
Recommendation: <one position and why>
Trade-off: <the strongest cost or viable alternative>
```

End the round with the smallest answer format, then wait. If the task is already sufficiently specified, ask nothing. If uncertainty is cheap and reversible, choose the repository or platform default and proceed. Each reply reshapes the decision tree: record settled choices, recompute the frontier, and reopen a dependent choice only when new evidence contradicts an earlier assumption.

When the user's answers resolve the current frontier and no newly unlocked independent user-owned choice remains, state the selected option and stop. Do not ask for confirmation of a now-determined choice. Return a compact execution capsule: selected option, governing constraints, strongest trade-off, assumptions, and any concrete validation still required.

## Resolve

1. State the exact decision and the constraints that distinguish acceptable options.
2. Check, in order: established project pattern, standard library, platform/framework, installed dependency, then mature maintained external implementation. Research external options only when the open choice cannot be resolved from local evidence; do not install or vendor an option merely to compare it.
3. Keep at most three viable options. Compare only material fit, correctness, compatibility, operational, maintenance, and migration differences.
4. Select the smallest option that fully satisfies current requirements. Do not create an abstraction, dependency, wrapper, or extension point without a present need.

Research only when local evidence cannot resolve a lasting choice or an external dependency is being considered. Prefer official and maintained sources; verify API fit, maintenance, license, and known constraints. Integrate a fitting mature surface instead of cloning it, and isolate only a demonstrated compatibility patch.

Converge when the goal and success condition are clear, hard constraints and non-goals are known, high-impact choices are resolved or deliberately deferred, material contradictions are gone, and remaining uncertainty is cheap to reverse or assigned to a concrete validation step.

## Exit to Execution

Decision resolution does not imply that execution needs another rigor profile. Return to the Core first. If safe execution is already known, continue Direct. If a different substantial blocker later requires Debugging or Implementation and this reference is already resident in the root, prefer an isolated follow-up when context savings exceed handoff cost rather than accumulating a second reasoning reference.

## Durable Decisions

Record the decision only if its reason is not evident in code, future maintainers will likely reconsider it, and the project already has an appropriate mechanism or the user requested one. Do not document facts reconstructable from code or Git.
