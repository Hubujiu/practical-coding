# Practical Coding benchmark chain

This directory contains the reproducible evaluation harness for **Practical Coding v1.2**. The v1.2 runner uses a two-dimensional routing contract; committed v1.1 results remain historical evidence for the former five-way classifier.

The benchmark design intentionally avoids a single manufactured leaderboard. Each capability is compared with the most relevant specialist behavior, while Practical-owned routing suites test the integration layer that specialists do not provide by themselves.

For exact commands, pinned upstream commits, evidence boundaries, and reproduction requirements, see [`REPRODUCING.md`](REPRODUCING.md). Current compact evidence lives in [`results/v1.2/`](results/v1.2/); [`results/v1.1/`](results/v1.1/) and [`results/v1.0/`](results/v1.0/) are retained as historical evidence.

## What is measured

| Suite | Compared arms | What it measures |
|---|---|---|
| Delivery | Practical vs Ponytail | Correctness, safety, build reachability, LOC, tokens, time, tool calls |
| Decision | Practical vs Matt Pocock `grilling` | Whether a material unresolved choice is surfaced and converged without premature implementation |
| Debug | Practical vs Superpowers | Root-cause repair, sibling callers, delivered invariant, safety, efficiency |
| Router | Practical vs expected two-dimensional contract | Reasoning (`NONE` plus Decision / Debugging / Implementation) and independent Retrieval (`NONE` / Targeted / Bounded / Structural) |
| Native behavior | Practical only | Real Skill discovery, reasoning-reference isolation, and independent Retrieval/reference/backend behavior without prompt injection |
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
| `standard` | 9 | 38 | 6 | 10 | 18 | 3 |
| `full` | 18 | 38 | 10 | 14 | 18 | 3 |

`standard` is the normal public release gate. `full` carries the broader complete public regression matrix. Router cases cover all four reasoning outputs (`NONE` plus three reasoning routes), all four Retrieval modes, and cross-products such as `NONE+STRUCTURAL` and `IMPLEMENTATION+STRUCTURAL`. Native behavior repeats Direct/Implementation boundaries without injected Skill text, adds Decision/Debug precedence cases, and scores Navigation/backend use independently from reasoning-reference selection. The expanded Debug set covers fourteen cases across parsing, normalization, tenant isolation, pagination, units, row handling, state invariants, TTL semantics, URL handling, and the upstream transfer/amount tasks. Decision grows from six to ten two-turn decisions in `full`. A stable published ranking requires at least three determinate repetitions per selected case/arm.

## Acceptance order

Interpret results in this order:

1. correctness and safety;
2. build/reachability;
3. only then LOC, tokens, model time, and tool calls.

A cheap failure cannot beat a correct safe result. The scorecard first applies a conservative quality gate and only computes relative efficiency after that gate is satisfied. See [`../docs/evaluations/2026-08-26-quality-gated-scorecard.md`](../docs/evaluations/2026-08-26-quality-gated-scorecard.md).

The public task catalog is a **regression corpus**, not a private generalization set. Once a case has influenced Skill wording, its future score is evidence against regression, not independent evidence that the same behavior generalizes everywhere.

## Why the router matters

Practical Coding's main architectural claim cannot be established by comparing only against Ponytail or only against Superpowers. The project also measures whether the integration policy itself behaves as intended:

- ordinary work selects no reasoning route;
- an unresolved bug loads Debugging, not every engineering module;
- a material choice loads Decision;
- risky boundaries load Implementation;
- Retrieval is classified independently as none, targeted, bounded, or structural;
- broad structural exploration may load Navigation without becoming a fourth reasoning route;
- only the selected reasoning reference is read;
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

## Suites and scoring

- `delivery`: Ponytail's published agentic tasks and deterministic scorer. For frontend template cases, the runner installs the pinned lockfile dependencies before the agent starts, so the agent and the runner-owned production build use the same executable type/build environment. Reports correctness, safety, production LOC, test LOC, files, tokens, time, tool calls, setup time, and optional frontend build result.
- `router`: exact two-field classification. `REASONING` is `NONE`, `DECISION`, `DEBUGGING`, or `IMPLEMENTATION`; only the latter three are reasoning routes. `RETRIEVAL` is independently `NONE`, `TARGETED`, `BOUNDED`, or `STRUCTURAL`. A cell passes only when both fields match. The former Verification route remains folded into Implementation, while former Exploration cases now expect `REASONING=NONE; RETRIEVAL=STRUCTURAL`; results are therefore not comparable with the v1.1 five-way classifier.
- `decision`: Practical versus Matt Pocock `grilling`. Uses a real resumed second turn and gates on frontier questions, one recommendation per question, no premature implementation, and convergence after scripted user decisions. Trade-off language is reported diagnostically but is not a declared grilling contract gate.
- `debug`: shared-root-cause tasks scored on the repaired invariant and sibling callers. Tests/TDD process receives no bonus. Each Practical-owned Debug seed is required to fail its deterministic scorer, and a separate oracle fixture must pass it before the case is accepted into the catalog.
- `behavior`: installs Practical Coding into an isolated native `CODEX_HOME`, does not inject its text into the prompt, and mechanically inspects command traces for `SKILL.md` discovery. Reasoning references are scored separately from Retrieval: Direct reads no reasoning reference; Decision, Debugging, and Implementation read only their expected reasoning reference; structural Retrieval may read `navigation.md` and is separately checked against the expected source/graph backend. Infrastructure, timeout, transcript-capture, missing-runtime, and build OOM failures are reported as `indeterminate`, not Skill failures. Comparisons omit pairs containing indeterminate cells instead of rewarding the unaffected arm.

`total_tokens` includes cached input because that is how Codex reports turn input. The report therefore also separates cached input, uncached input, output, and reasoning tokens. `duration_seconds` is per-cell process duration; suite elapsed time is recorded separately and is not obtained by summing concurrent cell durations.

## Acceptance

Use repeated paired results. A candidate is not accepted merely because its prose matches a Skill contract. Require no correctness/build regression, then compare delivered code and behavior. Treat LOC, tokens, and time as secondary within equally correct artifacts. `n=1` is a smoke result, not a stable ranking.

The machine-readable scorecard makes that order explicit. A comparison first has to stay within a 3 percentage-point suite pass-rate non-inferiority margin, with no lower suite build/safety rate and no case-level safety regression. Cost cannot rescue a failed quality gate. For a quality-qualified comparison, relative efficiency is the weighted geometric mean

`E = exp(sum(w_i * ln(cost_comparator_i / cost_practical_i)))`

over uncached input tokens (0.35), output tokens (0.15), model time (0.35), and tool calls (0.15), renormalized when a metric is unavailable. The diagnostic utility is `U = ((Q_practical + 0.01) / (Q_comparator + 0.01))^2 * E`. It is a relative sensitivity summary, not an absolute leaderboard score. The report also preserves the Pareto result, so users can see when one arm dominates and when the result is a real quality/cost trade-off. `qualified` additionally requires at least three determinate repetitions in every paired case; otherwise a quality-passing score remains `provisional`.

A published internal stable ranking must pass `benchmarks/check_stability.py` with the default minimum `n=3`. The gate checks distinct repetition IDs, complete-run metadata, and infrastructure errors. Behavioral or build failures remain valid benchmark observations and therefore do not invalidate the sample by themselves.

The public catalog is a **regression suite**, not a hidden generalization test. Once a case has influenced Skill wording, its future 100% score should be treated as a ceiling check. A private held-out set is still required for the strongest generalization claims.
