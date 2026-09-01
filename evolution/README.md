# Skill evolution knowledge

This directory is **maintenance-time knowledge**. Ordinary runtime coding agents must not read it while solving user tasks.

The architecture separates three things that should not collapse into one prompt:

1. **experience** — benchmark runs and real-project receipts;
2. **persistent knowledge** — consolidated mechanisms, routing failures, and accepted lessons;
3. **executable Skill** — the small runtime rules and references that have passed validation.

This follows the useful separation demonstrated by WikiSkill: experience should compound into durable maintenance knowledge, while candidate Skill changes still pass an explicit validation gate.

## Explicit maintenance skills

`evolution/skills/` contains two user-triggered maintenance skills. They are not automatic runtime nodes and are intentionally absent from `benchmarks/tree_topology.json`.

- `session-to-wiki` compiles the current visible session into a sanitized immutable receipt under `evolution/raw/`, then consolidates reusable mechanisms into the wiki. It must not edit runtime Skill files.
- `evolve-skill` reads the wiki and impact history, freezes one atomic hypothesis and its benchmark before changing runtime Skill text, compares baseline and candidate on the same evidence, and rolls back any required quality regression or indeterminate gate.

This keeps the paper-style Raw → Wiki → Skill separation operational without exposing maintenance history to ordinary inference.

## Loop

```text
benchmarks/results + evolution/raw receipts
                  ↓
          evolution/wiki
                  ↓
     frozen experiment hypothesis
                  ↓
     frozen/new benchmark + baseline
                  ↓
        atomic Skill candidate
                  ↓
 same-evidence validation + regressions
            ↙              ↘
         accept            reject
           ↓                  ↓
     runtime Skill      evolution/rejected
           ↓                  ↓
       skill-impact + persistent wiki
```

A rejected patch disappears from runtime behavior, but the learned mechanism remains available to maintainers.

## Wiki control files

- `wiki/index.md` — concise mechanism catalog;
- `wiki/log.md` — chronological evolution log;
- `wiki/skill-impact.md` — accepted/rejected intervention history;
- mechanism pages — causal claims, evidence, contradictions, triggers, and experiments.

## Evidence rules

- Do not create a global rule from one surprising task or one user correction.
- Keep exact evidence pointers; do not copy large raw transcripts into the wiki.
- Separate benchmark evidence, held-out evidence, and real-project experience explicitly.
- Record the hypothesis and proposed boundary/tree change before validation results are known.
- Freeze or add the benchmark before applying the candidate patch; baseline and candidate must use the same cases, scorer, model/harness, and repetition policy.
- Prefer repeated mechanisms across independent repositories/tasks before promoting a pattern.
- Treat expert-skill comparisons as family-specific evidence, not proof that Practical Coding should copy their whole workflow.
- The optimization target is **quality-qualified net lift at the lowest useful depth/path**, not maximum process.
- A required correctness/safety regression cannot be traded for lower token or time cost.

## Promotion path

```text
single receipt
   ↓
candidate lesson
   ↓
repeated independent mechanism
   ↓
evolution/wiki entry
   ↓
frozen experiment + benchmark
   ↓
baseline run
   ↓
atomic candidate
   ↓
held-out + regression + baseline validation
   ↓
Skill node / trigger / depth change OR rollback
```

Use `EXPERIENCE_SCHEMA.md` for receipts, `raw/` for immutable sanitized experience, `wiki/` for consolidated knowledge, `experiments/` for frozen hypotheses, and `rejected/` for failed changes. Existing `patterns/` remains valid historical evidence; new work should prefer the wiki layer so mechanisms can be linked across experiments rather than duplicated.
