# Material / Traceability / Inventory Boundary Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.0 | Added explicit source-of-truth boundary between traceability and inventory/WIP domains. |
| 2026-04-23 | v1.1 | Added consistency, idempotency, and correlation guidance for execution-to-inventory linkage. |

Status: Canonical cross-domain boundary note.

## 1. Purpose

This document clarifies the source-of-truth split between:
- Execution
- Traceability & Material Operations
- Inventory / WIP / Material Flow Context

## 2. Boundary summary

### Execution owns
- operational execution events
- reported quantity events
- downtime and runtime events
- execution-context facts about what work is being performed

### Traceability owns
- genealogy graph
- lot/batch/serial linkage
- backward/forward trace relationships
- linkage between execution facts, material identity, and quality outcomes

### Inventory / WIP / Material Flow owns
- stock/WIP position
- material movement transactions
- issue / consume / return / transfer transaction truth
- buffer/container/WIP location visibility where in scope

## 3. Practical split

### Consumption event
- Execution may record that consumption occurred in operational context
- Inventory/Material Flow owns the actual movement transaction truth
- Traceability owns the genealogy/lot linkage created from that transaction and execution context

### Produced quantity
- Execution owns reported production facts
- Inventory/Material Flow owns resulting operational stock/WIP position where modeled
- Traceability owns produced lot/batch/serial linkage

### Accepted good
- Quality and execution determine whether output is accepted
- Inventory/WIP reflects accepted operational position when applicable
- Traceability links accepted output identity to its genealogy

## 4. Consistency and idempotency rule

Where execution events lead to inventory movements or traceability linkage, the system must preserve explicit correlation between the operational event and the downstream transaction.

### Minimum rule
- inventory movement transactions should reference an execution-side correlation key
- suitable examples include:
  - `execution_event_id`
  - `operation_execution_id`
  - `material_movement_ref`
  - another documented idempotency/correlation identifier

### Transaction boundary rule
- within the same service boundary, event append + movement transaction creation + projection update should be handled within an explicit service-layer transaction where applicable
- across external boundaries or adjunct services, do not assume distributed atomicity by default
- instead, use explicit correlation ids, idempotency keys, and reconciliation-safe retry behavior

### Governance note
This aligns with coding rules that require transactional behavior and idempotency expectations to be documented for write paths that append events or update critical truth.

## 5. Rule

Do not let the same concept become authoritative in two modules at once.
When in doubt:
- movements and balances -> Inventory / WIP / Material Flow
- genealogy and trace relationships -> Traceability
- runtime operational mutation -> Execution
