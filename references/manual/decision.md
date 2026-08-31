# Manual Decision

This mode is outside the automatic execution tree.

Load it only when the current user explicitly asks to compare options, choose a technology or architecture, recommend among dependencies/APIs/data models/compatibility strategies, or otherwise perform decision analysis. The existence of alternatives, ambiguity, risk, or a technical choice discovered during execution does not activate this mode.

## Decision Frontier

Resolve discoverable facts from the repository and authoritative sources before asking the user. Work only on choices whose prerequisites are already known. Ask only about user-owned scope, compatibility, risk tolerance, cost, or preference when at least two plausible answers lead to materially different next actions and choosing the wrong default costs more than one interaction.

For each necessary question, explain why it matters, recommend one option with the reason, and state the strongest trade-off. Ask every independent decision on the current frontier in one round; defer dependent questions. If uncertainty is cheap and reversible, choose the repository or platform default.

Use a compact stable shape when a user choice is needed:

```text
Q<n> — Decision: <one consequential question>
Recommendation: <one position and why>
Trade-off: <the strongest cost or viable alternative>
```

## Resolve

1. State the exact decision and constraints that distinguish acceptable options.
2. Check, in order: established project pattern, standard library, platform/framework, installed dependency, then mature maintained external implementation.
3. Keep at most three viable options and compare only material fit, correctness, compatibility, operational, maintenance, and migration differences.
4. Select the smallest option that fully satisfies current requirements. Do not create an abstraction, dependency, wrapper, or extension point without a present need.

Research only when local evidence cannot resolve a lasting choice or an external dependency is being considered. Prefer official and maintained sources; verify API fit, maintenance, license, and known constraints.

When the requested decision is resolved, stop this mode. Return the settled result to Core as input. Do not route directly from this file to Debugging, Implementation, Clarification, or any descendant.

## Durable Decisions

Record the decision only if its reason is not evident in code, future maintainers will likely reconsider it, and the project already has an appropriate mechanism or the user requested one.
