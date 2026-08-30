# Skill evolution knowledge

This directory is **maintenance-time knowledge**. Ordinary runtime coding agents must not read it while solving user tasks.

The architecture separates three things that should not collapse into one prompt:

1. **experience** — benchmark runs and real-project receipts;
2. **persistent knowledge** — consolidated mechanisms, routing failures, and accepted lessons;
3. **executable Skill** — the small runtime rules and references that have passed validation.

This follows the useful separation demonstrated by WikiSkill: experience should compound into durable maintenance knowledge, while candidate Skill changes still pass an explicit validation gate.

## Loop

```text
benchmarks/results + real-project receipts
                  ↓
          evolution/wiki
                  ↓
     frozen experiment hypothesis
                  ↓
     candidate Skill/tree change
                  ↓
 no-skill + prior + depth/path validation
            ↙              ↘
         accept            reject
           ↓                  ↓
     runtime Skill      evolution/rejected
```

A rejected patch disappears from runtime behavior, but the learned mechanism remains available to maintainers.

## Evidence rules

- Do not create a global rule from one surprising task or one user correction.
- Keep exact evidence pointers; do not copy large raw transcripts into the wiki.
- Separate benchmark evidence, held-out evidence, and real-project experience explicitly.
- Record the hypothesis and proposed boundary/tree change before validation results are known.
- Prefer repeated mechanisms across independent repositories/tasks before promoting a pattern.
- Treat expert-skill comparisons as family-specific evidence, not proof that Practical Coding should copy their whole workflow.
- The optimization target is **quality-qualified net lift at the lowest useful depth/path**, not maximum process.

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
frozen experiment
   ↓
held-out + regression + baseline validation
   ↓
Skill node / trigger / depth change
```

Use `EXPERIENCE_SCHEMA.md` for receipts, `wiki/` for consolidated knowledge, `experiments/` for frozen hypotheses, and `rejected/` for failed changes. Existing `patterns/` remains valid historical evidence; new work should prefer the wiki layer so mechanisms can be linked across experiments rather than duplicated.
