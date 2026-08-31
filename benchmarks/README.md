# Practical Coding benchmark chain

The active release candidate uses one Core, a Debugging/Decision/Implementation Event Router, and orthogonal retrieval. The rejected E/R depth and specialist-leaf experiment remains historical evidence under [`results/progressive-tree/`](results/progressive-tree/) and [`../evolution/rejected/`](../evolution/rejected/).

## Active questions

1. Does the Skill deliver a correct, safe, reachable result?
2. Does it load the one reasoning module required by the present unresolved event—and no module for Direct work?
3. Does retrieval stop at the cheapest sufficient capability?
4. Does requirements interviewing remain at zero spontaneous activation?

## Iteration versus release

Use `n=1` while changing mechanisms or scorer contracts. Run the complete `n=3` matrices only after focused n=1 evidence supports release.

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
pwsh -NoProfile -File benchmarks/run.ps1 -ProgressiveSelfTest
```

Current-only public matrix:

```powershell
python benchmarks/run_catalog.py --profile full --runs 1 --workers 3 `
  --arm practical-current --arm practical-native `
  --output benchmark-results/public-n1
```

Current-only real-repository held-out:

```powershell
python benchmarks/progressive_validation.py --phase all --current-only --runs 1 --workers 3 `
  --output benchmark-results/heldout-n1
```

Change `--runs 1` to `--runs 3` only for the frozen final candidate.

## Interpretation

- Delivery and Debug grade delivered behavior, safety, and build evidence.
- Decision grades compact two-turn convergence.
- Router grades reasoning selection and retrieval separately.
- Native Behavior verifies actual Skill discovery and module isolation.
- Held-out tasks use frozen commits from three real repositories and mechanically grade evidence coverage, executable probes, clean workspaces, event/retrieval traces, and spontaneous requirements interviewing.

Historical reports are version-specific. Offline comparison with v1.2 is non-paired unless old and new arms are rerun together in one frozen matrix.
