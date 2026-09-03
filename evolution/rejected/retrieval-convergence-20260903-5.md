# Rejected: producer output bounds

Status: **Rejected; runtime fully rolled back**.

- Frozen hypothesis: `../experiments/retrieval-convergence-20260903-5.md`
- Exact rejected diff: `retrieval-convergence-20260903-5.patch`; candidate Skill SHA256 `325235a781a1de69103134088f3b5a73b3581afb8493bbf5161a2a7faca4704f`; no runtime candidate commit.
- Baseline: `f0c5b6f81574a927091974197d776e9918fa9b4a`; artifacts `benchmark-results/retrieval-iteration-5-baseline-n1` and `benchmark-results/retrieval-iteration-5-candidate-n1`.
- Sanitized gate: `../../benchmarks/results/retrieval-convergence/20260903-iteration-5.json`; formal decision `infrastructure_indeterminate`.
- Tail output paired median `0.8040367530206265`; input `1.6236526986802224`.
- Failed gates: infrastructure, quality, tail_output_ratio_le_070, tail_broad_after_read_halved, duplicate_command_calls_not_increased, uncached_input_tokens_not_increased, tail_input_ratio_le_090, all_input_ratio_le_102.
- No n=3. Original raw/audited evidence retained; duration excluded. Any infrastructure/audit limitations remain in the frozen experiment and sanitized report.
- Lesson: `../wiki/retrieval-output-and-context-cost.md`; future work requires another independently supported frozen mechanism.
