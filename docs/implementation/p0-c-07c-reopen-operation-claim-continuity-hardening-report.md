# P0-C-07C Reopen Operation / Claim Continuity Hardening Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: Strict
- Hard Mode MOM: v3
- Reason: Harden `reopen_operation` command guards and claim-continuity compatibility behavior
  while preserving StationSession diagnostic non-blocking behavior and claim deprecation lock.

## Slice Outcome

Status: COMPLETE

Classification: Tests-only hardening slice

Production code changed: No

## Scope Implemented

- Added focused hardening test suite:
  - `backend/tests/test_reopen_operation_claim_continuity_hardening.py`
- Verified reopen state legality:
  - happy path from CLOSED completed operation
  - rejects non-CLOSED (OPEN) operation with `STATE_NOT_CLOSED`
  - rejects PAUSED non-closed operation with `STATE_NOT_CLOSED`
- Verified reason requirement:
  - blank reason → `REOPEN_REASON_REQUIRED`
  - None reason → Pydantic `ValidationError` (schema-level guard)
- Verified tenant mismatch rejection:
  - `ValueError("Operation does not belong to the requesting tenant.")`
- Verified emitted reopen event:
  - `ExecutionEventType.OPERATION_REOPENED` = `"operation_reopened"`
  - event payload contains `actor_user_id`, `reason`, `reopened_at`
- Verified closure_status transition:
  - `closure_status: CLOSED → OPEN`
- Verified projection/detail after reopen:
  - `status = PAUSED` (OPERATION_REOPENED as last_runtime_event + has_completed=True)
  - `closure_status = OPEN`
  - backend-derived: re-derived and confirmed consistent
- Verified backend-derived allowed_actions after reopen:
  - `["resume_execution", "start_downtime"]`
  - `reopen_operation` and `close_operation` absent
- Re-verified StationSession diagnostic remains non-blocking:
  - T10: missing session path — reopen succeeds unchanged
  - T11: matching OPEN session path — reopen outcome identical
- Verified reopen_count increments on first reopen
- Re-verified claim compatibility and reopen/close regression baseline unchanged

## Behavior Contract Confirmed

- No StationSession enforcement in P0-C-07C.
- Missing StationSession does not reject `reopen_operation` in current source.
- Matching OPEN StationSession does not change `reopen_operation` outcome.
- `_restore_claim_continuity_for_reopen` preserved unchanged.
- Existing claim route guards remain unchanged.
- API response shape unchanged.
- No new event names.
- No close_operation changes.

## None Reason — Schema vs Service Boundary

`OperationReopenRequest(reason=None)` raises a Pydantic `ValidationError` at the schema
boundary before the service is called. This is the correct and expected behavior:
the schema enforces `reason` is a non-null string; the service enforces it is non-blank.
T4 documents this schema-level guard explicitly.

## Out-of-Scope Preserved

- No `close_operation` hardening (P0-C-07B complete)
- No `complete_operation` changes
- No claim removal or claim behavior change
- No StationSession hard enforcement
- No start/pause/resume/report_quantity/downtime changes
- No schema migration
- No FE/UI changes
- No dual-mode queue changes

## Hard Mode MOM v3 Gate Summary

### Event Map
| Command | Event Type | Event Name | Status | Payload |
|---|---|---|---|---|
| `reopen_operation` | `ExecutionEventType.OPERATION_REOPENED` | `"operation_reopened"` | CANONICAL IN CURRENT SOURCE — unchanged | `{actor_user_id, reason, reopened_at}` |

### Invariant Map (confirmed in source)
| Invariant | Enforcement | Verified By |
|---|---|---|
| reopen only from CLOSED | closure_status guard → STATE_NOT_CLOSED | T2, T12 |
| blank reason rejected | reason.strip() guard → REOPEN_REASON_REQUIRED | T3 |
| None reason rejected at schema | Pydantic ValidationError | T4 |
| tenant mismatch rejected | operation.tenant_id guard | T5 |
| reopen event emitted with payload | event append path | T6 |
| closure_status becomes OPEN | mark_operation_reopened + detail | T7 |
| runtime projection becomes PAUSED | _derive_status_from_runtime_facts | T8 |
| projection/detail backend-derived | derive_operation_detail | T8 |
| allowed_actions backend-derived | _derive_allowed_actions | T9 |
| session diagnostic non-blocking | _compute_session_diagnostic informational | T10, T11 |
| reopen_count increments | mark_operation_reopened | T13 |
| claim continuity preserved | _restore_claim_continuity_for_reopen | claim regression suite |
| single-active-claim constraint | conflict guard → STATE_REOPEN_OWNER_HAS_OTHER_ACTIVE_CLAIM | claim regression suite |
| claim compatibility lock unchanged | route-layer claim lock unchanged | claim regression suite |
| no close behavior changes | scope boundary | close/reopen baseline suite |

