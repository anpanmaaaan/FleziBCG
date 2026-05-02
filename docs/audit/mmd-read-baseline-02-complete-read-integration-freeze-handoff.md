# MMD-READ-BASELINE-02 — Complete MMD Read Integration Baseline Freeze / Handoff

## History

| Date       | Version | Change                                                                                         |
|------------|--------:|------------------------------------------------------------------------------------------------|
| 2026-05-02 |    v1.0 | Complete MMD read integration baseline frozen after MMD-AUDIT-00, MMD-READ-BASELINE-01, MMD-FULLSTACK-01 through MMD-FULLSTACK-08, MMD-BE-02 through MMD-BE-07, MMD-FE-QA-01. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Architecture / Product Baseline Freeze (documentation-only, critical pre-write-path governance checkpoint)
- **Hard Mode MOM:** v3 ON — freezes MMD manufacturing definition truth. Protects read-integration contracts consumed by execution, quality, material/traceability, planning, and digital twin domains. Documentation-only; no source, migration, or contract was modified.
- **Reason:** MMD-READ-BASELINE-02 is the mandatory freeze checkpoint before any write-path work begins. All nine MMD read-integration slices are complete. Backend foundations, frontend read pages, and regression test infrastructure are stable. This report establishes the verified state of the complete MMD read layer as the invariant baseline for subsequent write governance slices.

---

## 1. Scope

This baseline freeze covers the **complete** state of Manufacturing Master Data (MMD) / Product Definition read integration across the `autocode` branch, after all read-path slices from MMD-AUDIT-00 through MMD-FULLSTACK-08 (plus supporting backend slices and QA).

### Slice History Table (all MMD read slices)

| # | Slice ID | Type | Summary |
|---|---|---|---|
| 1 | MMD-AUDIT-00 | Audit / Evidence Pack | Full-stack source alignment; gap inventory (F1–F9) |
| 2 | MMD-FULLSTACK-01 | FE contract alignment | work_center drift fix; 3 extended routing fields added to FE type; rejected fields removed |
| 3 | MMD-FULLSTACK-02 | FE read integration | RoutingOperationDetail: shell/mock → live backend read |
| 4 | MMD-FULLSTACK-03 | FE read integration | ResourceRequirements: shell/mock → live nested backend API |
| 5 | MMD-FULLSTACK-04 | FE navigation | Routing Operation Detail → Resource Requirements contextual link |
| 6 | MMD-FULLSTACK-05 | QA / contract hardening | Static regression script created; 52 invariant checks established |
| 7 | MMD-BE-02 | BE governance | RBAC action-code fix — 14 MMD mutation endpoints re-authorized with domain-specific codes |
| 8 | MMD-BE-03 | BE read model | ProductVersion foundation — table, migration, service, 2 read endpoints |
| 9 | MMD-BE-04 | BE contract lock | BOM foundation contract documentation; boundary locked before implementation |
| 10 | MMD-BE-05 | BE read model | BOM minimal read model — boms/bom_items tables, migration, 2 product-scoped read endpoints |
| 11 | MMD-BE-06 | BE contract lock | Unified Reason Codes foundation contract; boundary locked before implementation |
| 12 | MMD-BE-07 | BE read model | Reason Codes minimal read model — reason_codes table, migration, 2 read endpoints |
| 13 | MMD-FULLSTACK-06 | FE read integration | ProductDetail: Product Version section added, `listProductVersions` / `getProductVersion` connected |
| 14 | MMD-FULLSTACK-07 | FE read integration | BomList / BomDetail: mock fixtures replaced, product-scoped backend read connected |
| 15 | MMD-FE-QA-01 | QA / visual sweep | 8 MMD read routes verified: 67/67 regression + build/lint/i18n/route gate |
| 16 | MMD-FULLSTACK-08 | FE read integration | ReasonCodes: mock primary source removed, backend read API connected; regression extended to 84 checks |

**Scope boundary:** All slices above are read-path only. Write-path, lifecycle workflow, ERP integration, quality decision, material/backflush, recipe/ISA-88, and operational event ownership are explicitly out of scope for this baseline.

