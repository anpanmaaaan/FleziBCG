# MMD-BE-09A — BOM Action Code Registry Patch — Audit Report

**Slice ID:** MMD-BE-09A  
**Status:** COMPLETE — PASSED ALL GATES  
**Date:** 2025  
**Author:** AI Agent (Hard Mode MOM v3)  
**Depends on:** MMD-BE-09 (BOM Write Governance Contract)  
**Required by:** MMD-BE-12 (BOM Write API Implementation)

---

## 1. Objective

Register `admin.master_data.bom.manage` in `ACTION_CODE_REGISTRY` in `backend/app/security/rbac.py` as a hard prerequisite for BOM write API implementation (MMD-BE-12). No BOM write endpoints are created in this slice — only the action code is registered.

---

## 2. Hard Mode MOM v3 Evidence

### 2.1 Design Evidence Extract

| Source | Finding |
|---|---|
| `docs/design/02_domain/product_definition/bom-write-governance-contract.md` (MMD-BE-09) | Explicitly requires `admin.master_data.bom.manage` as the action code for all BOM mutation operations |
| `backend/app/security/rbac.py` (lines 58–61, pre-patch) | 4 MMD codes present: `product.manage`, `product_version.manage`, `routing.manage`, `resource_requirement.manage`. `bom.manage` ABSENT |
| `docs/design/02_registry/action-code-registry.md` (pre-patch) | 4 MMD entries; BOM row ABSENT |
| `backend/app/api/v1/products.py` (lines 246, 262) | Only `GET /{product_id}/boms` and `GET /{product_id}/boms/{bom_id}` exist — both use `require_authenticated_identity`; no `require_action` |

### 2.2 Event Map

| Change | Expected Event / Side Effect | Forbidden Side Effects |
|---|---|---|
| Add `admin.master_data.bom.manage` to `ACTION_CODE_REGISTRY` | Code becomes evaluable by `has_action()` / `require_action()` for future BOM mutation routes | No endpoint change; no new route; no DB migration; no frontend change; no BOM write behavior |
| Add 5 new tests to `test_mmd_rbac_action_codes.py` | Tests pass; future regressions caught | No behavioral change |
| Update `action-code-registry.md` | Documentation reflects runtime truth | No runtime change |

### 2.3 Invariant Map

| Invariant | Enforcement |
|---|---|
| `admin.master_data.bom.manage` maps to ADMIN family | `test_bom_manage_action_code_is_domain_specific` |
| Code exists in registry | `test_bom_manage_action_code_exists` |
| BOM read endpoints do not use `require_action` | `test_bom_read_endpoints_do_not_require_manage_action` |
| No BOM write routes exist yet | `test_no_bom_write_routes_exist_yet` + `test_bom_routes_do_not_expose_write_methods` (foundation) |
| No BOM item write routes exist yet | `test_no_bom_item_write_routes_exist_yet` |
| Existing 4 MMD codes unchanged | All pre-existing `test_mmd_rbac_action_codes.py` tests pass |
| No DB/migration changes | Scope constraint — no Alembic files touched |
| No frontend changes | Scope constraint — no frontend files touched |

### 2.4 State Transition Map

Not applicable. `ACTION_CODE_REGISTRY` is a static dict. Change is purely additive.

### 2.5 Authorization Contract Map

| Route | Required Code | State (this slice) |
|---|---|---|
| `POST /products/{id}/boms` | `admin.master_data.bom.manage` | Not yet implemented — MMD-BE-12 |
| `PATCH /products/{id}/boms/{bom_id}` | `admin.master_data.bom.manage` | Not yet implemented — MMD-BE-12 |
| `POST /products/{id}/boms/{bom_id}/release` | `admin.master_data.bom.manage` | Not yet implemented — MMD-BE-12 |
| `GET /products/{id}/boms` | none (authenticated read) | Implemented — unchanged |
| `GET /products/{id}/boms/{bom_id}` | none (authenticated read) | Implemented — unchanged |

