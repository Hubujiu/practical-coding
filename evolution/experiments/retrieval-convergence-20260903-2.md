# Retrieval convergence — iteration 2: path-only discovery output

Status: **Rejected — candidate rolled back; cost-ineffective loop termination**

The hypothesis and thresholds below were frozen at `32132b173a670f27348f9d55b74272130926e147`. Only this status and the results section were updated after evaluation.

## Frozen hypothesis

- Baseline SHA: `9d742b22fadda8bdd78f84bc58b955cf628a1cc0` (repaired instrumentation; runtime byte-identical to starting remote `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`). A documentation-only freeze commit may be the actual baseline run HEAD; record it in the manifest.
- Accepted evidence: original `benchmark-results/tree-final-b202f7a-20260902/`, measured with frozen instrumentation into `benchmark-results/retrieval-iteration-1-repair-frozen-replay/`. The aborted four-cell diagnostic is excluded from cost calibration.
- Repeated mechanism: `sa-memory-map` produces 1,048,576 recorded bytes in an initial discovery event in all three repetitions, before any project read/candidate. `sa-memory-reset-concurrency` does so in two of three repetitions; `sa-sensitive-rejection-boundary` does so in one repetition and has earlier discovery outputs over 100 KiB in the others. `pp-token-rotation-boundary` also has early discovery outputs of 190,711–214,709 bytes. This supports discovery output reduction across several questions/repositories, not a rule keyed to a single case.
- Why this priority: one-way convergence/reopening restrictions alone cannot remove the dominant *initial* discovery output in several high-volume cells. The existing accepted rule already says to stop broad discovery after candidates are known. This independent hypothesis targets output at the discovery source.
- Causal claim: returning matching candidate filenames before matching source lines prevents unrelated source bodies from entering the first context. Existing bounded inspection and evidence requirements still determine completeness.
- Observable trigger: a project source location is unknown and a named symbol or current question is being located.
- Exact runtime file: `SKILL.md`, Retrieval Policy only, immediately after numbered item 2.
- Exact candidate rule: **When locating an unknown project source, request only candidate paths using a scoped filename query or filename-only text search for the named symbol or question. Inspect matching source lines only after candidate paths are known, using bounded reads.**
- Unchanged: all other Skill text, navigation and execution references, topology, manual modes, cases, answer scorers, harness, instrumentation, fixtures, tests/build requirements, retired execution-state files and historical artifacts.
- Expected quality: no loss in adaptive delivery, capability ceilings, trace legality, manual discipline, callers/contracts/safety evidence or necessary verification.
- Expected cost: at least 30% paired median recorded-output reduction and 10% input-token reduction in the frozen baseline tail; no broad-reopening/tool/ordinary-case regression under the gates below.
- Falsifier: output is merely moved into later reads, retrieval stops early, relevant paths are missed, fixed prompt/tool cost overwhelms savings, or any mandatory threshold fails. A failed rule is reverted, never reworded within this iteration.

## Frozen benchmark and infrastructure gate

- Model `gpt-5.6-luna`, reasoning `medium`; Codex CLI 0.145.0; Python 3.13.14; tree harness 1.0; unchanged scorer; retrieval metrics 1.1.
- All 15 current cases and original three frozen repository commits; current-only n=1 comprises 54 cells, workers=1, timeout=600 seconds, fresh directories for both arms.
- Baseline directory: `benchmark-results/retrieval-iteration-2-baseline-n1`.
- Candidate directory: `benchmark-results/retrieval-iteration-2-candidate-n1`.
- The manifest must match cases, fixture commits, model/reasoning, timeout, workers, repetitions, scorer/harness/instrumentation hashes, CLI executable, environment and build conditions. The expected runtime diff is exactly the frozen rule; no dependency installation or build-policy change.
- Before candidate application require all expected baseline cells determinate, no timeout/crash/contradictory scorer. Require all shell wrappers decodable, usage fields available, and at least 99% of completed event outputs measured. Audit unknown outputs above 16 KiB, mixed tail events and command scopes; unresolved classification affecting a mandatory metric invalidates the comparison. Truncated recorded bytes are lower bounds and never described as full/model-visible output.
- Freeze the three highest `tool_output_bytes` **ordinary adaptive** baseline case IDs in a separate tail receipt before candidate application. No replacement after viewing candidate results.