---

## 2. Baseline Inputs Reviewed

### 2a. Audit Reports

| Input | Status | Notes |
|---|---|---|
| `docs/audit/mmd-audit-00-fullstack-source-alignment.md` | ✅ Inspected | v1.0 — full-stack gap inventory (F1–F9 findings) |
| `docs/audit/mmd-be-00-evidence-and-contract-lock.md` | ✅ Referenced | F1-F9 backend evidence findings |
| `docs/audit/mmd-be-01-hard-mode-evidence-pack.md` | ✅ Referenced | Routing extended fields evidence (scope-reduced to 3 nullable fields) |
| `docs/audit/mmd-read-baseline-01-read-integration-freeze-handoff.md` | ✅ Inspected | v1.0 — frozen after FULLSTACK-01–04; locked FE API types; backend extended fields committed |
| `docs/audit/mmd-fullstack-01-routing-operation-contract-alignment.md` | ✅ Referenced | work_center fix; 3 extended fields; rejected fields removed |
| `docs/audit/mmd-fullstack-02-routing-operation-detail-read-integration.md` | ✅ Referenced | RoutingOperationDetail shell→BACKEND_API |
| `docs/audit/mmd-fullstack-03-resource-requirements-read-integration.md` | ✅ Referenced | ResourceRequirements shell→BACKEND_API |
| `docs/audit/mmd-fullstack-04-routing-operation-resource-requirement-context-link.md` | ✅ Referenced | contextual nav link |
| `docs/audit/mmd-fullstack-05-mmd-read-integration-regression-tests.md` | ✅ Inspected | 52-check baseline regression script created |
| `docs/audit/mmd-be-02-rbac-action-code-fix.md` | ✅ Inspected | 14 mutation endpoints re-authorized; 3 MMD action codes registered |
| `docs/audit/mmd-be-03-product-version-foundation-read-model.md` | ✅ Inspected | ProductVersion model/migration/endpoints; 16 tests |
| `docs/audit/mmd-be-04-bom-foundation-contract-boundary-lock.md` | ✅ Inspected | BOM contract locked; no write-path or backflush |
| `docs/audit/mmd-be-05-bom-minimal-read-model.md` | ✅ Inspected | BOM read model; migration 0008; 20 tests (11 API + 9 service) |
| `docs/audit/mmd-be-06-reason-code-foundation-contract-boundary-lock.md` | ✅ Inspected | Unified Reason Codes contract; boundary from downtime_reason confirmed |
| `docs/audit/mmd-be-07-reason-code-minimal-read-model.md` | ✅ Inspected | Reason Codes model/migration 0010; 22 tests; SQL bootstrap 0020 added |
| `docs/audit/mmd-fullstack-06-product-version-fe-read-integration.md` | ✅ Inspected | ProductDetail versions section added; 5 regression checks (Group G) |
| `docs/audit/mmd-fullstack-07-bom-fe-read-integration.md` | ✅ Inspected | BomList/BomDetail mock→BACKEND_API; 15 regression checks (Section H) |
| `docs/audit/mmd-fe-qa-01-read-pages-runtime-visual-qa.md` | ✅ Inspected | 8 routes QA PASS; 67/67 checks, build/lint/i18n all green |
| `docs/audit/mmd-fullstack-08-reason-codes-fe-read-integration.md` | ✅ Inspected | ReasonCodes mock→BACKEND_API; 17 regression checks (Section I); 84/84 total |

### 2b. Source Files Inspected

