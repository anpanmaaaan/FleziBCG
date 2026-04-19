# Station Execution Command and Event Contracts (Canonical v1)

Status: Authoritative implementation contract  
Owner: Product / Domain / Backend  
Depends on: `business-truth-station-execution.md`, `station-execution-state-matrix.md`

---

## 1. Purpose

This document defines the canonical command and event contracts for station execution.

It is the implementation contract for:

- command names
- event names
- common envelopes
- payload ownership
- canonical enums used by backend and clients
- idempotency and concurrency behavior

If another document uses older names such as `record_supervisor_decision`, `record_quality_disposition`, or `release_qc_hold` as canonical decision commands, this file takes precedence for canonical v1.

---

## 2. Canonical command set

### 2.1 Station session

- `open_station_session`
- `close_station_session`

### 2.2 Station execution

- `claim_operation`
- `start_execution`
- `pause_execution`
- `resume_execution`
- `report_production`
- `start_downtime`
- `end_downtime`
- `submit_qc_measurement`
- `complete_execution`
- `close_operation`
- `reopen_operation`

### 2.3 Review / exception

- `raise_exception`
- `record_disposition_decision`

Note: orchestration-owned commands such as dispatch and release are not part of this station execution command set.

---

## 3. Canonical event set

### 3.1 Session events

- `station_session_opened`
- `station_session_closed`

### 3.2 Execution events

- `operation_claimed`
- `execution_started`
- `execution_paused`
- `execution_resumed`
- `production_reported`
- `downtime_started`
- `downtime_ended`
- `qc_measurement_submitted`
- `qc_result_recorded`
- `qc_hold_applied`
- `execution_completed`
- `operation_closed_at_station`
- `operation_reopened`

### 3.3 Review / exception events

- `exception_raised`
- `disposition_decision_recorded`

### 3.4 Orchestration-fed precondition events visible in projections

- `operation_dispatched_to_station`
- `operation_released_to_execute`

These may appear in projection/event feeds, but they are owned by orchestration, not by station-execution writers.

---

## 4. Common command envelope

Every command must include a common envelope.

```json
{
  "command_id": "uuid",
  "command_name": "start_execution",
  "aggregate_id": "uuid",
  "tenant_id": "uuid",
  "scope": {
    "plant_id": "uuid",
    "area_id": "uuid",
    "line_id": "uuid",
    "station_id": "uuid"
  },
  "actor": {
    "user_id": "uuid",
    "role_codes": ["OPR"],
    "support_mode": false,
    "impersonated_user_id": null
  },
  "expected_version": 12,
  "occurred_at": "2026-04-19T08:00:00Z",
  "correlation_id": "uuid",
  "causation_id": "uuid-or-null",
  "payload": {}
}
```

### 4.1 Envelope rules

- `command_id` is required for idempotency
- `expected_version` is required for optimistic concurrency
- `occurred_at` is the client-supplied business occurrence timestamp, subject to policy validation
- backend may stamp additional server-received timestamps

---

## 5. Common event envelope

```json
{
  "event_id": "uuid",
  "event_name": "execution_started",
  "aggregate_id": "uuid",
  "tenant_id": "uuid",
  "scope": {
    "plant_id": "uuid",
    "area_id": "uuid",
    "line_id": "uuid",
    "station_id": "uuid"
  },
  "actor": {
    "user_id": "uuid",
    "role_codes": ["OPR"],
    "support_mode": false,
    "impersonated_user_id": null
  },
  "aggregate_version": 13,
  "occurred_at": "2026-04-19T08:00:03Z",
  "recorded_at": "2026-04-19T08:00:04Z",
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "payload": {}
}
```

### 5.1 Event envelope rules

- `aggregate_version` is assigned by backend
- `recorded_at` is backend-controlled
- event payload is immutable after persistence

---

## 6. Canonical enums

### 6.1 Review status enum

- `NO_REVIEW`
- `REVIEW_REQUIRED`
- `DECISION_PENDING`
- `DISPOSITION_DONE`

### 6.2 Closure status enum

- `OPEN`
- `CLOSED`

### 6.3 Decision outcome enum

- `APPROVED`
- `REJECTED`

### 6.4 Disposition code enum (canonical v1)

