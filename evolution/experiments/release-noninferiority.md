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

## Frozen gate

For every common suite, current pass/correctness/safety/build rates must be no lower than the prior version. Median uncached input, output, total tokens, duration, tool count, and changed LOC must be no higher. Iterations use current-only n=1; only a candidate that passes that directional check proceeds to current-only n=3 public and held-out validation. Do not add case nouns or alter expectations to make a candidate pass.
