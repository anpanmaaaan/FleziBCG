# MMD-AUDIT-00 — Manufacturing Master Data Full-Stack Source Alignment Audit

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Created full-stack source alignment audit for Manufacturing Master Data / Product Definition. Based on direct source inspection of frontend pages, API clients, backend models/schemas/services/APIs/tests, database migrations, and all referenced design and audit docs. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Audit Mode (read-only) — Full-stack source audit + MMD domain source alignment + backend/API/database evidence + frontend/source alignment + critical reviewer
- **Hard Mode MOM:** v3 — Source-truth discipline (not implementation). MMD defines manufacturing truth consumed by execution, quality, material/traceability, planning, and digital twin.
- **Reason:** MMD is canonical manufacturing definition layer. Any incorrect baseline claim would corrupt downstream implementation slices. Source inspection applied; no code, migration, or contract modified.

---

## 1. Scope

This audit covers the current state of Manufacturing Master Data (MMD) / Product Definition across:

- Frontend source (`frontend/src/app/pages/`, `api/`, `navigation/`, `persona/`, `screenStatus.ts`, `routes.tsx`)
- Backend source (`backend/app/models/`, `schemas/`, `repositories/`, `services/`, `api/v1/`, `tests/`)
- Database migrations (`backend/scripts/migrations/`, `backend/alembic/versions/`)
- Design and governance docs (`docs/design/02_domain/product_definition/`, `docs/audit/`)

Audit boundary: P0-B scope only. Out-of-scope MMD concepts (BOM, recipe, ISA-88, ERP sync, PLM, full versioning) are documented as missing or future — not recommended for immediate implementation.

---

## 2. Baseline Sources Reviewed

| Source | Status | Notes |
|---|---|---|
| `.github/copilot-instructions.md` | ✅ Read | Routing and entry rule confirmed |
| `.github/agent/AGENT.md` | ✅ Read | Behavioral guidelines confirmed |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | ✅ Read | Brain/mode selection confirmed |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | ✅ Read | v3 discipline — source-truth audit mode |
| `docs/design/02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md` | ✅ Read | v1.0 domain overview |
| `docs/design/02_domain/product_definition/product-foundation-contract.md` | ✅ Read | v1.2 product contract |
| `docs/design/02_domain/product_definition/routing-foundation-contract.md` | ✅ Read | v1.2 routing contract (with MMD-BE-01-PRE extended fields) |
| `docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md` | ✅ Read | v1.0 — IMPLEMENTED_AND_CANONICAL_FOR_P0_B |
| `docs/audit/mmd-current-state-report.md` | ✅ Read | v1.0 — 2026-05-01, 9-screen inventory |
| `docs/audit/mmd-be-00-evidence-and-contract-lock.md` | ✅ Read | v1.0 — 2026-05-01, backend evidence with F1-F9 findings |
| `docs/audit/mmd-be-01-hard-mode-evidence-pack.md` | ✅ Read | v1.1 — Routing extended fields evidence pack (scope-reduced to 3 fields) |
| `docs/audit/frontend-coverage-mmd-report.md` | ✅ Read | 5 SHELL screens delivery report |
| `docs/audit/frontend-source-alignment-snapshot.md` | ✅ Read | v1.24 — cumulative FE slice history |
| `frontend/src/app/routes.tsx` | ✅ Inspected | All route registrations verified |
| `frontend/src/app/screenStatus.ts` | ✅ Inspected | Screen phase registry verified |
| `frontend/src/app/navigation/navigationGroups.ts` | ✅ Inspected | MMD nav group verified |
| `frontend/src/app/persona/personaLanding.ts` | ✅ Inspected | MMD menu entries per persona verified |
| `backend/app/models/product.py` | ✅ Inspected | Full model |
| `backend/app/models/routing.py` | ✅ Inspected | Full model (including MMD-BE-01 extended fields) |
| `backend/app/models/resource_requirement.py` | ✅ Inspected | Full model |
| `backend/app/models/downtime_reason.py` | ✅ Inspected | Full model |
| `backend/app/schemas/product.py`, `routing.py`, `resource_requirement.py` | ✅ Inspected | Full schemas |
| `backend/app/api/v1/products.py` | ✅ Inspected | Full API (129 lines) |
| `backend/app/api/v1/routings.py` | ✅ Inspected | Full API (340 lines, includes resource requirement nested routes) |
| `backend/app/api/v1/downtime_reasons.py` | ✅ Inspected | Full API (80 lines) |
| `backend/app/security/rbac.py` | ✅ Inspected (partial) | action code registry — confirmed no `admin.master_data.*` entries |
| `backend/scripts/migrations/0012_downtime_reason_master.sql` | ✅ Inspected | downtime_reasons DDL |
| `backend/scripts/migrations/0014_products.sql` | ✅ Inspected | products DDL |
| `backend/scripts/migrations/0015_routings.sql` | ✅ Inspected | routings + routing_operations DDL |
| `backend/scripts/migrations/0016_resource_requirements.sql` | ✅ Inspected | resource_requirements DDL |
| `backend/alembic/versions/0001_baseline.py` | ✅ Inspected | No-op baseline stamp |
| `backend/alembic/versions/0002_add_refresh_tokens.py` | Listed only | Not MMD-related |
| `backend/alembic/versions/0003_routing_operation_extended_fields.py` | ✅ Inspected | MMD-BE-01 migration (setup_time, run_time_per_unit, work_center_code) |
| `backend/tests/test_product_foundation_api.py` | ✅ Inspected | Full happy path + state transitions |
| `backend/tests/test_product_foundation_service.py` | ✅ Inspected (partial) | Service-layer tests confirmed |
| `backend/tests/test_routing_foundation_api.py` | ✅ Inspected | Full routing happy path + lifecycle |
| `backend/tests/test_routing_foundation_service.py` | ✅ Inspected (partial) | Service tests confirmed |
| `backend/tests/test_resource_requirement_api.py` | ✅ Inspected | Full RR happy path + lifecycle guards |
| `backend/tests/test_resource_requirement_service.py` | Listed — confirmed exists | |
| `backend/tests/test_routing_operation_extended_fields.py` | ✅ Inspected | MMD-BE-01 model + API + negative tests |
| `backend/tests/test_downtime_reasons_endpoint.py` | Listed — confirmed exists | |
| `backend/tests/test_downtime_reason_admin_routes.py` | ✅ Inspected (partial) | Admin upsert/deactivate path confirmed |

**Missing design docs (not found under expected paths):**

| Expected doc | Status |
|---|---|
| `docs/design/00_platform/product-business-truth-overview.md` | NOT FOUND |
| `docs/design/00_platform/domain-boundary-map.md` | NOT FOUND — `docs/design/00_platform/` directory not found at that path |
| `docs/design/05_application/canonical-api-surface-map.md` | NOT FOUND under `05_application/` |
| `docs/design/05_application/api-catalog-current-baseline.md` | NOT FOUND |
| `docs/design/09_data/database-design-canonical.md` | NOT FOUND — `09_data/` directory not found |
| `docs/design/09_data/database-table-catalog.md` | NOT FOUND |
| `docs/audit/frontend-screen-coverage-matrix.md` | EXISTS (listed in audit dir) — not re-read in this audit |

These missing docs do not block this audit; source truth was established by direct source inspection.

---

## 3. Executive Summary

The FleziBCG MMD domain is at **mid-maturity partial implementation** with a clear two-tier structure:

**Tier 1 — Backend-connected PARTIAL screens (4 screens):**  
Product List, Product Detail, Routing List, and Routing Detail are connected to real backend APIs (`GET /v1/products`, `GET /v1/products/:id`, `GET /v1/routings`, `GET /v1/routings/:id`). Data is live. Lifecycle mutation actions (create, release, retire, edit) are correctly disabled in the UI pending MMD governance workflow.

**Tier 2 — Frontend SHELL screens (5 screens):**  
BOM List, BOM Detail, Routing Operation Detail, Resource Requirement Mapping, and Reason Code Management are SHELL pages using inline mock fixture data. No backend BOM API exists. No frontend API client for resource requirements or reason codes exists.

**Backend stack completeness:**  
Product, Routing, and Resource Requirement have full stacks (model → schema → repository → service → API → tests). Downtime Reason has a full operational stack (station execution reads live). BOM has no backend at all.

**Key gap discovered — FE type drift (MMD-BE-01 not reflected in FE):**  
Alembic migration 0003 added 3 extended columns to `routing_operations` (`setup_time`, `run_time_per_unit`, `work_center_code`) and backend response schema `RoutingOperationItem` now exposes these fields. However, `frontend/src/app/api/routingApi.ts` `RoutingOperationItemFromAPI` interface has **not been updated** and is missing all 3 fields. Additionally, `RoutingOperationDetail.tsx` mock fixture uses `work_center` (old field name), not `work_center_code` (canonical name per contract v1.2).

**Top 3 risks:**  
1. Authorization placeholder: all MMD mutation endpoints use `admin.user.manage` (an ADMIN family action code, semantic mismatch for master data governance — pre-existing debt documented in MMD-BE-00 as F3).  
2. BOM has zero backend and zero migration — a complete implementation gap.  
3. Reason code management (cross-domain) has no backend API or schema beyond downtime_reasons.

---

## 4. Current MMD Route Inventory

| Route | Page File | Navigation Group | Persona Visibility | Screen Status | Data Source | FE Status | Notes |
|---|---|---|---|---|---|---|---|
| `/products` | `ProductList.tsx` | Mfg Master Data | SUP, IEP, PMG, QC, ADM | PARTIAL | BACKEND_API | PARTIAL | Read connected; Create disabled |
| `/products/:productId` | `ProductDetail.tsx` | Mfg Master Data | SUP, IEP, PMG, QC, ADM | PARTIAL | BACKEND_API | PARTIAL | Read connected; Release/Retire disabled |
| `/routes` | `RouteList.tsx` | Mfg Master Data | SUP, IEP, PMG, QC, ADM | PARTIAL | BACKEND_API | PARTIAL | Read connected; Create/Export intent unclear |
| `/routes/:routeId` | `RouteDetail.tsx` | Mfg Master Data | SUP, IEP, PMG, QC, ADM | PARTIAL | BACKEND_API | PARTIAL | Read connected; operations list live |
| `/routes/:routeId/operations/:operationId` | `RoutingOperationDetail.tsx` | Mfg Master Data (via routes prefix) | SUP, IEP, PMG | SHELL | MOCK_FIXTURE | SHELL | Inline mockOperations; no backend call |
| `/bom` | `BomList.tsx` | Mfg Master Data | SUP, IEP, PMG | SHELL | MOCK_FIXTURE | SHELL | 4 mock BOMs; no BOM backend exists |
| `/bom/:bomId` | `BomDetail.tsx` | Mfg Master Data | SUP, IEP, PMG | SHELL | MOCK_FIXTURE | SHELL | Mock header + components; no BOM backend |
| `/resource-requirements` | `ResourceRequirements.tsx` | Mfg Master Data | IEP, PMG | SHELL | MOCK_FIXTURE | SHELL | 4 mock entries; BE nested under routings |
| `/reason-codes` | `ReasonCodes.tsx` | Mfg Master Data | SUP, IEP, PMG | SHELL | MOCK_FIXTURE | SHELL | 8 mock codes; only downtime_reasons API exists in BE |

**Navigation group registration (confirmed in `navigationGroups.ts`):**  
`/products`, `/routes`, `/bom`, `/resource-requirements`, `/reason-codes` — all in `mfg-master-data` group.

---

## 5. Current Frontend MMD Inventory

| FE Page / Component | Route | Data Source | API Client Used | Mock/Fixture Used | Actions Enabled | Mock Disclosure Visible | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| `ProductList.tsx` | `/products` | Backend API | `productApi.listProducts()` → `GET /v1/products` | None | Retry on error only; Create disabled | `BackendRequiredNotice` blue | PARTIAL | `frontend/src/app/pages/ProductList.tsx` |
| `ProductDetail.tsx` | `/products/:productId` | Backend API | `productApi.getProduct(id)` → `GET /v1/products/:id` | None | Retry only; Release, Retire disabled | `BackendRequiredNotice` blue | PARTIAL | `frontend/src/app/pages/ProductDetail.tsx` |
| `RouteList.tsx` | `/routes` | Backend API | `routingApi.listRoutings()` → `GET /v1/routings` | None | Client-side search; Create disabled; Export button present (status unclear) | `BackendRequiredNotice` blue | PARTIAL | `frontend/src/app/pages/RouteList.tsx` |
| `RouteDetail.tsx` | `/routes/:routeId` | Backend API | `routingApi.getRouting(id)` → `GET /v1/routings/:id` | None | Save/Edit disabled | `BackendRequiredNotice` blue | PARTIAL | `frontend/src/app/pages/RouteDetail.tsx` |
| `RoutingOperationDetail.tsx` | `/routes/:routeId/operations/:operationId` | Inline fixture | None | `mockOperations` (2 records) | Edit, Release disabled | `MockWarningBanner SHELL`, `BackendRequiredNotice`, `ScreenStatusBadge` | SHELL | `frontend/src/app/pages/RoutingOperationDetail.tsx` |
| `BomList.tsx` | `/bom` | Inline fixture | None | `mockBoms` (4 records) | Create, Import disabled | `MockWarningBanner SHELL`, `BackendRequiredNotice`, `ScreenStatusBadge` | SHELL | `frontend/src/app/pages/BomList.tsx` |
| `BomDetail.tsx` | `/bom/:bomId` | Inline fixture | None | `mockBomHeaders`, `mockBomComponents` | Edit, Release, Retire, Add Component disabled | `MockWarningBanner SHELL`, `BackendRequiredNotice`, `ScreenStatusBadge` | SHELL | `frontend/src/app/pages/BomDetail.tsx` |
| `ResourceRequirements.tsx` | `/resource-requirements` | Inline fixture | None | `mockRequirements` (4 records) | Assign Resource, Edit per row disabled | `MockWarningBanner SHELL`, `BackendRequiredNotice`, `ScreenStatusBadge` | SHELL | `frontend/src/app/pages/ResourceRequirements.tsx` |
| `ReasonCodes.tsx` | `/reason-codes` | Inline fixture | None | `mockReasonCodes` (8 records) | Create, Edit, Retire disabled; domain filter functional | `MockWarningBanner SHELL`, `BackendRequiredNotice`, `ScreenStatusBadge` | SHELL | `frontend/src/app/pages/ReasonCodes.tsx` |

**Frontend API clients — MMD-related:**

