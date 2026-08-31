# Release validation protocol — event-router restoration

This protocol freezes the final validation for `experiment/progressive-ladders` after n=1 iteration.

## Candidate contract

- Core plus Direct default;
- exactly three adaptive reasoning modules: Debugging, Decision, Implementation;
- retrieval orthogonal and cheapest-sufficient;
- requirements interviewing explicit-only;
- no numeric execution/retrieval runtime depths or specialist leaves.

## Iteration gate

Use n=1 while changing a mechanism. Save the full result, classify failures as infrastructure, scorer/oracle, stochastic, routing, or genuine capability failures, and record reusable lessons under `evolution/`. Never add case-specific nouns to runtime text.

## Final gate

The candidate must be committed and unchanged before both commands run:

```powershell
python benchmarks/run_catalog.py --profile full --runs 3 --workers 3 `
  --arm practical-current --arm practical-native `
  --output benchmark-results/event-router-final-public

python benchmarks/progressive_validation.py --phase all --current-only --runs 3 --workers 3 `
  --output benchmark-results/event-router-final-heldout
```

Required evidence:

- zero indeterminate cells and at least three determinate repetitions per cell;
- no Delivery correctness/safety/build regression;
- Debug, Decision, and Native Behavior stable enough for a release claim;
- Router reasoning and retrieval reported separately;
- at least 20 held-out real tasks across multiple repositories;
- zero spontaneous requirements-interview activation;
- held-out quality and routing failures individually classified;
- raw machine paths excluded from published compact artifacts.

Historical v1.2 reports may be compared offline, but this current-only cycle cannot make a paired superiority claim against v1.2, no-skill, Ponytail, or combined skill arms.

## Merge gate

Update the formal README and compact result artifacts from the final reports, run all unit/self/Skill validation, push the branch, and require PR CI success. If a genuine quality or stable reasoning regression remains, return to n=1 iteration and freeze the next mechanism change before editing runtime rules.
