# Evolvable local-router trees

This experiment treats progressive disclosure topology as a learned maintenance artifact rather than a permanent taxonomy. Execution reasoning and source Retrieval are independent trees with different signals, ceilings, and analysis.

## Invariants

1. Core is the automatic execution root at depth 0.
2. Every automatic execution node owns its behavior, current depth, and only its immediate-child router.
3. A parent does not know grandchildren. A leaf says it has no earned children.
4. Manual Decision and Clarification are outside both automatic trees and require an explicit current user request.
5. Automatic execution routing may deepen to resolve a blocker but may not reopen deliberation.
6. Retrieval starts at its own root and progresses only through the current node's immediate child.
7. Retrieval depth describes the unresolved information problem, not repository size, execution risk, or provider strength.
8. Navigation only bounds the repository area. It is not semantic discovery, evidence expansion, or graph tracing.
9. Ranked retrieval, graph retrieval, and execution-output compaction are capability providers outside both trees.
10. Provider setup, indexing, dependency resolution, and first-build warm-up occur before model measurement and never enter compared token, duration, or tool-call fields.
11. Depth means disclosure depth only; branches do not need equal depth or symmetric children.

## Current seed topologies

### Execution

```text
Core
├── Debugging      (leaf)
└── Implementation (leaf)
```

### Retrieval

```text
Retrieval Root
└── R0 Direct Locate
    └── R1 Ranked Discovery
        └── R2 Evidence Expansion
            └── R3 Structural Trace (leaf)
```

The execution tree branches by blocker type. The Retrieval seed is a monotonic path because each stage answers a strictly deeper unresolved information question. Benchmark evidence may still merge, split, reorder, promote, or remove these nodes.

## Why the old E0-E3 result does not reject trees

The rejected experiment froze numeric levels and specialist families before evidence existed, then scored the model against those labels. That tested one predefined taxonomy. It did not test whether local progressive disclosure itself was useful.

The active experiment reverses the dependency:

```text
small candidate topology
        ↓
parent/stage capability ceilings
        ↓
minimum-sufficient node or Retrieval stage
        ↓
adaptive traces + delivered quality + measured cost
        ↓
topology mutation candidate
        ↓
new frozen experiment
```

The benchmark is therefore allowed to conclude that a node should disappear, move, merge, split, or gain a child.

## Execution capability ceilings

`dependency_tree_validation.py` wraps the existing execution-tree runner with the mandatory provider and warm-up contract. For every ordinary task it exposes:

- Core only;
- every root-to-execution-node path in `tree_topology.json`;
- adaptive execution disclosure with the full current execution tree.

A capability ceiling is not an expected route. It asks: *if no execution capability below this node were available, could the task still be delivered correctly?*

At n=3 a ceiling is stable passing only when every determinate repetition passes. `tree_analysis.py` removes stable-passing descendants whose ancestor already passes. The remaining nodes form the task's minimum-sufficient execution-node set. Multiple minimum nodes are valid evidence of alternate sufficient branches or a weak boundary.

## Retrieval capability ceilings

`retrieval_validation.py` keeps the automatic execution tree adaptive while running the same task under these Retrieval ceilings:

- `NONE` — current Skill without loading the Retrieval tree;
- `R0_DIRECT` — Retrieval root plus Direct Locate;
- `R1_DISCOVERY` — adds ranked candidate discovery;
- `R2_EVIDENCE` — adds bounded cross-file evidence construction;
- `R3_STRUCTURAL` — adds graph relationship tracing.

All required provider binaries remain installed for every ceiling. The ceiling restricts policy references and deeper-stage provider use:

- `rtk` is available at every stage because output compaction is not Retrieval;
- `zg` becomes available to Retrieval at R1;
- `codebase-memory-mcp` becomes available at R3;
- repository-native exact reads/search remain available at every stage.

`NONE` is the no-Retrieval-policy control: no Retrieval reference is loaded, while repository-native exact reads remain available. `R0_DIRECT` is the first loaded policy prefix (`Retrieval root -> Direct Locate`).

The active runner compares the declared prefix with reference paths actually observed in commands. Missing parent reads, hidden deeper reads, or claimed-but-unread nodes invalidate the trace.

`retrieval_analysis.py` selects the shallowest stage whose repetitions all pass. That is the task's minimum-sufficient Retrieval stage. Adaptive disclosure is then classified as exact, over-disclosed, under-disclosed, invalid, or a quality gap.

R2 and R3 are not justified merely because an agent loaded them. They survive only if their ceilings solve stable task clusters that shallower stages cannot solve with equal delivered quality.

## Required provider environment

`capability_manifest.json` requires three roles:

- ranked retrieval through `zg`;
- graph retrieval through `codebase-memory-mcp`;
- execution-output compaction through `rtk`.

