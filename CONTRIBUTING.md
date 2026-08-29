# Contributing

Contributions should preserve Practical Coding as one compact Skill with a small route-agnostic Core, three independently loadable reasoning modules, and a retrieval policy that does not become a permanent prompt tax.

- Keep `SKILL.md` as a small shortest-path Core plus Event Router and compact Retrieval Policy. Do not add routing intensity modes unless a mature cross-agent mechanism materially improves evidence.
- The Event Router owns only unresolved reasoning blockers: Debugging, Decision, and Implementation. Navigation is retrieval, not a fourth reasoning route.
- Do not retune Core or module wording from a single failed benchmark cell, and do not add case-specific bans named after benchmark tasks.
- Keep the Direct Path real: simple, well-specified work must not require a reference, broad repository scan, or worker.
- Routine targeted source lookup must not require `references/navigation.md`. Load that reference only when broad retrieval itself is substantial enough to justify the prompt cost.
- Preserve context isolation. The root should normally carry the Core plus at most one reasoning reference. If broad mapping becomes expensive while another reference is resident, prefer a read-only Navigation worker when saved context exceeds handoff cost.
- Workers read `references/delegation.md` plus exactly one assigned reference and return compact evidence capsules, not transcripts.
- Keep shared-workspace workers read-only by default. An Implementation worker may write only when its assignment explicitly includes implementation, with one bounded writer scope.
- Prefer strengthening an existing module or retrieval primitive over adding another module. Verification remains part of Core or Implementation; do not create a mandatory Verification route.
- Do not introduce mandatory plans, execution documents, Git workflows, tests, reviews, documentation, or tool-specific ceremony as universal gates.
- Preserve reuse-before-invention, mature-implementation-first, risk-proportional verification, evidence-driven debugging, and resistance to speculative code and defensive bloat.
- Avoid new scripts, dependencies, configuration, generated project files, or persistent services unless they solve a demonstrated project need rather than merely making retrieval possible.

## Retrieval backends

Practical Coding manages retrieval cost, not ownership of a particular search engine.

1. Prefer already-known source and narrow direct reads.
2. Prefer an already-available bounded/ranked source-search primitive over unbounded output. Host-native ranked search and FFF-style retrieval are examples, not requirements.
3. Prefer an already-available structural index only for relationship-heavy questions where it materially reduces repeated source exploration. `DeusData/codebase-memory-mcp` is one mature example.
4. If a stronger capability is unavailable, fall back to ordinary source search without changing repository configuration or installing/persisting tooling solely for retrieval.
5. Material conclusions must still be checked against current source.

Do not reimplement mature retrieval engines inside Practical Coding merely to avoid an optional external capability. Conversely, do not turn an optional capability into a hard dependency or automatic installation side effect.

## Mature implementation first

For any non-trivial capability with credible prior art:

1. Inspect maintained mature implementations first.
2. Prefer supported public integration surfaces — API, CLI, protocol, package, library, binary, or host-native tool — over copying internals or rebuilding the subsystem.
3. Verify fit, maintenance state, known issues, release activity, operational constraints, and license.
4. Add local code only for concrete gaps or confirmed upstream defects.
5. Keep local patches narrow, attributable, and removable when upstream fixes the issue.

A change is moving in the wrong direction if a trivial local edit must load or execute more process after the change than before it, if retrieval dumps more irrelevant context into the model, or if Practical Coding starts maintaining a weaker duplicate of a mature subsystem.
