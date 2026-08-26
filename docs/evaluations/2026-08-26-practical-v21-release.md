# Practical Coding v2.1 release evaluation

## Verdict

This version is deliverable as a lean general-purpose coding Skill. Freeze the routing text here: the remaining misses are either stochastic, specialist advantages, or label ambiguity. Editing the public-case wording again would create more overfitting risk than expected general benefit.

The claim is deliberately bounded. v2.1 is not the best specialist on every suite. It is a strong generalist with a cheap Direct Path, selective escalation, materially better debug/security efficiency than Superpowers in this harness, and an explicit opt-in navigation backend whose benefit is not yet universal.

## Frozen evidence matrix

All project-owned release matrices use `gpt-5.6-luna`, `medium`, three repetitions per cell, isolated workspaces, and no indeterminate cells unless stated otherwise.

| Area | Practical | Comparator / baseline | Result | Release interpretation |
|---|---:|---:|---|---|
| Delivery, 27 cells | 96.3% pass; 100% correct; 100% safe | Ponytail 100% / 100% / 100% | Practical efficiency `1.125x`; one Practical build miss; median LOC 21 vs 11 | Specialist Ponytail retains a small quality and leanness advantage. Practical does not pass the conservative quality gate. |
| Decision, 18 cells | 100% pass | Grill-me 94.4% | Efficiency `0.945x`; quality-gated utility `1.058`; Pareto trade-off | Practical wins one migration case and is cheaper in output/time, but uses more uncached input. |
| Debug, 30 cells | 90.0% pass; 100% correct | Superpowers 83.3%; 100% correct | Practical dominates; efficiency `2.311x`; utility `2.691` | The small pass advantage does not require Superpowers' much larger token/time budget. |
| Explicit security, 12 cells | 100% correct and safe | Superpowers 100% correct and safe | Practical dominates; efficiency `2.323x` | Equal observed safety with about 56% less uncached input, 59% less output, 54% less time, and 62.5% fewer tool calls. |
| Router classifier, 84 cells | 80/84 = 95.2% | Expected labels | One stochastic navigation/implementation miss and one disputed 3-run Decision/Implementation label | Excluding the disputed case gives 80/81 = 98.8%; keep the published denominator as the primary result. |
| Native trigger behavior, 30 cells | 29/30 = 96.7% | Behavioral contract | Direct, Decision, Debug, navigation, and security routes passed 3/3; ordinary Implementation loaded no module once | Routing is operational, not merely keyword classification. The isolated workspace fix is included in the harness. |
| Medium real repository | source 3/3 | graph 3/3 | 496 files / 4.0 MB: warm graph was 38.8% slower, with 26.8% more uncached input and 56.7% more calls | Do not enable Codebase Memory by project size alone at this scale. |
| Large real repository | source 3/3 | graph 2/3, provisional | 1,385 files / 163.6 MB / 9,603 graph nodes: successful graph runs used 25.2% less output, 16.5% less time, and 7.9% fewer calls, but 7.2% more uncached input | This is the beginning of a possible graph benefit, not a proven file-count threshold. Explicit opt-in remains correct. |

Primary local artifacts:

- `benchmark-results/release-v21-standard-n3-20260826`
- `benchmark-results/security-v21-superpowers-n3-20260826`
- `benchmark-results/release-v21-router-n3-20260826`
- `benchmark-results/release-v21-behavior-isolated-n3-20260826`
- `benchmark-results/navigation-personal-progress-v21-n3-iter2-20260826`
- `benchmark-results/navigation-super-agent-v21-n3-20260826`

## Quality-first comparison formula

The executable definition is in [the quality-gated scorecard](2026-08-26-quality-gated-scorecard.md). Cost cannot compensate for unsafe or materially worse output.

First require three determinate paired repetitions, suite pass within three percentage points of the comparator, no lower suite safety/build rate, and no case-level safety regression. Only then compute:

`E = exp(sum_i(w_i * ln(C_comparator,i / C_practical,i)))`

with weights 0.35 uncached input, 0.15 output, 0.35 model time, and 0.15 tool calls. The optional diagnostic utility is:

`U = ((Q_practical + 0.01) / (Q_comparator + 0.01))^2 * E`

The gate and weights are project policy, not paper constants. This follows the evaluation pattern in HELM and MLCommons of exposing quality and efficiency separately, the ranking-sensitivity warning in Efficient Benchmarking of Language Models, and ENAMEL's separation of correctness from efficiency.

## What is actually improved

1. The entry point now has one core and a first-match event router. Local, well-specified work stays on the Direct Path without loading a reference or worker.
2. Decision, Implementation, Debugging, and Navigation are independent modules. Debugging takes precedence for observed failures; Decision handles material choices; Implementation handles unmapped contracts and risky evidence gaps.
3. Navigation merges ordinary source search and optional Codebase Memory into one route. Graph use requires explicit project configuration and remains a backend choice, not an always-on tax.
4. Worker isolation has a cost gate. Root retains intent, authorization, integration, and the completion claim; small or single-event contexts stay local.
5. The benchmark now reports quality gates, Pareto status, component cost ratios, security-specific cases, native routing behavior, and real-repository navigation ablation.

## Known limitations and next evidence

- Delivery is not comparator-qualified: Ponytail was one build result better and produced leaner patches. This is acceptable for a generalist release, but it must remain visible.
- Router and native behavior are high but not perfect. The remaining public misses are not a reason to add case-specific trigger phrases.
- The graph backend has no proven universal size threshold. Repeat the ablation on multiple large, structurally different repositories and require reliable 3/3 routing before claiming savings.
- v2.1 still needs a genuinely private holdout before making generalization claims.
- Cost weights should receive a sensitivity sweep in a later release. The current verdict does not depend on the exact weights: Delivery remains unqualified, Decision remains a trade-off, and Debug/security remain materially cheaper.

## Release decision

Ship v2.1 as a release candidate/generalist release with the limitations above. Do not continue prompt tuning on the frozen public suites. The next changes should be driven by new private tasks or repeated failures on different real repositories—not by individual cases already inspected here.