## n=1 gates, in order

1. Complete, determinate, comparable matrix and sufficient measurement coverage as above.
2. Adaptive quality and every required capability ceiling non-decreasing; every routing trace legal; explicit manual correct; spontaneous manual zero; no lost necessary evidence or checks; clean fixture worktrees. Any true-to-false paired quality change is a rejection.
3. Frozen tail: median paired output ratio <=0.70; total broad calls after first project read <=50% of baseline; duplicate commands, whole-file bytes, dependency-source bytes and outputs over 64 KiB do not increase. These non-increase checks use matched tail totals and retain per-case values for audit. Zero baseline broad calls require zero candidate calls and cannot independently prove reduction.
4. Frozen tail median input-token ratio <=0.90; total uncached input does not increase; all 54 cells median paired input ratio <=1.02; all-cell median paired tool-call ratio <=1.00; tail median paired serial-duration ratio <=1.05. Zero denominators with a positive candidate are regressions, never dropped pairs.

Only full passage qualifies a frozen candidate for n=3. n=1 is diagnostic, never a stable benefit claim.

## Frozen n=3 gates

- Full paired matrix: 252 cells, runs=3, workers=8, baseline-ref=`9d742b22fadda8bdd78f84bc58b955cf628a1cc0`; same timeout/model/reasoning/fixtures/scorer/instrumentation.
- Separate frozen-three-case paired runs=3, workers=1 for latency.
- All cells determinate; candidate delivered quality at least immediate baseline and required release no-skill boundary; trace failures=0, spontaneous manual=0, explicit manual failures=0; no additional safety, compatibility, caller, test or build regression.
- Tail paired median output ratio <=0.70, broad-after-read calls reduced >=50%, no increase in duplicates/whole-file/dependency output; improvement in >=2/3 repetitions and more than one case.
- Tail input-token median ratio <=0.90; tail uncached input not increased; all-case input-token median ratio <=1.02; all-case tool-call median not increased; separate serial-tail duration median ratio <=1.00. Cached-token fluctuations cannot substitute for reduced work. Unstable latency direction earns no latency benefit claim.
- Complete rollback of this exact runtime patch on any required failed/indeterminate gate. Retain observation code/raw artifacts and record rejection in the wiki. Acceptance requires all mandatory gates, committed/pushed evidence, then stop the loop.
- Iteration 3 is allowed only for a different independent mechanism exposed by this completed iteration. No threshold changes, case deletions, scorer tuning or rule rewording. The overall three-iteration and two-independent-rejection limits still apply.

## Results (not part of frozen hypothesis)

- Baseline complete: 54/54 determinate, 54/54 quality/trace passes, explicit manual 2/2, spontaneous manual 0; 395/395 tool events measured; no shell decode failure, usage gap or unknown output above 16 KiB.
- Frozen tail receipt: `retrieval-convergence-20260903-2-baseline.json`; selected only from this baseline's ordinary adaptive cells, before candidate application. Case IDs: `sa-sensitive-rejection-boundary`, `pp-running-after-throw`, `sa-memory-reset-concurrency`.
- Their recorded output is 1,233,970 / 592,058 / 152,782 bytes. Tail broad-after-read counts are all zero; the pre-frozen zero-baseline rule requires candidate zero and does not support a positive reduction claim.
- Large-event audit confirms initial root text search in the sensitive-content task (1 MiB recorded) and broad/large discovery in the executor task. The memory-reset task's largest output is a scoped contextual search after reading source; its inclusion is determined by output ranking, not by tailoring the case set to the hypothesis.
- Paired arithmetic was fixed before candidate execution in `benchmark-results/retrieval-iteration-2-gate.py`; its SHA-256 is preserved in the tail receipt. It rejects changed identities, missing cells, quality regressions and zero-to-positive metric regressions; large/mixed event and evidence audits remain separate requirements.

