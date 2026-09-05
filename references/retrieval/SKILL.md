# Retrieval

**Retrieval depth:** root

**Purpose:** minimum current-source evidence for the current claim

**Immediate child:** [`direct.md`](direct.md)

Start at Direct Locate. Each loaded node selects only its immediate child. A stage transition need not issue a redundant search: carry forward known paths and the remaining evidence gap, but do not skip loading the child's rules.

Keep the claim and evidence gap in working context, not a new state file. Stop when authoritative source supports the conclusion and its material boundary. A failed search is not proof of absence; distinguish wrong scope, unavailable provider, stale index, and unresolved evidence. Change an unproductive query only for a reason, not by repeating it.

After edits or regeneration, recheck affected evidence only. Provider results propose locations; current source establishes facts. Preserve counterexamples and uncertainty rather than trimming them to fit an output budget. Tools are replaceable capabilities, not stages.
