# Testing Strategy by Layer

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Added transition-critical coverage needs for session-owned execution. |

Status: Testing strategy note.

## Key coverage areas
- auth/session lifecycle
- tenant/scope isolation
- operator/equipment session flows
- execution lifecycle transitions
- quality gating
- close/reopen
- audit and support/impersonation restrictions

## Transition-critical tests
When cutting from claim-centric to session-owned execution, coverage is required for:
- session open/identify/bind/close
- start/pause/resume/report/complete under session rules
- reopen/resume behavior without claim-owned target semantics
