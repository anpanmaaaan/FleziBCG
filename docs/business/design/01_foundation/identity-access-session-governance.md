# Identity, Access, and Session Governance

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified separation between authenticated user, operator, and equipment context. |

Status: Canonical foundation note.

## 1. Purpose

This document defines how identity, access, and session governance work across the platform.

## 2. Separation of concerns

The platform separates:
- identity
- access control
- user lifecycle
- session/security governance
- approval/delegation

## 3. Key identity concepts

### Authenticated user
- login principal
- IAM subject
- session/token owner

### Identified operator
- production actor in execution flow
- may be linked to a user
- may be identified by scan/manual entry in station/resource contexts

### Equipment/resource context
- execution resource context
- never a user identity

## 4. Session governance

The system must support:
- login
- logout current session
- logout all sessions
- token refresh
- session revoke
- support/impersonation controls

Execution-related session governance additionally supports:
- station/resource session open/close
- operator identification within execution session
- equipment binding within execution session where required

## 5. Governance rules

- JWT proves identity only
- authorization is checked server-side per request
- production actions by ADM/OTS are not default behavior
- support/impersonation actions must be explicit, time-bound, and auditable
