# Embedded Codebase Memory Helper

`runtime/codebase_memory.py` is the public graph-helper entry point bundled with Practical Coding. It is **not** a second agent runtime: the Agent Skill is `SKILL.md` plus the reference modules, and the agent invokes this helper only when the Skill routes a task to Codebase Memory.

The graph engine lives in `runtime/_codebase_memory_impl.py`. The public entry point adds consistent discovery filtering and per-project mutation locking around that engine.

It has no third-party Python dependencies and does not require the upstream Codebase Memory MCP server.

## Runtime requirement

A usable Python 3 environment is required. Resolve the command in this order where applicable:

```text
python
python3
py -3    # Windows launcher
```

If Python is unavailable, **do not change** `.practical-coding.yaml`. The project preference and the current machine's Python availability are separate facts. The coding agent should continue with ordinary source search and explicitly report that Codebase Memory was not used for the task because no usable Python 3 environment was available.

Do not automatically install Python or repeatedly retry within the same task/session.

## Project preference

`.practical-coding.yaml` is read by the Agent Skill before deciding whether to invoke this helper:

```yaml
version: 1
codebase_memory:
  enabled: true
```

The preference is persistent. When the file is missing and graph navigation would materially help, the agent asks once and persists either `enabled: true` or `enabled: false`. The helper itself intentionally does not parse or enforce this file; a direct manual CLI invocation bypasses Skill routing.

## Commands

```bash
python codebase_memory.py --repo /path/to/project index
python codebase_memory.py --repo /path/to/project index --verify-hashes
python codebase_memory.py --repo /path/to/project index --full-rebuild
python codebase_memory.py --repo /path/to/project status
python codebase_memory.py --repo /path/to/project architecture
python codebase_memory.py --repo /path/to/project search SymbolName
python codebase_memory.py --repo /path/to/project trace SymbolName --direction both --depth 3
python codebase_memory.py --repo /path/to/project impact --git-diff
python codebase_memory.py --repo /path/to/project query "SELECT name FROM symbols" --budget-ms 1000
```

Replace `python` with the resolved Python 3 command when needed.

The SQLite database is stored in the user's cache directory, not in the project.

## Discovery filtering

Candidate files are filtered against the always-skip directory policy regardless of whether discovery comes from `git ls-files` or a filesystem walk. This prevents tracked dependency/build/cache trees such as `vendor`, `node_modules`, `dist`, `target`, and similar upstream-derived exclusions from entering the graph merely because Git tracks them.

The filtering policy is adapted from MIT-licensed `DeusData/codebase-memory-mcp`; see `../THIRD_PARTY_NOTICES.md`.

## Concurrent indexing

Only graph-mutating `index` operations take a per-project advisory lock. The lock file is stored beside the cached SQLite database, so it does not pollute the project tree. A second concurrent writer waits briefly and then exits with an explicit message instead of racing the same graph database.

Read-only status/search/trace/impact/query operations do not take the writer lock. This is a lightweight adaptation of upstream Codebase Memory's per-project mutation-lock design; Practical Coding does not bundle the upstream coordination daemon.

## Incremental refresh

Normal `index` uses stored `mtime_ns` and file size as a no-op fast path. Files whose metadata is unchanged are not re-read or hashed. When metadata changes, SHA-1 avoids reparsing content that is still identical.

Use `--verify-hashes` when timestamps or file metadata may be unreliable. It hashes every candidate source file before deciding whether reparsing is needed.

Call-edge resolution is incremental: changed caller files and calls whose target symbol names were added, removed, or replaced are re-resolved. Other call edges remain untouched.

Use `--full-rebuild` as the correctness oracle. It discards graph rows and rebuilds the graph from source, which is useful for verification and CI comparisons against incremental state.

## Parsing scope

Python uses the standard-library AST. Other recognized source languages use lightweight syntax-oriented extraction and are best-effort discovery only.

The mature upstream project is materially stronger here because it bundles Tree-sitter grammars and Hybrid LSP semantic resolution. Practical Coding deliberately does not try to recreate that stack with growing regex complexity. Treat graph results as discovery evidence and verify decisive source code before exact or exhaustive claims.

## Raw SQL limits

`query` opens the graph read-only, enables SQLite `query_only`, limits returned rows, and enforces a wall-clock execution budget through SQLite's progress handler. The default budget is 1000 ms and is clamped to a maximum of 5000 ms.
