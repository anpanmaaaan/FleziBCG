# P0-C-07B Close Operation Guard Hardening Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: Strict
- Hard Mode MOM: v3
- Reason: Harden `close_operation` command guards and closure projection behavior while preserving claim compatibility and non-blocking StationSession diagnostic behavior.

## Slice Outcome

Status: COMPLETE

Classification: Tests-only hardening slice

Production code changed: No

## Scope Implemented

- Added focused hardening test suite:
  - `backend/tests/test_close_operation_command_hardening.py`
- Verified close state legality:
  - happy path from COMPLETED
  - rejects invalid runtime state with `STATE_NOT_COMPLETED`
- Verified closed-record/already-closed rejection:
  - `STATE_ALREADY_CLOSED`
- Verified tenant mismatch rejection:
  - `ValueError("Operation does not belong to the requesting tenant.")`
- Verified emitted close event remains unchanged:
  - `operation_closed_at_station`
- Verified closure transition:
  - `closure_status: OPEN -> CLOSED`
- Verified projection/detail after close:
  - runtime `status` remains completed
  - detail includes close metadata (`last_closed_by`, `last_closed_at`)
- Verified backend-derived allowed actions after close:
  - `["reopen_operation"]`
- Re-verified StationSession diagnostic remains non-blocking:
  - missing session path
  - matching OPEN session path
- Re-verified claim compatibility and close/reopen regression baseline unchanged

## Behavior Contract Confirmed

- No StationSession enforcement in P0-C-07B.
- Missing StationSession does not reject `close_operation` in current source.
- Matching OPEN StationSession does not change `close_operation` outcome.
- Existing claim route guards remain unchanged.
- API response shape unchanged.
- No new event names.
- No reopen logic changes.

## Out-of-Scope Preserved

- No `reopen_operation` hardening (P0-C-07C)
- No claim continuity changes
- No StationSession hard enforcement
- No claim removal or claim behavior change
- No complete/downtime/report/start/pause/resume changes
- No schema migration
- No FE/UI changes

## Hard Mode MOM v3 Gate Summary

### Event Map
| Command | Event Type | Event Name | Status | Payload |
|---|---|---|---|---|
| `close_operation` | `ExecutionEventType.OPERATION_CLOSED_AT_STATION` | `"operation_closed_at_station"` | CANONICAL IN CURRENT SOURCE — unchanged | `{actor_user_id, note, closed_at}` |

### Invariant Map (confirmed in source)
| Invariant | Enforcement | Verified By |
|---|---|---|
| close only from completed runtime states | `detail.status` guard | T1, T2 |
| already-closed rejects close | closure_status guard | T3 |
| tenant mismatch rejected | service tenant guard | T4 |
| close event emitted | event append path | T5 |
| closure_status becomes CLOSED | mark_operation_closed + detail | T6 |
| projection/detail remains backend-derived | derive_operation_detail | T7 |
| allowed_actions backend-derived after close | _derive_allowed_actions | T8 |
| session diagnostic non-blocking | _compute_session_diagnostic informational | T9, T10 |
| claim compatibility preserved | route-layer claim lock unchanged | claim regression suite |
| no reopen behavior changes | scope boundary | close/reopen baseline suite |

## Test Matrix Coverage

Covered in `test_close_operation_command_hardening.py`:
1. (T1) close happy path from COMPLETED
2. (T2) close rejects invalid runtime state (STATE_NOT_COMPLETED)
3. (T3) close rejects already CLOSED operation (STATE_ALREADY_CLOSED)
4. (T4) close rejects tenant mismatch
5. (T5) close emits OPERATION_CLOSED_AT_STATION with expected payload
6. (T6) closure_status becomes CLOSED in detail and snapshot
7. (T7) projection/detail after close remains consistent
8. (T8) allowed_actions after close resolves to ["reopen_operation"]
9. (T9) no-session outcome parity
10. (T10) OPEN-session outcome parity

## Verification Executed

1. Focused P0-C-07B suite
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_close_operation_command_hardening.py`
- Result:
  - `10 passed in 4.42s`
- Exit code:
  - `0`

2. Recent command hardening regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_complete_operation_command_hardening.py tests/test_start_pause_resume_command_hardening.py tests/test_report_quantity_command_hardening.py tests/test_downtime_command_hardening.py`
- Result:
  - `48 passed in 19.44s`
- Exit code:
  - `0`

3. StationSession lifecycle + diagnostic suites
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py`
- Result:
  - `25 passed in 9.66s`
- Exit code:
  - `0`

4. Claim regression subset
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py tests/test_reopen_resumability_claim_continuity.py tests/test_close_reopen_operation_foundation.py`
- Result:
  - `36 passed in 8.99s`
- Exit code:
  - `0`

5. Projection/status regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_operation_detail_allowed_actions.py tests/test_operation_status_projection_reconcile.py tests/test_status_projection_reconcile_command.py`
- Result:
  - `41 passed in 2.46s`
- Exit code:
  - `0`

6. Full backend suite (sequential)
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q`
- Result:
  - `242 passed, 1 skipped in 46.26s`
- Exit code:
  - `0`

## Final Summary

| Item | Value |
|---|---|
| Files changed | `backend/tests/test_close_operation_command_hardening.py` (new) |
| Tests written | 10 new tests |
| Production code changed | No |
| Command behavior changed | No — `close_operation` behavior unchanged |
| Event behavior changed | No — `operation_closed_at_station` unchanged |
| StationSession diagnostic impact | None — remains non-blocking |
| Claim compatibility impact | None — claim lock unchanged |
| Tests run (focused) | 10 passed |
| Full backend suite | 242 passed, 1 skipped, exit 0 |
| P0-C-07B complete | Yes |

## Recommended Next Slice

**P0-C-07C Reopen Operation / Claim Continuity Hardening**

Scope:
- Harden `reopen_operation` guard and claim-continuity compatibility only
- Preserve StationSession diagnostic non-blocking behavior
- No StationSession hard enforcement in that slice
