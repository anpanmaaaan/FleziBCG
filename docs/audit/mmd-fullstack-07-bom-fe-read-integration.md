# MMD-FULLSTACK-07 — BOM FE Read Integration

## History

| Date | Author | Event |
|---|---|---|
| 2026-05 | Agent | MMD-FULLSTACK-07 implemented — BOM FE screens connected to backend read APIs from MMD-BE-05 |

---

## Scope

Connect the frontend BOM screens to the product-scoped backend BOM read APIs introduced in MMD-BE-05.

**In scope:**
- Add `BomItemFromAPI`, `BomComponentItemFromAPI`, `BomFromAPI` types to `productApi.ts`
- Add `listProductBoms` and `getProductBom` API helpers
- Rewrite `BomList.tsx` to load products and call `listProductBoms(selectedProductId)`
- Rewrite `BomDetail.tsx` to read `productId` from `?productId=` query param and call `getProductBom`
- Add new i18n keys for error/state messages in `en.ts` and `ja.ts`
- Update `screenStatus.ts` BOM entries from `SHELL/MOCK_FIXTURE` to `PARTIAL/BACKEND_API`
- Add section H (15 checks) to MMD regression script

**Out of scope:**
- No backend changes
- No BOM write UI
- No component name/code lookup (only `component_product_id` displayed as identifier)
- No product version or BOM version fields (not in `BomItem` schema)

---

## Baseline Evidence

- **MMD-BE-05 audit**: `docs/audit/mmd-be-05-bom-minimal-read-model.md` — confirmed present
- **Backend API**: `GET /api/v1/products/{product_id}/boms` → `BomItem[]`, `GET /api/v1/products/{product_id}/boms/{bom_id}` → `BomDetail`
- **Backend tests**: 20/20 pass (11 API + 9 service) before this task — no backend changes in this task
- **No global BOM list endpoint**: confirmed. Product context is mandatory.

---

## FE/BE Read Contract Map

| Backend Field | FE Type | UI Display | Decision |
|---|---|---|---|
| `bom_id` | `string` | key | keep |
| `tenant_id` | `string` | internal | type only, not displayed |
| `product_id` | `string` | query param context | used for API scoping |
| `bom_code` | `string` | BOM Code column | keep |
| `bom_name` | `string` | BOM Name column | keep |
| `lifecycle_status` | `"DRAFT"\|"RELEASED"\|"RETIRED"` | StatusBadge | keep |
| `effective_from` | `string\|null` | detail header field | keep |
| `effective_to` | `string\|null` | detail header field | keep |
| `description` | `string\|null` | detail header field | keep |
| `updated_at` | `string` | Last Updated column | keep |
| `items` | `BomComponentItemFromAPI[]` | Components table | keep |
| `component_product_id` | `string` | Component ID column | display as identifier — no name lookup |
| `line_no` | `number` | Line No column | replaces mock `seq` |
| `quantity` | `number` | Qty column | keep |
| `unit_of_measure` | `string` | UOM column | keep |
| `scrap_factor` | `number\|null` | Scrap % column | keep; null displayed as "—" |
| `version` | ❌ not in schema | — | REMOVED from UI |
| `component_count` | ❌ not in schema | — | REMOVED from UI |
| `component_name` | ❌ not in schema | — | REMOVED; `component_product_id` used instead |
| `item_type` | ❌ not in schema | — | REMOVED |
| `effective_date` (mock) | ❌ replaced | — | REMOVED; replaced by `effective_from`/`effective_to` |

---

## Files Changed

| File | Change |
|---|---|
| `frontend/src/app/api/productApi.ts` | Added `BomItemFromAPI`, `BomComponentItemFromAPI`, `BomFromAPI` interfaces; added `listProductBoms` and `getProductBom` methods |
| `frontend/src/app/pages/BomList.tsx` | Replaced mock fixture with product selection + `listProductBoms` backend read; removed version/components columns; updated phase to PARTIAL; added error/loading/empty states |
| `frontend/src/app/pages/BomDetail.tsx` | Replaced mock fixtures with `useSearchParams` + `getProductBom` backend read; added product context required guard; updated phase to PARTIAL; updated component table columns |
| `frontend/src/app/i18n/registry/en.ts` | Added 11 new keys: `bomList.notice.backendRead`, `bomList.notice.selectProduct`, `bomList.action.retry`, `bomList.select.product.placeholder`, `bomList.error.load`, `bomList.error.unauthorized`, `bomList.error.forbidden`, `bomDetail.notice.productContextRequired`, `bomDetail.col.lineNo`, `bomDetail.col.componentId`, `bomDetail.col.quantity`, `bomDetail.field.effectiveFrom`, `bomDetail.field.effectiveTo`, `bomDetail.field.description`, `bomDetail.error.load`, `bomDetail.error.notFound` |
| `frontend/src/app/i18n/registry/ja.ts` | Same new keys in Japanese |
| `frontend/src/app/screenStatus.ts` | `bomList` and `bomDetail` updated to `phase: "PARTIAL"`, `dataSource: "BACKEND_API"` |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | Added `bomList`/`bomDetail` to load block; added Section H (15 BOM invariant checks) |

---

## Frontend Changes Detail

### BomList.tsx
- Loads all products via `productApi.listProducts()` on mount
- Shows product dropdown; on selection calls `listProductBoms(selectedProductId)`
- No product selected → "Select a product..." empty state (no API call)
- Columns: BOM Code, BOM Name, Status, Last Updated (removed Version, Components)
- View links: `/bom/${bom.bom_id}?productId=${encodeURIComponent(bom.product_id)}`
- Loading/error states for both products and BOMs
- `MockWarningBanner phase="PARTIAL"`, `ScreenStatusBadge phase="PARTIAL"`
- Import/Create buttons remain disabled (no write UI)

