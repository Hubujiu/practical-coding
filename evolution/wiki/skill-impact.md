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

## 2026-09-02 — evolvable leaf tree delivery

- hypothesis: `evolution/experiments/tree-bounded-evidence-volume-20260902.md`
- target: Core retrieval-volume rule on the isolated Debugging/Implementation leaf topology
- frozen baseline: v1.5 at `ba4058b4ef47a42bf79c9963b25678a2389897c1`
- candidate ref: `b202f7a165ae3ea4404d404bb1235ebf4270cbfb`
- artifact: `benchmark-results/tree-final-b202f7a-20260902` (252/252 determinate, n=3)
- required quality: adaptive 45/45; v1.5 44/45; no-skill 44/45
- discipline: trace 45/45; explicit manual 6/6; spontaneous manual 0/39
- adaptive versus v1.5 cost: tokens 258,061.64 vs 217,460.96; duration 76.82s vs 72.20s; tools 8.42 vs 7.24
- decision: `Accepted`
- rationale: the frozen primary release gate requires strict paired delivered-quality superiority and no regression against no-skill; both comparators were exceeded by one cell with perfect discipline. The proposed cost mechanism was not confirmed and the regression remains an explicit limitation, not an acceptance claim.
