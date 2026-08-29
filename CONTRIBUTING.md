# Contributing

Contributions should preserve Practical Coding as one compact **adaptive-rigor Skill**: a small route-agnostic Core, one pre-execution Decision Gate, two independently loadable execution-rigor profiles, and a Retrieval Policy that does not become a permanent prompt tax.

- Keep `SKILL.md` small. The Core must contain only rules that apply to essentially every coding task.
- Treat **Decision** differently from execution rigor. Load `decision.md` only when a material unresolved choice blocks or materially changes the next safe action.
- Treat **Direct** as the default execution state, not a route or reference.
- Treat **Debugging** and **Implementation** as alternative escalation profiles, not a `Direct → Debugging → Implementation` pipeline.
- Debugging is justified only while an observed failure lacks an evidenced cause. If the cause is already established and the safe fix is known, stay Direct.
- Implementation rigor is justified only while safe execution is blocked by an unknown contract/invariant, unresolved material risk boundary, or insufficient evidence for a risky claim. Security, persistence, migration, concurrency, compatibility, or file count alone are not triggers.
- Do not retune Core or reference wording from a single failed benchmark cell, and do not add case-specific bans or trigger nouns named after public benchmark tasks.
- Keep simple, well-specified work genuinely cheap: no reasoning reference, broad repository scan, plan document, or worker merely because the task involves code.
- Routine targeted source lookup must not require `references/navigation.md`. Load that reference only when broad retrieval itself is substantial enough to justify the prompt cost.
- Preserve context isolation. The root should normally carry the Core plus at most one large reasoning reference at a time. Logical state transitions do not remove already-read context.
- If a later blocker needs another large reference, isolate substantial follow-up work only when saved context exceeds handoff cost. Do not create worker pipelines.
- Workers read `references/delegation.md` plus exactly one assigned reference and return compact evidence capsules, not raw transcripts.
- Keep shared-workspace workers read-only by default. An Implementation worker may write only when explicitly assigned one bounded writer scope.
- Prefer strengthening an existing profile or retrieval primitive over adding another module. Verification remains part of Core or Implementation rigor; do not create a mandatory Verification stage.
- Do not introduce mandatory plans, execution documents, Git workflows, tests, reviews, documentation, or tool-specific ceremony as universal gates.
- Preserve reuse-before-invention, mature-implementation-first, risk-proportional verification, evidence-driven debugging, and resistance to speculative code and defensive bloat.
- Avoid new scripts, dependencies, configuration, generated project files, or persistent services unless they solve a demonstrated project need rather than merely making retrieval possible.

## Decision Gate discipline

A proposed Decision trigger must answer:

> Without settling this choice, can the agent already know the next safe action?

If yes, it is not a blocking Decision Gate. Repository conventions, authoritative constraints, or a cheap reversible default should settle ordinary choices without an interview.

When a choice genuinely remains user-owned, ask only for the minimum scope, compatibility, cost, preference, or risk information that changes the next action. A Decision module should converge and return a compact execution capsule; it should not become a design-document generator.

## Execution-rigor discipline

When changing `debugging.md` or `implementation.md`, test both positive and negative boundaries:

- unknown-cause failure → Debugging;
- diagnosed failure → Direct;
- unresolved material execution boundary → Implementation;
- already-mapped risk boundary with known affected surface and sufficient check → Direct;
- Debugging completed with no remaining boundary blocker → Direct;
- Debugging completed but a materially different execution boundary remains unresolved → Implementation only as a new escalation, preferably isolated if a second large reference would accumulate.

The amount of code, number of files, or perceived task difficulty is not a valid substitute for these blocker conditions.

## Retrieval backends

Practical Coding manages retrieval cost, not ownership of a particular search engine.

1. Prefer already-known source and narrow direct reads.
2. Prefer an already-available bounded/ranked source-search primitive over unbounded output. Host-native ranked search and FFF-style retrieval are examples, not requirements.
3. Prefer an already-available structural index only for relationship-heavy questions where it materially reduces repeated source exploration. `DeusData/codebase-memory-mcp` is one mature example.
4. If a stronger capability is unavailable, fall back to ordinary source search without changing repository configuration or installing/persisting tooling solely for retrieval.
5. Material conclusions must still be checked against current source.

Do not reimplement mature retrieval engines inside Practical Coding merely to avoid an optional external capability. Conversely, do not turn an optional capability into a hard dependency or automatic installation side effect.

### Retrieval benchmark discipline

The v1.3 benchmark uses a minimum-sufficient / maximum-reasonable interval instead of requiring one unique exact Retrieval label.

A benchmark-case change must distinguish:

- **insufficient retrieval** — below the minimum context needed for safe action;
- **acceptable retrieval** — within the frozen cost interval;
- **excessive retrieval** — above the maximum reasonable cost for the task.

Do not widen an interval after seeing a failed run merely to make the cell pass. Change it only before a validation cycle or after documenting a genuine benchmark-instrument defect.

## Benchmark changes

The canonical v1.3 runner is `benchmarks/run_catalog.py` (runner v2.1). `run_benchmarks.py` remains the v2.0 execution core for historical interpretability; do not silently rewrite old result directories or reinterpret old Router scores under the new schema.

Any behavior-changing contribution should preserve or add regression coverage for the mechanism it changes. In particular, the current transition corpus must continue to cover:

- Decision → Direct;
- Decision → Implementation;
- Debugging → Direct;
- Debugging → Implementation.

Before publishing claims, follow [`benchmarks/NEXT_VALIDATION.md`](benchmarks/NEXT_VALIDATION.md). Public cells that influenced wording are regression evidence, not independent held-out evidence.

## Mature implementation first

For any non-trivial capability with credible prior art:

1. Inspect maintained mature implementations first.
2. Prefer supported public integration surfaces — API, CLI, protocol, package, library, binary, or host-native tool — over copying internals or rebuilding the subsystem.
3. Verify fit, maintenance state, known issues, release activity, operational constraints, and license.
4. Add local code only for concrete gaps or confirmed upstream defects.
5. Keep local patches narrow, attributable, and removable when upstream fixes the issue.

A change is moving in the wrong direction if a trivial local edit must load or execute more process after the change than before it, if retrieval dumps more irrelevant context into the model, or if Practical Coding starts maintaining a weaker duplicate of a mature subsystem.
