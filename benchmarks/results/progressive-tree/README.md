# Progressive capability-tree experiment evidence

This directory records the current-only validation completed on 2026-08-31 for candidate commit `eefb3b79c688ced94273daea6a0af22b74d47022` with `gpt-5.6-luna`, medium reasoning, and three determinate repetitions per cell.

## Verdict

**The candidate did not pass the merge gate.** It retained strong delivery behavior and never activated a manual-only mode spontaneously, but the progressive depth/path hypothesis was not supported:

| Surface | Result | Interpretation |
|---|---:|---|
| Public full regression | 294/294 determinate | Delivery 54/54; Debug 34/42. Legacy Router, Decision, and Native Behavior graders use the pre-tree labels/file names and are not valid E/R-tree scores. |
| Held-out real tasks | 58/66 cells; 18/22 tasks stable-pass | Three frozen repositories, 22 tasks, n=3. |
| Manual-only negative control | 0/66 spontaneous activations | The zero-trigger requirement passed. |
| Held-out routing trace validity | 40/66 | Root/leaf paths were often reported with an incompatible execution level. |
| Held-out exact routing | 21/66 | The adaptive tree did not select the frozen expected E/R/path reliably. |
| Execution minimum sufficient | E0: 6, E1: 1, E2: 0, E3: 1 | E2 was never the lowest sufficient cap in this calibration set. |
| Retrieval minimum sufficient | R0: 1, R1: 7, R2: 0, R3: 0 | R2/R3 were never the lowest sufficient cap in this calibration set. |
| E2 parent to E3 leaf ablation | 7 ties, 1 regression, 0 lifts | The specialist leaves did not earn their added context cost. |

## Historical comparison boundary

The accepted v1.2 report remains the prior published evidence: Router retrieval 106/114, Native Behavior 54/54, and capability regression 75/75. This experiment did **not** rerun v1.2, no-skill, Ponytail, or combined skill arms. The comparison is therefore report-to-report, non-paired, and not a ranking claim.

The current full regression's legacy Router/Decision/Native Behavior failures are primarily schema-oracle incompatibilities: those graders expect the old reasoning labels and filenames such as `implementation.md` and top-level `decision.md`. Delivery and Debug still grade delivered behavior; the eight Debug failures are genuine shared-boundary/sibling-safety misses and remain release blockers.

## Evidence boundary

- The frozen current-only progressive matrix contains 378 determinate cells: 66 held-out, 240 depth-cap, and 72 parent/leaf ablation cells.
- Raw transcripts, workspaces, and the 3 MB result file remain local because they contain machine-specific absolute paths.
- `release-summary.json` is the compact machine-readable publication artifact.
- The incomplete 189/768 comparative run was stopped after the scope changed and is excluded from every conclusion.

