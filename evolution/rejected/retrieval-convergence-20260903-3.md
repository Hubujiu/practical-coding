# Rejected: source reuse

Status: **Rejected; runtime fully rolled back**.

- Frozen hypothesis: `../experiments/retrieval-convergence-20260903-3.md`
- Exact rejected diff: `retrieval-convergence-20260903-3.patch`; candidate Skill SHA256 `bd3e0a6fba41baab05ad3728a6eb12a7ada7f70fca7468ab7b67d034fcd1618d`; no runtime candidate commit.
- Baseline: `ffa6b655aa683bb891cc50e0cdb7efa7ae333cd8`; artifacts `benchmark-results/retrieval-iteration-3-baseline-n1-attempt2` and `benchmark-results/retrieval-iteration-3-candidate-n1-attempt2`.
- Sanitized gate: `../../benchmarks/results/retrieval-convergence/20260903-iteration-3.json`; formal decision `Rejected`.
- Tail output paired median `0.9691258414179335`; input `0.6073711240722963`.
- Failed gates: tail_output_ratio_le_070, tail_broad_after_read_halved, whole_file_read_bytes_not_increased, dependency_source_bytes_not_increased.
- No n=3. Original raw/audited evidence retained; duration excluded. Any infrastructure/audit limitations remain in the frozen experiment and sanitized report.
- Lesson: `../wiki/retrieval-output-and-context-cost.md`; future work requires another independently supported frozen mechanism.
