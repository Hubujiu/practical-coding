# Rejected: progressive E/R depth and specialist-leaf tree

## Tried

A runtime tree with E0 Direct, E1 Probe, E2 diagnosis/engineering roots, E3 specialist leaves, and an independent R0-R3 retrieval tree.

## Why it was plausible

It separated source discovery from execution reasoning, attempted to pay specialist context only for material guarantees, and made minimum-sufficient depth measurable.

## Frozen evidence

- Candidate: `eefb3b79c688ced94273daea6a0af22b74d47022`
- Compact evidence: `benchmarks/results/progressive-tree/release-summary.json`
- Full interpretation: `benchmarks/results/progressive-tree/REPORT_ZH.md`
- Model/harness: `gpt-5.6-luna`, medium, n=3

## Result

- Delivery remained 54/54; Debug was 34/42.
- Held-out tasks were stable-pass on 18/22 tasks, with 21/66 exact routes.
- E2 was never minimum-sufficient; R2/R3 were never minimum-sufficient.
- Parent-to-leaf ablation produced 0 lifts, 7 ties, and 1 regression, usually at higher cost.
- Manual-only spontaneous activation was 0/66.

## Why rejected

The numeric depths and specialist leaves added control-state and context without stable quality lift. They also made valid source retrieval and capability selection difficult to express consistently. The supported ideas—orthogonal retrieval, explicit-only requirements interviewing, and evidence-driven evolution—do not require the rejected tree.

## Reconsider only if

A new family-level frozen experiment demonstrates stable quality lift from one narrowly scoped module over the general event module across multiple repositories, with an observable trigger available before loading and no regression in ordinary tasks.

