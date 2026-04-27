# Station Execution State Matrix

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Reworked matrix around session-owned execution and claim deprecation. |

Status: Canonical state matrix for the approved next-step Station Execution design.

## 1. Implemented/target state carriers

### Runtime execution status
- `PLANNED`
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`
- `ABORTED`

### Orthogonal dimension
- `closure_status`: `OPEN`, `CLOSED`

### Deferred dimensions
- `quality_status`
- `review_status`
- fuller `dispatch_status`

## 2. Global invariants

### INV-001 — Closed records reject execution writes
When `closure_status = CLOSED`, execution write commands are rejected except authorized reopen flow.

### INV-002 — One running execution per governing station/resource context
Implemented/target safe default.

### INV-003 — Open downtime blocks resume and completion
Implemented/target safe default.

### INV-004 — Active execution mutation requires valid station session context
Start/pause/resume/report/downtime/complete require valid session-owned context.

## 3. Session/context transitions

| ID | Current state | Command | Guard | Reject when | Event / effect | Next state |
|---|---|---|---|---|---|---|
| SS-OPEN-001 | no active station session | `open_station_session` | actor authenticated and authorized in scope | invalid station/resource context | `station_session_opened` | active station session |
| OP-ID-001 | active station session without operator | `identify_operator` | operator valid under policy | invalid/inactive operator | `operator_identified_at_station` | active station session with operator |
| EQ-BIND-001 | active station session | `bind_equipment` | equipment valid for station/resource policy | invalid equipment; out-of-scope equipment | `equipment_bound_to_station_session` | active station session with bound equipment |
| SS-CLOSE-001 | active station session | `close_station_session` | no active work would be orphaned | running/open work still owned by session | `station_session_closed` | no active station session |

## 4. Execution transitions

| ID | Current state | Command | Guard | Reject when | Event / effect | Next state |
|---|---|---|---|---|---|---|
| START-001 | `status = PLANNED`; `closure_status = OPEN` | `start_execution` | actor authorized; valid station session; operator identified; equipment bound when required; no competing running execution | invalid state; closed record; missing session/operator/equipment context | `execution_started` | `IN_PROGRESS` |
| PAUSE-001 | `status = IN_PROGRESS`; `closure_status = OPEN` | `pause_execution` | actor authorized; valid ownership session | invalid state; closed record; missing session context | `execution_paused` | `PAUSED` |
| RESUME-001 | `status = PAUSED`; `closure_status = OPEN`; no open downtime | `resume_execution` | actor authorized; valid ownership session; no competing running execution | open downtime; invalid state; closed record; missing session context | `execution_resumed` | `IN_PROGRESS` |
| PROD-REP-001 | `status = IN_PROGRESS`; `closure_status = OPEN` | `report_production` | non-negative delta; at least one delta > 0; valid ownership session | invalid delta; invalid state; closed record; missing session context | `production_reported` | status unchanged |
| DT-START-001 | `status IN (IN_PROGRESS, PAUSED)`; `closure_status = OPEN`; no open downtime | `start_downtime` | valid ownership session; valid `reason_code` | downtime already open; invalid state; closed record; invalid/inactive reason | `downtime_started` | `BLOCKED` |
| DT-END-001 | open downtime exists; `closure_status = OPEN` | `end_downtime` | valid ownership session | no open downtime; closed record; missing session context | `downtime_ended` | `PAUSED` |
| COMPLETE-001 | `status = IN_PROGRESS`; `closure_status = OPEN`; no open downtime | `complete_execution` | actor authorized; valid ownership session | invalid state; closed record; open downtime; missing session context | `execution_completed` | `COMPLETED` + `OPEN` |

## 5. Closure transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| CLOSE-001 | `status = COMPLETED`; `closure_status = OPEN` | `close_operation` | actor authorized under current phase rule; record completed | already closed; not completed; unauthorized | `operation_closed_at_station` | `closure_status = CLOSED` |
| REOPEN-001 | `closure_status = CLOSED` | `reopen_operation` | actor authorized under current phase rule; reason present; reopen path safe | reason missing; unauthorized | `operation_reopened` | `closure_status = OPEN`; runtime projection `PAUSED` |

## 6. Transition note

This matrix replaces claim-owned target semantics with session-owned target semantics.
Any remaining claim-owned behavior in current code is migration debt, not target matrix truth.
