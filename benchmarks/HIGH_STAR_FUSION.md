# High-star skill fusion experiment

Date: 2026-09-01  
Branch: `experiment/evolvable-router-tree`

## Goal

Use strong external coding-skill patterns as **candidate capabilities**, not as a larger always-on workflow. The experiment asks whether a narrower descendant actually earns its context cost over the parent node.

The active root remains intentionally small:

```text
Core
├── Debugging
│   └── Dynamic Evidence           [staged]
└── Implementation
    ├── Security Boundary          [staged]
    ├── Migration & Compatibility [staged]
    └── State & Concurrency        [staged]
```

Decision and Clarification remain manual-only. Retrieval remains orthogonal.

## External mechanisms reviewed

The research pool includes SkillsBench / Skill-Use, Superpowers, Ponytail, Addy Osmani's `agent-skills`, Matt Pocock's `skills`, Anthropic's public skill examples, wshobson/agents, Thermos, swell-agents/coding-skills, and other large engineering-skill collections.

The experiment deliberately **does not** import their full lifecycle taxonomies.

| Mechanism | Placement | Decision |
|---|---|---|
| smallest-correct-change / delete-first | Core | Already present; keep always-on and tiny |
| systematic root-cause tracing | Debugging | Already present |
| runtime instrumentation / condition-based async evidence | Debugging → Dynamic Evidence | Stage as a depth-2 candidate |
| security hardening | Implementation → Security Boundary | Stage only for explicit trust-boundary invariants |
| deprecation / migration compatibility | Implementation → Migration & Compatibility | Stage for coexistence and rollback surfaces |
| transactions / idempotency / concurrency | Implementation → State & Concurrency | Stage for ordering/atomicity/state-owner problems |
| TDD / verification-before-completion | Cross-cutting evidence | Do not create a node merely because testing is useful |
| context engineering / source-driven lookup | Retrieval | Keep orthogonal to execution depth |
| spec / grill / architectural choice | Manual Decision or Clarification | Never restore automatic deliberation |
| code review / simplification | Core for ordinary explicit review | Do not auto-run a review phase after every change |
| worktrees / multi-agent review | Delegation / harness capability | Do not make repository mechanics an execution node |
| performance optimization | Parent or Dynamic Evidence when an observed regression lacks measurements | Do not create a noun-only Performance node yet |
| shipping / CI / release orchestration | Outside the automatic tree until a repeatable coding blocker earns it | Avoid importing an SDLC pipeline |

## Why this topology

Three findings drive the experiment:

1. **Focused skills beat broad bundles.** SkillsBench reports that compact curated skills outperform exhaustive bundles, so depth should buy specificity without turning the root into a catalog.
2. **Routing is a separate capability.** Skill-Use decomposes skill use into Trigger, Compliance, and Boundary. A child that helps when forced but is triggered badly is not a good runtime node.
3. **Minimalism and rigor are not competing roots.** Ponytail-style minimalism belongs in Core; deeper engineering discipline should appear only at evidence-backed boundaries.

## Complexity contract for staged children

Every staged child must satisfy all of these:

- one observable pre-load signal stated in its parent;
- one narrow reference file;
- no mandatory new dependency or tool;
- a lightweight fallback: if the signal disappears, stay in the parent;
- no sibling preloading;
- no new automatic Decision path;
- no broad test suite unless the material surface requires it.

The benchmark records token, duration, and tool-call cost. A child with no independent quality lift is removed even if its advice is individually reasonable.

## Benchmark protocol

### A. Main paired quality benchmark

Use the existing frozen real repositories and every root-to-node capability ceiling:

```powershell
python benchmarks/tree_validation.py --runs 3 --workers 3
python benchmarks/tree_analysis.py <run-dir>/results.jsonl --topology benchmarks/tree_topology.json --output <run-dir>/tree-analysis.json
python benchmarks/tree_skilluse_analysis.py <run-dir>/results.jsonl --topology benchmarks/tree_topology.json --output <run-dir>/skill-use.json
```

Run `--runs 1 --current-only` only while debugging the harness. Freeze prompts, topology, repositories, and scorer before the n=3 run.

Each ordinary task is evaluated under:

- no skill;
- frozen previous Practical baseline;
- adaptive current tree;
- Core-only ceiling;
- every root-to-node ceiling.

Manual tasks remain no-skill / baseline / adaptive and must never contaminate the automatic path.

### B. Capability-derived Trigger / Compliance / Boundary

`tree_skilluse_analysis.py` avoids a human-authored gold automatic route.

For a node `C` with parent `P`:

- **positive Trigger opportunity**: `cap:C` is stable-passing and `cap:P` is not;
- **negative Boundary opportunity**: `cap:P` is already stable-passing;
- **Trigger recall**: adaptive runs select `C` or a descendant on positive opportunities;
- **Compliance**: adaptive runs that selected `C`/descendants still deliver a passing result;
- **Boundary specificity**: adaptive runs do **not** enter `C`/descendants when the parent was already sufficient.

This preserves the branch's principle that topology is inferred from capability evidence rather than scored against a predefined taxonomy.

### C. Candidate promotion gate

A staged child is eligible for promotion only when all are true:

1. at least 2 stable marginal-lift tasks;
2. those tasks span at least 2 repositories;
3. Trigger recall ≥ 0.80;
4. Boundary specificity ≥ 0.90;
5. Compliance when triggered ≥ 0.90;
6. the main adaptive quality/non-inferiority gate passes;
7. zero spontaneous manual-mode activation;
8. all adaptive paths are valid parent-child paths;
9. cost is reviewed against the quality gained;
10. no benchmark case leaks child wording, file-specific answers, or expected constants into the skill.

These thresholds are experiment defaults, not permanent product constants.

### D. Removal / merge rules

Remove a staged child when it has no independent minimum-sufficient or marginal-lift cases. Merge or move sibling boundaries when capability ceilings repeatedly make siblings co-minimum and adaptive routing confuses them without net quality benefit. Promote behavior into the parent if the child becomes necessary for most parent-scope tasks.

## Required benchmark expansion before release promotion

The current frozen tree suite is useful for routing and repository-evidence behavior, but descendant promotion should not rely only on keyword evidence. Before release promotion, add executable tasks with deterministic verifiers for each surviving child, following the SkillsBench pattern:

```text
task/
├── task.md
├── environment/
├── oracle/
│   └── solve.*
└── verifier/
    └── test.*
```

Minimum target inventory:

- Dynamic Evidence: 4 tasks / 2 repositories or fixtures
- Security Boundary: 4 tasks / 2 repositories or fixtures
- Migration & Compatibility: 4 tasks / 2 repositories or fixtures
- State & Concurrency: 4 tasks / 2 repositories or fixtures
- 1–2 hard negatives per child that look topically similar but should stop at the parent

Every oracle must pass before agent runs. Prefer behavior checks over LLM judges. Skills must encode reusable procedure, never benchmark-specific filenames, constants, or solution commands.

## Expected outcomes

This experiment is allowed to conclude that **none** of the four descendants should survive. A useful external practice is not automatically a useful runtime node. The target is the smallest topology on the quality/cost Pareto frontier, not the deepest tree.
