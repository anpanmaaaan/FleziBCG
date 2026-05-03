# MMD-FULLSTACK-11C — Product-Level Product Version Create Capability Projection

**Date:** 2025-07-14  
**Scope:** Backend schema + service + route handler + frontend type + create button gate + regression guards  
**Hard Mode MOM v3:** Applied  
**Status:** COMPLETE (patched by MMD-FULLSTACK-11C-A)

---

## Capability Truth Patch — MMD-FULLSTACK-11C-A

**Date:** 2026-05-03

### Problem

After MMD-FULLSTACK-11C, all 4 Product write service functions (`create_product`, `update_product`, `release_product`, `retire_product`) returned `_to_item(row, has_manage=True)` unconditionally. This meant any caller who passed `admin.master_data.product.manage` (the Product write action) would receive `product_version_capabilities.can_create=true` in the response — regardless of whether they actually hold `admin.master_data.product_version.manage`.

**Invariant violated:** `can_create=true` iff `has_action(..., "admin.master_data.product_version.manage")` — `product.manage` is a separate, non-implying permission.

### Fix Applied (Option A)

1. **`backend/app/services/product_service.py`** — Added `has_pv_manage: bool = False` parameter to `create_product`, `update_product`, `release_product`, `retire_product`. Each passes `has_manage=has_pv_manage` to `_to_item`. Default is `False` (conservative).

2. **`backend/app/api/v1/products.py`** — All 4 write handlers now compute:
   ```python
   has_pv_manage = has_action(db, identity, "admin.master_data.product_version.manage")
   ```
   and pass `has_pv_manage=has_pv_manage` to the service.

3. **`backend/tests/test_product_foundation_api.py`** — Added 2 new tests:
   - `test_product_write_response_can_create_false_when_no_pv_manage`: proves create/update/release/retire return `can_create=false` when `product_version.manage` is absent
   - `test_product_write_response_can_create_true_when_has_pv_manage`: proves create/update/release return `can_create=true` when `product_version.manage` is present

### Verification (11C-A)

| Check | Result |
|---|---|
| `pytest test_product_foundation_api.py ...` | **69 passed, 1 warning** (+2 from 11C) |
| `npm run check:mmd:read` | **105 passed, 0 failed** |
| `npm run build` | **PASS** |
| `npm run lint` | **PASS** (0 errors) |
| `npm run lint:i18n:registry` | **PASS** (1770 keys) |

---

## Problem Statement

The create button for Product Versions in `ProductDetail.tsx` was gated by:

```tsx
disabled={mutationBusyKey !== null || (versions.length > 0 && !versions[0].allowed_actions.can_create_sibling)}
```

When `versions.length === 0` (first-use / empty-version-list case), the condition short-circuited to `false`, enabling the button regardless of the user's actual permissions. The create guard was derived from row-level allowed_actions on a specific version, which does not exist before any version is created.

---

## Root Cause

`allowed_actions` (MMD-FULLSTACK-11B) is row-scoped to a product version. It answers "can this version be acted upon?" — not "can a new version be created for this product?". These are semantically different questions answered at different resource levels.

The first-use case (no versions yet) required a product-level capability from the server.

---

## Design Decision

Add `product_version_capabilities.can_create` to the **Product Detail response** (`GET /products/{product_id}`). This field is server-computed from `has_action(db, identity, "admin.master_data.product_version.manage")`, the same RBAC action that gates the write endpoints.

The `GET /products` list endpoint also carries this capability for consistency.

---

## Changes

### Backend — `backend/app/schemas/product.py`
- Added `class ProductVersionProductCapabilities(BaseModel): can_create: bool`
- Added `product_version_capabilities: ProductVersionProductCapabilities` to `ProductItem`

### Backend — `backend/app/services/product_service.py`
- Imported `ProductVersionProductCapabilities`
- Updated `_to_item(row, has_manage: bool = False)` to include `product_version_capabilities`
- Updated `list_products(db, *, tenant_id, has_manage_permission=False)` to accept and propagate capability
- Updated `get_product_by_id(db, *, tenant_id, product_id, has_manage_permission=False)` same pattern
- Write service functions (`create_product`, `update_product`, `release_product`, `retire_product`) pass `has_manage=True` — actor already passed `require_action` gate

### Backend — `backend/app/api/v1/products.py`
- Updated `list_products` handler: calls `has_action(db, identity, "admin.master_data.product_version.manage")` and passes `has_manage_permission=has_manage` to service
- Updated `get_product_by_id` handler: same pattern

### Backend Tests — `backend/tests/test_product_foundation_api.py`
- Updated `_build_app(identity, has_manage=False)` to monkey-patch `product_router_module.has_action`
- Added 4 new tests:
  - `test_product_detail_includes_product_version_capabilities_field`
  - `test_product_detail_can_create_false_for_non_manage_user`
  - `test_product_detail_can_create_true_for_manage_user`
  - `test_product_list_includes_product_version_capabilities`

### Frontend — `frontend/src/app/api/productApi.ts`
- Added `interface ProductVersionProductCapabilities { can_create: boolean }`
- Added `product_version_capabilities: ProductVersionProductCapabilities` to `ProductItemFromAPI`

### Frontend — `frontend/src/app/api/index.ts`
- Exported `ProductVersionProductCapabilities`

### Frontend — `frontend/src/app/pages/ProductDetail.tsx`
- Replaced create button gate:
  - **Before:** `disabled={mutationBusyKey !== null || (versions.length > 0 && !versions[0].allowed_actions.can_create_sibling)}`
  - **After:** `disabled={mutationBusyKey !== null || !product.product_version_capabilities.can_create}`

### Frontend — `frontend/scripts/mmd-read-integration-regression-check.mjs`
- Added guards G20–G24:
  - G20: `ProductVersionProductCapabilities` type exists in `productApi.ts`
  - G21: `ProductItemFromAPI` includes `product_version_capabilities` field
  - G22: `ProductDetail` uses `product.product_version_capabilities.can_create`
  - G23: `ProductDetail` does NOT use `versions[0].allowed_actions.can_create_sibling` as primary create gate
  - G24: No persona-based create inference in `ProductDetail`

---

## Verification Results

| Check | Result |
|---|---|
| `pytest test_product_foundation_api.py test_product_version_foundation_api.py ...` | **67 passed, 1 warning** (+7 from 11B baseline) |
| `npm run check:mmd:read` | **105 passed, 0 failed** (+5 from 11B baseline) |
| `npm run build` | **PASS** (built in 8.70s) |
| `npm run lint` | **PASS** (0 errors) |
| `npm run lint:i18n:registry` | **PASS** (1770 keys EN/JA synchronized) |

---

## Invariants Preserved

- Backend mutation endpoint (`POST /products/{id}/versions`) still requires `require_action("admin.master_data.product_version.manage")` — server is final authority
- Read endpoint remains `require_authenticated_identity` — no escalation
- `has_action` is a pure bool; no `require_action` added to read handlers
- No client-side role-based inference
- No persona-based create gate
- First-use case (empty version list) correctly gated by server-derived capability
