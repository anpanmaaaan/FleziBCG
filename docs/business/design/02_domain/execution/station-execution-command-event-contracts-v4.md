# Station Execution Command and Event Contracts

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v4.1 | Hardening Task 2 alignment. Clarified P0 production reporting is good/scrap only; rework is deferred to P1 Quality/Rework flow. Clarified ABORTED is reserved/future-only and quality-gated execution is design-now-build-later. |
| 2026-04-23 | v4.0 | Reworked contracts for session-owned execution and claim deprecation. |

## Status

**Canonical Station Execution command/event contract for current P0 target.**

This file is scoped to Station Execution P0. It does not define full Quality Gate, Backflush, Traceability, ERP posting, or Rework lifecycle.

---

## 1. Target Command Set

### 1.1 Session / context commands

- `open_station_session`
- `identify_operator`
- `bind_equipment`
- `close_station_session`

### 1.2 Execution commands

- `start_execution`
- `pause_execution`
- `resume_execution`
- `report_production`
- `start_downtime`
- `end_downtime`
- `complete_execution`
- `close_operation`
- `reopen_operation`

### 1.3 Reserved / future commands

The following commands are **not P0 target commands**:

- `abort_operation`
- `report_rework_quantity`
- `create_rework_operation`
- `execute_acceptance_gate`
- `trigger_backflush_posting`

These may be introduced in P1/P2 through Quality, Rework, Material, Integration, or governed exception flows.

---

## 2. Migration Note

`claim_operation` and related claim semantics are deprecated from the target model.
They may continue to exist temporarily in current code as compatibility debt during migration.

Target execution ownership is session-owned.

---

## 3. Canonical Event Intent

- `station_session_opened`
- `operator_identified_at_station`
- `equipment_bound_to_station_session`
- `execution_started`
- `execution_paused`
- `execution_resumed`
- `production_reported`
- `downtime_started`
- `downtime_ended`
- `execution_completed`
- `operation_closed_at_station`
- `operation_reopened`
- `station_session_closed`

Reserved/future event families:

- `operation_aborted`
- `rework_requested`
- `rework_operation_created`
- `acceptance_gate_evaluated`
- `backflush_consumption_recorded`

---

## 4. Payload / Contract Truths

### 4.1 `start_execution`

Backend resolves effective operator/resource context from the active station session.

### 4.2 `report_production`

P0 body remains discrete-first for Station Execution:

- `good_delta`
- `scrap_delta`
- optional `note` / `comment` under policy

P0 explicitly does **not** accept `rework_delta`.

Reason:

- rework requires lifecycle semantics such as disposition, rework instruction, rework routing, genealogy implication, and possible approval;
- P0 Station Execution only records good/scrap production deltas;
- rework belongs to P1/P2 Quality/Rework flow.

Canonical P0 validation:

```text
non-negative good_delta and scrap_delta
at least one of good_delta or scrap_delta > 0
operation is writable
valid session-owned context
```

### 4.3 `start_downtime`

Body:

- `reason_code`
- optional comment when policy requires

### 4.4 `reopen_operation`

Body:

- `reason`

### 4.5 `abort_operation`

`abort_operation` is **reserved/future-only**.

If introduced later, it must be a governed command requiring at minimum:

- privileged authorization;
- reason code;
- audit trail;
- policy decision about quantity/material/quality implications;
- optional approval depending on tenant policy.

---

## 5. Quality Gate Interaction

P0 Station Execution does not implement full Acceptance Gate enforcement in this contract.

Current rule:

```text
Quality Lite may influence operation projections and visibility.
Full Quality-Gated Execution is P1 design-now-build-later.
```

When P1 Acceptance Gate is enabled, `complete_execution`, `close_operation`, WIP movement, and output release must include backend-derived quality gate guards through `allowed_actions`.

Station Execution must not calculate quality pass/fail/hold locally.

---

## 6. Error-Family Expectations

- `STATE_INVALID_TRANSITION`
- `STATE_CLOSED_RECORD`
- `SESSION_REQUIRED`
- `OPERATOR_IDENTIFICATION_REQUIRED`
- `EQUIPMENT_BINDING_REQUIRED`
- `FORBIDDEN`
- `REASON_CODE_INVALID`
- `QUANTITY_DELTA_INVALID`
- `REWORK_NOT_SUPPORTED_IN_P0`
- `QUALITY_GATE_BLOCKED` — P1 when quality-gated execution is enabled

---

## Hardening Housekeeping v1.1 Amendment — Current Phase and BLOCKED Reason Context

### History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v4.2-amendment | Added current-phase rule and BLOCKED reason projection contract after CD Review 1 D17/D18 feedback. |

### Current-phase rule

Station Execution v4 is the **P0 execution-core baseline**.

Current P0 scope includes:

- station session / ownership context;
- operation start / pause / resume;
- quantity report with `good_delta` and `scrap_delta` only;
- downtime start/end;
- complete / close / reopen foundation;
- event history and backend-derived allowed actions.

Current P0 scope explicitly does **not** include full implementations of:

- Acceptance Gate enforcement;
- rework lifecycle;
- nonconformance/deviation workflow;
- material readiness blocking;
- backflush execution;
- ERP posting;
- APS dispatch optimization;
- AI recommendations;
- Digital Twin mutation.

If a future domain influences execution, it must do so through backend-owned state, projection, policy, and `allowed_actions`, not frontend-only checks.

### BLOCKED reason projection contract

`BLOCKED` is a derived operational state. It must not be treated as a single undifferentiated cause.

When an operation is projected as `BLOCKED`, the operation detail/read model should expose the following context where available:

| Field | Required in P0? | Description |
|---|---:|---|
| `block_source` | Yes when blocked | Source domain causing block, e.g. `downtime`, `quality`, `material`, `equipment`, `approval`, `system`. |
| `block_reason_code` | Yes when blocked | Stable machine-readable reason code. |
| `block_reason_text` | Optional | Human-readable localized/display reason. |
| `blocking_entity_type` | Optional | Entity type causing block, e.g. `downtime_event`, `quality_hold`, `material_shortage`, `equipment_status`. |
| `blocking_entity_id` | Optional | Entity ID causing block. |
| `blocked_since` | Optional | Timestamp when block started. |
| `unblock_condition` | Optional | Backend-owned description of what must happen to unblock. |

P0 minimum:

```text
BLOCKED due to open downtime:
  block_source = downtime
  block_reason_code = DOWNTIME_OPEN
  blocking_entity_type = downtime_event
```

Future examples:

```text
BLOCKED due to quality hold:
  block_source = quality
  block_reason_code = QUALITY_HOLD

BLOCKED due to missing material:
  block_source = material
  block_reason_code = MATERIAL_SHORTAGE

BLOCKED due to equipment unavailable:
  block_source = equipment
  block_reason_code = EQUIPMENT_UNAVAILABLE
```

### Command implication

Commands must use backend domain guards and projected `allowed_actions`. Frontend may display block reason context, but must not infer unlock permissions locally.
