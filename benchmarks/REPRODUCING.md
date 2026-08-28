# Reproducing the Practical Coding v1.1 Luna benchmarks

This document reproduces the public Practical Coding v1.1 benchmark chain. The runner invokes `gpt-5.6-luna` directly through `codex exec`, uses isolated workspaces, and records deterministic evidence where possible.

Published compact aggregates and the full Chinese report are in [`results/v1.1/`](results/v1.1/). Historical v1.0 evidence remains in [`results/v1.0/`](results/v1.0/).

## Evidence types

| Suite | Tasks / grader | Compared arms | Evidence status |
|---|---|---|---|
| Delivery | Ponytail's published agentic tasks and deterministic scorer through a Codex adapter | Practical, Ponytail | Upstream task content with project execution adapter |
| Router | Practical-owned exact routing corpus | Practical | Public project regression corpus |
| Decision | Practical-owned two-turn scenarios and mechanical contract grader | Practical, Matt Pocock `grilling` | Controlled comparative benchmark |
| Debug | Upstream and Practical-owned shared-boundary cases with deterministic invariant grading | Practical, Superpowers | Controlled comparative benchmark |
| Native behavior | Native Skill installation/discovery traces | Practical | Integration regression evidence |
| Navigation | Real-repository paired source-vs-graph ablation | Source, optional Codebase Memory graph | Repository-specific evidence |

Decision/Debug results must not be described as official upstream benchmark results. The benchmark scores delivered behavior and safety; it does not award points merely for following a particular planning or TDD process.

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

For each frontend template cell, the runner executes `bun install --frozen-lockfile` before the agent starts and keeps that `node_modules` tree for the runner-owned production build. This makes compile/type/build checks available to the agent without changing dependency declarations; setup duration is recorded separately from model duration.

Confirm the local tools:

```powershell
pwsh --version
git --version
python --version
codex --version
bun --version
```

## 1. Clone and self-test

```powershell
git clone https://github.com/Hubujiu/practical-coding.git
Set-Location practical-coding
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

The self-test makes no model calls. It validates the harness, profiles, source pins, seed failures, oracle passes, and scorer mechanics.

## 2. Reproduce the published v1.1 capability suites

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

Router regression matrix (114 cells):

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite router `
  -Runs 3 `
  -RequireStableRanking
```

Native Skill discovery and on-demand routing (54 cells):

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite behavior `
  -Runs 3 `
  -RequireStableRanking
```

Focused explicit-security comparison:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite debug `
  -Case security-path-containment `
  -Case security-tenant-authorization `
  -Runs 3 `
  -RequireStableRanking
```

Published v1.1 aggregates are split by affected surface in [`results/v1.1/`](results/v1.1/). Delivery/Decision and Router/Behavior used runner v1.8; the final Debug rerun and current harness use v1.9. The report does not present those split runs as one atomic manifest.

## 3. Complete public matrix

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3 -RequireStableRanking
```

The current public `standard` profile runs 318 isolated cells when no previous-version or no-Skill arm is requested:

- 9 Delivery cases × 2 arms × 3 runs = 54;
- 38 Router cases × 1 arm × 3 runs = 114;
- 6 Decision cases × 2 arms × 3 runs = 36;
- 10 Debug cases × 2 arms × 3 runs = 60;
- 18 native-behavior cases × 1 arm × 3 runs = 54.

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3
```

`full` runs 420 cells without a previous-version or no-Skill arm:

- 18 Delivery cases × 2 arms × 3 runs = 108;
- 38 Router cases × 1 arm × 3 runs = 114;
- 10 Decision cases × 2 arms × 3 runs = 60;
- 14 Debug cases × 2 arms × 3 runs = 84;
- 18 native-behavior cases × 1 arm × 3 runs = 54.

The `smoke` profile intentionally remains small and defaults to one repetition. It is for harness/model sanity only.
Do not publish `n=1` as a stable ranking.

## 4. Run a before/after candidate gate

While editing a dirty candidate, compare it with the checked-in version:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef HEAD
```

After a candidate has already been committed, use the actual previous revision or release tag instead, for example:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Runs 3 `
  -BaselineRef 75d501380bc4c9c26de8b81f8e4fc320717b0141
```

The materialized baseline Skill is copied into the run directory. Both entrypoint and complete Skill-bundle hashes are recorded in `manifest.json`, preventing an ambiguous "previous version" comparison.

For a comparison that will be published as a stable ranking, add `-RequireStableRanking`. It rejects effective `n<3`, incomplete runs, infrastructure failures, and Delivery rankings without production-build evidence. For release claims, also follow the stricter current/previous/no-Skill and claim-boundary requirements in [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md).

## 5. Run a focused regression

Selectors are repeatable:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite router `
  -Runs 3 `
  -BaselineRef HEAD
```

For a stable full candidate/baseline comparison:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef <accepted-previous-commit> `
  -IncludeBaseline `
  -RequireStableRanking
```

The run manifest records the materialized Skill bundle and hashes so the baseline is explicit.

## 6. Navigation ablation

```powershell
python benchmarks/navigation_ablation.py `
  --repository D:\path\to\large-project `
  --prompt "Map the complete production call chain for the named boundary." `
  --required "ExpectedController.java" `
  --required "ExpectedRepository.java" `
  --runs 3 `
  --output benchmark-results\navigation-large-n3
```

Publish repository commit, tracked files/bytes, the task oracle, and cold/warm graph observations. The current evidence does not establish a universal file-count threshold where graph navigation always wins.

## 7. Evidence boundary

The v1.1 data support role-specific statements such as:

- current Practical passed 242 of 243 applicable cells across the split affected-surface reruns;
- Delivery, Decision, Router, and Native Behavior were perfect in those reruns;
- Debug correctness was perfect, while safety was 29/30 because one run missed a sibling caller;
- the older 15-arm combo matrix remains useful interference evidence, but its comparator rows are cross-run rather than a new v1.9 paired scorecard.

They do **not** support:

- a universal ranking across every coding task/model/repository;
- a claim that Practical is already experimentally better than **Ponytail + Superpowers installed together**;
- a universal graph-navigation size threshold.

The exact combined-install comparison is a required arm in [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md).

## 8. Reproducibility note about the public v1.1 label

The committed aggregate files preserve the exact tested bundle hashes and runner versions. The v1.1 release metadata bump happened after the behavioral runs; the tested Skill text is otherwise the released routing/reference behavior. Treat the recorded hashes, runner versions, and pinned comparator commits as the authoritative identities of the measured runs.
