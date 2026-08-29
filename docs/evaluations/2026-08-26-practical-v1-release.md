# Practical Coding v1.0 release evaluation

## Verdict

Practical Coding v1.0 is a deliverable lean general-purpose coding Skill built around **adaptive rigor**: ordinary well-specified work stays Direct, while unresolved failures, material choices, risky boundaries, and broad structural blockers selectively load one specialist module.

The evidence does not show that Practical is the best specialist on every task. Ponytail retains a Delivery advantage in the published matrix; Practical's strongest measured advantage is Debug/Security efficiency against Superpowers in this harness. The integration claim is therefore bounded: Practical aims to provide the right engineering intensity without making every task pay for every capability.

## Frozen evidence matrix

All release matrices use `gpt-5.6-luna`, reasoning `medium`, three repetitions per cell, isolated workspaces, and fixed comparator commits.

| Area | Practical | Comparator / baseline | Release interpretation |
|---|---:|---:|---|
| Delivery, 27 cells | 96.3% pass; 100% correct; 100% safe | Ponytail 100% / 100% / 100% | Ponytail retains a small build/LOC advantage; Practical does not pass the conservative quality gate here. |
| Decision, 18 cells | 100% pass | grilling 94.4% | Practical leads quality on this matrix; cost is a trade-off. |
| Debug, 30 cells | 90.0% pass; 100% correct | Superpowers 83.3%; 100% correct | Practical passes the quality gate and records `2.311x` relative efficiency. |
| Explicit security, 12 combined cells | 100% correct/safe | Superpowers 100% correct/safe | Equal observed safety with materially lower input/output/time/tool calls for Practical. |
| Router, 84 cells | 95.2% | Expected labels | Strong public regression evidence for first-match routing, not a private generalization test. |
| Native behavior, 30 cells | 96.7% | Route/load contract | Shows real Skill discovery and selective reference loading rather than prompt-only classification. |
| Medium repository | source 3/3 | graph 3/3 | Graph navigation was materially more expensive; do not enable it by project size alone. |
| Large repository | source 3/3 | graph 2/3 provisional | Successful graph runs showed some cost advantages but routing reliability was insufficient for a universal threshold claim. |

Compact data: [`../../benchmarks/results/v1.0/`](../../benchmarks/results/v1.0/).

## What v1.0 actually contributes

The project borrows mature specialist ideas, but the architectural contribution is their **control policy**:

1. **Always-On Core:** a small common policy for scope, reuse, YAGNI, minimal diffs, and fresh evidence.
2. **Direct Path:** when the next safe action is clear, no engineering module is loaded.
3. **First-match Event Router:** unresolved failure → Debugging; material open choice → Decision; risky/unknown boundary → Implementation; broad structural blocker → Navigation.
4. **One module at a time:** the agent does not preload candidate workflows and then decide among them.
5. **Economic Isolation Gate:** workers are used only when avoided context or parallelism clearly exceeds handoff cost.
6. **Optional graph backend:** code intelligence is a Navigation backend, not a permanent system-prompt tax.

## Why this is not simply Ponytail + Superpowers

The current Ponytail Skill intentionally applies to any coding task and persists across responses. Superpowers' `using-superpowers` policy requires relevant Skill invocation before any response/action and gives process skills priority. Those are both coherent designs, but installing them together leaves their interaction to the host/model.

Practical adds an explicit arbitration layer: it decides **whether rigor is needed at all, which kind is needed now, and when to stop paying for it**.

That distinction is architectural. It is **not yet a combined-install benchmark result**.

## Unmeasured combined-stack claim

The v1.0 release matrix compares Practical against Ponytail and Superpowers separately. It did not run an arm with both installed simultaneously. Therefore v1.0 must not claim experimental superiority over the combined stack.

The next validation protocol requires a real `Ponytail + Superpowers` simultaneous-install arm and measures quality, safety, context/process overhead, Skill loads, missed escalations, and unnecessary workflow entry. See [`../../benchmarks/NEXT_VALIDATION.md`](../../benchmarks/NEXT_VALIDATION.md).

## Quality-first scorecard

Cost cannot rescue unsafe or materially worse output. A comparison first has to satisfy the quality gate before relative efficiency is interpreted. The executable policy and formula are documented in [`2026-08-26-quality-gated-scorecard.md`](2026-08-26-quality-gated-scorecard.md).

## Known limitations

- Delivery is not comparator-qualified: Ponytail was one build outcome better and produced leaner patches on the tested matrix.
- Router/native behavior are strong but not perfect.
- Public project-owned cases are regression evidence, not independent held-out generalization evidence.
- Graph navigation has no proven universal repository-size threshold.
- The exact Ponytail + Superpowers combined stack remains unmeasured in v1.0.
- A private held-out task population is still required before broad generalization claims.

## Release decision

Ship **v1.0** with the evidence boundaries above. Future prompt changes should be driven by new held-out tasks, combined-stack/interference evidence, or repeated independent failures—not by tuning individual already-inspected public cells.
