# User Lifecycle and Admin Operations

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Minor alignment to operator separation. |

Status: Canonical lifecycle/admin note.

## 1. User lifecycle

Explicit user states should exist:
- pending
- active
- suspended
- locked
- deactivated

## 2. Admin/support rule

ADM and OTS are not default production execution actors.
Any production-facing intervention must be explicit, time-bound, and auditable.

## 3. Operator separation implication

User lifecycle governs authenticated users.
Operator activation/eligibility may be related, but must not be collapsed blindly into the same lifecycle semantics.
