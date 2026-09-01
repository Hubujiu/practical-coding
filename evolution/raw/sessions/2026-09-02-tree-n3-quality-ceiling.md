# Receipt — paired n=3 reached quality ceiling without strict superiority

- Candidate commit: `ad2987c903fb8dc32dd87ead4ac658143397227c`
- Artifact: `benchmark-results/tree-final-ad2987c-20260902`
- Completeness: 252/252 cells (three repetitions across adaptive, baseline, no-skill, and three capability ceilings)
- Adaptive: 45/45
- Frozen v1.5: 45/45
- No-skill: 44/45
- Core: 39/39; Debugging: 38/39; Implementation: 39/39
- Adaptive trace: 45/45; explicit manual: 6/6; spontaneous manual: 0/39
- Mean tools: adaptive 7.60, v1.5 8.27
- Mean tokens: adaptive 242,910.84, v1.5 211,758.69
- Mean duration: adaptive 75.60s, v1.5 72.94s

The report passes noninferiority and all discipline gates but cannot show strict quality improvement because both Skill versions score 100%. It is retained as complete ceiling evidence, not the requested final delivery. Repeated ablation justifies testing a smaller Core-only automatic surface for cost improvement.
