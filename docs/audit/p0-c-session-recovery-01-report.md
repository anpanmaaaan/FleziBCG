# P0-C-SESSION-RECOVERY-01 — Station Session Open/Start Flow Report

| Field | Value |
|---|---|
| Task ID | P0-C-SESSION-RECOVERY-01B |
| Date | 2026-05-03 |
| Author | AI Agent (Hard Mode MOM v3) |
| Status | COMPLETE |

---

## Root Cause

After claim retirement (H08I-B/D), `StationExecution.tsx` required `owner_state === "mine" && has_open_session === true` to enter Mode B (execution cockpit). However, no UI existed to open a StationSession. The `StationSession` page was a non-functional shell with all buttons disabled. Operators had no path to reach Mode B and could not start operations.

---

## Changes Made

### Backend

**`backend/app/services/station_session_service.py`**
- Added spoofing guard in `open_station_session`: if `operator_user_id` is provided in payload and differs from `identity.user_id`, raises `PermissionError`
- Added auto-derive: if `operator_user_id` is None (not provided), defaults to `identity.user_id` (BT-AGG-002 / BT-CORE-001)
- Moved `_require_operator_eligible_for_station` call outside the if/else to always validate the derived operator

**`backend/tests/test_station_session_open_start_hardening.py`** — NEW
- 6 tests covering all required scenarios (T01–T06)

**`backend/tests/test_station_session_lifecycle.py`** — UPDATED
- Updated assertion in `test_open_station_session_happy_path_emits_candidate_event`: operator now auto-derived from identity, was `None`

### Frontend

**`frontend/src/app/api/stationApi.ts`**
- Added `openSession(payload)` and `closeSession(sessionId)` API methods
- Added `OpenStationSessionPayload` (without `operator_user_id`) and `StationSessionItem` interfaces
- Backend derives operator from authenticated user; frontend does not send it

**`frontend/src/app/pages/StationExecution.tsx`**
- Added session control card in Mode A (queue selection screen):
  - "Open Session" button when no active session exists
  - "Close Session" button when session is open and owned by current user
- Added `openStationSession()` and `closeStationSession()` handlers
- Added `sessionLoading` state
- `operator_user_id` removed from `openSession` call (backend derives from identity)

---

## Exact Endpoint Paths

| Operation | Method | Path | Backend File |
|---|---|---|---|
| Open session | POST | `/v1/station/sessions` | `api/v1/station_sessions.py` |
| Close session | POST | `/v1/station/sessions/{session_id}/close` | `api/v1/station_sessions.py` |
| Get queue (ownership projection) | GET | `/v1/station/queue` | `api/v1/station.py` |
| Get operation detail | GET | `/v1/station/queue/{operation_id}/detail` | `api/v1/station.py` |
| Start operation | POST | `/v1/operations/{operation_id}/start` | `api/v1/operations.py` |

Frontend calls verified to match backend routes.

---

## Operator Identity Derivation

| Scenario | Behavior |
|---|---|
| Frontend sends no `operator_user_id` | Backend sets `operator_user_id = identity.user_id` automatically |
| Frontend sends `operator_user_id == identity.user_id` | Allowed (matches) |
| Frontend sends `operator_user_id != identity.user_id` | `PermissionError` raised — spoofing rejected |

Backend derives operator from authenticated user. Frontend does not send `operator_user_id`. Server-side auth is authoritative (BT-CORE-001, BT-CORE-004).

---

## Test Results

### Backend Targeted Tests
```
tests/test_station_session_open_start_hardening.py  6 passed
tests/test_station_session_lifecycle.py             9 passed
```

### Backend Regression Sweep
```
136 passed, 539 deselected — 0 failures
```
Scope: `station_session, station_queue, start_pause, allowed_actions, close_operation, complete_operation, execution_route`

### Frontend
```
eslint src/       — no errors
vite build        — PASS
check:routes      — PASS 24, FAIL 0
```

---

## Deferred Gaps

### ~~P1 — Close session does not reject while execution is running~~ — RESOLVED in P0-C-SESSION-RECOVERY-02

