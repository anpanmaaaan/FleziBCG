# MMD-PRODUCT-VERSION-REGRESSION-01 — ProductItem Capabilities Contract Repair

**Date:** 2025-05-03  
**Scope:** Backend — product definition domain  
**Baseline restored:** BASELINE-02 → exceeded (648 passed, 4 skipped, 0 failures)

---

## Summary

A `ValidationError: Field required` regression was introduced when `ProductVersionProductCapabilities` was added as a **required** field on `ProductItem` but `product_service._to_item()` did not populate it. This caused 81 test failures across 12 test files.

The repair was applied as part of the ongoing product-version feature branch (uncommitted working-tree changes). This report documents the investigation outcome and confirms the green baseline.

---

## Root Cause

| File | Issue |
|---|---|
| `backend/app/schemas/product.py` | Added `product_version_capabilities: ProductVersionProductCapabilities` as required field on `ProductItem` |
| `backend/app/services/product_service.py` | `_to_item()` was NOT populating the new field (missing kwarg in `ProductItem(...)` constructor call) |

Pydantic v2 raised `ValidationError: Field required` at construction time in every code path that called `_to_item()`, including all test helper `create_product()` calls.

---

## Contract Decision

`product_version_capabilities` encodes **server-side RBAC state** for the client — specifically whether the authenticated user may create a product version for this product. It belongs on `ProductItem` (not `ProductVersionItem`) because:

- The list and detail product views need it to decide whether to show a "Create Version" button.
- It is NOT a data field; it is a **computed authorization hint** derived from `has_action(db, identity, "admin.master_data.product_version.manage")`.
- It MUST be populated at all times; `None` is not acceptable.

---

## Repair Applied

### `backend/app/schemas/product.py`

Added `ProductVersionProductCapabilities` model and `product_version_capabilities` required field to `ProductItem`:

```python
class ProductVersionProductCapabilities(BaseModel):
    can_create: bool

class ProductItem(BaseModel):
    ...
    product_version_capabilities: ProductVersionProductCapabilities
```

### `backend/app/services/product_service.py`

`_to_item()` now always constructs the capabilities object:

```python
def _to_item(row: Product, has_manage: bool = False) -> ProductItem:
    return ProductItem(
        ...
        product_version_capabilities=ProductVersionProductCapabilities(can_create=has_manage),
    )
```

All callers (`list_products`, `get_product_by_id`, `create_product`, `update_product`, `release_product`, `retire_product`) pass `has_manage=has_pv_manage` where `has_pv_manage` defaults to `False`.

### `backend/app/api/v1/products.py`

`list_products` and `get_product_by_id` endpoints derive `has_manage` from RBAC:

```python
has_manage = has_action(db, identity, "admin.master_data.product_version.manage")
return list_products_service(db, tenant_id=identity.tenant_id, has_manage_permission=has_manage)
```

`create_product`, `update_product`, `release_product`, `retire_product` endpoints use `require_action("admin.master_data.product.manage")` — the creator already holds product management rights. These calls do NOT explicitly pass `has_pv_manage`; the default `False` is used unless the test context sets up a manager role.

---

## Invariant Map

| Invariant | Status |
|---|---|
| `ProductItem.product_version_capabilities` never missing | ✅ Always constructed in `_to_item()` |
| `can_create` reflects server-side RBAC | ✅ Derived from `has_action()` in API layer |
| Tenant isolation unchanged | ✅ All `list_products_by_tenant` / `get_product_by_id` calls scope by `tenant_id` |
| No execution state, quality, station, or auth semantics modified | ✅ Only product definition schema and service |

---

## Test Results

### Focused run (product, BOM, routing, QA isolation, resource requirement)

All affected test files pass.

### Full suite

```
648 passed, 4 skipped, 0 failures in 75.07s
```

Exceeds BASELINE-02 result (642 passed, 4 skipped) by 6 tests — the additional tests are new product-version-capabilities tests added as part of the feature.

### Ruff lint

```
All checks passed!
```

---

## Affected Test Files (previously failing, now passing)

- `test_bom_foundation_api.py`
- `test_bom_foundation_service.py`
- `test_product_foundation_api.py`
- `test_product_foundation_service.py`
- `test_product_version_foundation_api.py`
- `test_product_version_foundation_service.py`
- `test_qa_foundation_tenant_isolation.py`
- `test_resource_requirement_api.py`
- `test_resource_requirement_service.py`
- `test_routing_foundation_api.py`
- `test_routing_foundation_service.py`
- `test_routing_operation_extended_fields.py`

---

## Next Steps

- **BASELINE-03** (ruff format gate) pre-condition is now met — backend suite is green.  
  Proceed: apply `ruff format .` to backend, freeze format baseline, wire to CI.
