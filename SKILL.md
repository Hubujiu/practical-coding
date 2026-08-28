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

Core handles work with no unresolved user-owned choice. Close the stated success with the smallest action allowed by the request: project code, the standard library, native/environment features, already-installed packages, minimum local code, or an external dependency/surface the user has already selected and authorized. Core does not independently choose a new external dependency.

- Read the request and the code it actually touches; define the smallest observable success before editing.
- Stop at the first rung that works within the current requirements: do nothing; reuse the nearest existing project primitive; use the standard library; use a native platform or environment feature; use an already-installed dependency; one line; otherwise the minimum new local code. An uninstalled external dependency is not a rung unless the request already selects and authorizes it.
- Reuse current APIs as they are. When an artifact only specializes an existing primitive, make the thinnest adapter and inherit its contract; do not restate its styles, types, refs, events, or value semantics without a requirement.
- Build only behavior a current requirement or caller needs. Names, common conventions, repository aesthetics, and sibling-component richness are not requirements. When the request is underspecified, preserve the platform representation and nearest existing contract instead of inventing a richer domain model, API surface, or UX.
- When the request names an artifact but leaves its interface, behavior, or integration underspecified, default to the thinnest adapter over the nearest existing primitive that meets the stated success. Do not invent secondary modes, public options, helper layers, or additional integration surface unless the request or an existing caller requires them.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo or new caller unless requested; a user-facing feature is incomplete until the existing application can reach it.
- Prefer deletion and boring code. Keep unrelated code and existing user changes untouched. Do not independently add a new dependency, vendor a library, or survey/compare external implementations on Core. If satisfying the stated success requires deciding whether or which external capability to adopt, route Decision. If the user already selected and authorized the external dependency or surface and the integration path is clear, treat that choice as settled input and remain Direct unless another blocker exists.
- Mechanism examples (not task names): reuse an existing project parser before introducing a parallel parser; fix a shared guard at the function all callers use before patching a single reported caller.
- Add validation, fallback, retry, documentation, comments, or tests only for a current contract, concrete boundary, observed risk, project rule, or necessary evidence.
- Before finishing, delete each new dependency, file, option, wrapper, or comment whose removal still preserves the stated success, existing contracts, and the chosen check; keep the smallest version that still works.
- After the final edit, run the cheapest focused check once. Never repeat an unchanged check or substitute diff inspection for a required compile, type, or build gate. In an isolated workspace, a routine dependency install is allowed only for dependencies already declared by the project or explicitly added as part of the authorized change when it is the bounded prerequisite for that gate; otherwise report missing dependencies instead of introducing one solely for verification.
- If a check creates unrelated generated churn, inspect at most one diff, then leave and report it. Never investigate its provenance or stage, restore, or rewrite unrelated files merely to clean status output.
- State only what fresh evidence supports; keep unrequested explanation short.

## Direct Path

When the next safe action is clear, apply the Core immediately: read no reference and dispatch no worker. A narrow lookup, reversible default, established project pattern, already-installed package, explicitly selected and authorized dependency with a clear integration path, or known coherent multi-file edit remains Direct. File count, task nouns, and the existence of a popular uninstalled library never select a module. Direct Path never independently chooses a new external dependency or surveys alternatives. A symptom or named failing function is not a cause; without prior evidence, read `references/debugging.md` before inspecting or editing.

## Event Router

Route only when a present unresolved event blocks the next safe action. If the request or repository already settles it, it is an input, not an event. Use this first-match ladder and stop at the first match:

1. An observed failure still lacks an evidenced cause: read `references/debugging.md`.
2. An open user-owned choice about architecture, whether or which new external dependency or mature external implementation to adopt, API, data model, or compatibility would change the next action: read `references/decision.md`. If Core cannot meet the stated success without making an unrequested external choice, that is this event. Research needed to resolve that open choice belongs in Decision; do not ask the user merely for permission to compare viable options.
3. Safe execution requires mapping an unknown cross-boundary contract/invariant, handling security, irreversible effects, persistence, concurrency, or compatibility risk, or deciding sufficient evidence for a material claim or risky change: read `references/implementation.md`.
4. Broad structural navigation is necessary: read `references/navigation.md`, which selects the configured backend.

Read and apply exactly that one module before routing again. Never load candidates together to compare them; route again only if resolving the first event exposes a different blocker.

Do not preload modules. A named option, migration, already-installed dependency, explicitly selected and authorized external dependency, or compatibility topic is not a Decision when its material policy is already fixed. Stay Direct when a higher Core rung already meets the stated success, even if a popular uninstalled library exists. Risk-related nouns, mechanisms, and file count do not select Implementation. Stay Direct only when repository evidence already establishes the affected boundary, required guarantee, next safe action, and sufficient focused check, with no unresolved migration, compatibility, side-effect, or evidence question; if the boundary or guarantee remains uncertain, use Implementation. A reported symptom is not a diagnosed cause. Known coordinated edits are Direct; Implementation is not a mandatory stage.

Navigation needed to execute a risky change stays inside Implementation; use Navigation when the structural map itself is the current outcome or independently blocks another event.

## Isolation Gate

Direct work and a single routed event in a small context use no worker. The root never reads `references/delegation.md`; when isolation clearly saves more context than its handoff costs, dispatch one worker and tell that worker to read it plus the one assigned module. Never use overlapping writers or worker pipelines.
