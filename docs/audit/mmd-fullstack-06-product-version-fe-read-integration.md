# MMD-FULLSTACK-06: Product Version FE Read Integration — Audit Report

| Field        | Value                                        |
|--------------|----------------------------------------------|
| Slice        | MMD-FULLSTACK-06                             |
| Date         | 2026-05-02                                   |
| Version      | v1.0                                         |
| Mode         | Hard Mode MOM v3 — Read-Only FE Integration  |
| Branch       | autocode                                     |
| Predecessor  | MMD-BE-03 (committed)                        |
| Author       | AI Agent (GitHub Copilot)                    |

---

## §1 Scope

Connect the existing frontend `ProductDetail` page to the MMD-BE-03 Product Version read API.

**In scope:**
- `ProductVersionItemFromAPI` type interface in `productApi.ts`
- `listProductVersions(productId, signal?)` HTTP helper
- `getProductVersion(productId, versionId, signal?)` HTTP helper
- `ProductDetail.tsx` versions section (read-only list view)
- i18n keys for `productDetail.versions.*` namespace (EN + JA)
- Export of `ProductVersionItemFromAPI` from `api/index.ts`
- Extension of MMD regression check (Group G — 5 new checks)

**Out of scope (deferred):**
- Product Version create / update / retire UI
- BOM binding to product version
- Routing binding to product version
- Any backend change

---

## §2 Baseline Evidence

**MMD-BE-03 backend endpoints verified before FE work began:**
- `GET /api/v1/products/{product_id}/versions` → `list[ProductVersionItem]`
- `GET /api/v1/products/{product_id}/versions/{version_id}` → `ProductVersionItem`
- Auth: `require_authenticated_identity` (tenant-scoped, read-only)
- Backend audit: `docs/audit/mmd-be-03-product-version-foundation-read-model.md`

**Frontend baseline files confirmed read-only target:**
- `frontend/src/app/screenStatus.ts`: `productDetail` entry = `PARTIAL / BACKEND_API` — **no change needed**
- `frontend/src/app/pages/ProductDetail.tsx`: existing page with product info, no version section

---

## §3 FE/BE Contract

| Frontend type field      | Backend schema field     | Type                            |
|--------------------------|--------------------------|---------------------------------|
| `product_version_id`     | `product_version_id`     | `string`                        |
| `tenant_id`              | `tenant_id`              | `string`                        |
| `product_id`             | `product_id`             | `string`                        |
| `version_code`           | `version_code`           | `string`                        |
| `version_name`           | `version_name`           | `string \| null \| undefined`   |
| `lifecycle_status`       | `lifecycle_status`       | `"DRAFT" \| "RELEASED" \| "RETIRED"` |
| `is_current`             | `is_current`             | `boolean`                       |
| `effective_from`         | `effective_from`         | `string \| null \| undefined`   |
| `effective_to`           | `effective_to`           | `string \| null \| undefined`   |
| `description`            | `description`            | `string \| null \| undefined`   |
| `created_at`             | `created_at`             | `string` (ISO 8601)             |
| `updated_at`             | `updated_at`             | `string` (ISO 8601)             |

API URL pattern: `/api/v1/products/{productId}/versions`

---

## §4 Files Changed

| File                                                  | Status    | Reason                                      |
|-------------------------------------------------------|-----------|---------------------------------------------|
| `frontend/src/app/api/productApi.ts`                  | MODIFIED  | Added `ProductVersionItemFromAPI`, `listProductVersions`, `getProductVersion` |
| `frontend/src/app/api/index.ts`                       | MODIFIED  | Export `ProductVersionItemFromAPI`          |
| `frontend/src/app/pages/ProductDetail.tsx`            | MODIFIED  | Added versions state, load, and read-only section |
| `frontend/src/app/i18n/registry/en.ts`                | MODIFIED  | Added 10 `productDetail.versions.*` keys (EN) |
| `frontend/src/app/i18n/registry/ja.ts`                | MODIFIED  | Added 10 `productDetail.versions.*` keys (JA) |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | MODIFIED | Added Group G (5 checks), loaded productApi + productDetail sources |

**No backend files changed.**
**No screenStatus.ts changes** (`productDetail` was already `PARTIAL / BACKEND_API`).

---

## §5 FE Changes Detail

### `productApi.ts`

```typescript
export interface ProductVersionItemFromAPI {
  product_version_id: string;
  tenant_id: string;
  product_id: string;
  version_code: string;
  version_name?: string | null;
  lifecycle_status: "DRAFT" | "RELEASED" | "RETIRED";
  is_current: boolean;
  effective_from?: string | null;
  effective_to?: string | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

// Added to productApi object:
listProductVersions(productId: string, signal?: AbortSignal)
  → request<ProductVersionItemFromAPI[]>(
      `/api/v1/products/${encodeURIComponent(productId)}/versions`,
      { method: "GET", signal }
    )

getProductVersion(productId: string, versionId: string, signal?: AbortSignal)
  → request<ProductVersionItemFromAPI>(
      `/api/v1/products/${encodeURIComponent(productId)}/versions/${encodeURIComponent(versionId)}`,
      { method: "GET", signal }
    )
```

### `ProductDetail.tsx` additions

