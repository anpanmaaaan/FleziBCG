# MES Lite Project Instructions

## Project type
This repository contains a lightweight MES system with:
- frontend in `frontend/`
- backend in `backend/`
- docs in `docs/`

## Backend stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- JWT auth
- simple RBAC
- modular monolith

## Architecture rules
- UI sends intent only
- backend is the source of truth
- backend derives state from append-only execution events
- no direct UI state mutation for execution status
- multi-tenant with tenant_id on tenant-owned tables
- enforce tenant filtering in service/repository layer
- Phase 1 only: deterministic MES execution, no AI/ML, no APS, no streaming infra

## Execution flow baseline (LOCKED)

The following execution flow is non-negotiable:

- Execution entry starts at Work Order, not Production Order
- Production Order is planning context and filter only
- Operation is the smallest execution unit
- Station Execution is the only write surface

Canonical execution flow:
- /work-orders
- /work-orders/:woId/operations
- /operations/:operationId/detail
- /station-execution?operationId=...

Do NOT introduce screens that mix Production Order, Work Order,
and Operation execution semantics.

## Coding rules
- keep modules small and explicit
- prefer service layer over putting logic in route handlers
- repository layer must not contain business rules
- use Pydantic schemas for request/response
- write clear names, avoid magic values
- do not over-engineer
- do not introduce Kafka, microservices, or cloud-only dependencies

## Business scope
Phase 1 includes:
- dashboard read APIs
- operations list/detail APIs
- execution tracking
- operation start
- quantity reporting
- operation complete
- QC measure record (backend computes pass/fail)

## Phase 2 scope (READ-ONLY monitoring)

Phase 2 introduces a Global Operation List for monitoring only.

Rules:
- Global Operation List is read-only
- No start / complete / report actions allowed
- No execution state derivation in frontend
- Backend remains source of truth

Allowed:
- status display via enum mapping
- filters by status, work center, WO, PO
- drill-down to operation detail

Not allowed:
- write actions
- business rule inference in UI

## Non-goals
- no AI control
- no advanced scheduling
- no external workflow engine
- no streaming platform

## Future-ready guardrails

### AI
- AI is advisory only
- AI may read execution events and history
- AI must never trigger or control execution actions
- No AI logic in execution or service layers in Phase 1–2

### Multi-language (i18n)
- Backend returns enums and codes, not translated text
- UI text must not contain business logic
- Prefer semantic keys for UI text (i18n-ready)
- Language preference belongs to tenant or user

### Microservice
- Current architecture is modular monolith
- Do NOT prematurely split into microservices
- Clear module boundaries are preferred over service extraction

## Phase 4 — RBAC & Persona Landing (LOCKED)

- Persona to default landing rules:
	- OPERATOR -> /station-execution
	- SUPERVISOR / SHIFT_LEADER -> /work-orders
	- MANAGER / OFFICE -> /dashboard
	- IE / PROCESS -> /operations
	- QA -> /quality

- Guardrail rules:
	- Agents MUST NOT change persona landing without new phase
	- Agents MUST NOT expose Station Execution to non-operators
	- Agents MUST NOT make Operations (Global) a manager default
	- Agents MUST NOT introduce execution logic into Dashboard

- Enforcement notes:
	- Phase 4 RBAC is frontend/UX-level only
	- Backend execution APIs are unchanged
	- Future phases may extend RBAC but must not violate these rules

## Phase 5A — i18n Infrastructure Rules (LOCKED)

- From Phase 5A onward:
	- All new UI text MUST use semantic i18n keys
	- Hardcoded business text is forbidden

- Backend MUST continue returning enums/codes only

- i18n runtime behavior MUST NOT be enabled without a new phase

- Phase 5B is the earliest phase allowed to:
	- Replace UI text with t()
	- Add language selector
	- Introduce locale switching

## Phase 2B — Global Operations Supervisor Rules (LOCKED)

- Global Operations is READ-ONLY.
- Supervisor view prioritizes BLOCKED and DELAYED operations.
- Operations MUST NOT include execution actions.
- Operations MUST NOT aggregate KPIs (Dashboard responsibility).
- Persona awareness does NOT imply role enforcement.
- IE / QA views are future phases and must not be mixed.

## Phase 2C — Global Operations IE / Process Rules (LOCKED)

- Global Operations IE / Process view is READ-ONLY.
- All analytical indicators MUST be backend-derived.
- Frontend MUST NOT compute cycle time, delay frequency, or variance.
- IE / Process view MUST NOT include KPI/dashboard semantics.
- IE / Process view MUST NOT include execution actions.
- Role/auth enforcement is NOT allowed in Phase 2C.

