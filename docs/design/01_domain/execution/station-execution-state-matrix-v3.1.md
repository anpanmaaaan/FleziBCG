# Station Execution State Matrix

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-22 | v3.1 | Align downtime reason documentation to backend master data using `reason_code`. |

## Current implemented backend baseline

Status: **Authoritative implementation matrix for the current backend baseline**  
Scope: **Station Execution Core / Pre-QC / Pre-Review**

This version reconciles the state matrix with what is actually implemented now. It does not claim full canonical parity.

## 1. Implemented state carriers

### 1.1 Runtime execution status (implemented carrier)
Current implementation uses:
- `PLANNED`
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`
- `ABORTED` where implementation enum supports it

### 1.2 Implemented orthogonal dimension
- `closure_status`: `OPEN`, `CLOSED`

### 1.3 Deferred dimensions
Not yet implemented in current backend baseline:
- `quality_status`
- `review_status`
- full `dispatch_status`

## 2. Global invariants

### INV-001 — Closed records reject execution writes
When `closure_status = CLOSED`, execution write commands are rejected except authorized reopen flow.

### INV-002 — One running execution per station (v1)
Implemented in current core baseline.

### INV-003 — Open downtime blocks resume and completion
Implemented.

### INV-004 — One active unreleased claim per operator per station context (default v1)
Implemented safe default:
- no routine multi-claim stacking
- claim continuity across active non-terminal states remains intact

## 3. Claim and execution transitions

| ID | Current state | Command | Guard | Reject when | Event / effect | Next state |
|---|---|---|---|---|---|---|
| CLAIM-001 | `status = PLANNED`; `closure_status = OPEN` | `claim_operation` | actor authorized; operator does not already hold another unreleased claim in same station context | already claimed elsewhere; second unreleased claim attempt in same station context | `operation_claimed` | remains execution-pending with claimed ownership |
| START-001 | `status = PLANNED`; `closure_status = OPEN`; claim owned by actor | `start_execution` | actor authorized; no competing running execution | not claimed by actor; invalid state; closed record | `execution_started` | `IN_PROGRESS` |
| PAUSE-001 | `status = IN_PROGRESS`; `closure_status = OPEN`; claim owned by actor | `pause_execution` | actor authorized | invalid state; closed record | `execution_paused` | `PAUSED` |
| RESUME-001 | `status = PAUSED`; `closure_status = OPEN`; claim owned by actor; no open downtime | `resume_execution` | actor authorized; no competing running execution | open downtime; invalid state; closed record; missing ownership | `execution_resumed` | `IN_PROGRESS` |
| PROD-REP-001 | `status = IN_PROGRESS`; `closure_status = OPEN`; claim owned by actor | `report_production` | non-negative delta; at least one delta > 0 | invalid delta; invalid state; closed record; missing ownership | `production_reported` / implementation legacy event naming may still exist internally | quantities updated; status unchanged |
| DT-START-001 | `status IN (IN_PROGRESS, PAUSED)`; `closure_status = OPEN`; claim owned by actor; no open downtime | `start_downtime` | valid `reason_code` from backend downtime reason master data | downtime already open; invalid state; closed record; invalid or inactive `reason_code` | `downtime_started` | `BLOCKED` with downtime open in current baseline behavior |
| DT-END-001 | open downtime exists; `closure_status = OPEN`; claim owned by actor | `end_downtime` | actor authorized | no open downtime; closed record; missing ownership | `downtime_ended` | `PAUSED` |
| COMPLETE-001 | `status = IN_PROGRESS`; `closure_status = OPEN`; claim owned by actor; no open downtime | `complete_execution` | actor authorized | invalid state; closed record; open downtime; missing ownership | `execution_completed` | `COMPLETED` + `OPEN` |

## 4. Closure transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| CLOSE-001 | `status = COMPLETED`; `closure_status = OPEN` | `close_operation` | actor authorized under current phase rule (`SUP` at API boundary); record completed | already closed; not completed; unauthorized | `operation_closed_at_station` | `closure_status = CLOSED` |
| REOPEN-001 | `closure_status = CLOSED` | `reopen_operation` | actor authorized under current phase rule; reason present; reopen path safe | reason missing; unauthorized; restore would violate single-active-claim semantics where claim restoration is required | `operation_reopened` | `closure_status = OPEN`; runtime projection `PAUSED`; reopen metadata incremented |

## 5. Reopen continuity note

Current implemented foundation preserves resumability by:
- keeping active claim continuity where it still exists
- or restoring the last historical claim owner on reopen when safe
- without widening generic paused-state claimability globally

This is implementation-phase truth for the current baseline.

## 6. Explicitly deferred from this matrix

Not implemented in the current backend baseline:
- station session transitions
- QC transitions
- exception/disposition transitions
- quality/review-based block matrix
- approved-effect unlock paths
- full dispatch/release orchestration-fed matrix

## 7. Implementation note on event naming

Canonical event names remain the target names in docs (`execution_started`, `production_reported`, etc.), but current backend storage still carries mixed legacy/internal event naming in places. Treat this as contract debt, not as canonical vocabulary.
