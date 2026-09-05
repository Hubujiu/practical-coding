# EXP-20260902 — Collapse automatic leaves into Core

Status: **rejected and reverted**

## Observation

The isolated leaf candidate reached the Core capability ceiling on every task. This raised the topology question of whether Debugging and Implementation added measurable value beyond Core.

## Hypothesis

Removing both automatic leaves should preserve quality and reduce runtime context or tool cost if Core already owns all minimum-sufficient behavior.

## Acceptance

Qualify the Core-only topology at complete current-only n=1. Only then run a complete paired n=3. Accept only if quality remains non-inferior and recorded cost improves against frozen v1.5.

## Result

The n=1 candidate qualified, but paired n=3 tied quality at 45/45 while regressing mean tokens, duration, and tool calls. Commit `55453299a1cd21774f453d4ccb9733f4c1f50e84` reverted the collapse.