| API Client | Path | Endpoints Covered | Notes |
|---|---|---|---|
| `productApi.ts` | `frontend/src/app/api/productApi.ts` | `GET /v1/products`, `GET /v1/products/:id` | Interface matches backend schema; NO mismatch detected |
| `routingApi.ts` | `frontend/src/app/api/routingApi.ts` | `GET /v1/routings`, `GET /v1/routings/:id` | **DRIFT: `RoutingOperationItemFromAPI` missing `setup_time`, `run_time_per_unit`, `work_center_code`** — backend now returns these fields per MMD-BE-01 |
| `downtimeReasons.ts` | `frontend/src/app/api/downtimeReasons.ts` | `GET /v1/downtime-reasons` | Operational; consumed by station execution StartDowntimeDialog — not an MMD management screen |
| *(missing)* | — | Resource requirements nested under routings | No FE API client for `GET /v1/routings/:id/operations/:op_id/resource-requirements` |
| *(missing)* | — | BOM (no BE exists) | No FE BOM API client; consistent with absent backend |
| *(missing)* | — | Reason code management | No FE reason code API client; only downtime_reasons API exists in BE |

---

## 6. Current Backend MMD Inventory

| Capability | Model | Schema | Repository | Service | API Route | Tests | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| Product | ✅ `models/product.py` — `Product` | ✅ `schemas/product.py` — `ProductItem`, `ProductCreateRequest`, `ProductUpdateRequest` | ✅ `repositories/product_repository.py` | ✅ `services/product_service.py` (276 lines) | ✅ `api/v1/products.py` — GET list, GET by id, POST, PATCH, POST release, POST retire | ✅ `test_product_foundation_api.py`, `test_product_foundation_service.py` | FULL_STACK | Direct source inspection |
| Routing | ✅ `models/routing.py` — `Routing` | ✅ `schemas/routing.py` — `RoutingItem`, `RoutingCreateRequest`, `RoutingUpdateRequest` | ✅ `repositories/routing_repository.py` | ✅ `services/routing_service.py` (510 lines) | ✅ `api/v1/routings.py` — GET list, GET by id, POST, PATCH, POST release, POST retire | ✅ `test_routing_foundation_api.py`, `test_routing_foundation_service.py` | FULL_STACK | Direct source inspection |
| Routing Operation (extended) | ✅ `models/routing.py` — `RoutingOperation` (3 extended fields added in MMD-BE-01) | ✅ `schemas/routing.py` — `RoutingOperationItem` (3 nullable fields in response), `RoutingOperationCreateRequest` (NO extended fields — intentionally read-only) | ✅ (nested under routing_repository) | ✅ `routing_service.py` — `add_routing_operation`, `update_routing_operation`, `remove_routing_operation` | ✅ `api/v1/routings.py` — POST ops, PATCH ops, DELETE ops | ✅ `test_routing_operation_extended_fields.py` | FULL_STACK (read extended) | `backend/app/models/routing.py:56-63`, `backend/app/schemas/routing.py:46-52` |
| Resource Requirement | ✅ `models/resource_requirement.py` — `ResourceRequirement` | ✅ `schemas/resource_requirement.py` — `ResourceRequirementItem`, `ResourceRequirementCreateRequest`, `ResourceRequirementUpdateRequest` | ✅ `repositories/resource_requirement_repository.py` | ✅ `services/resource_requirement_service.py` (386 lines) | ✅ `api/v1/routings.py` — nested 5 endpoints under `/routings/{id}/operations/{op_id}/resource-requirements` | ✅ `test_resource_requirement_api.py`, `test_resource_requirement_service.py` | FULL_STACK | Direct source inspection |
| Downtime Reason | ✅ `models/downtime_reason.py` — `DowntimeReason` | ✅ `schemas/downtime_reason.py` | ✅ `repositories/downtime_reason_repository.py` | ✅ `services/downtime_reason_service.py` (75 lines) | ✅ `api/v1/downtime_reasons.py` — GET list (public read), POST upsert, POST deactivate | ✅ `test_downtime_reasons_endpoint.py`, `test_downtime_reason_admin_routes.py` | FULL_STACK (operational) | Direct source inspection |
| BOM | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | MISSING | No `bom.py` model, no BOM schema, no BOM migration found |
| BOM Item | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | MISSING | Depends on BOM; also missing |
| Work Center Entity | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | MISSING (string only) | `work_center_code` exists as VARCHAR(64) on `routing_operations` but no `work_centers` table/entity |
| Master Data Lifecycle Status | ✅ Embedded in Product + Routing models | N/A (no separate entity) | N/A | ✅ Enforced via service invariants | N/A (part of product/routing API) | ✅ Via product + routing tests | PARTIAL (no separate lifecycle table; Product and Routing each own their state machine) | Source inspection of lifecycle paths |
| Reason Code Management (cross-domain) | ❌ Missing (only downtime_reasons) | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | MISSING | `downtime_reasons` covers only downtime domain; scrap/pause/reopen/quality_hold reason codes have no backend table or API |
| Product Version | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | MISSING / GAP | Required by P0-B baseline as part of Product/Product Version foundation, but not currently implemented in source. Not recommended as the immediate next slice until current Product/Routing/Resource Requirement alignment is stabilized. |

---

## 7. Current Database / Migration Inventory

| Table / Model | Model Exists | SQL Migration | Alembic Migration | Tenant Scoped | Lifecycle Status | Versioning | Indexes | Tests | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| `products` | ✅ `models/product.py` | ✅ `scripts/migrations/0014_products.sql` | Covered by 0001 no-op baseline | ✅ `tenant_id` indexed | ✅ `lifecycle_status VARCHAR(16)` default DRAFT | ❌ No version fields | `ix_products_tenant_id`, `ix_products_tenant_code`; unique `(tenant_id, product_code)` | ✅ API + service tests | Direct inspection |
| `routings` | ✅ `models/routing.py` | ✅ `scripts/migrations/0015_routings.sql` | Covered by 0001 no-op baseline | ✅ `tenant_id` indexed | ✅ `lifecycle_status VARCHAR(16)` default DRAFT | ❌ No version fields | `ix_routings_tenant_id`, `ix_routings_product_id`, `ix_routings_tenant_code`; unique `(tenant_id, routing_code)` | ✅ API + service tests | Direct inspection |
| `routing_operations` | ✅ `models/routing.py` (RoutingOperation) | ✅ `scripts/migrations/0015_routings.sql` (baseline columns only — no extended fields) | ✅ `alembic/versions/0003_routing_operation_extended_fields.py` adds 3 nullable columns | ✅ `tenant_id` indexed | ❌ No own lifecycle (inherits routing lifecycle) | ❌ No version fields | `ix_routing_operations_tenant_id`, `ix_routing_operations_routing_id`; unique `(routing_id, sequence_no)` | ✅ MMD-BE-01 tests | Direct inspection |
| `resource_requirements` | ✅ `models/resource_requirement.py` | ✅ `scripts/migrations/0016_resource_requirements.sql` | Covered by 0001 no-op baseline | ✅ `tenant_id` indexed | ❌ No own lifecycle (inherits routing DRAFT constraint) | ❌ No version fields | `ix_resource_requirements_tenant_id`, `ix_resource_requirements_routing_id`, `ix_resource_requirements_operation_id`; unique `(tenant_id, operation_id, required_resource_type, required_capability_code)` | ✅ API + service tests | Direct inspection |
| `downtime_reasons` | ✅ `models/downtime_reason.py` | ✅ `scripts/migrations/0012_downtime_reason_master.sql` | Covered by 0001 no-op baseline | ✅ `tenant_id` | ❌ No DRAFT/RELEASED/RETIRED; `active_flag BOOLEAN` | ❌ No versioning | `uq_downtime_reasons_tenant_code`, `ix_downtime_reasons_tenant_active`, `ix_downtime_reasons_station` | ✅ endpoint + admin route tests | Direct inspection |
| `bom` | ❌ Missing | ❌ Missing | ❌ Missing | — | — | — | — | — | No BOM model found in `backend/app/models/` |
| `bom_items` | ❌ Missing | ❌ Missing | ❌ Missing | — | — | — | — | — | Depends on BOM; also missing |
| `work_centers` | ❌ Missing | ❌ Missing | ❌ Missing | — | — | — | — | — | `work_center_code` on `routing_operations` is a free-text string; no entity table |
| `reason_codes` (unified) | ❌ Missing | ❌ Missing | ❌ Missing | — | — | — | — | — | Only `downtime_reasons` exists; other domains not covered |

