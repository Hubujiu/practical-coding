# 2.1-rc1 delivery readiness

Baseline: `6cf43d758d6f99aa051153edea67d5ac533acfe7`. This is a candidate,
not a claim of measured model lift. Acceptance numbers below are engineering
targets, not forecast observations. No model-performance rows are manufactured.

## Runtime changes

The local execution and Retrieval topologies are unchanged. Core, Debugging,
Implementation, Navigation, manual modes, delegation, and the default prompt
were shortened without adding a mandatory workflow. `AGENTS.md` points to the
runtime authority instead of repeating its complete routers. Explicit-only
manual activation, no speculative abstraction, minimal sufficient verification,
read-only boundaries, and truthful evidence remain.

A located target with insufficient evidence now has a path out of Direct Locate.
Discovery keeps a known location rather than searching for it again; Evidence
can request structural tracing before reconstructing an entire graph manually.
Every transition still loads only the immediate child. Already-loaded guidance
is reused. The root does not select distant descendants or providers.

The checked-in hypothesis precedes these runtime edits. Static size changes
are measured by `benchmark_readiness.py`; they are not model input-token savings.

## Active runner, not historical adapters

`retrieval_validation.py` now owns both `--axis retrieval` and `--axis execution`.
`dependency_tree_validation.py` delegates to the latter, without monkey-patching
the historical runner. Historical scripts/results remain for provenance, not
release certification. The active command defaults to n=1, one worker, a fixed
randomization seed, and an explicit baseline for paired comparisons.

The source suite retains its 15 real-repository cases across three repositories.
Its source/report oracle is largely lexical with successful executable probes
where requested; it does NOT certify arbitrary code delivery. Eight additional
public Python fixtures perform real code changes with independent executable
assertions: public entry, shared parser, path confinement, transaction rollback,
reservation race, backward-compatible status, async cancellation, and permission
rejection before side effects. These are controlled regression cases, NOT a
held-out suite or proof of broad language coverage.

No expected automatic route is assigned to a case. Capability ceilings diagnose
minimum sufficient disclosure. `--comparators-only` instead runs the identical
adaptive/baseline/no-skill task matrix without paying for all ceilings.

All profiles still require the pinned ranked, graph, and output providers.
Python delivery fixtures use an explicitly named warmup profile, not missing-
provider fallback. Provider setup, first indexes, model downloads, dependencies,
and first build warmup finish before the measured process begins. Measured
self-install/setup attempts are contract violations. Normal runtime can still
use native-source fallback when a provider is unavailable.

## Evidence and isolation

Candidate/baseline snapshots, harness sources, model/reasoning, versions, selected
cases, repetition schedule, platform, workers, timeout, and manifest are frozen.
Changed experiments need a new output directory. Cached cells bind raw prompts,
JSONL, stderr, setup receipts, and archived delivery submissions. Aggregates must
match cell records. The release gate re-parses usage and replays delivery oracles
from archived code. These are integrity checks, not cryptographic execution
attestations against a malicious host or contestant.

Tool attempts are counted once by event identity, including incomplete attempts.
Success requires a completed event and its actual successful exit/result. A
printed command/provider/path is not a successful invocation. Credited policy
reads require recognized readers, successful events, and matching frozen source
content. Unsupported readers are unverified, not silently successful. This is a
conservative protocol: novel host transports need adapters/tests; it cannot prove
all possible file accesses. Compound exit status does not establish every
provider/probe succeeded. Missing usage is null/unknown; explicit observed zero
is distinct. A completion-looking line never overrides a timeout or failed turn.

CODEX_HOME is isolated and supports existing CLI auth or an API-key environment.
Credentials are never included in plans or artifacts. Run model evaluation only
in a disposable, trusted environment: the existing Codex command intentionally
bypasses sandbox/approval prompts for benchmarks and is NOT a containment boundary.
Do not expose production secrets or unrelated writable checkouts. Never publish
an eval-home or authentication file. Public CI runs deterministic checks only.

## Engineering acceptance targets — not measurements

The checked-in `release_targets.json` is the authoritative, fingerprinted target.

| Suite | Tasks | Arms | Repeats | Total cells | Candidate floor |
| --- | ---: | ---: | ---: | ---: | ---: |
| Real-repository source analysis | 15 | 3 | 3 | 135 | 44/45 |
| Executable code delivery | 8 | 3 | 3 | 72 | 24/24 |
| Total | 23 | 3 | 3 | 207 | At least 68/69 |

