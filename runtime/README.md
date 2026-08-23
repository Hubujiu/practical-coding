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
python codebase_memory.py --repo /path/to/project status
python codebase_memory.py --repo /path/to/project architecture
python codebase_memory.py --repo /path/to/project search SymbolName
python codebase_memory.py --repo /path/to/project trace SymbolName --direction both --depth 3
python codebase_memory.py --repo /path/to/project impact --git-diff
```

Replace `python` with the resolved Python 3 command when needed.

The SQLite database is stored in the user's cache directory, not in the project.

Python uses the standard-library AST. Other supported languages use lightweight syntax-oriented extraction. Treat graph results as discovery evidence and verify decisive source code before exact or exhaustive claims.
