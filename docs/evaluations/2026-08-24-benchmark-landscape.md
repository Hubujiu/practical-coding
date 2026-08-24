# Coding-agent and Agent-Skill benchmark landscape

Date: 2026-08-24

This note separates project regression tests from external benchmark evidence. Public regression cases are useful for preventing known failures from returning, but repeated prompt iteration against them eventually makes them unsuitable as evidence of generalization.

## Most relevant public projects

| Project | What it measures | Dataset / repetition shape | Why it matters to Practical Coding |
|---|---|---|---|
| [SkillsBench](https://skillsbench.ai/) / [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench) | Skill effectiveness and agent ability to use Skills | v1.1 leaderboard: 87 tasks, paired with/without-Skills, up to 3 trials, deterministic verifiers, 95% CIs | Closest external benchmark to this project. Its primary question is the same one Practical should answer: does adding the Skill improve a fixed agent/model? |
| [langchain-ai/skills-benchmarks](https://github.com/langchain-ai/skills-benchmarks) | Skill documentation layout, treatment A/B, split/merged Skills, distractor/noise effects | Docker tasks decoupled from treatments; repeated pytest runs; trajectory logging | Strong reference for treatment design and testing routing/interference rather than only final task success. |
| [SWE-bench Verified](https://www.swebench.com/verified.html) | Real GitHub issue resolution | 500 human-filtered issues; public agent leaderboard plus a standardized mini-SWE-agent view | Canonical external coding-agent signal. Useful for testing whether Practical improves a neutral coding harness, but less specific to Skill design. |
| [Terminal-Bench](https://github.com/harbor-framework/terminal-bench) | Long-horizon terminal-agent work | Continuous tagged dataset releases; containerized tasks; oracle solutions; leaderboard; oracle is recommended to run 5x | Strong model for benchmark operations: version datasets, continuously validate tasks, keep oracle checks, and treat benchmark maintenance as a product. |
| [FeatureBench](https://github.com/LiberCoders/FeatureBench) | End-to-end feature development | 200 full tasks, 100 fast tasks, 30 lite tasks; executable environments and an open data-generation pipeline | Useful external evidence for Implementation/Exploration behavior because tasks span larger feature surfaces than bug-only benchmarks. |
| [Senior SWE-Bench](https://senior-swe-bench.snorkel.ai/) | Senior-level design/build and investigate/fix behavior from realistic messages | 100 initial tasks: 50 public and 50 private; recent real PRs; behavioral verification and quality gates | Best reference for contamination control and realistic debugging prompts. The private half is especially relevant once Practical's public regression set is used for prompt iteration. |
| [ProgramBench](https://programbench.com/) | Rebuilding complete programs from behavioral contracts | 200 tasks and a large hidden behavioral-test suite | Useful as a hard design/implementation ceiling, but less directly targeted at a procedural coding Skill. |

## Evidence model for Practical Coding

Use three layers instead of one leaderboard number:

1. **Public regression layer** — Router, Decision, Debug and the Ponytail-derived Delivery tasks in this repository. These should stay deterministic and are allowed to encode previously observed failures. Their job is to prevent regression, not prove unseen-task generalization.
2. **External benchmark layer** — run the Skill as an augmentation treatment on independent public suites. SkillsBench is executable through `benchmarks/run_external.ps1`: the same Codex/Luna configuration is paired as `no-skill` versus a custom Skill directory containing only Practical Coding. FeatureBench and a standardized SWE-bench/Terminal-Bench harness remain broader coding-agent validity targets.
3. **Held-out layer** — keep a small private task set that is not read while editing `SKILL.md` or references. Rotate or refresh it from recent real PRs/bugs. Only this layer should be used for claims that a prompt iteration generalized beyond the public regression corpus.

## Task-authoring rules adopted here

The expanded public catalog follows these rules:

- prefer a new failure mechanism over another paraphrase of an existing prompt;
- each custom Debug case has a deterministic reported-caller check and a sibling/shared-boundary check;
- every custom Debug seed must fail and an oracle fix must pass before model calls;
- Router additions cover all six routes rather than concentrating on the last observed failure;
- Decision cases use two turns: first expose a real decision frontier, then provide enough facts to require convergence;
- `standard` is a bounded release gate while `full` contains the complete public regression matrix;
- stable rankings still require at least `n=3`; public 100% results are described as regression ceilings, not generalization proof.

## SkillsBench adapter status

Implemented in `benchmarks/external/skillsbench_adapter.py` with the canonical PowerShell entrypoint `benchmarks/run_external.ps1`.

The adapter:

- pins execution to the immutable `skillsbench@1.1` dataset through BenchFlow;
- keeps a `v1.1` SkillsBench metadata checkout only for category/roster selection;
- pins BenchFlow to `0.6.5`, a tested 0.6.x release whose CLI supports versioned datasets, `bench eval run`, custom `--skills-dir`, repeated `--include`, and reasoning effort;
- runs the benchmark oracle before model calls by default;
- compares `codex-acp` + `gpt-5.6-luna` + medium reasoning under `no-skill` and `with-skill` treatments;
- mounts only the current Practical Coding bundle in the treatment arm rather than each task's curated SkillsBench Skill;
- alternates arm execution order across repetitions;
- requires three complete paired repetitions for stable evidence;
- records raw BenchFlow jobs, the selected task roster, source/version pins, adapter hash, Skill bundle hash, and exact commands;
- reports pass-rate lift, mean-reward lift, pass flips, normalized gain, per-task rates, and task-cluster-bootstrap 95% confidence intervals.

This is intentionally described as a **Practical-owned ablation on SkillsBench**, not an official SkillsBench leaderboard row.

## Next external-validation milestone

After a stable SkillsBench software-engineering run is recorded, the next useful adapter is FeatureBench's fast/lite split for larger feature implementation and exploration behavior. That should preserve the same evidence discipline: fixed model/harness/reasoning, immutable dataset version or commit, paired no-Skill/Practical arms, oracle/gold validation, raw artifacts, and a stable repeated-run gate.
