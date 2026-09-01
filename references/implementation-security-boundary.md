# Security Boundary

**Tree depth: 2**

Load only from Implementation when the primary unresolved invariant is a trust boundary: authentication, authorization, untrusted input, secret handling, permission, or a sensitive side effect that must not occur for a rejected request.

## Own One Trust Boundary

- Identify the protected asset/action, the actor or input crossing the boundary, and the single authoritative component that owns allow/deny.
- Normalize and validate at the narrowest canonical boundary before relying on the value. Authorize using the canonical identity/resource, not an earlier unchecked representation.
- Default to rejection when required security state is missing or unverifiable. Do not silently downgrade a protected path.
- Keep secret material out of logs, errors, fixtures, and generated examples.

## Reject Before Effects

Arrange the flow so authentication/authorization/validation failure occurs before the protected side effect, durable mutation, external call, or privileged dispatch. Do not "undo" an effect that should never have happened.

Avoid broad hardening unrelated to the requested boundary. Do not add a new auth abstraction when an established filter/interceptor/middleware/policy already owns the guarantee.

## Evidence

Use the smallest evidence set that can falsify the guarantee:

- one representative allowed case;
- one missing/invalid credential or input case;
- one unauthorized-but-authenticated case when authorization is distinct;
- proof that rejection precedes the protected side effect.

If the change rotates/revokes credentials, exercise both activation and revocation boundaries without exposing the credential itself.

## Local Router

**Current status: leaf.**
