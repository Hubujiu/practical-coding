# Retrieval loop continuation under the user's updated instructions

Status: active maintenance protocol; no runtime candidate applied by this document.

The user explicitly reopened the previously terminated loop: “你自己思考如何改进，然后重跑评测，直到能够成功交付。” This supersedes the prior three-iteration/two-rejection/cost-stop limit for continued independent investigation. It does not turn a failed candidate into a pass or authorize a scorer/threshold change. Retain the previous completed two-iteration record and continue numbering from iteration 3.

- Starting branch: `experiment/retrieval-convergence`, clean and matching fetched origin at `ed522d538e618c0e7f2804304939732a5ff6280f`.
- Original target `experiment/evolvable-router-tree` remains `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`.
- Tests run silently until completion. Duration is telemetry only and has no acceptance threshold. Work units contain at most five model cells, with eight concurrent isolated shards initially; baseline and candidate use identical shard allocation/concurrency. Do not selectively retry or replace results.
- Every runtime hypothesis is frozen before its candidate is applied or evaluated. Run a fresh complete baseline first, select the top three ordinary adaptive output cases from it, and freeze that tail before candidate execution. Rejected runtime patches are fully rolled back before the next hypothesis.
- No changes to cases, answer scorers, automatic nodes, manual modes or Router topology. Retrieval remains orthogonal. No execution-state/history-free restoration and no new runtime retrieval framework.
- Freeze pure runner/observation changes before baseline/candidate. Sharding must preserve existing `run_cell`, task prompts, scorer and exact cell coverage. Observation 1.3 adds explicit attribution uncertainty, retaining measured bytes and previous estimate semantics; flagged convergence counts cannot establish acceptance without audit.

## Non-time acceptance gates

For n=1, use all 54 current-only cells: 15 adaptive plus three ceilings for each of 13 ordinary cases. Require complete/determinate matching matrices; no timeout, scorer crash, missing usage or unexplained major output; no paired quality regression; all traces legal, explicit manual correct, spontaneous manual zero and clean fixtures. Review necessary caller/contract/test evidence where automated quality is insufficient. A real factual error cannot be accepted because the scorer passed it.

The baseline's three largest ordinary adaptive output tasks form the frozen tail. Require paired median output ratio <=0.70; broad calls after project source evidence reduced by at least half; no increase in duplicate command count, whole-file bytes, dependency-source bytes or >64 KiB events. A zero baseline broad count requires candidate zero and supports no positive reduction claim. Non-increase counters use matched tail totals, with per-cell values retained.

Require tail paired median input-token ratio <=0.90, tail total uncached input no higher, all 54 cells' paired median input-token ratio <=1.02 and paired median tool-call ratio <=1.00. Do not substitute cache fluctuations, output bytes or duration for reduced input work.

Only complete n=1 passage qualifies a committed frozen runtime candidate for the full existing paired n=3 matrix: 252 cells, original model/reasoning/fixtures/scorer, including immediate baseline and no-skill. Require all cells determinate, adaptive quality no lower than either comparator, legal traces, correct explicit manual and no spontaneous manual; required caller/contract/safety/test coverage must survive. For cost, compare current adaptive with immediate baseline (the legacy variant label is `v1.5`, but the actual supplied baseline SHA is authoritative): all 45 task/repetition pairs for ordinary fixed overhead, and nine pairs for the frozen three-task tail. Preserve the same output/token/tool thresholds, non-increase counters, improvement across at least two repetitions and more than one tail task. The separate serial latency run is unnecessary because duration is no longer judged.

## Auditable convergence semantics

Raw automatic counters are retained as command-shape estimates. Before accepting a tail gate, audit flagged and mixed events against returned output and command scope, preserving event IDs/output hashes and an explicit decision in a separate receipt. A project source read means returned project implementation evidence, including source lines from content search; it does not depend on spelling `Get-Content` versus `rg`. Filename inventory alone is not source content. An event is after the first read when an earlier completed event returned source evidence; same-event operations are not retroactively treated as model-observed evidence. Partial success can establish a read only when actual returned source proves it, not from exit status alone. Classify broad scope and whole/dependency reads by the actual operation, not renamed commands. Preserve raw conservative category totals alongside any audited values. Unresolved attribution that affects a required gate prevents qualification.

## Independent mechanism evidence for the next hypothesis

A bounded audit of four prior cells found baseline executor reads repeated 464 already-returned source lines in three later calls (27,323 bytes), and rejected sensitive-content context loops repeated 67,798 numbered bytes within two calls. A separate two-cell memory-reset audit found baseline repeated source rows across later searches (event 4: 19,616 bytes; event 6: 2,821; event 7: 17,026; event 8: 1,458; event 9: 271; event 10: 14,815). These are transcript-level diagnostics, not new scorer inputs or a stable benefit estimate.

The executor audit also found a quality caveat: its baseline answer called retained `RUNNING` after `Error` a defect even though returned Javadoc/tests assign crash reconciliation to startup. The rejected candidate's additional recovery-contract reads were necessary and produced a better diagnosis. A reuse intervention must preserve uncovered ownership/recovery facts, not merely forbid extra reads. The next hypothesis tests successful-source reuse and overlap coalescing, independently of the rejected filename-first round.
