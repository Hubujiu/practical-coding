# Third-Party Notices

Practical Coding does not vendor the provider source trees or release binaries listed below. Normal Skill use can fall back when a provider is absent. The dependency-enabled benchmark deliberately requires the declared executables so paired runs share one concrete capability surface.

## zvec-ai/zvec-grep

- Project: `zvec-ai/zvec-grep`
- Executable used by the benchmark: `zg`
- Frozen benchmark profile version: `0.2.0`
- Source: https://github.com/zvec-ai/zvec-grep
- License: Apache License 2.0
- Role: local ranked lexical + semantic retrieval for R1 Ranked Discovery and bounded R2 Evidence Expansion.

Provider results are candidate evidence, not repository truth. Material conclusions are checked in current source.

## DeusData/codebase-memory-mcp

- Project: `DeusData/codebase-memory-mcp`
- Executable used by the benchmark: `codebase-memory-mcp`
- Frozen benchmark profile version: `0.10.8`
- Source: https://github.com/DeusData/codebase-memory-mcp
- License: MIT
- Role: graph-aware callers, callees, dependencies, flows, and impact evidence for the R3 Structural Trace leaf.

Benchmark cells create distinct per-workspace graph identities while sharing one explicit account-daemon cache cohort for the run. The selected cohort is recorded; graph identity, freshness, and coverage must be checked, and material paths are verified in current source.

## rtk-ai/rtk

- Project: `rtk-ai/rtk`
- Executable used by the benchmark: `rtk`
- Frozen benchmark profile version: `0.47.0`
- Source: https://github.com/rtk-ai/rtk
- License: Apache License 2.0
- Role: cross-cutting compaction of noisy shell, test, build, and Git output.

Output compaction is infrastructure rather than a Retrieval node. It must preserve command semantics, exit status, failures, and sufficient evidence for the current claim.

## Distribution boundary

The repository records executable probes and setup commands in `benchmarks/capability_manifest.json`, but it does not redistribute provider binaries, embedding models, or cached indexes. Install each provider from its maintained upstream distribution and review its own license, security, data-handling, and configuration documentation.

If Practical Coding later vendors upstream code or carries a source patch, retain all required copyright and license notices with the copied or substantial portions.
