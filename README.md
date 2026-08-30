# Practical Coding — Progressive Capability Tree Experiment

> **Experimental branch:** `experiment/progressive-ladders`. The architecture below is a candidate and has not yet earned a release claim.

Practical Coding asks continuously:

> **What is the least engineering depth and least context needed for the next reliable decision?**

The key change in this experiment is that **depth and problem type are separate**. The Skill stays Ponytail-like and minimal at the Core, then expands only when evidence exposes a specific unresolved event.

## Architecture

```mermaid
flowchart TB
  T[Task] --> D{Material user-owned choice?}
  D -->|yes| DG[Decision Gate]
  D -->|no| E0[E0 Direct / Core]
  DG --> E0
  E0 --> E1[E1 Focused evidence]
  E1 -->|unexplained failure| DX[E2 diagnosis]
  E1 -->|unresolved contract/invariant| EN[E2 engineering]
  DX --> S1[E3 security/state/compatibility/performance]
  EN --> S2[E3 security/state/compatibility/performance/quality/interface]

  E0 -. independent .-> R0[R0 Target]
  R0 --> R1[R1 Local]
  R1 --> RS[R2 Structural]
  R1 --> RE[R2 External contract]
  R1 --> R3[R3 Bounded exhaustive repo]
```

No arrow means “always do the next step.” It means that branch becomes available if the current evidence test fails.

## Minimal Core

Most tasks should remain E0/E1:

- smallest observable success;
- smallest coherent diff;
- reuse existing project primitives;
- no speculative abstractions, fallbacks, options, validation, tests, or documentation;
- cheapest focused verification;
- preserve unrelated behavior and user changes.

That keeps the default behavior close to Ponytail-style anti-overengineering rather than turning every task into a lifecycle workflow.

## Progressive execution tree

| Depth | Meaning | Loaded context |
|---|---|---|
| **E0 Direct** | target, contract, and check are clear | Core only |
| **E1 Focused** | one bounded evidence step can remove a blocker | Core only |
| **E2 Root** | a real unresolved event needs a structured method | one root: diagnosis **or** engineering |
| **E3 Leaf** | a material specialist guarantee remains | root + one specialist leaf |

The specialist leaves are deliberately narrow: security, persistence/concurrency/state, compatibility/migration, measured performance, structural quality, and interface quality.

This takes the useful part of expert skill packs—concrete trigger, process, exit, verification—without loading their workflows globally. Addy Osmani's progressive-disclosure anatomy, Superpowers' executable procedures, focused SkillsBench expert skills, and design-oriented skills such as taste-skill are inputs to the leaf design, not dependencies.

## Retrieval is also a tree

The old sequence `R0 → R1 → R2 → R3 → R4 External` was wrong because external evidence is not inherently deeper than repository-wide search.

Now:

- **R0 Target** — known source;
- **R1 Local** — bounded/ranked search;
- **R2 Structural** — relation/flow lookup;
- **R2 External** — authoritative contract the repository cannot establish;
- **R3 Bounded exhaustive repository** — only for explicit exhaustive claims or failed localization.

The governing rule remains **expand → localize → contract**. Structural tools such as Codebase Memory are optional accelerators, never required dependencies.

## Benchmark-driven tree optimization

The tree is not architecture by aesthetics. Benchmark it against:

1. no-skill;
2. accepted prior Practical Coding;
3. candidate adaptive tree;
4. relevant specialist comparators only on families they claim to cover.

Measure minimum-sufficient depth **and** path behavior: unnecessary root/leaf loads, missed leaves, branch confusion, path exactness, tokens/time/tool calls/LOC, and quality gates.

A leaf that does not show stable net lift over its parent should be tightened, merged, replaced, or deleted. A depth rarely minimum-sufficient is a merge/removal candidate.

See [`benchmarks/LADDER_EVOLUTION.md`](benchmarks/LADDER_EVOLUTION.md).

## WikiSkill-style evolution loop

Runtime agents do not read `evolution/`. Maintainers separate raw experience, persistent knowledge, and executable Skill rules:

```text
benchmark runs + real-project experience
                ↓
        evolution/wiki
                ↓
      frozen experiment
                ↓
 no-skill/prior/depth/path validation
          ↙             ↘
       accept           reject
```

Real project corrections therefore become evidence receipts, not immediate prompt patches. Repeated mechanisms can accumulate across iterations even when a particular candidate wording is rejected.

See [`evolution/README.md`](evolution/README.md) and [`evolution/EXPERIENCE_SCHEMA.md`](evolution/EXPERIENCE_SCHEMA.md).

## Runtime reference tree

```text
SKILL.md
references/
├── decision.md
├── debugging.md          # diagnosis root
├── engineering.md        # engineering root
├── navigation.md
├── delegation.md
└── specialists/
    ├── security.md
    ├── state.md
    ├── compatibility.md
    ├── performance.md
    ├── quality.md
    └── interface.md
```

Historical benchmark results remain historical; fresh repeated runs are required before merging this experiment or publishing comparative claims.

MIT License. See `THIRD_PARTY_NOTICES.md` for upstream attribution.