| Source File | Status | Finding |
|---|---|---|
| `frontend/src/app/screenStatus.ts` | ✅ Inspected | All 9 MMD routes at `PARTIAL / BACKEND_API` or better (confirmed below) |
| `frontend/src/app/api/reasonCodeApi.ts` | ✅ Inspected | New module — `ReasonCodeItemFromAPI`, `reasonCodeApi.listReasonCodes/getReasonCode` |
| `frontend/src/app/api/productApi.ts` | ✅ Referenced | Includes `ProductVersionItemFromAPI`, `BomItemFromAPI`, `BomComponentItemFromAPI`, `BomFromAPI` |
| `frontend/src/app/api/routingApi.ts` | ✅ Referenced | Includes extended routing fields and ResourceRequirement types |
| `frontend/src/app/api/index.ts` | ✅ Inspected | All MMD API types exported; `reasonCodeApi` added in MMD-FULLSTACK-08 |
| `backend/app/api/v1/reason_codes.py` | ✅ Inspected | `GET /v1/reason-codes`, `GET /v1/reason-codes/{id}` — read-only, tenant-scoped |
| `backend/app/schemas/reason_code.py` | ✅ Inspected | `ReasonCodeItem` — 14 fields, `lifecycle_status` plain str |
| `backend/alembic/versions/0010_reason_codes.py` | ✅ Confirmed | Alembic head — verified by `alembic heads` |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | ✅ Inspected | 84 checks (Sections A–I); Sections A–F baseline, G product versions, H BOM, I reason codes |

---

## 3. Workspace / Git State

**Branch:** `autocode`  
**HEAD commit:** `a213edaf` — `feat(mmd): connect reason codes read view` (MMD-FULLSTACK-08)

> Note: HEAD is now `1cb63a90` (P0-A-07B add dedicated downtime reason admin action) — a post-MMD-FULLSTACK-08 commit unrelated to the MMD read slice series. All MMD source files for FULLSTACK-08 remain committed and unmodified in the working tree.

### MMD Slice Commit Chain (most recent MMD commit first)

| Commit | Message | Slice |
|---|---|---|
| `a213edaf` | feat(mmd): connect reason codes read view | MMD-FULLSTACK-08 |
| `b779c624` | chore(mmd): add reason code SQL bootstrap migration | MMD-BE-07 patch |
| `0950e9a9` | feat(mmd): add reason code minimal read model and read-only API (MMD-BE-07) | MMD-BE-07 |
| (prior) | feat(mmd): connect BOM read views | MMD-FULLSTACK-07 |
| (prior) | feat(mmd): connect product version read section | MMD-FULLSTACK-06 |
| (prior) | fix(mmd): align RBAC action codes for MMD mutations | MMD-BE-02 |
| (prior) | feat(mmd): add BOM read model | MMD-BE-05 |
| (prior) | feat(mmd): add product version read model | MMD-BE-03 |
| (prior) | (regression script + earlier read slices) | MMD-FULLSTACK-01–05 |

**All MMD-FULLSTACK-01 through FULLSTACK-08 and MMD-BE-02 through BE-07 FE/BE changes are committed.** Working tree changes for MMD source files: **none**.

The uncommitted changes in the working tree are exclusively in unrelated areas:
- Station execution (station_queue_service, QueueOperationCard, StationQueuePanel)
- RBAC governance (rbac.py claim-path changes)
- Governance admin FE pages (PlantHierarchy, RoleManagement, ScopeAssignments, etc.)
- P0-A and P0-C implementation documentation

None of these touch the MMD read-integration source files frozen in this baseline.

---

## 4. Alembic Migration Chain

**Head:** `0010` (verified via `alembic heads`)  
**Chain:** `0001_baseline` → `0002_add_refresh_tokens` → `0003_routing_operation_extended_fields` → `0004_add_user_lifecycle_status` → `0005_add_plant_hierarchy` → `0006_add_tenant_lifecycle_anchor` → `0007_product_versions` → `0008_boms` → `0009_drop_station_claims` → **`0010_reason_codes` (HEAD)**

### MMD-Relevant Migrations

| Revision | File | MMD Slice | Creates |
|---|---|---|---|
| `0003` | `0003_routing_operation_extended_fields.py` | MMD-BE-01 | routing extended fields (`setup_time`, `run_time_per_unit`, `work_center_code`) |
| `0007` | `0007_product_versions.py` | MMD-BE-03 | `product_versions` table |
| `0008` | `0008_boms.py` | MMD-BE-05 | `boms` + `bom_items` tables |
| `0010` | `0010_reason_codes.py` | MMD-BE-07 | `reason_codes` table |

