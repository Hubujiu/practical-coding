# Practical Coding benchmark chain

The active experiment uses two independent evolvable trees:

- the automatic execution tree starts at Core and currently exposes Debugging and Implementation leaves;
- the Retrieval tree progresses from R0 Direct Locate through R1 Ranked Discovery and R2 Evidence Expansion to the R3 Structural Trace leaf.

Decision and requirements interviewing are explicit-only manual modes. Ranked search, graph retrieval, and execution-output compaction are providers outside both trees.

The accepted v1.5 flat Event Router and rejected fixed E/R ladder remain historical baselines. Do not use their fixed labels, numeric depths, or gold routes as the acceptance oracle for this experiment.

## Active questions

1. Does the candidate deliver a correct, safe, evidence-backed result at least as reliably as the v1.5 baseline and no-skill arm?
2. Which automatic execution nodes are minimum-sufficient under parent-versus-child ceilings?
3. Does adaptive execution disclosure stop without spontaneous manual Decision or Clarification activation?
4. Does Retrieval start at R0 and escalate only through the current node's immediate child?
5. Does each Retrieval stage stop at the minimum current-source evidence required by the task?
6. With the required provider surface held constant, does the candidate improve quality or measured context cost?
7. Do repeated failures or boundary ambiguity justify growing, splitting, merging, promoting, collapsing, moving, or removing a node?

## Runtime topology

- `tree_topology.json` — execution nodes, manual modes, Retrieval nodes and edges, trace modes, dependency profile, and frozen baseline ref;
- `tree_cases.py` — topology-neutral real-repository tasks with no expected automatic execution route;
- `tree_validation.py` — underlying quality/scoring runner and historical-compatible execution trace parser;
- `dependency_tree_validation.py` — required active execution-tree runner that injects fail-closed provider setup before every measured turn;
- `retrieval_trace.py` — canonical R0–R3 parser plus observed Retrieval-reference extraction;
- `retrieval_validation.py` — independent Retrieval-stage ceiling runner;
- `retrieval_analysis.py` — minimum-sufficient Retrieval-depth and provider-use analysis;
- `tree_analysis.py` — minimum-sufficient execution-node and topology-change analysis;
- `TREE_EVOLUTION.md` — interpretation and mutation rules.

`tree_validation.py` remains directly runnable for historical reproduction and deterministic topology self-tests. Provider-enabled cost claims must use `dependency_tree_validation.py`.

## Required capability profile

`capability_manifest.json` declares the exact environment:

| Role | Required executable | Purpose |
|---|---|---|
| ranked retrieval | `zg` | R1 candidate discovery and bounded R2 support |
| graph retrieval | `codebase-memory-mcp` | R3 relationship tracing |
| execution output | `rtk` | compact noisy shell/test/build/Git evidence |
| repository warm-up | `node`/`npm`, `java`/`mvn` where declared | dependency and first-build parity |

The active runner has no allow-missing mode. It resolves and probes every required executable before model cells are created. A provider setup or repository warm-up failure aborts the run rather than silently switching capability surfaces.

## Measurement contract

Every cell has an auditable setup receipt at:

```text
cells/<task>/<variant>/rNNN/capability-setup.json
```

The setup phase includes:

- provider probes and local runtime/model initialization;
- workspace `zg` indexing;
- a per-workspace Codebase Memory graph in one explicit shared daemon/cache cohort;
- `rtk` command-path verification;
- repository-specific dependency resolution and first test/build warm-up;
- post-setup clean-tree validation.

Setup is marked `included_in_comparison: false`. It occurs before `run_codex`, produces no token estimate, and is absent from the `results.jsonl` measured usage fields. Only the later Codex transcript contributes input/output tokens, tool calls, and measured duration.

All paired arms receive the same initialized providers and repository warm-up. A baseline may choose not to use a provider, but it may not receive a colder environment.

The runner rejects reuse of a measured result without a matching setup receipt. It also marks measured provider installation/indexing commands as contract violations, including `zg index`, Codebase Memory indexing, `rtk init`, and package installation.

## Retrieval trace contract

The dependency runner emits only canonical modes:

```text
NONE
R0_DIRECT
R1_DISCOVERY
R2_EVIDENCE
R3_STRUCTURAL
```

