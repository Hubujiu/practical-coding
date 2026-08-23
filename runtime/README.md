# Embedded Codebase Memory Runtime

`codebase_memory.py` is the graph engine bundled with Practical Coding.

It has no third-party Python dependencies and does not require the upstream Codebase Memory MCP server.

## Commands

```bash
python codebase_memory.py --repo /path/to/project index
python codebase_memory.py --repo /path/to/project status
python codebase_memory.py --repo /path/to/project architecture
python codebase_memory.py --repo /path/to/project search SymbolName
python codebase_memory.py --repo /path/to/project trace SymbolName --direction both --depth 3
python codebase_memory.py --repo /path/to/project impact --git-diff
```

The SQLite database is stored in the user's cache directory, not in the project.

Python uses the standard-library AST. Other supported languages use lightweight syntax-oriented extraction. Treat graph results as discovery evidence and verify decisive source code before exact or exhaustive claims.
