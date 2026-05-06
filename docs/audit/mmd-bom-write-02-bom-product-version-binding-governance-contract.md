# MMD-BOM-WRITE-02 — BOM Product Version Binding Governance Contract Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-06 | v1.0 | Created governance contract for future BOM ↔ Product Version binding. |

## 1. Scope
Documentation-only governance slice.

In scope:
- Define BOM↔Product Version binding governance contract before implementation.
- Decide binding entity, cardinality, lifecycle, authorization, command boundary, events, and future API/test requirements.

Out of scope:
- Backend/frontend/runtime source changes
- Migration/schema changes
- Runtime tests/build changes
- Any operational side effects outside definition applicability

## 2. Baseline Evidence Used

## Routing
- Selected brain: MOM Brain
- Selected mode: Architecture + QA/contract hardening
- Hard Mode MOM: ON (v3)
- Reason: Binding touches lifecycle, authz, and manufacturing definition applicability boundaries.

## Baseline Evidence Extract

## Current Product Version / BOM Baseline Summary
| Area | Evidence | Decision |
|---|---|---|
| BOM runtime model | `backend/app/models/bom.py` has no `product_version_id` field | Keep as-is in this slice |
| BOM write payload boundary | `backend/app/schemas/bom.py` uses `extra="forbid"`; no binding fields | No payload-level implicit binding |
| PV write lifecycle | `backend/app/services/product_version_service.py` enforces DRAFT→RELEASED→RETIRED | Binding must respect existing lifecycle |
| BOM write lifecycle | `backend/app/services/bom_service.py` enforces DRAFT→RELEASED→RETIRED | Binding must not alter lifecycle behavior |
| Existing binding governance | `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` marks BOM bind/unbind deferred | Contract required before API work |
| Action codes | `admin.master_data.bom.manage` and `admin.master_data.product_version.manage` in `rbac.py` and registry doc | Reuse both for first binding implementation |
| FE capability gating pattern | `/products`, `/bom`, `/reason-codes` consume server-derived capabilities | Future binding UI must follow same pattern |

## Binding Option Matrix
| Option | Decision | Reason |
|---|---|---|
| A. One PV -> one active BOM | ACCEPT (PRIMARY in first implementation) | Minimal and deterministic applicability contract |
| B. One PV -> many BOMs by type/use | DEFER | Requires additional type semantics not yet governed |
| C. One BOM -> many PVs | ACCEPT_WITH_GUARD | Allow reuse if lifecycle and product/tenant invariants pass |
| D. Effective-date binding table | DEFER | Effective dating adds policy complexity; not needed for first implementation |
| E. Plant/scope-specific binding table | DEFER | Scope applicability contract should be separate slice |

## Lifecycle Compatibility Matrix
| Product Version State | BOM State | Binding Decision | Release Impact |
|---|---|---|---|
| DRAFT | DRAFT | ALLOW | PV release blocked until PRIMARY BOM is RELEASED |
| DRAFT | RELEASED | ALLOW | Ready for PV release validation |
| DRAFT | RETIRED | FORBID | Retired BOM cannot be newly bound |
| RELEASED | DRAFT | FORBID | Released PV must not point to DRAFT BOM |
| RELEASED | RELEASED | ALLOW | Valid released applicability |
| RELEASED | RETIRED | FORBID | No new binding to retired BOM |
| RETIRED | any | FORBID | No binding mutation on retired PV |

## Authorization / Action-Code Map
| Command | Required Action Code(s) | Decision |
|---|---|---|
| bind_bom_to_product_version | `admin.master_data.bom.manage` + `admin.master_data.product_version.manage` | REQUIRED |
| unbind_bom_from_product_version | same two codes | REQUIRED |
| replace_product_version_primary_bom | same two codes | DEFERRED_REQUIRES_CONTRACT |
| release_product_version_with_bom_validation | `admin.master_data.product_version.manage` (+ binding read validation) | READY_FOR_IMPLEMENTATION when binding exists |

## Event / Side-Effect Map
| Future Command | Allowed Event | Forbidden Side Effects |
|---|---|---|
| bind_bom_to_product_version | `ProductVersionBomBinding.CREATED` | MaterialReserved, MaterialConsumed, BackflushPosted, ERPPosted, GenealogyCreated, QualityAccepted, ExecutionStarted, OperationConfirmed |
| replace_product_version_primary_bom | `ProductVersionBomBinding.REPLACED` | Same forbidden set |
| unbind_bom_from_product_version | `ProductVersionBomBinding.REMOVED` | Same forbidden set |
| release_product_version_with_bom_validation | `ProductVersionBomBinding.VALIDATED_ON_RELEASE` | Same forbidden set |

## Boundary Map
| Boundary | Decision | Risk if Violated |
|---|---|---|
| MMD definition vs execution | Keep separated | Execution truth corruption |
| MMD definition vs material/inventory | Keep separated | Inventory/accounting drift |
| MMD definition vs ERP posting | Keep separated | External SoR conflict |
| MMD definition vs genealogy | Keep separated | Traceability contamination |
| MMD definition vs quality acceptance | Keep separated | Quality governance breach |
| Frontend vs backend authorization truth | Backend only | Privilege bypass |

## Future API Contract Proposal
| Endpoint | Command | Scope | Decision |
|---|---|---|---|
| `POST /api/v1/products/{product_id}/versions/{version_id}/bom-binding` | bind | Product-scoped PV binding | PROPOSED |
| `DELETE /api/v1/products/{product_id}/versions/{version_id}/bom-binding` | unbind | Product-scoped PV binding | PROPOSED |
| `PATCH /api/v1/products/{product_id}/versions/{version_id}/bom-binding` | replace | Product-scoped PV binding | DEFERRED pending atomic replacement policy |
| `GET /api/v1/products/{product_id}/versions/{version_id}/bom-binding` | read binding | Product-scoped PV binding | PROPOSED |

