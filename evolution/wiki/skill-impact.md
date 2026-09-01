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
