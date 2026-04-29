# Product Foundation Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Minimal executable P0-B Product Foundation contract to unblock safe implementation planning. |
| 2026-04-29 | v1.1 | Human-accepted P0-B decisions applied for events, product_type enum, RELEASED edit policy, cross-tenant read behavior, and 09_data handling. |
| 2026-04-29 | v1.2 | Event status canonicalized to CANONICAL_FOR_P0_B and taxonomy note added for transitional runtime event persistence. |

Status: Approved contract for P0-B implementation scope.

## 1. Purpose

Define the minimum Product Foundation contract that is safe to implement in P0-B without expanding into full Manufacturing Master Data scope.

## 2. P0-B Product Aggregate (Minimum)

### 2.1 Product identity

Required fields:
- product_id
- tenant_id
- product_code
- product_name
- product_type
- lifecycle_status

Field intent:
- product_id: immutable product identity key.
- tenant_id: tenant ownership and isolation boundary.
- product_code: business key, unique inside tenant.
- product_name: display name.
- product_type: minimal classification for downstream filtering.
- lifecycle_status: state machine field for governed lifecycle transitions.

### 2.2 Product type

P0-B includes minimal product_type as a simple controlled value for execution and planning filtering.

P0-B allowed values:
- FINISHED_GOOD
- SEMI_FINISHED
- COMPONENT

Any richer taxonomy is deferred.

Free-text product_type is not allowed in P0-B.

Future extension:
- product_type may move to reference or master-data governance in a later phase.

## 3. Versioning Rule (P0-B Decision)

Decision: Advanced versioning is deferred from P0-B.

P0-B behavior:
- Product is managed as a single active definition record.
- No product_version entity is implemented in this phase.
- No version lifecycle workflow is implemented in this phase.

Forward contract when versioning is activated later:
- product_version_id
- version_code
- version_status

Future invariant (active only when versioning is enabled):
- Released product structural change requires a new version.

## 4. Scope and Ownership

Ownership decision:
- Product is tenant-owned.
- Product is global-to-tenant in P0-B.
- Product is not plant-owned in P0-B.

Relation to plant hierarchy:
- Plant, area, line, station, and equipment relations are not direct ownership fields in Product Foundation.
- Plant-specific applicability is deferred to routing, resource requirement mapping, and later planning contracts.

## 5. Lifecycle States

Canonical P0-B states:
- DRAFT
- RELEASED
- RETIRED

Reserved state:
- BLOCKED is reserved for future governance expansion and is not active in P0-B command flow.

State semantics:
- DRAFT: editable product definition.
- RELEASED: usable for downstream release and routing linkage (when those slices are enabled).
- RETIRED: cannot be newly linked for downstream release flows.

## 6. Allowed Commands and State Transitions

Commands:
- create_product
- update_product
- release_product
- retire_product

Transition contract:
- create_product: creates product in DRAFT.
- update_product: allowed in DRAFT; allowed in RELEASED only for non-structural metadata; not allowed in RETIRED.
- release_product: DRAFT to RELEASED.
- retire_product: RELEASED or DRAFT to RETIRED.

Structural fields for update policy in P0-B:
- product_code
- product_type
- tenant_id
- version identity
- routing or BOM linkage when those domains are added later

Non-structural metadata in P0-B:
- product_name
- description
- display and metadata fields

## 7. Event Contract (Canonical for P0-B)

Event registry status:
- All event names in this section are CANONICAL_FOR_P0_B.

Canonical events:
- PRODUCT.CREATED (status: CANONICAL_FOR_P0_B)
- PRODUCT.UPDATED (status: CANONICAL_FOR_P0_B)
- PRODUCT.RELEASED (status: CANONICAL_FOR_P0_B)
- PRODUCT.RETIRED (status: CANONICAL_FOR_P0_B)

Minimum event payload:
- tenant_id
- actor_user_id
- product_id
- product_code
- lifecycle_status
- changed_fields
- occurred_at

## 8. Invariants

