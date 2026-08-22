# Execution Document

Create this document only for multi-step, long-running, oversized, or handoff-prone work. Store it at `.practical-coding/execution/<task-slug>.md` in the target repository.

The document is a resumable execution contract, not a design essay. Keep it current enough that another agent or harness can continue from the repository without relying on conversation memory.

```markdown
# Execution: <task>

Status: Awaiting approval | Approved | In progress | Blocked | Complete
Objective:
Scope:
Non-goals:
Current phase:

## Progress
- [x] Completed item — file path or commit evidence
- [~] Current item
- [ ] Pending item
- [!] Blocked item

## Decisions
- Decision — reason and supporting source

## Files
- Relevant or modified path — purpose

## Commits
- SHA — completed checkpoint

## Blockers
- Blocker — required user or environment action

## Next Action
- Exactly one concrete next step

## Handoff
- Minimum context required to continue safely
```

Update the document whenever a phase starts, completes, changes, or becomes blocked. Associate completed claims with paths or commits. Record only decisions that affect execution, and do not duplicate code or Git history.

After creating or restoring the document, reconcile it with `git status`, recent `git log`, and the current diff, then present the resulting plan and state to the user. Do not edit product code until the user explicitly confirms the current document.

If the user requests changes, set the status to `Awaiting approval`, return to clarification, revise every affected section, and present it again. After approval, set the status to `Approved` and commit the approved document as the first checkpoint.

Keep exactly one phase in progress. Commit each coherent phase together with its updated execution document. Do not mix unrelated existing changes, rewrite user commits, or push without an explicit request.

When execution reveals a material change to scope, architecture, dependencies, permissions, or risk, stop, update the document, and repeat the approval loop. On resume or handoff, read repository instructions, the execution document, Git status, recent commits, and the current diff before acting.