- `ALLOW_SHORT_CLOSE`
- `ALLOW_OVERRUN`
- `ALLOW_FORCE_COMPLETE`
- `ALLOW_REOPEN`
- `ALLOW_FORCE_RESUME`
- `ALLOW_BLOCK_OVERRIDE`
- `RELEASE_QC_HOLD`
- `ACCEPT_WITH_DEVIATION`
- `REQUIRE_RECHECK`
- `CONFIRM_SCRAP`
- `REJECT_REQUEST`

Notes:
- `REJECT_REQUEST` is allowed only when `decision_outcome = REJECTED` if the implementation wants an explicit rejection code.
- For simpler implementations, rejection may omit `disposition_code` entirely.

### 6.5 Exception type enum

- `SHORT_CLOSE_REQUEST`
- `OVERRUN_REQUEST`
- `FORCE_COMPLETE_REQUEST`
- `REOPEN_OPERATION_REQUEST`
- `FORCE_RESUME_REQUEST`
- `BLOCK_OVERRIDE_REQUEST`
- `QC_DEVIATION_ACCEPT_REQUEST`
- `QC_HOLD_RELEASE_REQUEST`
- `QC_RECHECK_REQUEST`
- `SCRAP_DISPOSITION_REQUEST`
- `SUPPORT_INTERVENTION_REQUEST`
- `BACKDATED_EVENT_REQUEST`

---

## 7. Command contracts

## 7.1 `open_station_session`

### Payload

```json
{
  "station_session_id": "uuid"
}
```

### Result event
- `station_session_opened`

---

## 7.2 `close_station_session`

### Payload

```json
{
  "station_session_id": "uuid",
  "reason_note": "optional"
}
```

### Result event
- `station_session_closed`

---

## 7.3 `claim_operation`

### Payload

```json
{
  "station_session_id": "uuid",
  "operation_id": "uuid"
}
```

### Result event
- `operation_claimed`

---

## 7.4 `start_execution`

### Payload

```json
{
  "station_session_id": "uuid",
  "operation_id": "uuid",
  "checklist_snapshot": null
}
```

### Result event
- `execution_started`

---

## 7.5 `pause_execution`

### Payload

```json
{
  "reason_code": "optional-policy-driven",
  "note": "optional"
}
```

### Result event
- `execution_paused`

---

## 7.6 `resume_execution`

### Payload

```json
{
  "note": "optional"
}
```

### Result event
- `execution_resumed`

---

## 7.7 `report_production`

### Payload

```json
{
  "good_qty_delta": 10,
  "ng_qty_delta": 1,
  "defect_reason_code": "DEFECT_A",
  "note": "optional"
}
```

### Contract rules

- deltas must be non-negative
- at least one delta must be greater than zero
- `defect_reason_code` may be mandatory when `ng_qty_delta > 0`
- canonical v1 does not allow free-form negative corrective delta

### Result event
- `production_reported`

---

## 7.8 `start_downtime`

### Payload

```json
{
  "downtime_id": "uuid",
  "reason_code": "WAIT_MATERIAL",
  "category_code": "UNPLANNED",
  "note": "optional"
}
```

### Result event
- `downtime_started`

---

## 7.9 `end_downtime`

### Payload

```json
{
  "downtime_id": "uuid",
  "note": "optional"
}
```

### Result event
- `downtime_ended`

---

## 7.10 `submit_qc_measurement`

### Payload

```json
{
  "sample_id": "uuid",
  "measurement_values": {
    "width": 10.2,
    "height": 5.1
  },
  "note": "optional"
}
```

### Result events
- `qc_measurement_submitted`
- followed by `qc_result_recorded` after backend evaluation

---

## 7.11 `complete_execution`

### Payload

```json
{
  "note": "optional"
}
```

### Result event
- `execution_completed`

---

## 7.12 `close_operation`

### Payload

```json
{
  "note": "optional"
}
```

### Result event
- `operation_closed_at_station`

---

## 7.13 `reopen_operation`

### Payload

```json
{
  "reason_code": "REOPEN_EXECUTION",
  "note": "required-reason-context"
}
```

### Result event
- `operation_reopened`

### Contract note

Backend increments and stamps:

- `reopen_count`
- `last_reopened_at`
- `last_reopened_by`

These are server-derived facts, not trusted client payload.

---

## 7.14 `raise_exception`

### Payload

```json
{
  "exception_id": "uuid",
  "exception_type_code": "SHORT_CLOSE_REQUEST",
  "reason_code": "SHORT_OUTPUT",
  "note": "required-or-optional-per-policy",
  "evidence": {
    "remaining_qty": 5
  }
}
```

