# Rejected: discriminating search anchors

Status: **Rejected; runtime fully rolled back**.

- Frozen hypothesis: `../experiments/retrieval-convergence-20260903-6.md`
- Exact rejected diff: `retrieval-convergence-20260903-6.patch`; candidate Skill SHA256 `491ae7780bbf86654bea8d044d379778d363004a899e52561137fcb1a40b91e7`; no runtime candidate commit.
- Baseline: `72d6d138228664c7ec2efc1fc8e12e3dba9b87a6`; artifacts `benchmark-results/retrieval-iteration-6-baseline-n1` and `benchmark-results/retrieval-iteration-6-candidate-n1`.
- Sanitized gate: `../../benchmarks/results/retrieval-convergence/20260903-iteration-6.json`; formal decision `Rejected`.
- Tail output paired median `0.6042386832384489`; input `0.9342233511533804`.
- Failed gates: quality, tail_broad_after_read_halved, duplicate_command_calls_not_increased, tail_input_ratio_le_090.
- No n=3. Original raw/audited evidence retained; duration excluded. Any infrastructure/audit limitations remain in the frozen experiment and sanitized report.
- Lesson: `../wiki/retrieval-output-and-context-cost.md`; future work requires another independently supported frozen mechanism.
