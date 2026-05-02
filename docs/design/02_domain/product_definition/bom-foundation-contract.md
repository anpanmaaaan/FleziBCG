# BOM Foundation Contract

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Added BOM foundation contract and boundary lock for MMD P0-B planning. |

## 1. Scope

This contract defines the BOM foundation for Manufacturing Master Data in FleziBCG before any BOM runtime implementation.

This is a documentation-first boundary lock only.

Implementation is not included in this slice.

## 2. Domain Meaning

BOM in FleziBCG means manufacturing definition truth for intended component structure of a product.

BOM may define:
- parent product context
- ordered component lines
- required quantity and unit of measure
- optional scrap factor
- optional effective date window
- lifecycle state

BOM does not execute material movement and does not represent runtime consumption facts.

## 3. In Scope for Minimal Foundation

The minimal P0-B BOM foundation contract includes:
- bom aggregate definition
- bom_item child entity definition
- lifecycle state set
- read API proposal
- invariants and boundary guardrails
- future write governance requirements

This contract is intentionally aligned with existing MMD patterns:
- tenant scoped ownership
- read-first delivery
- explicit out-of-scope lock for execution and inventory domains

## 4. Explicitly Out of Scope

The following are excluded from this contract and from this slice:
- BOM ORM model implementation
- BOM migration implementation
- BOM schema implementation
- BOM API implementation
- BOM frontend integration
- BOM explosion logic
- material consumption logic
- inventory reservation or movement
- warehouse allocation
- backflush
- ERP posting
- traceability genealogy creation
- quality acceptance or acceptance gate linkage
- APS planning engine behavior
- AI generated BOM behavior
- digital twin simulation

## 5. Entity Contract

### 5.1 Candidate entity: bom

Required fields:
- bom_id
- tenant_id
- product_id
- bom_code
- bom_name
- lifecycle_status
- created_at
- updated_at

Optional fields:
- product_version_id (nullable, deferred for future binding)
- effective_from
- effective_to
- description

Field intent:
- bom_id: immutable identity key for BOM definition.
- tenant_id: tenant isolation boundary.
- product_id: parent product linkage.
- product_version_id: future extension point only, not active in this slice.
- bom_code: business code for operator and engineering visibility.
- bom_name: display name.
- lifecycle_status: governed state value.
- effective_from/effective_to: applicability window for future planning and release semantics.
- description: optional explanatory text.
- created_at/updated_at: audit timestamps.

### 5.2 Candidate entity: bom_item

Required fields:
- bom_item_id
- tenant_id
- bom_id
- component_product_id
- line_no
- quantity
- unit_of_measure
- created_at
- updated_at

Optional fields:
- scrap_factor
- reference_designator
- notes

Field intent:
- bom_item_id: immutable identity key.
- tenant_id: tenant isolation boundary.
- bom_id: parent BOM linkage.
- component_product_id: component product definition reference.
- line_no: deterministic line ordering key.
- quantity: intended required quantity per parent definition.
- unit_of_measure: quantity semantics.
- scrap_factor: optional allowance ratio or percentage.
- reference_designator: optional engineering reference.
- notes: optional operator/engineering note.
- created_at/updated_at: audit timestamps.

### 5.3 Candidate uniqueness and linkage rules (for implementation slice)

- bom_code uniqueness: tenant scoped, with final scope decision to be locked in implementation (tenant-only or tenant+product).
- bom_item line_no uniqueness: unique within bom_id.
- all parent-child links must be same tenant.

## 6. Product / Product Version Relationship

### 6.1 Evaluated options

- Option A: bind BOM to Product only.
- Option B: bind BOM to Product Version.
- Option C: product-scoped now, nullable product_version_id extension later.

### 6.2 Decision

Decision for BOM foundation: Option C with product-scoped implementation start.

Meaning:
- minimal foundation and first implementation slice should be product-scoped.
- product_version_id may exist only as deferred nullable extension in contract language.
- no Product Version binding implementation is authorized in this slice.

### 6.3 Reason

Current design evidence confirms:
- Product Version read model exists and is read-only.
- BOM and Routing binding to Product Version is explicitly deferred in existing Product Version contract and BE-03 audit evidence.
- Introducing Product Version binding in BOM foundation now would expand scope and couple two deferred write governance paths.

## 7. Lifecycle Status

Minimal lifecycle statuses:
- DRAFT
- RELEASED
- RETIRED

No approval workflow or release gate workflow is implemented in this slice.

## 8. Read API Contract Proposal

Primary pattern, consistent with current product-scoped API style:
- GET /api/v1/products/{product_id}/boms
- GET /api/v1/products/{product_id}/boms/{bom_id}

Optional future convenience endpoint (deferred decision):
- GET /api/v1/boms/{bom_id}

Read API rules:
- tenant scoped filtering is mandatory.
- cross-tenant or cross-product lookup must return not found.
- read endpoints use authenticated identity guard (no fine-grained action code required for read-only).

## 9. Future Write Governance

Any future BOM write path must include:
- explicit MMD BOM action code in runtime registry and governance registry
- server-side lifecycle transition validation
- tenant and parent linkage invariant enforcement
- audit/domain event records per mutation
- tests for wrong tenant, invalid lifecycle transitions, and duplicate constraints

Recommended future action code candidate:
- admin.master_data.bom.manage

This code is not introduced in this documentation-only slice.

## 10. Boundary Guardrails

Boundary guardrails are mandatory:
- BOM is manufacturing definition truth only.
- BOM does not execute material movement.
- BOM does not perform backflush.
- BOM does not post to ERP.
- BOM does not create genealogy records.
- BOM does not own inventory availability truth.
- BOM does not own Quality pass/fail or acceptance gate truth.
- execution confirmation remains in execution domain.
- inventory movement remains in inventory/material domain.
- enterprise financial posting remains in ERP integration domain.

## 11. Invariants

Required invariants for future implementation:
- all BOM and BOM item reads and writes are tenant scoped.
- BOM must belong to an existing product in same tenant.
- BOM item must belong to existing BOM in same tenant.
- quantity must be positive.
- lifecycle_status must be bounded to DRAFT, RELEASED, RETIRED.
- released/retired mutation policy must be server governed.
- no side effects into execution/inventory/ERP/traceability in BOM read layer.
- BOM write path requires explicit MMD action code.

## 12. Recommended Implementation Slices

Recommended next slices:

1. MMD-BE-05: BOM read model implementation (backend only)
- create bom and bom_item tables
- add read schemas, repository, service
- add read APIs under products scope
- add tenant and linkage invariants
- no write APIs

2. MMD-FULLSTACK-07: BOM FE read integration
- connect BomList and BomDetail to backend read APIs
- preserve read-only UI state
- keep write buttons disabled

3. MMD-BE-06: BOM write governance
- add write APIs and lifecycle transitions
- add MMD BOM action code
- add event/audit and authorization coverage

4. MMD-BE-07: Product Version binding to BOM
- evaluate and implement product_version_id linkage only after BOM read and write foundation are stable
