# Skill impact tracker

Record every maintenance-time Skill proposal after validation. Rejected proposals remain here so later iterations do not repeat them without new evidence.

Each entry should include:

- date / iteration;
- hypothesis or experiment path;
- target Skill/node;
- baseline ref and benchmark artifact;
- candidate ref or unified diff;
- baseline and candidate required quality scores;
- relevant cost metrics;
- decision: `Accepted` or `Rejected`;
- rejection reason or acceptance rationale.

## Historical note

Experiments before this tracker was introduced remain authoritative in their existing benchmark artifacts and `evolution/rejected/` records; do not invent missing scores retroactively.

## 2026-09-01 — explicit maintenance skills

- hypothesis: `evolution/wiki/maintenance-trigger-isolation.md`
- target: maintenance orchestration only; no runtime Skill/tree node changed
- baseline ref: `118acd81cb0e26f4f8087555c3bd89cbf45c9d30`
- benchmark: `benchmarks/results/evolution-workflow/2026-09-01.json`
- baseline runtime surface: unchanged by candidate
- candidate maintenance-contract score: `28/28 = 1.000`
- decision: `Accepted`
- rationale: the new maintenance skills are isolated from automatic topology and the deterministic contract gate passes perfectly; runtime model-backed inputs remain byte-identical in this iteration.

## 2026-09-01 — tree scorer contract normalization

- hypotheses: `evolution/experiments/tree-oracle-alignment-20260901.md`, `tree-oracle-semantic-equivalence-20260901.md`, `tree-scorer-normalization-20260901.md`
- target: deterministic benchmark evidence matching and Windows reference enforcement; no runtime Skill/tree file changed
- baseline ref: `31ba37c9c324ff5863ee237a8c89203f4405fbe9`
- invalidated artifacts: `tree-delivery-n1-20260901-103036`, `tree-delivery-n1-oraclefix-20260901-111838`, `tree-delivery-n1-semantic-20260901-120715`
- accepted artifact: `benchmark-results/tree-delivery-n1-normalized-20260901-125524`
- baseline adaptive score: invalid for acceptance because each preceding artifact used a superseded scorer contract
- candidate required quality: 106/106 determinate; adaptive 15/15; trace 15/15; explicit manual 2/2; spontaneous manual 0/13
- deterministic gate: 22 tree/discriminator/evolution tests passed; maintenance workflow 28/28
- decision: `Accepted`
- rationale: prompt/scorer alignment, semantic and language equivalence, and Windows path normalization are covered by positive and negative tests; runtime inputs remain unchanged. Stable topology and prior-version claims remain pending paired n=3 evidence.
