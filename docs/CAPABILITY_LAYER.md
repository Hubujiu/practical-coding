# Capability Layer

Practical Coding separates policy from providers:

- the **execution tree** decides how much engineering reasoning is needed;
- the **Retrieval tree** decides which information problem remains unresolved;
- the **capability layer** supplies replaceable implementations;
- the **execution output layer** compacts noisy command results without changing semantics.

A provider name must never become a Retrieval node. Runtime policy remains valid when a provider is replaced or unavailable.

## Active dependency-enabled benchmark profile

The model-backed dependency profile requires all three providers below. It pins accepted versions in `benchmarks/capability_manifest.json`; the runner fails before creating comparison cells when a binary is missing, its probe fails, or its observed version does not match the frozen profile.

| Role | Required provider | Used by | Boundary |
|---|---|---|---|
| Ranked retrieval | `zg` from `@zvec/zvec-grep` 0.2.0 | R1 and bounded R2 discovery | Supplies hybrid semantic + lexical candidates; current source remains authoritative. |
| Structural retrieval | `codebase-memory-mcp` 0.10.8 | R3 | Supplies graph relationships; current source and index coverage must be checked. |
| Execution output compaction | `rtk` 0.47.0 | shell/test/build/Git transport | Compresses output while preserving command meaning, status, failures, and required evidence. |

The executable contract is machine-readable in `benchmarks/capability_manifest.json`.

## Runtime fallback versus benchmark requirements

Normal Skill use must remain portable. When ranked or graph retrieval is absent, the current node falls back to bounded repository-native search. Output compaction may also be absent without changing task semantics.

The dependency-enabled benchmark intentionally does **not** exercise that absence path. It asks whether the proposed tree benefits from concrete mature capabilities, so missing providers are an infrastructure failure rather than a fallback case. Fallback behavior is covered by deterministic contract tests and may receive a separate ablation; it is not mixed into provider-enabled cost comparisons.

## Two-phase measurement contract

Every model-backed comparison cell has two phases.

### 1. Setup — recorded separately, never compared

Before the model prompt, the runner:

1. verifies every required executable;
2. runs provider probes;
3. initializes local embedding/model assets when needed;
4. builds the workspace `zg` index and runs one unmeasured query to warm the query path;
5. builds the Codebase Memory graph and warms its daemon/CLI path;
6. warms declared repository dependencies and first-build/test caches;
7. verifies the workspace is still clean.

Setup commands, output bytes, and elapsed time are written to `capability-setup.json`. They are marked `included_in_comparison: false`. No setup token estimate is produced, and setup work occurs before Codex is started, so it cannot enter transcript token, tool-call, or measured wall-time fields.

### 2. Measured execution — compared

Only after setup succeeds does the runner start Codex and collect:

- input, cached-input, output, reasoning-output, and total tokens;
- model-visible tool calls;
- measured wall time;
- answer quality and routing trace.

Every arm for the same task receives the same preinitialized provider note and the same repository warm-up contract. A baseline may choose not to use a provider, but it does not receive a colder environment.

## Isolation

Codebase Memory owns an account-level daemon, so concurrent cells must share one cache cohort. By default the runner inherits the host's existing `CBM_CACHE_DIR` (or the provider default); an operator may set `PRACTICAL_BENCHMARK_CBM_CACHE_DIR` once for the whole run. The selected cohort is recorded in every setup receipt. Each frozen workspace has a distinct absolute path and is indexed before measurement. Workspace-local zvec indexes are excluded through `.git/info/exclude`, never committed to the frozen repository, and checked after setup with `git status --porcelain`.

RTK remains outside both trees. On hosts with hard command hooks the execution adapter can be transparent. Codex currently receives the same thin provider instruction in every arm, because RTK's Codex integration is rules-file based; provider usage is recorded rather than inferred from the selected Retrieval stage.

A provider setup failure aborts the run. The runner must not silently continue with a different capability surface, because that would invalidate paired cost comparison.
