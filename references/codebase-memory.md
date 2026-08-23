# Structured Codebase Memory

Load this module only when structured navigation is worth its indexing and context cost. It is an optional evidence source, not a mandatory workflow stage.

## Embedded Runtime

Practical Coding ships its own lightweight graph runtime:

```text
runtime/codebase_memory.py
```

Installing the skill installs the graph capability. Do **not** require the user to separately install `DeusData/codebase-memory-mcp`, configure an MCP server, run a WebUI, or start a daemon.

The embedded runtime is intentionally narrower than upstream Codebase Memory. It keeps the parts that matter for agent navigation:

- persistent SQLite graph storage;
- file, symbol, import, and call relationships;
- incremental refresh with a file-metadata fast path and content-hash verification;
- architecture summaries;
- symbol search;
- inbound/outbound call tracing;
- changed-file impact analysis;
- bounded read-only SQL for questions not covered by the built-ins.

It deliberately omits:

- MCP transport and client configuration;
- WebUI / 3D graph visualization;
- background daemon and watcher;
- semantic embedding model;
- automatic agent installation/adapters;
- shared graph artifacts;
- the large bundled Tree-sitter/LSP parser set.

The design is inspired by [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp), which is MIT-licensed. The embedded runtime is a lightweight implementation maintained inside Practical Coding rather than a vendored copy of the upstream runtime.

## Runtime Requirements

The runtime uses only the Python standard library: `sqlite3`, `ast`, `re`, `hashlib`, `subprocess`, and related modules.

No `pip install`, network access, API key, MCP registration, database server, or background service is required.

Before invoking the graph runtime, resolve an available Python 3 command in this order where applicable:

```text
python
python3
py -3    # Windows launcher
```

Use whichever command successfully runs Python 3. For example:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index
```

### Python unavailable

If none of the Python commands is available or usable:

1. Tell the user that the embedded Codebase Memory runtime requires Python 3 and that they can install or enable Python to use the graph.
2. Update the project `.practical-coding.yaml` so `codebase_memory.enabled` becomes `false`. Preserve unrelated configuration in the file.
3. If the configuration file did not yet exist because the user had just opted in, create the minimal file with `enabled: false` so the failed capability choice is persisted.
4. Continue the current coding task with normal source search and direct reads. The missing Python environment must not block ordinary coding work.
5. While `enabled: false`, do not keep retrying Python or repeatedly asking the user about Codebase Memory.

The persisted fallback is intentionally simple:

```yaml
version: 1
codebase_memory:
  enabled: false
```

When the user later confirms Python is available and wants Codebase Memory again, change the setting back to `true` and create or refresh the index on demand.

Do not automatically install Python. Environment installation remains a user-controlled system change.

## Activation Gate

Use codebase memory when at least one of these is true:

- the repository is large, multi-module, monorepo, microservice-oriented, or otherwise expensive to navigate repeatedly;
- the task asks who calls a symbol, what a change affects, how modules connect, or where an execution path crosses boundaries;
- architecture discovery would otherwise require reading many unrelated files;
- multiple agents or repeated sessions are re-discovering the same structural facts.

Skip it when targeted source search is cheaper, including:

- copy, CSS, rename, or obvious local edits;
- a small demo or one-off script;
- a task whose relevant files and execution path are already known.

## Project Configuration

Practical Coding recognizes one project-level opt-in:

```yaml
version: 1
codebase_memory:
  enabled: true
```

The file lives at `.practical-coding.yaml` in the project root.

Behavior:

- `enabled: false` — do not index or query the embedded graph for this project and do not repeatedly probe Python availability.
- `enabled: true` — the embedded graph may be used when the current task benefits from it; resolve Python before the first graph invocation.
- missing config — skip silently for cheap/local work; if a graph would materially help, ask once whether to enable it and persist the answer only when a durable project setting is wanted.

Do not add more graph configuration until a real project need requires it.

## Index Storage

The runtime does not write the SQLite graph into the project.

Default cache locations:

- Linux: `${XDG_CACHE_HOME:-~/.cache}/practical-coding/codebase-memory/`
- macOS: `~/Library/Caches/practical-coding/codebase-memory/`
- Windows: `%LOCALAPPDATA%\practical-coding\cache\codebase-memory\`

Set `PRACTICAL_CODING_CACHE_DIR` only when the user/project has a concrete reason to override the cache root.

Each repository gets a stable database name derived from its canonical path.

## Query Strategy

Use the narrowest operation that answers the structural question.

### Index or refresh

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index
```

