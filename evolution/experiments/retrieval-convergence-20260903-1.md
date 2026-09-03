# Retrieval convergence — iteration 1: observation only

Status: **Inconclusive — infrastructure_indeterminate; loop terminated**

Original frozen status: `candidate-not-applied`. The original hypothesis and thresholds below are unchanged.

## Frozen hypothesis (before implementation)

- Baseline SHA: `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`, matching fetched `origin/experiment/evolvable-router-tree`; initial worktree clean.
- Branch: `experiment/retrieval-convergence`.
- Original artifact: `benchmark-results/tree-final-b202f7a-20260902/results.jsonl` and its original `cells/**/round1.jsonl`; historical evidence only, not the current baseline.
- Evidence: adaptive `sa-sensitive-rejection-boundary` recorded 1,231,438 and 813,360 input tokens, with early broad outputs of 126,987 and 1,048,576 bytes; `sa-memory-reset-concurrency` recorded 602,872 input tokens and a 1,048,576-byte early search. These observations justify measurement, not a global runtime rule.
- Causal mechanism: aggregate usage cannot attribute long-tail cost to retrieval output or detect renewed discovery after project inspection. Pure offline metadata can expose that mechanism without changing model inputs or quality verdicts.
- Observable trigger: completed tool events in the existing JSONL transcript; classification uses command/tool shape and frozen repository paths, never case IDs or answers.
- Exact files: new `benchmarks/retrieval_metrics.py`, `benchmarks/retrieval_analysis.py`, `benchmarks/test_retrieval_metrics.py`; metadata-only integration in `benchmarks/tree_validation.py`; this record and maintenance wiki outcome.
- Candidate rule: record ordered output size/lines/hash, command identity, categories, duplicates, large outputs and prior source candidate/read indicators; aggregate separately from quality. Store raw output only in its original transcript. Record measurement gaps and mixed-command attribution explicitly.
- Unchanged: runtime Skill and references, topology, cases, answer scorers, model request construction, retired execution-state files, historical artifacts.
- Expected quality: byte-identical prompts and unchanged scorer inputs/verdicts. No quality claim from instrumentation itself.
- Expected cost: no runtime savings; expose recorded output volume, not undocumented model-visible or pre-truncation bytes.
- Falsifier: metadata changes quality/prompt behavior, classifies from task labels, duplicates raw output, hides unavailable output/usage, or cannot distinguish general positive/negative command examples.

## Frozen evaluation

- Harness: repository `tree_validation.py` 1.0 / `run_benchmarks.py` 2.0; Codex CLI 0.145.0; Python 3.13.14; Windows; model `gpt-5.6-luna`, reasoning `medium`, timeout 600 seconds.
- Case set: current `tree_cases.py`, all 15 cases; current-only is **54** cells (13 ordinary x 4 arms + 2 explicit manual), repetitions 1, workers 1. Full frozen n=3 would be 252 cells, workers 8; tail latency workers 1.
- Frozen fixtures: personal-progress `515c2e2193c3d547e04e65687da6666dc877ab61`; cover-atelier `fc3b12b3a944f45b5a1d19963e29307d95b120fb`; super-agent `d44edf063032a2d8797549411f11923aa4a83ec3`.
- Baseline deterministic evidence before candidate: 32 existing tree tests pass; tree self-test passes. All three frozen fixture commits locally available. Scorer/source hashes will be captured in the instrumentation manifest before model execution.
- Instrumentation acceptance: general positive/negative unit tests, prompt/scorer noninterference test, existing tree tests and self-test; replay historical transcripts into a **new** analysis directory without altering originals. Commit/freeze instrumentation before any model baseline/candidate comparison.
- n=1 model baseline after instrumentation freeze: fresh `benchmark-results/retrieval-iteration-1-baseline-n1`; no runtime candidate in this iteration. All expected cells determinate, no timeout/scorer crash, identity and output coverage auditable. Infrastructure failure stops the loop before a Skill candidate.
- n=3: not applicable to pure instrumentation; no stable cost claim. A later independent runtime hypothesis must freeze all user-specified quality, tail/output/token/tool/latency thresholds unchanged, qualify at n=1, then complete paired n=3.
- Rollback: revert instrumentation if it affects prompt/scoring or fails deterministic measurement contract. Preserve original transcripts. Never apply runtime edits in iteration 1.
- Continue only after this iteration is accepted and a fresh baseline reveals a repeated, independently testable retrieval mechanism. Otherwise stop `no_action` or infrastructure-indeterminate as appropriate. This iteration counts toward the maximum of three.