Candidate payload evaluation:
- Keep: `bom_id`, optional `notes`.
- Defer: `effective_from`, `effective_to`, and generalized `binding_type` beyond PRIMARY.
- Require server-derived `allowed_actions` in response.

## Future Test Matrix
| Test Area | Required Future Tests |
|---|---|
| Lifecycle compatibility | Matrix-positive and matrix-negative bind/unbind cases |
| Authorization | Missing either action code => forbidden |
| Tenant/product isolation | Cross-tenant and cross-product bind rejection |
| Cardinality | Single ACTIVE PRIMARY binding per PV invariant |
| Release validation | Released PV requires at least one RELEASED PRIMARY BOM binding |
| Historical readability | Retired BOM/PV historical bindings remain queryable |
| Side-effect boundary | Assert no execution/material/ERP/quality/traceability mutation |
| Event/audit correctness | CREATED/REMOVED/VALIDATED_ON_RELEASE event payload assertions |

## Verdict Before Writing
ALLOW_CONTRACT_ONLY

Reason:
- Required baseline and source evidence exists.
- No hidden BOM↔PV runtime binding detected.
- Contract can be safely authored without runtime modifications.

## 3. Source Inspection Summary
Inspected backend files:
- `backend/app/models/product.py`
- `backend/app/models/bom.py`
- `backend/app/schemas/product.py`
- `backend/app/schemas/bom.py`
- `backend/app/repositories/bom_repository.py`
- `backend/app/services/product_version_service.py`
- `backend/app/services/bom_service.py`
- `backend/app/api/v1/products.py`
- `backend/app/security/rbac.py`
- `backend/tests/test_product_version_foundation_api.py`
- `backend/tests/test_bom_foundation_api.py`
- `backend/tests/test_bom_allowed_actions_12b_a.py`
- `backend/tests/test_mmd_rbac_action_codes.py`

Inspected frontend files:
- `frontend/src/app/pages/ProductDetail.tsx`
- `frontend/src/app/pages/BomList.tsx`
- `frontend/src/app/pages/BomDetail.tsx`
- `frontend/src/app/api/productApi.ts`
- `frontend/scripts/mmd-read-integration-regression-check.mjs`

Adjacent boundary inspection:
- `backend/app/schemas/operation.py`
- `backend/app/api/v1/operations.py`
- `backend/app/models/execution.py`
- Requested exact files not found: `backend/app/models/operation.py`, `backend/app/models/material*`, `backend/app/models/trace*`

Findings:
- No runtime BOM↔PV binding commands/endpoints.
- No `product_version_id` in BOM runtime model.
- Existing BOM and PV write baselines are independent and frozen.

## 4. Binding Decisions
1. Binding entity name: `ProductVersionBomBinding`.
2. Cardinality (phase 1): one PV has zero/one ACTIVE PRIMARY BOM.
3. BOM reuse across PVs: allowed with tenant/product/lifecycle guardrails.
4. Binding command boundary: separate association commands, not implicit BOM/PV update side effects.

## 5. Lifecycle Compatibility Decisions
- DRAFT PV may bind DRAFT or RELEASED BOM.
- RELEASED PV may bind RELEASED BOM only.
- RETIRED PV cannot be changed.
- RETIRED BOM cannot be newly bound.
- PV release validation (future): must fail if PRIMARY bound BOM is not RELEASED.
- Released BOM may exist unbound.

## 6. Authorization / Action-Code Decisions
- Binding uses BOTH existing action codes (`bom.manage` and `product_version.manage`).
- No new dedicated binding action code required for first implementation.
- Dedicated binding code remains a future optional hardening path.

## 7. Future API Contract Proposal
Proposed endpoint family remains product-scoped under Product Version.

Phase-1 contract shape:
- Request: `bom_id`, optional `notes`.
- Response: binding row + backend-derived `allowed_actions`.
- Effective dating and multi-type binding are deferred.

## 8. Audit / Event Expectations
Allowed events:
- `ProductVersionBomBinding.CREATED`
- `ProductVersionBomBinding.REPLACED`
- `ProductVersionBomBinding.REMOVED`
- `ProductVersionBomBinding.VALIDATED_ON_RELEASE`

Forbidden side effects:
- Material/inventory/backflush/ERP/traceability/quality/execution side effects are prohibited.

## 9. Boundary Guardrails
- Binding is manufacturing definition applicability only.
- No ownership transfer into execution, quality, inventory, ERP, or genealogy domains.
- Frontend remains intent-only and backend-validated.

## 10. Future Test Requirements
Required future test suite includes:
- lifecycle matrix assertions
- dual-action-code authorization assertions
- cardinality invariant assertions
- release validation assertions
- no-side-effect assertions
- event payload assertions

## 11. Recommended Next Slice
**MMD-BE-14 — BOM Product Version Binding API Foundation**.

Reason:
- Existing action codes are sufficient for phase-1 API foundation.
- Frontend integration must wait for backend API completion.

## 12. Verification / Diff
Executed:
- `git diff -- docs/design/02_domain/product_definition/bom-product-version-binding-governance-contract.md docs/audit/mmd-bom-write-02-bom-product-version-binding-governance-contract.md`

Expected result:
- Only the two new documentation files introduced in this slice.

## 13. Final Verdict
PASS — CONTRACT_READY

All required governance decisions were documented without modifying runtime source, migrations, or tests.
