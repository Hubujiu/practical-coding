# EXP-20260901 — Evolvable local router tree

Status: **isolated leaf candidate n=1 qualified; paired n=3 pending**

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

The normalized current-only run at `benchmark-results/tree-delivery-n1-normalized-20260901-125524` completed 106/106 determinate cells. Adaptive passed 15/15 tasks, all 15 traces were valid, both explicit manual Decision tasks passed, and no automatic task activated a manual mode.

This qualifies the frozen candidate for the complete n=3 run; it is not yet a release or superiority claim. Capability minima varied across n=1 repetitions, so node removal/promotion decisions are deferred to repeated paired evidence against the frozen v1.5 and no-skill arms.

The first complete paired n=3 artifact (`benchmark-results/tree-final-eca9a09-20260901`) failed the release gate and was retained as diagnostic evidence. It exposed remaining semantic-oracle gaps and showed that none of the four staged depth-2 nodes entered a minimum-sufficient set. After general oracle corrections, a fresh 106-cell n=1 passed completely, again with no depth-2 marginal lift.

The candidate therefore returned to the original seed topology: Core with leaf Debugging and Implementation children, plus explicit-only manual Decision/Clarification. The first leaf run exposed one further recommendation-inflection oracle defect; after freezing and correcting it, `benchmark-results/tree-delivery-n1-leaves-inflection-20260901` completed 58/58 determinate cells with adaptive 15/15, all three capability ceilings 13/13, trace 15/15, explicit manual 2/2, and zero spontaneous manual activation. This leaf candidate is frozen for a new paired n=3; superiority remains pending.

That paired rerun also failed and revealed two additional mechanisms: deterministic evidence identities and trace instrumentation needed command-observed normalization, while retired child documents still under `references/` remained discoverable despite their removal from the topology. After freezing those mechanisms, adding positive/negative harness tests, and removing the four retired documents from the runtime reference surface, `benchmark-results/tree-delivery-n1-retired-isolated-20260902` completed 58/58 with every arm/capability cell passing and all trace/manual gates clean. This isolated leaf candidate is the current frozen n=3 candidate; no superiority claim exists until the new paired report completes.
