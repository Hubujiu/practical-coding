# Release non-inferiority experiment

## Baseline

The unified current-scorer scorecard compares the v1.5 candidate at `30ac7e7` with accepted prior ref `88382d2` on common catalog cases. The first strict gate failed:

- Delivery quality tied, but current output, total tokens, duration, tools, and LOC were higher.
- Debug quality improved, but every measured cost except tool count was higher.
- Decision passed 29/30 versus 30/30 and had slightly higher output and duration.
- Router passed 107/114 versus 96/114, with uncached input higher by 12.5 median tokens.
- Behavior passed 52/54 versus 53/54 and had higher uncached input.

The PR therefore remains Draft. Raw historical results remain unchanged; `benchmarks/release_comparison.py` rescored both arms with the active catalog and emitted `benchmarks/results/v1.5/COMPARISON_SCORECARD.md`.

## Findings and hypotheses

1. A quoted PowerShell `rg` command was not recognized by the behavior scorer. This is a general transcript-parsing defect; fix it and rescore every arm equally.
2. One debugging run searched source before loading its selected root. Put the pre-source routing requirement earlier and state it once.
3. One resolved Decision response changed the stable final label from `Recommendation:` to `Decision:`. Make the final shape explicit in the Decision contract.
4. The v1.5 always-loaded entrypoint is materially longer than the prior entrypoint even though its conditional references are shorter. Compress repeated routing, retrieval, and isolation prose while preserving architecture boundaries.
5. Unrequested process recaps increase output cost without increasing delivery quality. Keep the final evidence statement to outcome, changed surface, check, and remaining uncertainty.

## n=1 candidate 5724d02

Public current-only n=1 retained full Delivery, Debug, and Decision quality. Router passed 33/38, above the prior aggregate rate but below the candidate's earlier n=3 rate. The misses exposed general boundary ambiguity: standalone artifacts were treated as Implementation; evidence-sufficiency choices were treated as product Decisions; and known edit targets suppressed Structural retrieval even when authoritative boundaries and cross-file guarantees were unknown.

Behavior results were invalidated by native-install discovery interference. Codex declared the active Skill at `skills/.system/practical-coding`, while the runner installed it only at `skills/practical-coding`. Agents then searched the shared eval-history tree and sometimes loaded an older v1.3 copy, inflating costs and changing routes. Install the immutable candidate at both the normal location and the declared system alias, record the alias in the manifest, and verify this infrastructure repair before using new Behavior evidence.

## n=1 native isolation candidate 97675e0

The repaired native run passed 18/18 Behavior cells and loaded the current candidate from the run-specific install. This validates the earlier three failures as infrastructure interference. Against prior n=3 medians, however, the n=1 aggregate still regressed in uncached input (+637.5), output (+387.5), total tokens (+618.5), and duration (+12.5s); tool count tied at 7.

Transcripts showed repeated general waste mechanisms: invoking a broad test runner after discovery found no tests, retrying blocked generated-cache cleanup, reading a reference through a wrongly duplicated path before resolving it, and searching sibling workspaces for an implementation despite a known local target and settled contract. Tighten those general operating constraints without naming cases or changing scoring.

## n=1 full candidate e58e29a

Quality met or exceeded the prior version: Delivery, Debug, Decision, and Behavior were perfect; Router was 36/38 (94.7%) versus the prior aggregate 84.2%. The strict cost gate still failed. Delivery improved uncached input, output, time, and tools but total tokens and LOC were higher. Debug, Decision, and Behavior retained median cost regressions; Behavior improved materially from the preceding isolated run but remained +483 uncached, +193 output, +11,177 total tokens, +4.5 seconds, and +0.5 tools.

Cross-suite transcripts again showed the same mechanisms: repeated cleanup after an explicit rejection, broad history/inventory work for known local targets, broad test-runner attempts when no test exists, and one extra failed reference read. Prefer checks that suppress disposable output, make failed cleanup terminal, and keep known-target retrieval local. Clarify that finite known consumers located by identifiers remain Bounded, while a missing user-owned policy alone requires no retrieval.

## Frozen gate

For every common suite, current pass/correctness/safety/build rates must be no lower than the prior version. Median uncached input, output, total tokens, duration, tool count, and changed LOC must be no higher. Iterations use current-only n=1 to reject clear regressions and select the best mechanism; because one sample cannot establish a stable median against prior n=3, the strict non-inferiority verdict applies only to the frozen current-only n=3 public matrix. The selected candidate also requires current-only n=3 held-out validation. Do not add case nouns or alter expectations to make a candidate pass.

## Rejected candidate a021b7b and final selection

The final cost-tightening experiment was rejected. It made Behavior pass the strict historical cost comparison in one n=1 sample, but Decision fell to 9/10 and Debug safety to 13/14; Delivery and Debug costs still failed. Selecting its attractive Behavior row would be outcome cherry-picking. Revert its runtime rules and preserve this negative receipt.

Across the accepted n=1 candidates, `fb69a9c` had the strongest quality-qualified balance: perfect Delivery, Debug, Decision, and Behavior, Router above the prior rate, complete Decision/Router cost passes, and only small residual median gaps in the other suites. Its runtime content is restored at `caa5304`. Freeze that content for n=3 rather than continuing to tune against stochastic public cases. The n=3 scorecard alone decides release non-inferiority; held-out n=3 separately decides generalization.

## n=3 public candidate 8314f62

The strict gate failed. Decision and Router passed; Delivery failed only LOC; Debug improved quality to 40/42 but retained uncached, duration, and LOC cost gaps; Behavior fell to 52/54 versus the prior 53/54. Held-out was not started.

One Behavior miss never loaded the candidate because Codex declared a shared eval-root Skill path while the runner installed only hash-local aliases. Add a current-only shared alias and record it in the manifest; never use that alias for a simultaneous historical native arm. The other miss loaded Debugging after an Implementation candidate check failed, accumulating two roots. The two Debug safety misses left a shared invariant inconsistent by patching or parameterizing the named caller path. These support two general corrections: a failed candidate check remains in the active event, and shared behavior is repaired once at its authoritative primitive unless a real caller contract requires divergence.

## n=1 candidate 138c321 and entrypoint compression

The infrastructure/shared-boundary candidate restored perfect Delivery, Debug, Decision, and Behavior quality. Behavior passed every quality/cost gate and Delivery LOC tied the prior median. Remaining n=1 gaps were Delivery tool count (+0.5), Debug uncached input (+1551) and LOC (+0.5), and Decision duration (+0.62 seconds).

The always-loaded entrypoint remained 7,112 bytes versus roughly 6.8 KB for the prior version. Because the full prompt is carried across tool turns, repeated prose amplifies uncached input even when tool count falls. Mechanically consolidate duplicate Core, routing, retrieval, manual, isolation, and evolution wording while preserving every tested boundary and the newly validated shared-invariant rules. Target materially below the prior entrypoint size before another n=1 run.
