# BOM Product Version Binding Governance Contract

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-06 | v1.0 | Added governance contract for future BOM ↔ Product Version binding. |

## 1. Scope
This contract defines governance for a future BOM ↔ Product Version binding capability.

In scope:
- Binding entity, cardinality, lifecycle compatibility, authorization, command boundary, validation rules, event/audit expectations, read model expectations, and future API proposal.

Out of scope:
- Runtime API implementation
- Runtime DB/migration changes
- Runtime UI changes
- Runtime test implementation
- Any change to current BOM/Product Version write behavior
- Product Version `set_current`
- Material/inventory/backflush/ERP/traceability/quality/execution behavior

## 2. Current Baseline
Baseline evidence confirms:
- BOM and Product Version write baselines are frozen and implemented independently.
- BOM remains product-scoped in runtime; no `product_version_id` on BOM runtime model.
- BOM↔Product Version binding is deferred in existing governance matrix.
- Existing action codes include `admin.master_data.bom.manage` and `admin.master_data.product_version.manage`.
- Frontend capability gating consumes backend-derived capability truth.

Current-state source evidence:
- `backend/app/models/bom.py` excludes runtime `product_version_id`.
- `backend/app/schemas/bom.py` write payloads are `extra="forbid"` with no binding fields.
- `backend/app/api/v1/products.py` has BOM and Product Version write routes but no binding routes.
- `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` marks BOM bind/unbind as deferred.

## 3. Business Purpose
Binding enables definition applicability truth:
- Which BOM is applicable for Product + Product Version
- Controlled version-specific manufacturing definition selection
- No mutation of execution/material/quality/integration truth

Binding is definition applicability metadata only.

## 4. Binding Principles
1. Backend is source of truth for binding authorization, lifecycle, and validation.
2. Binding is a separate governed command boundary, not implicit in BOM/PV update commands.
3. Binding must not trigger material, inventory, ERP, genealogy, quality, or execution side effects.
4. Binding events are auditable governance facts.
5. Historical binding records remain readable even if BOM/PV becomes retired.

## 5. Binding Entity Decision
Decision: introduce conceptual association entity `ProductVersionBomBinding` in future implementation.

Contract-level fields (future):
- `binding_id`
- `tenant_id`
- `product_id`
- `product_version_id`
- `bom_id`
- `binding_type` (`PRIMARY` only in first implementation)
- `binding_status` (`ACTIVE`, `REMOVED`)
- `effective_from` and `effective_to` (deferred in first implementation)
- `created_at`, `updated_at`, `created_by`, `updated_by`

Runtime note:
- This contract does not authorize adding `product_version_id` to BOM runtime entity in this slice.

## 6. Cardinality Decision
Decision for first implementation:
- One Product Version can have zero or one ACTIVE PRIMARY BOM binding.
- One BOM may be bound to multiple Product Versions if lifecycle and product/tenant invariants pass.

Rationale:
- Preserves current product-scoped BOM model and allows shared released BOM definitions.
- Keeps first binding scope small while avoiding artificial one-BOM-one-version lock.

## 7. Lifecycle Compatibility Matrix
| Product Version State | BOM State | Binding Decision | Release Impact |
|---|---|---|---|
| DRAFT | DRAFT | ALLOW | PV cannot be released while PRIMARY bound BOM remains DRAFT |
| DRAFT | RELEASED | ALLOW | Preferred pre-release path |
| DRAFT | RETIRED | FORBID | Retired BOM cannot be newly bound |
| RELEASED | DRAFT | FORBID | Released PV cannot reference DRAFT BOM |
| RELEASED | RELEASED | ALLOW | Valid steady state |
| RELEASED | RETIRED | FORBID | New binding forbidden |
| RETIRED | any | FORBID | No new bind/unbind changes on retired PV |
| any | RETIRED | FORBID (new binding) | Historical rows remain readable |

Unbinding rules:
- DRAFT PV: unbind allowed.
- RELEASED PV: unbind forbidden unless atomic replace with another RELEASED BOM (replace contract deferred).
- RETIRED PV: unbind forbidden.

## 8. Authorization / Action-Code Requirements
Decision for first implementation:
- Binding commands require BOTH:
  - `admin.master_data.bom.manage`
  - `admin.master_data.product_version.manage`

Reason:
- Binding mutates both definition applicability domains.
- Existing registry already contains both domain action codes.

