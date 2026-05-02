# MMD-BE-02 — RBAC Action Code Fix for MMD Master Data Mutations

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Replaced placeholder authorization action codes on MMD mutation endpoints with MMD-specific action codes. |

---

## 1. Scope

Backend-only governance hardening slice.

Replaced `admin.user.manage` (an IAM user-management action code) with domain-specific
MMD action codes on all Product, Routing, and Resource Requirement mutation endpoints.

Authorization action-code identity changed on all 14 MMD mutation endpoints — from the placeholder IAM code `admin.user.manage` to MMD-specific codes — while effective permission family remains `ADMIN`.
No request/response schema, model, migration, endpoint path, or frontend runtime behavior changed.
No new endpoints or domain functionality were added.

---

## 2. Baseline Evidence Used

| Document | Status |
|---|---|
| `docs/audit/mmd-audit-00-fullstack-source-alignment.md` | Read |
| `docs/audit/mmd-be-00-evidence-and-contract-lock.md` | Read |
| `docs/audit/mmd-be-01-hard-mode-evidence-pack.md` | Read |
| `docs/audit/mmd-read-baseline-01-read-integration-freeze-handoff.md` | Read |
| `docs/audit/mmd-fullstack-05-mmd-read-integration-regression-tests.md` | Read |
| `backend/app/security/rbac.py` — `ACTION_CODE_REGISTRY` confirmed | Inspected |
| `backend/app/api/v1/products.py` — 4 mutations using `admin.user.manage` | Confirmed |
| `backend/app/api/v1/routings.py` — 10 mutations using `admin.user.manage` | Confirmed |
| `docs/design/02_registry/action-code-registry.md` | DID NOT EXIST — created by this slice |

---

## 3. Authorization Contract Map

| Area | Previous Action Code | New Action Code | Endpoints Changed |
|---|---|---|---|
| Product mutations | `admin.user.manage` | `admin.master_data.product.manage` | POST /products, PATCH /products/{id}, POST /products/{id}/release, POST /products/{id}/retire |
| Routing mutations | `admin.user.manage` | `admin.master_data.routing.manage` | POST /routings, PATCH /routings/{id}, POST /routings/{id}/operations, PATCH /routings/{id}/operations/{op_id}, DELETE /routings/{id}/operations/{op_id}, POST /routings/{id}/release, POST /routings/{id}/retire |
| Resource Requirement mutations | `admin.user.manage` | `admin.master_data.resource_requirement.manage` | POST .../resource-requirements, PATCH .../resource-requirements/{req_id}, DELETE .../resource-requirements/{req_id} |
| Product reads | `require_authenticated_identity` | (unchanged) | GET /products, GET /products/{id} |
| Routing reads | `require_authenticated_identity` | (unchanged) | GET /routings, GET /routings/{id}, GET .../resource-requirements, GET .../resource-requirements/{req_id} |

All 3 new action codes map to the `ADMIN` PermissionFamily — same as `admin.user.manage`.
Existing ADM/OTS roles retain equivalent access. No role redefinition was required.

---

## 4. Files Changed

| File | Change Type |
|---|---|
| `backend/app/security/rbac.py` | Modified — added 3 MMD action codes to `ACTION_CODE_REGISTRY` |
| `backend/app/api/v1/products.py` | Modified — 4 occurrences: `admin.user.manage` → `admin.master_data.product.manage` |
| `backend/app/api/v1/routings.py` | Modified — 7 occurrences: `admin.user.manage` → `admin.master_data.routing.manage`; 3 occurrences: `admin.user.manage` → `admin.master_data.resource_requirement.manage` |
| `backend/tests/test_mmd_rbac_action_codes.py` | Created — 12 regression tests |
| `docs/design/02_registry/action-code-registry.md` | Created — action code governance reference |
| `docs/audit/mmd-be-02-rbac-action-code-fix.md` | Created — this report |

---

## 5. Backend Changes

### `backend/app/security/rbac.py`

Added 3 entries to `ACTION_CODE_REGISTRY`:

```python
"admin.master_data.product.manage": "ADMIN",
"admin.master_data.routing.manage": "ADMIN",
"admin.master_data.resource_requirement.manage": "ADMIN",
```

### `backend/app/api/v1/products.py`

Replaced `require_action("admin.user.manage")` with `require_action("admin.master_data.product.manage")` on:
- `POST /products`
- `PATCH /products/{product_id}`
- `POST /products/{product_id}/release`
- `POST /products/{product_id}/retire`

### `backend/app/api/v1/routings.py`

Replaced `require_action("admin.user.manage")` with `require_action("admin.master_data.routing.manage")` on:
- `POST /routings`
- `PATCH /routings/{routing_id}`
- `POST /routings/{routing_id}/operations`
- `PATCH /routings/{routing_id}/operations/{operation_id}`
- `DELETE /routings/{routing_id}/operations/{operation_id}`
- `POST /routings/{routing_id}/release`
- `POST /routings/{routing_id}/retire`

