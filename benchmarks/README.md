# Practical Coding benchmark chain

The active experiment uses an evolvable local-router tree. Core is depth 0 and knows only its immediate automatic children. Each loaded node owns only its own next-level router. Decision and requirements interviewing are explicit-only manual modes outside the automatic tree. Retrieval remains orthogonal.

The accepted v1.5 flat Event Router and the rejected fixed E/R ladder remain historical baselines. Do not use their fixed reasoning labels, numeric depths, or gold route expectations as the acceptance oracle for this experiment.

## Active questions

1. Does the candidate deliver a correct, safe, evidence-backed result at least as reliably as the v1.5 baseline and no-skill arm?
2. Which automatic nodes are actually minimum-sufficient under parent-versus-child capability ceilings?
3. Does adaptive disclosure stop at a minimum-sufficient node without spontaneous manual Decision or Clarification activation?
4. Do repeated failures or sibling ambiguity justify growing, splitting, merging, promoting, collapsing, or removing a node?
5. Does retrieval stop at the cheapest sufficient capability independently of execution depth?
6. Under long-task state pressure, can a bounded validated execution snapshot replace history reconstruction without becoming a route or weakening delivered quality?

## Tree experiment

The runtime topology is data, not a scorer constant:

- `tree_topology.json` — current root, nodes, parent/child edges, depth, manual modes, cross-cutting substrates, and frozen baseline ref;
- `tree_cases.py` — topology-neutral real-repository tasks; no expected automatic route or E0-E3 label;
- `tree_validation.py` — runs no-skill, v1.5 baseline, adaptive candidate, and capability ceilings for every automatic node;
- `tree_analysis.py` — derives minimum-sufficient node sets, adaptive disclosure diagnostics, node marginal lift, and topology-change candidates;
- `TREE_EVOLUTION.md` — interpretation and mutation rules.

Iteration uses `n=1` while changing topology, node content, runtime substrate wording, or scorer contracts:

```powershell
python benchmarks/tree_validation.py --self-test
python benchmarks/tree_validation.py --current-only --runs 1 --workers 3 `
  --output benchmark-results/tree-n1
python benchmarks/tree_analysis.py benchmark-results/tree-n1/results.jsonl `
  --output benchmark-results/tree-n1/analysis.json
```

Only after the topology and runtime wording are frozen should the candidate run `n=3` with baseline/no-skill arms:

```powershell
python benchmarks/tree_validation.py --runs 3 --workers 3 `
  --output benchmark-results/tree-final
python benchmarks/tree_analysis.py benchmark-results/tree-final/results.jsonl `
  --output benchmark-results/tree-final/analysis.json
```

## Execution-state runtime contract

The SKILL.state-inspired mechanism is a cross-cutting runtime substrate. It is intentionally absent from `automatic_nodes`, `manual_modes`, and adaptive `TREE_TRACE` paths. The tree decides which execution capability is available; execution state holds only the current future-relevant snapshot inside that capability.

The deterministic gate is frozen in:

- `runtime/skill_state.py` — coding-domain schema, validated merge patch, null deletion, rollback, transition parser, and history-free prompt builder;
- `benchmarks/test_skill_state_runtime.py` — unit contracts for merge/deletion, schema and budget enforcement, exact transition shape, rollback, and bounded provenance references;
- `benchmarks/skill_state_validation.py` — horizons 10/50/200 with irrelevant telemetry, append-only-history comparison, immediate stale-fact correction, and invalid-patch rollback;
- `docs/SKILL_STATE.md` — architecture, activation boundary, and host-level limitations;
- `evolution/experiments/skill-state-runtime-20260902.md` — hypothesis frozen before the runtime patch.

```powershell
python -m unittest benchmarks.test_skill_state_runtime
python benchmarks/skill_state_validation.py --self-test `
  --output benchmark-results/skill-state-contract.json
```

A perfect deterministic contract score is required. This proves implementation mechanics only: it does not reproduce the paper's model accuracy/token figures and cannot prove horizon-independent prompts for a host that still appends prior messages. Because `SKILL.md` wording affects all tasks, a passing state contract must still be followed by the same model-backed `n=1` iteration and frozen `n=3` release gate used for any runtime Skill change.

## Explicit evolution workflow benchmark

Maintenance-time WikiSkill-inspired capabilities are tested separately from runtime routing. They must remain explicit-only and cannot weaken the acceptance gate for runtime Skill changes.

```powershell
python benchmarks/evolution_workflow_validation.py --self-test `
  --output benchmark-results/evolution-workflow-contract.json
```

This deterministic suite scores whether:

- `session-to-wiki` writes a sanitized immutable receipt before wiki consolidation and cannot mutate runtime Skill files;
- `evolve-skill` reads wiki/impact history first, freezes one atomic hypothesis and benchmark before the runtime patch, runs baseline before candidate, compares both on identical evidence, and rolls back regression/indeterminate candidates;
- neither maintenance skill appears as an automatic topology child/reference;
- wiki index/log/impact control files and the current-session receipt exist.

A perfect score is required. This is a maintenance-contract gate, **not** a substitute for `tree_validation.py` runtime-quality evidence. If runtime Skill/tree text changes, the relevant model-backed tree benchmark must still be rerun under the `evolve-skill` non-regression rule.

## Interpretation

Delivered quality gates the candidate. Automatic route exactness does not.

For each non-manual task the runner exposes Core and each root-to-node capability ceiling. The analyzer marks every stable passing ceiling, removes qualified descendants whose ancestor already passes, and reports the remaining set as the task's minimum-sufficient set. More than one minimum node is allowed.

Adaptive traces are then compared with that derived set:

- `exact_minimum` — adaptive disclosure stopped on a derived minimum node;
- `over_disclosure` — it went deeper than a sufficient ancestor;
- `under_disclosure` — it stopped above a node needed by the ceiling evidence;
- `alternate_branch` — it selected a different branch;
- `quality_gap` — no current node ceiling solves the task reliably.

These are topology diagnostics. Persistent disagreement should first trigger a tree-boundary review, not prompt wording patches that force a historical label.

Manual modes have a different contract: ordinary tasks must have zero spontaneous manual activation; explicit Decision or Clarification requests must load the corresponding `references/manual/` mode.

Execution-state diagnostics have another contract: schema/merge/rollback mechanics are deterministic, while usefulness and overhead must be tested on model-backed long-horizon cases. Do not reinterpret state activation as an expected automatic route.

## Historical baselines

- `progressive_validation.py`, `progressive_cases.py`, and `ladder_analysis.py` remain for reproducing the previous fixed E/R and flat Event Router experiments.
- `results/progressive-tree/` and `../evolution/rejected/` preserve the rejected fixed-depth evidence.
- `results/v1.5/` preserves the accepted flat-router evidence and is the baseline frozen by `tree_topology.json`.

Do not silently rewrite historical case contracts to make the new tree appear better. New topology or runtime-substrate changes require a frozen candidate, appropriate mechanism ablation, and real-repository evidence.
