# Status Model Direction Audit

**Date:** 2025-01-XX  
**Scope:** Read-only audit — NO code changes  
**Branch:** `phase6b`  
**Purpose:** Determine whether the codebase follows Direction A (single-dimension lifecycle with PENDING/BLOCKED as states) or Direction B (two-dimension model where execution lifecycle is PLANNED→IN_PROGRESS→COMPLETED|ABORTED and PENDING/BLOCKED are separate dimensions)  
**Verdict:** ⚠️ **HYBRID — Direction B in derivation logic, Direction A remnants in guards/DB/queue**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Status Inventory](#2-status-inventory)
3. [Execution Lifecycle Derivation](#3-execution-lifecycle-derivation)
4. [Execution Guards](#4-execution-guards)
5. [Station Queue Semantics](#5-station-queue-semantics)
6. [Frontend Status Usage](#6-frontend-status-usage)
7. [Authority Document Comparison](#7-authority-document-comparison)
8. [Gap / Conflict Report](#8-gap--conflict-report)
9. [Direction Verdict](#9-direction-verdict)
10. [Recommendations (No Code Changes)](#10-recommendations-no-code-changes)

---

## 1. Executive Summary

The codebase is a **conflicted hybrid**. The core execution derivation logic (`_derive_status()`) implements a clean **Direction B** 4-state lifecycle: `PLANNED → IN_PROGRESS → COMPLETED | ABORTED`. However, the DB defaults, execution guards, station queue filters, and seed data still use `PENDING` — a Direction A artifact. `BLOCKED` exists in the enum but has **zero write paths** in the entire codebase.

This creates a silent correctness bug: `_derive_status()` returns `PLANNED` for operations with no events, but `start_operation()` checks for `PENDING`, and station queue filters query for `PENDING`. These values never match the derived status, meaning the **start guard and queue filter rely on the stale DB-default column value, not the derived status**.

The two authority documents contradict each other:
- `docs/system/mes-business-logic-v1.md` defines a 6-state model with PENDING/BLOCKED (Direction A)
- `.github/copilot-instructions.md` defines a 4-state model explicitly forbidding PENDING/BLOCKED (Direction B)

---

## 2. Status Inventory

### 2.1 Backend StatusEnum (`app/models/master.py`)

| Value | In `_derive_status()`? | Has write path? | Role |
|-------|----------------------|-----------------|------|
| `PLANNED` | ✅ (initial state) | No explicit setter — returned by derivation | Execution lifecycle |
| `PENDING` | ❌ | DB default only | Legacy / Direction A remnant |
| `IN_PROGRESS` | ✅ | Via `_derive_status()` on OP_STARTED event | Execution lifecycle |
| `COMPLETED` | ✅ | Via `_derive_status()` on OP_COMPLETED event | Execution lifecycle (terminal) |
| `COMPLETED_LATE` | ❌ (operation level) | Via `_derive_work_order_status()` only | WO-level display |
| `ABORTED` | ✅ | Via `_derive_status()` on OP_ABORTED event | Execution lifecycle (terminal) |
| `BLOCKED` | ❌ | **None — no API, service, or event exists** | Dead enum member |
| `LATE` | ❌ | Via `_derive_work_order_status()` only | WO-level display |

**EDGE comment in code (L12-13):** _"Enum includes display-only values (PENDING, BLOCKED, LATE, COMPLETED_LATE) that are NOT part of the execution state machine (PLANNED→IN_PROGRESS→COMPLETED|ABORTED). They exist for PO/WO-level status columns and legacy seed data."_

### 2.2 ExecutionEventType (`app/models/execution.py`)

| Event | Exists in code? | Exists in `mes-business-logic-v1.md`? |
|-------|----------------|--------------------------------------|
| `OP_STARTED` | ✅ | ✅ (as `START`) |
| `QTY_REPORTED` | ✅ | ✅ (as `REPORT_QUANTITY`) |
| `NG_REPORTED` | ✅ | ❌ |
| `QC_MEASURE_RECORDED` | ✅ | ❌ |
| `OP_COMPLETED` | ✅ | ✅ (as `COMPLETE`) |
| `OP_ABORTED` | ✅ | ✅ (as `ABORT`) |
| `BLOCK` | ❌ | ✅ |
| `UNBLOCK` | ❌ | ✅ |

### 2.3 DB Column Defaults

| Model | Column | Default | Derived initial state |
|-------|--------|---------|-----------------------|
| `ProductionOrder` | `status` | `StatusEnum.pending.value` ("PENDING") | N/A (no derivation function) |
| `WorkOrder` | `status` | `StatusEnum.pending.value` ("PENDING") | `PLANNED` (from `_derive_work_order_status`) |
| `Operation` | `status` | `StatusEnum.pending.value` ("PENDING") | `PLANNED` (from `_derive_status`) |

**Mismatch:** DB inserts operations with `status = "PENDING"`, but the derivation function returns `"PLANNED"` for the same state (no events).

---

## 3. Execution Lifecycle Derivation

### 3.1 `_derive_status()` — `app/services/operation_service.py` L55-64

```python
def _derive_status(events):
    if not events:
        return StatusEnum.planned.value      # "PLANNED"
    types = {e.event_type for e in events}
    if ExecutionEventType.OP_ABORTED in types:
        return StatusEnum.aborted.value      # "ABORTED"
    if ExecutionEventType.OP_COMPLETED in types:
        return StatusEnum.completed.value    # "COMPLETED"
    if ExecutionEventType.OP_STARTED in types:
        return StatusEnum.in_progress.value  # "IN_PROGRESS"
    return StatusEnum.planned.value          # "PLANNED"
```

**Returns exactly 4 values:** `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `ABORTED`

**Never returns:** `PENDING`, `BLOCKED`, `LATE`, `COMPLETED_LATE`

**Comment at L62-63:** _"Current model intentionally converges PLANNED as execution-pending state. UI mapping is responsible for rendering this as Pending/Ready for operators."_

### 3.2 `_derive_work_order_status()` — `app/services/work_order_execution_service.py`

Returns 5 values: `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `COMPLETED_LATE`, `LATE`

**Never returns:** `PENDING`, `BLOCKED`

### 3.3 State Diagram (as implemented in code)

```
PLANNED ──[OP_STARTED]──▶ IN_PROGRESS ──[QTY_REPORTED]──▶ IN_PROGRESS
                                │
                     [OP_COMPLETED] or [OP_ABORTED]
                                ▼
                       COMPLETED or ABORTED
```

No BLOCK/UNBLOCK transitions exist. No path leads to BLOCKED or PENDING.

---

## 4. Execution Guards

### 4.1 `start_operation()` — L128

```python
if operation.status != StatusEnum.pending.value:
    raise StartOperationConflictError(...)
```

**Guard checks for `PENDING`**, but `_derive_status()` returns `PLANNED` for the same logical state.

**Why this works today:** The guard reads `operation.status` from the **DB column** (which defaults to `"PENDING"`), not the derived status. The column is only updated after the first event. So the guard relies on the stale DB-default value, not the event-derived state. This is **fragile** — if the status column is ever refreshed to the derived value before start, the guard breaks.

### 4.2 `report_quantity()` — L165

```python
if operation.status != StatusEnum.in_progress.value:
    raise ...
```

Correct — `IN_PROGRESS` is both the derived state and the DB-updated value.

### 4.3 `complete_operation()` — L205

```python
if operation.status != StatusEnum.in_progress.value:
    if operation.status == StatusEnum.completed.value:
        # Already completed — idempotent
    else:
        raise ...
```

Correct — checks `IN_PROGRESS` with `COMPLETED` special case.

### 4.4 `abort_operation()` — L250

```python
terminal_statuses = [StatusEnum.completed.value, StatusEnum.aborted.value]
if operation.status in terminal_statuses:
    raise ...
```

Allows abort from any non-terminal state. Works with both `PENDING` and `PLANNED`.

---

## 5. Station Queue Semantics

### 5.1 Queue Filter — `app/services/station_claim_service.py` L206-215

```python
Operation.status.in_([
    StatusEnum.pending.value,     # "PENDING"
    StatusEnum.in_progress.value  # "IN_PROGRESS"
])
```

Queries for `PENDING` + `IN_PROGRESS`. Since DB-default is `"PENDING"`, this works for new operations. But if the status column were refreshed to `"PLANNED"` (the derived value), operations would disappear from the queue.

### 5.2 Claim Validation

Checks that the operation status is `PENDING` or `IN_PROGRESS` before allowing claim. Claiming does **NOT** change `operation.status` — only creates an `OperationClaim` row.

### 5.3 BLOCK/UNBLOCK

**No BLOCK/UNBLOCK endpoint** exists in `app/api/v1/station.py` or `app/api/v1/operations.py`.  
**No `block_operation()` or `unblock_operation()`** function exists in any service.

---

## 6. Frontend Status Usage

### 6.1 Central Mapper — `executionMapper.ts`

| Backend status | Display text | Badge variant |
|---------------|-------------|--------------|
| `PLANNED` | "Pending" | `neutral` |
| `PENDING` | "Pending" | `neutral` |
| `IN_PROGRESS` | "In Progress" | `info` |
| `COMPLETED` | "Completed" | `success` |
| `COMPLETED_LATE` | "Completed Late" | `warning` |
| `ABORTED` | "Aborted" | `danger` |
| `BLOCKED` | "Blocked" | `danger` |
| `LATE` | "Delayed" | `warning` |

Both `PLANNED` and `PENDING` map to the same display text — the UI cannot distinguish them.

### 6.2 GanttChart Status Model (completely independent)

The GanttChart uses its own display-label status type:

```typescript
status: 'Not Started' | 'Running' | 'Completed' | 'Delayed' | 'Blocked'
```

`OperationExecutionOverview.tsx` bridges the gap via `mapTimelineStatusToGanttStatus()`, which:
1. Calls `mapExecutionStatusText()` to get display text
2. Compares the display text to string literals: `"Completed"`, `"In Progress"`
3. Maps to Gantt labels: `"Completed"`, `"Running"`, default `"Not Started"`

**Fragility:** Any change to `mapExecutionStatusText()` output silently misclassifies operations.

### 6.3 Frontend Comparisons to Backend Enum Codes (safe)

| File | Comparison | Context |
|------|-----------|---------|
| `GlobalOperationList.tsx` | `=== "BLOCKED"`, `"LATE"`, `"IN_PROGRESS"` | Supervisor bucket derivation |
| `StationExecution.tsx` | `=== "PENDING" \|\| === "PLANNED"` | Clock-on gate (defensive) |
| `StationExecution.tsx` | `=== "COMPLETED"`, `"ABORTED"`, `"IN_PROGRESS"` | UI section gating |
| `OperationExecutionOverview.tsx` | `=== "IN_PROGRESS"` | Running timer |
| `ProductionOrderList.tsx` | `=== 'COMPLETED'`, `'IN_PROGRESS'`, `'LATE'` | Badge styling |

### 6.4 Frontend Comparisons to Display Labels (fragile)

| File | Comparison | Risk |
|------|-----------|------|
| `OperationExecutionOverview.tsx` | `statusText === "Completed"`, `"In Progress"` | **HIGH** — breaks if mapper output changes |
| `OperationExecutionOverview.tsx` | `op.status === "Completed"`, `"Running"` | **HIGH** — Gantt display labels |
| `GanttChart.tsx` | `op.status === 'Not Started'`, `'Running'`, `'Blocked'` etc. | **HIGH** — own label system |
| `OperationExecutionDetail.tsx` | `c.status === "Passed"`, `"Pending"` | LOW — QC mock data |
| `OperationList.tsx` | Filter dropdown uses display labels as `<option value>` | **MEDIUM** — coupling to English text |

### 6.5 Filter Dropdowns

| Page | Filter values | Value type | Dead options |
|------|--------------|-----------|-------------|
| `GlobalOperationList.tsx` | PLANNED, IN_PROGRESS, COMPLETED, COMPLETED_LATE, BLOCKED, DELAYED, PENDING | Backend enums | `PENDING` (dead — never returned by API) |
| `OperationList.tsx` | Pending, In Progress, Late, Completed, etc. | Display labels | — |
| `ProductionOrderList.tsx` | PENDING, IN_PROGRESS, COMPLETED, LATE | Backend enums | — |

### 6.6 Status Type Definitions

| File | Type | Values |
|------|------|--------|
| `operationApi.ts` | `OperationExecutionStatus` | `"PENDING" \| "IN_PROGRESS" \| "COMPLETED" \| string` |
| `GanttChart.tsx` | `OperationExecutionGantt['status']` | `'Not Started' \| 'Running' \| 'Completed' \| 'Delayed' \| 'Blocked'` |
| `OperationList.tsx` | `WorkOrderExecution['status']` | `'Pending' \| 'In Progress' \| 'Completed' \| ...` |
| `database.ts` | `Operation['status']` | `'Pending' \| 'In Progress' \| 'Completed' \| 'Blocked' \| 'Skipped'` |

`OperationExecutionStatus` is the only type using backend enum codes — all others use display labels. The `| string` escape hatch makes it effectively untyped.

---

## 7. Authority Document Comparison

| Aspect | `mes-business-logic-v1.md` | `copilot-instructions.md` | **Code Reality** |
|--------|---------------------------|---------------------------|-----------------|
| **Initial state** | `PENDING` | `PLANNED` | DB default = `PENDING`; `_derive_status()` returns `PLANNED` |
| **Valid states** | PENDING, IN_PROGRESS, BLOCKED, COMPLETED, COMPLETED_LATE, ABORTED | PLANNED, IN_PROGRESS, COMPLETED, ABORTED | Derivation: PLANNED, IN_PROGRESS, COMPLETED, ABORTED. DB/guards: PENDING also used |
| **PENDING** | ✅ Initial state | ❌ "does NOT exist" | DB default; used in guards; not in derivation |
| **BLOCKED** | ✅ Intermediate state | ❌ "does NOT exist" | Enum member with **zero write paths** |
| **BLOCK event** | ✅ Defined | ❌ Not mentioned | **Does not exist** in code |
| **UNBLOCK event** | ✅ Defined | ❌ Not mentioned | **Does not exist** in code |
| **COMPLETED_LATE** | ✅ Terminal state | ❌ Not mentioned | WO-level only, not operation derivation |
| **LATE** | ❌ (WO state only) | ❌ Not mentioned | WO-level only |
| **Abort sources** | PENDING, IN_PROGRESS, BLOCKED | IN_PROGRESS (diagram implies) | Any non-terminal state |
| **Event types** | START, REPORT_QUANTITY, COMPLETE, BLOCK, UNBLOCK, ABORT | start, report_qty, complete, abort | OP_STARTED, QTY_REPORTED, NG_REPORTED, QC_MEASURE_RECORDED, OP_COMPLETED, OP_ABORTED |

### Which doc does the code follow?

The **derivation logic** (`_derive_status`) aligns with `copilot-instructions.md`:
- 4-state model: PLANNED → IN_PROGRESS → COMPLETED | ABORTED
- No BLOCK/UNBLOCK transitions
- No PENDING in the lifecycle

The **DB defaults and guards** align with `mes-business-logic-v1.md`:
- Initial column value is PENDING
- start_operation checks for PENDING
- Station queue filters for PENDING

The **API surface** aligns with `copilot-instructions.md`:
- No BLOCK/UNBLOCK endpoints
- 4 execution actions only (start, report, complete, abort)

---

## 8. Gap / Conflict Report

### 8.1 CRITICAL Conflicts

| # | Conflict | Location | Impact |
|---|---------|----------|--------|
| C1 | **PENDING vs PLANNED mismatch** — DB inserts `PENDING`, derivation returns `PLANNED`. Start guard checks `PENDING` (the stale DB value). | `operation_service.py` L128, `master.py` L139 | Start guard works **by accident** — relies on reading stale column, not derived status. If status column is ever refreshed before first event, start breaks. |
| C2 | **Station queue filters PENDING** — queue includes operations with `status = "PENDING"`, but if derivation refreshes the column to `"PLANNED"`, operations vanish from queue. | `station_claim_service.py` L206-215 | Same fragility as C1. |
| C3 | **Authority doc contradiction** — `mes-business-logic-v1.md` defines PENDING/BLOCKED as lifecycle states with BLOCK/UNBLOCK events. `copilot-instructions.md` explicitly forbids them. Both claim to be "LOCKED." | `docs/system/mes-business-logic-v1.md` §3-4, `.github/copilot-instructions.md` | Cannot determine canonical truth from docs alone. Code follows copilot-instructions direction but with PENDING remnants. |
| C4 | **`SOURCE_STRUCTURE.md` describes block endpoint** — references "block" in operation routes/services, but no such function or endpoint exists in code. | `.github/agent/SOURCE_STRUCTURE.md` | Misleading to AI agents and contributors. |

### 8.2 MAJOR Conflicts

| # | Conflict | Location | Impact |
|---|---------|----------|--------|
| M1 | **BLOCKED enum member has no write path** — exists in `StatusEnum` and is handled in `executionMapper.ts`, `global_operation_service.py` (supervisor bucket), but cannot be set via any API, service, or event. | `master.py` L8, `global_operation_service.py` L105 | Dead code / phantom state. FE shows "Blocked" badge variant but no operation can reach this state. |
| M2 | **`mapTimelineStatusToGanttStatus()` compares display text** — bridges backend status to Gantt by comparing `mapExecutionStatusText()` output to English string literals. | `OperationExecutionOverview.tsx` L63-73 | Any i18n translation of status text will silently break Gantt classification. |
| M3 | **GanttChart status type is independent** — uses `'Not Started' \| 'Running' \| 'Completed' \| 'Delayed' \| 'Blocked'`, unrelated to backend enums. ~20 comparison sites use these labels. | `GanttChart.tsx` L17 | Refactoring requires touching every comparison site. "Blocked" can never appear (no write path). |
| M4 | **`OperationExecutionStatus` loosely typed** — `"PENDING" \| "IN_PROGRESS" \| "COMPLETED" \| string` is effectively `string`. Declares `PENDING` but not `PLANNED` or `ABORTED`. | `operationApi.ts` L3 | No compile-time safety for status comparisons. |
| M5 | **GlobalOperationList filter includes PENDING** — `<option value="PENDING">` appears in the status filter dropdown, but API never returns operations with `status = "PENDING"` (they're `"PLANNED"` after derivation, or `"PENDING"` only if column was never refreshed). | `GlobalOperationList.tsx` L513 | Filter may or may not work depending on whether the cached column was refreshed. |

### 8.3 MINOR Conflicts

| # | Conflict | Location | Impact |
|---|---------|----------|--------|
| m1 | **`OperationList.tsx` duplicates mapper** — has its own `mapBackendStatus()` with fallback `?? 'Pending'`, redundant with `executionMapper.ts`. | `OperationList.tsx` L94-105 | Drift risk — two mappers may diverge. |
| m2 | **`database.ts` defines stale types** — `Operation.status = 'Pending' \| 'In Progress' \| 'Completed' \| 'Blocked' \| 'Skipped'` includes `Skipped` which doesn't exist anywhere. | `database.ts` L39 | Legacy/unused types may mislead. |
| m3 | **StationExecution defensively checks both** — `operation?.status === "PENDING" || operation?.status === "PLANNED"` hedges both values. | `StationExecution.tsx` L243 | Works but evidences the underlying confusion. |

---

## 9. Direction Verdict

### Evidence Summary

| Evidence | Points to |
|----------|-----------|
| `_derive_status()` returns PLANNED/IN_PROGRESS/COMPLETED/ABORTED only | **Direction B** |
| `_derive_work_order_status()` returns PLANNED-based states, no PENDING | **Direction B** |
| No BLOCK/UNBLOCK event types in `ExecutionEventType` | **Direction B** |
| No BLOCK/UNBLOCK endpoints in any API router | **Direction B** |
| No `block_operation()` / `unblock_operation()` service functions | **Direction B** |
| EDGE comment on StatusEnum declares PENDING/BLOCKED as "NOT part of execution state machine" | **Direction B** |
| `copilot-instructions.md` explicitly forbids PENDING and BLOCKED | **Direction B** |
| DB default for Operation.status is `PENDING` | Direction A remnant |
| `start_operation()` guard checks `PENDING` | Direction A remnant |
| Station queue filters by `PENDING` | Direction A remnant |
| `mes-business-logic-v1.md` defines PENDING + BLOCKED + BLOCK/UNBLOCK | Direction A spec |
| `SOURCE_STRUCTURE.md` references "block" in routes/services | Direction A spec |
| Seed data creates operations with `status = "PENDING"` | Direction A data |

### Verdict

**The codebase implements Direction B in its core execution logic**, with **Direction A remnants in the data layer and guards**.

- **Derivation (source of truth):** 4-state Direction B lifecycle. Clean, consistent, tested.
- **DB/guards/queue (stale layer):** Still use `PENDING` from Direction A. Work only because the cached column retains the DB-default `PENDING` value until the first event write.
- **BLOCKED:** Dead across the entire codebase. No write path exists. It is specified in `mes-business-logic-v1.md` but was never implemented.
- **COMPLETED_LATE / LATE:** Legitimately used at WO level as derived display states. Not part of the operation execution lifecycle.

The system works today because the status column is a stale cache that is only refreshed when events are written — so new operations keep `PENDING` in the column until `start_operation()` writes an event and refreshes it to `IN_PROGRESS`. This is a **coincidental correctness** pattern, not a deliberate two-layer design.

---

## 10. Recommendations (No Code Changes)

This section proposes remediation categories. **No code changes are made in this audit.**

### R1. Resolve Authority Document Contradiction (PREREQUISITE)

Before any code changes, the project must decide which document is authoritative:
- **Option A:** Update `copilot-instructions.md` to align with `mes-business-logic-v1.md` → implement BLOCK/UNBLOCK, change derivation initial state to PENDING
- **Option B:** Update `mes-business-logic-v1.md` to align with `copilot-instructions.md` → remove PENDING/BLOCKED/BLOCK/UNBLOCK from spec, formalize PLANNED as initial state
- **Option C:** Formalize the two-dimension model — lifecycle (PLANNED/IN_PROGRESS/COMPLETED/ABORTED) is one axis; blocking/scheduling flags are a separate dimension (not status enum values)

### R2. Align DB Defaults with Derivation

Change `Operation.status` default from `PENDING` to `PLANNED` (or whatever initial state is decided in R1). Same for PO/WO if applicable.

### R3. Fix Execution Guards

`start_operation()` should check `StatusEnum.planned.value` instead of `StatusEnum.pending.value` — or check both during migration.

### R4. Fix Station Queue Filter

Station queue should filter by `PLANNED` instead of (or in addition to) `PENDING`.

### R5. Clean Up Dead Enum Members

If Direction B is ratified, remove `BLOCKED` from `StatusEnum` (or mark it reserved for future use). Remove phantom BLOCKED handling from `global_operation_service.py` and `executionMapper.ts`.

### R6. Fix Frontend Status Fragility

- `mapTimelineStatusToGanttStatus()` must compare backend enum codes, not display text
- GanttChart should use backend enum codes internally, map to display labels only at render time
- `OperationExecutionStatus` type should be a strict union matching backend values
- Remove duplicate `mapBackendStatus()` in `OperationList.tsx`

### R7. Update SOURCE_STRUCTURE.md

Remove "block" references from operation routes/services descriptions since no such functionality exists in code.

---

## Appendix A — Files Audited

### Backend

| File | Lines | What was checked |
|------|-------|-----------------|
| `app/models/master.py` | 1-200 | StatusEnum, PO/WO/Operation model defaults |
| `app/models/execution.py` | 1-100 | ExecutionEventType members |
| `app/services/operation_service.py` | 1-300 | `_derive_status()`, all 4 execution guards |
| `app/services/work_order_execution_service.py` | 1-100 | `_derive_work_order_status()` |
| `app/services/global_operation_service.py` | 1-250 | `_derive_supervisor_bucket()`, delay calculation |
| `app/services/station_claim_service.py` | 1-250 | Queue filter, claim validation |
| `app/api/v1/operations.py` | Full | Endpoint inventory (no BLOCK/UNBLOCK) |
| `app/api/v1/station.py` | Full | Endpoint inventory (no BLOCK/UNBLOCK) |
| `app/repositories/operation_repository.py` | Full | Status filter queries |

### Frontend

| File | What was checked |
|------|-----------------|
| `src/app/api/operationApi.ts` | `OperationExecutionStatus` type |
| `src/app/api/mappers/executionMapper.ts` | `mapExecutionStatusText()`, `mapExecutionStatusBadgeVariant()` |
| `src/app/components/GanttChart.tsx` | Status type union, ~20 comparison sites |
| `src/app/pages/GlobalOperationList.tsx` | Supervisor bucket derivation, filter dropdowns |
| `src/app/pages/StationExecution.tsx` | Clock-on gate, section gating |
| `src/app/pages/OperationExecutionOverview.tsx` | `mapTimelineStatusToGanttStatus()`, stats counts |
| `src/app/pages/OperationExecutionDetail.tsx` | QC checkpoint / material status |
| `src/app/pages/OperationList.tsx` | `mapBackendStatus()`, filter dropdown |
| `src/app/pages/ProductionOrderList.tsx` | Status badge styling, filter |
| `src/app/pages/Home.tsx` | Mock status types |
| `src/types/database.ts` | Legacy status type definitions |

### Authority Documents

| Document | What was checked |
|----------|-----------------|
| `docs/system/mes-business-logic-v1.md` | §3-4: State machine, events, status derivation |
| `.github/copilot-instructions.md` | Execution Flow (LOCKED) section |
| `.github/agent/CODING_RULES.md` | Governance constraints |
| `.github/agent/SOURCE_STRUCTURE.md` | Route/service descriptions |
| `docs/architecture/EXECUTION_MODEL.md` | High-level execution principles |

---

**⚠️ DO NOT modify code based on this audit. Resolve the authority document contradiction (R1) first, then apply code changes in a coordinated PR.**

---

## Appendix B — Resolution

The authority document contradiction (R1) was resolved on 2026-04-17 via **Option C: Two-Dimension Status Model**.

- **ADR:** [ADR-0001-two-dimension-status-model.md](../adr/ADR-0001-two-dimension-status-model.md)
- **Updated spec:** [mes-business-logic-v1.md §3](../system/mes-business-logic-v1.md) (v1.1)
- **Updated guardrails:** [copilot-instructions.md](../../.github/copilot-instructions.md)
- **Terminology guide:** [docs/mom/no-go-terminology.md](../mom/no-go-terminology.md)

Code changes (R2–R7) remain pending for a follow-up coordinated PR — see ADR-0001 Follow-Up Implementation Plan.
