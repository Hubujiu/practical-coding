# Security Boundary

Load only when a material guarantee depends on a trust boundary: authentication/authorization, untrusted input or output, secret handling, injection, privilege, permission, or rejection-before-side-effect behavior.

## Procedure

- Identify the trusted and untrusted sides and the single boundary that should own the guarantee.
- Trace the minimum valid and invalid paths that cross it.
- Ensure authorization is about the requested resource/action, not merely identity presence.
- Validate/encode at the correct boundary; do not scatter duplicate checks downstream.
- Verify representative rejection happens before material side effects.
- Keep secrets out of code, output, logs, and persisted artifacts.

Do not perform a generic security audit unless the user asked for one. Do not add defensive checks unrelated to the touched trust boundary.

## Exit evidence

A valid case still succeeds, the smallest representative invalid/unauthorized cases fail at the owning boundary, and no material side effect occurs before rejection.
