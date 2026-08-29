# Coding-agent and Agent-Skill benchmark landscape

Date: 2026-08-24

This note separates project regression tests from external benchmark evidence. Public regression cases are useful for preventing known failures from returning, but repeated prompt iteration against them eventually makes them unsuitable as evidence of generalization.

## Most relevant public projects

| Project | What it measures | Dataset / repetition shape | Why it matters to Practical Coding |
|---|---|---|---|
| [langchain-ai/skills-benchmarks](https://github.com/langchain-ai/skills-benchmarks) | Skill documentation layout, treatment A/B, split/merged Skills, distractor/noise effects | Docker tasks decoupled from treatments; repeated pytest runs; trajectory logging | Strong reference for treatment design and testing routing/interference rather than only final task success. |
| [SWE-bench Verified](https://www.swebench.com/verified.html) | Real GitHub issue resolution | 500 human-filtered issues; public agent leaderboard plus a standardized mini-SWE-agent view | Canonical external coding-agent signal. Useful for testing whether Practical improves a neutral coding harness, but less specific to Skill design. |
| [Terminal-Bench](https://github.com/harbor-framework/terminal-bench) | Long-horizon terminal-agent work | Continuous tagged dataset releases; containerized tasks; oracle solutions; leaderboard; oracle is recommended to run 5x | Strong model for benchmark operations: version datasets, continuously validate tasks, keep oracle checks, and treat benchmark maintenance as a product. |
| [FeatureBench](https://github.com/LiberCoders/FeatureBench) | End-to-end feature development | 200 full tasks, 100 fast tasks, 30 lite tasks; executable environments and an open data-generation pipeline | Useful external evidence for Implementation/Exploration behavior because tasks span larger feature surfaces than bug-only benchmarks. |
| [Senior SWE-Bench](https://senior-swe-bench.snorkel.ai/) | Senior-level design/build and investigate/fix behavior from realistic messages | 100 initial tasks: 50 public and 50 private; recent real PRs; behavioral verification and quality gates | Best reference for contamination control and realistic debugging prompts. The private half is especially relevant once Practical's public regression set is used for prompt iteration. |
| [ProgramBench](https://programbench.com/) | Rebuilding complete programs from behavioral contracts | 200 tasks and a large hidden behavioral-test suite | Useful as a hard design/implementation ceiling, but less directly targeted at a procedural coding Skill. |

## Evidence model for Practical Coding

Use three layers instead of one leaderboard number:

1. **Public regression layer** — Router, Decision, Debug and the Ponytail-derived Delivery tasks in this repository. These should stay deterministic and are allowed to encode previously observed failures. Their job is to prevent regression, not prove unseen-task generalization.
2. **External benchmark layer** — run the Skill as an augmentation treatment on an independently reproducible public suite. FeatureBench and standardized SWE-bench/Terminal-Bench harnesses are possible future coding-agent validity targets; none is currently part of the published release evidence.
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

## Next external-validation milestone

Only add another external adapter after it is reproducible in the supported environment. A future FeatureBench fast/lite experiment could cover larger feature implementation and exploration behavior while preserving the same evidence discipline: fixed model/harness/reasoning, immutable dataset version or commit, paired no-Skill/Practical arms, oracle/gold validation, raw artifacts, and a stable repeated-run gate.
