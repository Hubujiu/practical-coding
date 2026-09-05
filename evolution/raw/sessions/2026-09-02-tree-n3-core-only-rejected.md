# Receipt — Core-only paired n=3 rejected

- Candidate commit: `230522fa914e50e219547f64607ee68383596660`
- Artifact: `benchmark-results/tree-final-230522f-20260902`
- Completeness: 174/174 determinate cells
- Adaptive, frozen v1.5, no-skill: each 45/45
- Core ceiling: 39/39
- Adaptive trace/manual discipline: perfect
- Adaptive mean tokens/duration/tools: 278,578.02 / 76.73s / 7.82
- v1.5 mean tokens/duration/tools: 245,327.98 / 72.69s / 7.64

The collapse preserved quality but regressed every recorded cost metric. It is rejected; commit `5545329` reverted the runtime/topology change and restored the isolated leaf candidate.
