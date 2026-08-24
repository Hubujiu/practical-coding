# Exploration

Load this module only when broad navigation of a large or structurally complex codebase is necessary and Codebase Memory is not enabled. The result is a bounded impact map, not a repository tour.

## Locate

1. Start from user-visible behavior, public symbols, errors, routes, configuration, or existing tests named by the task.
2. Use narrow filename/text/symbol searches to form a candidate set. Read definitions first, then only material callers, consumers, data transformations, and compatibility boundaries.
3. Confirm relevance through imports, calls, tests, or runtime data flow rather than name similarity. Stop when the requested behavior and minimum coherent change surface are explained.
4. Report exact paths/symbols, the relevant edges between them, compatibility constraints, likely change surface, and unresolved gaps. Do not copy full files or search logs.

Batch inventory/search and targeted reads, and stop as soon as the map is sufficient for the task. An Exploration worker is read-only. The root waits for its map, checks only current edit sites, and owns implementation. If ordinary targeted search finds the whole path cheaply, return to Direct Path instead of completing a ceremonial map.