### Completed candidate and rejection

- Both serial n=1 matrices completed 54/54 determinate cells; each has adaptive 15/15 and every ceiling 13/13, all traces valid, explicit manual 2/2, spontaneous manual 0, clean fixture worktrees, and no timeout. There is no observed quality regression in this matrix.
- Baseline run HEAD: `32132b173a670f27348f9d55b74272130926e147`; candidate run HEAD: `af7dc97fd16ebad90052280819cc0c6a0008bb02` plus the one frozen, uncommitted `SKILL.md` line. Candidate SHA: none, because n=1 never qualified it for a candidate commit. Candidate Skill SHA-256: `bea25bccd96b52bce8a3f0d8f85995c50b6c5590cd7e23152b82091b1c38b7d3`.
- Frozen tail paired median ratios: recorded output **0.415564**, input tokens **1.674233**, tool calls **1.411765**, serial duration **1.479779**. Tail uncached input totals increase from **177,240 to 182,403**. All-cell input median ratio is **1.064230** (limit 1.02); all-cell tool-call median ratio is **1.000000** (passes, despite total calls 395 to 456).
- Frozen v1.1 tail mechanism totals: whole-file bytes 295,450 to 264,007; dependency-source bytes 176,632 to 214,215; duplicates 0 to 3; outputs over 64 KiB 4 to 1. Broad-after-read 0 to 1 is the automated result, with the source-path interpolation limitation below; do not present it as a complete count.
- Completed-event output coverage is 395/395 baseline and 456/456 candidate, with no shell decoding or usage gap. Identity hashes match except the intended Skill line. A 20,980-byte candidate Maven test output was manually audited (24 passing tests); v1.1 does not recognize `.cmd` build wrappers. Final tail audit also found missed first source reads when a directory variable is interpolated into a source path. Automated arithmetic passes its numeric infrastructure check, but that alone does not establish complete semantic classification.
- These observation limitations do not affect measured output bytes, input/cache usage, tool counts or duration. Those direct metrics independently and conclusively reject the candidate and trigger the user's **cost ineffective termination**: output falls while tail input, tools and duration all worsen. The frozen matrices and arithmetic remain unchanged; any observer repair is a separately identified offline replay, never a favorable replacement run.
- Rollback completed with `git restore --source=9d742b22fadda8bdd78f84bc58b955cf628a1cc0 -- SKILL.md`; the active runtime, references and topology again match starting remote `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`. Frozen candidate patch retained in `benchmark-results/retrieval-iteration-2-candidate-frozen/candidate.patch` and the rejection record.
- No n=3, no third runtime hypothesis, no stable benefit claim. The complete queued matrix was allowed to finish to preserve a determinate artifact; no additional model run was started after the failing tail became known.

### User instruction after the completed model runs

The user subsequently removed duration from evaluation, requested silence while tests run, and permitted parallel work with preferably no more than five cells assigned to each worker. Preserve the original frozen protocol and receipts above as history; **duration is now telemetry only and is not a reason for the final decision**. Removing that gate still leaves failed tail input, tail uncached input, all-cell input, duplicate and dependency-output gates. Output falls while tail input and tool calls increase, so the cost-ineffective termination remains applicable under the updated cost definition. Do not repeat the already complete 108 model cells solely to change worker allocation. Future independently authorized evaluations should freeze matching baseline/candidate shards of at most five cells per work unit, with isolated outputs and silent waits.

The subsequent observation-only 1.2 repair and offline replay are documented in `retrieval-observer-closeout-repair-20260903.md`; frozen v1.1 artifacts are untouched. Corrected broad-after-read estimates are baseline 1 / candidate 3; compound-command partial success remains a disclosed conservative counting limit. Direct costs and the rejection are unchanged. Full sanitized results: `benchmarks/results/retrieval-convergence/20260903-iteration-2.json`.
