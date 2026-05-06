---
name: "FleziBCG IAM Domain"
description: "Use when working on FleziBCG IAM, authentication, authorization, RBAC, scope assignment, access control, user lifecycle, impersonation, session governance, refresh tokens, approvals tied to authority, audit or security events, or IAM-related specs and plans."
applyTo: ["backend/app/api/v1/auth.py", "backend/app/api/v1/iam.py", "backend/app/api/v1/access.py", "backend/app/api/v1/impersonations.py", "backend/app/api/v1/security_events.py", "backend/app/api/v1/users.py", "backend/app/services/iam_service.py", "backend/app/services/access_service.py", "backend/app/services/session_service.py", "backend/app/services/refresh_token_service.py", "backend/app/services/impersonation_service.py", "backend/app/services/security_event_service.py", "backend/app/services/user_service.py", "backend/app/services/user_lifecycle_service.py", "backend/app/models/rbac.py", "backend/app/models/user.py", "backend/app/models/session.py", "backend/app/models/refresh_token.py", "backend/app/models/impersonation.py", "backend/app/models/security_event.py", "backend/app/security/**", "frontend/src/app/api/authApi.ts", "frontend/src/app/api/impersonationApi.ts", "frontend/src/app/auth/**", "frontend/src/app/impersonation/**", "frontend/src/app/pages/UserManagement.tsx", "frontend/src/app/pages/RoleManagement.tsx", "frontend/src/app/pages/ScopeAssignments.tsx", "frontend/src/app/pages/SessionManagement.tsx", "frontend/src/app/pages/SecurityEvents.tsx", "frontend/src/app/pages/TenantSettings.tsx"]
---
# IAM Domain Guidance

Primary truth:

- `docs/design/01_foundation/identity-access-session-governance.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`

## Load This When

- The task changes login, logout, refresh, session revoke, impersonation, RBAC, scope assignment, permission checks, user lifecycle, security events, tenant/scope isolation, or any governed action.
- The task writes IAM specs, implementation plans, or reviews.

## Non-Negotiables

- JWT proves identity only.
- Authorization is server-side per request or command.
- Tenant and scope isolation are mandatory.
- Authenticated user, identified operator, and equipment/resource context are separate concepts.
- Support and admin production access must be explicit, time-bound, auditable, and governed.
- Requester must never equal decider for approval or governed decision paths, including under impersonation.
- AI is advisory only and must not bypass authority or audit.

## Required Modeling Rules

- Treat authentication, authorization, session governance, impersonation, and audit as separate but connected concerns.
- Keep permission truth in backend role/action/scope evaluation.
- Do not let frontend route guards or menu visibility become authorization truth.
- Record security or audit events for privileged and governed actions where policy requires it.
- When impersonation is active, preserve acting-role restrictions and audit trail.
- Never assume ADM or OTS are normal execution actors.

## Hard Mode Trigger

- IAM, tenant/scope, audit/security events, impersonation, approval authority, and governed role assignment work should be treated as Hard Mode MOM v3 unless the change is purely mechanical.

## Implementation Boundaries

- Routes remain thin; services own access-control branching and governed flows.
- Repository filters must keep tenant/scope context explicit.
- Do not encode permission truth in frontend-only affordances.
- Do not silently widen role powers, scope inheritance, or impersonation targets.

## Validation Focus

- Prefer behavior tests covering deny and allow paths.
- Verify tenant isolation and scope filtering explicitly.
- Verify impersonation and audit/security-event side effects for privileged flows.
- Treat route or OpenAPI changes as intentional contract work when authority surfaces change.
