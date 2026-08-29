# Practical Coding benchmark chain

This directory contains the reproducible evaluation harness for the **Practical Coding v1.3 adaptive-rigor candidate**. The last committed validated baseline is v1.2 under [`results/v1.2/`](results/v1.2/); v1.0/v1.1/v1.2 result directories remain historical evidence for their tested contracts.

The benchmark design intentionally avoids a single manufactured leaderboard. Each specialist capability is compared with the most relevant behavior, while the Practical-owned control suite tests the integration policy itself.

For exact commands, pinned upstream commits, evidence boundaries, and release gates, see [`REPRODUCING.md`](REPRODUCING.md) and [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md).

## What is measured

| Suite | Compared arms | What it measures |
|---|---|---|
| Delivery | Practical vs Ponytail | Correctness, safety, build reachability, LOC, tokens, time, tool calls |
| Decision | Practical vs Matt Pocock `grilling` | Whether a blocking material choice is surfaced and converged without premature implementation |
| Debug | Practical vs Superpowers | Root-cause repair, sibling callers, delivered invariant, safety, efficiency |
| `router` *(legacy suite id)* | Practical vs adaptive-rigor contract | Decision Gate state, current execution rigor, and Retrieval minimum/maximum cost bounds |
| Native behavior | Practical only | Real Skill discovery, selective reference loading, transition behavior, Retrieval/backend use, and context isolation without prompt injection |
| Navigation ablation | Source search vs optional graph backend | Whether structural retrieval pays for itself on real repositories |

The Decision and Debug comparisons are controlled project comparisons; they are not official upstream benchmark claims.

## v1.3 control contract

The old v1.2 exact classifier is no longer the architecture being tested. The v1.3 control state is:

```text
DECISION  = CLEAR | REQUIRED
EXECUTION = BLOCKED | DIRECT | DEBUGGING | IMPLEMENTATION
RETRIEVAL = minimum sufficient .. maximum reasonable
```

Required invariant:

```text
DECISION=REQUIRED  => EXECUTION=BLOCKED
DECISION=CLEAR     => EXECUTION in DIRECT | DEBUGGING | IMPLEMENTATION
```

Meaning:

- `DECISION=REQUIRED`: a material unresolved choice blocks or materially changes the next safe action;
- `DIRECT`: the Core is sufficient now;
- `DEBUGGING`: an observed failure exists and its cause is not evidenced;
- `IMPLEMENTATION`: safe execution is blocked by an unknown contract/invariant, unresolved material risk boundary, or insufficient evidence for a risky claim;
- Retrieval is not required to have one unique exact label when two neighboring cheap strategies are both reasonable.

Four explicit transition regressions prevent the profiles from becoming task categories or a mandatory pipeline:

- Decision → Direct;
- Decision → Implementation;
- Debugging → Direct after diagnosis;
- Debugging → Implementation only when an unresolved material execution boundary remains.

## Runner architecture

The benchmark runtime is intentionally layered:

- `run_benchmarks.py`: stable v2.0 execution/scoring core retained for historical interpretability;
- `case_catalog.py`: extended public regression corpus;
- `adaptive_rigor.py`: v1.3 state contract, retrieval-bound scoring, and transition cases;
- `run_catalog.py`: canonical v2.1 entrypoint that installs both adapters before execution.

Use `benchmarks/run.ps1`, which invokes the canonical runner. Do not run the v2.0 core directly when evaluating v1.3.

## Run the harness

Self-test without model calls:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

Normal candidate matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3 -RequireStableRanking
```

Complete public regression matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3 -RequireStableRanking
```

Focused adaptive-rigor examples:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Suite router -Runs 3 -RequireStableRanking
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Suite behavior -Runs 3 -RequireStableRanking
pwsh -NoProfile -File benchmarks/run.ps1 -Profile smoke -Suite router -Case transition-debug-to-direct -Arm practical-current
```

Candidate against accepted v1.2:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef 88382d2b0c00fa278067a5933bbcacc86f46b56e `
  -IncludeBaseline `
  -RequireStableRanking
```

The v1.2 and v1.3 classification schemas are not score-comparable. Before/after claims should be made only on unchanged task/scorer surfaces such as Delivery, Decision, and Debug, plus qualitative transition/reference-loading evidence.

## Profiles

After installing `case_catalog.py` and `adaptive_rigor.py` through the canonical runner:

