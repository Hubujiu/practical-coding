# Practical Coding benchmark chain

The active experiment uses an evolvable local-router tree. Core is depth 0 and knows only its immediate automatic children. Each loaded node owns only its own next-level router. Decision and requirements interviewing are explicit-only manual modes outside the automatic tree. Retrieval remains orthogonal.

The accepted v1.5 flat Event Router and the rejected fixed E/R ladder remain historical baselines. Do not use their fixed reasoning labels, numeric depths, or gold route expectations as the acceptance oracle for this experiment.

## Active questions

1. Does the candidate deliver a correct, safe, evidence-backed result at least as reliably as the v1.5 baseline and no-skill arm?
2. Which automatic nodes are actually minimum-sufficient under parent-versus-child capability ceilings?
3. Does adaptive disclosure stop at a minimum-sufficient node without spontaneous manual Decision or Clarification activation?
4. Do repeated failures or sibling ambiguity justify growing, splitting, merging, promoting, collapsing, or removing a node?
5. Does retrieval stop at the cheapest sufficient capability independently of execution depth?

## Tree experiment

The runtime topology is data, not a scorer constant:

- `tree_topology.json` — current root, nodes, parent/child edges, depth, manual modes, and frozen baseline ref;
- `tree_cases.py` — topology-neutral real-repository tasks; no expected automatic route or E0-E3 label;
- `tree_validation.py` — runs no-skill, v1.5 baseline, adaptive candidate, and capability ceilings for every automatic node;
- `tree_analysis.py` — derives minimum-sufficient node sets, adaptive disclosure diagnostics, node marginal lift, and topology-change candidates;
- `TREE_EVOLUTION.md` — interpretation and mutation rules.

Iteration uses `n=1` while changing topology, node content, or scorer contracts:

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

## Historical baselines

- `progressive_validation.py`, `progressive_cases.py`, and `ladder_analysis.py` remain for reproducing the previous fixed E/R and flat Event Router experiments.
- `results/progressive-tree/` and `../evolution/rejected/` preserve the rejected fixed-depth evidence.
- `results/v1.5/` preserves the accepted flat-router evidence and is the baseline frozen by `tree_topology.json`.

Do not silently rewrite historical case contracts to make the new tree appear better. New topology changes require a frozen candidate, parent-versus-child ablation, and real-repository evidence.
