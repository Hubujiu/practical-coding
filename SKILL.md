---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the smallest correct change; routes only unresolved architecture, debugging, exploration, or risk-boundary blockers while ordinary well-specified work stays direct."
license: MIT
metadata:
  author: Hubujiu
  version: "1.3"
---

# Practical Coding

One short core for every coding task, with optional modules only for unresolved blockers. Simple work does not enter a workflow.

## Core

Core is only for work that needs no human decision: close the stated success with what already exists in the project or the runtime/environment.

- Read the request and the code it actually touches; define the smallest observable success before editing.
- Stop at the first rung that works: do nothing; reuse the nearest existing project primitive; use the standard library; use a native platform or environment feature; use an already-installed dependency; one line; otherwise the minimum new local code. A popular library that is not already in the project is not a Core rung.
- Reuse current APIs as they are. When an artifact only specializes an existing primitive, make the thinnest adapter and inherit its contract; do not restate its styles, types, refs, events, or value semantics without a requirement.
- Build only behavior a current requirement or caller needs. Names, common conventions, repository aesthetics, and sibling-component richness are not requirements. When the request is underspecified, preserve the platform representation and nearest existing contract instead of inventing a richer domain model, API surface, or UX.
- When the request names an artifact but not its UX, API surface, or integration, default to the thinnest adapter on the nearest existing primitive that meets the stated success. Do not add controlled/uncontrolled modes, extra props, or helper components unless the request or an existing caller requires them.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo or new caller unless requested; a user-facing feature is incomplete until the existing application can reach it.
- Prefer deletion and boring code. Keep unrelated code and existing user changes untouched. Do not add a new dependency, vendor a library, or survey/compare mature external implementations on Core. If the stated success cannot be met with project code, stdlib, native/environment features, or already-installed packages, stop editing and route Decision.
- Mechanism examples (not task names): platform-native control before a picker library when only basic selection is requested; one shared guard in the function all callers use before patching a single reported caller.
- Add validation, fallback, retry, documentation, comments, or tests only for a current contract, concrete boundary, observed risk, project rule, or necessary evidence.
- Before finishing, delete every new file, prop, wrapper, and comment that the chosen check still passes without; keep the smallest version that still works.
- After the final edit, run the cheapest focused check once. Never repeat an unchanged check or substitute diff inspection for a required compile, type, or build gate. In an isolated workspace, a lockfile-preserving routine dependency install is allowed only for packages already declared in the lockfile when that is the bounded prerequisite for that gate; otherwise report missing dependencies instead of installing them solely for verification.
- If a check creates unrelated generated churn, inspect at most one diff, then leave and report it. Never investigate its provenance or stage, restore, or rewrite unrelated files merely to clean status output.
- State only what fresh evidence supports; keep unrequested explanation short.

## Direct Path

When the next safe action is clear, apply the Core immediately: read no reference and dispatch no worker. A narrow lookup, reversible default, established project pattern, already-installed package, or known coherent multi-file edit remains Direct. File count, task nouns, and the existence of a popular uninstalled library never select a module. Direct Path never adds a new dependency or surveys external implementations. A symptom or named failing function is not a cause; without prior evidence, read `references/debugging.md` before inspecting or editing.

## Event Router

Route only when a present unresolved event blocks the next safe action. If the request or repository already settles it, it is an input, not an event. Use this first-match ladder and stop at the first match:

1. An observed failure still lacks an evidenced cause: read `references/debugging.md`.
2. An open user-owned choice about architecture, introducing a new external dependency, surveying a mature external implementation, API, data model, or compatibility would change the next action: read `references/decision.md`. If Core rungs cannot meet the stated success without a new package or without researching external implementations, that is this event—do not install or compare libraries on Direct Path.
3. Safe execution requires mapping an unknown cross-boundary contract/invariant, handling security, irreversible effects, persistence, concurrency, or compatibility risk, or deciding sufficient evidence for a material claim or risky change: read `references/implementation.md`.
4. Broad structural navigation is necessary: read `references/navigation.md`, which selects the configured backend.

Read and apply exactly that one module before routing again. Never load candidates together to compare them; route again only if resolving the first event exposes a different blocker.

Do not preload modules. A named option, migration, already-installed dependency, or compatibility topic is not a Decision when its material policy is already fixed. Stay Direct when a higher Core rung already meets the stated success, even if a popular uninstalled library exists. Risk-related nouns, mechanisms, and file count do not select Implementation. Stay Direct only when repository evidence already establishes the affected boundary, required guarantee, next safe action, and sufficient focused check, with no unresolved migration, compatibility, side-effect, or evidence question; if the boundary or guarantee remains uncertain, use Implementation. A reported symptom is not a diagnosed cause. Known coordinated edits are Direct; Implementation is not a mandatory stage.

Navigation needed to execute a risky change stays inside Implementation; use Navigation when the structural map itself is the current outcome or independently blocks another event.

## Isolation Gate

Direct work and a single routed event in a small context use no worker. The root never reads `references/delegation.md`; when isolation clearly saves more context than its handoff costs, dispatch one worker and tell that worker to read it plus the one assigned module. Never use overlapping writers or worker pipelines.
