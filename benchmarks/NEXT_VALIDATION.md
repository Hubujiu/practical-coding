# Next validation protocol

This document freezes the evidence requirements for the next Practical Coding benchmark cycle **before** any new model results are inspected. Its purpose is to prevent post-hoc metric selection, public-regression overfitting, and ambiguous claims about what a benchmark proves.

The current accepted Skill is Practical Coding v2.1 from `53ee5ec5c48fc51795415986a54d9e93afa14105`. The published release result is [`docs/evaluations/2026-08-26-practical-v21-release.md`](../docs/evaluations/2026-08-26-practical-v21-release.md), with compact data under [`results/v2.1/`](results/v2.1/). That result is a public regression/comparator matrix, not external generalization evidence.

## 1. Freeze before running

Before any release-quality model run:

1. Commit the candidate. Do not benchmark a moving working tree for publication.
2. Record `git rev-parse HEAD` and `git status --short` in the run notes. The working tree must be clean.
3. Do not change `SKILL.md`, `references/`, benchmark task definitions, scorers, or acceptance thresholds after seeing partial results from the same validation cycle.
4. If a benchmark/scorer bug is discovered, fix the instrument, invalidate the affected run, document why, and rerun the complete affected matrix. Do not selectively rescore or exclude only unfavorable cells.
5. Preserve the candidate Skill bundle hash and benchmark runner/manifest hashes produced by the harness.

Documentation-only changes that do not change `SKILL.md` or `references/` do not require rerunning the accepted internal v2.1 matrix. The next new evidence priority is the independent external run.

## 2. Required run order

### Gate A — instrument self-test

Run before spending model calls:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
pwsh -NoProfile -File benchmarks/run_external.ps1 -Benchmark skillsbench -SelfTest
```

Both must pass. A failing self-test blocks every later claim.

### Gate B — internal full regression/comparator matrix

Run this gate whenever `SKILL.md` or anything under `references/` changes from the last accepted Skill.

Use the last accepted Skill commit as the previous-version baseline and include the Delivery no-Skill arm:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef 53ee5ec5c48fc51795415986a54d9e93afa14105 `
  -IncludeBaseline `
  -RequireStableRanking
```

For a later release, replace the baseline SHA with the immediately preceding accepted Skill revision. Do not silently keep comparing every future version against v2.1.

Acceptance rules:

- zero infrastructure failures;
- every selected case/arm/repetition is present;
- Delivery production builds remain enabled;
- minimum `n=3` is satisfied for every published cell;
- correctness, safety, and build behavior take precedence over LOC, tokens, tool calls, and latency;
- a candidate with a material correctness/safety/build regression against the previous accepted Practical version is rejected even if it is smaller or cheaper;
- comparator deltas are reported as controlled results on this public matrix, not as universal rankings.

The public Router/Decision/Debug/Delivery catalog is allowed to become saturated. A 100% score is a regression ceiling once the case has influenced Skill wording.

### Gate C — external SkillsBench software-engineering lift

This is the **mandatory next evidence milestone for the current unchanged v2.1 Skill**.

Run the complete SkillsBench v1.1 `software-engineering` roster with paired curated-Skills-only / curated-Skills-plus-Practical arms and three repetitions. Use Linux or WSL2 with Docker; the native-Windows v2.1 attempt was rejected as infrastructure-blocked before model execution.

```powershell
pwsh -NoProfile -File benchmarks/run_external.ps1 `
  -Benchmark skillsbench `
  -Comparison curated-vs-curated-practical `
  -Profile standard `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

A stable external result requires:

- SkillsBench oracle reward `1.0` for every selected task before model calls;
- at least three repetitions;
- exactly one healthy curated-only and one healthy curated-plus-Practical result for every task/repetition pair;
- no missing/unhealthy pairs;
- no post-hoc task removal because a task is unfavorable to Practical;
- the exact dataset version, BenchFlow version, model, reasoning effort, Skill bundle hash, task roster, commands, and adapter hash preserved in artifacts.

Primary metric: paired pass-rate lift. Secondary metrics: mean-reward lift, pass flips, normalized gain, cost/latency where available, and the adapter's task-cluster-bootstrap 95% confidence intervals.

Interpretation rule:

- CI entirely above zero: evidence of positive external lift on the selected SkillsBench software-engineering population;
- CI crossing zero: report the numerical delta, but do not claim a resolved improvement;
- CI entirely below zero: treat as external regression and investigate before strengthening project claims.

This run is a Practical-owned additive-Skill ablation on SkillsBench, **not** an official SkillsBench leaderboard submission.

### Gate D — cross-domain interference

Run only when making a claim that Practical is safe as a broadly installed general Skill outside software-engineering tasks, or before a major release where the cost is justified:

```powershell
pwsh -NoProfile -File benchmarks/run_external.ps1 `
  -Benchmark skillsbench `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

The purpose is interference detection, not maximizing a combined score. Report software-engineering lift separately from non-coding-domain behavior.

## 3. Private held-out requirement

External public benchmarks are still public. The strongest generalization claim requires a private held-out set that is not consulted while editing the Skill.

Minimum protocol for the first held-out set:

- at least 20 real coding tasks from recent issues/PRs or independently authored repositories;
- include simple/local changes, root-cause bugs, multi-file/risky changes, and broad-navigation/design work rather than prompt paraphrases of public regression cases;
- deterministic executable verification whenever possible;
- each task has a seed state that fails its verifier and an oracle/reference state that passes before model calls;
- compare the same fixed agent/model/harness under `no-skill` and `practical` treatments;
- use at least three paired repetitions for a publication-quality claim;
- keep task prompts, expected mechanisms, and verifier details unavailable while editing `SKILL.md` and `references/`;
- do not move failed held-out tasks into the public regression set until the validation cycle is frozen and reported.

A practical first stratification is 5 simple/direct tasks, 5 debugging tasks, 5 feature/risk-coordination tasks, and 5 architecture/navigation tasks. Diversity of failure mechanism matters more than exact category counts.

## 4. Statistical reporting rules

### External benchmark

Use the SkillsBench adapter's task-cluster-bootstrap 95% confidence intervals. Repetitions of the same task stay in one sampled cluster.

### Internal benchmark

`n=3` is a stability gate, **not** proof that small comparator differences are statistically resolved. Until the internal reporter gains paired task-cluster confidence intervals:

- say `numerically ahead`, `numerically behind`, or `tied on this matrix` for small deltas;
- do not convert a one-cell difference such as 54/54 versus 53/54 into a broad superiority claim;
- report task counts and repetitions separately so repeated trials are not mistaken for independent tasks.

A future internal-statistics change should bootstrap by task/case ID, keeping all repetitions for that task together.

## 5. Required ablations before architectural claims

Before claiming that event-driven progressive disclosure itself causes the gain, run an ablation rather than inferring mechanism from the full Skill.

Target treatment matrix:

```text
no-skill
Core only
Core + Decision
Core + Debugging
Core + Implementation
Full Practical
relevant external comparator
```

At minimum measure:

- task success / safety / build;
- unnecessary module loads;
- missed escalations;
- references loaded and reference bytes/tokens injected;
- uncached input, output, and reasoning tokens;
- tool calls and model time.

The existing comparator benchmarks can establish outcome differences; only the ablation can establish which Practical module or routing behavior caused them.

## 6. Routing/interference metrics to add

Router exact-classification accuracy is necessary but insufficient for the project's main progressive-disclosure claim. A future harness revision should additionally record:

- `unnecessary_module_loads`;
- `missed_escalations`;
- `references_loaded`;
- reference bytes/tokens loaded;
- route changes per task;
- time/token cost before the correct route is reached.

A separate noise/interference treatment should install unrelated or competing Skills and test whether Practical still avoids unnecessary module loading. Do not claim resistance to Skill-context interference until that treatment exists.

These are **future benchmark requirements**, not metrics available in the current v2.1 report.

## 7. Failure handling discipline

Behavioral failures are evidence, not harness failures.

When a failure appears:

1. Freeze and save the complete run first.
2. Classify it as infrastructure, scorer/oracle defect, stochastic behavior, or genuine Skill behavior.
3. For genuine behavior, identify the underlying mechanism across tasks before editing the Skill.
4. Do not add case-specific nouns or examples from the failed public task to `SKILL.md` merely to turn the cell green.
5. Prefer a general invariant only after the same mechanism appears in an independent task or held-out analogue.
6. After a Skill change, rerun the complete affected gate against the previous accepted Skill; do not publish only the repaired case.

For any current public Debug failure, the next useful evidence is an independent shared-boundary analogue, not wording that explicitly names the failed fixture's domain nouns.

## 8. Artifact retention and publication

For every result used in README/release claims, retain at least:

```text
manifest.json
results.json / pairs.json
summary.json
comparisons.json (internal, when present)
rollups.json and rollup-comparisons.json (internal, when present)
report.md
exact Skill bundle used
```

Preserve raw transcripts/workspaces/BenchFlow jobs locally. For a formal release, attach a compressed benchmark artifact or at minimum the machine-readable manifest/results/summary/comparison files so third parties can audit the published numbers without paying to rerun every model call.

Do not commit large generated workspaces into the normal source tree.

## 9. Claim ladder

Use the strongest claim justified by the completed gates, and no stronger:

| Completed evidence | Allowed claim |
|---|---|
| Internal public regression only | Practical is stable / numerically competitive on the fixed internal comparator matrix |
| + stable external SkillsBench standard | Practical shows the reported external lift (or lack of resolved lift) on SkillsBench software-engineering tasks |
| + cross-domain run | Add evidence about interference outside software engineering |
| + private held-out paired run | Generalization claims may reference the held-out population, with its scope stated explicitly |

Never collapse Delivery vs Ponytail, Decision vs grilling, and Debug vs Superpowers into a single universal leaderboard score. They are role-specific head-to-head comparisons against different task populations.

## 10. Immediate next action

Because the current documentation changes do not alter the accepted v2.1 Skill bundle, **do not tune the Skill against the existing public cells again before obtaining new evidence**.

Run in this order:

```text
1. Internal + external self-tests
2. SkillsBench software-engineering standard, n=3, stable gate
3. Freeze and archive the complete external artifacts
4. Interpret the CI before changing Skill wording
5. Only then decide whether a new Skill revision is justified
6. If the Skill changes, run the full internal current/previous/no-Skill comparator gate
7. Build and run private held-out evidence before broad SOTA/generalization claims
```
