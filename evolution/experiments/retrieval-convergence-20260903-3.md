# Retrieval convergence — iteration 3: reuse successful source evidence

Status: candidate-not-applied

## Frozen hypothesis

- Baseline SHA: `c3512a000da2916d1b6482beb95430c51f00a646`; runtime is unchanged from original remote `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`. A documentation-only hypothesis commit may be the actual baseline run HEAD; preserve its manifest.
- Evidence: accepted-runtime baseline and rejected candidate in `benchmark-results/retrieval-iteration-2-{baseline,candidate}-n1/`, reviewed without changing their artifacts. The prior 1.2/1.3 offline observations are diagnostics only; this iteration runs a fresh matched baseline.
- Repeated mechanism: baseline executor event 4 returned 1,370 numbered lines; later events 5, 6 and 9 reread 464 of those lines (27,323 bytes, three extra calls). Baseline memory-reset searches reread source already returned by earlier reads/searches (56,007 identifiable numbered-line bytes across events 4/6/7/8/9/10). In the rejected sensitive-content candidate, two per-hit loops emitted 67,798 duplicate numbered bytes within the same calls. This is evidence reuse/overlap failure across different source questions, distinct from the rejected mandatory filename-first round.
- Transfer limit: baseline sensitive-content archive reads had almost no detected overlap. Its broad initial output may remain expensive. The proposal is falsifiable and is not presumed to improve every high-output task.
- Causal claim: reusing successfully returned unchanged source and merging overlapping windows removes repeated output and extra context-replaying tool rounds while preserving new contract/caller/test facts. There is no extra locating stage or runtime bookkeeping service.
- Observable trigger: a requested source range overlaps evidence already returned successfully, or multiple context windows overlap in one source query.
- Exact modified file: `SKILL.md`, Retrieval Policy only. Append the following sentence as its own paragraph immediately after the existing paragraph beginning “Once candidate paths or symbols are known”.
- Exact candidate rule: **Read each unchanged source range once: merge overlapping context windows, reuse successfully returned source, and fetch additional ranges only to resolve an uncovered contract, caller, or test question; reread when source changed or the earlier output was incomplete.**
- Unchanged: all other Skill text/references, tree topology, automatic/manual nodes, cases, answer scorer, model, frozen runner/observer, dependencies/fixtures, and required verification. Execution-state/history-free remains retired.
- Expected quality: no loss in delivery, diagnosis correctness, authoritative ownership/recovery contracts, caller coverage, required tests, trace legality or manual discipline. A repeated snippet may be omitted only if it is still available and complete; an uncovered fact still requires retrieval.
- Expected cost: frozen-tail paired median output reduction >=30%, input reduction >=10%, with no required overhead or mechanism regression.
- Falsifier: repetition is only moved into other commands; fewer bytes do not reduce cumulative input; an earlier large dump is reused despite missing/incomplete evidence; a necessary contract/caller/test fact is skipped; or any mandatory gate fails. Do not reword this candidate after seeing its results.

## Frozen benchmark and procedure

- `gpt-5.6-luna`, reasoning medium, tree harness 1.0, observation 1.3, Codex CLI 0.145.0, Python 3.13.14; source fixture commits remain the original three in `tree_cases.py`. Preserve complete manifests/hashes and reject any unexplained identity drift.
- n=1: all 54 current-only cells, runs 1, timeout 600 seconds, eight concurrent isolated shards of at most five cells each. Identical shard assignment and build conditions in both arms; fresh directories, no retry/resume or selective result replacement.
- Baseline: `benchmark-results/retrieval-iteration-3-baseline-n1/`; candidate: `benchmark-results/retrieval-iteration-3-candidate-n1/`.
- Freeze the three highest-output ordinary adaptive baseline tasks before applying the candidate, including exact results and audit hashes. Do not replace the tail after seeing candidate results.
- Require 100% expected cells, determinate verdicts, no timeout/scorer crash, complete usage, no shell decoding gaps and >=99% measured completed outputs. Audit high-output unknown events and all tail convergence attribution that could affect a gate. Both source-content search and direct reads count as source evidence under the pre-frozen event-level audit contract in `retrieval-continuation-20260903.md`.
- Automated pass counts are necessary but insufficient. The executor quality boundary includes whether uncaught `Error` retention and startup recovery are intentional contracts rather than an unsupported claim that every nonterminal status is a bug. Preserve concrete source/test evidence; no case or scorer edit.

