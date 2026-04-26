# Material Operations Domain

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v2.2 | Hardening Task 2 alignment. Clarified Backflush trigger timing and relationship between material consumption events and backflush consumption records. |
| 2026-04-23 | v2.0 | Expanded from placeholder to mode-neutral material domain framing. |

## Status

**Material operations domain overview.**

---

## 1. Purpose

Material Operations owns MOM-level material and WIP context:

- issue/return/transfer semantics;
- WIP/container movement where in scope;
- material availability/reservation snapshots for readiness;
- staging/kitting/component verification;
- consumption and production records;
- backflush consumption records;
- byproduct/rework/loss implications later.

Material Operations does not own ERP financial inventory truth or replace full WMS.

---

## 2. Design Rule

Material operations must stay compatible with both:

- discrete component issue and assembly flows;
- process/batch consumption, yield, weighing/dispensing, and charging flows.

For the explicit boundary against traceability, see `../../00_platform/material-traceability-vs-inventory-boundary.md`.

---

## 3. Backflush Boundary

Backflush is cross-domain:

| Step | Owner |
|---|---|
| Define rule | Manufacturing Master Data |
| Trigger event | Execution |
| Record material consumption/backflush | Material Operations / Inventory/WIP |
| Link input/output genealogy | Traceability |
| Post consumption summary | Integration |
| Own financial inventory transaction | ERP |

Backflush must not be implemented as a pure Station Execution command.

---

## 4. Backflush Trigger Timing

Canonical trigger event types:

- `quantity_reported`
- `operation_completed`
- `operation_closed`

Recommended default:

```text
quantity_reported -> preferred when consumption should follow production reporting
operation_completed -> acceptable when consumption should happen once per operation completion
operation_closed -> allowed but must be used carefully to avoid late consumption surprises
```

Material domain flow:

```text
quantity_reported / operation_completed / operation_closed
→ apply backflush rule
→ create backflush consumption record
→ emit material consumption event
→ create traceability genealogy link where lot/batch is known
→ create ERP consumption posting request if integration is enabled
```

---

## 5. Material Consumption Event vs Backflush Record

Canonical relationship:

```text
inv.backflush_consumption_records = enriched operational transaction record
inv.material_consumption_events = append-only fact/event emitted from manual or backflush consumption
```

Required linkage:

```text
inv.backflush_consumption_records.material_consumption_event_id
  -> inv.material_consumption_events.id
```

If the implementation stores material consumption events as an event table rather than a relational entity table, the linkage may be carried as:

```text
material_consumption_events.payload.backflush_record_id
backflush_consumption_records.source_event_id
```

But the direction must be explicit and testable.

---

## 6. P0 / P1 Boundary

P0 Station Execution may record quantity and downtime without material consumption automation.

P1 adds:

- material readiness;
- staging/kitting;
- backflush rules;
- backflush records;
- ERP consumption posting request/result.
