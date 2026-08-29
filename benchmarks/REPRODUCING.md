# Reproducing the Practical Coding v1.3 adaptive-rigor benchmarks

This document reproduces the **v1.3 candidate** benchmark chain. The canonical runner is v2.1: `run_benchmarks.py` remains the stable v2.0 execution core, while `case_catalog.py` installs the public corpus and `adaptive_rigor.py` installs the v1.3 control contract before execution.

The last committed validated evidence is v1.2 under [`results/v1.2/`](results/v1.2/). [`results/v1.1/`](results/v1.1/) and [`results/v1.0/`](results/v1.0/) are also retained as historical evidence. Do not interpret their Router scores as v1.3 adaptive-rigor scores.

## Evidence types

| Suite | Tasks / grader | Compared arms | Evidence status |
|---|---|---|---|
| Delivery | Ponytail's published agentic tasks and deterministic scorer through a Codex adapter | Practical, Ponytail | Upstream task content with project execution adapter |
| Adaptive rigor (`router` suite id) | Practical-owned Decision / Execution / Retrieval-bound corpus | Practical | Public project regression corpus |
| Decision | Practical-owned two-turn scenarios and mechanical contract grader | Practical, Matt Pocock `grilling` | Controlled comparative benchmark |
| Debug | Upstream and Practical-owned shared-boundary cases with deterministic invariant grading | Practical, Superpowers | Controlled comparative benchmark |
| Native behavior | Native Skill installation/discovery traces and transition cases | Practical | Integration regression evidence |
| Navigation | Real-repository paired source-vs-graph ablation | Source, optional Codebase Memory graph | Repository-specific evidence |

Decision/Debug results must not be described as official upstream benchmark results. The benchmark scores delivered behavior and safety; it does not award points merely for following a named planning or TDD process.

## v1.3 state contract

The canonical classifier returns:

```text
DECISION=<CLEAR|REQUIRED>;
EXECUTION=<BLOCKED|DIRECT|DEBUGGING|IMPLEMENTATION>;
RETRIEVAL=<NONE|TARGETED|BOUNDED|STRUCTURAL>
```

with this state invariant:

```text
DECISION=REQUIRED  => EXECUTION=BLOCKED
DECISION=CLEAR     => EXECUTION in DIRECT | DEBUGGING | IMPLEMENTATION
```

Retrieval is graded against a case-specific interval rather than one unique exact label:

```text
retrieval_min <= actual_retrieval <= retrieval_max
```

The order is `NONE < TARGETED < BOUNDED < STRUCTURAL`. Falling below the minimum is insufficient context; exceeding the maximum is unnecessary retrieval cost.

## Pinned upstream sources

| Source | Commit |
|---|---|
| `DietrichGebert/ponytail` | `2ed6c52c9d7e5e56942508591085fd45dea277d3` |
| `mattpocock/skills` | `5b15a47f2d7150f545fbcacbfe381787fc0230dc` |
| `obra/superpowers` | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` |
| `fastapi/full-stack-fastapi-template` | `cd83fc10ca20393e9ee50e3005e170c6929e047e` |

## Prerequisites

- Windows PowerShell 7 (`pwsh`), Git, and Python 3.11 or newer.
- An installed and authenticated Codex CLI with access to `gpt-5.6-luna`.
- Network access for the first upstream clone.
- `bun` for the frontend production-build gate. Use `-NoBuilds` only for runner diagnosis; do not treat such a run as full delivery evidence.
- Enough model allowance for the selected matrix. `standard` and `full` default to three executions per cell.

For each frontend template cell, the runner executes `bun install --frozen-lockfile` before the agent starts and keeps that `node_modules` tree for the runner-owned production build. Setup duration is recorded separately from model duration.

Confirm the local tools:

```powershell
pwsh --version
git --version
python --version
codex --version
bun --version
```

## 1. Clone, select the candidate, and self-test

For the v1.3 candidate branch:

```powershell
git clone https://github.com/Hubujiu/practical-coding.git
Set-Location practical-coding
git switch adaptive-rigor-v1.3
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

The self-test makes no model calls. It validates the harness, profiles, source pins, seed failures, oracle passes, adaptive-rigor schema, transition catalog, and scorer mechanics.

`benchmarks/run.ps1` invokes `run_catalog.py`; do not invoke `run_benchmarks.py` directly for v1.3 evaluation because the latter intentionally remains the v2.0 core contract.

## 2. Run the specialist capability suites

Delivery + Decision + Debug:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite delivery `
  -Suite decision `
  -Suite debug `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

These task/scorer surfaces can be compared with v1.2 where the underlying case contract is unchanged.

## 3. Run the adaptive-rigor matrix

The standard/full canonical profile currently contains **42 adaptive-rigor cases**. At three repetitions and one current arm this is **126 cells**:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite router `
  -Runs 3 `
  -RequireStableRanking
```

