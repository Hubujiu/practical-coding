# Decision

Decision is a gate, not an execution level. Load it only when a material choice remains genuinely open, would change the next action, and cannot be settled from the request, repository, established contracts, or a cheap reversible default.

Do not load this module because alternatives exist. A choice already specified or authorized by the user is settled input.

## Decision frontier

Resolve discoverable facts before asking the user. Keep a compact ledger of verified facts, constraints, assumptions, decisions, and unresolved choices. Work only on the current frontier: choices whose prerequisites are known.

Research belongs here when authoritative external evidence is necessary to resolve the open choice. Do not ask permission merely to research. Ask the user only for user-owned scope, compatibility, risk tolerance, cost, or preference when at least two plausible answers lead to materially different next actions and choosing the wrong default costs more than one interaction.

Ask every independent user-owned decision on the current frontier in the same round. For each question:

```text
Q<n> — Decision: <one consequential question>
Recommendation: <one position and why>
Trade-off: <the strongest material cost or viable alternative>
```

If uncertainty is cheap and reversible, choose the repository or platform default and proceed. If the user delegated the choice, select the smallest option that fully satisfies current constraints rather than asking for confirmation.

## Resolve

1. State the exact decision and constraints that distinguish acceptable options.
2. Check, in order: established project pattern, standard library, platform/framework, installed dependency, then mature maintained external implementation.
3. Keep at most three viable options. Compare only material correctness, compatibility, operational, maintenance, migration, cost, and license differences.
4. Select the smallest option that fully satisfies current requirements.
5. Record assumptions or deferred validation only when they can change the result.

Prefer official and maintained sources for external facts. Verify API fit, maintenance, license, and known constraints when they are material. Integrate a fitting mature surface instead of cloning it, and isolate only a demonstrated compatibility patch.

Converge when the success condition is clear, hard constraints and non-goals are known, high-impact choices are resolved or deliberately deferred, material contradictions are gone, and remaining uncertainty is cheap to reverse or assigned to a concrete validation step.

Then return the selected option, rationale, strongest trade-off, assumptions, and deferred validation compactly. Continue execution at the lowest rung consistent with those settled facts.

## Durable decisions

Record a decision only if its reason is not evident in code, future maintainers will likely reconsider it, and the project already has an appropriate mechanism or the user requested one. Do not document facts reconstructable from code or Git.
