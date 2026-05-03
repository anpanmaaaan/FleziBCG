# MMD-WRITE-GOV-01 — MMD Write-Path Governance Matrix / Command Boundary Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Created MMD write-path governance matrix and command boundary before mutation implementation. |

## 1. Scope
This slice is documentation-only.

Purpose:
- define write-path governance matrix before any MMD mutation implementation
- lock command boundaries and lifecycle policy
- define authorization and audit expectations for future write slices

Out of scope:
- backend write API implementation
- frontend write UI implementation
- migration/schema changes
- runtime action-code registry changes
- tests

## 2. Baseline Evidence Used
Mandatory baseline inputs inspected:
- docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md
- docs/audit/mmd-read-baseline-01-read-integration-freeze-handoff.md
- docs/audit/mmd-fullstack-05-mmd-read-integration-regression-tests.md
- docs/audit/mmd-fe-qa-01-read-pages-runtime-visual-qa.md
- docs/audit/mmd-be-02-rbac-action-code-fix.md
- docs/audit/mmd-be-03-product-version-foundation-read-model.md
- docs/audit/mmd-fullstack-06-product-version-fe-read-integration.md
- docs/audit/mmd-be-04-bom-foundation-contract-boundary-lock.md
- docs/audit/mmd-be-05-bom-minimal-read-model.md
- docs/audit/mmd-fullstack-07-bom-fe-read-integration.md
- docs/audit/mmd-be-06-reason-code-foundation-contract-boundary-lock.md
- docs/audit/mmd-be-07-reason-code-minimal-read-model.md
- docs/audit/mmd-fullstack-08-reason-codes-fe-read-integration.md

Optional but inspected evidence:
- docs/audit/mmd-audit-00-fullstack-source-alignment.md
- docs/audit/mmd-fullstack-01-routing-operation-contract-alignment.md
- docs/audit/mmd-fullstack-02-routing-operation-detail-read-integration.md
- docs/audit/mmd-fullstack-03-resource-requirements-read-integration.md
- docs/audit/mmd-fullstack-04-routing-operation-resource-requirement-context-link.md

Design/governance inputs inspected:
- docs/design/02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md
- docs/design/02_domain/product_definition/product-foundation-contract.md
- docs/design/02_domain/product_definition/product-version-foundation-contract.md
- docs/design/02_domain/product_definition/routing-foundation-contract.md
- docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md
- docs/design/02_domain/product_definition/bom-foundation-contract.md
- docs/design/02_domain/product_definition/reason-code-foundation-contract.md
- docs/design/02_registry/action-code-registry.md
- docs/design/00_platform/product-business-truth-overview.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md

## 3. Source Inspection Summary
Backend inspected:
- backend/app/security/rbac.py
- backend/app/api/v1/products.py
- backend/app/api/v1/routings.py
- backend/app/api/v1/reason_codes.py
- backend/app/api/v1/router.py
- backend/app/models/product.py
- backend/app/models/product_version.py
- backend/app/models/routing.py
- backend/app/models/resource_requirement.py
- backend/app/models/bom.py
- backend/app/models/reason_code.py
- backend/app/schemas/product.py
- backend/app/schemas/routing.py
- backend/app/schemas/resource_requirement.py
- backend/app/schemas/bom.py
- backend/app/schemas/reason_code.py
- service and repository inventories under backend/app/services and backend/app/repositories

Frontend inspected:
- frontend/src/app/pages/ProductDetail.tsx
- frontend/src/app/pages/RouteDetail.tsx
- frontend/src/app/pages/RoutingOperationDetail.tsx
- frontend/src/app/pages/ResourceRequirements.tsx
- frontend/src/app/pages/BomList.tsx
- frontend/src/app/pages/BomDetail.tsx
- frontend/src/app/pages/ReasonCodes.tsx
- frontend/src/app/screenStatus.ts
- frontend/scripts/mmd-read-integration-regression-check.mjs

