# Event Schema Registry

Status: Authoritative event schema registry  
Scope: Cross-domain event naming and payload schema intent  
Depends on:
- `docs/system/mes-business-logic-v1.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `domain-contracts-execution.md`
- `quality-domain-contracts.md`

This document defines the canonical event registry for MOM Lite.

It is authoritative for:
- canonical event names
- minimum payload expectations
- event field semantics
- domain ownership of event families
- event compatibility rules

It is not:
- the event transport implementation detail
- the projection schema
- the API request contract

---

## 1. Purpose

The platform is event-driven.
To keep execution and future MOM domains consistent, event vocabulary must be:

- stable
- explicit
- append-only
- auditable
- machine-readable

This registry prevents:
- mixed event naming
- internal alias drift
- frontend/backend contract confusion
- analytics/AI consuming inconsistent event families

---

## 2. Event registry principles

### ESR-001 — Canonical event names are business-facing truth
Storage internals may temporarily carry legacy/internal names, but canonical names in this file are the contract target.

### ESR-002 — Events are facts, not commands
Events represent something that happened.
They must not be named as intent.

### ESR-003 — Events are append-only
No destructive update or rewrite of already-persisted business events.

### ESR-004 — Event payload must be minimally sufficient
Each event must carry enough data to support:
- audit
- projection rebuild
- domain reasoning
- cross-service extraction later

### ESR-005 — Event names are lower-case dot notation
Format:
`<domain>.<fact>`

Examples:
- `execution.started`
- `execution.completed`
- `quality.qc_result_recorded`

---

## 3. Common event envelope

All business events should conceptually carry this envelope:

```json
{
  "event_id": "uuid",
  "event_name": "execution.started",
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
  "aggregate_version": 3,
  "occurred_at": "2026-04-22T09:00:00Z",
  "recorded_at": "2026-04-22T09:00:01Z",
  "correlation_id": "uuid",
  "causation_id": "uuid-or-null",
  "payload": {}
}
```

---

## 4. Envelope field semantics

### `event_id`
Unique immutable event identifier.

### `event_name`
Canonical business-facing event name from this registry.

### `aggregate_id`
Primary aggregate identity for replay/ordering.

### `tenant_id`
Tenant boundary.

### `scope`
Resolved scope context for audit and isolation.

### `actor`
Resolved acting principal context.

### `aggregate_version`
Monotonic per aggregate.

### `occurred_at`
Business occurrence timestamp.

### `recorded_at`
Persistence timestamp.

### `correlation_id`
Links related events in one flow/request.

### `causation_id`
References parent command/event where relevant.

### `payload`
Event-specific facts only.

---

## 5. Execution event family

## 5.1 `execution.claimed`

### Meaning
Operation execution was claimed by an actor.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "station_id": "uuid",
  "claimed_by": "uuid"
}
```

---

## 5.2 `execution.released`

### Meaning
A previously claimed safe-releasable execution context was released.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "station_id": "uuid",
  "released_by": "uuid"
}
```

---

## 5.3 `execution.started`

### Meaning
Execution entered running state.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "runtime_status_after": "IN_PROGRESS"
}
```

---

## 5.4 `execution.paused`

### Meaning
Execution moved from running to paused.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "runtime_status_after": "PAUSED"
}
```

---

## 5.5 `execution.resumed`

### Meaning
Execution moved from paused to running.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "runtime_status_after": "IN_PROGRESS"
}
```

---

## 5.6 `execution.completed`

### Meaning
Execution reached completed state.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "runtime_status_after": "COMPLETED"
}
```

---

## 5.7 `execution.closed`

### Meaning
Completed execution record was business-closed.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "closure_status_after": "CLOSED",
  "note": "optional"
}
```

---

## 5.8 `execution.reopened`

### Meaning
Closed execution record was reopened.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "closure_status_after": "OPEN",
  "runtime_status_after": "PAUSED",
  "reason": "required reason",
  "reopen_count": 2
}
```

---

## 5.9 `execution.production_reported`

### Meaning
Production delta was reported.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "good_qty_delta": 5,
  "scrap_qty_delta": 1
}
```

