# Practical Coding

Practical Coding is an Agent Skill for producing the smallest reliable coding change without turning every task into a heavyweight workflow.

The active experiment uses progressive disclosure as an **evolvable local router tree** rather than a flat global router or a predefined E0-E3 ladder.

```text
Automatic execution tree

Core (depth 0)
├─ unexplained observed failure                → Debugging (depth 1, current leaf)
└─ unresolved execution contract/risk boundary → Implementation (depth 1, current leaf)

Manual modes — explicit request only
├─ Decision
└─ Clarification / grill-me

Retrieval — independent of execution depth
known target → bounded/ranked search → structural/authoritative evidence → bounded exhaustive coverage
```

## Runtime contract

Core applies to every coding task:

- define the smallest observable success;
- reuse established project primitives and contracts;
- add no speculative abstractions, dependencies, configuration, validation, tests, or documentation;
- preserve unrelated behavior and user changes;
- verify with the cheapest check that can falsify the material claim.

Core is the root node and knows only its immediate automatic children. A loaded node owns only its own next-level router. Core does not know future descendants, and a node with no benchmark-earned children explicitly declares itself a leaf.

Current automatic nodes:

- [`references/debugging.md`](references/debugging.md) — an observed failure still lacks an evidenced cause;
- [`references/implementation.md`](references/implementation.md) — safe execution is blocked by an unresolved contract, coordinated invariant, material risk boundary, or evidence requirement.

Automatic routing is convergent: it may deepen execution to resolve a blocker, but it must not reopen deliberation. If execution exposes an ordinary technical choice, use the established project convention or smallest sufficient reversible option. If a genuinely user-owned choice has no safe default, ask the minimum blocking question in the current context.

## Manual modes

Decision is no longer an automatic route.

- [`references/manual/decision.md`](references/manual/decision.md) loads only when the current user explicitly asks to compare options, select a technology/architecture/dependency/API/data model, or perform decision analysis.
- [`references/manual/clarification.md`](references/manual/clarification.md) loads only when the current user explicitly asks to be interviewed, grilled, questioned, or to clarify requirements before implementation.

Manual modes are outside the automatic capability path. No automatic node may route to Decision or Clarification. When a requested manual mode finishes, its settled result returns to Core as input.

## Retrieval policy

Retrieval remains orthogonal to the execution tree. Use the cheapest available capability that supplies enough current evidence:

1. read a known path or symbol;
2. use bounded/ranked filename, text, or symbol search;
3. use an already-available structural index for relationship questions when it materially saves exploration;
4. use bounded exhaustive coverage only for explicit exhaustive claims, and authoritative external sources only for contracts the repository cannot establish;
5. verify material conclusions against current source.

[`references/navigation.md`](references/navigation.md) is the optional detailed procedure for substantial retrieval. Codebase Memory, LSP/AST, ranked search, and ordinary search are capabilities, not required dependencies.

## Execution state

Long tasks may use a bounded current-state projection without adding a router node. [`runtime/skill_state.py`](runtime/skill_state.py) validates the coding-domain state and merge transitions. [`runtime/skill_state_host.py`](runtime/skill_state_host.py) builds and audits the exact one-current-input request needed by a true history-free host.

The host boundary freezes procedure, model, tools, options, and limits; rejects prior-response, conversation, prompt-reference, context-management, assistant, and tool-history channels; retries from the unchanged canonical state; and withholds an action until the valid successor is persisted. A validated action remains subject to the surrounding product's normal authorization policy.

A state projection used while prior messages remain attached is **state shadow**, not history-free execution. Deterministic byte limits can establish a bounded captured client request, but token, latency, and delivered-quality benefits remain pending until the four-arm model protocol in [`benchmarks/SKILL_STATE_MODEL_GATE.md`](benchmarks/SKILL_STATE_MODEL_GATE.md) is run. See [`docs/SKILL_STATE.md`](docs/SKILL_STATE.md) and [`docs/SKILL_STATE_HOST.md`](docs/SKILL_STATE_HOST.md).

## Benchmark-driven tree evolution

The benchmark does **not** validate a predefined tree. It provides evidence used to grow, split, merge, promote, collapse, or remove nodes.

The current topology lives in [`benchmarks/tree_topology.json`](benchmarks/tree_topology.json). New cases in [`benchmarks/tree_cases.py`](benchmarks/tree_cases.py) contain no expected automatic route, numeric execution level, or fixed capability path.

[`benchmarks/tree_validation.py`](benchmarks/tree_validation.py) runs each ordinary task under Core and every root-to-node capability ceiling, plus an adaptive candidate. [`benchmarks/tree_analysis.py`](benchmarks/tree_analysis.py) derives the task's **minimum-sufficient node set** from stable passing ceilings and then treats adaptive route disagreement as topology evidence rather than automatically as a model failure.

A node may change only when evidence supports the topology mutation:

- **add/deepen** when a repeatable pre-load signal exists and a child adds stable quality-qualified lift over its parent;
- **merge/move boundary** when siblings are repeatedly co-minimum-sufficient or hard to distinguish without net quality value;
- **promote/collapse** when a child is needed for most of its parent's useful scope;
- **remove** when the node has no independent minimum-sufficient or marginal-lift cases;
- **split** when a leaf has a repeated failure cluster with an observable pre-load boundary.

Depth describes disclosure depth only. It is not a fixed complexity scale, and different branches may have different depths.

## Validation

Use `n=1` while changing runtime wording, topology, cases, or scoring. Freeze the candidate before `n=3` comparison.

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -TreeSelfTest

python benchmarks/tree_validation.py --current-only --runs 1 --workers 3 `
  --output benchmark-results/tree-n1
python benchmarks/tree_analysis.py benchmark-results/tree-n1/results.jsonl `
  --output benchmark-results/tree-n1/analysis.json
```

Final frozen comparison against the v1.5 baseline and no-skill:

```powershell
python benchmarks/tree_validation.py --runs 3 --workers 3 `
  --output benchmark-results/tree-final
python benchmarks/tree_analysis.py benchmark-results/tree-final/results.jsonl `
  --output benchmark-results/tree-final/analysis.json
```

The accepted v1.5 flat Debugging/Decision/Implementation Event Router remains historical baseline evidence under [`benchmarks/results/v1.5/`](benchmarks/results/v1.5/) and [`evolution/experiments/event-router-restoration.md`](evolution/experiments/event-router-restoration.md). The rejected fixed E/R depth and specialist-leaf experiment remains under [`evolution/rejected/`](evolution/rejected/) and [`benchmarks/results/progressive-tree/`](benchmarks/results/progressive-tree/). Historical reports are not rewritten to fit the new topology.

The published `b82b38d` paired n=3 tree report is under [`benchmarks/results/evolvable-tree/`](benchmarks/results/evolvable-tree/): adaptive, frozen v1.5, and no-skill each passed 45/45 across 252/252 determinate cells, so the release quality gate passed. Adaptive still used more average tokens, time, and tool calls than frozen v1.5; the report therefore makes no cost-improvement claim.

MIT License. See `THIRD_PARTY_NOTICES.md` for attribution.