Key source findings:
- Product, Routing, Resource Requirement mutation routes already exist and are RBAC-protected.
- ProductVersion, BOM, ReasonCode are read-only at API level (no mutation routes).
- MMD action codes currently present: product.manage, routing.manage, resource_requirement.manage.
- Candidate action codes for product_version, bom, reason_code are not yet present.
- All 9 MMD screens are PARTIAL/BACKEND_API; write UI actions remain disabled.

## 4. Read Baseline Summary
| Domain | Read API | FE Screen | Status | Evidence |
|---|---|---|---|---|
| Product | GET /api/v1/products, GET /api/v1/products/{id} | /products, /products/:productId | PARTIAL/BACKEND_API | products.py, screenStatus.ts |
| Product Version | GET /api/v1/products/{product_id}/versions, GET /api/v1/products/{product_id}/versions/{version_id} | ProductDetail versions section | PARTIAL/BACKEND_API | MMD-BE-03, ProductDetail.tsx |
| Routing | GET /api/v1/routings, GET /api/v1/routings/{id} | /routes, /routes/:routeId | PARTIAL/BACKEND_API | routings.py |
| Routing Operation | read via routing detail operations[] | /routes/:routeId/operations/:operationId | PARTIAL/BACKEND_API | routing model/schema + ROD page |
| Resource Requirement | GET nested under routings operations | /resource-requirements | PARTIAL/BACKEND_API | routings.py nested GET |
| BOM | GET /api/v1/products/{product_id}/boms, GET /api/v1/products/{product_id}/boms/{bom_id} | /bom, /bom/:id | PARTIAL/BACKEND_API | products.py BOM endpoints |
| BOM Item | included in BomDetail.items | /bom/:id | PARTIAL/BACKEND_API | bom schemas |
| Reason Code | GET /api/v1/reason-codes, GET /api/v1/reason-codes/{id} | /reason-codes | PARTIAL/BACKEND_API | reason_codes.py |

## 5. Write-Path Governance Decisions
| Domain | Current Write API? | Current Action Code | Write Governance State | Notes |
|---|---|---|---|---|
| Product | Yes | admin.master_data.product.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | governed runtime exists; matrix formalized in this slice |
| Product Version | No | none | DEFERRED_REQUIRES_CONTRACT | first write-governance candidate |
| Routing | Yes | admin.master_data.routing.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | governed runtime exists |
| Routing Operation | Yes (nested) | admin.master_data.routing.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | parent-routing governed |
| Resource Requirement | Yes (nested) | admin.master_data.resource_requirement.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | parent-routing governed |
| BOM | No | none | DEFERRED_REQUIRES_CONTRACT | read-only currently |
| BOM Item | No | none | DEFERRED_REQUIRES_CONTRACT | read-only currently |
| Reason Code | No | none | DEFERRED_REQUIRES_CONTRACT | read-only currently |

## 6. Command Boundary Decisions
Decision values used:
- READY_FOR_FUTURE_SLICE
- DEFERRED_REQUIRES_CONTRACT
- FORBIDDEN
- NOT_APPLICABLE
- UNKNOWN_NEEDS_EVIDENCE

High-level command summary:
- Product create/update/release/retire: READY_FOR_FUTURE_SLICE
- Routing and nested operation/resource requirement mutations: READY_FOR_FUTURE_SLICE
- ProductVersion/BOM/BOM Item/ReasonCode write commands: DEFERRED_REQUIRES_CONTRACT
- delete for core governed entities (Product, ProductVersion, Routing, BOM, ReasonCode): FORBIDDEN
- set_current: only meaningful for ProductVersion and remains DEFERRED_REQUIRES_CONTRACT
- clone/copy_from_existing and bulk commands: DEFERRED_REQUIRES_CONTRACT across domains
- bind/unbind product version relations: DEFERRED_REQUIRES_CONTRACT

## 7. Lifecycle Transition Decisions
Decision values used:
- ALLOW
- FORBID
- DEFER
- N/A

