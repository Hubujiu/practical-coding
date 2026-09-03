# Retrieval instrumentation: not ready for cost acceptance

Decision: **Inconclusive / infrastructure_indeterminate**. No runtime candidate.

Hypothesis: `../experiments/retrieval-convergence-20260903-1.md`.
Starting remote baseline: `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`.
Frozen instrumentation: `6475c33cca967ffafadf09ee484ed84e2feb49a7`.

The deterministic gate passed 41 tests and the historical replay preserved all
original fields in 252 records. These checks did not establish classification
coverage for the current CLI's PowerShell command rendering.

The fresh n=1 run completed 4/54 cells, all passing quality and trace checks,
before the runner was deliberately stopped. Five completed tool events had
recorded output, but three were classified `other`. Two real source reads were
missed when the shell-rendered `-Command` began and ended with different quote
fragments. This also invalidated first-project-read and whole-file output
attribution. It is a measurement defect, not a task-quality regression.

Raw artifacts remain under `benchmark-results/retrieval-iteration-1-baseline-n1/`.
`partial-results.jsonl` and `termination.json` explicitly retain the incomplete
matrix; no ordinary `results.jsonl` was manufactured to imply completion.
Historical replays were written to a new directory, never over the original.

No Skill rule was changed, no long-tail set was frozen, no candidate model run
was started, and no n=3 result exists. Output/token/tool/latency improvements and
under-retrieval are untested. All runtime files remain at the starting baseline.
The diagnostic instrumentation is retained as requested; its category/convergence
metrics must not authorize acceptance in this version.

Reconsider only after a new independently frozen measurement
repair has general positive/negative tests for shell rendering and a classification
coverage gate. Do not resume this partial run or select favorable historical
cells. This does not reject the prompt-only retrieval hypothesis; it was never
tested.
