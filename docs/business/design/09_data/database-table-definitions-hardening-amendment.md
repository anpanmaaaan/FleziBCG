# Database Table Definitions — Hardening Amendment

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Hardening Task 2 amendment for backflush/material consumption relationship. |

## Status

**Amendment to `docs/design/09_data/database-table-definitions.md`.**

Use this amendment to patch Database Design v1.2 without expanding implementation scope.

---

## 1. Backflush Consumption Relationship

The relationship between `inv.backflush_consumption_records` and `inv.material_consumption_events` must be explicit.

Canonical interpretation:

| Table | Role |
|---|---|
| `inv.backflush_consumption_records` | Enriched operational transaction record created by applying a backflush rule. Stores calculated quantity, component, posting status, and ERP posting reference. |
| `inv.material_consumption_events` | Append-only material consumption fact emitted for manual or backflush-derived consumption. |

---

## 2. Required Linkage

Preferred relational linkage:

```text
inv.backflush_consumption_records.material_consumption_event_id
  -> inv.material_consumption_events.id
```

If `inv.material_consumption_events` is implemented as event-standard table and not as a relational transaction table, then linkage must be carried with both sides traceable:

```text
inv.backflush_consumption_records.source_event_id
  -> material consumption event id

inv.material_consumption_events.payload.backflush_record_id
  -> inv.backflush_consumption_records.id
```

Do not leave the relationship implicit.

---

## 3. Updated `inv.backflush_consumption_records` Logical Definition

Add this column:

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `material_consumption_event_id` | `uuid` | No | FK | Link to emitted material consumption event/fact when implementation stores consumption event as relational row. |

---

## 4. Backflush Trigger Enum Alignment

Canonical `trigger_event_type` values:

```text
quantity_reported
operation_completed
operation_closed
```

`operation_closed` is allowed but should be used carefully. It can create late consumption surprises if operators expect consumption at reporting/completion time.

---

## 5. Idempotency Requirement

Backflush record creation must be idempotent per semantic trigger.

Recommended idempotency key shape:

```text
tenant_id:operation_id:backflush_rule_id:trigger_event_id
```

ERP posting must use a separate posting idempotency key so retry does not duplicate ERP financial/inventory posting.
