# External benchmarks

Practical Coding keeps external evidence separate from its project-owned regression suites. The first executable adapter targets the immutable `skillsbench@1.1` dataset through BenchFlow.

Before a release-quality external run, follow [`../NEXT_VALIDATION.md`](../NEXT_VALIDATION.md). That document freezes the run order, no-post-hoc-change rule, confidence-interval interpretation, artifact-retention requirements, and the claim boundary for external versus held-out evidence.

## SkillsBench

The adapter supports two paired comparisons under the same Codex/model configuration:

- `no-skill-vs-practical`: no Agent Skill versus only the current `practical-coding` bundle.
- `curated-vs-curated-practical`: each task's immutable curated Skill set versus an exact per-task union of those curated Skills and `practical-coding`.

The first comparison measures Practical Coding by itself and is not an official curated-Skill leaderboard row. The second measures incremental value or interference on top of curated Skills. Because BenchFlow replaces bundled Skills when a custom `--skills-dir` is supplied, the adapter materializes a separate union directory and invokes the trained arm once per task; it never uses a cross-task mega-bundle.

### Prerequisites

- Python 3.12+
- Git
- `uv`/`uvx`
- Codex CLI authenticated with `codex login` or a supported Codex/OpenAI credential
- Docker for the default `docker` sandbox; Daytona or Modal can be selected explicitly when configured
- Linux, or a normal WSL2 Linux distribution with Docker access. Native Windows is rejected because the pinned BenchFlow release applies host path semantics to Linux container paths.

BenchFlow is launched on demand through `uvx` and pinned to `benchflow==0.6.3`, the release named by the SkillsBench v1.1 registry commit. The adapter keeps a metadata checkout at the exact `v1.1` tag; when task files are not present in that tag's working tree, it reads them from the immutable per-task commits recorded in `registry.json`. Actual execution uses `-d skillsbench@1.1`, so BenchFlow resolves the versioned dataset and validates task digests.

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
  -Profile smoke `
  -Comparison curated-vs-curated-practical
```

### Stable software-engineering lift

`standard` discovers every `software-engineering` task in the SkillsBench v1.1 registry roster and runs three separately materialized paired repetitions by default:

```powershell
pwsh -File benchmarks/run_external.ps1 `
  -Benchmark skillsbench `
  -Profile standard `
  -Comparison curated-vs-curated-practical `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

Before any model calls, the adapter runs the SkillsBench oracle across the selected task set. A stable result requires:

1. oracle reward `1.0` for every selected task;
2. at least three repetitions;
3. exactly one healthy base-arm and one healthy trained-arm result for every task/repetition pair;
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
    <base-arm>/       raw BenchFlow jobs
    <trained-arm>/    raw BenchFlow jobs
    <base-arm>.log
    <trained-arm>.log
  ...
pairs.json           healthy task/repetition pairs used for comparison
summary.json         pass/reward lift, win/loss/tie counts, 95% CIs, per-task rates
report.md            human-readable external lift report
staged-skills/       exact Practical Coding bundle mounted into BenchFlow
merged-skills/       per-task curated + Practical unions when requested
```

The two model arms alternate execution order on successive repetitions. Confidence intervals use a deterministic task-cluster bootstrap: task IDs are resampled as clusters while all repeated trials for the sampled task stay together.

### Interpretation

The primary result is paired pass-rate lift for the selected comparison. For example:

```text
Codex/Luna curated Skills
        vs
Codex/Luna curated Skills + Practical Coding
```

A positive numerical delta is external evidence on the selected public SkillsBench tasks, but statistical wording follows [`../NEXT_VALIDATION.md`](../NEXT_VALIDATION.md): distinguish a resolved positive interval from a delta whose 95% interval crosses zero. Because SkillsBench is public, this remains external public evidence rather than a private holdout. Do not fold these scores into the project-owned Router/Decision/Debug regression rollups, and do not describe either custom ablation as an official leaderboard row.
