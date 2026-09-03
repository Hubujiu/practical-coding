# Rejected: path-only discovery output

Decision: **Rejected; runtime rollback complete**. The loop ends after two iterations (one accepted observation iteration and one rejected runtime candidate).

- Frozen hypothesis: [iteration 2](../experiments/retrieval-convergence-20260903-2.md).
- Accepted baseline: `9d742b22fadda8bdd78f84bc58b955cf628a1cc0`; runtime identical to original remote `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`.
- Candidate: one Retrieval Policy line in `SKILL.md`, evaluated uncommitted on `af7dc97fd16ebad90052280819cc0c6a0008bb02`; it never qualified for a candidate commit. The [exact rejected patch](retrieval-path-only-discovery-20260903.patch) is retained.
- Benchmark: `gpt-5.6-luna`, medium, tree harness 1.0, retrieval metrics 1.1, timeout 600 seconds, workers 1, n=1, identical 15 cases / three frozen repositories. Fresh `benchmark-results/retrieval-iteration-2-{baseline,candidate}-n1/` directories contain all 54 cells per arm.
- Quality: baseline and candidate each pass 54/54; adaptive 15/15, each ceiling 13/13, every trace legal, explicit manual 2/2, spontaneous manual zero, clean fixtures. No observed under-retrieval or missing required verification in this matrix; repeated quality is untested because n=1 did not qualify.

## Cost result

Frozen tail: `sa-sensitive-rejection-boundary`, `pp-running-after-throw`, `sa-memory-reset-concurrency`; selected from baseline ordinary adaptive output before candidate application.

| Measure | Result | Required gate |
|---|---:|---|
| Tail recorded output paired median ratio | 0.415564 (-58.4%) | Pass, <=0.70 |
| Tail input-token paired median ratio | 1.674233 (+67.4%) | **Fail**, <=0.90 |
| Tail uncached input total | 177,240 -> 182,403 (+2.9%) | **Fail**, no increase |
| All-cell input-token paired median ratio | 1.064230 (+6.4%) | **Fail**, <=1.02 |
| All-cell tool-call paired median ratio | 1.000000 | Pass, <=1.00 |
| Tail tool-call paired median ratio | 1.411765 (+41.2%) | Mechanism diagnostic |
| Tail duplicate commands | 0 -> 3 | **Fail**, no increase |
| Tail whole-file bytes | 295,450 -> 264,007 | Pass |
| Tail dependency-source bytes | 176,632 -> 214,215 | **Fail**, no increase |
| Tail outputs above 64 KiB | 4 -> 1 | Pass |

Duration is recorded in the original artifacts but **excluded from the final decision**, following the user's subsequent instruction. Full metrics and identities are in the [sanitized report](../../benchmarks/results/retrieval-convergence/20260903-iteration-2.json).

## Why it failed and what remains uncertain

Filenames first reduced recorded output, but it did not reduce total context consumption. The executor tail went from 9 to 13 tool calls; the sensitive-content tail went from 17 to 24 with three repeated dependency-read commands. The latter includes retries of the same read after unsuccessful commands, so exact duplicate counts do not prove all repetitions were unnecessary. The frozen gate disallows their increase regardless, and the input-token failure is independently decisive. More tool exchanges and later inspection are a plausible explanation of increased cumulative input, not a proof from this single repetition.

Output measurement covers all 851 completed events; usage and shell decoding have no gaps. Recorded UTF-8 output can be truncated and is not a model-visible-token estimate. Mixed-category byte totals overlap. Final audit found `.cmd` build classification and interpolated-path misses; an observation-only 1.2 repair replays all 108 transcripts into a new directory without changing quality or direct costs. Broad-after-read estimates change from frozen v1.1's 0/1 to 1.2's 1/3, still failing. Partial success in compound commands remains a conservative counting limitation. This is sufficient to reject on direct costs, not to claim complete semantic instrumentation or qualify a candidate.

The candidate rule has been fully removed from active `SKILL.md`; references, topology, cases, scorers and manual modes retain their original runtime content. Execution-state/history-free remains retired. No n=3 and no third runtime candidate are run: under the user's updated cost definition, output decreases while tail input and tool calls do not improve.

Reconsideration requires independent mechanism evidence that removes retrieval exchanges or subsequent source consumption while retaining necessary callers/contracts/tests, plus a newly authorized frozen experiment. Rewording this rule, relaxing token gates, replacing tail cases or adding a runtime framework is not justified by these results.
