# Practical Coding v2.1 benchmark results

The headline comparison uses `gpt-5.6-luna`, reasoning `medium`, isolated workspaces, and three repetitions per cell. The committed data are compact, path-free release aggregates; raw transcripts and generated workspaces remain local because they are large and may contain machine-specific paths.

| Suite | Practical | Comparator | Headline |
|---|---:|---:|---|
| Debug | 90.0% | Superpowers 83.3% | Practical dominates the quality-gated scorecard at `2.311x` relative efficiency. |
| Explicit security | 100% safe | Superpowers 100% safe | Equal observed safety; Practical used about 56% less uncached input and 54% less time. |
| Decision | 100% | grilling 94.4% | Practical won quality; the cost result is a trade-off. |
| Delivery | 96.3% | Ponytail 100% | Practical was cheaper, but Ponytail retained the build and LOC lead. |
| Router | 95.2% | expected route | Public classification regression corpus. |
| Native behavior | 96.7% | route/load contract | Verifies actual Skill discovery and on-demand reference loading. |

Machine-readable files:

- [`summary.json`](summary.json) contains release suite rollups, comparator pins, and quality-gated scores.
- [`comparisons.csv`](comparisons.csv) provides the same headline arm metrics in a spreadsheet-friendly long format.
- [`navigation.json`](navigation.json) contains the two real-repository source-vs-graph ablations.

Interpret results in this order: correctness and safety, build/reachability, then cost and LOC. A low-cost result cannot compensate for a safety failure or material quality regression. The exact gate and formula are documented in [`../../../docs/evaluations/2026-08-26-quality-gated-scorecard.md`](../../../docs/evaluations/2026-08-26-quality-gated-scorecard.md).

These comparisons are role-specific, not a universal leaderboard. Delivery reuses Ponytail's published agentic task content and deterministic scorer through a Codex/Luna adapter. Decision and Debug are controlled project comparisons against the relevant behavior of grilling and Superpowers; they are not official upstream benchmark results. See [`../../REPRODUCING.md`](../../REPRODUCING.md) for exact commands and evidence boundaries.
