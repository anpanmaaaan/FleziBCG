# Station Execution State Matrix (Canonical v1)

Status: Authoritative implementation matrix  
Owner: Product / Domain / Backend  
Depends on: `business-truth-station-execution.md`

---

## 1. Purpose

This document defines the valid state transitions for the station execution aggregate.

It is the canonical source for:

- accepted and rejected transitions
- command preconditions and blockers
- state effects of accepted commands
- where disposition approvals unlock otherwise-blocked paths

This file does not define UI flow. It defines backend-valid business transitions.

---

## 2. Canonical state dimensions

### 2.1 Dispatch status

- `NOT_DISPATCHED`
- `DISPATCHED`
- `CLAIMED`
- `RELEASED_TO_EXECUTE`

### 2.2 Execution status

- `NOT_STARTED`
- `RUNNING`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`

### 2.3 Quality status

- `QC_NOT_REQUIRED`
- `QC_PENDING`
- `QC_PASSED`
- `QC_FAILED`
- `QC_HOLD`

### 2.4 Review status

- `NO_REVIEW`
- `REVIEW_REQUIRED`
- `DECISION_PENDING`
- `DISPOSITION_DONE`

### 2.5 Closure status

- `OPEN`
- `CLOSED`

### 2.6 Reopen representation

Reopen is not a status value. Reopen is represented by:

- event `operation_reopened`
- `reopen_count`
- `last_reopened_at`
- `last_reopened_by`

---

## 3. Aggregate scope

The matrix applies to **one operation execution context at one station**.

All command validation must also pass:

- tenant and scope validity
- aggregate identity validity
- optimistic concurrency checks
- authorization checks

---

## 4. Global invariants

### INV-001 — Closed records are immutable by default
When `closure_status = CLOSED`, operational commands are rejected except authorized reopen flow.

### INV-002 — Blocked means progression is not allowed
When execution is effectively blocked by quality hold or review policy, `resume_execution` and `complete_execution` are rejected unless valid approved effect exists where policy allows.

### INV-003 — One running execution per station (v1)
At most one execution may be in `RUNNING` at a station at a time.

### INV-004 — Open downtime blocks resume and completion
When downtime is open, `resume_execution` and `complete_execution` are rejected.

### INV-005 — Decision-needed state blocks normal progression
When review requires an unresolved decision, `resume_execution` and `complete_execution` are rejected unless a consumable approved effect explicitly unlocks the transition.

---

## 5. Orchestration-owned precondition transitions

These are visible in station execution state, but not owned by station actors.

| ID | Current state | Trigger source | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| ORCH-DISP-001 | `dispatch_status = NOT_DISPATCHED` | orchestration | operation assigned to station | station invalid; routing invalid | `operation_dispatched_to_station` | `dispatch_status = DISPATCHED` |
| ORCH-REL-001 | `dispatch_status IN (DISPATCHED, CLAIMED)`; `execution_status = NOT_STARTED`; `closure_status = OPEN` | orchestration | pre-start release policy passed | active hard hold; invalid station assignment | `operation_released_to_execute` | `dispatch_status = RELEASED_TO_EXECUTE` |

Note: implementations may merge `DISPATCHED` and `RELEASED_TO_EXECUTE` if release is implicit, but station execution consumers must still treat release semantics as orchestration-owned.

---

## 6. Station session transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| SESS-OPEN-001 | no active session | `open_station_session` | actor authorized; station active; exclusivity policy passes | station disabled; actor unauthorized; exclusivity conflict | `station_session_opened` | active session exists |
| SESS-CLOSE-001 | active session exists | `close_station_session` | no running execution tied to session; no orphaning rule violation | active running execution; open downtime would be orphaned; policy blocks exit | `station_session_closed` | no active session |

---

## 7. Claim and execution transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| CLAIM-001 | `dispatch_status IN (DISPATCHED, RELEASED_TO_EXECUTE)`; `execution_status = NOT_STARTED`; `closure_status = OPEN` | `claim_operation` | actor authorized; station session active; operation still assigned to station | operation already claimed elsewhere; assignment invalid; session missing | `operation_claimed` | `dispatch_status = CLAIMED` |
| START-001 | `dispatch_status IN (CLAIMED, RELEASED_TO_EXECUTE)`; `execution_status = NOT_STARTED`; `closure_status = OPEN` | `start_execution` | active station session; no open downtime; no quality hold; no unresolved hard review; station has no other running execution; pre-start gates pass | session missing; hard hold exists; downtime open; competing running execution; mandatory gate failed | `execution_started` | `execution_status = RUNNING` |
| PAUSE-001 | `execution_status = RUNNING`; `closure_status = OPEN` | `pause_execution` | actor authorized | execution not running; record closed | `execution_paused` | `execution_status = PAUSED` |
| RESUME-001 | `execution_status = PAUSED`; `closure_status = OPEN` | `resume_execution` | no open downtime; no quality hold; no pending decision; no other hard block; no competing running execution | open downtime; `quality_status = QC_HOLD`; `review_status IN (REVIEW_REQUIRED, DECISION_PENDING)`; another execution already running | `execution_resumed` | `execution_status = RUNNING` |
| RESUME-002 | `execution_status = BLOCKED`; `closure_status = OPEN` | `resume_execution` | blocking cause resolved **or** approved consumable effect exists (`ALLOW_FORCE_RESUME` or `ALLOW_BLOCK_OVERRIDE`); no open downtime; no quality hold; no unresolved quality-owned decision; no competing running execution | blocking cause unresolved; no consumable approved effect; downtime open; quality hold active; competing running execution | `execution_resumed` | `execution_status = RUNNING` |

### 7.1 Derived block rule

`BLOCKED` is entered by policy or event consequence, not by a direct free-form user command.

Typical causes:

- hard quality hold
- hard operational block
- review policy maps current pending exception to execution block

---

## 8. Production reporting transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| PROD-REP-001 | `execution_status IN (RUNNING, PAUSED)`; `closure_status = OPEN` | `report_production` | actor authorized; delta values valid; policy allows report in current runtime state | negative free-form correction submitted; invalid delta; mandatory reason missing for NG; closed record | `production_reported` | quantities updated by projection; statuses unchanged unless policy derives a review |
| PROD-REP-002 | any | `report_production` | none | `execution_status IN (NOT_STARTED, COMPLETED)`; `closure_status = CLOSED` | none | rejected |

Notes:

- canonical v1 uses delta reporting only
- free-form negative corrective quantity events are not allowed
- overrun may require approved exception before report is accepted, depending on policy

---

## 9. Downtime transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| DT-START-001 | `execution_status IN (RUNNING, PAUSED)`; `closure_status = OPEN`; no open downtime | `start_downtime` | valid reason classification; actor authorized | downtime already open; execution completed/closed; reason invalid | `downtime_started` | execution remains `PAUSED` or becomes `BLOCKED` per policy |
| DT-END-001 | open downtime exists; `closure_status = OPEN` | `end_downtime` | actor authorized; downtime target valid | no open downtime; closure is closed; SoD/policy rule blocks close | `downtime_ended` | downtime cleared; execution stays non-running until explicit resume |

---

## 10. Quality transitions

| ID | Current state | Command / source | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| QC-SUBMIT-001 | `execution_status IN (RUNNING, PAUSED)`; `closure_status = OPEN` | `submit_qc_measurement` | payload valid; actor authorized | payload invalid; record closed | `qc_measurement_submitted` | quality state unchanged until evaluation |
| QC-EVAL-001 | measurement submitted | backend policy evaluation | QC policy bound and evaluable | policy missing or payload invalid | `qc_result_recorded` | `quality_status = QC_PASSED` or `QC_FAILED` or `QC_PENDING` |
| QC-HOLD-001 | `quality_status = QC_FAILED` | backend quality policy | fail requires hold/review | policy says no hold required | `qc_hold_applied` | `quality_status = QC_HOLD`; `review_status = REVIEW_REQUIRED` or `DECISION_PENDING`; execution may become `BLOCKED` |
| QC-DISP-001 | `quality_status = QC_HOLD`; `closure_status = OPEN` | `record_disposition_decision` | actor authorized as quality owner; SoD passes; target exception/review open; `decision_outcome` valid; `disposition_code` present when approved | actor unauthorized; same actor where SoD required; no active review; invalid disposition | `disposition_decision_recorded` | `review_status = DISPOSITION_DONE`; `quality_status` and downstream effect derived from disposition; execution remains non-running unless separate resume occurs |

---

## 11. Exception and disposition transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| EXC-RAISE-001 | `closure_status = OPEN` | `raise_exception` | valid exception type; actor authorized to raise; target context valid | invalid type; closed record; actor unauthorized | `exception_raised` | `review_status = REVIEW_REQUIRED` or `DECISION_PENDING`; execution may become `BLOCKED` per policy |
| DISP-DECIDE-001 | `review_status IN (REVIEW_REQUIRED, DECISION_PENDING)`; `closure_status = OPEN` | `record_disposition_decision` | actor authorized for exception domain; SoD passes; target exception/review still open; `decision_outcome` valid; `disposition_code` present when approved | same actor where SoD required; no active review; invalid outcome; missing disposition code on approval | `disposition_decision_recorded` | `review_status = DISPOSITION_DONE`; approved business effect becomes consumable if applicable |

Notes:

- this canonical command is used for both operational and quality-owned decisions
- ownership comes from exception type and policy, not from different command names

---

## 12. Completion, close, and reopen transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|---|
| COMPLETE-001 | `execution_status IN (RUNNING, PAUSED)`; `closure_status = OPEN` | `complete_execution` | execution started; no open downtime; no mandatory QC pending; no quality hold; no unresolved review; quantity completion rule satisfied **or** consumable approved effect exists (`ALLOW_SHORT_CLOSE` or `ALLOW_FORCE_COMPLETE`) | execution never started; open downtime; `quality_status = QC_HOLD`; mandatory QC pending; `review_status IN (REVIEW_REQUIRED, DECISION_PENDING)`; quantity rule unsatisfied and no approved effect | `execution_completed` | `execution_status = COMPLETED`; `closure_status = OPEN` |
| CLOSE-001 | `execution_status = COMPLETED`; `closure_status = OPEN` | `close_operation` | post-execution validations pass; no unresolved review; no unresolved QC requirement; minimum audit data present | validation missing; review/QC unresolved; record already closed | `operation_closed_at_station` | `closure_status = CLOSED` |
| REOPEN-001 | `closure_status = CLOSED` | `reopen_operation` | actor authorized; reopen reason present; downstream dependency check passes; approved effect exists where required (`ALLOW_REOPEN`) | reason missing; downstream non-reversible consumption; missing required approval | `operation_reopened` | `closure_status = OPEN`; `execution_status = PAUSED`; `review_status = NO_REVIEW`; reopen metadata incremented |

---

## 13. Invalid transition summary

The following are always rejected in canonical v1:

- any execution write command while `closure_status = CLOSED` except `reopen_operation`
- `resume_execution` while downtime remains open
- `complete_execution` while quality hold remains active
- `report_production` using free-form negative corrective delta
- `record_disposition_decision` without active review / exception target
- `record_disposition_decision` approval without `disposition_code`
- `close_operation` before execution is completed

---

## 14. Backend implementation notes

1. `approved_effects` should be derived server-side from approved disposition and exception type.
2. Approved effects must be consumable and auditable; they must not remain ambiguous flags forever.
3. `allowed_actions` returned to UI should come from backend state + policy evaluation.
4. If dispatch and release are hidden from this aggregate in implementation, treat them as projection-fed preconditions rather than station-owned writes.