Dedicated binding action code:
- `admin.master_data.product_definition_binding.manage` is deferred unless later governance requires finer separation.

## 9. Future API Contract Proposal
Proposed route family (future, not implemented):
- `POST /api/v1/products/{product_id}/versions/{version_id}/bom-binding`
- `DELETE /api/v1/products/{product_id}/versions/{version_id}/bom-binding`
- `PATCH /api/v1/products/{product_id}/versions/{version_id}/bom-binding`
- `GET /api/v1/products/{product_id}/versions/{version_id}/bom-binding`

Command mapping:
- POST: `bind_bom_to_product_version`
- DELETE: `unbind_bom_from_product_version`
- PATCH: `replace_product_version_primary_bom` (deferred unless atomic replace policy is finalized)
- GET: read model fetch

Payload decision:
- First implementation accepts `bom_id` and optional `notes`.
- `binding_type` fixed to `PRIMARY` in first implementation.
- `effective_from/effective_to` deferred to a later effective-dating slice.

Response decision:
- Include backend-derived `allowed_actions` for update/remove.
- Include binding lifecycle status and reference ids.

## 10. Validation Rules
Mandatory future validation:
1. Tenant isolation: PV and BOM must belong to same tenant.
2. Product scope: PV.product_id must match BOM.product_id and route `product_id`.
3. Authorization: caller must satisfy both action codes.
4. Lifecycle compatibility matrix must pass.
5. One active PRIMARY binding per Product Version.
6. If binding exists: Product Version release must validate at least one ACTIVE PRIMARY binding to RELEASED BOM.
7. Released BOM may exist without any Product Version binding.
8. Historical bindings to retired BOM/PV remain queryable.

## 11. Audit / Event Expectations
Allowed governance events:
- `ProductVersionBomBinding.CREATED`
- `ProductVersionBomBinding.REPLACED`
- `ProductVersionBomBinding.REMOVED`
- `ProductVersionBomBinding.VALIDATED_ON_RELEASE`

Forbidden side effects:
- `MaterialReserved`
- `MaterialConsumed`
- `BackflushPosted`
- `ERPPosted`
- `GenealogyCreated`
- `QualityAccepted`
- `ExecutionStarted`
- `OperationConfirmed`

## 12. Read Model / Frontend Expectations
Read model expectations (future):
- Product Version detail may include current binding summary.
- BOM detail may include referencing Product Version count or list (optional, deferred).
- Binding read endpoint returns binding row and backend-derived `allowed_actions`.

Frontend readiness gate:
- No binding UI before backend binding API and server authorization are implemented.
- Frontend sends intent only; it must not infer lifecycle authorization from local state.

## 13. Cross-Domain Boundary Guardrails
Boundary decisions:
- MMD binding remains definition metadata only.
- No execution command/event ownership change.
- No quality decision ownership change.
- No inventory/material movement ownership change.
- No ERP/PLM posting behavior.
- No genealogy creation.
- No automatic dispatch/planning/APS decision.

Risk if violated:
- Operational truth corruption, ownership overlap, and audit ambiguity.

## 14. Explicit Non-Goals
This contract does not authorize:
- DB migrations
- Backend binding routes/services
- Frontend binding controls
- BOM/Product Version lifecycle rule rewrites
- Product Version `set_current`
- Material reservation/movement/backflush
- ERP posting
- Traceability genealogy
- Quality acceptance
- Execution dispatch/order creation
- Automatic current-version selection

## 15. Required Tests for Future Implementation
1. Bind success for DRAFT PV + RELEASED BOM.
2. Bind success for DRAFT PV + DRAFT BOM.
3. Bind rejection for RELEASED PV + DRAFT BOM.
4. Bind rejection for any new binding to RETIRED BOM/PV.
5. Release validation failure when PV has no PRIMARY RELEASED BOM binding.
6. Authorization rejection when either required action code is missing.
7. Cross-tenant and cross-product isolation failures.
8. Single-active-primary invariant enforcement.
9. Audit/security event payload assertions for CREATED/REMOVED/VALIDATED_ON_RELEASE.
10. No forbidden side effect assertions (execution/material/ERP/quality/traceability unchanged).

## 16. Recommended Next Slice
Recommended next slice: **MMD-BE-14 — BOM Product Version Binding API Foundation**.

Reason:
- Existing action codes are sufficient for first implementation (both manage codes required).
- A dedicated new binding action code is not mandatory for the first API foundation slice.
