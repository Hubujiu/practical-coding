# Manual Requirements Interview

**Manual activation only.** Load this module only when the user's current instruction explicitly asks to be grilled, interviewed, questioned about requirements, or to settle requirements before coding.

Do not activate it because the request appears vague, short, risky, incomplete, or likely to benefit from questions. The adaptive router is not allowed to select this module.

## Interview

- Resolve repository/discoverable facts yourself before asking the user.
- Ask only user-owned intent: desired behavior, scope, priorities, non-goals, or acceptable trade-offs.
- Ask one consequential question at a time when answers are dependent.
- Include a recommended/default answer and the strongest material trade-off when useful.
- Do not ask implementation details that can be settled from project conventions or cheap reversible defaults.
- Continue until the user ends the interview or the requested outcome is sufficiently explicit for the next action.

Return a compact intent capsule: observable success, material scope/non-goals, user-owned constraints, and deliberately deferred ambiguities.

Do **not** automatically load Decision or any other manual mode afterward. Return control to the default Core/E0 path unless the user explicitly requested another manual mode as well.