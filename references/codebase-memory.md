# Structured Codebase Memory

Load this module only when structured code navigation is worth its indexing and context cost. It is an optional evidence source, not a mandatory workflow stage.

## Default Provider

The default provider is [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp), an MIT-licensed local code-intelligence backend built around persistent structural indexes and graph queries.

Practical Coding intentionally does **not** vendor the provider runtime. Reuse the installed MCP server or its one-shot CLI instead of copying its daemon, UI, parser bundle, semantic model, or storage engine into this skill.

If future changes copy or substantially adapt upstream source code, preserve the upstream MIT copyright and license notice as required by that license.

## Activation Gate

Use codebase memory when at least one of these is true:

- the repository is large, multi-module, monorepo, microservice-oriented, or otherwise expensive to navigate repeatedly;
- the task asks who calls a symbol, what a change affects, how modules connect, or where an execution path crosses boundaries;
- architecture discovery would otherwise require reading many unrelated files;
- multiple agents or repeated sessions are re-discovering the same structural facts.

Skip it when targeted source search is cheaper, including:

- copy, CSS, rename, or obvious local edits;
- a small demo or one-off script;
- a task whose relevant files and execution path are already known;
- situations where the index is unavailable and creating it would cost more than direct inspection.

## Project Configuration

Practical Coding recognizes one small project-level contract:

```yaml
version: 1
codebase_memory:
  enabled: true
  provider: codebase-memory-mcp
```

The file lives at `.practical-coding.yaml` in the project root.

Keep provider-specific settings in the provider's own configuration. Do not mirror every Codebase Memory option into Practical Coding.

Behavior:

- `enabled: false` — do not query, install, or index codebase memory for this project.
- `enabled: true` — codebase memory may be used when the current task benefits from it.
- missing config — skip silently for cheap/local work; if a graph would materially help, ask the user once whether to enable it and persist the answer only when a durable project setting is wanted.

Enabling this setting is permission to **use** an available provider when useful. It is not permission to install software, start background watchers, commit graph artifacts, or make unrelated project changes.

## Provider Availability

Prefer an already-configured MCP provider. If the MCP tools are unavailable but the `codebase-memory-mcp` executable is already installed, its one-shot CLI is an acceptable fallback.

Do not block the coding task on Codebase Memory. If the provider is unavailable or indexing fails, fall back to ordinary source search and direct reads.

Do not automatically install the provider. Ask before installation because it is external executable software that reads the repository and may write agent configuration or local indexes.

## Query Strategy

Use the narrowest graph operation that answers the structural question.

| Need | Preferred provider operation |
|---|---|
| Check whether the project is indexed/fresh | `list_projects`, `index_status` |
| Create or refresh the index | `index_repository` |
| Understand packages, routes, hotspots, boundaries | `get_architecture` |
| Find symbols/files by structural properties | `search_graph` |
| Trace callers/callees | `trace_path` |
| Map a Git diff to affected symbols and blast radius | `detect_changes` |
| Read the indexed source for a known symbol | `get_code_snippet` |
| Ask a relationship question not covered by built-ins | `get_graph_schema` then `query_graph` |
| Grep indexed project text | `search_code` |

Use a simple two-level discipline adapted from Codebase Memory's own agent guidance:

### Discovery

Use a few narrow structural queries to locate likely symbols, paths, callers, packages, routes, or affected areas. Positive discovery can be provisional.

Do not turn every task into exhaustive graph analysis.

### Verification

Before making an exact or negative claim such as “nothing else calls this,” “only these files are affected,” or “this path is complete”:

- confirm the project/index identity and freshness;
- inspect pagination or query scope rather than assuming the first result set is complete;
- use provider coverage checks when the installed provider exposes them;
- read the decisive source ranges directly before editing or making high-confidence claims.

The graph is an acceleration structure, not the final authority. Source code and current project state win when they disagree with an index.

## Index Lifecycle

Index only when the current task benefits from it and the user has consented to using Codebase Memory.

Prefer explicit/on-demand indexing as the Practical Coding default. Do not enable auto-indexing or watchers merely because the provider supports them.

A provider may support a shared `.codebase-memory/graph.db.zst` artifact. Treat that as a separate project decision: do not commit it unless the user or project explicitly wants a shared graph snapshot.

After source changes, rely on the provider's documented incremental refresh when available, but verify freshness before impact analysis or exhaustive structural claims.

## Boundaries with Other Modules

Codebase Memory is independent:

- architecture discovery can use Codebase Memory without loading Decision;
- a local edit can use Implementation without Codebase Memory;
- debugging can use graph traces as evidence without making the graph mandatory;
- Verification may use graph impact information, but risk determines verification depth, not graph availability.

Do not record reconstructable graph facts as durable decision documentation. Persist only reasons and constraints that cannot be cheaply reconstructed from source, the graph, or Git history.
