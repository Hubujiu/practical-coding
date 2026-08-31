# Intent Clarification

Load this module **before execution** only when the user's intended outcome is materially under-specified and choosing the wrong interpretation could change delivered behavior or cause meaningful rework.

This is the Practical Coding equivalent of a focused `grill-me` / requirements interview. It is not a mandatory planning phase.

Do not load it merely because a request is short. If the desired behavior and observable success are already clear enough to make a reversible local change, proceed with Core.

## Resolve facts before asking

Do not ask the user for facts that the repository, current artifact, established contract, or authoritative source can answer cheaply. Inspect those first.

Ask only about **user-owned intent**: desired behavior, scope, priorities, non-goals, acceptable trade-offs, or ambiguous outcomes that materially change what should be built.

## Interrogate the current frontier

Work on the highest-impact unresolved intent decision whose prerequisites are already known.

Ask **one question at a time** when an answer can change the next question. Include a concrete recommendation so the user can accept or correct it instead of designing from zero.

Use this compact form when useful:

```text
Question: <one consequential ambiguity>
Recommendation: <the smallest/default interpretation and why>
Trade-off: <what materially changes if the alternative is chosen>
```

Do not dump a questionnaire. Do not ask implementation-detail questions that should be decided from project conventions or the later Decision Gate.

When the user explicitly asks to be grilled, interviewed, pressure-tested, or to think through the plan before coding, remain in clarification mode until the user ends the interview or the next concrete action is unambiguous.

## Convergence

Stop clarifying when all of these are true enough for the next action:

- the observable success condition is clear;
- material in-scope and out-of-scope behavior is clear;
- hard user-owned constraints are known;
- contradictions that would change the result are resolved;
- remaining uncertainty is technical, cheap/reversible, or can be validated during execution.

Then return a compact intent capsule: success condition, material constraints/non-goals, and any deliberately deferred ambiguity.

If a material **solution choice** remains after intent is clear, route that choice to `references/decision.md`. Otherwise enter Core/E0 directly.
