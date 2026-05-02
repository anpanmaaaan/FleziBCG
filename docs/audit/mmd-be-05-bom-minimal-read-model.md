# MMD-BE-05 - BOM Minimal Read Model / API Foundation Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Implemented BOM read model, migration, product-scoped read APIs, and boundary tests. |

## 1. Scope

This report documents MMD-BE-05 implementation and verification for BOM minimal backend read foundation.

In scope:
- BOM and BOM item read model introduction
- migration and SQL bootstrap alignment
- product-scoped read APIs
- service/repository/API boundary tests

Out of scope (explicitly deferred):
- BOM write commands or lifecycle mutation endpoints
- Product Version binding for BOM
- material movement or inventory consumption logic
- backflush logic
- ERP posting logic
- traceability genealogy linkage
- quality decision linkage

## 2. Baseline Evidence

Baseline and governance sources used:
- .github/copilot-instructions.md
- .github/agent/AGENT.md
- docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- docs/ai-skills/hard-mode-mom-v3/SKILL.md
- docs/design/INDEX.md
- docs/design/AUTHORITATIVE_FILE_MAP.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md
- docs/governance/SOURCE_STRUCTURE.md
- docs/design/02_domain/product_definition/bom-foundation-contract.md
- docs/audit/mmd-be-04-bom-foundation-contract-boundary-lock.md

## 3. BOM Contract Decision

Decision applied from BE-04 contract lock:
- BOM is product-scoped in this slice.
- Product Version binding remains deferred.
- BOM is master-data read truth only and does not own execution/inventory/ERP outcomes.

## 4. Data Model / Migration

Implemented model:
- bom table with tenant, product, code, name, lifecycle, effective range, description, timestamps
- bom_item table with tenant, bom, component product, line, quantity, UoM, optional scrap/reference/notes, timestamps

Migration implementation:
- Alembic revision 0008 creates boms and bom_items with constraints/indexes.
- SQL bootstrap script 0019 mirrors the same structure for SQL-based setup flow.

## 5. API Contract

Implemented read endpoints:
- GET /api/v1/products/{product_id}/boms
- GET /api/v1/products/{product_id}/boms/{bom_id}

Contract behavior:
- authenticated identity required
- tenant and parent-product scoping enforced
- missing product or mismatched linkage returns 404
- no BOM write routes exposed

## 6. Files Changed

Backend model/schema/repository/service/API:
- backend/app/models/bom.py
- backend/app/schemas/bom.py
- backend/app/repositories/bom_repository.py
- backend/app/services/bom_service.py
- backend/app/api/v1/products.py
- backend/app/db/init_db.py

Migrations:
- backend/alembic/versions/0008_boms.py
- backend/scripts/migrations/0019_boms.sql

Tests:
- backend/tests/test_bom_foundation_service.py
- backend/tests/test_bom_foundation_api.py

Audit:
- docs/audit/mmd-be-05-bom-minimal-read-model.md

## 7. Backend Changes Summary

- Added BOM ORM models with ordered one-to-many relationship for items by line number.
- Added BOM response schemas for list/detail reads.
- Added repository methods for product-scoped list and detail retrieval.
- Added service methods to enforce parent product existence and linkage checks.
- Added product-scoped BOM GET endpoints in products router.
- Registered BOM models in DB init imports for metadata discovery.

## 8. Tests Added / Updated

Added tests:
- service/repository foundation tests for tenant/product scoping, ordering, and boundary field exclusions
- API tests for list/detail success and 404/401 conditions
- API and model boundary tests asserting absence of write routes and forbidden execution/inventory/ERP fields

Fix applied during verification:
- corrected detached SQLAlchemy instance access in one API test by capturing bom_id before session close

## 9. Boundary Guardrails

Guardrails enforced in implementation/tests:
- no product_version_id field in BOM foundation schema/model
- no backflush fields
- no ERP posting fields
- no inventory movement/issue/reservation fields
- no BOM write route methods (POST/PATCH/PUT/DELETE)

## 10. Verification Commands

Executed verification commands and outcomes:

1) Targeted BE-05 tests
- Command:
  - ../.venv/Scripts/python.exe -m pytest tests/test_bom_foundation_api.py tests/test_bom_foundation_service.py
- Outcome:
  - PASS (20 passed)

2) Related backend safety suite available in current repository
- Initial requested file list from handoff did not exist under backend/tests and was mapped to current foundation suite names.
- Command:
  - ../.venv/Scripts/python.exe -m pytest tests/test_product_foundation_api.py tests/test_product_foundation_service.py tests/test_product_version_foundation_api.py tests/test_product_version_foundation_service.py tests/test_mmd_rbac_action_codes.py
- Outcome:
  - PASS (36 passed)

3) Alembic status checks
- Command:
  - ../.venv/Scripts/python.exe -m alembic heads
  - ../.venv/Scripts/python.exe -m alembic current
- Outcome:
  - heads: 0008 (head)
  - current: 0007

4) Frontend smoke checks (no FE changes, regression guard)
- PowerShell policy blocked npm.ps1 invocation; executed via npm.cmd.
- Command:
  - npm.cmd run check:mmd:read
  - npm.cmd run check:routes
- Outcome:
  - check:mmd:read PASS (52 passed, 0 failed)
  - check:routes PASS (24 pass, 0 fail)

## 11. Remaining Risks / Deferred Items

Deferred by design:
- Product Version BOM binding
- BOM write lifecycle governance
- inventory/backflush/ERP integration semantics
- FE consumption of backend BOM APIs in dedicated fullstack slice

Operational note:
- Alembic current remains at 0007 in checked runtime environment, while heads is 0008; environment migration apply step is external to this implementation report.

## 12. Final Verdict

PASS - MMD-BE-05 completed for BOM minimal read model and API foundation within defined boundaries.

Definition of done met for this slice:
- model + migration + SQL bootstrap
- product-scoped read endpoints
- boundary tests and regression checks
- no out-of-scope execution/inventory/ERP/write behavior introduced