**Alembic migration posture note:**  
Alembic revision `0001` is a deliberate no-op baseline stamp. The schema for `products`, `routings`, `routing_operations`, `resource_requirements`, `downtime_reasons` was established via `Base.metadata.create_all()` + SQL scripts `0001–0017`. Alembic `0003` (MMD-BE-01 extended fields) is the first real Alembic-managed migration and must be applied via `alembic upgrade head` on all installations that were provisioned before 2026-05-01. Failure to apply will result in 3 missing columns in `routing_operations` and silent NULL returns for `setup_time`, `run_time_per_unit`, `work_center_code` in API responses.

---

## 8. Current API / Contract Inventory

| API Capability | Method/Path | Request Schema | Response Schema | Auth / Scope Guard | FE Consumer | Tests | Status |
|---|---|---|---|---|---|---|---|
| List Products | `GET /api/v1/products` | None (query TBD) | `list[ProductItem]` | `require_authenticated_identity` (read) | `productApi.listProducts()` | ✅ | LIVE |
| Get Product | `GET /api/v1/products/{product_id}` | Path param | `ProductItem` | `require_authenticated_identity` (read) | `productApi.getProduct(id)` | ✅ | LIVE |
| Create Product | `POST /api/v1/products` | `ProductCreateRequest` | `ProductItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None (FE action disabled) | ✅ | LIVE (auth placeholder) |
| Update Product | `PATCH /api/v1/products/{product_id}` | `ProductUpdateRequest` | `ProductItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE (auth placeholder) |
| Release Product | `POST /api/v1/products/{product_id}/release` | None | `ProductItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE (auth placeholder; no approval gate) |
| Retire Product | `POST /api/v1/products/{product_id}/retire` | None | `ProductItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE (auth placeholder; no approval gate) |
| List Routings | `GET /api/v1/routings` | None | `list[RoutingItem]` | `require_authenticated_identity` (read) | `routingApi.listRoutings()` | ✅ | LIVE |
| Get Routing | `GET /api/v1/routings/{routing_id}` | Path param | `RoutingItem` (includes extended op fields) | `require_authenticated_identity` (read) | `routingApi.getRouting(id)` | ✅ | LIVE (BE returns extended fields; FE type lags) |
| Create Routing | `POST /api/v1/routings` | `RoutingCreateRequest` | `RoutingItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE (auth placeholder) |
| Update Routing | `PATCH /api/v1/routings/{routing_id}` | `RoutingUpdateRequest` | `RoutingItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| Add Routing Operation | `POST /api/v1/routings/{routing_id}/operations` | `RoutingOperationCreateRequest` (no extended fields) | `RoutingItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE (extended fields not in create schema — intentional per MMD-BE-01 scope) |
| Update Routing Operation | `PATCH /api/v1/routings/{routing_id}/operations/{operation_id}` | `RoutingOperationUpdateRequest` (no extended fields) | `RoutingItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| Remove Routing Operation | `DELETE /api/v1/routings/{routing_id}/operations/{operation_id}` | Path params | `RoutingItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| Release Routing | `POST /api/v1/routings/{routing_id}/release` | None | `RoutingItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE (no approval gate) |
| Retire Routing | `POST /api/v1/routings/{routing_id}/retire` | None | `RoutingItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| List Resource Requirements | `GET /api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements` | Path params | `list[ResourceRequirementItem]` | `require_authenticated_identity` (read) | ❌ No FE client | ✅ | LIVE (no FE consumer) |
| Get Resource Requirement | `GET /api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}` | Path params | `ResourceRequirementItem` | `require_authenticated_identity` (read) | ❌ No FE client | ✅ | LIVE |
| Create Resource Requirement | `POST /api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements` | `ResourceRequirementCreateRequest` | `ResourceRequirementItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| Update Resource Requirement | `PATCH /api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}` | `ResourceRequirementUpdateRequest` | `ResourceRequirementItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| Delete Resource Requirement | `DELETE /api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}` | Path params | `ResourceRequirementItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| List Downtime Reasons (read) | `GET /api/v1/downtime-reasons` | None | `list[DowntimeReasonItem]` | `require_authenticated_identity` (read) | `downtimeReasons.ts` → `StartDowntimeDialog` | ✅ | LIVE |
| Upsert Downtime Reason | `POST /api/v1/downtime-reasons` | `DowntimeReasonUpsertRequest` | `DowntimeReasonAdminItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| Deactivate Downtime Reason | `POST /api/v1/downtime-reasons/{reason_code}/deactivate` | Path param | `DowntimeReasonAdminItem` | `require_action("admin.user.manage")` ⚠️ PLACEHOLDER | ❌ None | ✅ | LIVE |
| BOM (any) | ❌ MISSING | — | — | — | ❌ None | ❌ None | MISSING |
| Reason Codes (cross-domain) | ❌ MISSING | — | — | — | ❌ None | ❌ None | MISSING |

**Pagination / filter note:**  
No pagination or server-side filter parameters were found on any MMD list endpoint. All list responses are unbounded. This is a scalability concern but not an implementation blocker for P0-B.

---

## 9. Current Test Coverage Inventory

| Test File | Domain | Coverage | Pass Status |
|---|---|---|---|
| `test_product_foundation_api.py` | Product | Happy path + state transitions (create, update, release, retire, duplicate code, tenant isolation) | ✅ Source confirms well-structured; runtime BLOCKED (Python not in PATH in current PowerShell environment) |
| `test_product_foundation_service.py` | Product | Service-layer isolation (cross-tenant code uniqueness, lifecycle rules) | ✅ Source confirms well-structured; runtime BLOCKED |
| `test_routing_foundation_api.py` | Routing | Happy path + lifecycle guards | ✅ Source confirms well-structured; runtime BLOCKED |
| `test_routing_foundation_service.py` | Routing | Service-layer isolation (cross-tenant routing_code uniqueness) | ✅ Source confirms well-structured; runtime BLOCKED |
| `test_routing_operation_extended_fields.py` | Routing Operation extended fields (MMD-BE-01) | Model persistence, API response, negative tests (extended fields NOT in create/update schemas, rejected fields not present) | ✅ Source confirms well-structured; runtime BLOCKED |
| `test_resource_requirement_api.py` | Resource Requirement | Happy path + lifecycle guards (parent routing DRAFT guard) | ✅ Source confirms well-structured; runtime BLOCKED |
| `test_resource_requirement_service.py` | Resource Requirement | Service-layer isolation | Source confirmed exists; not read in full |
| `test_downtime_reasons_endpoint.py` | Downtime Reason (operational) | Endpoint read coverage | Source confirmed exists |
| `test_downtime_reason_admin_routes.py` | Downtime Reason (admin) | Upsert + deactivate paths | Source confirmed exists; partial inspection |

**Verification environment status:**  
Backend pytest BLOCKED in current PowerShell environment — `python`, `python3` not in PATH; `.venv/bin/python` (Linux-style path) does not execute in PowerShell without activation. Runtime test results cannot be reported as PASS/FAIL from this audit invocation. Source structure of test files confirms test intent and coverage, but live execution results are unverified by this audit run.

**Previous test evidence:** `mmd-be-01-hard-mode-evidence-pack.md` documents T1–T9 test matrix with expected pass results for MMD-BE-01. A previous Docker-based verification (noted in `frontend-source-alignment-snapshot.md` v1.15) confirmed frontend build passes.

---

## 10. FE ↔ BE Alignment Matrix

| MMD Screen | FE Status | Expected Backend Capability | Actual Backend Capability | Alignment | Gap | Recommended Slice |
|---|---|---|---|---|---|---|
| Product List (`/products`) | PARTIAL | `GET /v1/products` | ✅ Exists, tested | ALIGNED | Minor: no server-side filter/pagination | MMD-FE-01 — Add client-side search (already partially present) |
| Product Detail (`/products/:productId`) | PARTIAL | `GET /v1/products/:id` | ✅ Exists, tested | ALIGNED | BOM tab absent (no BOM backend); Release/Retire FE action disabled correctly | MMD-FE-02 — Surface product type badge + BOM tab placeholder (pending BOM backend) |
| Routing List (`/routes`) | PARTIAL | `GET /v1/routings` | ✅ Exists, tested | ALIGNED | Export button intent unclear (may be cosmetic) | MMD-FE-03 — Verify export button wiring; low priority |
| Routing Detail (`/routes/:routeId`) | PARTIAL | `GET /v1/routings/:id` with operations | ✅ Exists, tested; response now includes `setup_time`, `run_time_per_unit`, `work_center_code` | FE_BEHIND_OF_BE | FE type `RoutingOperationItemFromAPI` missing 3 extended fields — `routingApi.ts` not updated after MMD-BE-01 | **MMD-FULLSTACK-01 — Update `routingApi.ts` interface + surface extended fields** |
| Routing Operation Detail (`/routes/:routeId/operations/:operationId`) | SHELL | `GET /v1/routings/:id` (operation embedded) | ✅ Operation data embedded in routing response | FE_BEHIND_OF_BE | SHELL uses `mockOperations` with 2 records; FE mock uses `work_center` (wrong field name; canonical is `work_center_code`); also has `required_skill`, `required_skill_level`, `qc_checkpoint_count` in mock which are NOT on backend RoutingOperation | **MMD-FULLSTACK-01 — Connect RoutingOperationDetail to real routing response; fix `work_center` → `work_center_code`; remove deferred/rejected mock fields** |
| BOM List (`/bom`) | SHELL | `GET /v1/bom` | ❌ No BOM backend | MISSING | BOM model/schema/service/API/migration entirely absent from backend | MMD-BE-03 — BOM foundation (model + migration + read API) — HIGH scope, not next immediate slice |
| BOM Detail (`/bom/:bomId`) | SHELL | `GET /v1/bom/:id` | ❌ No BOM backend | MISSING | Same as BOM List | Blocked by MMD-BE-03 |
| Resource Requirement Mapping (`/resource-requirements`) | SHELL | `GET /v1/resource-requirements` (expected flat) | ✅ Exists nested: `GET /v1/routings/:id/operations/:op_id/resource-requirements` | FE_BEHIND_OF_BE | Path mismatch: FE SHELL mock expects flat `/resource-requirements`; BE is nested. FE has no API client. Mock schema has fields (`resource_code`, `resource_name`, `resource_type`, `capability`, `qualification`, `setup_constraint`) that don't directly map to BE `ResourceRequirementItem` fields | **MMD-FE-06 — Add resourceRequirementApi.ts client with nested path; update ResourceRequirements.tsx to query by routing/operation context or provide a summary view** |
| Reason Code Management (`/reason-codes`) | SHELL | Cross-domain `GET /v1/reason-codes` | ❌ Only `GET /v1/downtime-reasons` exists | FE_AHEAD_OF_BE | FE SHELL mocks scrap/pause/reopen/quality_hold domains with no backend equivalent; `downtime_reasons` API covers only downtime domain | MMD-BE-04 — Reason code unification (lower priority; operational downtime path works today) |

---

## 11. Design ↔ Source Alignment Matrix

| Design Document | Design Intent | Source Alignment | Conflict / Gap |
|---|---|---|---|
| `product-foundation-contract.md` v1.2 | Product aggregate: 8 fields, 3-state lifecycle, no versioning in P0-B, tenant-scoped | ✅ Source matches: `models/product.py` has exact 8 fields + `lifecycle_status`; no version fields | ALIGNED |
| `routing-foundation-contract.md` v1.2 | Routing aggregate + RoutingOperation with 6 base + 3 extended fields; `setup_time`, `run_time_per_unit`, `work_center_code` nullable | ✅ Source matches: `models/routing.py` has all fields; `schemas/routing.py` response has 3 extended fields | ALIGNED |
| `routing-foundation-contract.md` v1.2 Section 10.2 | `qc_checkpoint_count` rejected as RoutingOperation column | ✅ Not in model, not in schema | ALIGNED |
| `routing-foundation-contract.md` v1.2 Section 10.1 | `required_skill`, `required_skill_level` deferred to ResourceRequirement | ✅ Not on RoutingOperation in BE. **DRIFT in FE mock**: `RoutingOperationDetail.tsx` still has `required_skill`, `required_skill_level` in mockOperations fixture and displays them | DRIFT in FE SHELL mock — FE mock predates contract v1.2 decision |
| `resource-requirement-mapping-contract.md` v1.0 | RR aggregate: 10 fields, lifecycle inherited from parent routing, 5 `required_resource_type` values | ✅ Source matches: `models/resource_requirement.py` has exact fields; service validates 5 resource types | ALIGNED |
| `manufacturing-master-data-and-product-definition-domain.md` | MMD boundary: separate from Traceability, Inventory, Execution | ✅ No MMD→Execution coupling found in current source | ALIGNED |
| BOM (P0-B candidate per audit task spec) | BOM model + product structure | ❌ Not implemented — no design doc for BOM found under `02_domain/product_definition/`; no implementation | DOC-ONLY gap: BOM mentioned in domain overview but no contract doc or implementation |
| Reason Code Management (cross-domain) | Unified reason code registry | ❌ Not implemented — no design contract found; only operational downtime_reasons exists | DOC-ONLY gap: ReasonCodes SHELL exists but no design contract or backend implementation |
| `mmd-be-00-evidence-and-contract-lock.md` F3 | No `admin.master_data.*` action codes in RBAC registry | ✅ Confirmed: `rbac.py` has no master_data action codes; all MMD endpoints use `admin.user.manage` placeholder | KNOWN DEBT — pre-existing, documented |
| `mmd-be-00-evidence-and-contract-lock.md` F2 | Release/retire are direct mutations with no approval gate | ✅ Confirmed: `release_product()`, `retire_product()`, `release_routing()`, `retire_routing()` all mutate directly | KNOWN DEBT — pre-existing, documented |
| `mmd-be-00-evidence-and-contract-lock.md` F8 | RoutingOperation missing extended fields | ✅ RESOLVED by MMD-BE-01 (Alembic 0003, model v1.2, schema update) | RESOLVED |

---

## 12. Source / Report Drift Resolution

The following drifts were identified between existing audit reports and current source:

| Report Claim | Current Source Truth | Resolution |
|---|---|---|
| `mmd-current-state-report.md` (2026-05-01) states "No BOM API client file was found" | ✅ Still true — no `bomApi.ts` exists in `frontend/src/app/api/` | No drift |
| `mmd-current-state-report.md` states RoutingApi covers `routingApi.listRoutings()` and `routingApi.getRouting()` only | ✅ Still true — but this report adds that `RoutingOperationItemFromAPI` interface lacks 3 fields now returned by backend | **This audit adds new finding on top of previous report** |
| `mmd-be-00-evidence-and-contract-lock.md` F8 states RoutingOperation missing 6 extended fields | **Partially resolved**: MMD-BE-01 implemented 3 fields (setup_time, run_time_per_unit, work_center_code). 3 other fields (required_skill, required_skill_level) deferred; qc_checkpoint_count rejected. | PARTIAL RESOLUTION — noted |
| `mmd-be-01-hard-mode-evidence-pack.md` states "FE not in scope" | ✅ Confirmed — FE `routingApi.ts` was not updated as part of MMD-BE-01 (intentionally deferred). | No conflict — but gap now identified as a next slice target |
| `frontend-coverage-mmd-report.md` reports all 5 SHELL screens delivered and verified (build/lint/routes PASS) | ✅ Source confirms all 5 SHELL pages exist in `routes.tsx`, `screenStatus.ts`, `pages/` | ALIGNED |

---

## 13. MMD Boundary Risk Review

### 13.1 MMD vs Execution

**Status: CLEAN — no accidental coupling found.**

- No routing operation in MMD directly mutates work order state.
- No product page derives execution status from MMD data.
- FE does not allow route release to trigger execution.
- `release_routing()` / `retire_routing()` mutate MMD lifecycle only — no execution event emitted.
- Execution queries routings for applicability checks but MMD service is not called from execution service (confirmed by absence of routing_service import in execution-related service files).

**One note:** `RoutingOperationDetail.tsx` SHELL mock displays `qc_checkpoint_count` from mock data, which has been **rejected** as a RoutingOperation column per contract v1.2 (Quality Lite owns checkpoint definition). This is in a SHELL mock only; no backend coupling exists. But it should be corrected when this screen is connected.

### 13.2 MMD vs Quality

**Status: CLEAN at source level. Boundary risk in FE mock.**

- No QC pass/fail logic in MMD service layer.
- No acceptance gate inside MMD.
- `qc_checkpoint_count` is NOT on the backend RoutingOperation model (correctly rejected per contract).
- **Risk:** `RoutingOperationDetail.tsx` SHELL mock still shows `qc_checkpoint_count: 2` / `qc_checkpoint_count: 3` in the mock fixture and renders it as a display field. When this screen is connected to real backend data, this field will be absent and will silently display `undefined` or an old mock value unless the page is updated first.

**Recommended action:** Remove `qc_checkpoint_count` from `RoutingOperationDetail.tsx` mock fixture before connecting to backend (part of MMD-FE-05 slice).

### 13.3 MMD vs Material / Backflush

**Status: CLEAN — no coupling found.**

- No BOM save triggers inventory movement (BOM backend does not exist).
- No routing screen triggers backflush.
- No ERP posting from any MMD component.
- Material consumption is not MMD truth.

No risk at current implementation level.

### 13.4 MMD vs ERP/PLM

**Status: CLEAN — no coupling found.**

- No ERP master sync implemented.
- No financial inventory truth inside MMD.
- No PLM-like lifecycle workflow beyond P0-B lifecycle states.
- `display_metadata` JSON field on Product is a safe extension hook but does not imply ERP sync.

### 13.5 MMD vs ISA-88 Future Scope

**Status: CLEAN — no ISA-88 artifacts found in current source.**

- No `recipe`, `procedure`, `unit_procedure`, `operation_phase`, `equipment_module`, or `control_module` models, schemas, or tables found.
- Domain overview doc (`manufacturing-master-data-and-product-definition-domain.md`) mentions "recipe/formula/procedure/phase-ready definitions" as scope, but no implementation artifact exists.

**Classification:** Future/deferred. Safe to confirm out of scope for current P0-B.

---

## 14. Mock / Shell / Partial Connectivity Review

| Screen | Mock Disclosure | Correct Phase Label | Actions Correctly Disabled | Data Boundary Warning | Findings |
|---|---|---|---|---|---|
| ProductList | ✅ `BackendRequiredNotice` | ✅ PARTIAL in screenStatus | ✅ Create disabled | ✅ Blue info box | No governance issues |
| ProductDetail | ✅ `BackendRequiredNotice` | ✅ PARTIAL in screenStatus | ✅ Release, Retire disabled | ✅ | No governance issues |
| RouteList | ✅ `BackendRequiredNotice` | ✅ PARTIAL in screenStatus | ✅ Create disabled | ✅ | **Export button presence not confirmed as backend call — may be cosmetic** |
| RouteDetail | ✅ `BackendRequiredNotice` | ✅ PARTIAL in screenStatus | ✅ Save/Edit disabled | ✅ | No governance issues |
| RoutingOperationDetail | ✅ `MockWarningBanner SHELL` + `BackendRequiredNotice` + `ScreenStatusBadge` | ✅ SHELL | ✅ Edit, Release disabled | ✅ | Mock uses `work_center` (not `work_center_code`) and shows deferred/rejected fields (`required_skill`, `required_skill_level`, `qc_checkpoint_count`) |
| BomList | ✅ `MockWarningBanner SHELL` + `BackendRequiredNotice` + `ScreenStatusBadge` | ✅ SHELL | ✅ Create, Import disabled | ✅ | Mock BOMs include RELEASED status — no risk since no mutation possible |
| BomDetail | ✅ `MockWarningBanner SHELL` + `BackendRequiredNotice` + `ScreenStatusBadge` | ✅ SHELL | ✅ Edit, Release, Retire, Add Component disabled | ✅ | No governance issues |
| ResourceRequirements | ✅ `MockWarningBanner SHELL` + `BackendRequiredNotice` + `ScreenStatusBadge` | ✅ SHELL | ✅ Assign Resource, Edit per row disabled | ✅ | Mock schema diverges significantly from actual BE `ResourceRequirementItem` schema |
| ReasonCodes | ✅ `MockWarningBanner SHELL` + `BackendRequiredNotice` + `ScreenStatusBadge` | ✅ SHELL | ✅ Create, Edit, Retire disabled | ✅ | Domain filter (downtime/scrap/pause etc.) is UI-only; no backend validation |

**Verdict:** All SHELL screens correctly surface mock disclosure. No SHELL screen makes backend API calls. No SHELL screen allows lifecycle mutations. Governance compliance is maintained.

---

## 15. Tenant / Scope / Authorization Review

| Area | Finding | Risk Level |
|---|---|---|
| Product read endpoints (`GET /products`, `GET /products/:id`) | `require_authenticated_identity` — tenant_id from JWT, threaded to service and repository | SAFE |
| Routing read endpoints (`GET /routings`, `GET /routings/:id`) | `require_authenticated_identity` — tenant_id from JWT | SAFE |
| Resource Requirement read endpoints | `require_authenticated_identity` — tenant_id from JWT | SAFE |
| Product mutation endpoints (create, update, release, retire) | `require_action("admin.user.manage")` — **semantic mismatch**: this is a USER ADMIN action, not a MASTER DATA action | P1 PRE-EXISTING DEBT — documented in MMD-BE-00 F3 |
| Routing mutation endpoints (create, update, release, retire, ops management) | Same `admin.user.manage` placeholder | P1 PRE-EXISTING DEBT |
| Resource Requirement mutation endpoints | Same `admin.user.manage` placeholder | P1 PRE-EXISTING DEBT |
| Downtime Reason mutation endpoints | Same `admin.user.manage` placeholder | P1 PRE-EXISTING DEBT |
| Release/retire paths (product + routing) | Direct mutation — no approval gate | P1 GOVERNANCE DEBT — documented in MMD-BE-00 F2 |
| Plant/area/line scope on Products | Not present — Product is tenant-global in P0-B per contract | ALIGNED WITH P0-B CONTRACT |
| Plant/area/line scope on Routings | Not present — Routing is tenant-global in P0-B | ALIGNED WITH P0-B CONTRACT |
| Plant/area/line scope on ResourceRequirement | Not present — RR is tenant-global in P0-B | ALIGNED WITH P0-B CONTRACT |
| Scope hierarchy columns on DowntimeReason | `plant_code`, `area_code`, `line_code`, `station_scope_value` — declared but unused (baseline resolver uses only tenant_id + reason_code) | P3 TECH DEBT — documented in MMD-BE-00 F7 |
| `ACTION_CODE_REGISTRY` in `rbac.py` | Hardcoded Python dict — no `admin.master_data.*` entries exist | P1 — Fix requires source code edit + RBAC re-seed; blocks proper MMD permission model |

---

## 16. Gaps Blocking Implementation

The following gaps must be resolved before implementing certain MMD slices:

| ID | Gap | Severity | Blocks | Resolution Path |
|---|---|---|---|---|
| G1 | `routingApi.ts` FE interface (`RoutingOperationItemFromAPI`) missing `setup_time`, `run_time_per_unit`, `work_center_code` — backend now returns these fields | P1 | MMD-FULLSTACK-01 cannot accurately display extended operation data | Add 3 fields to `RoutingOperationItemFromAPI` in `routingApi.ts` |
| G2 | `RoutingOperationDetail.tsx` mock uses `work_center` (old name); canonical name is `work_center_code` | P2 | Will silently bind wrong field when screen connects to backend | Fix field name in mock; correct when connecting screen |
| G3 | `RoutingOperationDetail.tsx` mock includes `required_skill`, `required_skill_level`, `qc_checkpoint_count` — these are deferred/rejected per contract v1.2 | P2 | When screen is connected to real BE data, these fields will be undefined; display logic will silently fail | Remove from mock or mark as DEFERRED_FIELD before connecting |
| G4 | No `admin.master_data.*` RBAC action codes — all MMD mutations use `admin.user.manage` placeholder | P1 GOVERNANCE DEBT | Proper permission-based access control for MMD not possible; any ADMIN-role user can create/modify/release/retire master data | `ACTION_CODE_REGISTRY` in `rbac.py` needs new entries; permission re-seed required |
| G5 | Release/retire are direct mutations with no approval gate (product + routing) | P1 GOVERNANCE DEBT | Unauthorized single-user lifecycle decisions without SoD review | Approval service extension required; approval_service only handles 6 hardcoded action types (none are master_data) |
| G6 | BOM has zero backend (no model, schema, migration, service, API) and no design contract doc under `docs/design/02_domain/product_definition/` | P2 | BOM SHELL screens cannot be connected; BOM-linked product hierarchy cannot be built | Requires BOM foundation slice (MMD-BE-03) — high scope; create design contract first |
| G7 | Unified reason code management (cross-domain) has no backend — only `downtime_reasons` operational table exists | P2 | `/reason-codes` SHELL cannot connect; scrap/pause/reopen/quality_hold reason code management unavailable | Requires MMD-BE-04 reason code unification — medium scope |
| G8 | No resource requirements FE API client — backend nested path exists but is not consumed by frontend | P2 | `ResourceRequirements.tsx` SHELL cannot connect | Requires MMD-FE-06 — add `resourceRequirementApi.ts` with nested path |
| G9 | No pagination / server-side filter on any MMD list API (`/products`, `/routings`) | P3 SCALABILITY | At production scale, unbounded list responses could cause timeout or OOM on read | Requires API pagination + FE filter wiring; low priority for P0-B |
| G10 | No `work_centers` entity/table — `work_center_code` is a free-text string; no FK validation | P3 SOFT | Downstream code-to-record validation impossible; orphaned codes silently pass | Deferred per contract v1.2 Section 3 — acceptable for P0-B |
| G11 | Alembic migration `0003` (extended op fields) was NOT included in baseline SQL scripts `0001–0017` — must be applied separately on existing installations | P1 DEPLOYMENT | Installations provisioned before 2026-05-01 will not have `setup_time`, `run_time_per_unit`, `work_center_code` columns in `routing_operations` | Run `alembic upgrade head` on all existing environments |
| G12 | Backend pytest cannot be run in current PowerShell environment (no python/python3 in PATH; .venv/bin/python hangs) | P2 ENVIRONMENT | Cannot verify test pass/fail in this audit run | Requires Docker or WSL invocation; or env PATH fix |

---

## 17. Safe Next Implementation Slices

| Slice | Intent | In Scope | Out of Scope | Depends On | Risk | Recommendation |
|---|---|---|---|---|---|---|
| **MMD-FULLSTACK-01** — Routing Operation Extended Field FE/BE Contract Alignment | Align frontend `routingApi.ts` types with backend extended routing operation fields; update Routing Operation Detail display; remove/defer rejected mock-only fields; verify backend tests and FE build/lint/routes | (1) Add `setup_time`, `run_time_per_unit`, `work_center_code` to `RoutingOperationItemFromAPI` in `routingApi.ts`; (2) Connect `RoutingOperationDetail.tsx` to real routing response; (3) Fix `work_center` → `work_center_code`; (4) Remove `required_skill`, `required_skill_level`, `qc_checkpoint_count` from display; (5) Verify backend extended field tests pass; (6) Verify FE build/lint/routes pass | BOM implementation; Product Version implementation; Unified Reason Codes; Work Center entity; RBAC action-code migration; Backflush rule; Acceptance policy; ERP master data sync; Recipe/ISA-88 full model | G1, G2, G3 resolved; Alembic 0003 applied (G11) | LOW–MEDIUM — FE-side changes only; no new backend endpoints or migrations | **RECOMMENDED NEXT SLICE** |
| **MMD-FE-06** — Resource Requirement FE API Client | Add `resourceRequirementApi.ts` with nested path; wire `ResourceRequirements.tsx` to display real data for a selected routing/operation | Add FE API client for nested RR endpoint; update ResourceRequirements.tsx to accept routing + operation context | No new backend endpoints; no mutation; no auth change | G8 resolution; backend RR stack is complete | LOW — BE is complete; FE client is missing | **NEXT BATCH — safe to implement alongside MMD-FE-05** |
| **MMD-BE-02** — RBAC Action Code Fix for MMD | Add `admin.master_data.create`, `admin.master_data.update`, `admin.master_data.release`, `admin.master_data.retire` to `ACTION_CODE_REGISTRY`; update MMD endpoints to use correct action codes | `rbac.py` ACTION_CODE_REGISTRY update; endpoint dependency references updated; RBAC re-seed | No permission logic change beyond action code semantics; no new role tiers | G4 resolution; requires decision on which role tier (ADMIN vs new MASTER_DATA_MANAGER) | MEDIUM — affects all MMD mutation endpoints; needs RBAC re-seed | **RECOMMENDED before any MMD write-path FE work** |
| **MMD-BE-03** — BOM Foundation | BOM model + migration + read API | `bom` + `bom_items` tables; BOM model + schema + service + read-only GET endpoints; BOM linked to product_id | BOM release/retire approval gate; BOM-FE connection; backflush; full BOM explosion | G6 resolution; needs BOM design contract doc first; depends on Product model stable | MEDIUM-HIGH — new schema; requires migration design; new domain model | **NOT NEXT IMMEDIATE SLICE** — needs design contract first |
| **MMD-FULLSTACK-02** — Product + Routing + Resource Requirement Read Integration Hardening | Comprehensive read-path hardening across all 4 PARTIAL screens + resource requirement connection | Pagination on product/routing lists; FE filter wiring; RR API client integration; RouteDetail shows extended op fields | Write paths; lifecycle mutations; BOM; reason codes | G1, G8 resolved; MMD-FULLSTACK-01 complete | MEDIUM — cross-cutting FE slice | **MEDIUM TERM — after MMD-FULLSTACK-01 stabilizes** |
| **MMD-BE-04** — Reason Code Unification | Unified reason code management backend (cross-domain) | `reason_codes` table design + migration; reason code service; read API; map downtime_reasons to unified schema | FE connection; reason code FE management UI write paths | G7 resolution; design decision on whether to migrate existing `downtime_reasons` data or keep parallel | MEDIUM — schema design; data migration implications for existing downtime_reasons | **LOWER PRIORITY — operational downtime path works today via `downtime_reasons` API** |

---

## 18. Verification Commands

**Frontend verification (from prior audit evidence — `frontend-coverage-mmd-report.md` 2026-04-28):**

```bash
cd frontend
npm run build       # Previous result: PASS (built in ~7s)
npm run lint        # Previous result: PASS (0 errors)
npm run check:routes  # Previous result: PASS (0 FAIL)
npm run lint:i18n:registry  # Previous result: PASS (1092 keys, en/ja synchronized)
```

Current audit could not re-run frontend commands (Node.js/npm status not verified in this run). Source inspection confirms no MMD FE files were modified since last verification.

**Backend verification — blocked in current environment:**

```bash
cd backend
# Requires Python in PATH or .venv activation
# Windows PowerShell: python/python3 not found in system PATH
# .venv/bin/python exists (Linux-style path) but does not execute in PowerShell without activation
# Recommended: use Docker or WSL

