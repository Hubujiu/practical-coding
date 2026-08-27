# Reproducing the Practical Coding v1.0 Luna benchmarks

This document reproduces the public Practical Coding v1.0 benchmark chain. The runner invokes `gpt-5.6-luna` directly through `codex exec`, uses isolated workspaces, and records deterministic evidence where possible.

Published compact aggregates are in [`results/v1.0/`](results/v1.0/). The release interpretation is in [`../docs/evaluations/2026-08-26-practical-v1-release.md`](../docs/evaluations/2026-08-26-practical-v1-release.md).

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

- PowerShell 7 (`pwsh`), Git, Python 3.11+;
- installed/authenticated Codex CLI with access to `gpt-5.6-luna`;
- network access for the first upstream clone;
- `bun` for frontend production-build gates.

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

## 2. Reproduce the published v1.0 capability suites

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

Router:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite router `
  -Runs 3 `
  -RequireStableRanking
```

Native Skill discovery / selective loading:

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

Published aggregate values are committed in [`results/v1.0/summary.json`](results/v1.0/summary.json), with navigation evidence in [`results/v1.0/navigation.json`](results/v1.0/navigation.json).

## 3. Complete public matrix

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3 -RequireStableRanking
```

The `smoke` profile defaults to one repetition and is only a harness/model sanity check. Do not publish `n=1` as a stable ranking.

## 4. Candidate before/after gate

While changing Skill behavior, compare the candidate against the immediately preceding accepted commit:

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

## 5. Navigation ablation

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

## 6. Evidence boundary

The v1.0 data support role-specific statements such as:

- Practical was materially more efficient than Superpowers on the tested Debug/Security matrices after passing the quality gate;
- Ponytail retained the Delivery build/LOC advantage on the tested matrix;
- Practical's native routing usually kept irrelevant references unloaded.

They do **not** support:

- a universal ranking across every coding task/model/repository;
- a claim that Practical is already experimentally better than **Ponytail + Superpowers installed together**;
- a universal graph-navigation size threshold.

The exact combined-install comparison is a required arm in [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md).

## 7. Reproducibility note about the public v1.0 label

The committed aggregate files preserve the exact tested bundle hash. Public version naming was normalized to **v1.0** without changing the routing/reference behavior represented by the published release evaluation. Treat the recorded bundle hash and pinned comparator commits as the authoritative identity of the measured run.
