# Practical Coding benchmark chain

## Active 2.1-rc1 entry points

| Entry | Purpose |
| --- | --- |
| `retrieval_validation.py` | Shared dependency-enabled source/delivery runner with Retrieval or execution ceilings |
| `dependency_tree_validation.py` | Compatibility entry selecting the execution axis; no global monkey patches |
| `release_gate.py` | Complete paired engineering gate with raw-evidence checks and replayed code oracles |
| `benchmark_readiness.py` | Prompt-byte comparison and known-bad/reference-code oracle controls, not model scores |
| `benchmark_retrieval_integrity.py` | Pinned old-versus-current evaluator regression checks |

[DELIVERY_READINESS.md](DELIVERY_READINESS.md) is the current command and evidence contract. [release_targets.json](release_targets.json) contains unmeasured engineering targets. Running a gate without measured directories returns `not_run`, not a generated score.

## Experiment design

Execution and Retrieval are independent local trees. Current execution leaves are Debugging and Implementation. Retrieval progresses through Direct Locate, Ranked Discovery, Evidence Expansion, and Structural Trace. No task encodes a gold automatic node; capability ceilings determine minimum sufficient disclosure through measured ablation. Manual activation is explicit-only.

The source suite preserves 15 frozen real-repository analysis tasks. Its largely lexical/source oracle and requested successful probes do not certify code delivery. The delivery suite adds eight public Python change tasks with independent post-run executable assertions. These public regressions are not held-out generalization evidence.

The full engineering comparison is 23 tasks × three arms × three repetitions = 207 cells. `--comparators-only` selects adaptive/baseline/no-skill without diagnostic ceilings. Use n=1 for iterative screening; only a frozen candidate receives the repeated full comparison. Changes to prompts, scorer, model, provider versions, or task matrix require new output directories and new paired evidence.

## Required capabilities and measurement boundary

[capability_manifest.json](capability_manifest.json) pins ranked search, graph retrieval, and output compaction providers. All three are required for every measured profile, including the explicitly named Python delivery-fixture profile. There is no allow-missing mode. Normal runtime fallback remains separate from benchmark capability requirements.

Setup installs no model-facing prompt and ends before measured execution: provider probes, model assets, indexes, dependency resolution, and first test/build warmup. Setup receipts are retained separately and excluded from compared tokens, duration, and tool calls. No setup token estimate is used. Measured setup attempts are violations.

Missing usage is unknown rather than zero. Failed and timed-out attempts remain visible. A printed command is not a successful probe; policy reads need successful reader events and matching current content. Candidate/baseline snapshots, model/reasoning, harness, settings, schedule, and raw artifacts are identity-bound. Cached results require matching receipts; aggregate data must match each cell. The release gate replays submitted-code oracles from archived source.

Cost reports distinguish all attempts from matched joint successes. Joint-success comparisons have selection bias and are not overall cost savings. n=3 repeats of a public task are not independent tasks and do not prove statistical non-inferiority.

## Reproduction

```sh
# Deterministic controls, no model or external providers required.
python benchmarks/retrieval_validation.py --self-test
python benchmarks/dependency_tree_validation.py --self-test
python benchmarks/benchmark_retrieval_integrity.py --output benchmark-results/evaluator.json
python benchmarks/benchmark_readiness.py --output benchmark-results/readiness.json

# Planned dimensions only.
python benchmarks/retrieval_validation.py --suite source --runs 3 --comparators-only --describe
python benchmarks/retrieval_validation.py --suite delivery --runs 3 --comparators-only --describe
```

For actual runs provision authenticated Codex, the pinned providers, and source repositories/commits from `tree_cases.py`. Use the full paired commands in [DELIVERY_READINESS.md](DELIVERY_READINESS.md). Supply the same available `--model` and `--reasoning` across suites; unavailable models must fail rather than be silently substituted.

Run only in a disposable trusted environment. The unattended Codex command is not a security containment boundary. Keep production secrets, unrelated writable checkouts, authentication files, and eval-home out of public artifacts.

## Historical evidence

Existing task cases, results, prior comparisons, and rejected experiments remain immutable evidence, not current release certification. Historical scripts such as `tree_validation.py`, `run_benchmarks.py`, and the retired monkey-patch adapter still explain old reports; use the active entry points above for new measurements. `retrieval_analysis.py` and `tree_analysis.py` provide diagnostic topology analysis; those reports do not replace the complete engineering gate.

The earlier [Retrieval integrity audit](RETRIEVAL_INTEGRITY.md), [reproduction notes](REPRODUCING.md), and [tree evolution](TREE_EVOLUTION.md) describe their own historical contracts. Where commands differ, the active readiness document takes precedence. Never rewrite old results after a scorer change; invalidate the comparison and rerun both arms.
