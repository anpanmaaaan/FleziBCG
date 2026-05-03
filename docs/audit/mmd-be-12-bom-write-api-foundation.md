# Audit Report: MMD-BE-12 — BOM Write API Foundation

## History

| Version | Date       | Author | Summary                                      |
|---------|------------|--------|----------------------------------------------|
| 1.0     | 2025-08-02 | Agent  | Initial implementation — all 7 write endpoints, full test coverage |

## Scope

MMD-BE-12 implements the governed BOM write API on top of the read-only BOM foundation (MMD-BE-05) and the BOM write governance contract (MMD-BE-09, MMD-BE-09A).

**Included:**
- 7 BOM mutation endpoints (create, update, release, retire, add/update/remove item)
- Authorization enforcement via `admin.master_data.bom.manage` action code
- Audit event emission for all mutations
- Full write schema validation (extra fields forbidden, lifecycle_status not client-settable)
- BOM lifecycle state machine enforcement (DRAFT → RELEASED → RETIRED)
- BOM item governance (DRAFT-only mutations, quantity > 0, scrap_factor ≥ 0, no circular BOM)

**Excluded (boundary guardrails enforced):**
- No hard delete of BOM header
- No reactivate, clone, bind-product-version endpoints
- No product_version_id field or behavior
- No material reservation, backflush, ERP posting, inventory movement
- No bulk import, replace-items, or compound mutation endpoints
- No quality hold, traceability, or production reporting behavior
- No frontend source changes
- No DB migrations

## Baseline Evidence

- MMD-BE-09 governance contract: `docs/audit/mmd-be-09-bom-write-governance-contract.md`
- MMD-BE-09A action code registry: `docs/audit/mmd-be-09a-bom-action-code-registry-patch.md`
- Action code `admin.master_data.bom.manage` confirmed in `backend/app/security/rbac.py`
- BOM models: `backend/app/models/bom.py` — `Bom`, `BomItem` confirmed schema-stable
- No `product_version_id`, no backflush/ERP fields in DB schema

## BOM Write Contract

### Lifecycle State Machine

```
DRAFT  →  RELEASED  →  RETIRED
  ↓                       ↑
RETIRED ←─────────────────
```

- **DRAFT**: all mutations allowed; items can be added/updated/removed
- **RELEASED**: no metadata updates; no item mutations; can be retired
- **RETIRED**: terminal; no further transitions except through new BOM creation
- BOM cannot be released with zero items
- BOM code is immutable after creation (only enforced at service layer, no rename endpoint)

### BOM Item Governance

- `component_product_id` and `line_no` are immutable after creation
- `quantity` must be > 0
- `scrap_factor` must be ≥ 0
- `unit_of_measure` must be non-empty
- Component product must exist in the same tenant
- Component product must not equal the parent product (circular BOM guard)
- `line_no` must be unique per BOM

## API Contract

All endpoints are under `/api/v1/products/{product_id}/boms`.

| Method   | Path                                    | Status | Request Body        | Response Body   |
|----------|-----------------------------------------|--------|---------------------|-----------------|
| POST     | `/{product_id}/boms`                    | 201    | `BomCreateRequest`  | `BomItem`       |
| PATCH    | `/{product_id}/boms/{bom_id}`           | 200    | `BomUpdateRequest`  | `BomItem`       |
| POST     | `/{product_id}/boms/{bom_id}/release`   | 200    | (none)              | `BomItem`       |
| POST     | `/{product_id}/boms/{bom_id}/retire`    | 200    | (none)              | `BomItem`       |
| POST     | `/{product_id}/boms/{bom_id}/items`     | 201    | `BomItemCreateRequest` | `BomComponentItem` |
| PATCH    | `/{product_id}/boms/{bom_id}/items/{bom_item_id}` | 200 | `BomItemUpdateRequest` | `BomComponentItem` |
| DELETE   | `/{product_id}/boms/{bom_id}/items/{bom_item_id}` | 204 | (none)          | (none)          |

