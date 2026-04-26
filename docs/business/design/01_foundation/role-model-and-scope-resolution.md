# Role Model and Scope Resolution

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.1 | Clarified planning/inventory roles and specialized compatibility/support roles. |

Status: Canonical role/scope note.

## 1. Business roles

Primary roles for MOM-facing business behavior:
- OPR
- SUP
- IEP
- QAL
- PMG
- PLN
- INV
- ADM

## 2. Specialized / compatibility / support roles

These may exist where needed, but they are not the primary platform-wide business role families:
- QCI
- OTS

## 3. Role principles

- persona is UX-only, not authorization
- role assignment and scope assignment are separate concerns
- backend evaluates effective authorization
- visible screens do not prove command permission
- support roles do not become default production actors

## 4. Scope resolution

Scopes must be ready for:
- tenant
- plant
- area
- line
- station
- equipment

## 5. Execution implication

Execution ownership is not decided by role alone.
It also depends on current execution session context and business-state guards.
