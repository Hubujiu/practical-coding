# Practical Coding benchmark chain

This directory contains the reproducible evaluation harness for the public **Practical Coding v1.0** release.

The benchmark design intentionally avoids a single manufactured leaderboard. Each capability is compared with the most relevant specialist behavior, while Practical-owned routing suites test the integration layer that specialists do not provide by themselves.

For exact commands, pinned upstream commits, evidence boundaries, and reproduction requirements, see [`REPRODUCING.md`](REPRODUCING.md). Compact published aggregates live in [`results/v1.0/`](results/v1.0/).

## What is measured

| Suite | Compared arms | What it measures |
|---|---|---|
| Delivery | Practical vs Ponytail | Correctness, safety, build reachability, LOC, tokens, time, tool calls |
| Decision | Practical vs Matt Pocock `grilling` | Whether a material unresolved choice is surfaced and converged without premature implementation |
| Debug | Practical vs Superpowers | Root-cause repair, sibling callers, delivered invariant, safety, efficiency |
| Router | Practical vs expected route | Direct / Decision / Debugging / Implementation / Navigation classification |
| Native behavior | Practical only | Real Skill discovery and selective reference loading without prompt injection |
| Navigation ablation | Source search vs optional graph backend | Whether AST/LSP graph navigation pays for itself on real repositories |

The Decision and Debug comparisons are controlled project comparisons; they are not official upstream benchmark claims.

## Run the harness

Self-test without model calls:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

Normal release-quality matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3 -RequireStableRanking
```

Complete public regression matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3 -RequireStableRanking
```

Focused examples:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Suite router -Runs 3 -RequireStableRanking
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Suite debug -Runs 3 -RequireStableRanking
pwsh -NoProfile -File benchmarks/run.ps1 -Profile smoke -Suite router -Case direct-artifact -Arm practical-current
```

Candidate before/after gate:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef <accepted-previous-commit> `
  -IncludeBaseline `
  -RequireStableRanking
```

## Profiles

| Profile | Delivery | Router | Decision | Debug | Native behavior | Default runs |
|---|---:|---:|---:|---:|---:|---:|
| `smoke` | 3 | 4 | 1 | 1 | 3 | 1 |
| `standard` | 9 | 28 | 6 | 10 | 10 | 3 |
| `full` | 18 | 28 | 10 | 14 | 10 | 3 |

`standard` is the normal public release gate. `full` is the broader regression matrix. A stable published ranking requires at least three determinate repetitions per selected case/arm.

## Acceptance order

Interpret results in this order:

1. correctness and safety;
2. build/reachability;
3. only then LOC, tokens, model time, and tool calls.

A cheap failure cannot beat a correct safe result. The scorecard first applies a conservative quality gate and only computes relative efficiency after that gate is satisfied. See [`../docs/evaluations/2026-08-26-quality-gated-scorecard.md`](../docs/evaluations/2026-08-26-quality-gated-scorecard.md).

The public task catalog is a **regression corpus**, not a private generalization set. Once a case has influenced Skill wording, its future score is evidence against regression, not independent evidence that the same behavior generalizes everywhere.

## Why the router matters

Practical Coding's main architectural claim cannot be established by comparing only against Ponytail or only against Superpowers. The project also measures whether the integration policy itself behaves as intended:

- ordinary work remains Direct;
- an unresolved bug loads Debugging, not every engineering module;
- a material choice loads Decision;
- risky boundaries load Implementation;
- broad structural exploration loads Navigation;
- only the selected reference is read;
- workers are not a mandatory stage.

The next validation cycle also includes a **Ponytail + Superpowers combined-install arm**. That test is required before claiming that Practical is experimentally superior to installing both together. See [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md).

## Output artifacts

Normal run artifacts are written under ignored `benchmark-results/` directories and include:

```text
manifest.json
results.json
summary.json
comparisons.json
rollups.json
rollup-comparisons.json
scorecards.json
report.md
cells/
```

The committed release directory contains only compact aggregates suitable for public review. Raw transcripts/workspaces stay local because they are large and may contain machine-specific paths.