These small public regression tasks use strict floors rather than a broad
claimed percentage for general coding ability. Additionally, candidate pass count cannot be lower than either comparator in
either suite. All 15 candidate attempts on the five safety-critical delivery
tasks must pass. Require zero spontaneous manual activation, invalid routing
traces, missing required telemetry, incomplete cells, and setup contamination.
Source and delivery must use the same candidate, harness, baseline, model,
reasoning, platform and provider versions.

On matched joint-success pairs (at least 10 per suite), uncached input tokens
must not exceed baseline; elapsed time/tool calls may rise at most 5%. Against
no-skill, the corresponding overhead limits are 10%. These are engineering
tradeoffs, not confidence intervals. Report all-attempt costs and quality too;
joint-success costs alone have selection bias and are not total cost savings.

An aspirational target is 5–15% fewer uncached input tokens and 0–10% less elapsed
time versus baseline. It is NOT a measured/predicted result, a release guarantee,
or a substitute for the gate. The only direct size claim is file bytes. A
smaller prompt may still lead to more tool output or model reasoning.

Even a passing gate requires human review and further independent held-out,
language/host-diverse tasks. n=3 repeated runs of 23 public tasks do not prove
statistical non-inferiority on general software engineering.

## Reproduce deterministic evidence

```sh
python -m unittest benchmarks.test_measured_transcript benchmarks.test_measured_process benchmarks.test_delivery_cases benchmarks.test_active_runner benchmarks.test_release_gate
python benchmarks/benchmark_retrieval_integrity.py --output benchmark-results/evaluator-regression.json
python benchmarks/benchmark_readiness.py --output benchmark-results/readiness.json
```

The readiness script runs flawed and reference implementations through the
same independent oracles, not through a simulated model. Its report marks
`model_executed: false`. The CI workflow also runs all existing unit/contract tests
and publishes tracked source plus deterministic results as auditable artifacts.

## Run real model evaluation

Install the pinned providers in `capability_manifest.json`; provision the source
checkouts/commits from `tree_cases.py` and authenticated Codex. Configure a model
actually available to the account with `--model` and `--reasoning` consistently
across suites. The historical default is retained, not silently replaced. An
unavailable model/provider blocks the run; do not generate synthetic substitutes.

```sh
# No dependencies/model required: display dimensions only.
python benchmarks/retrieval_validation.py --suite source --runs 3 --comparators-only --describe
python benchmarks/retrieval_validation.py --suite delivery --runs 3 --comparators-only --describe

# Current-only iteration screen; no release ranking claim.
python benchmarks/retrieval_validation.py --suite delivery --runs 1 --current-only --output benchmark-results/rc1-delivery-screen

# Freeze the candidate before these paired runs. Set the same available model
# and reasoning explicitly in both commands when overriding historical defaults.
python benchmarks/retrieval_validation.py --suite source --runs 3 --comparators-only --baseline-ref 6cf43d758d6f99aa051153edea67d5ac533acfe7 --output benchmark-results/rc1-source
python benchmarks/retrieval_validation.py --suite delivery --runs 3 --comparators-only --baseline-ref 6cf43d758d6f99aa051153edea67d5ac533acfe7 --output benchmark-results/rc1-delivery

python benchmarks/release_gate.py --source benchmark-results/rc1-source --delivery benchmark-results/rc1-delivery --output benchmark-results/rc1-gate.json
```

The gate exits 2 for not-run, incomplete or failing evidence. Calling it without
run directories prints targets with `status: not_run`; it never turns targets
into measured results. A code/scorer change requires new runs on both arms.
Use `dependency_tree_validation.py` for execution ceilings or omit
`--comparators-only` for Retrieval ceilings; these diagnostic runs do not replace
the 207-cell release matrix.

## Status of this revision

Deterministic checks can establish prompt byte reductions, parser and cache
invariants, oracle discrimination, process timeout handling, and gate behavior.
No authenticated model/provider comparison was available during this revision.
Therefore model correctness, routing behavior in actual sessions, total token
savings, runtime savings, and generalization remain unmeasured. The shipped
artifact is a testable release candidate, not an empirically certified release.
