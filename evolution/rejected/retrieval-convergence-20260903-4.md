# Rejected: initial project-owned corpus

Status: **Rejected; runtime fully rolled back**.

- Frozen hypothesis: `../experiments/retrieval-convergence-20260903-4.md`
- Exact rejected diff: `retrieval-convergence-20260903-4.patch`; candidate Skill SHA256 `5101397b3e65ad8f32248bbd8050ebc60ea3a738daa38ae92930c6a0fa0f0748`; no runtime candidate commit.
- Baseline: `205f5fe76ee88b951f9a6690d2a7bfbe0bfe0d15`; artifacts `benchmark-results/retrieval-iteration-4-baseline-n1` and `benchmark-results/retrieval-iteration-4-candidate-n1`.
- Sanitized gate: `../../benchmarks/results/retrieval-convergence/20260903-iteration-4.json`; formal decision `Rejected`.
- Tail output paired median `0.39805234327449784`; input `0.6093817203481083`.
- Failed gates: quality, whole_file_read_bytes_not_increased.
- No n=3. Original raw/audited evidence retained; duration excluded. Any infrastructure/audit limitations remain in the frozen experiment and sanitized report.
- Lesson: `../wiki/retrieval-output-and-context-cost.md`; future work requires another independently supported frozen mechanism.
