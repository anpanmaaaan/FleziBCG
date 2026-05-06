# Audit Report: MMD-BE-14 — BOM↔Product Version Binding API Foundation

**Status:** COMPLETE  
**Date:** 2025-07-10  
**Slice:** Backend API only — no frontend changes, no release validation

---

## Routing (Hard Mode MOM v3)

- **Selected brain:** flezibcg-ai-brain-v6-auto-execution
- **Selected mode:** Hard Mode MOM v3 — Autonomous Implementation
- **Hard Mode MOM:** v3
- **Reason:** Work touches master data write paths (BOM and product version), enforces invariants (one ACTIVE PRIMARY binding per PV), emits security events, and introduces new RBAC action code checks with AND semantics.

---

## Scope

Implement the backend API foundation to bind a BOM to a Product Version and unbind it. This slice provides the data model, Alembic migration, repository, service, and API routes. Release validation logic (RELEASED PV restrictions and ERP impact) is deferred to MMD-BE-14A.

---

## Files Created / Modified

| File | Action | Description |
|---|---|---|
| `backend/app/models/product_version_bom_binding.py` | Created | ORM model for `product_version_bom_bindings` table |
| `backend/app/db/init_db.py` | Modified | Import `ProductVersionBomBinding` for table registration |
| `backend/alembic/versions/0013_product_version_bom_bindings.py` | Created | Migration: creates table + 4 indexes; `down_revision="0011"` |
| `backend/app/schemas/product.py` | Modified | Added `BomBindingCreateRequest`, `ProductVersionBomBindingResponse`, `ProductVersionBomBindingAllowedActions` |
| `backend/app/repositories/product_version_bom_binding_repository.py` | Created | `get_active_binding_by_version`, `create_binding`, `update_binding` |
| `backend/app/services/product_version_bom_binding_service.py` | Created | `get_product_version_bom_binding`, `bind_bom_to_product_version`, `unbind_bom_from_product_version` |
| `backend/app/api/v1/products.py` | Modified | Added 3 routes: GET/POST/DELETE `/{product_id}/versions/{version_id}/bom-binding` |
| `backend/tests/test_bom_binding_api.py` | Created | 23 test cases (see test matrix below) |
| `backend/tests/test_mmd_rbac_action_codes.py` | Modified | 4 new source-level contract tests for binding routes |
| `backend/tests/test_alembic_baseline.py` | Modified | Updated HEAD assertion from `"0011"` to `"0013"` |

---

## API Routes

| Method | Path | Auth | Status codes |
|---|---|---|---|
| `GET` | `/api/v1/products/{product_id}/versions/{version_id}/bom-binding` | `require_authenticated_identity` | 200, 404 |
| `POST` | `/api/v1/products/{product_id}/versions/{version_id}/bom-binding` | `require_action("admin.master_data.bom.manage")` + inner `has_action(…"admin.master_data.product_version.manage")` | 201, 404, 409, 422 |
| `DELETE` | `/api/v1/products/{product_id}/versions/{version_id}/bom-binding` | `require_action("admin.master_data.bom.manage")` + inner `has_action(…"admin.master_data.product_version.manage")` | 204, 404, 422 |

Authorization is AND-gated: both `bom.manage` AND `product_version.manage` are required for mutation. Missing either returns 403.

---

## Invariants Enforced

| Invariant | Where enforced |
|---|---|
| One ACTIVE PRIMARY binding per product version | Service: checks existing before creating; raises `ValueError("already exists")` → 409 |
| Cannot bind a RETIRED BOM | Service: `_FORBIDDEN_BOM_BIND_STATUSES = {"RETIRED"}` → 422 |
| Cannot bind/unbind a non-DRAFT PV | Service: `_ALLOWED_PV_BIND_STATUSES = {"DRAFT"}` → 422 |
| BOM must belong to same product (tenant + product_id scope) | Repository: `get_bom_by_id` enforces both tenant_id and product_id |
| Unbind deactivates (status → INACTIVE), not hard-delete | Service: `update_binding` sets `binding_status="INACTIVE"` |

---

## Security Events Emitted

| Event type (stored) | Trigger |
|---|---|
| `PRODUCTVERSIONBOMBINDING.CREATED` | Successful bind |
| `PRODUCTVERSIONBOMBINDING.REMOVED` | Successful unbind |

Note: `record_security_event` applies `.strip().upper()` so all event types are stored uppercased.

---

## Test Matrix

| ID | Test | Result |
|---|---|---|
| T01 | Bind DRAFT PV + RELEASED BOM → 201 | ✅ |
| T02 | Bind DRAFT PV + DRAFT BOM → 201 | ✅ |
| T03 | GET after bind → 200 with correct payload | ✅ |
| T04 | Unbind DRAFT PV → 204 | ✅ |
| T05 | GET after unbind → 404 | ✅ |
| T06 | Bind RETIRED BOM → 422 | ✅ |
| T07 | Bind RELEASED PV → 422 | ✅ |
| T08 | Bind RETIRED PV → 422 | ✅ |
| T09 | Duplicate bind (already ACTIVE) → 409 | ✅ |
| T10 | Unbind RELEASED PV → 422 | ✅ |
| T11 | Unbind with no existing binding → 404 | ✅ |
| T12 | BOM from wrong product → 404 | ✅ |
| T13 | PV not found → 404 | ✅ |
| T14 | Missing bom.manage → 403 | ✅ |
| T15 | Missing pv.manage → 403 | ✅ |
| T16 | Missing both permissions → 403 | ✅ |
| T17 | BOM not found → 404 | ✅ |
| T20 | Bind emits CREATED security event | ✅ |
| — | Unbind emits REMOVED security event | ✅ |
| — | GET allowed_actions with both perms | ✅ |
| — | GET allowed_actions without perms | ✅ |
| — | Source contract: routes exist in products.py | ✅ |
| — | Source contract: bom.manage used ≥9 times | ✅ |
| — | Source contract: product_version.manage referenced | ✅ |

---

## Migration Chain

```
0001 → 0002 → ... → 0011 → 0013
```

Migration 0013 creates `product_version_bom_bindings` with columns:
`binding_id`, `tenant_id`, `product_id`, `product_version_id`, `bom_id`,
`binding_type` (default: "PRIMARY"), `binding_status` (default: "ACTIVE"),
`notes`, `created_at`, `updated_at`, `created_by`, `updated_by`

Indexes on: `tenant_id`, `product_id`, `product_version_id`, `bom_id`

Note: migration 0012 (`add_scope_applicability_to_approval_rules`) was applied to the live DB in a prior session but never committed to git. The alembic_version table was corrected to `0011` via direct SQL before running this migration.

---

## Deferred

- **MMD-BE-14A:** Release validation — prevent binding/unbinding when PV is in RELEASED/ARCHIVED/ACTIVE_PRODUCTION status (beyond DRAFT-only restriction already in place)
- **MMD-BE-14B:** ERP posting / backflush impact on binding changes
- **MMD-FE-14:** Frontend UI for BOM binding management

---

## Verification Results

```
58 passed, 1 skipped   — test_bom_binding_api.py + test_mmd_rbac_action_codes.py + test_alembic_baseline.py
96 passed              — test_bom_foundation_api.py + test_bom_foundation_service.py + test_product_version_foundation_api.py
```

All target tests green. No regressions in BOM or product version foundation suites.
