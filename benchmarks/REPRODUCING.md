# Reproducing the v2.1 Luna benchmarks

This document reproduces Practical Coding's Codex benchmark chain. The runner invokes `gpt-5.6-luna` directly through `codex exec`; it does not use a child agent, a hidden judge model, or the user's normal Skill installation.

For the next release-quality validation cycle, read [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md) **before** running model calls. It freezes the accepted baseline, run order, no-post-hoc-change rule, external confidence-interval interpretation, held-out requirements, ablation/interference work, artifact retention, and the strongest claims each evidence layer permits. Reproduction tells you how to run the instruments; `NEXT_VALIDATION.md` defines when the resulting evidence is sufficient for a release claim.

## What is official and what is adapted

The chain deliberately separates three evidence types:

| Suite | Tasks and grader | Compared arms | Evidence status |
|---|---|---|---|
| Delivery | Ponytail's published agentic tasks, fixtures, good/bad references, and deterministic scorer | Practical, Ponytail, optional no-Skill and previous Practical | Upstream benchmark content with a Codex/Luna execution adapter |
| Router | Practical-owned exact classification corpus covering Direct, Decision, Debugging, Implementation, and Exploration | Current and previous Practical | Project regression benchmark |
| Decision | Practical-owned two-turn scenarios and mechanical contract grader | Practical and Matt Pocock `grilling`, plus optional previous Practical | Comparative benchmark; `grilling` has no declared upstream behavior benchmark |
| Debug | Ponytail `trace-transfer`/`trace-amount` plus Practical-owned shared-boundary cases; deterministic invariant and sibling-caller grading | Practical and Superpowers, plus optional previous Practical | Mixed upstream/custom comparative benchmark |
| Harness tests | Python unit tests for runner mechanics, stability gating, catalog breadth, duplicate detection, scorer seed rejection, and oracle acceptance | Runner only | Local benchmark-infrastructure regression tests |

The Decision and Debug comparisons must not be described as official Matt Pocock or Superpowers benchmark results. They are controlled Codex/Luna comparisons against those Skills' relevant behavior. Tests, TDD phases, planning prose, and workflow completeness receive no quality points; only the delivered behavior, safety invariant, build, and artifact metrics are scored.

The public Router/Decision/Debug catalog is a regression corpus. Cases that have influenced Skill wording remain useful for preventing regressions but are no longer independent evidence of generalization. See [`../docs/evaluations/2026-08-24-benchmark-landscape.md`](../docs/evaluations/2026-08-24-benchmark-landscape.md) for the held-out evidence plan.

## Pinned upstream sources

The runner verifies these exact commits before spending model calls:

| Source | Commit |
|---|---|
| `DietrichGebert/ponytail` | `2ed6c52c9d7e5e56942508591085fd45dea277d3` |
| `mattpocock/skills` | `5b15a47f2d7150f545fbcacbfe381787fc0230dc` |
| `obra/superpowers` | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` |
| `fastapi/full-stack-fastapi-template` | `cd83fc10ca20393e9ee50e3005e170c6929e047e` |

Without `-SourcesRoot`, the repositories are cloned into `%LOCALAPPDATA%\practical-coding-benchmarks\sources`. An existing source directory is accepted only when its `HEAD` equals the pinned commit.

## Prerequisites

- Windows PowerShell 7 (`pwsh`), Git, and Python 3.11 or newer.
- An installed and authenticated Codex CLI with access to `gpt-5.6-luna`.
- Network access for the first upstream clone.
- `bun` for the frontend production-build gate. Use `-NoBuilds` only for runner diagnosis; do not treat such a run as full delivery evidence.
- Enough model allowance for the selected matrix. `standard` and `full` default to three executions per cell.

Confirm the local tools:

```powershell
pwsh --version
git --version
python --version
codex --version
bun --version
```

## 1. Clone and validate the instruments

```powershell
git clone https://github.com/Hubujiu/practical-coding.git
Set-Location practical-coding
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

`-SelfTest` makes no model calls. It runs the harness/stability/catalog unit tests, verifies every profile case ID, proves the pinned Ponytail scorers reject their bad references, proves every Practical-owned Debug seed fails, and proves each expanded Debug oracle passes its deterministic scorer.

## 2. Reproduce the published v2.1 suites

The release was intentionally split into capability-specific artifacts. This makes failures easier to diagnose and prevents a large unrelated suite from obscuring the comparison being reported.

Delivery, Decision, and Debug comparator matrix (150 cells):

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

Router regression matrix (84 cells):

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite router `
  -Runs 3 `
  -RequireStableRanking
```

Native Skill discovery and on-demand routing (30 cells):

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite behavior `
  -Runs 3 `
  -RequireStableRanking
```

Focused explicit-security comparison with Superpowers (12 cells):

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite debug `
  -Case security-path-containment `
  -Case security-tenant-authorization `
  -Runs 3 `
  -RequireStableRanking
```

Published aggregate values are committed in [`results/v2.1/summary.json`](results/v2.1/summary.json), with navigation results in [`results/v2.1/navigation.json`](results/v2.1/navigation.json). Raw transcripts and generated workspaces are deliberately not committed because they are large and can contain environment-specific paths.

## 3. Run a complete profile

To run all suites together:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3
```