The suite id remains `router` for CLI compatibility only. It now scores:

- Decision Gate correctness;
- current execution rigor;
- state validity;
- Retrieval sufficiency;
- Retrieval efficiency relative to the declared maximum.

The four explicit transition cases are:

```text
transition-decision-to-direct
transition-decision-to-implementation
transition-debug-to-direct
transition-debug-to-implementation
```

A focused transition run:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Suite router `
  -Case transition-decision-to-direct `
  -Case transition-decision-to-implementation `
  -Case transition-debug-to-direct `
  -Case transition-debug-to-implementation `
  -Runs 3 `
  -RequireStableRanking
```

## 4. Run Native Behavior

The canonical standard/full profile contains **22 native-behavior cases**, or **66 cells** at three repetitions:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite behavior `
  -Runs 3 `
  -RequireStableRanking
```

Native Behavior validates real Skill discovery without prompt injection, selective reference loading, structural Retrieval/backend behavior, and the new transition boundaries. In particular, settled decisions and already-diagnosed bugs should not reload obsolete Decision/Debugging references.

## 5. Complete public matrices

`standard` without previous/no-Skill arms contains 342 cells:

- 9 Delivery × 2 arms × 3 = 54;
- 42 adaptive-rigor × 1 arm × 3 = 126;
- 6 Decision × 2 arms × 3 = 36;
- 10 Debug × 2 arms × 3 = 60;
- 22 Native Behavior × 1 arm × 3 = 66.

Run:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3 -RequireStableRanking
```

`full` without previous/no-Skill arms contains 444 cells:

- 18 Delivery × 2 arms × 3 = 108;
- 42 adaptive-rigor × 1 arm × 3 = 126;
- 10 Decision × 2 arms × 3 = 60;
- 14 Debug × 2 arms × 3 = 84;
- 22 Native Behavior × 1 arm × 3 = 66.

Run:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3 -RequireStableRanking
```

The `smoke` profile intentionally remains small and defaults to one repetition. It is for harness/model sanity only. Do not publish `n=1` as a stable ranking.

## 6. Run the v1.3 vs accepted-v1.2 candidate gate

Use the accepted v1.2 baseline commit explicitly:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef 88382d2b0c00fa278067a5933bbcacc86f46b56e `
  -IncludeBaseline `
  -RequireStableRanking
```

The materialized baseline Skill is copied into the run directory. Entry-point and complete Skill-bundle hashes are recorded in `manifest.json`.

Do **not** compare v1.2 Router accuracy numerically with v1.3 adaptive-rigor accuracy: the classification schemas differ. Use unchanged Delivery/Decision/Debug task contracts for before/after performance claims, and use transition/reference-loading results to validate the new control architecture.

## 7. Focused explicit-security comparison

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite debug `
  -Case security-path-containment `
  -Case security-tenant-authorization `
  -Runs 3 `
  -RequireStableRanking
```

## 8. Combined-install matrix

For the required integrated-stack comparison:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -ComboMatrix `
  -RequireStableRanking
```

Interpret this through the claim boundaries in [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md). The existence of a combo result does not by itself establish universal superiority.

## 9. Navigation ablation

```powershell
python benchmarks/navigation_ablation.py `
  --repository D:\path\to\large-project `
  --prompt "Map the complete production call chain for the named boundary." `
  --required "ExpectedController.java" `
  --required "ExpectedRepository.java" `
  --runs 3 `
  --output benchmark-results\navigation-large-n3
```

Publish repository commit, tracked files/bytes, the task oracle, and cold/warm graph observations. Current evidence does not establish a universal file-count threshold where graph navigation always wins.

## 10. Evidence boundary

The committed v1.2 baseline supports statements such as:

- reasoning classification passed 114/114 cells under the v1.2 exact schema;
- Retrieval exact classification passed 106/114;
- Native Behavior passed 54/54;
- the Practical-only Delivery/Decision/Debug regression passed 75/75.

It does **not** validate the v1.3 adaptive-rigor classifier or its Retrieval intervals.

Likewise, a future public v1.3 regression does not by itself support:

- a universal ranking across every coding task/model/repository;
- a claim that Practical is experimentally better than Ponytail + Superpowers installed together unless that combined arm is measured;
- a universal graph-navigation size threshold;
- broad generalization beyond the public regression corpus without held-out evidence.

## 11. Reproducibility identity

The authoritative identity of a run is the manifest, not a marketing version label. Preserve:

- candidate commit;
- previous baseline commit when applicable;
- canonical runner version and bundle SHA;
- Skill entrypoint and complete bundle SHA;
- model/reasoning setting;
- pinned comparator commits;
- profile/case list and repetition count.

Historical v1.0/v1.1/v1.2 aggregate files keep their original identities and should not be rewritten to look like v1.3 results.
