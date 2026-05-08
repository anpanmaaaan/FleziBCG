# MMD-FULLSTACK-14B — BOM Product Version Binding Server-Derived Capability Guard

**Slice:** MMD-FULLSTACK-14B  
**Status:** COMPLETE  
**Date:** 2025-07-08  
**Hard Mode MOM v3:** APPLIED — lifecycle-governed write capability projection, authorization semantics  

---

## Objective

Replace lifecycle-only frontend inference for binding button states with server-derived capabilities returned by the `GET bom-binding` endpoint. The backend now computes and returns `can_bind`, `can_unbind`, and `can_toggle_bom_binding_required_for_release` based on lifecycle + permissions; the frontend consumes these fields rather than deriving authorization from lifecycle status alone.

---

## Design Evidence

- Authorization is server-side (governance non-negotiable)
- Frontend sends intent only — never derives write authorization
- Capabilities are read-model projections: server computes them based on PV lifecycle + RBAC action code ownership
- GET endpoint returns 200 with `binding: null` when no active binding exists (no longer 404)

---

## Changes Made

### Backend

**`backend/app/schemas/product.py`**
- Added `ProductVersionBomBindingCapabilities` (fields: `can_bind`, `can_unbind`, `can_toggle_bom_binding_required_for_release`, `reason?`)
- Renamed `ProductVersionBomBindingResponse` → `ProductVersionBomBindingData` (existing binding data shape, returned by POST)
- Added new `ProductVersionBomBindingResponse` as GET wrapper: `{ product_id, product_version_id, binding: ProductVersionBomBindingData | None, capabilities: ProductVersionBomBindingCapabilities }`

**`backend/app/services/product_version_bom_binding_service.py`**
- Added `_compute_capabilities(pv_lifecycle, has_active_binding, has_pv_manage, has_bom_manage)` — pure function, no side effects
- Added `_to_binding_data()` (renamed from `_to_binding_response()`)
- Updated `get_product_version_bom_binding()`: accepts `has_pv_manage` and `has_bom_manage` separately; returns `ProductVersionBomBindingResponse` wrapper; returns 200 with `binding=None` when no active binding (no longer raises `LookupError` for missing binding)
- Updated `bind_bom_to_product_version()` return type → `ProductVersionBomBindingData`

**`backend/app/api/v1/products.py`**
- GET `get_bom_binding`: passes `has_pv_manage=has_pv_manage, has_bom_manage=has_bom_manage` (separate, not combined)
- POST `bind_bom`: `response_model=ProductVersionBomBindingData`
- Imported `ProductVersionBomBindingData`

### Backend Tests

**`backend/tests/test_bom_binding_api.py`**
- Updated `test_get_binding_after_create_returns_200`: assertions now use `data["binding"]["bom_id"]` etc. (wrapper shape)
- Replaced `test_get_binding_after_unbind_returns_404` → `test_get_binding_when_no_binding_returns_200_with_null` (behavioral change: GET returns 200 + `binding: null`)
- Updated `test_get_binding_allowed_actions_*`: assertions use `data["binding"]["allowed_actions"]`
- Added 11 new tests:
  - `test_get_bom_binding_includes_capabilities`
  - `test_get_bom_binding_capabilities_manage_user_draft_no_binding_can_bind`
  - `test_get_bom_binding_capabilities_manage_user_draft_with_binding_can_unbind`
  - `test_get_bom_binding_capabilities_non_manage_user_all_false`
  - `test_get_bom_binding_capabilities_released_pv_all_false`
  - `test_get_bom_binding_capabilities_retired_pv_all_false`
  - `test_get_bom_binding_capability_can_toggle_requires_product_version_manage`
  - `test_get_bom_binding_capability_can_bind_requires_both_bom_and_pv_manage`
  - `test_get_bom_binding_capability_can_unbind_requires_both_bom_and_pv_manage`
  - `test_bom_binding_mutation_routes_still_require_both_action_codes`
  - `test_bom_binding_read_route_still_authenticated_read`

**`backend/tests/test_mmd_rbac_action_codes.py`**
- Added `test_bom_binding_get_response_schema_includes_capabilities` (source-level contract for all new schema fields)

### Frontend

**`frontend/src/app/api/productApi.ts`**
- Added `ProductVersionBomBindingCapabilities` interface
- Added `ProductVersionBomBindingData` interface (binding data — returned by POST)
- Redefined `ProductVersionBomBindingResponse` as GET wrapper: `{ product_id, product_version_id, binding: ProductVersionBomBindingData | null, capabilities: ProductVersionBomBindingCapabilities }`
- `bindBomToProductVersion` return type → `ProductVersionBomBindingData`

