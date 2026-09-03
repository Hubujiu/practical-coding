# Retrieval convergence — iteration 5: bound source output at the producer

Status: **Rejected and rolled back; recorded-output coverage also fails**

## Frozen hypothesis

- Baseline SHA: `f0c5b6f81574a927091974197d776e9918fa9b4a`; runtime remains the original accepted tree at `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`. Iteration4 initial-corpus candidate was rejected and fully rolled back before this independent proposal.
- Evidence: complete iteration4 baseline/candidate and reviewed output metadata; no held-out or selectively rerun cells. Baseline memory-map event1 returned1,048,576 bytes across553 recorded lines, with one line750,662 bytes long. A line-count-only limit cannot control that width. Baseline executor event2 returned173,191 bytes/1,015 lines (maximum955 bytes per line); event3 returned76,797 bytes/1,509 lines despite no line exceeding141 bytes. A line-width-only limit cannot control that height. These are different retrieval questions in different repositories, not a special-case path or symbol rule.
- Causal mechanism: source output needs bounds on both returned rows and row width before entering model context. Limiting only scope or reusing earlier source does not prevent an individual response from dominating later input or hiding contracts in noise. Compact excerpts preserve named locations and the relevant contract; an omitted fact remains an explicit evidence gap.
- Observable trigger: a source content search or source read is about to emit text into context. Apply output shaping within that existing command/tool, not a mandatory preliminary locating call. The rule is independent of project/vendor classification and does not change which authoritative source is eligible.
- Exact runtime surface: one paragraph in `SKILL.md` Retrieval Policy, immediately before the existing paragraph beginning “Once candidate paths or symbols are known”. All rejected paragraphs remain absent.
- Exact proposed paragraph: **Bound the returned line count and source-text width before source-search or read output enters context; preserve complete path-and-line locators and mark omissions. If a needed contract is cut off, retrieve its missing portion in bounded excerpts, and never treat omitted content as checked. These limits apply to displayed output, not required search, test, or coverage scope.**
- Required evidence is not optional: source needed for a requested caller/contract/filename/path/verification claim must still be obtained. Bounds constrain one response, not total evidence coverage, test execution, correctness requirements or access to a necessary dependency boundary. A result with omissions cannot establish an exhaustive or negative claim. No case-specific text, numeric benchmark metric target, extra runtime helper, installed tooling or new automatic/manual route.
- Expected effect: reduce first and subsequent oversized source responses and whole-file bytes, preserving complete delivered artifacts. Additional focused pages may increase tool rounds; all overhead gates remain mandatory. No benefit is presumed.
- Falsifiers: required behavior/contracts are cut off and ignored; path provenance is lost; quality or caller/verification coverage decreases; oversized output moves to another tool; extra pagination/replayed context outweighs savings; or any unchanged gate fails. Do not reword this candidate after observing its outputs.

## Frozen evaluation and semantic audit

- Same repaired sharded harness, observation1.3, unchanged model/scorer/cases/fixtures: `gpt-5.6-luna`, reasoning medium, Codex CLI0.145.0, Python3.13.14, timeout600, workers8, fresh isolated shards of at most5 cells. Both arms use identical conditions and assignments; no retry/resume/selective replacement.
- Fresh complete current-only n=1:54 cells (15adaptive and3ceilings for13ordinary cases). Baseline `benchmark-results/retrieval-iteration-5-baseline-n1`; candidate `benchmark-results/retrieval-iteration-5-candidate-n1`. Baseline runs before the paragraph is applied. Freeze its top3 ordinary adaptive output case IDs using CASES manual_request flags, result hash, audit hashes and arithmetic before candidate execution.
- Require complete comparable/determinate matrices; no cell timeouts/scorer crash/usage/decode gaps, >=99% measured completed outputs, and audit of material unknown events. Preserve raw estimates and original transcripts.
- Same semantic audit contract as iteration4 and `retrieval-continuation-20260903.md`: actual returned project source establishes first read; filename inventory does not. Only later completed repo-wide operations count as after-read broad; partial successful events count only for proven returned content. Explicit reads that actually return a full file count as whole even with generous caps; filtered/bounded source matches remain searches. Full bytecode implementation dumps count as whole/dependency; names/signatures alone are not full implementation. Policy-rejected operations are not executed source reads. Retain full mixed-event bytes for each applicable category.
- Audit returned content for vendored implementation regardless of directory spelling, including first broad outputs; do not infer dependency solely from a glob that excludes it. This applies the established contract and closes the observed manual-audit omission without changing observer or raw metrics. Freeze any required audit before candidate; preserve later discoveries as transparent supplements, never silent replacements.
- All candidate tail answers must satisfy the original request and authoritative contracts, not only machine required-symbol checks. Preserve exact source paths requested in mappings, requested filename/type/caller items, and intentional Error/crash/startup recovery semantics. These are existing quality obligations, not new case/scorer edits.

## Mandatory non-time gates

1. Complete infrastructure, comparable identities and determinate semantic audits.
2. No paired machine quality regression in adaptive or required ceilings; legal traces, correct explicit manual, spontaneous manual zero, clean fixtures and candidate manual tail quality passes.
3. Tail paired median output ratio<=0.70; audited broad-after-source total<=50%baseline (baseline0 requires candidate0 and supports no positive reduction claim); tail exact duplicates, whole-file bytes, dependency-source bytes and >64KiB events do not increase.
4. Tail paired median input ratio<=0.90, uncached-input total no increase; all54 paired input median<=1.02 and tool-call median<=1.00. Preserve zero-to-positive regressions, never omit them. Duration telemetry only; cached fluctuations cannot substitute for input-work reduction.

