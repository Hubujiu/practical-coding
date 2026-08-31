---
name: practical-coding
description: "Use for implementing, fixing, refactoring, reviewing, or navigating code with the least engineering process and repository context that can still produce a reliable result; deepen only when a concrete unresolved execution or retrieval event requires it."
license: MIT
metadata:
  author: Hubujiu
  version: "1.4"
---

# Practical Coding

Use the least engineering and the least context that can still produce a reliable coding result.

The **default path starts at Core/E0**. Practical Coding has two adaptive controls:

- **Execution depth** — how much reasoning structure and assurance the current unresolved event needs.
- **Retrieval depth** — how much source/context the next material decision needs.

Depth is not a workflow to complete. Start shallow, expand only when current evidence cannot answer the next material question, then contract after localization.

## Manual-only modes — outside adaptive routing

Requirements interviews (`grill-me`-style clarification), Decision/option-selection workflows, and similar user-interaction modes are **not nodes, gates, roots, or leaves in the default tree**.

Never activate them because the model infers that a request is vague, alternatives exist, a decision seems important, the task is high-stakes, or more questioning might help. The adaptive router is not allowed to select them.

They may be loaded only when the user's current instruction **explicitly asks for that behavior**, for example:

- "grill me / interview me / ask requirements before coding" → `references/manual/clarification.md`;
- "use Decision mode / compare the options with me before coding" → `references/manual/decision.md`.

An explicit behavioral request counts even if the user does not name the file. One manual mode must not automatically route into another manual mode.

If an ordinary coding request is missing information that makes safe execution impossible, ask only the minimum blocking question as normal interaction. That does **not** activate a manual interview or Decision workflow.

## Core

The Core applies everywhere and should remain sufficient for most work.

- Define the smallest observable success before editing.
- Prefer the smallest coherent reachable change that satisfies the request and established contracts.
- Reuse the nearest project primitive before inventing a new abstraction or dependency.
- Add no speculative wrapper, alias, option, configuration surface, helper layer, extension point, retry, fallback, validation, test, comment, or documentation.
- Prefer deletion, direct control flow, and boring code. Preserve unrelated behavior and user changes.
- Put a guarantee at the narrowest authoritative boundary that owns it.
- Verify with the cheapest focused check that can falsify the material claim. Do not repeat an unchanged check.
- State only what fresh evidence supports.
- Never escalate because a task sounds difficult, touches many files, or contains a risk-related noun. Escalate because a specific execution or retrieval uncertainty remains unresolved.

## Execution Depth + Capability Tree

Execution depth answers **how much engineering is needed**. Capability paths answer **what kind of engineering is needed**.

```text
Core
 ├─ E0 Direct
 └─ E1 Focused evidence
      └─ E2 Capability root
          ├─ diagnosis
          │    ├─ security
          │    ├─ state
          │    ├─ compatibility
          │    └─ performance
          └─ engineering
               ├─ security
               ├─ state
               ├─ compatibility
               ├─ performance
               ├─ quality
               └─ interface
                    ↓
                 E3 leaf depth
```

The tree is sparse and evidence-driven. Do not traverse every node. In the root context, load at most **one capability root and one specialist leaf** for the current unresolved event.

### E0 — Direct

Default here. Use Core only when the target behavior, governing contract, and sufficient focused check are already clear.

Do not load a reasoning reference.

### E1 — Focused

Stay Core-only and take one bounded local evidence step to remove a specific blocker:

- inspect the nearest caller, contract, sibling pattern, or focused test;
- reproduce or directly exercise one behavior;
- identify the smallest check that can falsify the change.

If that resolves the blocker, return to E0 behavior. Do not turn local inspection into a workflow.

### E2 — Capability root

Load exactly one root only when E1 was insufficient.

- **diagnosis** → `references/debugging.md` when an observed failure, regression, incorrect behavior, or failed verification still lacks an evidenced cause.
- **engineering** → `references/engineering.md` when the desired behavior is known but safe execution is blocked by an unresolved contract, invariant, ownership boundary, or multi-part change surface.

These are event types, not mandatory phases. A feature does not require engineering depth merely because it is a feature; a bug does not require diagnosis after its cause is already known.

### E3 — Specialist leaf

Load one specialist leaf only when the active root cannot support a material guarantee without domain-specific reasoning. The trigger must be observable before loading the leaf.

