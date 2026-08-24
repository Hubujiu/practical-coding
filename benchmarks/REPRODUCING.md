# Reproducing the Luna benchmarks

This document reproduces Practical Coding's Codex benchmark chain. The runner invokes `gpt-5.6-luna` directly through `codex exec`; it does not use a child agent, a hidden judge model, or the user's normal Skill installation.

## What is official and what is adapted

The chain deliberately separates three evidence types:

| Suite | Tasks and grader | Compared arms | Evidence status |
|---|---|---|---|
| Delivery | Ponytail's published agentic tasks, fixtures, good/bad references, and deterministic scorer | Practical, Ponytail, optional no-Skill and previous Practical | Upstream benchmark content with a Codex/Luna execution adapter |
| Router | Practical-owned exact classification corpus covering Direct, Decision, Debugging, Implementation, Exploration, and Verification | Current and previous Practical | Project regression benchmark |
| Decision | Practical-owned two-turn scenarios and mechanical contract grader | Practical and Matt Pocock `grilling`, plus optional previous Practical | Comparative benchmark; `grilling` has no declared upstream behavior benchmark |
| Debug | Ponytail `trace-transfer`/`trace-amount` plus Practical-owned shared-boundary cases; deterministic invariant and sibling-caller grading | Practical and Superpowers, plus optional previous Practical | Mixed upstream/custom comparative benchmark |
| Harness tests | Six Python tests for question/recommendation counting, delta direction, fixed Luna configuration, route coverage, and Decision-module injection | Runner only | Local benchmark-infrastructure regression tests |

The Decision and Debug comparisons must not be described as official Matt Pocock or Superpowers benchmark results. They are controlled Codex/Luna comparisons against those Skills' relevant behavior. Tests, TDD phases, planning prose, and workflow completeness receive no quality points; only the delivered behavior, safety invariant, build, and artifact metrics are scored.

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

`-SelfTest` makes no model calls. It runs the six harness regression tests, verifies every profile case ID, then proves that the Ponytail and custom scorers accept their good fixtures and reject their bad fixtures.

## 2. Run the standard comparison

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Runs 3 `
  -Workers 3
```

This runs 150 isolated cells when no previous-version or no-Skill arm is requested:

- 9 Delivery cases × 2 arms × 3 runs;
- 16 Router cases × 1 arm × 3 runs;
- 4 Decision cases × 2 arms × 3 runs;
- 4 Debug cases × 2 arms × 3 runs.

For the expanded 18-case Ponytail delivery matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3
```

## 3. Run a before/after candidate gate

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

## 4. Run a focused regression

Selectors are repeatable:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile standard `
  -Suite router `
  -Runs 3 `
  -BaselineRef HEAD

pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile smoke `
  -Suite decision `
  -Case service-boundary `
  -Runs 3
```

Use `-FailOnCellFailure` only when every selected cell is expected to pass. A comparison run normally returns success when the infrastructure completed, even when it correctly exposes a behavioral failure in one arm.

## 5. Inspect and rescore results

Each run is stored under `benchmark-results/<timestamp>/`:

```text
manifest.json             environment, model, source commits, Skill hashes
results.json              complete per-cell records
summary.json              per-case rates, median, mean, standard deviation
comparisons.json          per-case Practical-minus-comparator deltas
rollups.json              suite/arm aggregate results
rollup-comparisons.json   suite-level deltas
report.md                 human-readable report
cells/                    prompts, JSONL transcripts, stderr, answers, workspaces
```

Mechanical grading can be updated without another model call:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Rescore D:\path\to\benchmark-results\20260824-204244
```

The rescore timestamp and current runner hash are written to the manifest. Raw run directories are intentionally ignored by Git because they contain large generated workspaces and transcripts.

## Published v1.11 calibration

The following results were produced on Windows 11 with Python 3.13.14, Codex CLI 0.145.0, `gpt-5.6-luna`, reasoning `medium`, and three parallel workers. They are calibration results, not claims about every repository or model.

| Matrix | Practical v1.11 | Frozen v1.10 | Comparator | Main difference |
|---|---:|---:|---:|---|
| Router, 16 cases × n=3 | 48/48 | 48/48 | — | Both arms reached the current harness ceiling; the new negative rules caused no regression but did not prove a gain |
| Debug, 4 cases × n=3 | 12/12 | 12/12 | Superpowers 10/12 | Superpowers twice repaired only the named caller and missed the sibling/shared invariant |
| Decision, 4 cases × n=3 | 12/12 | 12/12 | grilling 10/12 | Both Practical versions converged after the scripted reply; grilling reopened `api-migration` twice |
| Delivery, 6 differentiating cases × n=1 | 5/6 | 5/6 | Ponytail 5/6 | All arms scored 6/6 correct/safe; production builds separated the pass rate and remain unstable at `n=1` |

For Debug, suite median time was 39.1 seconds for v1.11, 44.5 seconds for v1.10, and 78.8 seconds for Superpowers; median total tokens were 80,940, 88,053, and 245,966 respectively. These secondary efficiency metrics matter only after correctness and safety. Delivery total LOC at `n=1` was 376 for v1.11, 363 for v1.10, and 343 for Ponytail, so the current data does **not** support a claim that v1.11 matches Ponytail's compactness.

The published comparison used `-BaselineSkill docs/evaluations/snapshots/practical-v1.10`, not commit `75d5013`. See [`../docs/evaluations/2026-08-24-practical-v111-iteration.md`](../docs/evaluations/2026-08-24-practical-v111-iteration.md) for the complete per-case tables and acceptance decisions.

## Reproducibility limits

- Luna sampling is nondeterministic; use at least three runs and inspect standard deviation rather than treating one sample as a ranking.
- Concurrent cells share the Codex service and package caches, so suite wall time is not the sum of cell durations. Build duration and model duration are recorded separately.
- `input_tokens` already includes cached input. Compare `uncached_input_tokens`, `output_tokens`, and reasoning tokens separately when discussing cost.
- A successful Ponytail-derived Delivery score proves the reused deterministic contract, not equivalence with Ponytail's original Claude runtime.
- The runner disables normal user Skills, plugins, apps, memories, and multi-agent behavior, then embeds exactly one selected Skill arm. This isolates the comparison but differs from a user's fully configured interactive session.
- Do not generalize the focused v1.11 calibration rows into a whole-Skill ranking. Run the standard or full matrix after each material prompt change.