- 3 state variables: `versions`, `versionsLoading`, `versionsError`
- `loadVersions()` async function using `productApi.listProductVersions(productId, signal)` with `HttpError` handling
- `useEffect` extended to also call `loadVersions()`
- Read-only table section with 6 columns: Version Code, Name, Lifecycle, Current, Effective From, Effective To
- Shows loading/error/empty states per existing UI pattern
- `ScreenStatusBadge phase="PARTIAL"` in section header (consistent with `productDetail` screen status)
- No write actions, no create/update/delete buttons

### i18n keys added (EN → JA)

| Key                                      | EN                              | JA                                        |
|------------------------------------------|---------------------------------|-------------------------------------------|
| `productDetail.section.versions`         | Product Versions                | 製品バージョン                            |
| `productDetail.versions.loading`         | Loading product versions...     | 製品バージョンを読み込み中...              |
| `productDetail.versions.error`           | Failed to load product versions.| 製品バージョンの読み込みに失敗しました。    |
| `productDetail.versions.empty`           | No product versions found.      | 製品バージョンが見つかりません。            |
| `productDetail.versions.col.versionCode` | Version Code                    | バージョンコード                           |
| `productDetail.versions.col.versionName` | Name                            | 名称                                       |
| `productDetail.versions.col.lifecycle`   | Lifecycle                       | ライフサイクル                             |
| `productDetail.versions.col.isCurrent`   | Current                         | 現行                                       |
| `productDetail.versions.col.effectiveFrom` | Effective From               | 有効開始日                                 |
| `productDetail.versions.col.effectiveTo` | Effective To                    | 有効終了日                                 |

---

## §6 BE Verification

Backend tests run as regression confirmation (no backend changes made):

```
tests/test_product_version_foundation_api.py     7 tests — PASS
tests/test_product_version_foundation_service.py 9 tests — PASS
tests/test_product_foundation_api.py             3 tests — PASS
Total: 19 passed
```

---

## §7 Screen Status Decision

`productDetail` was already registered as `PARTIAL / BACKEND_API` in `frontend/src/app/screenStatus.ts` before this slice. Adding the versions read section is consistent with this status — Product List API already connected, now Product Versions API connected. No status change needed.

---

## §8 Boundary Guardrails

| Rule                                   | Status |
|----------------------------------------|--------|
| Frontend sends intent only             | ✅ No mutations in this slice |
| Frontend does not derive execution state | ✅ Status fields read from API |
| Frontend does not decide authorization | ✅ 401/403 handled via HttpError |
| Backend is source of truth             | ✅ All data from API responses |
| No write UI for product versions       | ✅ G5 regression check enforces this |
| No BOM/routing binding                 | ✅ Deferred, not present |
| Tenant isolation                       | ✅ Enforced server-side via `require_authenticated_identity` |

---

## §9 Regression Coverage

### MMD regression script Group G (5 new checks added)

| Check ID                            | Description                                               | Result |
|-------------------------------------|-----------------------------------------------------------|--------|
| `pv_api_type_exists`                | `ProductVersionItemFromAPI` in `productApi.ts`            | PASS   |
| `pv_api_list_helper_exists`         | `listProductVersions` in `productApi.ts`                  | PASS   |
| `pv_api_get_helper_exists`          | `getProductVersion` in `productApi.ts`                    | PASS   |
| `pv_product_detail_consumes_list`   | `ProductDetail.tsx` calls `listProductVersions`           | PASS   |
| `pv_no_write_ui_in_product_detail`  | No version write/mutation UI in `ProductDetail.tsx`       | PASS   |

**Full regression run: 52/52 checks PASS**

---

## §10 Verification Results

| Gate                               | Result       | Notes                                      |
|------------------------------------|--------------|--------------------------------------------|
| MMD regression check (52 checks)   | 52/52 PASS   | Groups A–G all green                       |
| TypeScript type check (`tsc --noEmit`) | Pre-existing errors only | No new errors from this slice |
| Backend tests (19 tests)           | 19/19 PASS   | Product version and product foundation     |
| i18n type safety                   | ✅           | `I18nSemanticKey` = `${I18nNamespace}.${string}`, `productDetail` is a valid namespace |

**Pre-existing TypeScript errors** (not from this slice):
- `AIInsightsDashboard.tsx` — `aiInsightsDashboard.*` namespace not registered
- `en.ts` / `ja.ts` — `integrationDashboard.*` namespace not registered
- `RouteStatusBanner.tsx` — `notes` property type mismatch

---

## §11 Risks / Deferred

| Item                              | Risk Level | Disposition             |
|-----------------------------------|------------|-------------------------|
| Effective date display format     | Low        | Renders raw ISO string; no locale formatting. Acceptable for partial status. |
| `getProductVersion` helper unused | Low        | Added for completeness per contract; no page uses detail view yet. Deferred to next slice. |
| Lifecycle badge styling           | Low        | Plain text — no color coding for DRAFT/RELEASED/RETIRED. Deferred. |
| BOM/routing linkage               | N/A        | Explicitly out of scope for MMD-FULLSTACK-06 |
| Version create/edit UI            | N/A        | Explicitly out of scope for MMD-FULLSTACK-06 |

---

## §12 Final Verdict

**PASS — MMD-FULLSTACK-06 implementation complete.**

The `ProductDetail` page now connects to the MMD-BE-03 Product Version read API. The integration is:
- Read-only (no mutation UI)
- Tenant-scoped (auth delegated to backend)
- Regression-locked (Group G, 52/52 checks pass)
- i18n-complete (EN + JA)
- Backend-verified (19/19 tests)

No boundary violations. No pre-existing errors introduced. Ready for user review and commit.