| Profile | Delivery | Adaptive-rigor (`router`) | Decision | Debug | Native behavior | Default runs |
|---|---:|---:|---:|---:|---:|---:|
| `smoke` | 3 | 5 | 1 | 1 | 3 | 1 |
| `standard` | 9 | 42 | 6 | 10 | 22 | 3 |
| `full` | 18 | 42 | 10 | 14 | 22 | 3 |

`standard` is the normal bounded candidate gate. `full` carries the complete public regression matrix. A stable published comparison requires at least three determinate repetitions per selected case/arm.

The public task catalog is a **regression corpus**, not a private generalization set. Once a case has influenced Skill wording or scoring design, its future score is evidence against regression, not independent evidence that the same behavior generalizes everywhere.

## Acceptance order

Interpret results in this order:

1. correctness and safety;
2. build/reachability;
3. control correctness and missed escalation;
4. Retrieval sufficiency before Retrieval efficiency;
5. only then LOC, tokens, model time, and tool calls.

A cheap failure cannot beat a correct safe result. Cost cannot rescue insufficient retrieval or a wrong execution state.

## Why adaptive-rigor classification matters

Practical Coding's architectural claim cannot be established only by Delivery vs Ponytail or Debug vs Superpowers. The control suite measures whether the system pays for stricter process only when a blocker exists:

- settled or cheap reversible choices do not block execution;
- an unresolved material choice blocks execution rather than competing with Debugging/Implementation as a peer route;
- ordinary execution starts Direct;
- an unknown-cause failure adds Debugging rigor;
- an unresolved material execution boundary adds Implementation rigor;
- diagnosed failures return to Direct unless a different blocker remains;
- Retrieval is independent and bounded by sufficiency and reasonable cost;
- broad structural exploration does not become a reasoning state;
- only the required reasoning reference is read in a root context;
- workers are an economic isolation mechanism, not a mandatory stage.

The next validation cycle also requires a **Ponytail + Superpowers combined-install arm** before any claim of experimental superiority over installing both together. See [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md).

## Retrieval scoring

The v1.3 classifier stores each case with:

```text
retrieval_min
retrieval_max
```

A result is:

- **insufficient** when actual retrieval is below `retrieval_min`;
- **efficient enough** when actual retrieval is at or below `retrieval_max`;
- **passed** on Retrieval only when both conditions hold.

This avoids treating `TARGETED` vs a still-cheap `BOUNDED` search as necessarily semantically wrong while continuing to reject missing context and unnecessary structural exploration.

The bounds are part of the benchmark contract and must be frozen before a validation cycle. Do not widen them after seeing failures simply to improve the score.

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

The committed result directories contain compact aggregates suitable for public review. Raw transcripts/workspaces stay local because they are large and may contain machine-specific paths.

## Suites and scoring

- `delivery`: Ponytail's published agentic tasks and deterministic scorer. Frontend cases prepare pinned dependencies before the agent starts and use the same environment for runner-owned production build evidence.
- `router`: retained as a CLI suite name for compatibility. Under canonical runner v2.1 it scores the three-field adaptive-rigor state and Retrieval interval, not the v1.2 `REASONING/RETRIEVAL` classifier.
- `decision`: Practical versus Matt Pocock `grilling`. Uses a real resumed second turn and gates on frontier questions, recommendations, no premature implementation, and convergence after scripted user constraints.
- `debug`: shared-root-cause tasks scored on the repaired invariant and sibling callers. Named TDD/process rituals receive no bonus; delivered behavior and safety are what count.
- `behavior`: installs Practical Coding into an isolated native `CODEX_HOME`, does not inject Skill text into the prompt, and inspects tool traces for Skill discovery and reference isolation. Transition cases ensure settled decisions and diagnosed failures do not reload obsolete profiles. Structural Retrieval/backend use is scored independently.

Infrastructure, timeout, transcript-capture, missing-runtime, and build-OOM failures are `indeterminate`, not Skill failures. Comparisons omit pairs containing indeterminate cells instead of rewarding the unaffected arm.

`total_tokens` includes cached input because that is how Codex reports usage. Reports also separate cached input, uncached input, output, and reasoning tokens. `duration_seconds` is per-cell process duration; suite elapsed time is recorded separately.

## Evidence status

No v1.3 model result is committed yet. The last validated evidence is v1.2:

- reasoning classification: 114/114;
- exact Retrieval classification: 106/114;
- Native Behavior: 54/54;
- Practical-only Delivery/Decision/Debug regression: 75/75.

Those values are historical baseline evidence, not v1.3 scores.

Use repeated paired results. `n=1` is a smoke result, not a stable ranking. The strongest generalization claims still require the private held-out protocol in [`NEXT_VALIDATION.md`](NEXT_VALIDATION.md).
