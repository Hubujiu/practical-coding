# Execution-state semantic invariants

`runtime/skill_state.py` validates both the fixed JSON shape and a small set of
cross-container invariants that cannot be expressed by independent field types.
These checks apply to initial state, model patches, host patches, transitions,
prompt construction, and the direct CLI.

## Hypothesis lifecycle partition

A hypothesis ID may occur in exactly one lifecycle partition:

- `hypotheses.active`: still live and worth testing;
- `hypotheses.rejected`: disproved evidence retained to prevent repetition.

The two exact-key sets must be disjoint. Moving `h-cache` from active to rejected
with JSON Merge Patch therefore requires one atomic patch:

```json
{
  "hypotheses": {
    "active": {"h-cache": null},
    "rejected": {"h-cache": "cache-disabled reproduction disproved it"}
  }
}
```

Adding the rejected entry without deleting the active entry rejects the complete
successor. The previous canonical state remains unchanged and the transition's
action is not released. A bounded host retry may then request a corrected patch.
The runtime deliberately does not auto-move the entry because silently repairing
model output would hide a semantic transition error and weaken auditability.

This is a validation tightening, not a state-shape change, so schema version 1 is
unchanged. It establishes no model-quality, token, latency, or bounded-context
claim; those remain subject to the frozen model gate.