## n=1 gates

1. Complete comparable infrastructure and audited attribution as above.
2. No paired quality regression in adaptive or any required ceiling; all traces legal; explicit manual correct; spontaneous manual zero; clean fixtures; necessary correctness/caller/contract/test evidence retained.
3. Frozen tail median paired `tool_output_bytes` ratio <=0.70. Audited broad calls after returned project source evidence <=50% of baseline; baseline zero requires candidate zero. Tail totals of duplicate commands, whole-file bytes, dependency-source bytes and >64 KiB outputs do not increase. Preserve automatic estimates and audited receipts separately; command spelling alone cannot earn a pass.
4. Tail median input-token ratio <=0.90; tail uncached-input total no increase; all 54 paired input-token median ratio <=1.02; all-cell tool-call median ratio <=1.00. Zero-to-positive values are regressions, never dropped pairs.

Duration is telemetry only. No latency gate or separate serial latency rerun.

## Frozen n=3 qualification and acceptance

Only if every n=1 gate passes: commit the exact candidate, record its full SHA, and run the complete existing paired n=3 matrix (252 cells, 51 shards, at most eight concurrent shards, same timeout/model/reasoning/fixtures/observer). Compare adaptive against this immediate baseline and the required no-skill boundary. All cells must be determinate, quality non-decreasing, traces/manual discipline valid, and necessary evidence preserved. Tail cost uses nine matched adaptive/baseline pairs; all-task cost uses 45 pairs. Apply the same output/input/tool thresholds and tail non-increase counters; improvement must persist in at least two repetitions and more than one tail task. No cached-token or timing substitution.

On failure, preserve the raw complete matrices and rejected patch, restore `SKILL.md` to this baseline, and record the outcome before considering a different independent hypothesis under the user's reopened-loop authorization. Never relax thresholds, delete cases, tune the scorer or keep this rejected rule active. On full passage, update wiki/impact/log, save a sanitized report, commit/push/verify the result and stop successfully.

## Results (outside the frozen hypothesis)

- Fresh sharded baseline complete: 54/54 determinate machine passes, all 54 traces legal, explicit manual 2/2, spontaneous manual zero, no dirty fixture or timeout; all 393 completed tool outputs measured, no decoding/usage gap. Actual run HEAD `eead15a43ee486d961821c9b0b3bdfded4c53295`.
- Frozen tail: `sa-sensitive-rejection-boundary` (1,547,000 bytes), `sa-memory-reset-concurrency` (1,092,290), `pp-running-after-throw` (358,600), selected before candidate application. Full result/gate/audit hashes are in `retrieval-convergence-20260903-3-baseline.json`.
- Tail attribution audits are complete. First project source is event 2 in all three cells. Audited broad-after-read counts are 0/1/0. Audited whole-file and dependency attribution retain full output bytes for mixed operations; raw automatic estimates are preserved separately. No non-tail unknown category output exceeds 16 KiB.
- Supplemental manual quality: sensitive-content and memory-reset pass. The executor answer accurately distinguishes Error and RuntimeException, but omits the intended crash marker and startup recovery contract despite receiving that evidence. Its machine pass is retained as a limited oracle result, not treated as proof of full correctness. The candidate must satisfy the manual completeness criterion already frozen above, in addition to no automated regression; this does not change cases, scorer, thresholds or baseline answers.
- The non-time gate arithmetic and baseline audit hashes were frozen before candidate application. Candidate pending.