### Error Codes

| Code | Condition                                           |
|------|-----------------------------------------------------|
| 400  | Business rule violation (wrong state, invalid data) |
| 403  | Missing `admin.master_data.bom.manage` action       |
| 404  | Product or BOM or BomItem not found in tenant       |
| 409  | Duplicate bom_code or duplicate line_no             |
| 422  | Schema validation failure (extra fields, bad types) |

### Write Schema Rules

**`BomCreateRequest`** — fields: `bom_code`, `bom_name`, `effective_from`, `effective_to`, `description`
- `extra="forbid"` — rejects `lifecycle_status`, `product_version_id`, any unknown field
- Date range validator: `effective_from <= effective_to` when both provided
- `lifecycle_status` is always set to `"DRAFT"` by service — not client-settable

**`BomUpdateRequest`** — fields: `bom_name`, `effective_from`, `effective_to`, `description`
- `extra="forbid"` — rejects `lifecycle_status`, `bom_code`, `product_version_id`
- Uses `model_fields_set` for null-safe partial update of optional fields

**`BomItemCreateRequest`** — fields: `component_product_id`, `line_no`, `quantity`, `unit_of_measure`, `scrap_factor`, `reference_designator`, `notes`
- `extra="forbid"`

**`BomItemUpdateRequest`** — fields: `quantity`, `unit_of_measure`, `scrap_factor`, `reference_designator`, `notes`
- `extra="forbid"` — intentionally excludes `component_product_id` and `line_no` (immutable per governance)
- Uses `model_fields_set` for null-safe partial update

## Authorization Enforcement

- All 7 mutation endpoints use `require_action("admin.master_data.bom.manage")`
- BOM read endpoints (`GET /{product_id}/boms`, `GET /{product_id}/boms/{bom_id}`) use `require_authenticated_identity` only — no `require_action` gate
- Authorization is server-side; frontend cannot bypass
- Action code `admin.master_data.bom.manage` is registered in `ACTION_CODE_REGISTRY` in `backend/app/security/rbac.py` (added by MMD-BE-09A)

## Audit Event Emission

All mutations call `record_security_event()` via helper functions:

| Operation     | `event_type`       | `resource_type` |
|---------------|--------------------|-----------------|
| Create BOM    | `BOM.CREATED`      | `bom`           |
| Update BOM    | `BOM.UPDATED`      | `bom`           |
| Release BOM   | `BOM.RELEASED`     | `bom`           |
| Retire BOM    | `BOM.RETIRED`      | `bom`           |
| Add Item      | `BOM_ITEM.ADDED`   | `bom_item`      |
| Update Item   | `BOM_ITEM.UPDATED` | `bom_item`      |
| Remove Item   | `BOM_ITEM.REMOVED` | `bom_item`      |

`changed_fields` JSON is recorded for UPDATE events. For REMOVE, the event is emitted **before** `delete_bom_item_row` to ensure audit integrity.

## Files Changed

### Backend

| File | Change |
|------|--------|
| `backend/app/schemas/bom.py` | Added 4 write schemas (`BomCreateRequest`, `BomUpdateRequest`, `BomItemCreateRequest`, `BomItemUpdateRequest`) |
| `backend/app/repositories/bom_repository.py` | Added 9 write functions (`get_bom_by_code`, `get_bom_row`, `create_bom_row`, `update_bom_row`, `get_bom_item_by_id`, `get_bom_item_by_line_no`, `create_bom_item_row`, `update_bom_item_row`, `delete_bom_item_row`) |
| `backend/app/services/bom_service.py` | Added private helpers + 7 write service functions; updated imports |
| `backend/app/api/v1/products.py` | Added 7 new write endpoints + imports |

### Tests