### BomDetail.tsx
- Reads `productId` from `useSearchParams()` — query param injected by BomList view links
- If no `productId`: renders "product context required" notice; no API call
- Calls `getProductBom(productId, bomId)` when both IDs present
- Header fields: bom_code, bom_name, lifecycle_status, effective_from, effective_to, description
- Components table columns: Line No (`line_no`), Component ID (`component_product_id`), Quantity (`quantity`), UOM (`unit_of_measure`), Scrap % (`scrap_factor`)
- Error states: load, notFound, unauthorized, forbidden
- `MockWarningBanner phase="PARTIAL"`, `ScreenStatusBadge phase="PARTIAL"`
- Release/Retire/Edit/AddComponent buttons remain disabled

---

## Backend Verification

No backend changes. MMD-BE-05 tests remain valid:
- `tests/test_bom_foundation_api.py` — 11 tests
- `tests/test_bom_foundation_service.py` — 9 tests

---

## Screen Status Decision

| Screen | Before | After | Reason |
|---|---|---|---|
| bomList | `SHELL / MOCK_FIXTURE` | `PARTIAL / BACKEND_API` | Reads backend product list + product-scoped BOM list. Partial because component count/product name not available; write actions disabled. |
| bomDetail | `SHELL / MOCK_FIXTURE` | `PARTIAL / BACKEND_API` | Reads backend BOM detail with component items. Partial because component names require product lookup (deferred). Write actions disabled. |

---

## Boundary Guardrails

| Invariant | Enforcement |
|---|---|
| No global BOM list endpoint | Product selection required before `listProductBoms` is called |
| BomDetail requires product context | `useSearchParams()` reads `?productId=`; missing → safe notice; no API call |
| No write UI | Import/Create/Release/Retire/Edit/AddComponent all disabled |
| Backend is source of truth | Fixtures fully removed; error states surface on backend failure |
| No faking execution state | Component table displays `component_product_id` only; no derived names |
| URL injection safety | `encodeURIComponent(productId)` and `encodeURIComponent(bomId)` on all API paths |
| No rejected schema fields | `version`, `component_count`, `component_name`, `item_type`, `effective_date` removed |

---

## Regression Coverage

Section H added to `frontend/scripts/mmd-read-integration-regression-check.mjs`:

| Check ID | Check Name | Description |
|---|---|---|
| H1 | `bom_api_type_exists` | `BomItemFromAPI` present in productApi.ts |
| H2 | `bom_api_component_type_exists` | `BomComponentItemFromAPI` present |
| H3 | `bom_api_list_helper_exists` | `listProductBoms` present |
| H4 | `bom_api_get_helper_exists` | `getProductBom` present |
| H5 | `bom_list_uses_list_product_boms` | BomList.tsx calls `listProductBoms` |
| H6 | `bom_list_no_primary_mock_array` | No `const mockBoms = [...]` in BomList |
| H7 | `bom_list_product_selection` | BomList manages `selectedProductId` |
| H8 | `bom_list_view_links_pass_product_id` | View links include productId + encodeURIComponent |
| H9 | `bom_detail_uses_get_product_bom` | BomDetail.tsx calls `getProductBom` |
| H10 | `bom_detail_product_context_handling` | BomDetail uses `useSearchParams` for productId |
| H11 | `bom_detail_no_primary_mock_fixtures` | No `mockBomHeaders`/`mockBomComponents` |
| H12 | `screen_status_bom_list_partial_backend` | bomList is PARTIAL/BACKEND_API |
| H13 | `screen_status_bom_detail_partial_backend` | bomDetail is PARTIAL/BACKEND_API |
| H14 | `bom_detail_uses_component_product_id` | Correct backend field used |
| H15 | `bom_no_rejected_fields` | No `component_code`, `component_name`, `item_type` |

---

## Verification Commands Run

| Command | Result |
|---|---|
| `npm.cmd run check:mmd:read` | 67 passed, 0 failed |
| `npm.cmd run build` | 0 TypeScript errors (chunk size warning only, pre-existing) |
| `npm.cmd run lint` | 0 errors |
| `npm.cmd run lint:i18n:registry` | PASS: en.ts and ja.ts key-synchronized (1728 keys) |
| `npm.cmd run check:routes` | Exit 0, all routes covered |

---

## Remaining Risks / Deferred

| Item | Reason | Deferred To |
|---|---|---|
| Component product name lookup | `component_product_id` is an ID, not a display name. Name requires `/v1/products/{id}` lookup per component. | Future MMD slice |
| Effective dates on BomList | Backend `BomItem` does not expose `effective_from`/`effective_to` in the list endpoint; shown in detail only. | Acceptable per current schema |
| Product code in BomDetail | `product_id` is in BomDetail but not `product_code`/`product_name`. Display of product context requires separate product lookup. | Future MMD slice |
| BOM write UI (create/import/release/retire/edit/add component) | Backend MMD governance workflow required | Separate MMD write task |

---

## Final Verdict

**PASS** — MMD-FULLSTACK-07 BOM FE Read Integration is complete.

- All 67 regression checks pass (52 baseline + 15 new BOM section H)
- Build: 0 TypeScript errors
- Lint: 0 errors
- i18n: 1728 keys synchronized (en+ja)
- Routes: all pass
- Boundary invariants enforced: product context required, no write UI, no mock fixtures, no rejected schema fields
- screenStatus updated: both BOM screens at `PARTIAL/BACKEND_API`