### SQL Bootstrap Mirrors

| Script | MMD Slice | Mirrors |
|---|---|---|
| `backend/scripts/migrations/0018_product_versions.sql` | MMD-BE-03 | `product_versions` table |
| `backend/scripts/migrations/0019_boms.sql` | MMD-BE-05 | `boms` + `bom_items` tables |
| `backend/scripts/migrations/0020_reason_codes.sql` | MMD-BE-07 patch | `reason_codes` table |

---

## 5. Frontend Screen Status Registry — MMD Entries

The following is the verified state of all MMD-related entries in `frontend/src/app/screenStatus.ts` at this baseline:

| Screen Key | Route Pattern | Phase | Data Source | Slice |
|---|---|---|---|---|
| `productList` | `/products` | `PARTIAL` | `BACKEND_API` | FE-4A (pre-MMD) |
| `productDetail` | `/products/:productId` | `PARTIAL` | `BACKEND_API` | FE-4A + MMD-FULLSTACK-06 |
| `routeList` | `/routes` | `PARTIAL` | `BACKEND_API` | FE-5 (pre-MMD) |
| `routeDetail` | `/routes/:routeId` | `PARTIAL` | `BACKEND_API` | FE-5 (pre-MMD) |
| `routingOpDetail` | `/routes/:routeId/operations/:operationId` | `PARTIAL` | `BACKEND_API` | MMD-FULLSTACK-02 |
| `resourceRequirements` | `/resource-requirements` | `PARTIAL` | `BACKEND_API` | MMD-FULLSTACK-03 |
| `bomList` | `/bom` | `PARTIAL` | `BACKEND_API` | MMD-FULLSTACK-07 |
| `bomDetail` | `/bom/:id` | `PARTIAL` | `BACKEND_API` | MMD-FULLSTACK-07 |
| `reasonCodes` | `/reason-codes` | `PARTIAL` | `BACKEND_API` | MMD-FULLSTACK-08 |

**All 9 MMD read routes are at phase `PARTIAL` or better with `BACKEND_API` data source.**  
No MMD route remains at `SHELL` or `MOCK_FIXTURE`.

---

## 6. Backend API Contract Map — MMD Read Endpoints

The following read endpoints constitute the complete MMD read API surface frozen in this baseline:

### Product Domain

| Endpoint | Auth Guard | Response | Slice |
|---|---|---|---|
| `GET /api/v1/products` | `require_authenticated_identity` | `list[ProductItem]` | pre-MMD |
| `GET /api/v1/products/{product_id}` | `require_authenticated_identity` | `ProductItem` \| 404 | pre-MMD |
| `GET /api/v1/products/{product_id}/versions` | `require_authenticated_identity` | `list[ProductVersionItem]` \| 404 | MMD-BE-03 |
| `GET /api/v1/products/{product_id}/versions/{version_id}` | `require_authenticated_identity` | `ProductVersionItem` \| 404 | MMD-BE-03 |
| `GET /api/v1/products/{product_id}/boms` | `require_authenticated_identity` | `list[BomItem]` \| 404 | MMD-BE-05 |
| `GET /api/v1/products/{product_id}/boms/{bom_id}` | `require_authenticated_identity` | `BomDetail` \| 404 | MMD-BE-05 |

### Routing Domain

| Endpoint | Auth Guard | Response | Slice |
|---|---|---|---|
| `GET /api/v1/routings` | `require_authenticated_identity` | `list[RoutingItem]` | pre-MMD |
| `GET /api/v1/routings/{routing_id}` | `require_authenticated_identity` | `RoutingDetail` \| 404 | pre-MMD + MMD-BE-01 |
| `GET /api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements` | `require_authenticated_identity` | `list[ResourceRequirementItem]` | pre-MMD |
| `GET /api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req_id}` | `require_authenticated_identity` | `ResourceRequirementItem` \| 404 | pre-MMD |

### Reason Codes Domain