The benchmark fails closed when a binary is missing, a probe fails, indexing fails, repository warm-up fails, or setup dirties the frozen workspace. There is no allow-missing path for provider-enabled claims.

Normal Skill runtime remains portable and retains bounded fallbacks. Provider absence is a separate runtime condition, not noise mixed into this experiment.

## Measurement boundary

Each comparison cell has two phases.

### Unmeasured setup

Before Codex starts, the runner:

1. probes required providers;
2. initializes local provider assets;
3. creates the workspace ranked index;
4. creates a per-workspace graph in one explicit shared Codebase Memory daemon/cache cohort;
5. warms each provider query path, repository dependencies, and the first focused test/build path;
6. verifies a clean worktree;
7. writes `capability-setup.json` with `included_in_comparison: false`.

Setup elapsed time and output bytes are auditable but never merged into model records. Setup reports contain no token estimate.

### Measured execution

Only `run_codex` and the transcript after setup contribute:

- input/cached-input/output/reasoning/total tokens;
- model-visible tool calls;
- measured duration;
- answer quality and routing trace.

Every paired arm receives the same initialized environment. A measured attempt to reinstall packages, rebuild provider indexes, or initialize the output adapter is a contract failure rather than accepted cold-start cost.

## What gates a candidate

Release quality is primary:

- adaptive delivered quality must remain non-inferior to the frozen v1.5 baseline and no-skill within the configured margin;
- ordinary tasks must have zero spontaneous manual-mode activation;
- explicit manual tasks must activate the requested manual mode;
- execution traces must describe a valid parent-child path;
- Retrieval traces must use canonical stages and list a complete loaded root-to-stage prefix;
- a Retrieval ceiling must not use a provider owned by a deeper stage;
- measured setup-violation count must be zero;
- all setup receipts must match the frozen capability manifest.

Exact agreement with one human-authored execution node is deliberately not a release gate. Retrieval minimum stage is derived from quality-qualified ceilings, not prompt nouns.

## Diagnostics

### Execution

- `exact_minimum` — adaptive execution stopped on a minimum-sufficient node;
- `over_disclosure` — a sufficient execution ancestor existed;
- `under_disclosure` — execution stopped above a required capability;
- `alternate_branch` — adaptive execution chose another branch;
- `quality_gap` — no current execution ceiling solves the task reliably.

### Retrieval

- `exact_minimum` — adaptive Retrieval stopped on the shallowest stable-passing stage;
- `over_disclosure` — a shallower stage already passed;
- `under_disclosure` — adaptive stopped before the minimum stage;
- `invalid_trace` — the canonical stage/reference-prefix contract failed;
- `quality_gap` — no current Retrieval ceiling solves the task reliably;
- `adaptive_quality_failure` — the adaptive result itself failed quality.

These labels diagnose topology. They do not justify adding benchmark case nouns to runtime prompts.

## Cross-cutting infrastructure

A mechanism belongs outside both trees when it changes how every node executes rather than which task or information capability is selected.

RTK-style output compaction is such infrastructure:

- it may wrap shell, test, build, and Git output at any execution or Retrieval depth;
- a `Core -> Output Compression` or `R2 -> RTK` tree edge is meaningless;
- compaction must preserve semantics, exit status, failures, and material evidence;
- provider initialization is setup, while model-visible compact commands remain measured execution;
- replacing the provider should not require Retrieval-policy changes.

Do not add a cross-cutting provider as a child merely to make it visible in a diagram.

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

Merge siblings or move their boundary when they are repeatedly co-minimum-sufficient, frequently confused by adaptive routing, and their separation does not produce net quality or context value.

For the linear Retrieval seed, merge adjacent stages when the deeper stage has no independent minimum-sufficient cluster or the boundary cannot be observed before loading it.

### PROMOTE / COLLAPSE

Promote child behavior into its parent when the child is required for most of the parent's useful scope. A nearly mandatory child is not progressive disclosure.

### REMOVE

Remove a node when it has no independent minimum-sufficient cases and no stable marginal lift over its parent. Historical symmetry or a provider's existence is not a retention reason.

## Experiment discipline

- Use n=1 only for mechanism iteration and scorer correctness.
- Freeze runtime wording, both topologies, capability manifest, warm-up commands, cases, repositories, and scorer contracts before n=3.
- Compare a topology mutation against its immediate parent topology, not only against old public releases.
- Preserve raw outputs, setup receipts, provider preflight, and topology manifests with results.
- Do not edit a frozen case after seeing candidate output unless the oracle itself is demonstrably contradictory; record such corrections separately.
- Do not compare a warm candidate with a cold baseline or count setup output as model tokens.
- Do not reopen the rejected numeric E/R taxonomy merely to make the new trees look familiar.