### Result event
- `exception_raised`

---

## 7.15 `record_disposition_decision`

### Payload

```json
{
  "exception_id": "uuid",
  "decision_outcome": "APPROVED",
  "disposition_code": "ALLOW_SHORT_CLOSE",
  "note": "required decision rationale"
}
```

### Contract rules

- `exception_id` is required
- `decision_outcome` is required
- `disposition_code` is required when `decision_outcome = APPROVED`
- backend derives any `approved_effects`; client must not submit them as authoritative input
- backend validates actor ownership based on exception type and policy

### Result event
- `disposition_decision_recorded`

---

## 8. Event payload contracts

## 8.1 `production_reported`

```json
{
  "good_qty_delta": 10,
  "ng_qty_delta": 1,
  "defect_reason_code": "DEFECT_A",
  "reported_good_qty_total": 110,
  "reported_ng_qty_total": 3
}
```

Note: `accepted_good_qty_total` may be updated by projection logic after quality/disposition evaluation, not necessarily at the same moment as every production report.

---

## 8.2 `qc_result_recorded`

```json
{
  "sample_id": "uuid",
  "result_code": "FAIL",
  "quality_status_after": "QC_FAILED",
  "spec_rule_code": "WIDTH_RANGE"
}
```

---

## 8.3 `qc_hold_applied`

```json
{
  "hold_reason_code": "QC_FAIL_HARD_HOLD",
  "quality_status_after": "QC_HOLD",
  "review_status_after": "DECISION_PENDING",
  "blocks_execution": true
}
```

---

## 8.4 `exception_raised`

```json
{
  "exception_id": "uuid",
  "exception_type_code": "SHORT_CLOSE_REQUEST",
  "review_status_after": "DECISION_PENDING"
}
```

---

## 8.5 `disposition_decision_recorded`

```json
{
  "exception_id": "uuid",
  "exception_type_code": "SHORT_CLOSE_REQUEST",
  "decision_outcome": "APPROVED",
  "disposition_code": "ALLOW_SHORT_CLOSE",
  "approved_effects": ["ALLOW_SHORT_CLOSE"],
  "review_status_after": "DISPOSITION_DONE"
}
```

### Important ownership rule

`approved_effects` in event payload is **server-derived output**, not client-owned input.

---

## 8.6 `operation_reopened`

```json
{
  "reopen_count": 2,
  "last_reopened_at": "2026-04-19T10:15:00Z",
  "last_reopened_by": "uuid",
  "closure_status_after": "OPEN",
  "execution_status_after": "PAUSED"
}
```

---

## 9. Command result contract

Successful command result should at minimum include:

```json
{
  "command_id": "uuid",
  "status": "ACCEPTED",
  "aggregate_id": "uuid",
  "aggregate_version": 13,
  "primary_event_name": "execution_started"
}
```

Rejected result should at minimum include:

```json
{
  "command_id": "uuid",
  "status": "REJECTED",
  "error_code": "QUALITY_HOLD_ACTIVE",
  "message": "Execution cannot resume while quality hold is active."
}
```

---

## 10. Error families

Recommended top-level error families:

- `AUTH_*`
- `STATE_*`
- `POLICY_*`
- `CONCURRENCY_*`
- `VALIDATION_*`
- `NOT_FOUND_*`
- `SOD_*`

Examples:

- `STATE_CLOSED_RECORD`
- `STATE_QC_HOLD_ACTIVE`
- `STATE_DOWNTIME_OPEN`
- `POLICY_NEGATIVE_CORRECTION_NOT_ALLOWED`
- `SOD_REQUESTER_EQUALS_APPROVER`
- `VALIDATION_DISPOSITION_CODE_REQUIRED`

---

## 11. Idempotency and concurrency

### 11.1 Idempotency

If the same `command_id` is replayed with identical payload, backend should return the already-known result and must not emit duplicate events.

### 11.2 Optimistic concurrency

If `expected_version` is stale, backend rejects with concurrency error and does not mutate truth.

### 11.3 Event ordering

Within one aggregate, accepted events must be persisted in strict aggregate version order.

---

## 12. Canonical naming summary

Canonical v1 names are:

- command: `record_disposition_decision`
- event: `disposition_decision_recorded`
- review pending state: `DECISION_PENDING`
- closure states: `OPEN`, `CLOSED`
- reopen represented by event + metadata, not a `REOPENED` status

