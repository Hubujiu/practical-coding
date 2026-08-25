# External benchmarks

Practical Coding keeps external evidence separate from its project-owned regression suites. The first executable adapter targets the immutable `skillsbench@1.1` dataset through BenchFlow.

Before a release-quality external run, follow [`../NEXT_VALIDATION.md`](../NEXT_VALIDATION.md). That document freezes the run order, no-post-hoc-change rule, confidence-interval interpretation, artifact-retention requirements, and the claim boundary for external versus held-out evidence. The current unchanged v2.0 Skill's mandatory next evidence milestone is the stable SkillsBench software-engineering run described below.

## SkillsBench

The adapter compares the same Codex/model configuration under two treatments:

- `no-skill`: no Agent Skill is mounted.
- `practical`: only the current repository's `practical-coding` Skill bundle is mounted through BenchFlow's custom `--skills-dir` path.

This deliberately does **not** use each SkillsBench task's curated Skill. The result measures Practical Coding's lift on SkillsBench tasks; it is not an official SkillsBench leaderboard submission for the benchmark's curated-Skill condition.

### Prerequisites

- Python 3.12+
- Git
- `uv`/`uvx`
- Codex CLI authenticated with `codex login` or a supported Codex/OpenAI credential
- Docker for the default `docker` sandbox; Daytona or Modal can be selected explicitly when configured

BenchFlow itself is launched on demand through `uvx` and pinned to `benchflow==0.6.5`, a tested 0.6.x release compatible with SkillsBench v1.1 and its `bench eval run` / versioned-dataset / custom-Skill CLI contract. The adapter also keeps a metadata checkout at the exact `v1.1` tag for category selection. Actual benchmark execution uses `-d skillsbench@1.1`, so BenchFlow resolves the versioned dataset and validates its task digests.

### Fast instrument check

No model, network, or Docker calls:

```powershell
pwsh -File benchmarks/run_external.ps1 -Benchmark skillsbench -SelfTest
```

### Smoke

Three software-engineering tasks, one run per arm. This is only a plumbing check and is always provisional:

```powershell
pwsh -File benchmarks/run_external.ps1 `
  -Benchmark skillsbench `
  -Profile smoke
```

### Stable software-engineering lift

`standard` discovers every `software-engineering` task in the SkillsBench v1.1 registry roster and runs three separately materialized paired repetitions by default:

```powershell
pwsh -File benchmarks/run_external.ps1 `
  -Benchmark skillsbench `
  -Profile standard `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

Before any model calls, the adapter runs the SkillsBench oracle across the selected task set. A stable result requires:

1. oracle reward `1.0` for every selected task;
2. at least three repetitions;
3. exactly one healthy `no-skill` and one healthy `practical` result for every task/repetition pair;
4. no missing or unhealthy pair.

Behavioral failures remain valid data. Infrastructure failures or missing rewards make the evidence provisional or abort the run.

For interpretation, use the task-cluster-bootstrap 95% confidence interval in the adapter output. If the interval crosses zero, report the numerical lift but do not call the improvement resolved. If it is entirely below zero, treat that as an external regression. Do not remove unfavorable tasks after inspecting results; instrument defects invalidate and require rerunning the affected complete matrix rather than selective exclusion.

### Full cross-domain interference run

`full` uses the complete `skillsbench@1.1` registry roster. This is intentionally expensive and is mainly useful for measuring whether a general coding Skill causes irrelevant-domain interference:

```powershell
pwsh -File benchmarks/run_external.ps1 `
  -Benchmark skillsbench `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

Use `-Task <id>` repeatedly to run an explicit versioned subset.

### Outputs

Artifacts are written under `benchmark-results/external/skillsbench-<timestamp>/` unless `-Output` is supplied:

```text
manifest.json        dataset/model/environment pins, task roster, Skill hash, commands
oracle/              BenchFlow oracle jobs
oracle.log           oracle command output
runs/
  r001/
    no-skill/        raw BenchFlow jobs
    practical/       raw BenchFlow jobs
    no-skill.log
    practical.log
  ...
pairs.json           healthy task/repetition pairs used for comparison
summary.json         pass/reward lift, win/loss/tie counts, 95% CIs, per-task rates
report.md            human-readable external lift report
staged-skills/       exact Practical Coding bundle mounted into BenchFlow
```

The two model arms alternate execution order on successive repetitions. Confidence intervals use a deterministic task-cluster bootstrap: task IDs are resampled as clusters while all repeated trials for the sampled task stay together.

### Interpretation

The primary result is pass-rate lift:

```text
Codex/Luna no Skill
        vs
Codex/Luna + Practical Coding
```

A positive numerical delta is external evidence on the selected public SkillsBench tasks, but statistical wording follows [`../NEXT_VALIDATION.md`](../NEXT_VALIDATION.md): distinguish a resolved positive interval from a delta whose 95% interval crosses zero. Because SkillsBench is public, this remains external public evidence rather than a private holdout. Do not fold these scores into the project-owned Router/Decision/Debug regression rollups, and do not describe this custom-Skill ablation as an official SkillsBench curated-Skill leaderboard row.
