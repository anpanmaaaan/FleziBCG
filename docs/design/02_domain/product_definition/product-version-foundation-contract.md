# Product Version Foundation Contract

**Slice:** MMD-BE-03  
**Status:** Implemented  
**Scope:** Backend only — read model, migration, API, service, repository, tests  
**Hard Mode MOM:** v3 applied

---

## 1. Purpose

Product Version is the versioned manufacturing definition context for a Product. It does **not** replace ERP/PLM revision truth. It provides a minimal read model for downstream MMD slices (BOM binding, Routing binding, execution traceability, quality hold) that require versioned product identity.

This slice delivers the data structure and read-only API. No write-path, lifecycle workflow, or cross-entity binding is included.

---

## 2. Domain Model

### `product_versions` table

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `product_version_id` | `VARCHAR(64)` | PK | UUID |
| `tenant_id` | `VARCHAR(64)` | NOT NULL, indexed | Tenant isolation |
| `product_id` | `VARCHAR(64)` | NOT NULL, FK → `products.product_id`, indexed | Parent product |
| `version_code` | `VARCHAR(64)` | NOT NULL | Free-form version identifier |
| `version_name` | `VARCHAR(256)` | nullable | Display name |
| `lifecycle_status` | `VARCHAR(16)` | NOT NULL, default `DRAFT` | `DRAFT` / `RELEASED` / `RETIRED` |
| `is_current` | `BOOLEAN` | NOT NULL, default `false` | Advisory; no partial unique constraint (deferred) |
| `effective_from` | `DATE` | nullable | Planning boundary |
| `effective_to` | `DATE` | nullable | Planning boundary |
| `description` | `TEXT` | nullable | Free-form |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | |

**Unique constraint:** `(tenant_id, product_id, version_code)` → `uq_product_versions_tenant_product_code`

---

## 3. Invariants

| Invariant | Enforcement |
|---|---|
| All versions are tenant-scoped | `tenant_id` always included in read queries |
| All versions are product-scoped | `product_id` always included in read queries |
| Parent product must exist | Service validates product existence before returning versions |
| `lifecycle_status` is bounded | `DRAFT`, `RELEASED`, `RETIRED` — constant set in `schemas/product.py` |
| `is_current` is advisory | Single `BOOLEAN`; no partial unique index — at-most-one-current is a future write-path concern |
| No write endpoints in this slice | Enforced by regression test `test_no_write_endpoints_for_product_versions_registered` |
| No BOM/Routing/RR binding | No FK from `product_versions` to `routings`, `bom`, or `resource_requirements` tables |

---

## 4. API Contract

### `GET /api/v1/products/{product_id}/versions`

- **Auth:** `require_authenticated_identity` (same as product reads)
- **Response:** `200 list[ProductVersionItem]` — ordered by `version_code ASC, product_version_id ASC`
- **Errors:**
  - `404` — if product does not exist or belongs to a different tenant

### `GET /api/v1/products/{product_id}/versions/{version_id}`

- **Auth:** `require_authenticated_identity`
- **Response:** `200 ProductVersionItem`
- **Errors:**
  - `404` — if product does not exist, or if version does not exist under that product/tenant

---

## 5. Schema (`ProductVersionItem`)

```python
class ProductVersionItem(BaseModel):
    product_version_id: str
    tenant_id: str
    product_id: str
    version_code: str
    version_name: str | None
    lifecycle_status: str
    is_current: bool
    effective_from: date | None
    effective_to: date | None
    description: str | None
    created_at: datetime
    updated_at: datetime
```

---

## 6. Migration Chain

| Revision | File | `down_revision` |
|---|---|---|
| `0007` | `0007_product_versions.py` | `0006` |

SQL bootstrap script: `backend/scripts/migrations/0018_product_versions.sql`

---

## 7. Known Deferred Items

| Item | Risk | Deferred Until |
|---|---|---|
| Partial unique index on `is_current = true` per product | Multiple `is_current = true` rows possible | Write-path slice |
| Write endpoints (create/update/release/retire) | No mutation path exists | Future MMD slice |
| BOM / Routing binding to specific `product_version_id` | BOM and Routing are product-level today | Future binding slice |
| ERP/PLM sync | External master data integration | Integration slice |

---

## 8. Files Introduced

| File | Purpose |
|---|---|
| `backend/app/models/product_version.py` | ORM model |
| `backend/alembic/versions/0007_product_versions.py` | Alembic migration |
| `backend/scripts/migrations/0018_product_versions.sql` | SQL bootstrap script |
| `backend/app/repositories/product_version_repository.py` | DB access layer |
| `backend/app/services/product_version_service.py` | Business logic / read |
| `backend/app/schemas/product.py` | `ProductVersionItem` added |
| `backend/app/api/v1/products.py` | 2 read endpoints added |
| `backend/app/db/init_db.py` | `ProductVersion` import added |
| `backend/tests/test_product_version_foundation_service.py` | Service-layer tests |
| `backend/tests/test_product_version_foundation_api.py` | API-layer tests |
