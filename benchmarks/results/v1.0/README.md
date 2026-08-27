# Practical Coding v1.0 benchmark results

The public release matrix uses `gpt-5.6-luna`, reasoning `medium`, isolated workspaces, fixed upstream comparator commits, and three repetitions per cell. The committed files are compact release aggregates; raw transcripts/workspaces remain local because they are large and may contain machine-specific paths.

| Suite | Practical | Comparator | Headline |
|---|---:|---:|---|
| Debug | 90.0% | Superpowers 83.3% | Practical dominates the quality-gated scorecard at `2.311x` relative efficiency in this harness. |
| Explicit security | 100% safe | Superpowers 100% safe | Equal observed safety; Practical used materially less input/output/time/tool calls. |
| Decision | 100% | grilling 94.4% | Practical led on quality; cost remained a trade-off. |
| Delivery | 96.3% | Ponytail 100% | Ponytail retained the build and LOC lead; Practical was cheaper but did not pass the conservative quality gate. |
| Router | 95.2% | expected route | Public classification regression corpus. |
| Native behavior | 96.7% | route/load contract | Verifies actual Skill discovery and selective reference loading. |

Machine-readable files:

- [`summary.json`](summary.json): suite rollups, comparator pins, quality-gated scores and limitations;
- [`comparisons.csv`](comparisons.csv): headline arm metrics in spreadsheet-friendly form;
- [`navigation.json`](navigation.json): two real-repository source-vs-graph ablations.

Interpret results in this order: correctness/safety → build/reachability → cost/LOC. A low-cost failure cannot compensate for a quality regression. The gate and formula are documented in [`../../../docs/evaluations/2026-08-26-quality-gated-scorecard.md`](../../../docs/evaluations/2026-08-26-quality-gated-scorecard.md).

These are role-specific comparisons, not a universal leaderboard. Delivery reuses Ponytail's published task content/scorer through a Codex/Luna adapter. Decision and Debug are controlled project comparisons against the relevant behavior of grilling and Superpowers; they are not official upstream benchmark results.

The v1.0 matrix does **not** include a Ponytail + Superpowers combined-install arm. See [`../../NEXT_VALIDATION.md`](../../NEXT_VALIDATION.md) for that planned comparison and [`../../REPRODUCING.md`](../../REPRODUCING.md) for exact reproduction boundaries.
