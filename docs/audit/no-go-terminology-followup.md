# No-Go Terminology Follow-Up Audit

**Date:** 2026-04-17  
**Scope:** Option C — Two-Dimension Status Model code alignment  
**Branch:** `phase6b`  
**Result:** CRITICAL = 0

---

## Fixed CRITICALs

### C1 — Default status for PO/WO/Operation was `PENDING`
- **Files:** `backend/app/models/master.py`, `backend/scripts/seed/seed_station_execution_opr.py`, `backend/scripts/verify_clock_on.py`, `backend/scripts/verify_clock_off.py`
- **Fix:** Changed all defaults from `StatusEnum.pending.value` to `StatusEnum.planned.value`

### C2 — `start_operation` guard checked `PENDING`
- **File:** `backend/app/services/operation_service.py`
- **Fix:** Guard changed from `StatusEnum.pending.value` to `StatusEnum.planned.value`; error message updated to "Operation must be PLANNED to start."

### C3 — Station queue filter included `PENDING`
- **File:** `backend/app/services/station_claim_service.py`
- **Fix:** Queue filter changed from `[pending, in_progress]` to `[planned, in_progress]`; claim validation also updated

### C4 — Frontend used label-based status comparison
- **Files:** `frontend/src/app/pages/OperationExecutionOverview.tsx`, `frontend/src/app/api/mappers/executionMapper.ts`
- **Fix:** `mapTimelineStatusToGanttStatus()` rewritten from `mapExecutionStatusText(status) === "Completed"` to `status === "COMPLETED"`. Mapper removed PENDING/BLOCKED/LATE/COMPLETED_LATE cases — only 4 lifecycle statuses remain.

### C5 — GanttChart used display-string statuses
- **File:** `frontend/src/app/components/GanttChart.tsx`
- **Fix:** Status union changed from `'Not Started'|'Running'|'Completed'|'Delayed'|'Blocked'` to `'PLANNED'|'IN_PROGRESS'|'COMPLETED'|'ABORTED'`. All comparisons, legend, bar styles updated. "Delayed" is now a derived flag from `delayMinutes > 0`.

---

## Additional Fixes (discovered during verification)

### A1 — `StartOperationConflictError` returned 400 instead of 409
- **File:** `backend/app/api/v1/operations.py`
- **Fix:** Added explicit catch for `StartOperationConflictError` → HTTP 409, separate from generic `ValueError` → 400. Same fix applied for `CompleteOperationConflictError`.

### A2 — Station claim/queue verification scripts had stale claim state
- **Files:** `backend/scripts/verify_station_claim.py`, `backend/scripts/verify_station_queue_claim.py`
- **Fix:** Added claim cleanup (UPDATE `released_at`) before each test run. `verify_station_claim.py` now picks unclaimed operations from the queue.

### A3 — S3 scenario operator concurrency conflict
- **Files:** `backend/scripts/seed/common.py`, `backend/scripts/seed/scenario_s3_in_progress_block.py`
- **Fix:** `run_start`/`run_complete`/`run_abort` accept optional `operator_id` parameter; S3 uses unique operator IDs per operation.

### A4 — GanttStressTestPage used old status literals
- **File:** `frontend/src/app/pages/GanttStressTestPage.tsx`
- **Fix:** Updated from `'Not Started'|'Running'|'Completed'|'Delayed'` to `'PLANNED'|'IN_PROGRESS'|'COMPLETED'|'ABORTED'`.

---

## New Invariants

1. **Operation initial lifecycle status is `PLANNED`** — never `PENDING`
2. **`OperationExecutionStatus` is a strict union:** `"PLANNED" | "IN_PROGRESS" | "COMPLETED" | "ABORTED"` — no `string` fallback
3. **Frontend status comparisons are code-based** — never `mapExecutionStatusText(s) === "label"`
4. **GanttChart status values are backend codes** — not display strings
5. **`StartOperationConflictError` → HTTP 409** — not 400

---

## Remaining Debts (non-CRITICAL)

| Location | Usage | Classification | Reason |
|----------|-------|---------------|--------|
| `backend/app/models/master.py` | `StatusEnum.pending`, `StatusEnum.blocked` enum members | ENUM_DEFINITION | Members retained for DB compatibility; not used as lifecycle defaults |
| `backend/app/schemas/approval.py` | `ApprovalStatus = Literal["PENDING", ...]` | APPROVAL_DOMAIN | Approval workflow, not execution lifecycle |
| `backend/app/services/global_operation_service.py` | BLOCKED supervisor bucket | READINESS_DIMENSION | Supervisor lens display (S3 scenario); not lifecycle |
| `backend/app/services/dashboard_service.py` | `blocked_operations` count | READINESS_DIMENSION | Dashboard aggregate for blocked readiness |
| `frontend/src/app/pages/ProductionOrderList.tsx` | `PENDING` for PO status | PO_READINESS | PO-level readiness, not operation lifecycle |
| `frontend/src/app/pages/OperationList.tsx` | `'PENDING': 'Pending'` mapping | LEGACY_LIST_VIEW | Read-only list page; uses label-based patterns |
| `frontend/src/app/pages/Home.tsx` | Mock PO data with `Pending` | STATIC_MOCK | Demo page, no execution logic |
| `frontend/src/app/pages/OperationExecutionDetail.tsx` | `Pending` in QC checkpoints | QC_DOMAIN | QC checkpoint status, not execution lifecycle |
| `frontend/src/app/pages/Dashboard.tsx` | `pending_backend` text | UI_TEXT | Display label only |
| `frontend/src/app/pages/OEEDeepDive.tsx` | CSS variable `--status-pending` | CSS_THEMING | Visual styling only |

---

## Verification Gates

| Gate | Result |
|------|--------|
| Backend import + ruff lint | PASS |
| seed_all (S1–S4) | PASS 6/6 |
| verify_users_auth | PASS 9/9 |
| verify_approval | PASS 12/12 |
| verify_impersonation | PASS 13/13 |
| verify_station_claim | PASS 8/8 |
| verify_station_queue_claim | PASS 14/14 |
| verify_clock_on | PASS 5/5 |
| verify_clock_off | PASS 5/5 |
| Frontend `tsc --noEmit` | PASS (0 new errors; 2 pre-existing) |
| Frontend `npm run build` | PASS |
| i18n key parity (en ↔ ja) | PASS |
| No-Go audit CRITICAL count | **0** |
