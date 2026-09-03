# Retrieval convergence — iteration 2: path-only discovery output

Status: candidate-not-applied

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

Pending baseline.