**`frontend/src/app/api/index.ts`**
- Added exports: `ProductVersionBomBindingCapabilities`, `ProductVersionBomBindingData`

**`frontend/src/app/pages/ProductDetail.tsx`**
- Added `capabilities` state (`ProductVersionBomBindingCapabilities | null`)
- `loadBinding`: sets both `binding` (full wrapper) and `capabilities`; removed 404 special-case (404 only triggers for PV-not-found)
- Replaced lifecycle-only gating:
  - `selectedVersionCanToggleFlag` ← `capabilities?.can_toggle_bom_binding_required_for_release`
  - `canShowBindIntent` ← `capabilities?.can_bind`
  - `canShowUnbindIntent` ← `capabilities?.can_unbind`
- `selectedBoundBom` derives from `binding?.binding?.bom_id`
- `selectedVersionReadiness` checks `binding?.binding` (not bare `binding`)
- JSX binding display uses `binding?.binding.*` fields
- `setCapabilities(null)` on version clear

**`frontend/scripts/mmd-read-integration-regression-check.mjs`**
- Added Section P (checks P1–P8):
  - P1: `ProductVersionBomBindingCapabilities` type exists
  - P2: `ProductVersionBomBindingResponse` includes `capabilities` field
  - P3: `ProductVersionBomBindingData` type exists
  - P4: ProductDetail consumes `capabilities?.can_bind`
  - P5: ProductDetail consumes `capabilities?.can_unbind`
  - P6: ProductDetail consumes `capabilities?.can_toggle_bom_binding_required_for_release`
  - P7: ProductDetail does not gate bind solely on lifecycle-only inference
  - P8: ProductDetail still handles 403

---

## Capability Logic

| Condition | `can_bind` | `can_unbind` | `can_toggle` |
|-----------|-----------|-------------|-------------|
| DRAFT + no binding + both perms | ✅ | ❌ | ✅ |
| DRAFT + active binding + both perms | ❌ | ✅ | ✅ |
| DRAFT + pv.manage only | ❌ | ❌ | ✅ |
| DRAFT + bom.manage only | ❌ | ❌ | ❌ |
| DRAFT + no perms | ❌ | ❌ | ❌ |
| RELEASED (any perms) | ❌ | ❌ | ❌ |
| RETIRED (any perms) | ❌ | ❌ | ❌ |

---

## Invariants Verified

1. Authorization is server-side — frontend receives computed booleans, does not derive from lifecycle
2. `can_bind` requires **both** `bom.manage` AND `pv.manage`
3. `can_unbind` requires **both** `bom.manage` AND `pv.manage`  
4. `can_toggle` requires `pv.manage` only
5. All capabilities are `false` when PV is not DRAFT
6. POST/DELETE mutation routes still gate on action codes (not weakened)
7. GET uses `require_authenticated_identity` only (read does not require manage)
8. GET returns 200 with `binding: null` when no active binding (PV-not-found still 404)

---

## Verification Results

### Backend Tests
```
74 passed, 0 failed in 8.38s
tests/test_bom_binding_api.py: 35 passed
tests/test_mmd_rbac_action_codes.py: 39 passed
```

### Frontend Regression
```
209 passed, 0 failed
Section P (14B checks): 8/8 PASS
```

### Frontend Build
- `npm run build`: ✅ (3409 modules transformed, no errors)
- `npm run lint`: ✅ (exit 0)
- `npm run lint:i18n:registry`: ✅ (1902 keys, en/ja parity)
- `npm run check:routes`: ✅ (exit 0)

---

## Files Changed

| File | Type | Change |
|------|------|--------|
| `backend/app/schemas/product.py` | BE schema | Added capabilities type, wrapper response, renamed Data type |
| `backend/app/services/product_version_bom_binding_service.py` | BE service | `_compute_capabilities`, `_to_binding_data`, updated GET service, return type fix |
| `backend/app/api/v1/products.py` | BE API | Separate pv/bom manage args, POST response_model updated |
| `backend/tests/test_bom_binding_api.py` | BE test | 11 new tests, 3 updated |
| `backend/tests/test_mmd_rbac_action_codes.py` | BE test | 1 new source-level contract test |
| `frontend/src/app/api/productApi.ts` | FE API | New types, wrapper response shape |
| `frontend/src/app/api/index.ts` | FE API | New exports |
| `frontend/src/app/pages/ProductDetail.tsx` | FE page | Capability-driven button gating |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | FE script | Section P (8 checks) |
