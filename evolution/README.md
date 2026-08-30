# Skill evolution knowledge

This directory is **maintenance-time knowledge**. Ordinary runtime coding agents must not read it while solving user tasks.

Its purpose is to keep benchmark experience across Skill revisions without permanently injecting that history into `SKILL.md`.

## Layers

```text
benchmark/raw traces and aggregates
             ↓
evolution/patterns
             ↓
evolution/experiments
             ↓
candidate Skill patch
             ↓
validation benchmark
        ↙          ↘
     accept       reject
       ↓             ↓
 runtime Skill   evolution/rejected
```

A rejected patch rolls back from runtime behavior, but the lesson stays here.

## Rules

- Do not create a global rule from one surprising task.
- Prefer repeated mechanisms across independent tasks before promoting a pattern.
- Keep evidence IDs/paths, not copied raw transcripts.
- Record the exact hypothesis and boundary change before seeing validation results.
- Public regression cases that influenced wording are regression evidence, not held-out proof.
- A pattern may justify changing an escalation boundary, changing a retrieval contraction rule, merging levels, splitting a level, or changing module wording.
- The target is not maximum process. The target is the lowest quality-qualified rung.

## Promotion ladder

```text
single case
  ↓
candidate lesson
  ↓
repeated independent mechanism
  ↓
pattern
  ↓
frozen experiment
  ↓
held-out + regression validation
  ↓
Skill rule / boundary / level change
```

Use `patterns/`, `experiments/`, and `rejected/` for the durable record. Historical raw benchmark artifacts remain under the benchmark system rather than being duplicated here.