The current public `standard` profile runs 264 isolated cells when no previous-version or no-Skill arm is requested:

- 9 Delivery cases × 2 arms × 3 runs = 54;
- 28 Router cases × 1 arm × 3 runs = 84;
- 6 Decision cases × 2 arms × 3 runs = 36;
- 10 Debug cases × 2 arms × 3 runs = 60;
- 10 native-behavior cases × 1 arm × 3 runs = 30.

For the complete public matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3
```

`full` runs 366 cells without a previous-version or no-Skill arm:

- 18 Delivery cases × 2 arms × 3 runs = 108;
- 28 Router cases × 1 arm × 3 runs = 84;
- 10 Decision cases × 2 arms × 3 runs = 60;
- 14 Debug cases × 2 arms × 3 runs = 84;
- 10 native-behavior cases × 1 arm × 3 runs = 30.

The `smoke` profile intentionally remains small and defaults to one repetition. It is for harness/model sanity only.

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

pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Suite debug `
  -Case trace-cache-tenant `
  -Runs 3
```

Use `-FailOnCellFailure` only when every selected cell is expected to pass. A comparison run normally returns success when the infrastructure completed, even when it correctly exposes a behavioral failure in one arm.

## 6. Reproduce Navigation evidence

Navigation is a repository-specific paired ablation. Substitute a real tracked checkout and an independently checkable answer oracle:

```powershell
python benchmarks/navigation_ablation.py `
  --repository D:\path\to\large-project `
  --prompt "Map the complete production call chain for the named boundary." `
  --required "ExpectedController.java" `
  --required "ExpectedRepository.java" `
  --runs 3 `
  --output benchmark-results\navigation-large-n3
```

Publish the repository commit, tracked file/byte counts, prompt, required evidence, and both cold and warm graph observations. The v2.1 results do not establish a universal file-count threshold: graph navigation lost clearly on the 496-file repository and was promising but still provisional on the 1,385-file repository.

## 7. Inspect and rescore results

Each run is stored under `benchmark-results/<timestamp>/`:

```text
manifest.json             environment, model, source commits, Skill hashes
results.json              complete per-cell records
summary.json              per-case rates, median, mean, standard deviation
comparisons.json          per-case Practical-minus-comparator deltas
rollups.json              suite/arm aggregate results
rollup-comparisons.json   suite-level deltas
scorecards.json           quality gates, Pareto status, relative efficiency
report.md                 human-readable report
cells/                    prompts, JSONL transcripts, stderr, answers, workspaces
```

Mechanical grading can be updated without another model call:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Rescore D:\path\to\benchmark-results\20260824-204244
```

The rescore timestamp and current runner hash are written to the manifest. Raw run directories are intentionally ignored by Git because they contain large generated workspaces and transcripts.

## Published v2.1 result summary

The release matrix used Windows 11, Codex CLI, `gpt-5.6-luna`, reasoning `medium`, isolated workspaces, three repetitions per cell, and the pinned comparator commits above.

| Suite | Practical | Comparator | Qualified interpretation |
|---|---:|---:|---|
| Delivery, 27 cells | 96.3% | Ponytail 100% | Quality gate failed by one build; Practical used fewer tokens/time, while Ponytail produced less code |
| Decision, 18 cells | 100% | grilling 94.4% | Quality-qualified trade-off; Practical used more uncached input but less output/time |
| Debug, 30 cells | 90.0% | Superpowers 83.3% | Practical dominates; relative efficiency 2.311 and diagnostic utility 2.691 |
| Explicit security, 12 cells | 100% safe | Superpowers 100% safe | Equal observed correctness/safety; Practical relative efficiency 2.323 |
| Router, 84 cells | 95.238% | — | Two route misses; project-owned regression evidence |
| Native behavior, 30 cells | 96.667% | — | One behavior miss; verifies real discovery and selective reference loading |

The formulas, exact medians, limitations, and machine-readable values are in [`results/v2.1/`](results/v2.1/). Older iteration reports remain under [`../docs/evaluations/`](../docs/evaluations/) and must not be relabeled as v2.1 results.

## Reproducibility limits

- Luna sampling is nondeterministic; use at least three runs and inspect standard deviation rather than treating one sample as a ranking.
- Concurrent cells share the Codex service and package caches, so suite wall time is not the sum of cell durations. Build duration and model duration are recorded separately.
- `input_tokens` already includes cached input. Compare `uncached_input_tokens`, `output_tokens`, and reasoning tokens separately when discussing cost.
- A successful Ponytail-derived Delivery score proves the reused deterministic contract, not equivalence with Ponytail's original Claude runtime.
- The runner disables normal user Skills, plugins, apps, memories, and multi-agent behavior, then embeds exactly one selected Skill arm. This isolates the comparison but differs from a user's fully configured interactive session.
- The public Practical-owned cases are visible regression tests. Do not use their saturation as proof of unseen-task generalization.
- Do not combine specialist suites into a universal leaderboard. Run the current standard/full matrix and an independent external or held-out suite after material prompt changes.