---

## 5.10 `execution.downtime_started`

### Meaning
Downtime interval opened.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "reason_code": "MECH_STOP"
}
```

---

## 5.11 `execution.downtime_ended`

### Meaning
Downtime interval closed.

### Minimum payload
```json
{
  "operation_execution_id": "uuid"
}
```

---

## 6. Quality event family

## 6.1 `quality.qc_measurement_submitted`

### Meaning
Measurement payload was submitted for QC evaluation.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "sample_id": "uuid",
  "inspection_template_id": "uuid",
  "measurement_values": [
    {
      "item_code": "WIDTH",
      "input_type": "NUMERIC",
      "numeric_value": 10.2
    }
  ]
}
```

---

## 6.2 `quality.qc_result_recorded`

### Meaning
Backend evaluated submitted measurement and recorded QC result.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "sample_id": "uuid",
  "result_code": "FAIL",
  "failed_item_codes": ["WIDTH"],
  "quality_status_after": "QC_FAILED"
}
```

---

## 6.3 `quality.qc_hold_applied`

### Meaning
QC failure caused hold state.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "sample_id": "uuid",
  "quality_status_after": "QC_HOLD",
  "review_status_after": "DECISION_PENDING"
}
```

---

## 6.4 `quality.exception_raised`

### Meaning
An explicit quality/governed review target was raised.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "exception_id": "uuid",
  "exception_type_code": "QC_HOLD_RELEASE_REQUEST"
}
```

---

## 6.5 `quality.disposition_decision_recorded`

### Meaning
Authorized disposition decision was recorded for a quality/review target.

### Minimum payload
```json
{
  "operation_execution_id": "uuid",
  "exception_id": "uuid",
  "decision_outcome": "APPROVED",
  "disposition_code": "RELEASE_QC_HOLD",
  "quality_status_after": "QC_PASSED",
  "review_status_after": "DISPOSITION_DONE"
}
```

---

## 7. Auth / governance event family

These event families may already exist elsewhere or be built later, but the canonical naming style is reserved here.

### Examples
- `auth.logged_in`
- `auth.logged_out`
- `auth.logout_all_requested`
- `session.revoked`
- `approval.requested`
- `approval.decided`
- `impersonation.started`
- `impersonation.ended`

This file does not yet define full minimum payloads for all governance families unless they become active implementation scope.

---

## 8. Payload schema rules

### ESR-PAY-001 — Payload uses canonical field names
Use:
- `runtime_status_after`
- `closure_status_after`
- `quality_status_after`
- `review_status_after`

Do not use one generic `status_after`.

### ESR-PAY-002 — Quantities are explicit
Use:
- `good_qty_delta`
- `scrap_qty_delta`
- `accepted_good_qty_after` only when truly needed

### ESR-PAY-003 — Event payload contains facts, not labels
No localized UI labels in event payload.

### ESR-PAY-004 — Optional fields must remain additive
Breaking payload change requires architecture/contract PR.

---

## 9. Compatibility rules

### Additive allowed
- adding optional payload fields
- adding new event families

### Breaking
- renaming event_name
- removing required payload field
- changing field semantics
- changing canonical enum vocabulary

Breaking changes require:
- architecture/contract PR
- registry update
- impacted docs update
- migration note if persisted events are affected

---

## 10. Forbidden patterns

- mixed naming styles (`execution_started` in one place, `execution.started` in another as canonical peers)
- UI labels in payload
- overloaded generic event names like `updated`, `changed`, `handled`
- event payload that hides critical domain facts behind generic blobs
- rewriting historical event payload semantics silently

---

## 11. Current implementation debt note

Current codebase may still carry mixed internal or legacy event naming in places for Station Execution.  
This registry defines the canonical target naming and should be used for:
- new features
- doc truth
- future migration/cleanup
- AI/analytics integration