---

## Phase 6 — Governance & Access Layer (LOCKED)

This phase establishes the permanent governance, authentication, authorization, impersonation, and approval engine for the MES. **All rules in this section are non-negotiable and carry forward to Phase 7, 8, and beyond.**

### 6.1 Phase 6 Lock Declaration

**Status:** Phase 6 is LOCKED as of April 3, 2026.

The following domains are immutable without explicit architectural review:

- **RBAC Core** — Permission families, role-to-permission mappings, scope model
- **Authentication Flow** — JWT structure, login process, session management
- **Impersonation System** — Time bounds, allowed impersonators, audit trail
- **Approval Engine** — Action types, approval rules, separation of duties
- **Persona Semantics** — Frontend UX landing pages, menu visibility, role mapping
- **Execution Invariants** — State machine, event types, status derivation

Any modification to these areas requires:
1. Explicit architectural review (not code review alone)
2. Customer/stakeholder alignment
3. A new phase gate (Phase 7+)
4. Updated documentation in `/docs/system/mes-business-logic-v1.md`

### 6.2 Governance Core (DO NOT MODIFY)

The following governance rules are carved in stone and must not be circumvented:

#### 6.2.1 Permission Family Model (Immutable)

Five permission families enable all authorization decisions:

| Family | Granted To | Use Case |
|---|---|---|
| **VIEW** | All operational roles | Read-only access to data, status, KPIs |
| **EXECUTE** | OPR, SUP | Trigger execution state changes (START, COMPLETE, REPORT, BLOCK, ABORT) |
| **APPROVE** | QAL, PMG | Create/decide workflow approval requests |
| **CONFIGURE** | IEP | Modify parameters, standards, thresholds |
| **ADMIN** | ADM, OTS | System administration, user management, audit access |

**Immutable constraint:** Do NOT add new permission families or rename existing ones — this breaks the entire authorization layer.

#### 6.2.2 Role-to-Permission Assignment (Locked)

The following mappings are frozen:

```
OPR (Operator)           → EXECUTE
SUP (Supervisor)         → VIEW, EXECUTE
IEP (IE / Process)       → VIEW, CONFIGURE
QCI (QA Inspector)       → VIEW
QAL (QA Lines)           → VIEW, APPROVE
PMG (Production Manager) → VIEW, APPROVE
EXE (Execution Reporter) → VIEW
ADM (Admin)              → VIEW, ADMIN
OTS (On-the-Spot)        → VIEW, ADMIN
```

**Immutable constraint:** Do NOT modify these mappings without Phase 7 design review. Any change to role permissions must be tracked as a new phase.

#### 6.2.3 Separation of Duties (Canonical)

The following SOD rules are non-negotiable:

| Rule | Implementation | Exception |
|---|---|---|
| **Requester ≠ Approver** | Check `decision.decider_user_id ≠ request.requester_id` on REAL user_id | No exception; even ADM impersonating QAL cannot approve their own request |
| **Role-Based Approval** | `approval_rules` table enforces (action_type, approver_role_code) | Future phases cannot skip rule lookup |
| **Immutable Audit Trail** | `approval_audit_logs`, `impersonation_audit_logs` are append-only | Logs cannot be deleted, modified, or backfilled |
| **Approval Does Not Skip Execution** | Approved action is separate from execution trigger | Approval MUST NOT automatically execute the action |

**Immutable constraint:** Do NOT bypass these rules for convenience. If a rule seems inconvenient, it's a feature, not a bug.

#### 6.2.4 Scope Model (Tenant-Based)

The current scope model is tenant-only:

- **Scope Type:** `tenant` (immutable; plant/area/line/station are Phase 8+)
- **Scope Value:** Tenant ID or wildcard `*`
- **Scope Binding:** Every permission is granted to a user+role+tenant combination
- **Tenant Isolation:** Repository layer MUST filter all queries by `tenant_id`

**Immutable constraint:** Do NOT skip tenant filtering in any repository method. Do NOT introduce location-based scopes without Phase 8 design gate.

### 6.3 Impersonation Rules (DO NOT MODIFY)

Impersonation allows ADM/OTS to temporarily assume another role for demo, training, or support.

#### 6.3.1 Who Can Impersonate

**Allowed Impersonators:**
- `ADM` (Admin)
- `OTS` (On-the-Spot)

**Forbidden Impersonators:** Everyone else.

**Immutable constraint:** Do NOT add new impersonator roles without Phase 7+ design.

#### 6.3.2 Which Roles Can Be Assumed

**Allowed Acting Roles:** OPR, SUP, IEP, QCI, QAL, PMG, EXE

