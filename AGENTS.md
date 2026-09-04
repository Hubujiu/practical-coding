# Practical Coding

This repository is an Agent Skill. Apply [`SKILL.md`](SKILL.md) when working from this checkout.

## Runtime model

1. Apply Core at execution-tree depth 0.
2. Core knows only its immediate automatic execution children: Debugging and Implementation.
3. A loaded execution node owns only its own next-level router. Do not preload siblings or descendants and do not send descendant selection back to Core.
4. Current Debugging and Implementation nodes are leaves until benchmark evidence earns a child.
5. Retrieval is a separate progressive tree. Its depth describes the unresolved information problem, not execution complexity or tool strength.
6. Host capabilities such as ranked search, graph retrieval, and output compaction are replaceable infrastructure outside both trees.
7. Automatic routing must converge toward resolving the current blocker; it must not reopen deliberation.

## Root Router

| Present unresolved blocker | Immediate child |
|---|---|
| Observed failure still lacks an evidenced cause | [`references/debugging.md`](references/debugging.md) |
| Unknown contract/invariant, coordinated guarantee, material risk boundary, or evidence requirement blocks safe execution | [`references/implementation.md`](references/implementation.md) |

A known target and settled behavior/boundary/check stay at Core even when risk nouns are present. A read-only mapping request is Core plus Retrieval.

## Manual modes

Manual modes are outside the automatic trees:

- [`references/manual/decision.md`](references/manual/decision.md) only for an explicit current request to compare options, choose a technology/architecture/dependency/API/data model, or perform decision analysis;
- [`references/manual/clarification.md`](references/manual/clarification.md) only for an explicit current request to be interviewed, grilled, questioned, or to clarify requirements before implementation.

No automatic node may route to a manual mode. Ordinary technical choices discovered during execution use the established project convention or the smallest sufficient reversible option. If a user-owned choice has no safe default, ask the minimum blocking question in the current context without opening Decision.

## Navigation and Retrieval

Navigation answers **which bounded repository area** should be searched. Load [`references/navigation.md`](references/navigation.md) only when that map is genuinely unresolved; it must return a compact topology and stop.

Retrieval answers **which concrete evidence** resolves the current claim. Load [`references/retrieval/SKILL.md`](references/retrieval/SKILL.md), then follow only the immediate child declared by the currently loaded node. The runtime root must not reproduce the complete topology from the benchmark manifest or select a distant descendant directly.

Do not route by provider name. Runtime fallback remains lossless when a ranked or graph provider is unavailable. The dependency-enabled benchmark is different: it fails closed unless every provider in [`benchmarks/capability_manifest.json`](benchmarks/capability_manifest.json) is installed and successfully pre-initialized.

## Execution output

Output compaction is a cross-cutting execution layer. A host adapter should make it transparent where command hooks exist; otherwise use the thinnest wrapper instruction available. It may reduce noisy shell, test, build, and Git output, but it must preserve semantics, exit status, failures, and material verification evidence. It is never a Retrieval or execution-tree node.

## Evolution

`evolution/` is maintainer knowledge and must not enter ordinary runtime context. The trees are experiment results, not fixed taxonomies.

Use [`benchmarks/tree_topology.json`](benchmarks/tree_topology.json), [`benchmarks/dependency_tree_validation.py`](benchmarks/dependency_tree_validation.py), [`benchmarks/retrieval_validation.py`](benchmarks/retrieval_validation.py), [`benchmarks/tree_analysis.py`](benchmarks/tree_analysis.py), and [`benchmarks/retrieval_analysis.py`](benchmarks/retrieval_analysis.py) for active dependency-enabled topology work. Cases must not encode a gold automatic node or fixed numeric execution level. Derive minimum-sufficient nodes by capability ablation, then use repeated routing ambiguity or quality failures to propose add/split/merge/promote/collapse/remove changes.

Iterations use n=1. Only a frozen candidate receives the complete n=3 baseline/no-skill comparison. Provider installation, model download, first index, dependency resolution, and first build warm-up are setup work and are never included in benchmark token, duration, or tool-call comparisons.

Preserve v1.5 and rejected experiments as historical evidence rather than rewriting them for the current topology. The execution-state/history-free proposal is retired under [`evolution/rejected/execution-state/`](evolution/rejected/execution-state/); do not restore it without a new frozen hypothesis and independent evidence.
