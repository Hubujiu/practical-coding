# Retrieval integrity audit — 2026-09-04

Base revision: `942f0aa17bdac381ad50c544683c88e6320e6cf1`.

## What changed

The execution and Retrieval topologies, real-repository task prompts, task
oracles, provider versions, and historical results are unchanged. Core no longer
names a distant Retrieval stage. The Retrieval root has a small claim, stopping,
negative-evidence, and freshness contract. That wording is an experimental
candidate: this audit does not establish improved model accuracy or token cost.

The active **Retrieval runner** now freezes `run-plan.json` before measured
cells. Its fingerprint includes recursive Skill references, agent instructions,
benchmark Python/JSON sources, baseline contents, topology, manifest, model and
reasoning settings, timeout, Codex version, provider version observations, and
planned task/arm/repetition identities. Results and setup receipts must match.
Changed inputs or legacy unbound caches require a new output directory. The
runner also rejects source changes detected at the end of a run. Fingerprints
identify declared inputs; they are not tamper-proof execution attestations.

Analysis schema 2 changes `pass_rate` to successes divided by **all attempts**.
`determinate_pass_rate`, indeterminate counts, and timeouts remain separate.
Available costs from failed and timed-out attempts stay in arm aggregates;
missing fields are unknown, not imputed as zero. Pairwise cost deltas use the
same task and repetition only where both arms succeed, and are explicitly
labeled `costs_on_joint_passes`. They are not an overall cost-saving claim.

A minimum-sufficient stage requires complete, determinate, uncontaminated data
at every smaller ceiling. Missing or timed-out lower ceilings are unknown, not
failed ablations. The frozen plan detects even a repetition missing from every
arm. Duplicate, unexpected, misidentified, or setup-contaminated cells invalidate
the completeness gate. Without a plan, legacy analysis is descriptive only.
`comparison_evidence_complete` means the **planned matrix** is complete; it does
not mean an n=1/current-only run qualifies a release or proves statistical lift.

`tool_output_bytes` measures UTF-8 bytes of observed measured tool outputs. It is
not a token estimate, not necessarily Retrieval-only output, and not setup cost.

## Executed evidence

The audit used exact source snapshots checked against Git blob hashes, not a
complete local checkout. Python 3.13.5 on Linux ran 41 focused unit tests, the
analysis self-test, and syntax checks. One cache-boundary test mocks external
modules; it is not a provider integration test.

The evaluator regression benchmark executes the pinned original analysis module
and the modified module on the same 13 synthetic checks:

| Evaluator | Checks passed |
| --- | ---: |
| Original at the base revision | 4 / 13 |
| Modified analysis | 13 / 13 |

The four positive controls remain passing. Nine counterexamples cover missing
or indeterminate lower ceilings, duplicate/noncontiguous repetitions, setup or
provider-ceiling contamination, missing folds exposed by adaptive rows, timeout
success denominators, and timeout costs. This is **evaluator correctness**, not
13 coding tasks solved by an LLM. See the raw JSON in
`results/retrieval-integrity-2026-09-04/evaluator-regression.json`.

No model benchmark was executed: this environment has no `codex`, `zg`,
`codebase-memory-mcp`, or `rtk`; Maven is also absent for the Java repository.
There is no new n=1/n=3 model score, routing-accuracy score, provider-performance
measurement, or token-saving percentage. The dependency-enabled profile must
continue to fail closed rather than substitute mocks or dependency-free search.

## Reproduce evaluator checks

From a full repository checkout with the base revision available:

```sh
python -m unittest benchmarks.test_retrieval_analysis benchmarks.test_retrieval_integrity
python benchmarks/retrieval_analysis.py --self-test
python benchmarks/benchmark_retrieval_integrity.py --output benchmark-results/retrieval-integrity.json
```

An offline exact snapshot can be supplied with
`--baseline-analysis /path/to/original/retrieval_analysis.py`. The benchmark
verifies its Git blob hash before executing it. Historical results are not edited.

## Run actual Skill evaluation

First provision the pinned providers and repository checkouts specified in
`capability_manifest.json` and `tree_cases.py`, plus the authenticated Codex CLI.
Do not commit credentials. Existing provider/index/dependency/build preparation
remains before measured execution and outside compared tokens, duration, and
tool calls. Each arm receives the same required initialized capabilities.

```sh
# Iteration screen, not release evidence.
python benchmarks/retrieval_validation.py --runs 1 --current-only --output benchmark-results/retrieval-integrity-n1

# Only after freezing a candidate: full paired comparison against this audit's base.
python benchmarks/retrieval_validation.py --runs 3 --baseline-ref 942f0aa17bdac381ad50c544683c88e6320e6cf1 --output benchmark-results/retrieval-integrity-n3

python benchmarks/retrieval_analysis.py benchmark-results/retrieval-integrity-n3/results.jsonl --require-complete --output benchmark-results/retrieval-integrity-n3/analysis.json
```

Reuse an output directory only to resume the identical frozen experiment. A new
candidate, model, provider version, timeout, or task matrix needs a new directory.
An incomplete or indeterminate matrix exits nonzero; an observed task failure is
still a valid measurement, not missing data. Completeness is necessary but not
sufficient for a quality-qualified release. Inspect paired correctness and
safety before comparing cost, and revert the wording if it adds no net value.

## Remaining limits and next priority

The historical execution-tree wrapper is not migrated to this new cache contract.
Its results must not be assumed to have the Retrieval runner's identity checks.
Reference/provider observations still partly infer use from command text, not
successful typed read events. A command mentioning a path is not proof that its
contents were read. The historical transcript parser can also initialize missing
usage to zero; absence of token telemetry must not be presented as measured
savings. These require separate, frozen telemetry work rather than invented data.

The next model experiment should measure bounded source reads, repeated queries,
missing evidence, and delivered correctness on the same paired tasks. Do not add
a node, a provider, automatic Decision, or execution-state to make the tree look
more elaborate.
