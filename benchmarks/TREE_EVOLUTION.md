# Evolvable local-router tree

This experiment treats progressive disclosure topology as a learned maintenance artifact rather than a permanent taxonomy.

## Invariants

1. Core is the automatic root at depth 0.
2. Every automatic node owns its behavior, current depth, and only its immediate-child router.
3. A parent does not know grandchildren. A leaf says it has no earned children.
4. Manual Decision and Clarification are outside the automatic tree and require an explicit current user request.
5. Automatic routing may deepen execution to resolve a blocker but may not reopen deliberation.
6. Retrieval is orthogonal. Retrieval breadth does not imply execution depth.
7. Depth means disclosure depth only; branches do not need equal depth or symmetric children.
8. Execution-state projection is also orthogonal. It may preserve current future-relevant facts inside any node, but it is not a task capability and never appears in an automatic path.

## Why the old E0-E3 result does not reject trees

The rejected experiment froze numeric levels and specialist families before the evidence existed, then scored the model against those labels. That tested one predefined taxonomy. It did not test whether local progressive disclosure itself was useful.

The active experiment reverses the dependency:

```text
small candidate topology
        ↓
capability ceilings
        ↓
minimum-sufficient node sets
        ↓
adaptive traces + quality failures
        ↓
topology mutation candidate
        ↓
new frozen experiment
```

The benchmark is therefore allowed to conclude that a node should disappear, move, merge, split, or gain a child.

## Capability ceilings

For every ordinary task, `tree_validation.py` runs the current Skill with these capability arms:

- Core only;
- every root-to-node path in `tree_topology.json`;
- adaptive disclosure with the full current tree.

A capability ceiling is not an expected route. It asks a counterfactual question: *if no capability below this node were available, could the task still be delivered correctly?*

At n=3 a ceiling is considered stable passing only when every determinate repetition passes. `tree_analysis.py` removes any stable-passing node whose ancestor also passes. The remaining nodes form the task's **minimum-sufficient set**.

Multiple minimum nodes are valid. They are evidence that more than one branch can solve the task at the same disclosure frontier; repeated sibling co-minimality may indicate a weak boundary.

## What gates a candidate

Release quality is primary:

- adaptive delivered quality must remain non-inferior to the frozen v1.5 baseline and no-skill within the configured margin;
- ordinary automatic tasks must have zero spontaneous manual-mode activation;
- explicit manual tasks must activate the requested manual mode;
- adaptive traces must describe a valid parent-child path in the topology manifest.

Exact agreement with one human-authored automatic node is deliberately **not** a release gate.

## Routing diagnostics

Adaptive terminal nodes are compared with the derived minimum-sufficient set:

- `exact_minimum`: stopped on a minimum-sufficient node;
- `over_disclosure`: a sufficient ancestor existed;
- `under_disclosure`: the run stopped above a capability required by the ceiling evidence;
- `alternate_branch`: the adaptive run chose another branch;
- `quality_gap`: no current ceiling solves the task reliably.

These labels diagnose the tree. They do not justify adding benchmark case nouns to runtime prompts.

## Cross-cutting runtime substrates

A mechanism belongs outside the tree when it changes how every node executes rather than what task capability is selected. Execution-state projection is one such candidate:

- activation is caused by state pressure inside a multi-round run, not by a Debugging/Implementation/task-domain label;
- state cannot satisfy a task on its own, so a `Core -> State` capability ceiling is not meaningful;
- deterministic tests should gate schema, merge, deletion, rollback, size, and prompt-construction mechanics;
- model-backed tree tests must still rerun because substrate wording can change delivered quality, route behavior, and cost across every node;
- a markdown Skill alone cannot prove bounded prompt growth when the surrounding host continues to append conversation history.

Do not add a cross-cutting substrate as a child merely to make it visible in the diagram. Promote it into runtime wording only after its own mechanism gate passes, then accept/reject the whole candidate under the existing release non-regression gate.

## Mutation rules

### ADD / DEEPEN

Add a child only when all are true:

- a repeated failure cluster exists under one parent;
- the cluster has an observable pre-load signal that does not require loading the proposed child first;
- the child adds stable quality-qualified lift over the parent across multiple tasks or repositories;
- ordinary parent tasks do not pay the child context cost.

### SPLIT

Split a node when distinct failure clusters require materially different behavior and can be distinguished before loading either child. Do not split merely because domain nouns are recognizable.

### MERGE / MOVE BOUNDARY

Merge siblings or move their boundary upward when they are repeatedly co-minimum-sufficient, frequently confused by adaptive routing, and their separation does not produce net quality or context value.

### PROMOTE / COLLAPSE

Promote child behavior into its parent when the child is required for most of the parent's useful scope. A nearly mandatory child is not progressive disclosure.

### REMOVE

Remove a node when it has no independent minimum-sufficient cases and no stable marginal lift over its parent. Historical symmetry is not a retention reason.

## Experiment discipline

- Use n=1 only for mechanism iteration and scorer correctness.
- Freeze runtime wording, topology, cases, repositories, and scorer contracts before n=3.
- Compare a topology mutation against its immediate parent topology, not only against old public releases.
- Freeze a substrate-specific deterministic benchmark before implementing that substrate; do not let its scorer reward model prose.
- Preserve raw outputs and topology manifests with results.
- Do not edit a frozen case after seeing candidate output unless the oracle itself is demonstrably contradictory; record such corrections separately.
- Do not reopen the rejected numeric E/R taxonomy merely to make the new tree look familiar.

## Current seed topology

The initial seed is intentionally small:

```text
Core
├── Debugging
└── Implementation
```

Both children are current leaves. Decision and Clarification are manual-only. Execution state is a cross-cutting substrate, not a third child. This is a starting hypothesis, not a claim that two children or depth 1 is optimal.