**Forbidden Acting Roles:** ADM, OTS (cannot impersonate other admins)

**Immutable constraint:** Do NOT allow impersonation of administrative roles. This is a security boundary.

#### 6.3.3 Time Bounds (Canonical)

- **Default Duration:** 60 minutes
- **Maximum Duration:** 480 minutes (8 hours)
- **Expiration Check:** `expires_at > now() AND revoked_at IS NULL`
- **Auto-Cleanup:** Expired sessions are silently ignored; no explicit revocation required

**Immutable constraint:** Do NOT extend max duration or eliminate time bounds. Time-bound elevation is a core principle.

#### 6.3.4 Requester ≠ Approver Still Applies

**Critical rule:** Impersonation DOES NOT bypass the requester ≠ approver check.

- ADM (impersonating QAL) creates an approval request → requester_id = ADM (real user_id)
- ADM (impersonating QAL) tries to approve their own request → REJECTED (requester_id == decider_real_id)
- ADM (impersonating QAL) can approve someone *else's* request → APPROVED

**Immutable constraint:** Do NOT skip the user_id check in `decide_approval_request()`. Separation of duties is absolute.

#### 6.3.5 Impersonation Does NOT Alter Permissions

When impersonating, the acting role's permission family is used:

- Real user: ADM (ADMIN permission)
- Acting as: OPR (EXECUTE permission)
- Call `/operations/{id}/start` → Requires EXECUTE → Granted (via acting role)

Impersonation does NOT grant permissions beyond the acting role's family.

**Immutable constraint:** Do NOT use impersonation to escalate permissions. Use role assignment instead.

#### 6.3.6 Audit Trail (Mandatory)

Every impersonation action logs:

| Event | Logged | Purpose |
|---|---|---|
| SESSION_CREATED | user_id, acting_role_code, duration_minutes, reason | Who impersonated whom, why |
| SESSION_REVOKED | session_id, revoked_at | When session ended |
| PERMISSION_USED | session_id, permission_family, endpoint | What actions were taken |

**Immutable constraint:** Do NOT skip audit logging for impersonation. Compliance depends on a complete trail.

### 6.4 Approval Engine Rules (DO NOT MODIFY)

The approval engine enforces separation of duties for critical actions.

#### 6.4.1 Action Types (Canonical)

The following action types require approval:

```
QC_HOLD    — Quality hold; defect found
QC_RELEASE — Quality release; hold lifted
SCRAP      — Scrap decision; material waste
REWORK     — Rework decision; re-process operation
WO_SPLIT   — Work order split into two
WO_MERGE   — Merge two work orders
```

**Immutable constraint:** Do NOT add new action types without Phase 7 design. Each action type must have explicit approval rules.

#### 6.4.2 Approval Rules (Data-Driven)

Approval rules are stored in the database and define (action_type, approver_role_code) pairs.

**Seeded Rules:**
- QC_HOLD → QAL
- QC_RELEASE → QAL
- SCRAP → QAL, PMG (multi-role)
- REWORK → QAL
- WO_SPLIT → PMG
- WO_MERGE → PMG

**Immutable constraint:** Do NOT hardcode approval rules in application logic. Rules must be table-driven for Phase 8+ extensibility.

#### 6.4.3 Approval Request Lifecycle

1. **CREATE** — Requester submits request with action_type, reasone, subject_ref
2. **DECIDE** — Approver (with correct role) reviews and issues APPROVED or REJECTED
3. **FINALIZED** — Once decided, request is immutable; no re-decision allowed

**Immutable constraint:** Do NOT allow re-decision or modification of decided requests. Once finalized, the record is permanent.

#### 6.4.4 Relationship to RBAC

**Both** RBAC and approval rules must be satisfied:

- RBAC Check: Decider has APPROVE permission family → Yes/No
- Approval Rule Check: Decider's role is in `approval_rules` for action_type → Yes/No
- **Both must pass.** RBAC alone is insufficient; role-specific rules add a second gate.

Example: PMG can APPROVE (RBAC) but cannot approve QC_HOLD (approval rules) because only QAL is listed.

**Immutable constraint:** Do NOT remove the approval rule check. Approval is not just RBAC.

### 6.5 Persona Semantics (Frontend UX Only)

Persona determines the **default landing page** and **menu visibility**, NOT permissions.

#### 6.5.1 Persona Resolution (Canonical)

When a user logs in, their role_code is mapped to a single Persona:

| Role Code | Persona | Landing Page |
|---|---|---|
| OPR | OPR | `/station-execution` |
| SUP | SUP | `/operations?lens=supervisor` |
| IEP | IEP | `/operations?lens=ie` |
| QCI | QCI | `/operations?lens=qc` |
| PMG | PMG | `/dashboard` |
| EXE | EXE | `/dashboard` |
| QAL | QCI | `/operations?lens=qc` (map QAL to QC persona) |
| ADM, OTS | (no default) | Free roaming; no forced landing |

**Immutable constraint:** Do NOT change these mappings without Phase 7+ design. Persona landing is a UX contract.

#### 6.5.2 Persona is NOT Authorization

**Critical rule:** Persona is **UX only** and does NOT grant or deny permissions.

- A user with OPR persona **can still call** `/dashboard` if the backend permits
- Frontend does NOT check persona before calling APIs
- Backend 403 errors are handled uniformly (access denied, redirect to default landing)
- Frontend NEVER hardcodes permissions based on persona

**Immutable constraint:** Do NOT implement permission checks in the frontend. Backend is always the source of truth for authorization.

#### 6.5.3 Menu Visibility (Per Persona)

Each persona has a default menu visible in the sidebar:

| Persona | Default Menu | Notes |
|---|---|---|
| OPR | Station Execution | Single focused entry |
| SUP | Global Operations (supervisor lens) | Shift management |
| IEP | Global Operations (IE lens) | Process variance |
| QCI | Global Operations (QC lens) | Quality tracking |
| PMG | Dashboard, Global Operations | Manager overview |
| EXE | Dashboard | Read-only reporting |
| ADM/OTS | All available screens | Admin access |

**Immutable constraint:** Do NOT change menu mappings without phase design. Add new menus as separate Phase 7 design discussions.

### 6.6 Authentication vs Authorization (Separate Concerns)

**Critical Principle:** Authentication and Authorization are **completely separate.**

#### 6.6.1 Authentication (Proves Identity)

- **What:** Is the user who they claim to be?
- **How:** Username + password → JWT token
- **Resolution:** At login time; role is resolved from `user_roles` table
- **Frontend Guard:** RequireAuth component checks `isAuthenticated` before allowing route access
- **Expiry:** JWT expires after 30 minutes; user must re-login

**Immutable constraint:** Do NOT encode permissions in JWT. JWT only proves identity.

#### 6.6.2 Authorization (Grants Permission)

- **What:** Is the user allowed to perform this action?
- **How:** Backend checks role + permission family at every API call
- **Resolution:** At request time; can change mid-session if role/permissions are updated
- **Frontend Constraint:** Frontend has NO permission logic; all 403 errors are handled uniformly
- **Scope:** Tenant_id must match request context

**Immutable constraint:** Do NOT move authorization logic to the frontend. Backend must always decide.

#### 6.6.3 Why This Separation?

- **Permissions can change mid-session** (admin updates role)
- **Impersonation sessions can expire** mid-session
- **Approval rules can be updated** without re-login
- **Frontend caching = security vulnerability** if it encodes permissions

**Immutable constraint:** This separation is architectural; do NOT collapse it.

### 6.7 Explicitly Forbidden Changes (Phase 7+)

The following changes are **FORBIDDEN** without a new phase design gate:

#### 6.7.1 Granting EXECUTE to ADM/OTS

**Forbidden:** `ADM → VIEW, ADMIN, EXECUTE` (adding EXECUTE)

**Reason:** ADM is administrative; operational execution should be delegated to OPR/SUP. If ADM needs to execute, they impersonate OPR.

**What to do instead:** If Phase 7 requires admin execution, design a new role (e.g., MES_ADMIN) with deliberate permissions and document the architectural change.

#### 6.7.2 Bypassing Approval for QC/Scrap/Rework

**Forbidden:** Making QC_HOLD, SCRAP, REWORK auto-execute without approval

**Reason:** Separation of duties is a core principle. These actions impact product quality; approval is non-optional.

**What to do instead:** If approval feels slow, optimize the approval workflow (e.g., fast-track rules, delegation) but do NOT eliminate the gate.

#### 6.7.3 Encoding Permission Logic in Frontend

**Forbidden:** 

```js
// FORBIDDEN: Permission check in frontend
if (user.role === "OPR") {
  // Show START button
}
```

**Reason:** Frontend cannot be trusted. Permissions change server-side; frontend caches can go stale.

**What to do instead:** Call the API; if you get 403, hide the button. Trust the backend.

#### 6.7.4 Modifying Execution Invariants

**Forbidden:** Changing the execution state machine without documentation:

```python
# FORBIDDEN: Removing the START-before-COMPLETE rule
if operation.status != OperationStatus.PENDING:
    raise ValueError("Must be PENDING to START")
```