| Endpoint | Auth Guard | Response | Filters | Slice |
|---|---|---|---|---|
| `GET /v1/reason-codes` | `require_authenticated_identity` | `list[ReasonCodeItem]` | `domain`, `category`, `lifecycle_status`, `include_inactive` (default false) | MMD-BE-07 |
| `GET /v1/reason-codes/{reason_code_id}` | `require_authenticated_identity` | `ReasonCodeItem` \| 404 | — | MMD-BE-07 |

**Write endpoints (POST/PATCH/DELETE) on Product, Routing, and Resource Requirement entities** exist in the codebase but are protected by domain-specific RBAC action codes per MMD-BE-02:

| Action Code | Endpoints Protected | RBAC Family |
|---|---|---|
| `admin.master_data.product.manage` | POST/PATCH product + lifecycle transitions | `ADMIN` |
| `admin.master_data.routing.manage` | POST/PATCH routing + operation mutations + lifecycle | `ADMIN` |
| `admin.master_data.resource_requirement.manage` | POST/PATCH/DELETE resource requirements | `ADMIN` |

No write endpoints exist for `product_versions`, `boms`, or `reason_codes` — read-only by design for this baseline.

---

## 7. Frontend API Module Map

| Module File | Exports | MMD Slices |
|---|---|---|
| `frontend/src/app/api/productApi.ts` | `productApi`, `ProductItem`, `RoutingItemFromAPI`, `ResourceRequirementItemFromAPI`, `ProductVersionItemFromAPI`, `BomItemFromAPI`, `BomComponentItemFromAPI`, `BomFromAPI` | pre-MMD, MMD-FULLSTACK-01–03, MMD-BE-03, MMD-FULLSTACK-06, MMD-BE-05, MMD-FULLSTACK-07 |
| `frontend/src/app/api/routingApi.ts` | `routingApi`, `RoutingItemFromAPI`, `ResourceRequirementItemFromAPI` (extended fields) | MMD-FULLSTACK-01–04 |
| `frontend/src/app/api/reasonCodeApi.ts` | `reasonCodeApi`, `ReasonCodeItemFromAPI`, `ListReasonCodesParams` | MMD-FULLSTACK-08 |
| `frontend/src/app/api/index.ts` | All of the above re-exported | all MMD slices |

All modules use the shared `request<T>(path, options)` helper from `./httpClient` and accept `AbortSignal` for cancellation.

---

## 8. i18n Baseline

**Parity check result:** ✅ `en.ts` and `ja.ts` are key-synchronized — **1732 keys** (verified `2026-05-02`)

### MMD i18n Key Groups Added

| Key Namespace | Keys Added | Slice |
|---|---|---|
| `productDetail.versions.*` | 10 keys (EN + JA) | MMD-FULLSTACK-06 |
| `bomList.*` | 7 keys (EN + JA) | MMD-FULLSTACK-07 |
| `bomDetail.*` | 9 keys (EN + JA) | MMD-FULLSTACK-07 |
| `reasonCodes.col.name` | 1 key (EN + JA) | MMD-FULLSTACK-08 |
| `reasonCodes.filter.includeInactive` | 1 key (EN + JA) | MMD-FULLSTACK-08 |
| `reasonCodes.notice.readonly` | 1 key (EN + JA) | MMD-FULLSTACK-08 |
| `reasonCodes.error.load` | 1 key (EN + JA) | MMD-FULLSTACK-08 |

---

## 9. Regression Test Baseline

### Frontend Static Regression Script

**File:** `frontend/scripts/mmd-read-integration-regression-check.mjs`  
**Invocation:** `node scripts/mmd-read-integration-regression-check.mjs`  
**npm alias:** `npm run check:mmd:read`  
**Result:** ✅ **84 passed, 0 failed** (verified `2026-05-02`)