- `references/specialists/security.md` — trust, authentication/authorization, untrusted input/output, secret exposure, or rejection-before-side-effect behavior is material.
- `references/specialists/state.md` — persistence, migration state, transactionality, ordering, retries, idempotency, rollback, restart, or concurrency is material.
- `references/specialists/compatibility.md` — public API/schema/protocol/version compatibility or old/new coexistence is material.
- `references/specialists/performance.md` — a measured or explicitly required latency, throughput, memory, query, render, or scale boundary is material.
- `references/specialists/quality.md` — the task is a substantive review/refactor or structural complexity itself blocks safe change; style preference alone is insufficient.
- `references/specialists/interface.md` — user-facing visual/interface quality is a material deliverable and repository conventions alone do not settle the design direction.

A specialist leaf adds a narrow expert procedure, not a general hardening checklist. If its material guarantee becomes localized, stop using it and contract.

Do not stack sibling leaves because several might be relevant. Finish the current unresolved guarantee first. If a second orthogonal guarantee is substantial enough that keeping both contexts would be wasteful, use the Isolation Gate.

### De-escalation

As soon as the cause, contract, invariant, ownership boundary, or evidence boundary is clear:

1. stop the broader procedure;
2. contract to the smallest affected surface;
3. make the smallest coherent change;
4. run the cheapest sufficient final check.

Higher-depth context may remain in the model, but higher-depth behavior should stop.

## Retrieval Depth + Retrieval Tree

Retrieval is independent of execution. A simple edit can need broad discovery; a difficult bug can already have a known target.

```text
R0 Target
 └─ R1 Local search
      ├─ R2 Structural relation
      ├─ R2 External contract
      └─ R3 Bounded exhaustive repository claim
```

External evidence is a branch, not a rung after repository-wide search.

### R0 — Target

Use current context, a known path, symbol, error, route, test, or configuration. Read only what the next decision needs.

### R1 — Local

Use bounded/ranked filename, text, symbol, reference, or host-native source search inside the nearest plausible scope. Prefer top-k, limits, pagination, and batched narrow queries.

### R2 — Specialized retrieval

Choose one branch when R1 cannot answer the unresolved question:

- **Structural relation:** callers, callees, imports, implementations, inheritance, dependency flow, data flow, or configuration flow. Prefer an already-available structural capability when it reduces exploration; otherwise reconstruct only the required relation from source.
- **External contract:** authoritative current framework/API/license/protocol behavior that the repository cannot establish. Prefer primary maintained sources and return only the contract needed for the code decision.

Read `references/navigation.md` only when structural retrieval itself becomes substantial. Routine R0/R1 work does not need it.

### R3 — Bounded exhaustive repository claim

Use repository-wide discovery only when R0–R2 cannot localize the relevant boundary or the task requires an explicit bounded exhaustive repository claim. Narrow results before reading source; do not dump broad matches into context.

### Retrieval contraction

After expansion identifies the relevant files, symbols, relationships, or external contract, contract immediately to that surface. Current source remains authoritative for repository behavior.

## Isolation Gate

Do not create workers for ordinary E0/E1 work or merely because parallelism is available.

When a second substantial event, specialist guarantee, or broad structural mapping would add more root-context cost than a compact handoff, dispatch one worker. The worker reads `references/delegation.md` plus only its assigned capability root/leaf or Navigation reference and returns an evidence capsule.

- Diagnosis, Navigation, and read-only specialist workers do not write.
- A bounded Engineering worker may write only when explicitly assigned a non-overlapping scope and there is no competing writer.
- Manual-only interaction modes stay in the root conversation and are never worker-selected.
- Never build worker pipelines or overlapping writers.

## Benchmark Contract

The adaptive depths, roots, leaves, and trigger boundaries are hypotheses. Manual-only modes are evaluated separately and are not eligible adaptive routing paths.

Measure against **no-skill** and the accepted prior Practical Coding version, not only against other expert skills. Quality gates come before cost.

Track at least:

- correctness, safety, build/reachability;
- tokens, time, tool calls, LOC, references loaded;
- execution and retrieval minimum-sufficient depth;
- selected `capability_path` such as `diagnosis>state` or `engineering>security`;
- unnecessary root/leaf loads, missed specialist loads, and branch-confusion clusters;
- over-escalation and under-escalation by task family;
- transfer across repositories and, when practical, model/harness configurations.

For manual-only modes, separately test explicit activation and **zero spontaneous activation** on ordinary tasks. Do not tune them as adaptive gates.

If a depth is rarely minimum-sufficient, test merging/removing it. If a root or leaf does not deliver stable net lift over its parent on the tasks it claims to cover, tighten, merge, replace, or remove it. Never preserve a node for symmetry.

Runtime agents do not read `evolution/`. Skill-maintenance work uses benchmark results and real-project experience receipts to update persistent evolution knowledge before proposing changes. See `benchmarks/LADDER_EVOLUTION.md` and `evolution/README.md`.