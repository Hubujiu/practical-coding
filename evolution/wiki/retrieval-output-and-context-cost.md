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
