# Station Execution State Matrix

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v4.1 | Hardening Task 2 alignment. Marked `ABORTED` as reserved/future-only, clarified P0 quality gate guard deferral, and made rework handling non-P0. |
| 2026-04-23 | v4.0 | Reworked matrix around session-owned execution and claim deprecation. |

## Status

**Canonical state matrix for current P0 Station Execution target.**

---

## 1. Target State Carriers

### 1.1 Runtime execution status — P0 active states

- `PLANNED`
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`

### 1.2 Reserved runtime status

- `ABORTED`

`ABORTED` is reserved/future-only in P0. No current P0 transition reaches `ABORTED`. It must not be implemented as reachable state unless an explicit governed `abort_operation` command is added.

### 1.3 Orthogonal dimension

- `closure_status`: `OPEN`, `CLOSED`

### 1.4 Deferred dimensions

- `quality_status`
- `review_status`
- fuller `dispatch_status`

---

## 2. Global Invariants

### INV-001 — Closed records reject execution writes

When `closure_status = CLOSED`, execution write commands are rejected except authorized reopen flow.

### INV-002 — One running execution per governing station/resource context

Implemented/target safe default.

### INV-003 — Open downtime blocks resume and completion

Implemented/target safe default.

### INV-004 — Active execution mutation requires valid station session context

Start/pause/resume/report/downtime/complete require valid session-owned context.

### INV-005 — Rework is not P0 runtime state

Rework is not represented as a P0 execution runtime state. Rework is deferred to Quality/Rework flow.

### INV-006 — Full quality-gated execution is deferred

P0 state matrix does not enforce full Acceptance Gate policy. P1 will add explicit quality-gate guard through backend-derived `allowed_actions`.

---

## 3. Session / Context Transitions

| ID | Current state | Command | Guard | Reject when | Event / effect | Next state |
|---|---|---|---|---|---|---|
| SS-OPEN-001 | no active station session | `open_station_session` | actor authenticated and authorized in scope | invalid station/resource context | `station_session_opened` | active station session |
| OP-ID-001 | active station session without operator | `identify_operator` | operator valid under policy | invalid/inactive operator | `operator_identified_at_station` | active station session with operator |
| EQ-BIND-001 | active station session | `bind_equipment` | equipment valid for station/resource policy | invalid equipment; out-of-scope equipment | `equipment_bound_to_station_session` | active station session with bound equipment |
| SS-CLOSE-001 | active station session | `close_station_session` | no active work would be orphaned | running/open work still owned by session | `station_session_closed` | no active station session |

---

## 4. Execution Transitions

| ID | Current state | Command | Guard | Reject when | Event / effect | Next state |
|---|---|---|---|---|---|---|
| START-001 | `status = PLANNED`; `closure_status = OPEN` | `start_execution` | actor authorized; valid station session; operator identified; equipment bound when required; no competing running execution | invalid state; closed record; missing session/operator/equipment context | `execution_started` | `IN_PROGRESS` |
| PAUSE-001 | `status = IN_PROGRESS`; `closure_status = OPEN` | `pause_execution` | actor authorized; valid ownership session | invalid state; closed record; missing session context | `execution_paused` | `PAUSED` |
| RESUME-001 | `status = PAUSED`; `closure_status = OPEN`; no open downtime | `resume_execution` | actor authorized; valid ownership session; no competing running execution | open downtime; invalid state; closed record; missing session context | `execution_resumed` | `IN_PROGRESS` |
| PROD-REP-001 | `status = IN_PROGRESS`; `closure_status = OPEN` | `report_production` | non-negative `good_delta`/`scrap_delta`; at least one delta > 0; valid ownership session | invalid delta; `rework_delta` supplied; invalid state; closed record; missing session context | `production_reported` | status unchanged |
| DT-START-001 | `status IN (IN_PROGRESS, PAUSED)`; `closure_status = OPEN`; no open downtime | `start_downtime` | valid ownership session; valid `reason_code` | downtime already open; invalid state; closed record; invalid/inactive reason | `downtime_started` | `BLOCKED` |
| DT-END-001 | open downtime exists; `closure_status = OPEN` | `end_downtime` | valid ownership session | no open downtime; closed record; missing session context | `downtime_ended` | `PAUSED` |
| COMPLETE-001 | `status = IN_PROGRESS`; `closure_status = OPEN`; no open downtime | `complete_execution` | actor authorized; valid ownership session | invalid state; closed record; open downtime; missing session context | `execution_completed` | `COMPLETED` + `OPEN` |

Quality gate note for `COMPLETE-001`:

```text
P0 does not include full Acceptance Gate guard in this transition.
When P1 quality-gated execution is enabled, complete/close/move-next must check backend-derived gate state and may reject with QUALITY_GATE_BLOCKED.
```

---

## 5. Closure Transitions

| ID | Current state | Command | Guard | Reject when | Event | Next state |
|---|---|---|---|---|---|
| CLOSE-001 | `status = COMPLETED`; `closure_status = OPEN` | `close_operation` | actor authorized under current phase rule; record completed | already closed; not completed; unauthorized | `operation_closed_at_station` | `closure_status = CLOSED` |
| REOPEN-001 | `closure_status = CLOSED` | `reopen_operation` | actor authorized under current phase rule; reason present; reopen path safe | reason missing; unauthorized | `operation_reopened` | `closure_status = OPEN`; runtime projection `PAUSED` |

---

## 6. Reserved ABORTED Branch

`ABORTED` remains reserved/future-only.

If a future `abort_operation` command is approved, this matrix must be updated with:

- allowed source states;
- authorization rule;
- reason requirement;
- quantity/material/quality impact;
- audit/approval policy;
- recovery/reopen behavior.

Until then, no implementation should emit `operation_aborted` or transition runtime status to `ABORTED`.

---

## 7. Transition Note

This matrix replaces claim-owned target semantics with session-owned target semantics.
Any remaining claim-owned behavior in current code is migration debt, not target matrix truth.

---

## Hardening Housekeeping v1.1 Amendment — Current Phase and BLOCKED Reason Context

### History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v4.2-amendment | Added explicit current-phase rule and canonical BLOCKED reason projection fields after CD Review 1 D17/D18 feedback. |

### Current-phase rule

This state matrix is the **P0 execution-core matrix**.

P0 state rules are authoritative only for the current Station Execution core:

```text
PLANNED / READY / RUNNING / PAUSED / BLOCKED / COMPLETED / CLOSED foundation
```

P0 does not enforce the full future state impact of:

- Acceptance Gate;
- nonconformance/deviation;
- material readiness;
- equipment calibration;
- backflush posting;
- ERP posting;
- APS recommendation;
- AI insight;
- compliance/e-record review.

When those modules are enabled in P1/P2, they must extend guards through backend policy and `allowed_actions` rather than changing the frontend only.

### BLOCKED is derived

`BLOCKED` is not a manually-entered generic state. It is derived from an active blocking condition.

Canonical block sources:

| `block_source` | Example `block_reason_code` | Phase |
|---|---|---|
| `downtime` | `DOWNTIME_OPEN` | P0 |
| `quality` | `QUALITY_HOLD`, `ACCEPTANCE_GATE_FAILED` | P1 |
| `material` | `MATERIAL_SHORTAGE`, `KIT_NOT_READY` | P1 |
| `equipment` | `EQUIPMENT_UNAVAILABLE`, `CALIBRATION_EXPIRED` | P1/P2 |
| `approval` | `APPROVAL_PENDING` | P1 |
| `system` | `INTEGRATION_BLOCK`, `POLICY_BLOCK` | P1/P2 |

Canonical BLOCKED projection fields:

```text
execution_status = BLOCKED
block_source
block_reason_code
block_reason_text
blocking_entity_type
blocking_entity_id
blocked_since
unblock_condition
```

P0 minimum requirement:

```text
if open downtime exists:
  execution_status = BLOCKED
  block_source = downtime
  block_reason_code = DOWNTIME_OPEN
```

Future modules may add new block sources, but they must not overload `BLOCKED` without a stable source/reason code.