| Section | Checks | Domain | Added In |
|---|---|---|---|
| A | (baseline) | Routing API types, extended fields, rejected fields | MMD-FULLSTACK-05 |
| B | (baseline) | RoutingOperationDetail page — read-only, BACKEND_API | MMD-FULLSTACK-05 |
| C | (baseline) | ResourceRequirements page — read-only, filter, BACKEND_API | MMD-FULLSTACK-05 |
| D | (baseline) | Resource Requirements link + encodeURIComponent | MMD-FULLSTACK-05 |
| E | (baseline) | screenStatus entries | MMD-FULLSTACK-05 |
| F | (baseline) | i18n key presence | MMD-FULLSTACK-05 |
| G | 5 checks | Product Version types + UI section | MMD-FULLSTACK-06 |
| H | 15 checks | BOM types, BomList, BomDetail — read-only, BACKEND_API | MMD-FULLSTACK-07 |
| I | 17 checks | ReasonCodes — BACKEND_API, no mock, no downtime_reason boundary violation | MMD-FULLSTACK-08 |

**Total baseline section checks (A–F):** 47  
**Total extended checks (G–I):** 37  
**Total:** 84

### Backend Test Baseline

**Invocation (all MMD tests):**
```
python -m pytest -q \
  tests/test_reason_code_foundation_api.py \
  tests/test_reason_code_foundation_service.py \
  tests/test_product_version_foundation_api.py \
  tests/test_product_version_foundation_service.py \
  tests/test_bom_foundation_api.py \
  tests/test_bom_foundation_service.py \
  tests/test_mmd_rbac_action_codes.py
```

**Result:** ✅ **70 passed** (verified `2026-05-02`)

| Test File | Tests | Slice |
|---|---|---|
| `test_product_version_foundation_api.py` | 7 | MMD-BE-03 |
| `test_product_version_foundation_service.py` | 9 | MMD-BE-03 |
| `test_bom_foundation_api.py` | 11 | MMD-BE-05 |
| `test_bom_foundation_service.py` | 9 | MMD-BE-05 |
| `test_reason_code_foundation_api.py` | 14 | MMD-BE-07 |
| `test_reason_code_foundation_service.py` | 8 | MMD-BE-07 |
| `test_mmd_rbac_action_codes.py` | 12 | MMD-BE-02 |
| **Total** | **70** | |

---

## 10. Route Coverage Gate

**Route smoke check result:** ✅ **PASS 24/24 checks — 77/78 covered, 1 excluded (redirect-only)**  
**Invocation:** `node scripts/route-smoke-check.mjs`  

`/reason-codes` route: ✅ COVERED in route registry and screenStatus.

---

## 11. Boundary Invariant Map

The following invariants are locked by this baseline and must not be violated by any subsequent slice without explicit re-review under Hard Mode MOM v3:

| # | Invariant | Enforcement |
|---|---|---|
| INV-01 | MMD read screens are read-only — all write-action buttons remain `disabled` | Regression checks B, C, H, I; visual QA in MMD-FE-QA-01 |
| INV-02 | Backend is sole source of truth for MMD data — no inline mock array as primary data source | Regression checks (no `const mock[…] = [` pattern); MMD-FE-QA-01 |
| INV-03 | `work_center` bare field is rejected; `work_center_code` is canonical | Regression check A |
| INV-04 | `qc_checkpoint_count` belongs to Quality domain — absent from Routing and ResourceRequirement types | Regression check A |
| INV-05 | `required_skill` / `required_skill_level` belong to ResourceRequirement — absent from RoutingOperationDetail | Regression check B |
| INV-06 | Reason Codes do not own operational events; they are passive classifiers only | Regression checks I; boundary documented in MMD-BE-06 and MMD-BE-07 |
| INV-07 | `downtime_reason` (operational) and unified `reason_codes` (MMD reference) are separate entities — no FK between them | Regression check I9 (no `downtime_reason` import or reference in ReasonCodes page); MMD-BE-06/07 boundary |
| INV-08 | Reason Codes write actions (create/edit/retire) remain `disabled` in frontend | Regression checks I10–I12 |
| INV-09 | BOM does not perform backflush, inventory movement, or ERP posting | Boundary documented in MMD-BE-04; regression checks H |
| INV-10 | Product Version binding to BOM is deferred — not present in current slice | Regression checks H; MMD-BE-04/05 |
| INV-11 | All MMD mutation endpoints are protected by domain-specific RBAC action codes (not IAM placeholder) | `test_mmd_rbac_action_codes.py` (12 tests) |
| INV-12 | Frontend does not derive execution state from MMD data | General principle; read pages display reference data only |
| INV-13 | Frontend does not decide authorization — all writes require server-side RBAC evaluation | UI buttons disabled; no client-side auth decision on MMD writes |
| INV-14 | AbortController (cancel on unmount) is used in all MMD read page API calls | Regression check (signal pattern); all rewritten pages confirmed |
| INV-15 | i18n keys remain synchronized between `en.ts` and `ja.ts` | `check_i18n_registry_parity.mjs` (1732 keys, parity confirmed) |