## Results (append-only after freeze)

- Instrumentation deterministic candidate: 41 tests passed (9 new retrieval tests and 32 existing tree tests); tree self-test passed. Integration test compares original record fields, scorer arguments, and prompt bytes with metadata enabled/disabled.
- Historical replay: `benchmark-results/retrieval-iteration-1-instrumentation-replay/`; 252 records, every original result field unchanged. Original results SHA-256 `fdba2d83ef600fb5e541f2e302b0a9ee7dc063e6a249cf740cba4949fb07776c`.
- Coverage: 1,844/1,845 completed tool events have recorded output; 252 commands classified `other`, 421 have overlapping mixed categories, 41 possible truncations. These limitations remain explicit; byte counts do not claim untruncated/model-visible output. Duplicate identity is conservative normalized syntax; semantic-equivalence claims require command review.
- Decision: **Accepted — instrumentation only**. No runtime quality or cost improvement claimed. Instrumentation must be committed before the fresh current-baseline n=1 below; the runtime Skill remains byte-identical to the remote starting baseline.
- Next action: run the frozen current-only baseline to decide whether a separately frozen iteration 2 is justified. Any model/auth/fixture failure stops the entire loop.

## Fresh baseline invalidates gate readiness

- Frozen instrumentation commit: `6475c33cca967ffafadf09ee484ed84e2feb49a7`, pushed to `origin/experiment/retrieval-convergence` before termination.
- The earlier deterministic/replay acceptance is **withdrawn as a cost-gate readiness claim**. It remains evidence of additive metadata and unchanged old verdicts only.
- Fresh baseline artifact: `benchmark-results/retrieval-iteration-1-baseline-n1/`; identity in `manifest.json`, completed records in `partial-results.jsonl`, exact missing cells in `termination.json`, original cell transcripts retained. This is an interrupted diagnostic, not a complete baseline matrix.
- Completed: 4/54 determinate, 4 quality passes and 4 valid traces; 50 missing cells, including an interrupted fifth cell. No explicit manual case completed, so manual-mode completeness remains unverified. Completed spontaneous manual count is zero.
- Recorded output: 5/5 completed tool events measured, but 3/5 categorized `other`. Two source reads in the Core/Debugging ceiling cells were missed because CLI shell rendering used differently quoted fragments at the beginning/end of `-Command`. Their source-read flags and whole-file byte totals are therefore wrong. Complete byte coverage does not prove category or convergence coverage.
- The first adaptive cell recorded 5,958 bytes, 26,212 input tokens, 14,180 uncached input tokens, one tool call and 26.57 seconds. There is no candidate pair, frozen tail set or cost result.
- Action: stop the benchmark runner and its descendants; preserve all raw artifacts and the frozen instrumentation unchanged. No selective rerun, classification repair against these results, runtime patch, iteration 2 or n=3 was attempted.
- Decision: **Inconclusive / infrastructure_indeterminate**. The instrumentation remains diagnostic and must not gate acceptance in its current version. Rejection/limitation record: `evolution/rejected/retrieval-instrumentation-20260903.md`.
- Stop condition: n=1 measurement coverage is insufficient for the principal convergence metrics; the baseline artifact is incomplete and cannot establish the required gates. The user's infrastructure-stop rule takes precedence over starting another candidate.
- Runtime rollback: no Skill candidate was applied. `SKILL.md`, all `references/`, topology and cases are unchanged from `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`; AST comparison also confirms unchanged scoring, prompt construction and trace validation functions.
- Future prerequisite: independent general shell-rendering fixtures and explicit classification coverage checks are needed before a new frozen instrumentation evaluation. This is not evidence against prompt-only retrieval convergence itself.