Replaced `require_action("admin.user.manage")` with `require_action("admin.master_data.resource_requirement.manage")` on:
- `POST /routings/{routing_id}/operations/{operation_id}/resource-requirements`
- `PATCH /routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}`
- `DELETE /routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}`

---

## 6. Tests Added / Updated

### New: `backend/tests/test_mmd_rbac_action_codes.py` — 12 tests

| Test | Asserts |
|---|---|
| `test_product_action_code_in_registry` | `admin.master_data.product.manage` in `ACTION_CODE_REGISTRY` |
| `test_product_action_code_is_admin_family` | maps to `ADMIN` |
| `test_routing_action_code_in_registry` | `admin.master_data.routing.manage` in `ACTION_CODE_REGISTRY` |
| `test_routing_action_code_is_admin_family` | maps to `ADMIN` |
| `test_resource_requirement_action_code_in_registry` | `admin.master_data.resource_requirement.manage` in `ACTION_CODE_REGISTRY` |
| `test_resource_requirement_action_code_is_admin_family` | maps to `ADMIN` |
| `test_admin_user_manage_not_in_product_mutations` | `admin.user.manage` absent from `products.py` |
| `test_admin_user_manage_not_in_routing_mutations` | `admin.user.manage` absent from `routings.py` |
| `test_product_endpoints_use_product_action_code` | ≥4 uses of product code in `products.py` |
| `test_routing_endpoints_use_routing_action_code` | ≥7 uses of routing code in `routings.py` |
| `test_resource_requirement_endpoints_use_rr_action_code` | ≥3 uses of RR code in `routings.py` |
| `test_read_endpoints_do_not_require_mutation_action_code` | No GET handler uses `require_action` |

---

## 7. Read Endpoint Impact

**No change.** All read (GET) endpoints continue to use `require_authenticated_identity`. This slice did not add `require_action` to any GET handler.

Verified by test `test_read_endpoints_do_not_require_mutation_action_code`.

---

## 8. Boundary Guardrails

| Guardrail | Status |
|---|---|
| No new endpoints added | ✅ |
| No DB migration added | ✅ |
| No schema changes | ✅ |
| No frontend runtime source changed | ✅ |
| No new domain functionality | ✅ |
| No Product Version / BOM / Work Center / Backflush / Quality implemented | ✅ |
| No broad RBAC redesign | ✅ — only `ACTION_CODE_REGISTRY` additions |
| ADM/OTS access preserved | ✅ — all 3 new codes map to `ADMIN` family |

---

## 9. Verification Commands

```bash
# New regression tests
cd backend
python -m pytest -q tests/test_mmd_rbac_action_codes.py
# Expected: 12 passed

# Existing targeted MMD backend tests
python -m pytest -q tests/test_product_foundation_api.py tests/test_routing_foundation_api.py tests/test_resource_requirement_api.py tests/test_routing_operation_extended_fields.py tests/test_resource_requirement_service.py tests/test_routing_foundation_service.py tests/test_product_foundation_service.py
# Expected: 33 passed

# Frontend MMD read regression (no FE breakage)
cd frontend
node scripts/mmd-read-integration-regression-check.mjs
# Expected: 47 passed

node scripts/route-smoke-check.mjs
# Expected: 24 PASS, 0 FAIL
```

### Actual Results

| Gate | Result |
|---|---|
| `test_mmd_rbac_action_codes.py` | ✅ 12 passed in 0.48s |
| Targeted MMD backend tests (7 files) | ✅ 33 passed in 2.40s |
| `mmd-read-integration-regression-check.mjs` | ✅ 47 passed |
| Route smoke check | ✅ PASS |

---

## 10. Remaining Risks / Deferred Items

| Item | Notes |
|---|---|
| Granular create/update/delete codes | Current registry uses single `.manage` verb per domain. If future RBAC requires create-only vs delete-only roles for MMD, codes can be split. Out of scope for this slice. |
| `admin.user.manage` remains in registry | Intentionally preserved — it is still used by IAM user management endpoints (not in scope of this slice). |
| DB-backed permission rows for new codes | Existing seed data grants `ADMIN` family-level access to ADM/OTS. New codes resolve via `ACTION_CODE_REGISTRY` → `ADMIN` family → same DB rows. No seed update needed. |
| `docs/design/02_registry/action-code-registry.md` | Created. Future slices must add new action codes here alongside `rbac.py`. |

---

## 11. Final Verdict

**MMD-BE-02 is complete.**

MMD mutation endpoints no longer share authorization with IAM user management actions.
Domain boundaries are explicitly enforced at the action-code level.
All 14 endpoint authorization action-code transitions are verified. All 12 regression tests pass.
No request/response schema, model, migration, endpoint path, or frontend runtime behavior changed.