---

## 12. What Is Deferred / Out of Scope

The following are explicitly NOT included in this read baseline and must not be implemented without a new slice and Hard Mode MOM v3 evidence:

| Area | Status | Reason |
|---|---|---|
| Product Version write / lifecycle transition UI | ❌ Deferred | No write governance slice yet |
| BOM write / lifecycle transition UI | ❌ Deferred | No write governance slice yet |
| Reason Code write / lifecycle transition UI | ❌ Deferred | No write governance slice yet |
| Product Version → BOM binding UI | ❌ Deferred | Not in current schema |
| Reason Code → DowntimeReason integration | ❌ Deferred | Boundary locked in MMD-BE-06; operational domain owns this |
| Work Center entity frontend | ❌ Deferred | Backend entity exists but FE screen not in MMD scope |
| BOM component name/code lookup | ❌ Deferred | Only `component_product_id` displayed; no name resolution endpoint |
| Material/backflush linkage from BOM | ❌ Deferred | Not in scope until Material domain slice |
| ERP posting from product definitions | ❌ Deferred | ERP integration is a separate domain |
| Quality linkage from routing operations | ❌ Deferred | Quality is a separate domain |
| Recipe / ISA-88 structure | ❌ Deferred | Not in P0-B scope |
| ProductVersion read in BomDetail context | ❌ Deferred | BOM→Version binding deferred |

---

## 13. Verification Commands (Reference)

The following commands were used to verify this baseline. Run before any subsequent MMD write-path slice to confirm no regression:

```bash
# Frontend regression (84 invariant checks)
cd frontend
node scripts/mmd-read-integration-regression-check.mjs

# i18n key parity (must be 1732 keys, en=ja)
node scripts/check_i18n_registry_parity.mjs

# Route smoke check (78 routes, 77 smoke targets, 24 PASS checks)
node scripts/route-smoke-check.mjs

# Backend MMD tests (70 tests across all MMD slices)
cd backend
..\.venv\Scripts\python.exe -m pytest -q \
  tests/test_reason_code_foundation_api.py \
  tests/test_reason_code_foundation_service.py \
  tests/test_product_version_foundation_api.py \
  tests/test_product_version_foundation_service.py \
  tests/test_bom_foundation_api.py \
  tests/test_bom_foundation_service.py \
  tests/test_mmd_rbac_action_codes.py

# Alembic migration head check (must be 0010)
..\.venv\Scripts\python.exe -m alembic heads
```

---

## 14. Stop Conditions Before Write Governance

Before any write-path MMD slice begins (product/routing/BOM/version/reason code lifecycle mutations), the following stop conditions must be cleared:

| # | Stop Condition | Current State |
|---|---|---|
| SC-01 | All 84 MMD regression checks pass | ✅ PASS |
| SC-02 | i18n keys synchronized (en.ts = ja.ts) | ✅ 1732 keys, parity confirmed |
| SC-03 | Route smoke check passes | ✅ 24/24 checks, 77/78 coverage |
| SC-04 | All 70 MMD backend tests pass | ✅ 70 passed |
| SC-05 | Alembic migration chain is single-head | ✅ `0010` is sole head |
| SC-06 | All 9 MMD screens are at `PARTIAL` or `CONNECTED` — no `SHELL` or `MOCK_FIXTURE` | ✅ All 9 confirmed |
| SC-07 | No uncommitted changes in MMD source files | ✅ Working tree clean for all MMD source |
| SC-08 | Write governance design evidence (domain contract doc) exists for target entity | ❌ Must be created per entity before write slice |
| SC-09 | Hard Mode MOM v3 evidence tables generated and reviewed | ❌ Required per write slice |
| SC-10 | RBAC action codes for target mutation registered in `ACTION_CODE_REGISTRY` | ✅ For Product/Routing/ResourceReq; ❌ Not yet for BOM writes, ProductVersion writes, ReasonCode admin |