# Inside Docker / WSL:
alembic current          # Should show: 0003 (head)
alembic heads            # Should show: 0003
python -m pytest tests/test_product_foundation_api.py tests/test_routing_foundation_api.py tests/test_resource_requirement_api.py tests/test_routing_operation_extended_fields.py -v
```

**Critical deployment check:**

```bash
# Verify Alembic migration 0003 has been applied:
alembic current
# Expected: 0003 (head)
# If shows 0001 or 0002: run alembic upgrade head before any routing operation read
```

---

## 19. Final Audit Verdict

**Overall MMD implementation health: PARTIAL — Backend ahead of frontend; BOM entirely missing; FE type drift introduced by MMD-BE-01.**

| Domain | Backend | Frontend | DB / Migration | Test Coverage | Verdict |
|---|---|---|---|---|---|
| Product | FULL_STACK | PARTIAL (read only) | COMPLETE (SQL 0014 + Alembic 0001 baseline) | PRESENT | ✅ Safe to build on |
| Routing | FULL_STACK (including extended fields) | PARTIAL (read only; FE type LAGS BE) | COMPLETE (SQL 0015 + Alembic 0001 baseline + 0003 extended fields) | PRESENT | ⚠️ FE type drift (G1) — fix before FE work |
| Routing Operation Extended Fields | FULL_STACK (read only; write deferred) | NOT REFLECTED IN FE API CLIENT | Alembic 0003 — must be applied | PRESENT (MMD-BE-01 tests) | ⚠️ Deployment gap (G11); FE client gap (G1) |
| Resource Requirement | FULL_STACK | SHELL (mock; no FE client) | COMPLETE (SQL 0016 + Alembic 0001 baseline) | PRESENT | ⚠️ FE client missing (G8) |
| Downtime Reason | FULL_STACK (operational) | CONNECTED for station execution | COMPLETE (SQL 0012) | PRESENT | ✅ Operational path safe |
| BOM | MISSING | SHELL (mock only) | MISSING | NONE | ❌ Entire domain absent — cannot implement without design contract + BE foundation |
| Work Center Entity | MISSING (string only) | N/A | MISSING | NONE | ⚠️ Deferred per P0-B contract — acceptable as string |
| Reason Code Management (cross-domain) | MISSING | SHELL (mock only) | MISSING | NONE | ❌ Absent — downtime_reasons is only operational coverage |
| Product Version | MISSING / GAP | MISSING | MISSING | NONE | ❌ Required by P0-B baseline but not implemented. Not the immediate next slice — stabilize Routing extended field alignment first. |
| RBAC / Authorization for MMD | MISSING (placeholder) | N/A | N/A | N/A | ❌ Pre-existing governance debt (G4, G5) |

## Recommended Next Slice

**MMD-FULLSTACK-01 — Routing Operation Extended Field FE/BE Contract Alignment**

Intent:
- Align frontend `routingApi.ts` types with backend extended routing operation fields.
- Update Routing Operation Detail display to use `work_center_code`.
- Remove/defer rejected mock-only fields from connected display: `required_skill`, `required_skill_level`, `qc_checkpoint_count`.
- Verify backend tests for routing extended fields still pass.
- Verify frontend build/lint/routes pass.

Out of scope:
- BOM implementation
- Product Version implementation
- Unified Reason Codes
- Work Center entity
- RBAC action-code migration
- Backflush rule
- Acceptance policy
- ERP master data sync
- Recipe/ISA-88 full model

**Do NOT implement yet without resolving prerequisites:**
- BOM backend (G6 — no design contract)
- Release/retire approval gate (F2 / G5 — approval service extension needed)
- Unified reason code management (G7 — design decision pending)
- Any MMD write-path FE flows (G4 — RBAC action codes not defined)

**Not in P0-B scope — confirm out of P0-B:**
- Recipe / ISA-88 model
- ERP master sync
- Advanced versioning workflow (PLM-level full version management)
- PLM integration
- Full BOM explosion
- AI-generated routing definitions
- Digital Twin scenario generation from MMD

---

*Audit produced by: AI Brain (MOM Brain, Audit Mode, Hard Mode MOM v3 source-truth discipline)*  
*Audit date: 2026-05-02*  
*No source code, migrations, or contracts were modified in producing this report.*
