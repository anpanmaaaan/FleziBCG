# Resource Requirement Mapping Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial executable P0-B-03 Resource Requirement Mapping contract to unblock implementation planning. |

Status: IMPLEMENTED_AND_CANONICAL_FOR_P0_B.

## 1. Purpose

Define the minimum executable contract for P0-B-03 Resource Requirement Mapping.

Resource Requirement Mapping is Manufacturing Master Data. It defines what capability category a routing operation requires.

It does not:
- assign a concrete station, equipment, or operator
- dispatch work
- reserve capacity
- create execution truth

## 2. Aggregate (P0-B Minimum)

Required fields:
- requirement_id
- tenant_id
- routing_id
- operation_id
- required_resource_type
- required_capability_code
- quantity_required
- notes
- metadata_json
- created_at
- updated_at

Field intent:
- requirement_id: immutable requirement identity key.
- tenant_id: tenant ownership and isolation boundary.
- routing_id: parent routing linkage key.
- operation_id: parent routing operation linkage key.
- required_resource_type: capability category required for operation execution readiness.
- required_capability_code: tenant-scoped capability/reference code.
- quantity_required: minimum required quantity for the capability category.
- notes: optional human-readable note.
- metadata_json: optional structured extension payload.
- created_at/updated_at: audit timestamps.

## 3. required_resource_type (P0-B Enum)

P0-B allowed values:
- WORK_CENTER
- STATION_CAPABILITY
- EQUIPMENT_CAPABILITY
- OPERATOR_SKILL
- TOOLING

Clarification:
- These values classify requirement type only.
- They are not concrete assignment fields.

## 4. required_capability_code

Definition:
- tenant-scoped capability/reference code required by the operation.

Examples:
- WELDING_CELL
- TORQUE_TOOL
- PAINT_BOOTH
- FINAL_INSPECTION
- CERTIFIED_OPERATOR

P0-B rule:
- required_capability_code is mandatory.
- If no capability master exists in this phase, validate only required presence and format semantics.

## 5. quantity_required

Default:
- 1

P0-B type decision:
- integer

Rules:
- must be positive
- zero and negative values are rejected

## 6. Uniqueness Policy

P0-B uniqueness key:
- tenant_id
- operation_id
- required_resource_type
- required_capability_code

Reason:
- Reject duplicate ambiguous requirements before priority/sequence semantics are introduced.

## 7. Lifecycle Policy (Parent Routing Governed)

Parent routing lifecycle controls requirement mutation.

DRAFT routing:
- create allowed
- update allowed
- remove allowed

RELEASED routing:
- create rejected
- update rejected
- remove rejected

RETIRED routing:
- create rejected
- update rejected
- remove rejected

## 8. Delete Policy

P0-B policy:
- hard delete allowed only when parent routing is DRAFT.

Reason:
- P0-B requirement records are draft master-data structures; released/retired structures are immutable.

## 9. Event Contract (Canonical for P0-B-03)

Canonical events:
- RESOURCE_REQUIREMENT.CREATED
- RESOURCE_REQUIREMENT.UPDATED
- RESOURCE_REQUIREMENT.REMOVED

Status for all events in this contract:
- CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT

Minimum event payload:
- tenant_id
- actor_user_id
- requirement_id
- routing_id
- operation_id
- required_resource_type
- required_capability_code
- changed_fields
- occurred_at

Event taxonomy decision:
- logical taxonomy = domain_event
- runtime persistence may use governed/security event infrastructure as transitional implementation until a dedicated domain event store is introduced

## 10. API Surface (P0-B Minimum)

Read:
- GET /routings/{routing_id}/operations/{operation_id}/resource-requirements
- GET /routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}

Write:
- POST /routings/{routing_id}/operations/{operation_id}/resource-requirements
- PATCH /routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}
- DELETE /routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}

API behavior notes:
- all endpoints are tenant-scoped
- cross-tenant detail reads return 404 to avoid existence leakage
- server validates that operation belongs to routing
- lifecycle policy is server-governed via parent routing status

## 11. Invariants

Mandatory invariants:
- tenant isolation mandatory
- routing must belong to same tenant
- operation must belong to routing
- operation must belong to same tenant
- requirement must link to same-tenant routing operation
- required_resource_type must be valid enum value
- required_capability_code is required in P0-B
- quantity_required must be positive integer
- duplicate requirement rejected by uniqueness rule
- parent routing must be DRAFT for create/update/remove
- RELEASED routing blocks requirement mutation
- RETIRED routing blocks requirement mutation
- no execution truth introduced in this slice
- no dispatch/reservation/planning logic introduced in this slice

## 12. Explicit Exclusions

Excluded from this contract:
- concrete station assignment
- concrete equipment assignment
- operator assignment
- equipment reservation
- capacity planning
- APS
- dispatch queue
- execution queue
- work order generation
- BOM
- recipe / ISA-88 phase logic
- Backflush
- ERP sync
- Acceptance Gate
- frontend UI

## 13. Hard Mode MOM v3 Implementation Gate