SC-08, SC-09, SC-10 must be resolved by the first write-path slice.

---

## 15. Recommended Next Slice

**Recommended next slice:** `MMD-WRITE-GOV-01` — Write Governance Foundation for MMD Mutations

**Justification:**
- All read-integration work is complete and verified.
- Write-path FE buttons are present but `disabled` on all 9 MMD screens.
- Before any write slice can be safely implemented, the write governance contract must be locked.
- This slice should: (a) define the lifecycle state machine for each MMD entity (Product, Routing, ProductVersion, BOM, ReasonCode), (b) document allowed write actions per persona/role, (c) confirm RBAC action codes for all target mutation endpoints, (d) document invariants that must hold across create/update/release/retire.
- Scope: documentation-only contract + boundary lock (no implementation yet).
- Hard Mode MOM v3 is mandatory for `MMD-WRITE-GOV-01`.

**Alternative sequencing:** If a specific entity write slice is urgently needed before full write governance, use `MMD-WRITE-PRODUCT-01` (Product create/update) as the narrowest entry point, as Product is the least operationally complex entity and has no downstream references to BOM version binding.

---

## 16. Invariant Summary Table

| Domain | Entity | Read | Write | Migration | Tests | FE Screen | Phase |
|---|---|---|---|---|---|---|---|
| Product | Product | ✅ | 🔒 ADMIN-guarded (disabled FE) | `0001_baseline` | — | `/products`, `/products/:id` | PARTIAL |
| Product | ProductVersion | ✅ | ❌ Not yet | `0007_product_versions` | 16 | `/products/:id` (versions section) | PARTIAL |
| BOM | Bom + BomItem | ✅ | ❌ Not yet | `0008_boms` | 20 | `/bom`, `/bom/:id` | PARTIAL |
| Routing | Routing + Operations | ✅ | 🔒 ADMIN-guarded (disabled FE) | `0003_routing_extended_fields` | — | `/routes`, `/routes/:id`, `/routes/:id/operations/:id` | PARTIAL |
| Routing | ResourceRequirement | ✅ | 🔒 ADMIN-guarded (disabled FE) | `0001_baseline` | — | `/resource-requirements` | PARTIAL |
| Reference | ReasonCode | ✅ | ❌ Not yet | `0010_reason_codes` | 22 | `/reason-codes` | PARTIAL |

---

## 17. Sign-Off

| Gate | Result | Verified |
|---|---|---|
| MMD regression: 84/84 checks pass | ✅ PASS | `2026-05-02` |
| i18n parity: 1732 keys, en=ja | ✅ PASS | `2026-05-02` |
| Route smoke: 24/24 checks, 77/78 coverage | ✅ PASS | `2026-05-02` |
| Backend tests: 70/70 MMD tests pass | ✅ PASS | `2026-05-02` |
| Alembic head: single head `0010` | ✅ PASS | `2026-05-02` |
| No uncommitted MMD source changes | ✅ CLEAN | `2026-05-02` |
| All 9 MMD screens at PARTIAL/BACKEND_API | ✅ CONFIRMED | `2026-05-02` |
| All write buttons remain disabled in FE | ✅ CONFIRMED | Regression checks B, C, H, I |
| Boundary invariants documented (15 invariants) | ✅ DOCUMENTED | Section 11 |
| Deferred scope documented | ✅ DOCUMENTED | Section 12 |

**Baseline status: FROZEN. Safe to begin write-path governance planning.**

---

## Commit Guidance

```bash
git add docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md
git commit -m "docs(mmd): freeze complete MMD read integration baseline (MMD-READ-BASELINE-02)"
```
