# Design Gap Report

## Gap ID
DG-P0B-PRODUCT-FOUNDATION-001

## Blocked slice
P0-B Product Foundation

## Missing contract
Authoritative design documents define product-definition ownership and boundaries, and a minimal executable product contract is now proposed in:
- docs/design/02_domain/product_definition/product-foundation-contract.md

Human decisions have accepted the P0-B candidate event names and the minimal executable contract for implementation.

## Why it blocks implementation
The original design gap is resolved for P0-B Product Foundation scope. Implementation can proceed under the approved contract while event registry finalization and broader canonical data-doc sync remain follow-up governance tasks.

## Minimal design proposal
Minimal Product Foundation contract approved with:
- Product aggregate identity and lifecycle fields
- Versioning decision for P0-B scope
- Tenant ownership and scope policy
- Command set and transition contract
- Canonical event names marked CANONICAL_FOR_P0_B
- Baseline invariants and test matrix for implementation gate

## Options
1. Keep product foundation blocked and continue only reference/master-data seams that are already design-backed.
2. Approve a minimal ADR that defines the missing Product Foundation contract and event naming.
3. Expand design docs for full product+routing+resource requirement contract before further P0-B coding.

## Recommended decision
Option 2. Approve a minimal Product Foundation ADR and event registry entries so the next P0-B slice can proceed without inventing behavior.

## Impacted modules
- backend/app/models (future product/routing models)
- backend/app/services (future product/routing services)
- backend/app/api/v1 (future product/routing routes)
- docs/design/02_domain/product_definition/
- docs/design/05_application/ (API/event catalog alignment)
- docs/implementation/ (slice plan and verification updates)

## Required human decision
Decision applied on 2026-04-29:
- Product Foundation contract approved for P0-B implementation.
- Product event names finalized as CANONICAL_FOR_P0_B.
- P0-B implementation is not blocked by missing 09_data docs; contract is temporary executable source of truth.

## Status
APPROVED_FOR_P0_B_IMPLEMENTATION

---

## Gap ID
DG-P0B-RESOURCE-REQUIREMENT-001

## Blocked slice
P0-B-03 Resource Requirement Mapping

## Missing contract summary
P0-B-03 implementation was blocked by Hard Mode MOM v3 due to missing executable, slice-specific contract semantics for Resource Requirement Mapping (aggregate fields, uniqueness, lifecycle mutation gates, event payload minimum, API surface, and invariants).

New proposed contract:
- docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md

## Decisions applied
- Resource Requirement Mapping defined as Manufacturing Master Data only; no execution/dispatch/reservation/planning truth.
- Aggregate fields finalized for P0-B: requirement_id, tenant_id, routing_id, operation_id, required_resource_type, required_capability_code, quantity_required, notes, metadata_json, created_at, updated_at.
- required_resource_type enum finalized for P0-B: WORK_CENTER, STATION_CAPABILITY, EQUIPMENT_CAPABILITY, OPERATOR_SKILL, TOOLING.
- required_capability_code mandatory in P0-B; tenant-scoped reference code; capability master table not required in this slice.
- quantity_required finalized as positive integer with default 1.
- Uniqueness finalized: tenant_id + operation_id + required_resource_type + required_capability_code.
- Parent routing lifecycle governs mutation: DRAFT allow create/update/remove; RELEASED and RETIRED reject mutation.
- Delete policy finalized as hard delete only in DRAFT.
- Canonical event names finalized for this phase:
	- RESOURCE_REQUIREMENT.CREATED
	- RESOURCE_REQUIREMENT.UPDATED
	- RESOURCE_REQUIREMENT.REMOVED
- Event status finalized for this phase:
	- CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT

---

## Gap ID
DG-P0C01-ROUTING-FK-001

## Blocked slice
P0-C-01 Work Order / Operation Foundation Alignment (documentation only, not blocking P0-C-01 tests)

## Missing contract
`ProductionOrder.route_id` is a loose `String(64)` field that semantically references a `Routing.routing_id` but has no database FK constraint. There is no `routing_operation_id` on the `Operation` model to formally link execution operations to `RoutingOperation` steps.

## Why this is a gap
The routing foundation contract (implemented in P0-B-02) establishes `Routing.routing_id` (str PK) and `RoutingOperation.operation_id` (str PK) as authoritative identity keys. The execution models (`ProductionOrder`, `WorkOrder`, `Operation`) predate P0-B-02 and carry routing context only as unvalidated string fields. Cross-domain integrity between routing definitions and execution instances is currently not enforced at the database level.

## Risk classification
LOW for P0-C execution behavior. The loose string fields do not affect runtime execution state machine correctness. They only affect routing traceability and execution-to-master-data linkage.

## Recommended resolution
Future P0-C slice (after P0-C-04 Session Ownership Alignment):
- Add nullable `routing_id` column to `ProductionOrder` as String FK referencing `routings.routing_id`.
- Add nullable `routing_operation_id` column to `Operation` as String FK referencing `routing_operations.operation_id`.
- Both columns nullable to preserve existing execution data without migration failures.
- Requires Alembic migration; classify as schema migration slice.

## Impacted modules
- backend/app/models/master.py (ProductionOrder, Operation)
- backend/scripts/migrations/ (new migration file)
- backend/alembic/versions/ (new revision)

## Status
DOCUMENTED_FOR_FUTURE_SLICE — not blocking P0-C execution baseline
- Hard Mode MOM v3 gate artifacts included in the contract:
	- Event Map
	- Invariant Map
	- Lifecycle Map
	- Test Matrix
	- Implementation-readiness verdict

## Remaining open questions
- None blocking P0-B-03 minimum scope.
- Follow-up governance item after implementation: canonicalize resource requirement events via dedicated registry finalization process.

## Recommended next implementation slice
Proceed with P0-B-03 backend implementation as a test-first vertical slice only:
- model/table
- schema
- repository
- service
- API routes
- SQL migration (0016_resource_requirements.sql)
- focused tests and regression verification

## Status
APPROVED_FOR_P0_B_IMPLEMENTATION