## Test Matrix Coverage

Covered in `test_reopen_operation_claim_continuity_hardening.py`:
1. (T1) reopen happy path from CLOSED completed
2. (T2) reopen rejects non-CLOSED (OPEN) operation → STATE_NOT_CLOSED
3. (T3) reopen rejects blank reason → REOPEN_REASON_REQUIRED
4. (T4) schema rejects None reason → Pydantic ValidationError
5. (T5) reopen rejects tenant mismatch → ValueError
6. (T6) reopen emits OPERATION_REOPENED with expected payload
7. (T7) closure_status becomes OPEN in detail and snapshot
8. (T8) projection/detail after reopen consistent (PAUSED + OPEN)
9. (T9) allowed_actions after reopen = ["resume_execution", "start_downtime"]
10. (T10) missing StationSession does not change reopen outcome
11. (T11) matching OPEN StationSession does not change reopen outcome
12. (T12) PAUSED non-closed operation rejects reopen → STATE_NOT_CLOSED
13. (T13) reopen_count increments on first reopen

## Verification Executed

1. Focused P0-C-07C suite
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_reopen_operation_claim_continuity_hardening.py`
- Result:
  - `13 passed in 5.30s`
- Exit code:
  - `0`

2. Close/complete command hardening regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_close_operation_command_hardening.py tests/test_complete_operation_command_hardening.py`
- Result:
  - `20 passed in 7.84s`
- Exit code:
  - `0`

3. Recent command hardening regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_start_pause_resume_command_hardening.py tests/test_report_quantity_command_hardening.py tests/test_downtime_command_hardening.py`
- Result:
  - `38 passed in 15.42s`
- Exit code:
  - `0`

4. StationSession lifecycle + diagnostic suites
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py`
- Result:
  - `25 passed in 9.85s`
- Exit code:
  - `0`

5. Claim regression subset
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py tests/test_reopen_resumability_claim_continuity.py tests/test_close_reopen_operation_foundation.py`
- Result:
  - `36 passed in 7.90s`
- Exit code:
  - `0`

6. Projection/status regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_operation_detail_allowed_actions.py tests/test_operation_status_projection_reconcile.py tests/test_status_projection_reconcile_command.py`
- Result:
  - `41 passed in 2.47s`
- Exit code:
  - `0`

7. Full backend suite (sequential)
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest --tb=no -q`
- Result:
  - `255 passed, 1 skipped in 53.29s`
- Exit code:
  - `0`
- Note: intermittent teardown deadlocks (psycopg DeadlockDetected in _purge fixtures)
  are pre-existing in the test suite and unrelated to P0-C-07C. On clean runs: 255 passed, 1 skipped, EXIT_CODE:0.

## Final Summary

| Item | Value |
|---|---|
| Files changed | `backend/tests/test_reopen_operation_claim_continuity_hardening.py` (new) |
| Tests written | 13 new tests |
| Production code changed | No |
| Command behavior changed | No — `reopen_operation` behavior unchanged |
| Event behavior changed | No — `operation_reopened` unchanged |
| StationSession diagnostic impact | None — remains non-blocking |
| Claim compatibility impact | None — claim lock unchanged |
| Claim continuity behavior | Preserved — `_restore_claim_continuity_for_reopen` unchanged |
| Tests run (focused) | 13 passed |
| Full backend suite | 255 passed, 1 skipped, exit 0 |
| P0-C-07C complete | Yes |

## Recommended Next Slice

**P0-C Closeout Review** — verify P0-C execution hardening batch (07A+07B+07C) is complete
and determine whether additional guard hardening or documentation is needed before moving to
P0-D Quality Lite.

Alternative: **P0-C-07D** (if a further slice is needed for any remaining execution command).
