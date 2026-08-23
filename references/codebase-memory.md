# Structured Codebase Memory

Load this module only when structured navigation is worth its indexing and context cost. It is an optional evidence source, not a mandatory workflow stage.

## What “runtime” means here

Practical Coding itself is an Agent Skill: the agent loads `SKILL.md` and, when triggered, this reference file. The bundled Python files are only helper programs that the Skill may invoke after routing a task to Codebase Memory.

The public entry point is:

```text
runtime/codebase_memory.py
```

The graph engine implementation is kept behind it at:

```text
runtime/_codebase_memory_impl.py
```

`.practical-coding.yaml` is therefore a **Skill routing preference** read by the agent before it decides whether to call the helper. The helper is not a second agent runtime and does not independently enforce that preference. A user who manually runs `runtime/codebase_memory.py` directly is intentionally bypassing the Skill routing layer.

Installing the Skill installs this lightweight graph capability. Do **not** require the user to separately install `DeusData/codebase-memory-mcp`, configure an MCP server, run a WebUI, or start a daemon.

## Relationship to upstream Codebase Memory

The design is based on the MIT-licensed [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp). Upstream is substantially more capable as a code-intelligence engine: it uses a large bundled Tree-sitter grammar set, Hybrid LSP semantic resolution for major languages, a coordination daemon, watchers, and per-project mutation locks.

Practical Coding should not imitate that production parser stack with an ever-growing pile of regular expressions. The embedded helper keeps only the parts that fit a small, zero-third-party-dependency Skill runtime:

- persistent SQLite graph storage;
- file, symbol, import, and call relationships;
- incremental refresh with a metadata fast path and content-hash verification;
- architecture summaries;
- symbol search;
- inbound/outbound call tracing;
- changed-file impact analysis;
- bounded read-only SQL;
- upstream-style always-skip directory filtering applied consistently to both Git-backed and filesystem discovery;
- upstream-style per-project serialization of graph mutation so concurrent agents do not write the same graph at once.

It deliberately omits:

- MCP transport and client configuration;
- WebUI / 3D graph visualization;
- background daemon and watcher;
- semantic embedding model;
- automatic agent installation/adapters;
- shared graph artifacts;
- the upstream Tree-sitter/LSP parser bundle.

Selected filtering and project-lock behaviour is adapted from upstream. See `THIRD_PARTY_NOTICES.md` for attribution and the MIT notice.

## Runtime Requirements

The embedded helper uses only the Python standard library. No `pip install`, network access, API key, MCP registration, database server, or background service is required.

Before invoking it, resolve an available Python 3 command in this order where applicable:

```text
python
python3
py -3    # Windows launcher
```

Use whichever command successfully runs Python 3:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index
```

### Python unavailable

If none of the Python commands is available or usable:

1. **Do not change** the project's persisted `codebase_memory.enabled` preference. Python availability is an environment fact, not a project preference.
2. Continue the current coding task with normal source search and direct reads. Missing Python must not block ordinary coding work.
3. Explicitly report that Codebase Memory was **not used for this task** because no usable Python 3 environment was available.
4. Do not automatically install Python and do not repeatedly retry within the same task/session.

If the project preference remains `enabled: true`, another task or another machine may try the helper again when Python is available.

## Activation Gate

Use Codebase Memory when at least one of these is true:

- the repository is large, multi-module, monorepo, microservice-oriented, or otherwise expensive to navigate repeatedly;
- the task asks who calls a symbol, what a change affects, how modules connect, or where an execution path crosses boundaries;
- architecture discovery would otherwise require reading many unrelated files;
- multiple agents or repeated sessions are re-discovering the same structural facts.

Skip it when targeted source search is cheaper, including:

- copy, CSS, rename, or obvious local edits;
- a small demo or one-off script;
- a task whose relevant files and execution path are already known.

## Persistent Project Configuration

Practical Coding recognizes one project-level preference:

```yaml
version: 1
codebase_memory:
  enabled: true
