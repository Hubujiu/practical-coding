# Release validation protocol — evolvable local-router tree

This protocol freezes final validation for `experiment/evolvable-router-tree` after n=1 mechanism iteration.

## Frozen candidate

- Core owns only Debugging and Implementation as automatic children.
- Debugging and Implementation are leaves; repeated ablation did not earn a depth-2 child.
- Decision and Clarification remain explicit-only manual modes.
- Retrieval remains orthogonal to execution-tree depth.
- The deterministic scorer normalizes equivalent semantic acts, outcome wording, ordinary inflections, and Windows/POSIX reference paths without changing the frozen task prompts.

Qualified n=1 artifact: `benchmark-results/tree-delivery-n1-retired-isolated-20260902` (58/58 determinate cells; adaptive 15/15; every capability ceiling 13/13; all traces/manual contracts valid).

## Iteration gate

Use n=1 while changing runtime wording, topology, cases, scorer contracts, or evidence normalization. Save each complete artifact, classify every failure, and write an immutable receipt before consolidating the reusable mechanism into `evolution/wiki/`. A scorer correction invalidates all affected model-backed results; rerun the complete matrix in a fresh directory.

## Final paired gate

Commit and freeze runtime, topology, cases, scorer, repository refs, model, and harness before running:

```powershell
python benchmarks/tree_validation.py --runs 3 --workers 3 `
  --output benchmark-results/tree-final

python benchmarks/tree_analysis.py benchmark-results/tree-final/results.jsonl `
  --output benchmark-results/tree-final/analysis.json
```

Required evidence:

- every expected cell exists, is determinate, and has three unique repetitions;
- adaptive delivered quality is strictly better than the frozen v1.5 baseline on the same cases and no worse than no-skill on required correctness/safety/reachability;
- zero adaptive trace failures and zero spontaneous manual-mode activation;
- both explicit manual tasks load the requested manual mode in every repetition;
- parent-versus-child capability evidence uses all three repetitions before retaining, removing, promoting, or merging a node;
- raw machine paths remain in ignored artifacts and are excluded from published compact reports;
- report version, commit, model, harness, frozen repository refs, cell counts, pass counts, noninferiority results, and limitations separately.

Router exactness and topology diagnostics do not override delivered quality. A favorable n=1 cell or incomplete split rerun is not release evidence.

## Merge gate

Update the formal README and compact result artifacts from the complete n=3 report, run all unit/self/Skill validation, and require PR CI success before merge. If a genuine stable quality regression or unearned staged node remains, return to a new frozen n=1 hypothesis and repeat the gate; do not edit the n=3 artifact in place.
