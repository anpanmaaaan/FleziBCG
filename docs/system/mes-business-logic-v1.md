# MES Lite – Business Logic Contract (Phase 6)

**Version:** 1.1  
**Phase:** 6 (Complete)  
**Date:** April 17, 2026  
**Status:** Locked

---

## Table of Contents

1. [System Scope & Core Principles](#1-system-scope--core-principles)
2. [Core Domain Model & Entity Semantics](#2-core-domain-model--entity-semantics)
3. [Two-Dimension Status Model](#3-two-dimension-status-model)
4. [Execution Logic](#4-execution-logic-core-mes-behavior)
5. [Status Derivation Rules](#5-status-derivation-rules)
6. [Persona & UX Semantics (Phase 6B)](#6-persona--ux-semantics-phase-6b)
7. [Authorization & Governance Logic (Phase 6C)](#7-authorization--governance-logic-phase-6c)
8. [Impersonation (Temporary Elevation)](#8-impersonation-temporary-elevation)
9. [Approval Engine Logic](#9-approval-engine-logic)
10. [Authentication & Login Flow](#10-authentication--login-flow)
11. [Demo & Seed Data Semantics](#11-demo--seed-data-semantics)
12. [Explicit Non-Goals (Phase Boundary)](#12-explicit-non-goals-phase-boundary)

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

The system uses **append-only execution events** as its source of truth for execution lifecycle:

- Every execution state change (START, COMPLETE, ABORT, etc.) is recorded as an immutable event
- **Execution lifecycle status** is **derived** from the event log in real-time, never mutated
- Events contain only facts (who, what, when, where); no derived state
- This ensures auditability, replayed history, and idempotency

**Two-Dimension Status Model (v1.1):** The system distinguishes between:
1. **ExecutionLifecycleStatus** — derived from events: `PLANNED → IN_PROGRESS → COMPLETED | ABORTED`
2. **ReadinessStatus** — planning/dispatch constraints (e.g., PENDING, BLOCKED, HOLD) that are orthogonal to execution lifecycle. See [§3 Two-Dimension Status Model](#3-two-dimension-status-model).

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
- **Status:** Derived from operation statuses — see [§5 Status Derivation Rules](#5-status-derivation-rules)
- **Lifecycle:**
  - PLANNED: All operations are in PLANNED state
  - IN_PROGRESS: At least one operation is in progress
  - COMPLETED: All operations are completed
  - LATE: Not yet completed AND planned_end < now (forecasting display state)
  - COMPLETED_LATE: Completed after planned_end (display state)
  - Note: LATE and COMPLETED_LATE are **WO-level derived display states**, not part of the operation execution lifecycle.
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
  - `block_reason_code` — Reason if blocked (readiness constraint; e.g., "UPSTREAM_DELAY", "MATERIAL")
- **Execution Lifecycle Status:** Derived from execution events: `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `ABORTED` — see [§3 Two-Dimension Status Model](#3-two-dimension-status-model)
- **Readiness Status:** Orthogonal dimension for dispatch/constraint state (not yet implemented in code) — see [§3.2](#32-readiness--dispatch-status-dimension-2)
- **Execution Entry Point:** Station Execution uses `/station-execution?operationId=...` to start, track, complete

### 2.4 Execution Event

**Purpose:** Immutable record of every state change

- **Properties:**
  - `operation_id` — Which operation changed
  - `event_type` — START, REPORT_QUANTITY, COMPLETE, ABORT (execution lifecycle events)\n  - Note: BLOCK/UNBLOCK are readiness constraint events, not execution lifecycle events — see [§3.2](#32-readiness--dispatch-status-dimension-2). Not yet implemented in code.
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
  - `PLN` (Planner) — View only; production planning (no execution)
  - `INV` (Inventory) — View only; inventory visibility (no execution)
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
  PLN    → VIEW
  INV    → VIEW
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

## 3. Two-Dimension Status Model

**Added in v1.1 — Resolves authority contradiction found by [Status Model Direction Audit](../audit/status-model-direction-audit.md) — See [ADR-0001](../adr/ADR-0001-two-dimension-status-model.md)**

The system uses **two orthogonal dimensions** to describe an operation's state. These dimensions must never be conflated.

### 3.1 ExecutionLifecycleStatus (Dimension 1)

The execution lifecycle is event-derived, append-only, and authoritative. It answers: **"Where is this operation in the execution flow?"**

```
PLANNED ──[START]──▶ IN_PROGRESS ──[REPORT_QUANTITY]──▶ IN_PROGRESS
                          │
                   [COMPLETE] or [ABORT]
                          ▼
                   COMPLETED or ABORTED
```

| Status | Meaning | Event trigger |
|--------|---------|---------------|
| `PLANNED` | Operation exists but execution has not started. This is the initial state. | No events recorded |
| `IN_PROGRESS` | Operator has clocked on; work is active | `START` (OP_STARTED) event |
| `COMPLETED` | Operator has clocked off; work is finished | `COMPLETE` (OP_COMPLETED) event |
| `ABORTED` | Operation terminated before completion; will not resume | `ABORT` (OP_ABORTED) event |

**Rules:**
- Exactly 4 valid values. No other lifecycle states exist.
- `PENDING` is **NOT** an execution lifecycle state. The initial lifecycle state is `PLANNED`.
- `BLOCKED` is **NOT** an execution lifecycle state. It belongs to Dimension 2 (Readiness).
- `COMPLETED_LATE` and `LATE` are **WO-level derived display states**, not operation lifecycle values.
- Status is derived from the append-only `ExecutionEvent` log via `_derive_status()`. A cached `status` column on `Operation` is a materialized projection, not the source of truth.

### 3.2 Readiness / Dispatch Status (Dimension 2)

The readiness dimension answers: **"Is this operation eligible for dispatch / execution?"**

This dimension is **orthogonal** to execution lifecycle — an operation can be PLANNED (lifecycle) and BLOCKED (readiness) simultaneously.

| Status | Meaning | Implementation status |
|--------|---------|----------------------|
| `PENDING` | Released and queued; eligible for claim and execution | Currently expressed as station queue membership; not a separate column |
| `BLOCKED` | A constraint prevents execution eligibility (upstream delay, material shortage, hold) | Defined in spec; **not yet implemented in code** (no BLOCK/UNBLOCK events or API exist) |
| `HOLD` | Quality or material hold; requires approval to release | Future — approval engine can gate this |
| `READY` | All prerequisites met; actively dispatchable | Future — optional explicit readiness flag |

**Rules:**
- Readiness states are **NOT** part of `ExecutionLifecycleStatus`.
- Readiness does not affect `_derive_status()` computation.
- UI may display readiness information alongside lifecycle status (e.g., "Planned — Blocked: Material shortage").
- When BLOCK/UNBLOCK is implemented, it will be a change to readiness state, not an execution lifecycle transition.
- A `BLOCKED` operation in `IN_PROGRESS` lifecycle state means work was paused due to a constraint, but the execution lifecycle remains `IN_PROGRESS` — the block is a readiness overlay, not a lifecycle regression.

### 3.3 Mapping: How They Relate

| Lifecycle Status | Possible Readiness | Example scenario |
|------------------|--------------------|------------------|
| `PLANNED` | PENDING, BLOCKED, HOLD, READY | Operation created, waiting for dispatch |
| `IN_PROGRESS` | (active), BLOCKED | Work started; may be paused by constraint |
| `COMPLETED` | (n/a) | Work finished; readiness is irrelevant |
| `ABORTED` | (n/a) | Terminated; readiness is irrelevant |

### 3.4 Impact on Existing Code (Follow-Up)

The following items require **coordinated code changes in a follow-up PR** (not in this document update):

1. **DB default alignment:** `Operation.status` column default should be `PLANNED`, not `PENDING`
2. **Start guard fix:** `start_operation()` should check `PLANNED`, not `PENDING`
3. **Station queue filter:** Should filter by `PLANNED` (or a future readiness column), not `PENDING`
4. **Frontend mapper:** Should not map `PLANNED` → "Pending" — use canonical label "Planned"
5. **BLOCKED handling:** Remove phantom BLOCKED from execution mapper; move to readiness UI when implemented
6. **GanttChart:** Should use lifecycle status codes internally, not display-label strings

See [ADR-0001](../adr/ADR-0001-two-dimension-status-model.md) for the full implementation plan.

---

## 4. Execution Logic (Core MES Behavior)

### 4.1 Execution State Machine

An operation transitions through **execution lifecycle states** via execution events:

```
PLANNED
  ↓ (START / Clock On)
IN_PROGRESS
  ↓ (REPORT_QUANTITY)
IN_PROGRESS (multiple reports allowed)
  ├─ (COMPLETE / Clock Off) → COMPLETED
  └─ (ABORT) → ABORTED (terminal)
```

**Note on BLOCK/UNBLOCK:** These are **readiness constraint changes**, not execution lifecycle transitions. When implemented, a BLOCK event on an IN_PROGRESS operation would set a readiness flag but would NOT change the execution lifecycle status from IN_PROGRESS. See [§3.2](#32-readiness--dispatch-status-dimension-2). **Not yet implemented in code.**

### 4.2 Event Types & Semantics

#### Execution Lifecycle Events (implemented)

| Event Type | Precondition | Effect | Payload |
|---|---|---|---|
| **START** | lifecycle_status = PLANNED | actual_start = now, lifecycle_status → IN_PROGRESS | operator_id (optional) |
| **REPORT_QUANTITY** | lifecycle_status ∈ {IN_PROGRESS} | good_qty += amount, scrap_qty += amount | good_qty, scrap_qty (both ≥ 0) |
| **COMPLETE** | lifecycle_status = IN_PROGRESS | actual_end = now, lifecycle_status → COMPLETED | — |
| **ABORT** | lifecycle_status ∈ {PLANNED, IN_PROGRESS} | lifecycle_status → ABORTED (terminal; cannot resume) | abort_reason_code |

#### Readiness Constraint Events (not yet implemented)

| Event Type | Precondition | Effect | Payload | Implementation Status |
|---|---|---|---|---|
| **BLOCK** | lifecycle_status = IN_PROGRESS | readiness → BLOCKED (lifecycle stays IN_PROGRESS) | block_reason_code (required) | **Not implemented** |
| **UNBLOCK** | readiness = BLOCKED | readiness → cleared (lifecycle unchanged) | — | **Not implemented** |

When implemented, BLOCK/UNBLOCK will modify a readiness/constraint dimension, not the execution lifecycle status. See [§3 Two-Dimension Status Model](#3-two-dimension-status-model).

### 4.3 Execution Invariants

**What IS allowed:**

- Multiple REPORT_QUANTITY events for a single operation (partial completion)
- Quantity reported can exceed planned quantity (no over-production guard in Phase 6)
- COMPLETE after any number of REPORT_QUANTITY events
- ABORT from any non-terminal lifecycle state (PLANNED or IN_PROGRESS)

**What is explicitly FORBIDDEN:**

- START on non-PLANNED operation (idempotency: second START is rejected)
- COMPLETE on non-IN_PROGRESS operation
- Transition PLANNED → COMPLETED directly (must START first)
- Treating PENDING or BLOCKED as execution lifecycle states (they are readiness dimension)

### 4.4 Idempotency & Append-Only Guarantees

- **Append-Only Events:** New events are added; old events are never modified or deleted
- **Status Idempotency:** Computing status by replaying events always yields the same result
- **Duplicate Prevention:** The API layer (not documented here) prevents exact duplicate submissions within a short window
- **Event Ordering:** Events are timestamped and ordered by `created_at`; no out-of-order processing

---

## 5. Status Derivation Rules

Execution lifecycle status is not stored as source of truth; it is computed by inspecting execution events. The cached `status` column on `Operation` is a materialized projection.

### 5.1 Operation Execution Lifecycle Status

Derived by examining execution events in chronological order:

| Lifecycle Status | Condition | Rule |
|---|---|---|
| **PLANNED** | No START event | Operation has never been started |
| **IN_PROGRESS** | Latest relevant event is START or REPORT_QUANTITY (no COMPLETE/ABORT) | Operation is active |
| **COMPLETED** | Latest event is COMPLETE | Finished |
| **ABORTED** | Latest event is ABORT | Terminated; will not resume |

**Note:** `PENDING` and `BLOCKED` are NOT returned by `_derive_status()`. They belong to the readiness dimension (see [§3](#3-two-dimension-status-model)).

### 5.2 Work Order Derived Display Status

Aggregated from all child operation lifecycle statuses. These are **display states** for WO-level views:

| Display Status | Condition |
|---|---|
| **PLANNED** | All child operations are in PLANNED lifecycle state |
| **IN_PROGRESS** | At least one operation is IN_PROGRESS |
| **COMPLETED** | All child operations are COMPLETED or ABORTED AND at least one is COMPLETED |
| **COMPLETED_LATE** | All completed AND at least one actual_end > planned_end |
| **LATE** | WO not yet completed AND planned_end < now (forecasting indicator) |

**Note:** LATE and COMPLETED_LATE are WO-level derived display values, not part of the 4-state operation execution lifecycle.

### 5.3 Progress Calculation

- **Operation Progress (%):** `(completed_qty / quantity) × 100` where completed_qty = good_qty + scrap_qty
- **Work Order Progress (%):** Average of all child operation progress percentages
- **Timing Indicators:**
  - `delay_minutes` — Max(0, now - planned_end) if not yet completed
  - `cycle_time_minutes` — (actual_end - actual_start) if completed

---

## 6. Persona & UX Semantics (Phase 6B)

**Core Principle:** Persona determines **default landing page** and **menu scope**, not permissions. All authorization is backend-driven.

### 6.1 Persona Resolution

When a user logs in, their role_code is mapped to a Persona:

| Role Code → Persona | Landing Page | Primary Function |
|---|---|---|
| OPR → OPR | `/station` | Execute work at station |
| SUP → SUP | `/operations?lens=supervisor` | Monitor WO/OP; supervisor-focused KPIs |
| IEP → IEP | `/operations?lens=ie` | Process analysis; cycle time variance |
| QCI → QCI | `/operations?lens=qc` | Quality KPIs; defect tracking |
| PMG → PMG | `/dashboard` | Production metrics; KPI overview |
| EXE → EXE | `/dashboard` | Dashboard; read-only reporting |
| PLN → PMG | `/dashboard` | Planner; read-only dashboard view |
| INV → PMG | `/dashboard` | Inventory; read-only dashboard view |
| QAL → QCI | `/operations?lens=qc` | Map QAL (approval role) to QC persona |
| ADM, OTS → (multiple options) | (no default; free roam) | Admin access to all screens |

### 6.2 Menu Scope by Persona

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

### 6.3 Operation Lenses

The Global Operations screen shows different **analytical lenses** based on persona:

| Lens | Persona | Focus |
|---|---|---|
| **supervisor** | SUP, PMG | Blocked/delayed operations; WO status; overdue alerts |
| **ie** | IEP, PMG | Cycle time variance; repeat delays; high-variance operations |
| **qc** | QCI, QAL, PMG | QC failures; defect rates; scrap trends |

### 6.4 Persona is NOT Authorization

- A user with OPR persona **can still access** `/dashboard` if the backend permits (no frontend block)
- Persona is **suggestion only** for the default entry point
- Frontend does **not** check persona before calling APIs
- Backend may still return 403 if the user lacks the required permission
- Frontend respects 403 and shows "Access Denied" or redirects to default landing

---

## 7. Authorization & Governance Logic (Phase 6C)

### 7.1 Permission Families & Role Mapping

Every API endpoint that mutates or returns restricted data requires one of these permissions:

| Family | Granted To | Semantics |
|---|---|---|
| **VIEW** | OPR, SUP, IEP, QCI, QAL, PMG, EXE, PLN, INV, ADM, OTS | Read access to execution, status, KPIs |
| **EXECUTE** | OPR, SUP | Trigger execution lifecycle state changes (START, COMPLETE, REPORT, ABORT) |
| **APPROVE** | QAL, PMG | Create/decide approval requests |
| **CONFIGURE** | IEP | Modify parameters (standards, thresholds, process definitions) |
| **ADMIN** | ADM, OTS | System administration (user mgmt, role assignment, audit access) |

### 7.2 Permission Check Flow

1. **Request arrives at API**
2. **Decode JWT** → resolve user_id, tenant_id, role_code
3. **Look up UserRole** in database for (user_id, role_id, tenant_id)
4. **Look up RolePermission** for (role_id, required_permission_family)
5. **Check Scope** — User's tenant_id matches request tenant_id (or has wildcard)
6. **If impersonating:** Use acting_role_code's permission family directly (skip DB lookup)
7. **Decision:** 200 OK (permitted) or 403 Forbidden (denied)

### 7.3 Scope Model

All permissions are scoped:

- **Scope Type:** `tenant` (only implemented type in Phase 6)
- **Scope Value:** Tenant identifier or wildcard `*`
- **Tenant Isolation:** Repositories filter queries by `tenant_id`
- **Future Scopes:** Plant, Area, Line (not Phase 6)

### 7.4 Separation of Duties Principles

The system enforces several SOD rules:

| Rule | Enforcement | Purpose |
|---|---|---|
| Requester ≠ Approver | `decide_approval_request()` checks `decider_user_id ≠ requester_id` | Prevent self-approval |
| Role-Based Approval | `approval_rules` table defines per-action approver roles | No one can approve an action they're not authorized for |
| Immutable Audit Trail | `approval_audit_logs`, `impersonation_audit_logs` are append-only | Compliance: cannot hide who did what |
| Impersonation Does Not Bypass Approval | `require_approval` checks role, not impersonation status | Elevated users cannot skip review |

---

## 8. Impersonation (Temporary Elevation)

**Purpose:** Allow ADM/OTS to act as other roles for demo, training, or emergency fixes without permanently granting the role.

### 8.1 Who Can Impersonate (Impersonators)

Only these roles can create an impersonation session:

- `ADM` (Admin)
- `OTS` (On-the-Spot/Support)

Everyone else is forbidden; attempting to create a session will raise `PermissionError`.

### 8.2 Which Roles Can Be Acted As (Acting Roles)

Impersonators CANNOT act as:

- `ADM` (cannot impersonate admin)
- `OTS` (cannot impersonate support)

Attempting to impersonate ADM or OTS will raise `ValueError`.

Allowed acting roles:

- `OPR, SUP, IEP, QCI, QAL, PMG, EXE` (any operational role)

### 8.3 Time-Bound Sessions

- **Default Duration:** 60 minutes
- **Maximum Duration:** 480 minutes (8 hours)
- **Expiration Logic:** `expires_at = now() + duration_minutes`
- **Active Check:** Session is active if `revoked_at IS NULL AND expires_at > now()`
- **Expired sessions** are automatically ignored by `get_active_impersonation_session()`

### 8.4 Permission Resolution During Impersonation

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

### 8.5 Requester ≠ Approver Still Applies During Impersonation

**Key Rule:** Even if ADM is impersonating QAL and QAL can approve, ADM themselves CANNOT approve a request they created.

- Check uses REAL user_id (requester_id), not acting_role_code
- Prevents: ADM (impersonating QAL) creates a QC_HOLD request, then QAL-approves it
- Allows: ADM (impersonating QAL) approves someone else's QC_HOLD request

### 8.6 Audit Semantics

Every impersonation action is logged:

| Event | Logged | Purpose |
|---|---|---|
| **SESSION_CREATED** | user_id, acting_role_code, duration_minutes, reason | Who impersonated whom when, why |
| **SESSION_REVOKED** | session_id, revoked_at | When impersonation ended |
| **PERMISSION_USED** | session_id, permission_family, endpoint | What permissions were exercised during session |

Audit logs include REAL user_id (even when acting), so there is no ambiguity about who actually performed the action.

---

## 9. Approval Engine Logic

### 9.1 Action Types Requiring Approval

These actions trigger approval request workflows:

| Action Type | Typical Initiator | Default Approver Role |
|---|---|---|
| **QC_HOLD** | Operator / QC | QAL (QA Lead) |
| **QC_RELEASE** | QC / Operator | QAL |
| **SCRAP** | Operator / QC | QAL or PMG |
| **REWORK** | Operator | QAL |
| **WO_SPLIT** | Planner / Manager | PMG (Production Manager) |
| **WO_MERGE** | Planner / Manager | PMG |

### 9.2 Approval Request Lifecycle

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

### 9.3 Approval Rule Engine

- **approval_rules table** defines (action_type, approver_role_code) pairs
- **Multi-role rules:** Some actions have multiple valid approvers
  - Example: SCRAP can be approved by QAL *or* PMG
- **get_approver_role_codes()** returns the SET of authorized roles for an action
- At decision time, `decide_approval_request()` checks `decider_role_code IN approved_roles`

### 9.4 Relationship with RBAC

- **RBAC enforces** that approver has APPROVE permission
- **Approval rules enforce** that approver's role is listed for the action_type
- Both must be satisfied; neither alone is sufficient
- Example: PMG can APPROVE (RBAC) but cannot approve QC_HOLD (approval_rules)

### 9.5 Relationship with Impersonation

- **Approver role can be impersonated**
  - ADM (impersonating QAL) can approve QC_HOLD
- **Requester cannot be bypassed**
  - ADM (impersonating QAL) cannot approve their own request
  - `requester_id` is always real user_id, not acting role
- **Audit captures the session**
  - `decision.impersonation_session_id` records if decision was made under impersonation

---

## 10. Authentication & Login Flow

### 10.1 Users Table

Store persistent user identities:

- `user_id` — Unique identifier (assigned externally)
- `username` — Display name for login (unique per tenant)
- `email` — Optional contact
- `password_hash` — Argon2-hashed password
- `tenant_id` — Multi-tenant scope (default: "default")
- `is_active` — Whether login is allowed
- `created_at`, `updated_at` — Timestamps

### 10.2 Login Flow

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

### 10.3 JWT Semantics

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

### 10.4 RequireAuth Routing Guard

Frontend-side authentication guard (not authorization):

- Check `isAuthenticated` from AuthContext
- If false AND not initializing → Redirect to `/login`
- If true → Allow access to protected routes
- Login page auto-redirects authenticated users to "/" (or referrer)

### 10.5 401 Handling (Unauthorized)

- **Backend returns 401** when: Invalid token, expired token, missing Authorization header
- **Frontend handler:**
  - In httpClient, intercept 401 responses
  - Call `logout()` from AuthContext
  - Redirect to `/login`
  - Display "Session expired; please log in again"

---

## 11. Demo & Seed Data Semantics

### 11.1 Seed Scenarios (S1–S4)

Four predefined work-order scenarios that exercise core execution logic:

| Scenario | Description | Business Rule Validated |
|---|---|---|
| **S1: Normal Completion** | WO with 1 OP starts, quantities reported, completes on time | Normal path; status derivation; progress calculation |
| **S2: Completed Late** | WO with 1 OP completes after planned_end | Late detection; COMPLETED_LATE status |
| **S3: In Progress + Block** | WO with 2 OPs; one blocks, one in-progress | BLOCKED status; WO status aggregation; operator message |
| **S4: Repeat Variance** | Same operation repeats with different cycle times | Variance detection; delay frequency calculation |

### 11.2 Seed Users & Roles

Demo users created at init time for testing:

| Username | Password | Role | Purpose |
|---|---|---|---|
| admin | password123 | ADM | Test admin access |
| manager | password123 | PMG | Test approval & dashboard |
| supervisor | password123 | SUP | Test operation monitoring |
| operator | password123 | OPR | Test execution at station |
| qa | password123 | QAL | Test approval from QA perspective |

**Note:** Passwords are lowercase plain text for demo; production deployments must override via environment config or DB seeding.

### 11.3 Seed Data Purpose

- **NOT for realism:** Seed WOs may have unrealistic quantities, dates, etc.
- **FOR validation:** Each seed scenario validates one or two core business rules
- **Regression testing:** If a seed scenario fails, a core feature is broken

### 11.4 Seed Workflow

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

## 12. Explicit Non-Goals (Phase Boundary)

### 12.1 What Phase 6 Does NOT Include

The following features are **explicitly out of scope** and will not be implemented in Phase 6:

#### 12.1.1 Advanced Planning & Scheduling (APS)

- No constraint-based scheduling engine
- No resource leveling or capacity optimization
- No simulation or what-if analysis
- Phase 7+ scope

#### 12.1.2 Quality Control Workflow

- **No QC Inspection UI:** Operators cannot enter QC measurements or pass/fail decisions in Phase 6
- **No Sampling Logic:** No statistical sampling plans or AQL-based acceptance
- **No Disposition Workflow:** "Hold for QC" exists as an approval request, but QC release is manual approval only
- Phase 7+ scope

#### 12.1.3 Material & Backflush

- No BOM (Bill of Materials) explosion
- No material allocation or reservations
- No inventory integration
- No pick/pack workflows
- Phase 8+ scope

#### 12.1.4 External System Integration

- No EDI (orders from customers)
- No SAP / ERP integration
- No WMS (warehouse management)
- No MMS (maintenance management)
- Phase 8+ scope

#### 12.1.5 Advanced RBAC Features

- **No multi-role assignment per user per tenant** (Phase 6 limitation: 1 role per user-tenant)
- **No custom roles** (all roles are system-defined)
- **No attribute-based access control (ABAC)** (only role + scope)
- **No dynamic permission grants** (permissions are static per role)
- Phase 7+ scope

#### 12.1.6 Single Sign-On & Directory Services

- No LDAP integration
- No SAML 2.0 federation
- No OAuth 2.0 / OpenID Connect
- No API key authentication (humans only)
- Phase 7+ scope

#### 12.1.7 Real-Time Streaming

- No WebSocket push notifications
- No Apache Kafka event broker
- No message queues (RabbitMQ, etc.)
- API polling only
- Phase 8+ scope

#### 12.1.8 Microservices Architecture

- System is a **modular monolith**
- Single FastAPI backend, single PostgreSQL database
- No service decomposition, API gateway, circuit breakers
- Monolith must remain for Phases 6–7; Phase 8+ can consider extraction if high-load scenarios emerge

#### 12.1.9 Data Warehouse / Analytics Platform

- No analytical data mart
- No aggregated KPI storage
- No pre-computed dashboards (real-time queries only)
- Phase 7+ scope

#### 12.1.10 Mobile Application

- Web browser only; no mobile app (iOS/Android)
- Phase 7+ scope

### 12.2 Why These Are Excluded

These features require:

1. **Significant domain expertise** (QC sampling, APS algorithms) that is out of scope for MVP phase
2. **New integration surfaces** (ERP, MMS) that depend on partner system availability
3. **Infrastructure investment** (Kafka, data warehouse) that is premature before use-case validation
4. **Complex UX patterns** (multi-role selection, attribute matching) that need user research
5. **Regulatory expertise** (FDA 21 CFR, GxP) that is customer-specific

### 12.3 How to Request Phase 7+

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
| 1.1 | 2026-04-17 | MES Platform Team | Two-Dimension Status Model (§3); reframe PENDING/BLOCKED as readiness dimension; align with execution-lifecycle.md and copilot-instructions.md; see ADR-0001 |

---

**End of Document**
