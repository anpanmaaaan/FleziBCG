# MES Lite – Business Logic Contract (Phase 6)

**Version:** 1.0  
**Phase:** 6 (Complete)  
**Date:** April 3, 2026  
**Status:** Locked

---

## Table of Contents

1. [System Scope & Core Principles](#1-system-scope--core-principles)
2. [Core Domain Model & Entity Semantics](#2-core-domain-model--entity-semantics)
3. [Execution Logic](#3-execution-logic-core-mes-behavior)
4. [Status Derivation Rules](#4-status-derivation-rules)
5. [Persona & UX Semantics (Phase 6B)](#5-persona--ux-semantics-phase-6b)
6. [Authorization & Governance Logic (Phase 6C)](#6-authorization--governance-logic-phase-6c)
7. [Impersonation (Temporary Elevation)](#7-impersonation-temporary-elevation)
8. [Approval Engine Logic](#8-approval-engine-logic)
9. [Authentication & Login Flow](#9-authentication--login-flow)
10. [Demo & Seed Data Semantics](#10-demo--seed-data-semantics)
11. [Explicit Non-Goals (Phase Boundary)](#11-explicit-non-goals-phase-boundary)

---

## 1. System Scope & Core Principles

### 1.1 What This System Is Responsible For

The MES Lite system is a **Production Execution System** designed to track and manage:

- **Production Orders (POs)** — Planning-level scheduling and demand
- **Work Orders (WOs)** — Execution-level unit of work derived from POs
- **Operations (OPs)** — Production unit that executes within a work order
- **Execution Events** — Append-only log of state transitions (START, COMPLETE, BLOCK, etc.)
- **Status Derivation** — Real-time status computation from execution events without mutation
- **User & Role Management** — Persistent identity and RBAC permission enforcement
- **Temporary Elevation** — Secure impersonation for demo, support, and emergency scenarios
- **Approval Workflows** — Separation-of-duties enforcement for critical actions
- **Persona-Based UX** — Role-driven default landing and menu scope

### 1.2 What This System Is Explicitly NOT Responsible For

The following areas are **out of scope** for Phase 6 and beyond:

- **Advanced Planning & Scheduling (APS)** — No algorithmic optimization or constraint-based scheduling
- **Quality Control Workflow UI** — No QC inspection entry, sampling logic, or disposition UI
- **Material Backflush** — No material accounting, BOM explosion, or inventory integration
- **Supply Chain Integration** — No supplier, purchase order, or material receipt workflows
- **Single Sign-On / Active Directory** — No external identity federation; local users only
- **Real-time Streaming** — No Kafka, websocket, or event broker dependency
- **Microservices Architecture** — Modular monolith; no service extraction without design review

### 1.3 Event-Driven Execution Philosophy

The system uses **append-only execution events** as its source of truth:

- Every state change (START, COMPLETE, BLOCK, etc.) is recorded as an immutable event
- Status is **derived** from the event log in real-time, never mutated
- Events contain only facts (who, what, when, where); no derived state
- This ensures auditability, replayed history, and idempotency

### 1.4 Backend-as-Source-of-Truth Principle

- **Frontend does NOT infer permission or role logic**
- All authorization decisions are made by the backend API
- Frontend can only see what the backend returns; it makes no decisions based on role
- A 403 Forbidden from any API means "you don't have permission" — handled uniformly
- Persona landing is **UX only**, not authorization

### 1.5 Separation of Authentication vs Authorization

- **Authentication (AuthN)** — Who are you? Resolved via JWT after login
- **Authorization (AuthZ)** — What can you do? Resolved by backend RBAC on every API call
- Frontend guards access to **routes** based on authentication state (logged-in vs logged-out)
- Backend guards access to **data and actions** based on authorization (role, permission, scope, approval)
- Never move authorization checks to the frontend

---

## 2. Core Domain Model & Entity Semantics

### 2.1 Production Order (PO)

**Purpose:** Planning-level demand signal; defines what product and quantity is requested

- **Immutable:** Once created, PO properties do not change (customer, product, quantity, dates)
- **Parent:** None (root entity)
- **Child:** Multiple Work Orders
- **Lifecycle:** PO is created in a planning system (external to Phase 1 MES); MES reads it and derives statistics (progress, late/on-time status)
- **MES Role:** Planning context and filter only; does not drive execution behavior directly

### 2.2 Work Order (WO)

**Purpose:** Execution-level unit of work that must be completed by a specific date

- **Derived from:** Production Order (1-to-many)
- **Composition:** Contains 1 or more Operations
- **Status:** Derived from operation statuses (PENDING, IN_PROGRESS, BLOCKED, COMPLETED, LATE)
- **Lifecycle:**
  - PENDING: All operations are pending
  - IN_PROGRESS: At least one operation is in progress
  - BLOCKED: At least one operation is blocked (no other operations in progress)
  - COMPLETED: All operations are completed
  - LATE: Completed after planned_end
- **Execution Entry Point:** Users navigate to WOs to see work, not POs

### 2.3 Operation (OP)

**Purpose:** Smallest execution unit; represents a single production activity

- **Parent:** Work Order (many-to-one)
- **Properties:**
  - `operation_number` — Unique human-readable identifier in sequence
  - `sequence` — Order within work order
  - `workstation` — Where it runs (e.g., "PRESS-01", "ASSEMBLY-A")
  - `planned_start`, `planned_end` — Expected time window
  - `actual_start`, `actual_end` — Recorded time from execution events
  - `quantity` — Target units to produce
  - `completed_qty`, `good_qty`, `scrap_qty` — Recorded from execution
  - `qc_required` — Flag indicating QC checkpoint needed
  - `block_reason_code` — Reason if blocked (e.g., "UPSTREAM_DELAY", "MATERIAL")
- **Status:** Derived from execution events (PENDING, IN_PROGRESS, BLOCKED, COMPLETED, LATE, COMPLETED_LATE)
- **Execution Entry Point:** Station Execution uses `/station-execution?operationId=...` to start, track, complete

### 2.4 Execution Event

**Purpose:** Immutable record of every state change

- **Properties:**
  - `operation_id` — Which operation changed
  - `event_type` — START, REPORT_QUANTITY, COMPLETE, BLOCK, ABORT
  - `created_by` — User who triggered event
  - `created_at` — Timestamp (server-generated)
  - `payload` — Event-specific data (e.g., quantities for REPORT_QUANTITY, reason for BLOCK)
- **Append-Only:** Never updated or deleted; new events are added only
- **Status Derivation:** Status is computed by scanning events in chronological order

### 2.5 User

**Purpose:** Persistent identity for login and audit trail

- **Properties:**
  - `user_id` — Unique identifier (UUID-like; externally assigned)
  - `username` — Display name for login
  - `email` — Optional contact
  - `password_hash` — Argon2 hash of password
  - `tenant_id` — Multi-tenant scope (default: "default")
  - `is_active` — Whether login is permitted
- **Lifecycle:** Created once; can be deactivated but not deleted
- **Password:** Only stored as hash; system does not email/reset passwords in Phase 6

### 2.6 Role

**Purpose:** Named job category for RBAC

- **System Roles (immutable in Phase 6):**
  - `OPR` (Operator) — Execute work; limited view
  - `SUP` (Supervisor) — Execute + view; shift leader duties
  - `IEP` (IE / Process) — Configure; process improvement focus
  - `QCI` (QA / Quality Inspector) — View; inspection duties
  - `QAL` (QA / Lines) — View + Approve; quality sign-off
  - `PMG` (Production Manager) — View + Approve; planning & approval
  - `EXE` (Execution Reporter) — View only; data entry for external systems
  - `ADM` (Admin) — Unrestricted; system administration
  - `OTS` (On-the-Spot) — Support/Demo; same privileges as ADM but audit-tagged differently
- **Properties:** `code`, `name`, `description`, `is_system` (all system roles are is_system=true)

### 2.7 Permission

**Purpose:** Atomic authorization primitive

- **Permission Families (static):**
  - `VIEW` — Read access to data
  - `EXECUTE` — Trigger execution state changes (START, COMPLETE, REPORT, etc.)
  - `APPROVE` — Approve or reject workflow requests
  - `CONFIGURE` — Modify parameters (processes, standards, etc.)
  - `ADMIN` — Full system access and management
- **Role-to-Permission Mapping:**
  ```
  OPR    → EXECUTE
  SUP    → VIEW, EXECUTE
  IEP    → VIEW, CONFIGURE
  QCI    → VIEW
  QAL    → VIEW, APPROVE
  PMG    → VIEW, APPROVE
  EXE    → VIEW
  ADM    → VIEW, ADMIN
  OTS    → VIEW, ADMIN
  ```
- **Scope-Qualified:** Permissions are also bound to scope (e.g., tenant-level or wildcard)

### 2.8 Scope

**Purpose:** Tenant + optional location hierarchy for multi-tenant + site-based access control

- **Scope Type:** Currently `tenant` (site/plant/line scopes are future)
- **Scope Value:** Tenant identifier (e.g., "default")
- **Assignment:** User is assigned a role scoped to a specific tenant
- **Tenant Isolation:** API queries are filtered by `tenant_id` at repository layer

### 2.9 Approval Request & Decision

**Purpose:** Separation of duties; some actions require approval before execution

- **Approval Request:**
  - `action_type` — What is being requested (QC_HOLD, QC_RELEASE, SCRAP, REWORK, WO_SPLIT, WO_MERGE)
  - `requester_id` — Who requested it (real user_id in all cases, even if impersonating)
  - `status` — PENDING, APPROVED, or REJECTED
  - `reason` — Why the action is needed
  - `subject_ref` — What it applies to (e.g., operation_id, work_order_id)
  - `created_at`, `updated_at` — Timestamps
- **Approval Decision:**
  - `decision` — APPROVED or REJECTED
  - `decider_id` — Real user_id who approved (requester cannot approve own)
  - `decider_role_code` — Role acting at decision time (may be impersonation)
  - `comment` — Optional reasoning
  - `impersonation_session_id` — If decision made under impersonation
- **Lifecycle:**
  1. Requester creates request (status=PENDING)
  2. Approver (specific role) reviews and issues decision
  3. Once decided, cannot be re-decided

---

## 3. Execution Logic (Core MES Behavior)

### 3.1 Execution State Machine

An operation transitions through states via execution events:

```
PENDING
  ↓ (START)
IN_PROGRESS
  ↓ (REPORT_QUANTITY)
IN_PROGRESS (multiple reports allowed)
  ├─ (BLOCK) → BLOCKED
  │            ↓ (UNBLOCK / resolve upstream)
  │            (back to IN_PROGRESS)
  ├─ (COMPLETE) → COMPLETED
  │                ├─ (within planned_end) → COMPLETED (on-time)
  │                └─ (after planned_end) → COMPLETED_LATE
  └─ (ABORT) → ABORTED (terminal)
```

### 3.2 Event Types & Semantics

| Event Type | Precondition | Effect | Payload |
|---|---|---|---|
| **START** | status = PENDING | actual_start = now, status → IN_PROGRESS | operator_id (optional) |
| **REPORT_QUANTITY** | status ∈ {IN_PROGRESS} | good_qty += amount, scrap_qty += amount | good_qty, scrap_qty (both ≥ 0) |
| **COMPLETE** | status = IN_PROGRESS | actual_end = now, status → COMPLETED or COMPLETED_LATE | — |
| **BLOCK** | status ∈ {IN_PROGRESS} | status → BLOCKED | block_reason_code (required) |
| **UNBLOCK** | status = BLOCKED | status → IN_PROGRESS (resume) | — |
| **ABORT** | status ∈ {PENDING, IN_PROGRESS, BLOCKED} | status → ABORTED (terminal; cannot resume) | abort_reason_code |

### 3.3 Execution Invariants

**What IS allowed:**

- Multiple REPORT_QUANTITY events for a single operation (partial completion)
- Blocking and unblocking (BLOCK ↔ IN_PROGRESS allowed multiple times)
- Quantity reported can exceed planned quantity (no over-production guard in Phase 6)
- COMPLETE after any number of REPORT_QUANTITY events
- ABORT from any non-terminal state

**What is explicitly FORBIDDEN:**

- START on non-PENDING operation (idempotency: second START is rejected)
- COMPLETE on non-IN_PROGRESS operation
- BLOCK on non-executing operation
- Transition PENDING → BLOCKED (must START first)
- Transition BLOCKED → COMPLETED (must UNBLOCK and return to IN_PROGRESS first)

### 3.4 Idempotency & Append-Only Guarantees

- **Append-Only Events:** New events are added; old events are never modified or deleted
- **Status Idempotency:** Computing status by replaying events always yields the same result
- **Duplicate Prevention:** The API layer (not documented here) prevents exact duplicate submissions within a short window
- **Event Ordering:** Events are timestamped and ordered by `created_at`; no out-of-order processing

---

## 4. Status Derivation Rules

Status is not stored; it is computed by inspecting the most recent relevant event(s) for each operation.

### 4.1 Operation Status

Derived by examining execution events in chronological order:

| Status | Condition | Rule |
|---|---|---|
| **PENDING** | No START event | Operation has never been started |
| **IN_PROGRESS** | Latest event is START (no REPORT_QUANTITY after) | Operation has started; no quantity reported yet |
| **IN_PROGRESS** | Latest non-terminal event is REPORT_QUANTITY or START | Operation is active; quantities being reported |
| **BLOCKED** | Latest event is BLOCK (and no subsequent UNBLOCK) | Operation is waiting; resources unavailable |
| **COMPLETED** | Latest event is COMPLETE AND actual_end ≤ planned_end | Finished on or before deadline |
| **COMPLETED_LATE** | Latest event is COMPLETE AND actual_end > planned_end | Finished but after deadline |
| **ABORTED** | Latest event is ABORT | Terminated; will not resume |

### 4.2 Work Order Status

Aggregated from all child operations:

| Status | Condition |
|---|---|
| **PENDING** | All child operations are PENDING |
| **IN_PROGRESS** | At least one operation is IN_PROGRESS AND no operations are BLOCKED |
| **BLOCKED** | At least one operation is BLOCKED AND no operations are IN_PROGRESS |
| **COMPLETED** | All child operations are COMPLETED or ABORTED AND at least one is COMPLETED |
| **COMPLETED_LATE** | All child operations are COMPLETED or ABORTED AND at least one is COMPLETED_LATE AND none are COMPLETED (on-time) |
| **LATE** | WO not yet completed AND planned_end < now (forecasting) |

### 4.3 Progress Calculation

- **Operation Progress (%):** `(completed_qty / quantity) × 100` where completed_qty = good_qty + scrap_qty
- **Work Order Progress (%):** Average of all child operation progress percentages
- **Timing Indicators:**
  - `delay_minutes` — Max(0, now - planned_end) if not yet completed
  - `cycle_time_minutes` — (actual_end - actual_start) if completed

---

## 5. Persona & UX Semantics (Phase 6B)

**Core Principle:** Persona determines **default landing page** and **menu scope**, not permissions. All authorization is backend-driven.

### 5.1 Persona Resolution

When a user logs in, their role_code is mapped to a Persona:

| Role Code → Persona | Landing Page | Primary Function |
|---|---|---|
| OPR → OPR | `/station` | Execute work at station |
| SUP → SUP | `/operations?lens=supervisor` | Monitor WO/OP; supervisor-focused KPIs |
| IEP → IEP | `/operations?lens=ie` | Process analysis; cycle time variance |
| QCI → QCI | `/operations?lens=qc` | Quality KPIs; defect tracking |
| PMG → PMG | `/dashboard` | Production metrics; KPI overview |
| EXE → EXE | `/dashboard` | Dashboard; read-only reporting |
| QAL → QCI | `/operations?lens=qc` | Map QAL (approval role) to QC persona |
| ADM, OTS → (multiple options) | (no default; free roam) | Admin access to all screens |

### 5.2 Menu Scope by Persona

Each persona has a **default menu** that drives what the user sees. This is UX only.

| Persona | Menu Items | Notes |
|---|---|---|
| **OPR** | • Station Execution | Single focused entry point |
| **SUP** | • Global Operations (supervisor lens) | Shift management view |
| **IEP** | • Global Operations (IE lens) | Process variance analysis |
| **QCI** | • Global Operations (QC lens) | Quality defect/variance view |
| **PMG** | • Dashboard<br>• Global Operations (all lenses) | Manager overview + operation detail |
| **EXE** | • Dashboard | Read-only reporting |
| **ADM/OTS** | (all available screens) | Unrestricted system access |

### 5.3 Operation Lenses

The Global Operations screen shows different **analytical lenses** based on persona:

| Lens | Persona | Focus |
|---|---|---|
| **supervisor** | SUP, PMG | Blocked/delayed operations; WO status; overdue alerts |
| **ie** | IEP, PMG | Cycle time variance; repeat delays; high-variance operations |
| **qc** | QCI, QAL, PMG | QC failures; defect rates; scrap trends |

### 5.4 Persona is NOT Authorization

- A user with OPR persona **can still access** `/dashboard` if the backend permits (no frontend block)
- Persona is **suggestion only** for the default entry point
- Frontend does **not** check persona before calling APIs
- Backend may still return 403 if the user lacks the required permission
- Frontend respects 403 and shows "Access Denied" or redirects to default landing

---

## 6. Authorization & Governance Logic (Phase 6C)

### 6.1 Permission Families & Role Mapping

Every API endpoint that mutates or returns restricted data requires one of these permissions:

| Family | Granted To | Semantics |
|---|---|---|
| **VIEW** | OPR, SUP, IEP, QCI, QAL, PMG, EXE, ADM, OTS | Read access to execution, status, KPIs |
| **EXECUTE** | OPR, SUP, ADM, OTS | Trigger execution state changes (START, COMPLETE, REPORT, BLOCK, ABORT) |
| **APPROVE** | QAL, PMG, ADM, OTS | Create/decide approval requests |
| **CONFIGURE** | IEP, ADM, OTS | Modify parameters (standards, thresholds, process definitions) |
| **ADMIN** | ADM, OTS | System administration (user mgmt, role assignment, audit access) |

### 6.2 Permission Check Flow

1. **Request arrives at API**
2. **Decode JWT** → resolve user_id, tenant_id, role_code
3. **Look up UserRole** in database for (user_id, role_id, tenant_id)
4. **Look up RolePermission** for (role_id, required_permission_family)
5. **Check Scope** — User's tenant_id matches request tenant_id (or has wildcard)
6. **If impersonating:** Use acting_role_code's permission family directly (skip DB lookup)
7. **Decision:** 200 OK (permitted) or 403 Forbidden (denied)

### 6.3 Scope Model

All permissions are scoped:

- **Scope Type:** `tenant` (only implemented type in Phase 6)
- **Scope Value:** Tenant identifier or wildcard `*`
- **Tenant Isolation:** Repositories filter queries by `tenant_id`
- **Future Scopes:** Plant, Area, Line (not Phase 6)

### 6.4 Separation of Duties Principles

The system enforces several SOD rules:

| Rule | Enforcement | Purpose |
|---|---|---|
| Requester ≠ Approver | `decide_approval_request()` checks `decider_user_id ≠ requester_id` | Prevent self-approval |
| Role-Based Approval | `approval_rules` table defines per-action approver roles | No one can approve an action they're not authorized for |
| Immutable Audit Trail | `approval_audit_logs`, `impersonation_audit_logs` are append-only | Compliance: cannot hide who did what |
| Impersonation Does Not Bypass Approval | `require_approval` checks role, not impersonation status | Elevated users cannot skip review |

---

## 7. Impersonation (Temporary Elevation)

**Purpose:** Allow ADM/OTS to act as other roles for demo, training, or emergency fixes without permanently granting the role.

### 7.1 Who Can Impersonate (Impersonators)

Only these roles can create an impersonation session:

- `ADM` (Admin)
- `OTS` (On-the-Spot/Support)

Everyone else is forbidden; attempting to create a session will raise `PermissionError`.

### 7.2 Which Roles Can Be Acted As (Acting Roles)

Impersonators CANNOT act as:

- `ADM` (cannot impersonate admin)
- `OTS` (cannot impersonate support)

Attempting to impersonate ADM or OTS will raise `ValueError`.

Allowed acting roles:

- `OPR, SUP, IEP, QCI, QAL, PMG, EXE` (any operational role)

### 7.3 Time-Bound Sessions

- **Default Duration:** 60 minutes
- **Maximum Duration:** 480 minutes (8 hours)
- **Expiration Logic:** `expires_at = now() + duration_minutes`
- **Active Check:** Session is active if `revoked_at IS NULL AND expires_at > now()`
- **Expired sessions** are automatically ignored by `get_active_impersonation_session()`

### 7.4 Permission Resolution During Impersonation

When impersonating:

1. **JWT still contains real_role_code** (e.g., "ADM")
2. **Impersonation session is looked up** at request time
3. **If active,** effective_role_code ← acting_role_code
4. **Permission check** uses SYSTEM_ROLE_FAMILIES[acting_role_code] directly
5. **No DB lookup** for impersonated role permissions (deterministic)

Example:
- Real user: ADM (ADMIN permission)
- Acting as: OPR (EXECUTE permission)
- Call to `/operations/{id}/start` → Requires EXECUTE → Acting as OPR → Granted

### 7.5 Requester ≠ Approver Still Applies During Impersonation

**Key Rule:** Even if ADM is impersonating QAL and QAL can approve, ADM themselves CANNOT approve a request they created.

- Check uses REAL user_id (requester_id), not acting_role_code
- Prevents: ADM (impersonating QAL) creates a QC_HOLD request, then QAL-approves it
- Allows: ADM (impersonating QAL) approves someone else's QC_HOLD request

### 7.6 Audit Semantics

Every impersonation action is logged:

| Event | Logged | Purpose |
|---|---|---|
| **SESSION_CREATED** | user_id, acting_role_code, duration_minutes, reason | Who impersonated whom when, why |
| **SESSION_REVOKED** | session_id, revoked_at | When impersonation ended |
| **PERMISSION_USED** | session_id, permission_family, endpoint | What permissions were exercised during session |

Audit logs include REAL user_id (even when acting), so there is no ambiguity about who actually performed the action.

---

## 8. Approval Engine Logic

### 8.1 Action Types Requiring Approval

These actions trigger approval request workflows:

| Action Type | Typical Initiator | Default Approver Role |
|---|---|---|
| **QC_HOLD** | Operator / QC | QAL (QA Lead) |
| **QC_RELEASE** | QC / Operator | QAL |
| **SCRAP** | Operator / QC | QAL or PMG |
| **REWORK** | Operator | QAL |
| **WO_SPLIT** | Planner / Manager | PMG (Production Manager) |
| **WO_MERGE** | Planner / Manager | PMG |

### 8.2 Approval Request Lifecycle

1. **CREATE (Requester)**
   - User submits request: action_type, subject_ref (op/wo id), reason
   - Requester role is recorded (may be impersonifying)
   - Status ← PENDING
   - Audit log: REQUEST_CREATED

2. **DECIDE (Approver)**
   - Approver with correct role reviews
   - Must NOT be the requester (checked by user_id, not role)
   - Issues decision: APPROVED or REJECTED
   - Decision record created with decider_id, decider_role_code, impersonation_session_id
   - Request status updated to match decision
   - Audit log: DECISION_MADE

3. **FINALIZED**
   - Once decided, request is immutable
   - Attempting to re-decide raises ValueError

### 8.3 Approval Rule Engine

- **approval_rules table** defines (action_type, approver_role_code) pairs
- **Multi-role rules:** Some actions have multiple valid approvers
  - Example: SCRAP can be approved by QAL *or* PMG
- **get_approver_role_codes()** returns the SET of authorized roles for an action
- At decision time, `decide_approval_request()` checks `decider_role_code IN approved_roles`

### 8.4 Relationship with RBAC

- **RBAC enforces** that approver has APPROVE permission
- **Approval rules enforce** that approver's role is listed for the action_type
- Both must be satisfied; neither alone is sufficient
- Example: PMG can APPROVE (RBAC) but cannot approve QC_HOLD (approval_rules)

### 8.5 Relationship with Impersonation

- **Approver role can be impersonated**
  - ADM (impersonating QAL) can approve QC_HOLD
- **Requester cannot be bypassed**
  - ADM (impersonating QAL) cannot approve their own request
  - `requester_id` is always real user_id, not acting role
- **Audit captures the session**
  - `decision.impersonation_session_id` records if decision was made under impersonation

---

## 9. Authentication & Login Flow

### 9.1 Users Table

Store persistent user identities:

- `user_id` — Unique identifier (assigned externally)
- `username` — Display name for login (unique per tenant)
- `email` — Optional contact
- `password_hash` — Argon2-hashed password
- `tenant_id` — Multi-tenant scope (default: "default")
- `is_active` — Whether login is allowed
- `created_at`, `updated_at` — Timestamps

### 9.2 Login Flow

1. **Frontend:** User submits username + password to POST `/api/auth/login`
2. **Backend Auth:**
   - Query `users` table by (username, tenant_id)
   - Verify password using Argon2
   - Check is_active = true
   - If any check fails → 401 Unauthorized
3. **Role Resolution:**
   - Look up `user_roles` for (user_id, tenant_id) where is_active = true
   - Join with `roles` table to get role_code
   - Associate single role with user (Phase 6 limitation: one role per user per tenant)
4. **Token Creation:**
   - Call `create_access_token(identity)` → JWT signed with `jwt_secret_key`
   - JWT payload:
     ```json
     {
       "sub": "user_id",
       "username": "username",
       "email": "email@example.com",
       "tenant_id": "default",
       "role_code": "OPR",
       "exp": 1234567890
     }
     ```
   - Expiry: `jwt_access_token_expire_minutes` (default: 30 minutes)
5. **Return Response:**
   - HTTP 200 with access_token, token_type="bearer", user object
6. **Frontend Storage:**
   - Store token in localStorage as `mes.auth.token`
   - Set in Authorization header for all subsequent API calls

### 9.3 JWT Semantics

**What JWT Contains:**
- `sub` (user_id) — Identifies the user
- `username` — Display name
- `email` — Contact
- `tenant_id` — Tenant scope
- `role_code` — User's current role (before any impersonation)
- `exp` — Expiration time

**What JWT Does NOT Contain:**
- Permissions (derived at request time from DB)
- Impersonation state (looked up at request time)
- Token does not encode authorization; it only proves identity

**Why:** Permissions and impersonation can change mid-session. Deriving at request time guarantees fresh state.

### 9.4 RequireAuth Routing Guard

Frontend-side authentication guard (not authorization):

- Check `isAuthenticated` from AuthContext
- If false AND not initializing → Redirect to `/login`
- If true → Allow access to protected routes
- Login page auto-redirects authenticated users to "/" (or referrer)

### 9.5 401 Handling (Unauthorized)

- **Backend returns 401** when: Invalid token, expired token, missing Authorization header
- **Frontend handler:**
  - In httpClient, intercept 401 responses
  - Call `logout()` from AuthContext
  - Redirect to `/login`
  - Display "Session expired; please log in again"

---

## 10. Demo & Seed Data Semantics

### 10.1 Seed Scenarios (S1–S4)

Four predefined work-order scenarios that exercise core execution logic:

| Scenario | Description | Business Rule Validated |
|---|---|---|
| **S1: Normal Completion** | WO with 1 OP starts, quantities reported, completes on time | Normal path; status derivation; progress calculation |
| **S2: Completed Late** | WO with 1 OP completes after planned_end | Late detection; COMPLETED_LATE status |
| **S3: In Progress + Block** | WO with 2 OPs; one blocks, one in-progress | BLOCKED status; WO status aggregation; operator message |
| **S4: Repeat Variance** | Same operation repeats with different cycle times | Variance detection; delay frequency calculation |

### 10.2 Seed Users & Roles

Demo users created at init time for testing:

| Username | Password | Role | Purpose |
|---|---|---|---|
| admin | password123 | ADM | Test admin access |
| manager | password123 | PMG | Test approval & dashboard |
| supervisor | password123 | SUP | Test operation monitoring |
| operator | password123 | OPR | Test execution at station |
| qa | password123 | QAL | Test approval from QA perspective |

**Note:** Passwords are lowercase plain text for demo; production deployments must override via environment config or DB seeding.

### 10.3 Seed Data Purpose

- **NOT for realism:** Seed WOs may have unrealistic quantities, dates, etc.
- **FOR validation:** Each seed scenario validates one or two core business rules
- **Regression testing:** If a seed scenario fails, a core feature is broken

### 10.4 Seed Workflow

```
init_db() calls:
  ↓
seed_rbac_core()           → creates roles, permissions, assigns to roles
  ↓
seed_approval_rules()      → creates approval rule records
  ↓
seed_demo_users()          → creates users, binds via user_roles
  ↓
seed_all() (external)      → creates work orders, operations, execution events
  ↓
Verification script        → runs S1–S4 checks
```

---

## 11. Explicit Non-Goals (Phase Boundary)

### 11.1 What Phase 6 Does NOT Include

The following features are **explicitly out of scope** and will not be implemented in Phase 6:

#### 11.1.1 Advanced Planning & Scheduling (APS)

- No constraint-based scheduling engine
- No resource leveling or capacity optimization
- No simulation or what-if analysis
- Phase 7+ scope

#### 11.1.2 Quality Control Workflow

- **No QC Inspection UI:** Operators cannot enter QC measurements or pass/fail decisions in Phase 6
- **No Sampling Logic:** No statistical sampling plans or AQL-based acceptance
- **No Disposition Workflow:** "Hold for QC" exists as an approval request, but QC release is manual approval only
- Phase 7+ scope

#### 11.1.3 Material & Backflush

- No BOM (Bill of Materials) explosion
- No material allocation or reservations
- No inventory integration
- No pick/pack workflows
- Phase 8+ scope

#### 11.1.4 External System Integration

- No EDI (orders from customers)
- No SAP / ERP integration
- No WMS (warehouse management)
- No MMS (maintenance management)
- Phase 8+ scope

#### 11.1.5 Advanced RBAC Features

- **No multi-role assignment per user per tenant** (Phase 6 limitation: 1 role per user-tenant)
- **No custom roles** (all roles are system-defined)
- **No attribute-based access control (ABAC)** (only role + scope)
- **No dynamic permission grants** (permissions are static per role)
- Phase 7+ scope

#### 11.1.6 Single Sign-On & Directory Services

- No LDAP integration
- No SAML 2.0 federation
- No OAuth 2.0 / OpenID Connect
- No API key authentication (humans only)
- Phase 7+ scope

#### 11.1.7 Real-Time Streaming

- No WebSocket push notifications
- No Apache Kafka event broker
- No message queues (RabbitMQ, etc.)
- API polling only
- Phase 8+ scope

#### 11.1.8 Microservices Architecture

- System is a **modular monolith**
- Single FastAPI backend, single PostgreSQL database
- No service decomposition, API gateway, circuit breakers
- Monolith must remain for Phases 6–7; Phase 8+ can consider extraction if high-load scenarios emerge

#### 11.1.9 Data Warehouse / Analytics Platform

- No analytical data mart
- No aggregated KPI storage
- No pre-computed dashboards (real-time queries only)
- Phase 7+ scope

#### 11.1.10 Mobile Application

- Web browser only; no mobile app (iOS/Android)
- Phase 7+ scope

### 11.2 Why These Are Excluded

These features require:

1. **Significant domain expertise** (QC sampling, APS algorithms) that is out of scope for MVP phase
2. **New integration surfaces** (ERP, MMS) that depend on partner system availability
3. **Infrastructure investment** (Kafka, data warehouse) that is premature before use-case validation
4. **Complex UX patterns** (multi-role selection, attribute matching) that need user research
5. **Regulatory expertise** (FDA 21 CFR, GxP) that is customer-specific

### 11.3 How to Request Phase 7+

To propose additions beyond Phase 6:

1. Submit a feature request documenting:
   - **Business driver:** Why is this feature required?
   - **Scope:** How many operations / users affected?
   - **Constraints:** Regulatory, temporal, technical
   - **MVPs:** What is the minimal useful subset?
2. Get technical review and customer alignment
3. Create a Phase 7 design document (similar to this one)
4. Phase 6 code must not be modified for Phase 7 planning

---

## Appendix: Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-04-03 | MES Platform Team | Phase 6 completion; locked |

---

**End of Document**
