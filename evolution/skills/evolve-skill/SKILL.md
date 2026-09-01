---
name: evolve-skill
description: "Explicit maintenance skill for proposing one wiki-informed Practical Coding change, adding/fixing its benchmark first, and accepting it only through a non-regression validation gate. Never activate automatically."
license: MIT
metadata:
  author: Hubujiu
  version: "1.0"
---

# Evolve Skill

Activate this maintenance skill only when the user explicitly asks to evolve, optimize, refine, split, merge, deepen, collapse, or otherwise update Practical Coding from accumulated evolution knowledge. It is outside the automatic coding router tree.

The wiki is persistent evidence. Runtime Skill changes are reversible candidates.

## Preconditions

- Work on an `experiment/*` branch or another explicitly designated evolution branch.
- Read `evolution/wiki/index.md` and `evolution/wiki/skill-impact.md` first.
- Read only the relevant wiki pages and evidence receipts/benchmark artifacts needed to diagnose the mechanism.
- Do not repeat a previously rejected intervention unless new evidence directly addresses its recorded failure mode.

## Evolution Loop

1. **Choose one atomic proposal.** Target one runtime skill/node/boundary or return `no_action`. Prefer a patch to an existing node over a new node when the current node is partially correct.
2. **Freeze the hypothesis before seeing candidate validation.** Create/update one file under `evolution/experiments/` containing: evidence pointers, causal claim, observable preload/activation signal, exact target, proposed patch shape, expected benefit, falsifier, baseline ref, benchmark plan, and acceptance criteria. Do not backfill the hypothesis after results are known.
3. **Freeze or add the benchmark before applying the runtime patch.** New behavior needs at least one positive case and one boundary/negative case when applicable. The case contract and deterministic scorer/oracle must agree. Do not tune a scorer to reward the candidate.
4. **Run the baseline on the frozen benchmark.** Record the exact commit/ref, model, harness, repetitions, cases, scorer version, and quality/cost metrics.
5. **Apply the smallest candidate patch.** Change only the targeted Skill/tree surface needed to exploit the wiki-supported signal. Keep the proposal atomic so rollback and causal attribution remain possible.
6. **Run the candidate on the same frozen benchmark.** Use the same model, harness, repetitions, cases, and scorer. Re-run the existing relevant regression suite as well. If a genuine scorer defect is discovered, fix it, invalidate both affected results, and rerun baseline and candidate from scratch.
7. **Gate on delivered quality, not route aesthetics.** Accept only if all required correctness/safety/reachability scores are not lower than baseline, the new benchmark score is not lower than baseline, spontaneous manual activation is not worse, and no required regression gate becomes indeterminate. For statistically noisy model benchmarks, require the repository's configured repeated-run/significance rule rather than accepting a single favorable sample.
8. **Rollback on any quality regression.** If a required score is worse or the gate is indeterminate, revert the runtime candidate. Keep valid raw receipts/wiki knowledge and the frozen benchmark; record the rejected diff and reason under `evolution/rejected/` and `evolution/wiki/skill-impact.md`.
9. **Record accepted impact.** If the gate passes, update `evolution/wiki/skill-impact.md` with proposal metadata, target, diff/commit, baseline and candidate scores, benchmark artifact, and `Accepted`. Append the outcome to `evolution/wiki/log.md` and update affected pattern status.

## Non-Regression Rule

A change is not complete because it sounds better. It is complete only after the candidate has been evaluated against the same frozen evidence as its baseline and every required quality gate is equal or better. Cost improvements may break a quality tie; cost savings never compensate for lower required correctness or safety.

## Anti-Overfitting Rules

- Training/calibration evidence may shape a proposal; held-out evidence gates it.
- Do not inspect held-out failures and then edit the candidate without starting a new iteration/hypothesis.
- Do not change route labels merely to match historical labels; use parent-versus-child capability lift and delivered quality.
- Do not promote a new child because a noun appears in the task; require an observable pre-load signal and independent lift.

Finish with the hypothesis file, benchmark added/changed, baseline result, candidate result, accepted/rejected decision, and final runtime commit/ref. If rejected, state explicitly that the runtime patch was rolled back while wiki knowledge remained.