```

The file lives at `.practical-coding.yaml` in the project root.

Behavior:

- `enabled: false` — do not index or query the embedded graph for this project and do not probe Python for graph use.
- `enabled: true` — the embedded graph may be used when the current task benefits from it; resolve Python before the first graph invocation in the current environment.
- missing config + cheap/local task — skip silently; do not ask merely because the capability exists.
- missing config + graph materially useful — ask the user once whether to enable Codebase Memory **for this project**, then persist the answer as `enabled: true` or `enabled: false`, preserving unrelated configuration.

Persist both answers. “Ask once” is a project-level promise, so a negative answer must also survive future sessions.

Do not change `enabled` merely because Python is missing on one machine or in one sandbox.

Do not add more project graph configuration until a demonstrated need requires it.

## Index Storage and Concurrency

The SQLite graph is stored in the user's cache directory, not in the project:

- Linux: `${XDG_CACHE_HOME:-~/.cache}/practical-coding/codebase-memory/`
- macOS: `~/Library/Caches/practical-coding/codebase-memory/`
- Windows: `%LOCALAPPDATA%\practical-coding\cache\codebase-memory\`

Set `PRACTICAL_CODING_CACHE_DIR` only when there is a concrete reason to override the cache root.

Each repository gets a stable database name derived from its canonical path. A small advisory lock file is stored beside that database. Only graph-mutating `index` operations take the exclusive project lock; read-only status/search/trace/impact/query operations remain independent. If another index writer holds the project lock, a second writer waits briefly and then exits with an explicit “another index operation is already running” message instead of racing SQLite writes.

This is a lightweight analogue of upstream Codebase Memory's per-project mutation locking. Practical Coding does not copy the upstream coordination daemon.

## Discovery Filtering

Always-skip directory rules are applied **after candidate discovery as well as during filesystem walking**. This matters because `git ls-files` can still return tracked files under directories such as `vendor`, `dist`, `target`, cache trees, or other generated/dependency areas even when those names would normally be ignored during a raw directory walk.

The skip set is adapted from the mature upstream discovery policy and intentionally focuses on dependency trees, build artifacts, caches, deployment outputs, IDE state, and generated tool state. It does not attempt to reproduce upstream's complete discovery pipeline.

## Query Strategy

Use the narrowest operation that answers the structural question.

### Index or refresh

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index
```

The first run creates the graph. Normal refresh first trusts unchanged `mtime_ns` plus file size and does not re-read or hash those files. If metadata changed, the runtime hashes the file and reparses only when content changed. Deleted files are removed and only affected call edges are re-resolved.

When timestamps or file metadata may be unreliable:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index --verify-hashes
```

For correctness verification or debugging incremental state:

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> index --full-rebuild
```

`--full-rebuild` is the correctness oracle for incremental graph state.

### Status

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> status
```

### Architecture

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> architecture
```

### Search symbols

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> search ProcessOrder
```

### Trace callers/callees

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> trace ProcessOrder --direction both --depth 3
```

If an unqualified symbol is ambiguous, use a qualified name.

### Impact analysis

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> impact --git-diff
python <skill-root>/runtime/codebase_memory.py --repo <project-root> impact --files src/order.py,src/payment.py
```

Impact combines reverse call edges with lightweight reverse-import evidence.

### Read-only graph query

```bash
python <skill-root>/runtime/codebase_memory.py --repo <project-root> query \
  "SELECT name, qualified_name FROM symbols WHERE kind='function' LIMIT 20" \
  --budget-ms 1000
```

Only `SELECT` and `WITH` are accepted. The graph is opened read-only with SQLite `query_only`, returned rows are capped, and execution receives a wall-clock budget.

## Parsing Model

Python uses the standard-library AST and has the strongest extraction in the bundled helper.

The helper also **recognizes** common source extensions for JavaScript / TypeScript / JSX / TSX, Java / Kotlin, Go, Rust, C / C++, C#, PHP, Ruby, Vue / Svelte, Scala, and Swift. These non-Python paths use lightweight syntax-oriented extraction and are **best-effort discovery only**.

Do not describe this as parser parity with upstream Codebase Memory. Upstream's substantially stronger multi-language quality comes from its Tree-sitter and Hybrid LSP stack, which is not meaningfully separable into a few lightweight regex fixes. Do not keep adding parser complexity merely to inflate a supported-language claim.

## Evidence Discipline

Use the graph for cheap discovery of likely symbols, callers, imports, hotspots, and affected areas.

Before exact, negative, or exhaustive claims such as:

- “nothing else calls this”;
- “only these files are affected”;
- “this is the complete execution path”;

read the decisive source ranges directly and, when relevant, use Git/runtime/test evidence.

The graph is an acceleration structure, not the final authority. Current source code wins.

## Boundaries with Other Modules

Codebase Memory remains independent:

- architecture discovery can use Codebase Memory without loading Decision;
- a local edit can use Implementation without Codebase Memory;
- Debugging can use graph traces as evidence without making the graph mandatory;
- Verification may use impact information, but risk determines verification depth.

Do not record reconstructable graph facts as durable decision documentation. Persist only reasons and constraints that cannot be cheaply reconstructed from source, graph, or Git history.
