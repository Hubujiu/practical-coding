# Practical Coding

This repository is an Agent Skill. Apply [`SKILL.md`](SKILL.md) when working from this checkout.

## Runtime model

1. Apply Core at tree depth 0.
2. Core knows only its immediate automatic children: Debugging and Implementation.
3. A loaded node owns only its own next-level router. Do not preload siblings or descendants and do not send descendant selection back to Core.
4. Current Debugging and Implementation nodes are leaves until benchmark evidence earns a child.
5. Keep retrieval orthogonal. Unknown paths, callers, consumers, and data flow are retrieval questions, not execution-tree depth.
6. Automatic routing must converge toward resolving the current blocker; it must not reopen deliberation.

## Root Router

| Present unresolved blocker | Immediate child |
|---|---|
| Observed failure still lacks an evidenced cause | [`references/debugging.md`](references/debugging.md) |
| Unknown contract/invariant, coordinated guarantee, material risk boundary, or evidence requirement blocks safe execution | [`references/implementation.md`](references/implementation.md) |

A known target and settled behavior/boundary/check stay at Core even when risk nouns are present. A read-only mapping request is Core plus Retrieval.

## Manual modes

Manual modes are outside the automatic tree:

- [`references/manual/decision.md`](references/manual/decision.md) only for an explicit current request to compare options, choose a technology/architecture/dependency/API/data model, or perform decision analysis;
- [`references/manual/clarification.md`](references/manual/clarification.md) only for an explicit current request to be interviewed, grilled, questioned, or to clarify requirements before implementation.

No automatic node may route to a manual mode. Ordinary technical choices discovered during execution use the established project convention or the smallest sufficient reversible option. If a user-owned choice has no safe default, ask the minimum blocking question in the current context without opening Decision.

## Retrieval

Use known source, then bounded/ranked search, then an already-available structural capability when it materially reduces relationship discovery. Use exhaustive coverage or external authoritative sources only when the claim requires them. Source remains authoritative.

Read [`references/navigation.md`](references/navigation.md) only for substantial retrieval. Missing graph/ranked capabilities fall back without installing or persisting tooling solely for retrieval.

## Evolution

`evolution/` is maintainer knowledge and must not enter ordinary runtime context. The tree is an experiment result, not a fixed taxonomy.

Use [`benchmarks/tree_topology.json`](benchmarks/tree_topology.json), [`benchmarks/tree_validation.py`](benchmarks/tree_validation.py), and [`benchmarks/tree_analysis.py`](benchmarks/tree_analysis.py) for active topology work. Cases must not encode a gold automatic node or fixed numeric execution level. Derive minimum-sufficient nodes by capability ablation, then use repeated routing ambiguity or quality failures to propose add/split/merge/promote/collapse/remove changes.

Iterations use n=1. Only a frozen candidate receives the complete n=3 baseline/no-skill comparison. Preserve v1.5 and rejected progressive-tree artifacts as historical evidence rather than rewriting them for the new topology.
