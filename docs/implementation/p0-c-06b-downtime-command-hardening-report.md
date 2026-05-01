# P0-C-06B Downtime Start / End Command Hardening Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: Strict
- Hard Mode MOM: v3
- Reason: Harden `start_downtime` and `end_downtime` command guards including state legality, open-downtime invariants, reason code validation, event emission, projection transitions, and no-auto-resume contract while preserving claim compatibility and non-blocking StationSession diagnostic behavior.

## Slice Outcome

Status: COMPLETE

Classification: Tests-only hardening slice

Production code changed: No

## Scope Implemented

- Added focused hardening test suite:
  - `backend/tests/test_downtime_command_hardening.py`
- Verified command guard legality and rejection behavior for:
  - `start_downtime`
  - `end_downtime`
- Verified downtime invariants:
  - `start_downtime` allowed only from IN_PROGRESS or PAUSED
  - Duplicate open downtime rejected (DOWNTIME_ALREADY_OPEN via event-count guard)
  - Invalid/unknown reason code rejected (INVALID_REASON_CODE)
  - `end_downtime` requires open downtime (STATE_NO_OPEN_DOWNTIME when none)
- Verified emitted event names are unchanged:
  - `downtime_started`
  - `downtime_ended`
- Verified snapshot and event-derived projection transitions:
  - `start_downtime` from IN_PROGRESS → snapshot BLOCKED, derived BLOCKED
  - `start_downtime` from PAUSED → snapshot stays PAUSED, derived BLOCKED (event-count wins)
  - `end_downtime` → snapshot BLOCKED→PAUSED, derived PAUSED, `downtime_open=False`
- Verified no-auto-resume invariant: `end_downtime` never emits EXECUTION_RESUMED
- Verified `resume_operation` blocked while downtime open (STATE_DOWNTIME_OPEN)
- Re-verified StationSession diagnostic remains non-blocking for downtime commands

## Design Clarification (Not a Bug)

`_derive_status` returns BLOCKED whenever `downtime_started_count > downtime_ended_count`, independent of snapshot. The service comment "If PAUSED, stay PAUSED" in `start_downtime` refers to the snapshot column only. When `start_downtime` is called from PAUSED, the snapshot remains PAUSED but the event-derived projection (authoritative) shows BLOCKED because downtime is open. This is consistent with the state machine spec and confirmed by T2.

## Out-of-Scope Preserved

- No StationSession hard enforcement
- No claim removal or claim behavior change
- No production reporting changes
- No complete/close/reopen hardening (P0-C-07)
- No schema migration
- No event name change
- No FE/UI changes

## Hard Mode MOM v3 Gate Summary

### Event Map
| Command | Event Type | Event Name | Status | Payload |
|---|---|---|---|---|
| `start_downtime` | `ExecutionEventType.DOWNTIME_STARTED` | `"downtime_started"` | CANONICAL — unchanged | `{actor_user_id, reason_code, reason_name, reason_group, planned_flag, note, started_at}` |
| `end_downtime` | `ExecutionEventType.DOWNTIME_ENDED` | `"downtime_ended"` | CANONICAL — unchanged | `{actor_user_id, note, ended_at}` |

### Invariant Map (confirmed in source)
| Invariant | Enforcement | Verified By |
|---|---|---|
| start_downtime from IN_PROGRESS or PAUSED only | status guard | T1, T2, T3 |
| duplicate open downtime rejected | event-count guard | T5, T5b |
| invalid reason code rejected | reason resolver | T6 |
| CLOSED record rejected (both commands) | `_ensure_operation_open_for_write` | T4, T10 |
| end_downtime requires open downtime | event-count guard | T9 |
| IN_PROGRESS→BLOCKED on start_downtime (event-derived) | `_derive_status` | T1 |
| PAUSED→BLOCKED (event-derived) on start_downtime from PAUSED | `_derive_status` (clarification) | T2 |
| BLOCKED→PAUSED on end_downtime | `mark_operation_paused` + `_derive_status` | T7 |
| No auto-resume after end_downtime | no EXECUTION_RESUMED emitted | T8 |
| resume blocked while downtime open | STATE_DOWNTIME_OPEN | T11 |
| session diagnostic non-blocking | `_compute_session_diagnostic` informational | T12, T13 |
| claim route guards unchanged | route layer | claim regression |

