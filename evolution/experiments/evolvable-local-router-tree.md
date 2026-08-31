# EXP-20260901 — Evolvable local router tree

Status: **candidate implemented; benchmark execution pending**

## Observation

The accepted v1.5 flat Event Router restored delivered quality after the rejected fixed E0-E3/R0-R3 capability-tree experiment, but it also restored two assumptions that are not established by that evidence:

1. Decision is again an automatic route, even though a technical choice can appear repeatedly during execution and reopen deliberation after another route has already started.
2. Core owns the whole automatic reasoning taxonomy, so progressive disclosure applies to reference content but not to routing knowledge itself.

The rejected progressive-tree result showed that its predefined numeric levels and specialist leaves did not earn stable lift. It did **not** establish that all tree-shaped progressive disclosure is harmful.

## Hypothesis

A local router tree can preserve progressive disclosure without the failed numeric taxonomy if:

- Core is only the root and knows immediate children;
- every loaded node owns only its own immediate children and current disclosure depth;
- nodes may be leaves and branches may have unequal depth;
- automatic routing only deepens execution and never reopens Decision;
- Decision and Clarification are explicit-only manual modes;
- benchmark ablation derives minimum-sufficient nodes instead of scoring against a predefined automatic route;
- repeated benchmark evidence is allowed to change the topology itself.

## Candidate runtime

Initial seed:

```text
Automatic
Core (0)
├── Debugging (1, leaf)
└── Implementation (1, leaf)

Manual only
├── Decision
└── Clarification

Retrieval
└── orthogonal capability expansion
```

Changes:

- remove Decision from the automatic root router;
- move Decision to `references/manual/decision.md`;
- prohibit automatic nodes from routing to manual modes;
- add a convergence rule for technical choices discovered during execution;
- make depth explicit metadata in the node prose, where depth means disclosure depth only;
- add a Local Router section to Debugging and Implementation; both start as leaves;
- state that future descendants are owned by their parent, not Core.

## Benchmark redesign

The active tree benchmark is intentionally separate from the legacy flat-router and fixed-level scorers.

`benchmarks/tree_topology.json` stores the candidate topology as data.

`benchmarks/tree_cases.py` contains frozen real-repository tasks but no `expected_reasoning`, E0-E3 level, or automatic `capability_path` oracle. It includes explicit manual Decision tasks and negative controls where execution encounters technical alternatives but should not open Decision automatically.

`benchmarks/tree_validation.py` runs:

- no-skill;
- frozen v1.5 baseline at `ba4058b4ef47a42bf79c9963b25678a2389897c1`;
- adaptive current tree;
- one capability ceiling for every automatic node path.

`benchmarks/tree_analysis.py` derives minimum-sufficient node sets from stable passing ceilings. Adaptive route disagreement is diagnostic evidence about the topology, not a release failure by itself. Delivered quality, trace validity, zero spontaneous manual activation, and explicit-manual adherence remain gates.

The analyzer can emit topology candidates such as:

- remove a node with no marginal lift or minimum-sufficient cases;
- promote/collapse a nearly mandatory child;
- merge/move sibling boundaries with repeated co-minimality;
- deepen/split a leaf with a repeated quality-failure cluster.

## Frozen iteration protocol

1. Run tree self-tests.
2. Run current-only n=1 on all tree cases.
3. Inspect scorer correctness before inspecting topology recommendations.
4. If failures form a repeated mechanism, freeze one topology mutation candidate before editing runtime wording.
5. Compare the mutation to its immediate parent topology with the same cases.
6. Only after runtime, topology, cases, and scorers freeze, run n=3 with v1.5 and no-skill arms.
7. Preserve raw outputs and do not rewrite v1.5 or rejected-tree historical evidence.

## Acceptance questions

This experiment is not accepted merely because the new Router looks cleaner. Evidence must answer:

- Does manual-only Decision eliminate spontaneous deliberation without reducing delivered quality?
- Does local routing reduce root context/control-state cost without increasing under-disclosure?
- Which seed nodes are actually minimum-sufficient for repeated task clusters?
- Does any child earn another depth level?
- Are Debugging and Implementation stable sibling boundaries, or should benchmark evidence merge/move/split them?

## Result

Pending fresh n=1 and frozen n=3 evidence. The current branch is an experiment implementation, not a release claim.