This gap was resolved. See [P0-C-SESSION-RECOVERY-02 section below](#p0-c-session-recovery-02--close-station-session-active-execution-guard).

---

## P0-C-SESSION-RECOVERY-02 — Close Station Session Active Execution Guard

| Field | Value |
|---|---|
| Task ID | P0-C-SESSION-RECOVERY-02 |
| Date | 2026-05-03 |
| Author | AI Agent (Hard Mode MOM v3) |
| Status | COMPLETE |
| Design rule | SS-CLOSE-001 |
| Error type | `StationSessionConflictError` → HTTP 409 |

### Problem

`close_station_session` closed a station session unconditionally, even while operations were `IN_PROGRESS`, `PAUSED`, or `BLOCKED`. This orphaned execution work from its session context, violating SS-CLOSE-001 ("no active work would be orphaned; running/open work still owned by session").

### Changes Made

**`backend/app/repositories/operation_repository.py`**
- Added `get_active_non_terminal_operations_by_station(db, *, tenant_id, station_scope_value)` — returns open Operations with status ∈ {IN_PROGRESS, PAUSED, BLOCKED} and `closure_status = OPEN`
- Added `_CLOSE_SESSION_BLOCKER_STATUSES` constant documenting the invariant
- Active blocker states rationale: `IN_PROGRESS` = running; `PAUSED` = non-terminal, must be resumed/completed; `BLOCKED` = downtime open, must end first

**`backend/app/services/station_session_service.py`**
- Imported `get_active_non_terminal_operations_by_station` from operation_repository
- Added active execution guard in `close_station_session` before the close logic:
  - Queries active non-terminal operations for the session's station scope
  - If any found: raises `StationSessionConflictError("STATION_SESSION_ACTIVE_EXECUTION")`

**`backend/app/api/v1/station_sessions.py`**
- Added `StationSessionConflictError` handler to `close_station_session_route` → HTTP 409

**`backend/tests/test_station_session_close_execution_guard.py`** — NEW
- 7 tests (T01–T07) covering: IN_PROGRESS rejection, PAUSED rejection, clean close, close after complete, scope guard preserved, downtime resolved, regression for start guard

**`backend/tests/test_station_session_open_start_hardening.py`** — UPDATED
- T06 updated from gap documentation to active assertion: now expects `StationSessionConflictError` (guard is enforced)

**`frontend/src/app/pages/StationExecution.tsx`**
- `closeStationSession` handler now detects `HttpError` with `status === 409` and shows a specific user-facing message

**`frontend/src/app/i18n/registry/en.ts`** + `ja.ts`
- Added `station.session.closeBlockedActiveExecution` key with user-facing message

### Test Results

```
tests/test_station_session_close_execution_guard.py   7 passed
tests/test_station_session_open_start_hardening.py    6 passed (T06 now asserts rejection)
tests/test_station_session_lifecycle.py               9 passed
tests/test_start_pause_resume_command_hardening.py   12 passed
tests/test_operation_detail_allowed_actions.py       23 passed
```

### Definition of Done Verification

| Criterion | Status |
|---|---|
| Close rejected when IN_PROGRESS operation exists | ✓ (T01 passes) |
| Close rejected when PAUSED operation exists | ✓ (T02 passes) |
| Close succeeds when no active execution | ✓ (T03 passes) |
| Close succeeds after operation completed | ✓ (T04 passes) |
| Wrong scope guard still fires before execution check | ✓ (T05 passes) |
| Error is 409 Conflict, not 400/500 | ✓ (StationSessionConflictError → 409) |
| Frontend shows specific message for 409 | ✓ |
| No regressions in existing session/operation tests | ✓ (50/50) |
| Frontend lint and build clean | ✓ |



## Definition of Done Verification

| Criterion | Status |
|---|---|
| Operator can open Mode A and open a station session | ✓ |
| Backend owns operator/session authorization | ✓ |
| Start operation works after valid session open | ✓ (T04 passes) |
| Wrong scope rejected | ✓ (T02 passes) |
| Operator spoofing rejected | ✓ (T03 passes) |
| Frontend does not fake permissions | ✓ (`allowed_actions` from backend) |
| Required tests pass | ✓ (6/6) |
| i18n/route/build checks pass | ✓ |
