# Tree discriminator benchmark

This is the cheap routing-language diagnostic for staged automatic children. It complements, but never replaces, `tree_validation.py` capability ceilings and executable outcome verifiers.

Run a harness check first:

```powershell
python benchmarks/tree_discriminator_validation.py --self-test
```

Then run the frozen discriminator matrix:

```powershell
python benchmarks/tree_discriminator_validation.py --runs 3 --workers 3
```

The suite exposes only one parent node and a task summary. It does **not** expose child bodies. The model must return the immediate child name or `parent`.

Cases include positive signals, ordinary parent-stay negatives, and sibling-confusion hard negatives. The report emits per-parent accuracy plus per-child Trigger recall, Boundary specificity, false-trigger counts, token use, tool calls, and duration.

These labels are allowed here because the suite is testing whether the written Local Router distinguishes deliberately constructed boundary examples. They are diagnostic only. A child still needs empirically minimum-sufficient parent-vs-child lift in the real tree benchmark before promotion.
