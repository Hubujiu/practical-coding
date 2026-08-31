# Decision

Load this module only when a material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations remains open—including whether or which package, library, service, or mature external implementation to adopt. Its output is a resolved choice that changes the next action, not a design essay or option dump.

Do not load this module when the request or repository has already settled the material choice. The existence of a popular alternative is not by itself a Decision event.

## Decision Frontier

Resolve discoverable facts from the repository and authoritative sources before asking the user. Work only on choices whose prerequisites are already known. Ask only about user-owned scope, compatibility, risk tolerance, cost, or preference when at least two plausible answers lead to materially different next actions and choosing the wrong default costs more than one interaction.

For each necessary question, explain why it matters, recommend one option with the reason, and state the strongest trade-off. Ask every independent decision on the current frontier in one round; defer dependent questions. If uncertainty is cheap and reversible, choose the repository or platform default and proceed.

Use a compact stable shape so the recommendation is visible rather than buried in prose:

```text
Q<n> — Decision: <one consequential question>
Recommendation: <one position and why>
Trade-off: <the strongest cost or viable alternative>
```

End with the smallest answer format and wait. When the reply resolves the frontier, do not ask for confirmation of a now-determined choice.

## Resolve

1. State the exact decision and constraints that distinguish acceptable options.
2. Check, in order: established project pattern, standard library, platform/framework, installed dependency, then mature maintained external implementation.
3. Keep at most three viable options and compare only material fit, correctness, compatibility, operational, maintenance, and migration differences.
4. Select the smallest option that fully satisfies current requirements. Do not create an abstraction, dependency, wrapper, or extension point without a present need.

Research only when local evidence cannot resolve a lasting choice or an external dependency is being considered. Prefer official and maintained sources; verify API fit, maintenance, license, and known constraints. Unless an unresolved assumption requires one extra line, every resolved final decision is exactly two lines: `Recommendation:` with selection and reason, then `Trade-off:` with the strongest cost or alternative. Proceed only within existing authorization.

## Durable Decisions

Record the decision only if its reason is not evident in code, future maintainers will likely reconsider it, and the project already has an appropriate mechanism or the user requested one.
