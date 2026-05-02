# MMD-BE-03 — Product Version Foundation Read Model

**Slice:** MMD-BE-03  
**Branch:** autocode  
**Hard Mode MOM:** v3 applied  
**Status:** PASS — all gates green

---

## 1. Summary

MMD-BE-03 introduces `ProductVersion` as the minimal backend read model for the Product Version foundation contract (P0-B MMD baseline). This slice adds the `product_versions` table, a migration, repository, service, schema, and two read-only API endpoints. No write-path, lifecycle workflow, BOM/Routing binding, or frontend changes are included.

**Scope guard confirmed:** 0 write endpoints for product versions in API registration (locked by regression test).

---

## 2. Pre-Coding Evidence Compliance

Hard Mode MOM v3 evidence tables were produced before coding:

- ✅ Design Evidence Extract
- ✅ Domain Contract Map
- ✅ Data Model / Migration Map
- ✅ API Contract Map
- ✅ Invariant Map
- ✅ Test Matrix
- ✅ Verdict: PROCEED (all stop conditions clear)

---

## 3. Files Changed

| File | Action | Notes |
|---|---|---|
| `backend/app/models/product_version.py` | Created | ORM model, `ProductVersion` class |
| `backend/alembic/versions/0007_product_versions.py` | Created | Migration, `down_revision = "0006"` |
| `backend/scripts/migrations/0018_product_versions.sql` | Created | SQL bootstrap |
| `backend/app/repositories/product_version_repository.py` | Created | `list_product_versions_by_product`, `get_product_version_by_id` |
| `backend/app/services/product_version_service.py` | Created | `list_product_versions`, `get_product_version` |
| `backend/app/schemas/product.py` | Modified | Added `date` import, `ProductVersionItem`, `_ALLOWED_VERSION_LIFECYCLE_STATUSES` |
| `backend/app/api/v1/products.py` | Modified | 2 read GET endpoints, no write endpoints |
| `backend/app/db/init_db.py` | Modified | Added `from app.models.product_version import ProductVersion  # noqa: F401` |
| `backend/tests/test_product_version_foundation_service.py` | Created | 9 service-layer tests |
| `backend/tests/test_product_version_foundation_api.py` | Created | 7 API-layer tests |
| `docs/design/02_domain/product_definition/product-version-foundation-contract.md` | Created | Contract doc |

---

## 4. API Contract

| Endpoint | Auth | Response |
|---|---|---|
| `GET /api/v1/products/{product_id}/versions` | `require_authenticated_identity` | `200 list[ProductVersionItem]`, `404` if product missing |
| `GET /api/v1/products/{product_id}/versions/{version_id}` | `require_authenticated_identity` | `200 ProductVersionItem`, `404` if missing |

No action code guard required — read-only, consistent with product and routing read endpoints.

---

## 5. Migration

- Revision: `0007`  
- `down_revision`: `0006`  
- SQL script: `0018_product_versions.sql`  
- Chain verified: `0001 → 0002 → 0003 → 0004 → 0005 → 0006 → 0007`  

Unique constraint: `uq_product_versions_tenant_product_code (tenant_id, product_id, version_code)`

---

## 6. Invariant Compliance

| Invariant | Result |
|---|---|
| Tenant isolation on all read paths | ✅ `tenant_id` in all queries |
| Product isolation (versions scoped to product_id) | ✅ `product_id` in all queries |
| Parent product existence check before returning versions | ✅ Service validates product row first |
| No write endpoints in this slice | ✅ Regression test `test_no_write_endpoints_for_product_versions_registered` locks this |
| lifecycle_status bounded | ✅ `_ALLOWED_VERSION_LIFECYCLE_STATUSES = {"DRAFT", "RELEASED", "RETIRED"}` locked by test |
| No BOM/Routing/RR FK binding | ✅ Confirmed in model — no FK to routings or resource_requirements |
| Migration chain unbroken | ✅ `down_revision = "0006"` |

---

## 7. Test Results

### New tests (16 total)

```
tests/test_product_version_foundation_service.py  — 9 passed
tests/test_product_version_foundation_api.py      — 7 passed
```

### Regression suite

```
tests/test_product_foundation_api.py       — passed
tests/test_product_foundation_service.py   — passed
tests/test_routing_foundation_api.py       — passed
tests/test_resource_requirement_api.py     — passed
tests/test_mmd_rbac_action_codes.py        — passed
```

### FE MMD Read Regression

```
[MMD READ REGRESSION] SUMMARY: 47 passed, 0 failed — PASS all checks
```

---

## 8. Known Deferred Items

| Item | Documented |
|---|---|
| Partial unique index on `is_current = true` | ✅ documented in contract |
| Write endpoints (create/release/retire version) | ✅ out of scope, locked by test |
| BOM / Routing binding to `product_version_id` | ✅ future slice |
| ERP/PLM sync | ✅ integration slice |
