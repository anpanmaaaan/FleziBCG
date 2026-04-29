# Routing Foundation Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial P0-B routing foundation draft contract (doc-only, no implementation). |
| 2026-04-29 | v1.1 | Coverage review completed; marked READY_FOR_HUMAN_REVIEW_BEFORE_IMPLEMENTATION with explicit non-implementation boundary. |

Status: READY_FOR_HUMAN_REVIEW_BEFORE_IMPLEMENTATION.

## 1. Purpose

Define the minimum routing foundation contract for P0-B without expanding into execution-dispatch, recipe, or planning systems.

## 2. P0-B Routing Aggregate (Minimum)

Required fields:
- routing_id
- tenant_id
- product_id
- routing_code
- routing_name
- lifecycle_status
- operations sequence

Field intent:
- routing_id: immutable routing identity key.
- tenant_id: tenant ownership and isolation boundary.
- product_id: product linkage key for routing applicability.
- routing_code: business key, unique inside tenant.
- routing_name: display name.
- lifecycle_status: routing lifecycle state machine field.
- operations sequence: ordered list of operation steps for this routing.

## 3. Operations Sequence (P0-B)

Minimum sequence structure per operation item:
- operation_id
- operation_code
- operation_name
- sequence_no
- standard_cycle_time (optional)
- required_resource_type (optional)

P0-B sequence rules:
- sequence_no must be unique within a routing.
- sequence_no ordering is authoritative for operation order.
- no parallel branch semantics in P0-B.

## 4. Allowed Commands

- create_routing
- update_routing
- add_routing_operation
- update_routing_operation
- remove_routing_operation
- release_routing
- retire_routing

## 5. Lifecycle States

Canonical P0-B states:
- DRAFT
- RELEASED
- RETIRED

State semantics:
- DRAFT: routing and operation sequence are editable.
- RELEASED: routing is consumable by downstream linkage/read models; structural edits are restricted.
- RETIRED: routing is no longer available for new downstream linkage.

## 6. State Transition Contract

- create_routing: creates routing in DRAFT.
- update_routing: allowed in DRAFT; restricted in RELEASED; rejected in RETIRED.
- add/update/remove operation: allowed in DRAFT; rejected in RELEASED and RETIRED for P0-B.
- release_routing: DRAFT to RELEASED.
- retire_routing: DRAFT or RELEASED to RETIRED.

## 7. Event Contract (Candidate for P0-B)

Event naming status for routing in this draft:
- CANDIDATE_FOR_P0_B

Candidate events:
- ROUTING.CREATED
- ROUTING.UPDATED
- ROUTING.OPERATION_ADDED
- ROUTING.OPERATION_UPDATED
- ROUTING.OPERATION_REMOVED
- ROUTING.RELEASED
- ROUTING.RETIRED

Minimum event payload:
- tenant_id
- actor_user_id
- routing_id
- routing_code
- product_id
- lifecycle_status
- changed_fields
- occurred_at

## 8. Invariants

Mandatory invariants:
- routing_code must be unique per tenant.
- routing is tenant-owned and tenant-scoped for all reads/writes.
- product_id must reference a product in the same tenant.
- operations sequence_no values are unique within routing.
- RELEASED routing structural updates are rejected in P0-B.
- RETIRED routing cannot be newly linked downstream.

Structural fields for RELEASED immutability in P0-B:
- routing_code
- product_id
- operations sequence

## 9. API Surface (P0-B Minimum)

Read:
- GET /routings
- GET /routings/{routing_id}

Write:
- POST /routings
- PATCH /routings/{routing_id}
- POST /routings/{routing_id}/operations
- PATCH /routings/{routing_id}/operations/{operation_id}
- DELETE /routings/{routing_id}/operations/{operation_id}
- POST /routings/{routing_id}/release
- POST /routings/{routing_id}/retire

API behavior notes:
- All endpoints are tenant-scoped.
- Cross-tenant detail reads return 404 to avoid existence leakage.
- Lifecycle transitions are server-governed.

## 10. Explicit Exclusions

Excluded from this contract:
- BOM
- recipe/ISA-88
- advanced versioning
- APS
- Backflush
- ERP sync
- Acceptance Gate
- plant-specific execution dispatch logic

## 11. Coverage Review Verdict

Coverage check against requested minimums:
- routing identity: covered
- product linkage: covered
- lifecycle states: covered
- operation sequence model: covered
- release/retire commands: covered
- event candidates: covered
- invariants: covered
- API surface: covered
- explicit exclusions: covered

Verdict: READY_FOR_HUMAN_REVIEW_BEFORE_IMPLEMENTATION.

## 12. Implementation Boundary

This file is a design draft contract only.

No routing code implementation, migration, or API delivery is included by this document.
