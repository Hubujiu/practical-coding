# Practical Coding

This repository is an Agent Skill. Apply [`SKILL.md`](SKILL.md) when working from this checkout.

## Runtime model

1. Apply the Core and stay Direct unless one present unresolved event matches the Router.
2. Route only Debugging, Decision, or Implementation; load at most one reasoning reference for the current event.
3. Complete routing before diagnostic, decision-research, or change-mapping source work. The selected reference is the next read.
4. Keep retrieval orthogonal. Unknown paths, callers, consumers, and data flow are retrieval questions, not Implementation events.
5. Contract to the smallest affected surface as soon as the cause, choice, contract, invariant, or evidence boundary is established.

## Event Router

| Present unresolved event | Reference |
|---|---|
| Observed failure still lacks an evidenced cause | [`references/debugging.md`](references/debugging.md) |
| Material user-owned implementation choice changes the next action | [`references/decision.md`](references/decision.md) |
| Unknown contract/invariant, coordinated guarantee, material risk boundary, or evidence plan blocks safe execution | [`references/implementation.md`](references/implementation.md) |

A known target and settled behavior/boundary/check stay Direct even when risk nouns are present. A read-only mapping request is Direct plus Retrieval.

Requirements interviewing is explicit-only through [`references/manual/clarification.md`](references/manual/clarification.md).

## Retrieval

Use known source, then bounded/ranked search, then an already-available structural capability when it materially reduces relationship discovery. Use exhaustive coverage or external authoritative sources only when the claim requires them. Source remains authoritative.

Read [`references/navigation.md`](references/navigation.md) only for substantial retrieval. Missing graph/ranked capabilities fall back without installing or persisting tooling solely for retrieval.

## Evolution

`evolution/` is maintainer knowledge and must not enter ordinary runtime context. During Skill maintenance, record mechanisms and failed changes there before modifying another runtime rule. Iterations use n=1; only a frozen release candidate receives the complete n=3 matrix.