Transition summary:
- Product and Routing:
  - DRAFT -> RELEASED: ALLOW (explicit release command)
  - RELEASED -> RETIRED: ALLOW (explicit retire command)
  - DRAFT -> RETIRED: ALLOW (current runtime behavior)
  - RELEASED -> DRAFT: FORBID
  - RETIRED -> RELEASED: FORBID
  - RETIRED -> DRAFT: FORBID
- ProductVersion/BOM/ReasonCode:
  - DRAFT -> RELEASED and RELEASED -> RETIRED: DEFER until write contract exists
  - DRAFT -> RETIRED: DEFER pending operational-usage constraints
  - RELEASED -> DRAFT and RETIRED reversions: FORBID until explicit reactivation governance exists
- Routing Operation, Resource Requirement, BOM Item:
  - lifecycle transitions are N/A (parent aggregate lifecycle-governed)

## 8. Authorization / Action-Code Decisions
Current runtime action codes confirmed:
- admin.master_data.product.manage
- admin.master_data.routing.manage
- admin.master_data.resource_requirement.manage

Candidate action codes evaluated (documentation only, not implemented):
- admin.master_data.product_version.manage
- admin.master_data.bom.manage
- admin.master_data.reason_code.manage

Decision summary:
- keep existing three MMD mutation action codes unchanged
- require dedicated new action codes before introducing ProductVersion/BOM/ReasonCode mutation APIs
- keep read endpoints on require_authenticated_identity
- do not reuse admin.user.manage for new MMD write domains

## 9. Audit / Event Expectations
Future write commands must produce auditable mutation trace.

Expectation summary:
- create/update/release/retire: audit log record required
- privileged mutations: security event required
- lifecycle commands: lifecycle transition record required
- domain event model: required as canonical command outcome record where implemented in the domain strategy
- read/list/get: no domain event required by default

Forbidden side effects for MMD write paths:
- execution commands/events
- quality pass/fail outcomes
- material movement/inventory postings
- backflush completion
- ERP posting
- traceability genealogy creation

## 10. Boundary Guardrails
Explicit boundary locks:
- MMD vs Execution
- MMD vs Quality
- MMD vs Material/Inventory
- MMD vs Backflush
- MMD vs ERP/PLM
- MMD vs Traceability/Genealogy
- MMD vs Maintenance
- MMD vs Planning/APS
- MMD vs Digital Twin
- MMD vs Authorization truth
- Frontend UI vs Backend truth
- Reason Codes vs Downtime Reasons
- BOM vs Material Consumption
- Product Version vs ERP/PLM Revision
- Resource Requirement vs Routing Operation

For all above boundaries:
- current decision: separated ownership
- allowed future behavior: explicit integration by dedicated slice
- forbidden behavior: implicit side effects or ownership crossing from MMD write commands

## 11. Recommended Next Slice
Selected next slice:
- MMD-BE-08 — Product Version Write Governance / Minimal Mutation Contract

Reason:
- safest first write-governance domain
- already read-connected
- minimal immediate coupling to execution, inventory movement, backflush, ERP posting, and reason-code operational harmonization
- provides governance pattern reusable for BOM and ReasonCode write paths

## 12. Verification / Diff
Command executed:
- git diff -- docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md docs/audit/mmd-write-gov-01-command-boundary.md

Expected/observed scope:
- only the two documentation files from this slice are introduced
- no backend runtime source changed
- no frontend runtime source changed
- no migration files changed

Optional status check context:
- repository has unrelated local changes outside these two new docs
- no merge conflicts detected

## 13. Final Verdict
PASS — MMD-WRITE-GOV-01 completed as documentation-only governance and command-boundary slice.

Definition of done satisfied:
- governance matrix document created
- audit report created
- all requested MMD domains covered
- command boundary matrix decisions documented
- lifecycle transition decisions documented
- authorization/action-code decisions documented
- audit/event expectations documented
- boundary guardrails documented
- frontend write UI readiness gate documented (in matrix)
- backend implementation readiness gate documented (in matrix)
- single recommended next slice selected
- no runtime source changes
- no migration changes
- no tests added
- no commit performed