Mandatory invariants:
- product_code must be unique per tenant.
- tenant isolation is mandatory for all reads and writes.
- retired product cannot be used for new routing linkage or new release linkage.

Conditional invariant (active only when versioning is enabled in future phase):
- released product structural change is not allowed without a new version.

P0-B practical enforcement while versioning is deferred:
- disallow structural field mutation for RELEASED product.

## 9. API Surface (P0-B Minimum)

Read:
- GET /products
- GET /products/{product_id}

Write:
- POST /products
- PATCH /products/{product_id}
- POST /products/{product_id}/release
- POST /products/{product_id}/retire

API behavior notes:
- All endpoints are tenant-scoped.
- RELEASED and RETIRED transitions are server-governed lifecycle actions.
- PATCH applies update policy by lifecycle status and field type.
- Cross-tenant GET /products/{product_id} must return 404 Not Found to avoid entity-existence leakage.

## 10. P0-B Explicit Exclusions

Excluded from this contract:
- BOM
- full routing
- recipe and ISA-88 workflow
- ERP product synchronization
- advanced versioning workflow
- Backflush
- Acceptance Gate

## 11. Hard Mode MOM v3 Implementation Gate for Future Coding

No implementation is allowed unless all maps below are prepared from authoritative docs and reviewed.

### 11.1 Event map

| Command | Required event | Event type | Name status | Notes |
|---|---|---|---|---|
| create_product | PRODUCT.CREATED | domain_event | CANONICAL_FOR_P0_B | emit once product is persisted |
| update_product | PRODUCT.UPDATED | domain_event | CANONICAL_FOR_P0_B | include changed_fields |
| release_product | PRODUCT.RELEASED | domain_event | CANONICAL_FOR_P0_B | include transition DRAFT to RELEASED |
| retire_product | PRODUCT.RETIRED | domain_event | CANONICAL_FOR_P0_B | include transition to RETIRED |

### 11.2 Invariant map

| Invariant | Category | Enforcement layer | Test required |
|---|---|---|---|
| product_code unique per tenant | tenant and identity | DB constraint and service validation | yes |
| tenant isolation on all operations | tenant | route, service, repository filters | yes |
| RELEASED structural immutability in P0-B | lifecycle | service validation | yes |
| RETIRED cannot be newly linked for downstream release | lifecycle | service validation | yes |

### 11.3 Test matrix

| Test ID | Scenario | Type | Given | When | Then |
|---|---|---|---|---|---|
| PF-T1 | create draft product | happy_path | tenant admin | create_product | product in DRAFT and code persisted |
| PF-T2 | duplicate product_code in same tenant | db_invariant | existing code | create_product | rejected |
| PF-T3 | same product_code in different tenant | tenant | second tenant | create_product | allowed |
| PF-T4 | release draft product | state_transition | DRAFT product | release_product | state RELEASED |
| PF-T5 | update released structural field | invalid_state | RELEASED product | update_product with structural field | rejected |
| PF-T6 | update released non-structural field | happy_path | RELEASED product | update_product with product_name | allowed |
| PF-T7 | retire product | state_transition | DRAFT or RELEASED | retire_product | state RETIRED |
| PF-T8 | mutate retired product | invalid_state | RETIRED product | update_product | rejected |
| PF-T9 | cross-tenant product read | authorization | tenant A actor and tenant B product | GET product detail | return 404 Not Found |

## 12. Event Taxonomy Decision

Logical event taxonomy = domain_event. Current runtime persistence may use governed/security event infrastructure as transitional implementation until a dedicated domain event store is introduced.

## 13. 09_data Canonical Document Gap Handling

For P0-B Product Foundation only, this contract is the executable source of truth for schema, API, event, and invariant behavior.

This temporary rule does not block P0-B Product Foundation implementation.

Post-implementation follow-up required:
- sync future database canonical documentation with implemented contract behavior.

## 14. Approval Note

This contract is approved for P0-B Product Foundation implementation scope only and remains phase-bounded.