A trace that reports a stage must list the actually loaded Retrieval references as a complete root-to-stage prefix. For example, `R2_EVIDENCE` requires:

```text
references/retrieval/SKILL.md
references/retrieval/direct.md
references/retrieval/discovery.md
references/retrieval/evidence.md
```

Legacy `TARGETED`, `BOUNDED`, and `STRUCTURAL` values remain parser-compatible only so historical result files can still be read. The active dependency runner does not emit them.

`NONE` means no Retrieval policy reference was loaded; repository-native exact reads remain available as the no-tree control. `R0_DIRECT` begins by loading the Retrieval root followed by `direct.md`.

For active arms, the declared Retrieval prefix must exactly match Retrieval reference paths observed in command execution. A self-reported stage cannot stand in for an unread node, and a hidden deeper read is a trace failure.

## Deterministic validation

These checks do not claim that external providers are installed; they validate topology, fail-closed preflight, setup separation and shared-cohort handling, receipt structure, and measurement boundaries with controlled shims:

```powershell
python benchmarks/dependency_tree_validation.py --self-test
python benchmarks/retrieval_validation.py --self-test
python benchmarks/retrieval_analysis.py /dev/null --self-test
python -m unittest `
  benchmarks.test_tree_benchmarks `
  benchmarks.test_capability_environment `
  benchmarks.test_dependency_tree_validation `
  benchmarks.test_retrieval_analysis
```

CI runs these deterministic checks. The full model benchmark is intentionally not disguised as a unit test.

## Model-backed iteration

Install and verify the frozen dependency profile first. Exact accepted provider versions live in `capability_manifest.json`; preflight rejects a different provider version instead of mixing it into an older result set:

```powershell
zg --version
codebase-memory-mcp --version
rtk --version
git --version
node --version
npm --version
java -version
mvn --version
```

Use `n=1` while changing topology, node content, provider contracts, cases, or scoring:

```powershell
python benchmarks/retrieval_validation.py --current-only --runs 1 --workers 3 `
  --output benchmark-results/retrieval-tree-n1
python benchmarks/retrieval_analysis.py benchmark-results/retrieval-tree-n1/results.jsonl `
  --output benchmark-results/retrieval-tree-n1/analysis.json
```

Only after freezing the candidate should it run `n=3` with baseline and no-skill arms:

```powershell
python benchmarks/retrieval_validation.py --runs 3 --workers 3 `
  --output benchmark-results/retrieval-tree-final
python benchmarks/retrieval_analysis.py benchmark-results/retrieval-tree-final/results.jsonl `
  --output benchmark-results/retrieval-tree-final/analysis.json
```

## Interpretation

Delivered quality gates the candidate. Exact historical route labels do not.

For each non-manual task, the execution-tree runner exposes Core and every root-to-node capability ceiling. The analyzer marks stable passing ceilings, removes qualified descendants whose ancestor already passes, and reports the remaining set as the task's minimum-sufficient set. More than one minimum node is allowed.

Adaptive execution traces are reported as:

- `exact_minimum` — stopped on a derived minimum node;
- `over_disclosure` — went deeper than a sufficient ancestor;
- `under_disclosure` — stopped above a node needed by ceiling evidence;
- `alternate_branch` — selected a different branch;
- `quality_gap` — no current node ceiling solves the task reliably.

Retrieval disclosure is analyzed separately through canonical stage traces, loaded-reference prefixes, provider-use counts, quality, and measured cost. A provider can be present without being used; presence is held constant, while stage and provider selection remain behavior under test.

Manual modes retain a separate contract: ordinary tasks must have zero spontaneous manual activation; explicit requests must load the corresponding `references/manual/` mode.

## Historical baselines

- `progressive_validation.py`, `progressive_cases.py`, and `ladder_analysis.py` reproduce previous fixed E/R and flat Event Router experiments.
- `results/progressive-tree/` and `../evolution/rejected/` preserve rejected fixed-depth evidence.
- `results/v1.5/` preserves the accepted flat-router evidence frozen by `tree_topology.json`.
- `../evolution/rejected/execution-state/` preserves the retired execution-state/history-free experiment.

Do not rewrite historical contracts to make the current tree appear better. New topology or capability-policy claims require a frozen candidate, appropriate ablation, identical provider setup across arms, and real-repository evidence.
