# Manufacturing Mode Profile Decision

Status: Active
Last updated: 2026-05-17

## Decision

FleziBCG is discrete-first for the pilot MVP, but it is not discrete-only.

The active runtime profile is:

- `DISCRETE`

The supported future profile is:

- `BATCH_PROCESS`

No batch/process runtime is implemented by this decision.

## Runtime Meaning

`DISCRETE` means the current execution model remains work-order/operation/station
oriented:

- production orders
- work orders
- operations
- station sessions
- equipment binding
- execution events
- quality measurements and holds

`BATCH_PROCESS` is a future profile marker only. It reserves product direction
for customers that require recipe, phase, batch/lot, process parameter,
weighing/dispensing, or eBR capabilities later.

## Profile Anchors

Manufacturing mode profile data is anchored at three levels:

- Tenant default: `tenants.manufacturing_mode_default`, default `DISCRETE`.
- Plant override: `plants.manufacturing_mode_profile`, nullable.
- Scope override: `scopes.manufacturing_mode_profile`, nullable.

Null plant/scope values mean "inherit from the broader context." Effective
profile resolution is reserved for a future service slice. No execution command
currently branches on this profile.

## Explicit Non-Implementation

This decision does not implement:

- Recipe runtime.
- Procedure runtime.
- ISA-88 phase state machine.
- Batch/lot execution context.
- Process parameter capture or enforcement.
- Weighing or dispensing workflows.
- Electronic batch record runtime.
- Continuous run orchestration.
- ERP, SCADA, historian, OPC UA, MQTT, or Sparkplug integration.

## Guardrails

- Do not rename current discrete execution concepts to batch/process concepts.
- Do not hard-code the product as discrete-only.
- Do not create fake batch/process screens or API responses.
- Do not let frontend infer manufacturing mode authority.
- Do not add batch/process runtime until the discrete pilot path is stable or a
  real customer pull-forward decision is documented.

## Future Unlock Criteria

Batch/process implementation may start when all of the following are true:

- A customer or pilot scenario requires batch/process behavior.
- A design slice defines the entity model for recipe, procedure, phase, and
  batch/lot context.
- Boundary with MMD, execution, quality, and compliance is documented.
- RBAC and approval requirements are defined.
- A migration and API contract are reviewed before implementation.