Only full n=1 passage permits an exact committed candidate and the complete paired n=3 matrix of252cells (51shards, at most8concurrent and5cells each). Immediate baseline and no-skill comparisons are mandatory, all cells determinate, no adaptive quality regression against either, perfect trace/manual discipline and clean fixtures, and necessary requested/contract/test evidence retained. Compare all45 adaptive/baseline pairs for fixed overhead and9frozen-tail pairs for cost; apply the same thresholds/non-increase counters, with improvement across at least2repetitions and more than1tail task. No separate serial latency gate.

On any failure preserve evidence, reject and fully restore this paragraph before another independently justified hypothesis. On complete passage update wiki/impact/log, sanitize records, commit/push/verify and stop successfully. Until-success continuation does not relax any quality, cost, topology or retirement requirement.

## Results (outside the frozen hypothesis)

Pre-freeze independent review confirmed the single producer-output mechanism. The exact paragraph preserves full locators, explicit omission signals, continued access to the same contract and unchanged required verification scope. Pending fresh baseline; candidate not applied.


- Fresh baseline completed54/54 determinate with53 machine passes. The sole `ca-cancel-download/adaptive` failure is frozen lexical test-evidence matching: the answer discusses an existing cancellation test but misses `focused|suite|existing test|.test.`. Preserve original fail and audit rather than altering scorer or rerunning. Model exit0, no timeout, fixture unchanged; missing vitest is separately disclosed.
- All54 traces/manual contracts valid, spontaneous manual0, dirty fixtures0;388/388 outputs measured, no decode/malformed/usage gaps or unknown output over16KiB. Actual baseline HEAD `1af8121`.
- Frozen ordinary adaptive tail: sensitive rejection1,359,773 bytes; memory map1,083,618; executor302,669. Complete hashes and audited values in `retrieval-convergence-20260903-5-baseline.json`.
- Audited tail broad-after-source total1; whole-file286,583 bytes; dependency2,357,615 bytes. Initial vendored content was checked explicitly in both Super Agent tasks before freeze. Memory-map matching/range-loop outputs are bounded searches/reads, not whole-file despite automatic estimates.
- Manual quality: sensitive and memory-map pass; executor acknowledges intentional Error behavior but omits startup recovery responsibility and subsequent INTERRUPTED state, so existing completeness requirement fails. Candidate still must pass that requirement. No baseline answer or oracle modified.


### Complete candidate: rejected with explicit measurement limitation

- Both54-cell matrices completed, model exits determinate: baseline53/54 and candidate54/54 machine passes; legal traces/manual discipline and clean final fixtures. Candidate manual memory-map and sensitive answers pass with disclosed caveats; executor fails the existing contract criterion by recommending FAILED/rejecting RUNNING despite intentional Error and received startup-recovery evidence. No automatic quality regression; machine scores do not establish full correctness.
- Candidate exact Skill hash `325235a781a1de69103134088f3b5a73b3581afb8493bbf5161a2a7faca4704f`; actual run HEAD `67008e0e4f10a52ed9c36d4292f06b00d05eac0a` plus only the frozen paragraph. No candidate commit or n=3.
- Formal gate decision is `infrastructure_indeterminate`: sensitive event46 is a file-change deletion record without any output payload, so this cell has47/48 measured outputs (97.9167%), below frozen99%. Keep output bytes/hash null and disclose the limitation; do not fabricate empty output, reinterpret the denominator, modify instrumentation mid-pair or selectively rerun the cell.
- Maintainer disposition is nevertheless **Rejected**, based on independently recorded direct-cost and manual-quality failures. An infrastructure rerun cannot justify retaining this already cost-ineffective exact proposal; no acceptance or stable-benefit claim is made from this matrix.

| Metric | Baseline | Candidate | Paired median ratio |
|---|---:|---:|---:|
| tool_output_bytes | 2746060 | 1609821 | 0.8040367530206265 |
| input_tokens | 1243983 | 2125677 | 1.6236526986802224 |
| uncached_input_tokens | 167247 | 179309 | 1.0603855016275923 |
| tool_calls | 29 | 64 | 1.4 |
| broad_calls_after_first_project_read | 1 | 1 | 1.0 |
| duplicate_command_calls | 0 | 3 | 1.0 |
| whole_file_read_bytes | 286583 | 103029 | 1.7179320562472382 |
| dependency_source_bytes | 2357615 | 1144561 | 0.8743521010451178 |
| outputs_over_64k | 5 | 3 | 0.5 |

- All-cell input median 1.032019; tool-call median 1.000000. Tail output0.804037 fails0.70, input1.623653 fails0.90, tail uncached input and duplicates increase, and broad-after-source1 does not halve baseline1. Whole-file/dependency totals improve but do not compensate. Duration is telemetry only.
- Sensitive candidate takes48 tool events, including repeated source discovery, dependency investigation and temporary extraction cleanup. Memory-map introduces custom range-loop/PowerShell syntax failures and repair calls; its initial Java content search still returns84,710 bytes. Output shaping is not consistently followed and extra rounds can dominate cumulative input.
- Full sanitized results: `benchmarks/results/retrieval-convergence/20260903-iteration-5.json`. All original matrices/audits and candidate snapshot/patch are retained. Baseline's lexical test-evidence fail remains unchanged and separately qualified.
- Rollback completed with `git restore --source=f0c5b6f81574a927091974197d776e9918fa9b4a -- SKILL.md`. The producer-output paragraph is absent. The reopened loop may consider only another independently supported mechanism, not reword or retry this candidate for favorable variance.