**Reason:** Execution invariants are published in `/docs/system/mes-business-logic-v1.md`. Changing them requires a phase update.

**What to do instead:** If Phase 7 needs different execution rules, document them explicitly and update the business logic contract.

#### 6.7.5 Introducing Planning (APS) Logic into Execution

**Forbidden:** Adding scheduling constraints to the operation execution layer:

```python
# FORBIDDEN: Scheduling logic in operation service
if operation.planned_start > now():
    raise ValueError("Cannot start before planned time")
```

**Reason:** MES does not do planning; it executes. Planning constraints belong in a Phase 7+ APS module.

**What to do instead:** If Phase 7 needs planning enforcement, build a separate planning service and guard execution at the API layer (not in the core engine).

#### 6.7.6 Removing Tenant Isolation

**Forbidden:** Skipping tenant_id checks in repositories:

```python
# FORBIDDEN: No tenant filter
operations = db.query(Operation).all()
```

**Reason:** Multi-tenant isolation is a core architectural principle. Violating it can expose data.

**What to do instead:** Always filter by tenant_id. If you need cross-tenant data for a new feature, design it explicitly with Phase 7+ governance.

#### 6.7.7 Adding New Impersonator Roles

**Forbidden:** Allowing QAL to impersonate OPR

**Reason:** Impersonation is an emergency/support tool for ADM/OTS only. Widespread impersonation creates audit trails that are hard to interpret.

**What to do instead:** If Phase 7 needs delegation, design a formal permission delegation system (not impersonation) and document it.

#### 6.7.8 Skipping Audit Logs for Sensitive Actions

**Forbidden:** Omitting approval decision logs

**Reason:** Compliance requires a complete trail. Skipping logs is a audit failure.

**What to do instead:** Always log approval requests, decisions, and impersonation actions. If logs are too verbose, add filtering at query time, not insert time.

### 6.8 Required Verification Discipline

Any task touching governance, execution, or approval logic MUST follow this discipline:

#### 6.8.1 Run Seed Scenarios (S1–S4)

After any change to execution or approval logic, run the seed regression:

```bash
cd /workspaces/FleziBCG/backend
python scripts/verify_users_auth.py
python scripts/verify_approval.py
python scripts/verify_impersonation.py
```

**All 34 checks must PASS.** If any check fails, the change has broken a core invariant.

**Immutable constraint:** Do NOT bypass seed verification. Seed scenarios are the contract.

#### 6.8.2 Build Frontend Without Errors

After any frontend change:

```bash
cd /workspaces/FleziBCG/frontend
npm run build
```

**Zero TypeScript errors required.** If build fails, the change is incomplete.

**Immutable constraint:** Do NOT merge broken builds. Frontend code must type-check.

#### 6.8.3 Document Changes to Business Logic

If a change affects business rules, update `/docs/system/mes-business-logic-v1.md`:

- Addition example: Phase 7 adds multi-role assignment → document in section 2.6
- Modification example: Phase 7 extends persona landing → update section 5.1
- Bug fix example: Fixed approval requester check → reference the fix in section 8.2

**Immutable constraint:** Business logic documentation must stay in sync with code. If docs and code diverge, someone loses trust.

#### 6.8.4 No Execution Logic in Frontend

**Rule:** Frontend must never derive execution status or state machine logic.

**What frontend CAN do:**
- Display status from API (status = "IN_PROGRESS")
- Show generic "Processing..." message
- Render buttons based on API success/failure

**What frontend MUST NOT do:**
- Compute status from events: `status = events.length > 0 ? "IN_PROGRESS" : "PENDING"`
- Infer state machine: `if (events.last() == "BLOCK") canStart = false`
- Make business rule decisions: `if (scrap_qty > threshold) requireApproval = true`

**Immutable constraint:** Backend is the source of truth. Frontend is a dumb view.

#### 6.8.5 Impersonation Audit Trail Check

If any approval or execution action happens during impersonation, verify the audit logs:

```python
from backend.app.models import ImpersonationAuditLog
logs = db.query(ImpersonationAuditLog).filter(
    ImpersonationAuditLog.session_id == session_id
).all()
# Should include PERMISSION_USED events for each action
```

**Immutable constraint:** Impersonation without audit is a security failure. Always log.

---

## Summary: Phase 6 Lock

Phase 6 establishes a **permanent, immutable governance foundation** for the MES.

**No Phase 7, 8, or future work may violate these rules without explicit architectural review.**

If you find a rule inconvenient, it is intentional. Submit a Phase 7 feature request instead of working around the rule.

**The Phase 6 lock exists to prevent governance drift and keep the system maintainable.**