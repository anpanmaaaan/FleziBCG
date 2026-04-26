# Session and Token Lifecycle

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Added execution-session distinction from security session lifecycle. |

Status: Canonical session/token lifecycle note.

## 1. Security session lifecycle

The platform must support:
- login
- refresh
- logout current session
- logout all sessions
- session revoke
- password reset flows where applicable

## 2. Execution session lifecycle

Separate from security session lifecycle, execution may use station/resource sessions that bind:
- authenticated user
- identified operator
- station/resource context
- equipment binding when required

## 3. Important rule

Security session and execution session must not be conflated.
A valid JWT does not by itself prove that the caller currently owns the active execution context.