### 13.1 Event Map

| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| create_resource_requirement | RESOURCE_REQUIREMENT.CREATED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | tenant_id, actor_user_id, requirement_id, routing_id, operation_id, required_resource_type, required_capability_code, changed_fields, occurred_at | resource requirement read models (future), planning linkage consumers (future), audit pipelines | resource-requirement-mapping-contract |
| update_resource_requirement | RESOURCE_REQUIREMENT.UPDATED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | same minimum payload | resource requirement read models (future), planning linkage consumers (future), audit pipelines | resource-requirement-mapping-contract |
| remove_resource_requirement | RESOURCE_REQUIREMENT.REMOVED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | same minimum payload | resource requirement read models (future), planning linkage consumers (future), audit pipelines | resource-requirement-mapping-contract |

### 13.2 Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| tenant isolation on list/detail/mutation | tenant | route identity + service/repository filters | no | yes | resource-requirement-mapping-contract |
| operation belongs to routing and tenant | domain_link | service validation | no | yes | resource-requirement-mapping-contract |
| required_resource_type is valid enum | invalid_input | schema + service validation | no | yes | resource-requirement-mapping-contract |
| required_capability_code is required and formatted | invalid_input | schema + service validation | no | yes | resource-requirement-mapping-contract |
| quantity_required positive integer | quantity | schema + service validation | no | yes | resource-requirement-mapping-contract |
| uniqueness on tenant_id+operation_id+resource_type+capability_code | db_invariant | DB unique constraint + service pre-check | yes | yes | resource-requirement-mapping-contract |
| parent routing DRAFT required for create/update/remove | state_machine | service validation | no | yes | routing-foundation-contract + resource-requirement-mapping-contract |
| RELEASED/RETIRED routing rejects mutation | state_machine | service validation | no | yes | routing-foundation-contract + resource-requirement-mapping-contract |
| no dispatch/reservation/planning/execution truth introduced | integration_boundary | scope guard + service boundary | no | yes | resource-requirement-mapping-contract |

### 13.3 Lifecycle Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| RoutingRequirement | parent routing DRAFT | create_resource_requirement | yes | RESOURCE_REQUIREMENT.CREATED | requirement row exists | n/a | resource-requirement-mapping-contract |
| RoutingRequirement | parent routing DRAFT | update_resource_requirement | yes | RESOURCE_REQUIREMENT.UPDATED | requirement row updated | n/a | resource-requirement-mapping-contract |
| RoutingRequirement | parent routing DRAFT | remove_resource_requirement | yes | RESOURCE_REQUIREMENT.REMOVED | requirement row deleted | n/a | resource-requirement-mapping-contract |
| RoutingRequirement | parent routing RELEASED | create/update/remove | no | none | unchanged | mutation rejected | routing-foundation-contract + resource-requirement-mapping-contract |
| RoutingRequirement | parent routing RETIRED | create/update/remove | no | none | unchanged | mutation rejected | routing-foundation-contract + resource-requirement-mapping-contract |

### 13.4 Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| RR-T1 | create requirement happy path | happy_path | DRAFT routing with valid operation | create | requirement persisted | RESOURCE_REQUIREMENT.CREATED | linkage + lifecycle held |
| RR-T2 | list requirements by operation | projection_consistency | existing requirements | list | tenant-scoped list returned | none_required | tenant isolation held |
| RR-T3 | get requirement by id | happy_path | existing requirement in tenant | get detail | item returned | none_required | tenant isolation held |
| RR-T4 | cross-tenant detail read | wrong_tenant | requirement in other tenant | get detail | 404 | none_required | no existence leakage |
| RR-T5 | create with operation not in tenant | wrong_tenant | cross-tenant operation reference | create | rejected | none | same-tenant linkage enforced |
| RR-T6 | create where operation does not belong to routing | invalid_input | mismatched routing_id + operation_id | create | rejected | none | routing-operation linkage enforced |
| RR-T7 | duplicate requirement rejected | db_invariant | existing unique-key row | create duplicate | rejected | none | uniqueness invariant enforced |
| RR-T8 | update on DRAFT routing | happy_path | DRAFT parent | update | updated | RESOURCE_REQUIREMENT.UPDATED | lifecycle held |
| RR-T9 | remove on DRAFT routing | happy_path | DRAFT parent | remove | deleted | RESOURCE_REQUIREMENT.REMOVED | delete policy held |
| RR-T10 | update/remove on RELEASED routing rejected | invalid_state | RELEASED parent | mutate | rejected | none | release immutability held |
| RR-T11 | create/update/remove on RETIRED routing rejected | invalid_state | RETIRED parent | mutate | rejected | none | retired immutability held |
| RR-T12 | API permission rejection | missing_permission | authenticated without required action | write command | 403 | none | server-side authorization held |

### 13.5 Implementation-readiness verdict

READY_FOR_P0_B_IMPLEMENTATION

This contract is complete enough to support test-first implementation for P0-B-03 without inventing out-of-scope behavior.
