# Manual Decision Mode

**Manual activation only.** Load this module only when the user's current instruction explicitly asks to compare materially different options, make a decision together, or use Decision mode before implementation.

Do not activate it merely because alternatives exist, a choice seems consequential, or the model prefers confirmation. The adaptive router is not allowed to select this module.

## Resolve the requested decision

1. State the decision and the constraints that materially distinguish acceptable options.
2. Resolve discoverable facts before asking the user.
3. Keep at most three viable options and compare only material correctness, compatibility, operational, maintenance, migration, cost, and license differences.
4. Recommend the smallest option that fully satisfies the stated constraints.
5. Ask the user only when the explicit Decision interaction requires a user-owned preference or trade-off.

Use this compact shape when useful:

```text
Decision: <one consequential choice>
Recommendation: <preferred option and why>
Trade-off: <strongest material cost or viable alternative>
```

When the user selects/delegates the option, return the selected choice, rationale, strongest trade-off, and any assumption that can materially change implementation.

Do **not** automatically enter a requirements interview or another manual mode. Return control to the default Core/E0 path unless the user's original instruction explicitly requested additional manual interaction.