**Verdict:** All invariants verifiable. Change is minimal and isolated. Proceeded.

---

## 3. Files Changed

### 3.1 `backend/app/security/rbac.py`

**Change:** Added one line to the MMD block in `ACTION_CODE_REGISTRY`.

**Before (lines 58–61):**
```python
"admin.master_data.product.manage": "ADMIN",
"admin.master_data.product_version.manage": "ADMIN",
"admin.master_data.routing.manage": "ADMIN",
"admin.master_data.resource_requirement.manage": "ADMIN",
```

**After (lines 58–62):**
```python
"admin.master_data.product.manage": "ADMIN",
"admin.master_data.product_version.manage": "ADMIN",
"admin.master_data.routing.manage": "ADMIN",
"admin.master_data.resource_requirement.manage": "ADMIN",
"admin.master_data.bom.manage": "ADMIN",
```

### 3.2 `backend/tests/test_mmd_rbac_action_codes.py`

**Change:** Added 5 new test functions after the existing Product Version scope guard test.

| New Test | Purpose |
|---|---|
| `test_bom_manage_action_code_exists` | Registry presence check |
| `test_bom_manage_action_code_is_domain_specific` | Family check; IAM separation check |
| `test_bom_read_endpoints_do_not_require_manage_action` | BOM GET routes must not use `require_action` |
| `test_no_bom_write_routes_exist_yet` | Scope guard — BOM write endpoints (MMD-BE-12 deferred) |
| `test_no_bom_item_write_routes_exist_yet` | Scope guard — BOM item write endpoints (MMD-BE-12 deferred) |

### 3.3 `docs/design/02_registry/action-code-registry.md`

**Change:** Added BOM row to MMD table:

```markdown
| `admin.master_data.bom.manage` | ADMIN | Create, update, add/remove items, release, or retire a BOM (when write APIs are enabled by MMD-BE-12) |
```

---

## 4. Verification Results

### 4.1 `test_mmd_rbac_action_codes.py`

```
23 passed, 1 warning in 1.46s
```

All 23 tests pass. 5 new BOM tests included.

### 4.2 BOM Foundation Tests

```
20 passed, 1 warning in 2.18s
```

`test_bom_foundation_api.py` (11) + `test_bom_foundation_service.py` (9) — no regression.

---

## 5. Scope Constraints Enforced

| Constraint | Status |
|---|---|
| No BOM write endpoints added | VERIFIED — `test_no_bom_write_routes_exist_yet` PASSES |
| No BOM item write endpoints added | VERIFIED — `test_no_bom_item_write_routes_exist_yet` PASSES |
| No DB migration touched | VERIFIED — no Alembic changes |
| No frontend files touched | VERIFIED — no frontend changes |
| No other rbac.py codes modified | VERIFIED — existing 4 MMD codes unchanged |

---

## 6. Out-of-Scope Note: `admin.master_data.reason_code.manage`

A review of `backend/app/security/rbac.py` confirms that `admin.master_data.reason_code.manage` does **not** currently exist in the registry. This code was referenced in MMD-BE-09A planning notes but is not an existing code to preserve in this slice. It must not be added here — it belongs to a separate governance slice when reason code mutation APIs are implemented.

---

## 7. Next Steps

| Slice | Depends on | Description |
|---|---|---|
| MMD-BE-12 | MMD-BE-09A (this slice) | BOM Write API — `POST /products/{id}/boms`, `PATCH`, lifecycle commands, item management |

Before MMD-BE-12 begins, the agent must re-verify:
1. `admin.master_data.bom.manage` is still present in `ACTION_CODE_REGISTRY`
2. `test_no_bom_write_routes_exist_yet` still passes (confirming scope was not jumped)
3. `docs/design/02_domain/product_definition/bom-write-governance-contract.md` for full command/invariant specification

---

*Report generated under Hard Mode MOM v3. All gates passed. Change is production-safe.*