| File | Change |
|------|--------|
| `backend/tests/test_bom_foundation_api.py` | Added 35 write API tests; updated `_mk_bom` helper; updated route-existence guards; added `_override_bom_manage` and `_make_managed_app` helpers; set `expire_on_commit=False` on test session factory |
| `backend/tests/test_bom_foundation_service.py` | Added 13 service write tests covering all validation invariants; updated imports |
| `backend/tests/test_mmd_rbac_action_codes.py` | Replaced scope guard tests (MMD-BE-09A) with post-implementation route existence and forbidden-route tests |

### No Changes

- No DB migrations
- No frontend source files
- No `docs/design/` authoritative docs
- No model changes

## Boundary Guardrails Verified

| Guardrail | Enforcement | Verified By |
|-----------|-------------|-------------|
| No hard delete BOM header | No `DELETE /{product_id}/boms/{bom_id}` route | `test_no_bom_hard_delete_reactivate_clone_bind_product_version_routes_exist` |
| No reactivate | No POST `.../reactivate` route | Same test |
| No clone | No POST `.../clone` route | Same test |
| No bind-product-version | No POST `.../bind-product-version` route | Same test |
| No product_version_id in schema | `BomCreateRequest` rejects it (extra=forbid) | `test_create_bom_rejects_product_version_id_payload`, `test_no_product_version_binding_field_or_behavior` |
| No lifecycle_status settable by client | Schema rejects it (extra=forbid) | `test_create_bom_rejects_lifecycle_status_payload`, `test_update_bom_rejects_lifecycle_status_patch` |
| No backflush/ERP fields in DB | `Bom.__table__.columns` check | `test_bom_model_has_no_backflush_or_erp_fields` |
| BOM item immutable fields (component_id, line_no) | `BomItemUpdateRequest` excludes them | Schema definition |
| Circular BOM guard | Service rejects component == parent | `test_add_bom_item_rejects_parent_as_component`, `test_component_product_cannot_equal_parent_product` |
| DRAFT-only item mutations | Service enforces lifecycle_status == DRAFT | All item write tests |
| Release requires items | Service validates `row.items` non-empty | `test_release_bom_requires_items`, `test_release_only_draft` |

## Verification Commands

```powershell
# BOM foundation tests (66 tests)
cd g:\Work\FleziBCG\backend
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_bom_foundation_api.py tests/test_bom_foundation_service.py

# RBAC action code tests (24 tests)
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_mmd_rbac_action_codes.py

# Regression: product/version/reason code APIs
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_reason_code_foundation_api.py
```

## Remaining Risks / Deferred Items

| Item | Deferred To | Reason |
|------|-------------|--------|
| BOM code immutability enforcement at DB level | Post-MMD-BE-12 | No DB migration in scope |
| `line_no` uniqueness at DB constraint level | Post-MMD-BE-12 | No DB migration in scope |
| BOM clone / copy-as-draft workflow | Future milestone | Out of scope per governance contract |
| Product version binding | Future milestone | Explicitly deferred per governance contract §7 |
| Effective date conflict detection across BOMs for same product | Future milestone | Governance contract defers this |
| Material/backflush/ERP integration | Production execution milestones | Hard-excluded from master data foundation |
| Frontend BOM management UI | Separate milestone | Backend-only story |

## Final Verdict

**PASS** — MMD-BE-12 is complete.

- All 7 governed write endpoints implemented
- All endpoints require `admin.master_data.bom.manage` action
- BOM read endpoints remain authenticated-read only (no action gate)
- Lifecycle state machine enforced in service layer
- Write schemas use `extra="forbid"` — no lifecycle_status or product_version_id injection possible
- Audit events emitted for all 7 mutation types
- 66 tests pass (35 new API tests + 13 new service tests + 18 existing BOM tests)
- 24 RBAC tests pass (scope guards updated)
- 49 regression tests pass (product/version/reason code APIs unaffected)
- No DB migrations, no frontend changes, no model changes
- All boundary guardrails for deferred behavior are enforced and tested
