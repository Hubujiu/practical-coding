# Practical Coding benchmark chain

This chain runs isolated Codex sessions directly against `gpt-5.6-luna`, preserves every prompt/transcript/workspace, applies mechanical graders, and writes JSON plus Markdown summaries. It follows the mature evaluation shape used by Agent Skills and Ponytail: realistic cases, fixed sources, clean sessions, repeated paired arms, deterministic assertions where possible, tokens/time, and raw evidence.

For prerequisites, pinned revisions, exact reproduction commands, evidence boundaries, and the published v1.11 calibration results, see [`REPRODUCING.md`](REPRODUCING.md). For the external benchmark landscape and the public-regression/external/held-out evidence model, see [`../docs/evaluations/2026-08-24-benchmark-landscape.md`](../docs/evaluations/2026-08-24-benchmark-landscape.md).

## Run

```powershell
pwsh -File benchmarks/run.ps1 -Profile smoke
pwsh -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3
pwsh -File benchmarks/run.ps1 -Profile full -Runs 3 -BaselineSkill D:\snapshots\practical-v1.9
pwsh -File benchmarks/run.ps1 -Profile standard -Runs 3 -BaselineRef HEAD
pwsh -File benchmarks/run.ps1 -Profile smoke -Suite router -Case direct-artifact -Arm practical-current
pwsh -File benchmarks/run.ps1 -Rescore D:\path\to\benchmark-results\20260824-203839
```

`run.ps1` is the canonical entrypoint. It loads the core runner through `run_catalog.py`, which installs the extended public case catalog before execution. This keeps benchmark mechanics separate from the evolving task corpus.

For a result that will be presented as a stable ranking, opt into the evidence gate:

```powershell
pwsh -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3 -RequireStableRanking
pwsh -File benchmarks/run.ps1 -Profile full -Suite delivery -Runs 3 -BaselineSkill docs\evaluations\snapshots\practical-v1.10 -RequireStableRanking
```

`-RequireStableRanking` refuses an effective run count below three, keeps production builds enabled for Delivery, writes to an explicit output directory when needed, and validates the completed result with `benchmarks/check_stability.py`. Existing artifacts can be checked directly:

```powershell
python benchmarks/check_stability.py benchmark-results\v111-delivery-n1-core-reverted --suite delivery
```

That command intentionally reports the published v1.11 Delivery `n=1` artifact as `PROVISIONAL`; it must not be used for a stable ranking until the same cells are rerun with at least three distinct repetitions.

## Profiles

| Profile | Delivery | Router | Decision | Debug | Default runs | Cells without previous/no-Skill arm |
|---|---:|---:|---:|---:|---:|---:|
| `smoke` | 3 | 4 | 1 | 1 | 1 | 13 |
| `standard` | 9 | 28 | 6 | 8 | 3 | 222 |
| `full` | 18 | 28 | 10 | 12 | 3 | 324 |

`standard` is the normal release gate. `full` carries the complete public regression matrix. The extra Router cases span all six routes; the expanded Debug set covers twelve cases across parsing, normalization, tenant isolation, pagination, units, row handling, state invariants, TTL semantics, URL handling, and the upstream transfer/amount tasks. Decision grows from four to ten two-turn decisions in `full`.

Useful options:

- `-BaselineSkill <directory>` adds a previous Practical snapshot to every suite. The directory must contain `SKILL.md` and its `references` directory.
- `-BaselineRef <git-revision>` materializes `SKILL.md` plus `references/` from a commit into the run artifact and adds it as `practical-previous`. This is the simplest before/after gate for dirty candidate edits.
- `-Suite`, `-Case`, and `-Arm` select repeatable subsets for diagnosis or focused regression gates.
- `-SourcesRoot <directory>` reuses pinned competitor checkouts. Without it, sources are cached under the user-local application data directory and cloned as needed.
- `-IncludeBaseline` adds a no-skill delivery arm.
- `-NoBuilds` skips runner-owned frontend production builds. It is rejected for a stable Delivery ranking.
- `-SelfTest` runs the local harness regression tests and validates fixtures, upstream scorers, expanded custom scorers, source pins, and reporting without model calls.
- `-FailOnCellFailure` makes any behavioral cell failure return exit code 2. By default only harness/infrastructure failures are non-zero, because a valid comparison may intentionally expose competitor or candidate failures.
- `-RequireStableRanking` requires at least three distinct repetitions per selected suite/case/arm and rejects incomplete or infrastructure-failed runs before they are called stable.
- `-Rescore <run-directory>` reapplies the current mechanical graders to saved workspaces/transcripts without another model call; the manifest records the new runner hash and rescore time.

By default, run artifacts are written under `benchmark-results/` and ignored by Git, so transcripts and generated workspaces remain inspectable across commands without entering commits. Use `-Output` for an explicit location.

The fast harness regression suite is also runnable without model calls:

```powershell
python -m unittest benchmarks.test_benchmarks benchmarks.test_stability benchmarks.test_catalog
```

The output directory contains:

```text
manifest.json           fixed model, commits, profile, cases, and skill hashes
results.json            one record per cell
summary.json            grouped rates, medians, means, and standard deviations
comparisons.json        Practical-minus-comparator behavioral and efficiency deltas
rollups.json            suite/arm totals across cases
rollup-comparisons.json suite-level Practical-minus-comparator deltas
report.md               human-readable comparison and Practical deltas
cells/                  prompt, raw JSONL, stderr, answer, and code workspace per cell
```

## Suites and scoring

- `delivery`: Ponytail's published agentic tasks and deterministic scorer. Reports correctness, safety, production LOC, test LOC, files, tokens, time, tool calls, and optional frontend build result.
- `router`: exact classification across Direct, Decision, Debugging, Implementation, Exploration, and Verification, including overlap and negative-boundary cases.
- `decision`: Practical versus Matt Pocock `grilling`. Uses a real resumed second turn and gates on frontier questions, one recommendation per question, no premature implementation, and convergence after scripted user decisions. Trade-off language is reported diagnostically but is not a declared grilling contract gate.
- `debug`: shared-root-cause tasks scored on the repaired invariant and sibling callers. Tests/TDD process receives no bonus. Each Practical-owned Debug seed is required to fail its deterministic scorer, and a separate oracle fixture must pass it before the case is accepted into the catalog.

`total_tokens` includes cached input because that is how Codex reports turn input. The report therefore also separates cached input, uncached input, output, and reasoning tokens. `duration_seconds` is per-cell process duration; suite elapsed time is recorded separately and is not obtained by summing concurrent cell durations.

## Acceptance

Use repeated paired results. A candidate is not accepted merely because its prose matches a Skill contract. Require no correctness/build regression, then compare delivered code and behavior. Treat LOC, tokens, and time as secondary within equally correct artifacts. `n=1` is a smoke result, not a stable ranking.

A published stable ranking must pass `benchmarks/check_stability.py` with the default minimum `n=3`. The gate checks distinct repetition IDs, complete-run metadata, and infrastructure errors. Behavioral or build failures remain valid benchmark observations and therefore do not invalidate the sample by themselves.

The public catalog is a **regression suite**, not a hidden generalization test. Once a case has influenced Skill wording, its future 100% score should be treated as a ceiling check. External benchmarks and a private held-out set are required for stronger claims.
