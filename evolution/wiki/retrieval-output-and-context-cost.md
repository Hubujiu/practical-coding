# Mechanism: reduced output does not establish reduced context cost

## Claim

A path-only discovery step can reduce recorded search output while increasing cumulative model input and tool exchanges. Measure the complete task, preserve quality gates, and reject a cost proposal when its required input-token reduction fails.

## Observable trigger

- Discovery returns fewer bytes, followed by more inspection or repeated commands.
- Large recorded output is truncated, so transcript byte changes do not track model-visible input changes directly.
- A classifier measures bytes completely but misses command semantics such as shell escaping, platform wrappers or interpolated source paths.

## Evidence

The frozen [2026-09-03 iteration 2](../experiments/retrieval-convergence-20260903-2.md) selected three tail tasks before candidate evaluation. Both complete n=1 matrices passed 54/54 quality cells. Tail paired median recorded output fell 58.4%, while input tokens rose 67.4% and tool calls rose 41.2%. All-cell paired median input rose 6.4%, exceeding the frozen 2% limit. The candidate was rejected and rolled back; no n=3 was warranted. Timing is telemetry only under the user's updated protocol.

The [observer closeout repair](../experiments/retrieval-observer-closeout-repair-20260903.md) demonstrates why output coverage and semantic coverage are different: 851/851 outputs were available, while `.cmd` wrappers and interpolated paths required metadata corrections. Offline replay preserved direct costs and quality; raw matrices and their frozen classifications remain intact. Compound-command partial success still requires audit when a first-read count is material.

## Application and boundaries

Freeze quality, task/case identities, input-token and tool-call gates before candidate execution. Keep output bytes, uncached tokens and repeated command identities visible, rather than accepting one as a proxy for another. A passing quality matrix cannot compensate for a failed cost requirement.

Audit the highest-output unknown calls and the few events that determine convergence. Treat classifiers as conservative command-shape observations; do not silently relabel failed commands, infer arbitrary shell values or rewrite old artifacts. General observer repairs use positive/negative tests and new offline replay artifacts, with any changed derived counters disclosed.

This n=1 rejection does not prove every prompt-only retrieval policy is ineffective. It establishes that this frozen rule did not earn adoption and triggered the loop's cost stop condition. New runtime experimentation needs an independent mechanism and explicit continuation authority; the current rejection is not grounds to restore execution-state, alter the router or introduce a retrieval service.


## Source reuse does not bound initial output

The independently frozen source-reuse rule (iteration 3) improved tail input and tool rounds at n=1 but reduced paired median output by only 3.1%. First discovery still returned 1 MiB of unrelated vendored content, source could still be reread using a changed command, and audited whole-file/dependency output and reopened broad search increased. It was rejected and rolled back; there is no n=3 benefit claim. Evidence: `../experiments/retrieval-convergence-20260903-3.md` and `../../benchmarks/results/retrieval-convergence/20260903-iteration-3.json`.

Measure initial output volume separately from later convergence, and retain semantic event audits beside exact-command estimates. A changed command can reread the same source; a lower tool count can still emit more whole-file bytes. All mandatory quality and cost gates must pass together. The current user excludes duration from acceptance.

The first sharded candidate attempt also exposed a Windows parent-creation race: Python path resolution retained an extended prefix rejected by Git. Creating the shared shard parent before child launch fixed the general race. The incomplete artifact was preserved and both complete arms rerun with frozen repaired infrastructure; selectively filling failed cells was not used.


## Initial corpus selection still needs complete delivery

Iteration4 tested selecting project-owned scope before content output without a mandatory filename-first round. Its complete paired n=1 reduced tail output/input medians to0.398052/0.609382, but a required filename-mapping item was omitted after it had been read, two manually reviewed answers remained incomplete/incorrect, and whole-file output increased. The paragraph was rejected and rolled back; no n=3 followed. Evidence: `../experiments/retrieval-convergence-20260903-4.md`.

Retrieval availability and delivered coverage are different: finding a symbol does not prove it appears in the final artifact, and reading an invariant does not prove the diagnosis respects it. Continue using the original quality gate rather than adding case-specific exceptions. Source-corpus filtering alone has not established a complete improvement.

A semantic audit must examine returned content, including minified third-party implementation outside conventional dependency directories. The iteration4 baseline initially missed one such mixed 1MiB event. A separate hash-bound supplement corrects its dependency attribution while preserving the frozen audit; independently failed gates leave the rejection unchanged.


## Response bounds can increase cumulative work

Iteration5 independently constrained returned row count/source-text width while preserving locators, omissions and required coverage. Its candidate reached54/54 machine passes versus53/54, but tail input median ratio1.623653 and tool median1.4 regressed while output ratio0.804037 missed the target. The executor still failed manual contract completeness. A file-change deletion event without an output payload also failed the fixed per-cell measurement-coverage gate; null metadata was preserved. The exact paragraph was rejected and rolled back, without selective retries or a new observer definition. Evidence: `../experiments/retrieval-convergence-20260903-5.md`.

A smaller individual response is insufficient when repeated queries, manual shell formatting and retries replay more context. Separate guaranteed direct usage measurements, semantic attribution and unavailable output payloads; neither machine pass counts nor improved whole-file totals override other failed gates.
