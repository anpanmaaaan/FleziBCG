# P0-C-06A Production Reporting Command Hardening Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: Strict
- Hard Mode MOM: v3
- Reason: Harden `report_quantity` command guards including state legality, quantity validation, closed-record rejection, event emission, and projection consistency while preserving claim compatibility and non-blocking StationSession diagnostic behavior.

## Slice Outcome

Status: COMPLETE

Classification: Tests-only hardening slice

Production code changed: No

## Scope Implemented

- Added focused hardening test suite:
  - `backend/tests/test_report_quantity_command_hardening.py`
- Verified command guard legality and rejection behavior for:
  - `report_quantity`
- Verified quantity invariants:
  - `good_qty >= 0 AND scrap_qty >= 0` (non-negative)
  - `good_qty + scrap_qty > 0` (at least one positive)
  - Both defaults (scrap_qty=0 with good_qty>0 accepted)
- Verified emitted event name is unchanged:
  - `QTY_REPORTED`
- Verified event-derived projection after `report_quantity`:
  - Status remains `in_progress`
  - `good_qty` and `scrap_qty` accumulate across multiple `QTY_REPORTED` events
- Verified backend-derived `allowed_actions` after `report_quantity`:
  - `["report_production", "pause_execution", "complete_execution", "start_downtime"]`
- Re-verified StationSession diagnostic remains non-blocking for command outcomes:
  - no active session path
  - matching OPEN session path

## Out-of-Scope Preserved

- No StationSession hard enforcement
- No claim removal or claim behavior change
- No downtime command hardening (P0-C-06B)
- No complete/close/reopen hardening (P0-C-07)
- No schema migration
- No event name change
- No FE/UI changes

## Hard Mode MOM v3 Gate Summary

### Event Map
| Command | Event Type | Event Name | Status | Payload |
|---|---|---|---|---|
| `report_quantity` | `ExecutionEventType.QTY_REPORTED` | `"QTY_REPORTED"` | CANONICAL — unchanged | `{good_qty, scrap_qty, operator_id}` |

### Invariant Map (confirmed in source)
| Invariant | Enforcement | Verified By |
|---|---|---|
| report only from IN_PROGRESS | service guard line 1040 | T3, T4 |
| good_qty >= 0 AND scrap_qty >= 0 | service guard line 1042 | T6, T7 |
| good_qty + scrap_qty > 0 | service guard line 1045 | T8 |
| CLOSED record rejected | `_ensure_operation_open_for_write` | T5 |
| tenant mismatch rejected | tenant guard line 1035 | existing tests |
| session diagnostic non-blocking | `_compute_session_diagnostic` informational | T11, T12 |
| QTY_REPORTED does not change status | `_derive_status` ignores QTY_REPORTED | T1, T2, T9 |
| good_qty/scrap_qty accumulate | `derive_operation_detail` accumulation loop | T9 |
| allowed_actions backend-derived | `_derive_allowed_actions` with IN_PROGRESS | T10 |
| claim route guards unchanged | route layer, unchanged | claim regression |

## Test Matrix Coverage

Covered in `test_report_quantity_command_hardening.py`:
1. (T1) happy path — good_qty only, status stays IN_PROGRESS, QTY_REPORTED emitted
2. (T2) happy path — mixed good+scrap qty, projection accumulates correctly
3. (T3) rejects PLANNED operation (non-IN_PROGRESS)
4. (T4) rejects PAUSED operation (non-IN_PROGRESS)
5. (T5) rejects CLOSED operation (closure_status=closed) with STATE_CLOSED_RECORD
6. (T6) rejects negative good_qty
7. (T7) rejects negative scrap_qty
8. (T8) rejects zero-sum (both good_qty=0 and scrap_qty=0)
9. (T9) cumulative projection across two QTY_REPORTED events
10. (T10) allowed_actions after report are backend-derived and correct
11. (T11) no-session outcome parity — missing StationSession does not change outcome
12. (T12) open-session outcome parity — OPEN StationSession does not change outcome

## Verification Executed

1. Focused P0-C-06A suite
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_report_quantity_command_hardening.py`
- Result:
  - `12 passed in 5.93s`
- Exit code:
  - `0`

2. P0-C-05 regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_start_pause_resume_command_hardening.py`
- Result:
  - `12 passed in 5.14s`
- Exit code:
  - `0`

3. StationSession lifecycle + diagnostic suites
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py`
- Result:
  - `25 passed in 9.45s`
- Exit code:
  - `0`

4. Claim regression subset
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py tests/test_reopen_resumability_claim_continuity.py tests/test_close_reopen_operation_foundation.py`
- Result:
  - `36 passed in 10.16s`
- Exit code:
  - `0`

5. Projection/status regression
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_operation_detail_allowed_actions.py tests/test_operation_status_projection_reconcile.py tests/test_status_projection_reconcile_command.py`
- Result:
  - `41 passed in 2.60s`
- Exit code:
  - `0`

6. Full backend suite
- Command:
  - `g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest --tb=no -q`
- Result:
  - `208 passed, 1 skipped in 37.10s`
- Exit code:
  - `0`

## Final Summary

| Item | Value |
|---|---|
| Files changed | `backend/tests/test_report_quantity_command_hardening.py` (new) |
| Tests written | 12 new tests |
| Production code changed | No |
| Command behavior changed | No — `report_quantity` behavior unchanged |
| Event behavior changed | No — `QTY_REPORTED` canonical and unchanged |
| StationSession diagnostic impact | None — non-blocking confirmed |
| Claim compatibility impact | None — claim route guards unchanged |
| Tests run (focused) | 12 passed |
| Full backend suite | 208 passed, 1 skipped, exit 0 |
| P0-C-06A complete | Yes |

## Recommended Next Slice

**P0-C-06B Downtime Command Hardening**

Scope: Harden `start_downtime` and `end_downtime` command guards.
- `start_downtime` only from IN_PROGRESS or PAUSED without open downtime
- `end_downtime` only when downtime is open
- Closed-record rejection
- Event emission: `downtime_started`, `downtime_ended`
- Projection: downtime_open flag derives from event count parity
- StationSession diagnostic non-blocking
- Claim compatibility preserved
