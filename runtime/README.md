# Embedded Codebase Memory Runtime

`codebase_memory.py` is the graph engine bundled with Practical Coding.

It has no third-party Python dependencies and does not require the upstream Codebase Memory MCP server.

## Runtime requirement

A usable Python 3 environment is required. Resolve the command in this order where applicable:

```text
python
python3
py -3    # Windows launcher
```

If Python is unavailable, the coding agent should explain that Python 3 is required for the graph, set the project's `.practical-coding.yaml` to:

```yaml
version: 1
codebase_memory:
  enabled: false
```

and continue the task with ordinary source search. Do not automatically install Python or repeatedly retry while the project setting remains disabled.

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

## Incremental refresh

Normal `index` uses stored `mtime_ns` and file size as a no-op fast path. Files whose metadata is unchanged are not re-read or hashed. When metadata changes, SHA-1 is used to avoid reparsing content that is still identical.

Use `--verify-hashes` when timestamps or file metadata may be unreliable. It hashes every candidate source file before deciding whether reparsing is needed.

Call-edge resolution is incremental: changed caller files and calls whose target symbol names were added, removed, or replaced are re-resolved. Other call edges remain untouched.

Use `--full-rebuild` as the correctness oracle. It discards graph rows and rebuilds the graph from source, which is useful for verification and CI comparisons against incremental state.

## Raw SQL limits

`query` opens the graph read-only, enables SQLite `query_only`, limits returned rows, and enforces a wall-clock execution budget through SQLite's progress handler. The default budget is 1000 ms and is clamped to a maximum of 5000 ms.

Python uses the standard-library AST. Other supported languages use lightweight syntax-oriented extraction. Treat graph results as discovery evidence and verify decisive source code before exact or exhaustive claims.
