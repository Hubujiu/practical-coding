# Rejected changes

Keep failed or regressive Skill experiments here even after runtime text is rolled back.

Each record should state:

- what was tried;
- why it was plausible;
- frozen evidence/benchmark IDs;
- correctness/safety/build effect;
- over/under-escalation and cost effect when available;
- why it was rejected;
- the explicit condition under which it is worth reconsidering.

The purpose is to prevent repeated rediscovery of the same failed architecture or wording change.

## Archived experiments

- [`execution-state/`](execution-state/) — retired explicit execution-state/history-free runtime, host transport, and four-arm model-gate experiment.
- [`progressive-capability-tree.md`](progressive-capability-tree.md) — rejected fixed-depth progressive capability tree.