## Test Matrix Coverage

Covered in `test_downtime_command_hardening.py`:
1. (T1) start_downtime happy path from IN_PROGRESS → BLOCKED, downtime_open=True, allowed=["end_downtime"]
2. (T2) start_downtime happy path from PAUSED → event-derived BLOCKED, downtime_open=True
3. (T3) start_downtime rejects PLANNED (STATE_NOT_RUNNING_OR_PAUSED)
4. (T4) start_downtime rejects CLOSED operation (STATE_CLOSED_RECORD)
5. (T5) start_downtime rejects duplicate via snapshot-BLOCKED path
6. (T5b) start_downtime rejects DOWNTIME_ALREADY_OPEN via event-count guard
7. (T6) start_downtime rejects unknown reason code (INVALID_REASON_CODE)
8. (T7) end_downtime happy path BLOCKED→PAUSED, downtime_open=False, allowed=["resume_execution","start_downtime"]
9. (T8) end_downtime no auto-resume (no EXECUTION_RESUMED emitted)
10. (T9) end_downtime rejects when no open downtime (STATE_NO_OPEN_DOWNTIME)
11. (T10) end_downtime rejects CLOSED operation (STATE_CLOSED_RECORD)
12. (T11) resume_operation rejected while downtime open (STATE_DOWNTIME_OPEN)
13. (T12) no-session outcome parity — missing StationSession does not change outcome
14. (T13) open-session outcome parity — OPEN StationSession does not change outcome

## Verification Executed

1. Focused P0-C-06B suite
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_downtime_command_hardening.py`
- Result:
  - `14 passed in 6.20s`
- Exit code:
  - `0`

2. P0-C-06A + P0-C-05 regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_report_quantity_command_hardening.py tests/test_start_pause_resume_command_hardening.py`
- Result:
  - `24 passed in 9.71s`
- Exit code:
  - `0`

3. StationSession lifecycle + diagnostic suites
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py`
- Result:
  - `25 passed in 9.34s`
- Exit code:
  - `0`

4. Claim regression subset
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py tests/test_reopen_resumability_claim_continuity.py tests/test_close_reopen_operation_foundation.py`
- Result:
  - `36 passed in 8.06s`
- Exit code:
  - `0`

5. Projection/status regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_operation_detail_allowed_actions.py tests/test_operation_status_projection_reconcile.py tests/test_status_projection_reconcile_command.py`
- Result:
  - `41 passed in 2.48s`
- Exit code:
  - `0`

6. Full backend suite
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest --tb=no -q`
- Result:
  - `222 passed, 1 skipped in 39.83s`
- Exit code:
  - `0`

## Final Summary

| Item | Value |
|---|---|
| Files changed | `backend/tests/test_downtime_command_hardening.py` (new) |
| Tests written | 14 new tests |
| Production code changed | No |
| Command behavior changed | No — `start_downtime` and `end_downtime` behavior unchanged |
| Event behavior changed | No — `downtime_started` / `downtime_ended` canonical and unchanged |
| StationSession diagnostic impact | None — non-blocking confirmed |
| Claim compatibility impact | None — claim route guards unchanged |
| Tests run (focused) | 14 passed |
| Full backend suite | 222 passed, 1 skipped, exit 0 |
| P0-C-06B complete | Yes |

## Recommended Next Slice

**P0-C-07 Complete / Close / Reopen Guard Alignment**

Scope: Harden `complete_operation`, `close_operation`, and `reopen_operation` command guards.
- `complete_operation` only from IN_PROGRESS
- `close_operation` only from COMPLETED/COMPLETED_LATE
- `reopen_operation` only from CLOSED record
- Closed-record rejection where applicable
- Event emission: `OP_COMPLETED`, `OPERATION_CLOSED_AT_STATION`, `OPERATION_REOPENED`
- Projection verified after each command
- StationSession diagnostic non-blocking
- Claim compatibility preserved
