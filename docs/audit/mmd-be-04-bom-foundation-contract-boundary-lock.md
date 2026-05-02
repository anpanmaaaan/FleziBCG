# MMD-BE-04 - BOM Foundation Contract / Boundary Lock Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Created BOM foundation contract and implementation boundary lock. |

## 1. Scope

This report captures evidence, decisions, and boundary locks for MMD-BE-04.

Scope is documentation only:
- define BOM foundation contract
- lock implementation boundaries
- recommend next slice sequencing

No runtime source, migration, or API implementation is included.

## 2. Baseline Evidence Used

Mandatory baseline reports reviewed:
- docs/audit/mmd-audit-00-fullstack-source-alignment.md
- docs/audit/mmd-read-baseline-01-read-integration-freeze-handoff.md
- docs/audit/mmd-fullstack-05-mmd-read-integration-regression-tests.md
- docs/audit/mmd-be-03-product-version-foundation-read-model.md
- docs/audit/mmd-fullstack-06-product-version-fe-read-integration.md

Design/governance sources reviewed:
- .github/copilot-instructions.md
- .github/agent/AGENT.md
- docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- docs/ai-skills/hard-mode-mom-v3/SKILL.md
- docs/design/INDEX.md
- docs/design/AUTHORITATIVE_FILE_MAP.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md
- docs/governance/SOURCE_STRUCTURE.md
- docs/design/00_platform/product-business-truth-overview.md
- docs/design/02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md
- docs/design/02_domain/product_definition/product-foundation-contract.md
- docs/design/02_domain/product_definition/product-version-foundation-contract.md
- docs/design/02_domain/product_definition/routing-foundation-contract.md
- docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md
- docs/design/02_registry/action-code-registry.md

Optional requested docs not found at expected paths:
- docs/design/00_platform/product-scope-and-phase-boundary.md
- docs/design/09_data/database-implementation-phasing.md

## 3. Source Inspection Summary

Frontend inspection summary:
- BomList and BomDetail are shell pages using inline mock fixtures.
- routes include /bom and /bom/:bomId only as shell UI surfaces.
- screen status marks bomList and bomDetail as SHELL with MOCK_FIXTURE.
- regression script currently protects MMD read integration but does not add BOM backend assertions yet.

Backend inspection summary:
- no bom model found
- no bom schema found
- no bom repository found
- no bom service found
- no bom API route found
- no bom migration found
- product version read model exists and explicitly defers BOM binding

Conclusion:
- BOM backend implementation gap is confirmed.
- MMD-BE-04 is safe and necessary as contract-first boundary lock.

## 4. BOM Boundary Decisions

Boundary decisions locked:
- BOM belongs to Manufacturing Master Data as definition truth.
- BOM does not execute material movement.
- BOM does not perform backflush.
- BOM does not post to ERP.
- BOM does not create traceability genealogy records.
- BOM does not own inventory availability truth.
- BOM does not own quality pass/fail or acceptance gate truth.
- execution domain remains source of operational confirmation.
- inventory/material domain remains source of movement truth.

## 5. Product / Product Version Binding Decision

Evaluated options:
- Option A: Product-only BOM binding
- Option B: Product Version BOM binding
- Option C: Product scoped first, Product Version binding deferred via nullable extension point

Decision: Option C

Rationale:
- Product Version read model is now stable and read-only.
- Existing Product Version contract and BE-03 evidence explicitly defer BOM binding.
- Immediate BOM Product Version binding would prematurely couple BOM foundation with deferred version-governance and write-path concerns.

Lock:
- first BOM implementation slice must be product scoped.
- Product Version binding is deferred to a later explicit slice.

## 6. Proposed Entity Contract

### bom (candidate)

Fields:
- bom_id
- tenant_id
- product_id
- product_version_id nullable and deferred
- bom_code
- bom_name
- lifecycle_status
- effective_from
- effective_to
- description
- created_at
- updated_at

### bom_item (candidate)

Fields:
- bom_item_id
- tenant_id
- bom_id
- component_product_id
- line_no
- quantity
- unit_of_measure
- scrap_factor nullable
- reference_designator nullable
- notes nullable
- created_at
- updated_at

## 7. Proposed API Contract

Primary proposed read API pattern:
- GET /api/v1/products/{product_id}/boms
- GET /api/v1/products/{product_id}/boms/{bom_id}

Optional deferred endpoint:
- GET /api/v1/boms/{bom_id}

Contract notes:
- tenant scoped filtering is mandatory
- cross-tenant and cross-product leakage must return not found
- read endpoints should remain authenticated-read only

## 8. Explicit Non-Goals

This slice does not implement:
- BOM ORM
- BOM migration
- BOM schemas
- BOM APIs
- BOM tests
- BOM frontend backend integration
- BOM explosion
- material consumption
- inventory allocation or movement
- backflush
- ERP posting
- lot genealogy
- quality checkpoint linkage
- acceptance gate
- APS planning engine
- AI generated BOM
- digital twin simulation

## 9. Future Implementation Slice Recommendation

Recommended next slice: MMD-BE-05

Purpose:
- implement BOM and BOM item read model only
- keep product scoped binding
- add read-only APIs and tests
- enforce tenant and linkage invariants

Deferred slices:
- MMD-FULLSTACK-07 for BOM FE read integration
- MMD-BE-06 for BOM write governance and lifecycle mutation
- MMD-BE-07 for Product Version binding after BOM foundation stabilizes

## 10. Verification / Diff

Verification command executed:
- git diff -- docs/design/02_domain/product_definition/bom-foundation-contract.md docs/audit/mmd-be-04-bom-foundation-contract-boundary-lock.md

Result:
- only the two expected documentation files are introduced in this slice.
- no backend runtime source modified.
- no frontend runtime source modified.
- no migration files modified.

## 11. Final Verdict

PASS - MMD-BE-04 completed as documentation-first boundary lock.

Definition of done achieved:
- BOM contract document created
- audit report created
- Product versus Product Version decision explicitly locked
- material/backflush/ERP/traceability boundaries explicitly locked
- entity and API proposals documented
- future write governance requirement documented
- recommended next slice provided

No runtime implementation was performed in this slice.