The first run creates the graph. Normal refresh first trusts unchanged `mtime_ns` plus file size and does not re-read or hash those files. If metadata changed, the runtime hashes the file and reparses only when the content hash changed. Deleted files are removed and only affected call edges are re-resolved.

Run this before structural analysis when the source may have changed.

When timestamps or file metadata may be unreliable, force content verification:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index --verify-hashes
```

`--verify-hashes` hashes every candidate source file before deciding whether parsing is needed. Use it after file copies/restores, unusual build tooling, filesystem timestamp preservation, or when exact freshness matters more than the metadata fast path.

For correctness verification or debugging the incremental index, rebuild graph rows from source:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index --full-rebuild
```

`--full-rebuild` is the correctness oracle for incremental state. Call-edge target selection is deterministic, so an incremental graph and a full rebuild should have the same graph semantics for the same source tree.

### Status

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> status
```

Use this to confirm the graph exists and inspect file/symbol/edge counts.

### Architecture

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> architecture
```

Returns languages, top-level areas, and inbound-call hotspots.

### Search symbols

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> search ProcessOrder
```

Use this before tracing when the symbol name or qualified name is uncertain.

### Trace callers/callees

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> trace ProcessOrder --direction both --depth 3
```

Directions:

- `in` — callers;
- `out` — callees;
- `both` — traverse both directions.

If an unqualified symbol is ambiguous, the runtime returns candidates instead of silently choosing one. Re-run with a qualified name.

### Impact analysis

For current Git changes:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> impact --git-diff
```

For explicit files:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> impact --files src/order.py,src/payment.py
```

Impact combines reverse call edges with lightweight reverse-import evidence.

### Read-only graph query

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> query \
  "SELECT name, qualified_name FROM symbols WHERE kind='function' LIMIT 20" \
  --budget-ms 1000
```

Only `SELECT` and `WITH` queries are accepted. The database is opened read-only with SQLite `query_only`, returned rows are capped, and execution receives a wall-clock budget. The default budget is 1000 ms and is clamped to at most 5000 ms. Do not mutate the graph with ad hoc SQL.

## Parsing Model

Python uses the standard-library AST and therefore has stronger symbol/import/call extraction.

The embedded runtime also recognizes common source extensions for:

- JavaScript / TypeScript / JSX / TSX;
- Java / Kotlin;
- Go;
- Rust;
- C / C++;
- C#;
- PHP;
- Ruby;
- Vue / Svelte;
- Scala;
- Swift.

Those languages currently use lightweight syntax-oriented extraction rather than the upstream project's full Tree-sitter + LSP pipeline.

This is intentional: the runtime is designed to be immediately available with the Skill and remain small. It is not presented as a drop-in replacement for every Codebase Memory feature.

## Evidence Discipline

Use a two-level discipline:

### Discovery

Use the graph to cheaply locate likely symbols, callers, imports, hotspots, and affected areas.

Positive discovery may be provisional. Do not turn every task into exhaustive graph analysis.

### Verification

Before exact, negative, or exhaustive claims such as:

- “nothing else calls this”;
- “only these files are affected”;
- “this is the complete execution path”;

read the decisive source ranges directly and, when relevant, use Git/runtime/test evidence.

The embedded non-Python parsers are intentionally heuristic, and even exact parsers can become stale between index refreshes.

The graph is an acceleration structure, not the final authority. Current source code wins.

## Boundaries with Other Modules

Codebase Memory remains independent:

- architecture discovery can use Codebase Memory without loading Decision;
- a local edit can use Implementation without Codebase Memory;
- Debugging can use graph traces as evidence without making the graph mandatory;
- Verification may use impact information, but risk determines verification depth.

Do not record reconstructable graph facts as durable decision documentation. Persist only reasons and constraints that cannot be cheaply reconstructed from source, graph, or Git history.