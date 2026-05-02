# MMD-READ-BASELINE-01 — MMD Read Integration Baseline Freeze / Handoff

## History

| Date       | Version | Change                                                                                                            |
|------------|--------:|-------------------------------------------------------------------------------------------------------------------|
| 2026-05-02 |    v1.0 | Frozen MMD read integration baseline after MMD-AUDIT-00 and MMD-FULLSTACK-01 through 04. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Audit / Source-Truth Discipline
- **Hard Mode MOM:** v3 ON — review discipline for MMD manufacturing definition truth; no implementation.
- **Reason:** MMD is the canonical manufacturing definition layer consumed by execution, quality, material/traceability, planning, and digital twin. Freeze reports incorrect baseline claims corrupt downstream slices. Documentation-only; no source, migration, or contract was modified.

---

## 1. Scope

This freeze report covers the state of Manufacturing Master Data (MMD) / Product Definition across the `autocode` branch after five sequential slices:

| Slice | ID | Type | Summary |
|---|---|---|---|
| MMD-AUDIT-00 | Source alignment audit | Read-only | Full-stack gap inventory across FE, BE, API, migrations |
| MMD-FULLSTACK-01 | FE/BE contract alignment | FE read-only | Fixed work_center drift; added 3 extended fields to FE type; removed rejected fields |
| MMD-FULLSTACK-02 | Routing Operation Detail read integration | FE read | Replaced shell/mock with live backend read |
| MMD-FULLSTACK-03 | Resource Requirements read integration | FE read | Replaced shell/mock with live nested backend API |
| MMD-FULLSTACK-04 | Navigation context link | FE navigation | Added contextual link from Routing Operation Detail to Resource Requirements |

Scope boundary: P0-B read-integration only. Write-path, BOM backend, Product Version, Work Center entity, Unified Reason Codes, RBAC action-code migration, ERP integration, quality, material/backflush, recipe/ISA-88 are explicitly out of scope.

---

## 2. Baseline Inputs Reviewed

| Input | Status | Notes |
|---|---|---|
| `docs/audit/mmd-audit-00-fullstack-source-alignment.md` | ✅ Inspected | v1.0 — full-stack gap inventory (F1–F9 findings, including field drift and deferred fields) |
| `docs/audit/mmd-fullstack-01-routing-operation-contract-alignment.md` | ✅ Inspected | v1.0 — work_center fix, 3 extended fields added to FE, rejected fields removed |
| `docs/audit/mmd-fullstack-02-routing-operation-detail-read-integration.md` | ✅ Inspected | v1.0 — shell→backend_api, loading/error/notFound states |
| `docs/audit/mmd-fullstack-03-resource-requirements-read-integration.md` | ✅ Inspected | v1.0 — shell→backend_api, nested API integration, scope filtering |
| `docs/audit/mmd-fullstack-04-routing-operation-resource-requirement-context-link.md` | ✅ Inspected | v1.0 — contextual link with encodeURIComponent, clear-filter escape |
| `docs/audit/mmd-be-00-evidence-and-contract-lock.md` | ✅ Inspected | v1.0 — F1-F9 backend evidence findings |
| `docs/audit/mmd-be-01-hard-mode-evidence-pack.md` | ✅ Inspected | v1.1 — Routing extended fields evidence (scope-reduced to 3 nullable fields) |
| `docs/audit/frontend-coverage-baseline-freeze-report.md` | ✅ Inspected | 5-screen MMD shell delivery report |
| `docs/audit/frontend-source-alignment-snapshot.md` | ✅ Inspected | v1.24 — cumulative FE slice history |
| `frontend/src/app/screenStatus.ts` | ✅ Inspected | Current working-tree state |
| `frontend/src/app/api/routingApi.ts` (HEAD commit) | ✅ Inspected | Committed FE API type |
| `backend/app/models/routing.py` (HEAD commit) | ✅ Inspected | Committed model — no extended fields |
| `backend/app/schemas/routing.py` (HEAD commit) | ✅ Inspected | Committed schema — no extended fields |
| `backend/app/models/routing.py` (working tree) | ✅ Inspected | Working tree — has extended fields (MMD-BE-01, uncommitted) |

**Optional inputs — not present under standard paths:**

| Input | Status |
|---|---|
| `docs/design/02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md` | Referenced in MMD-AUDIT-00; not re-read for this freeze |
| `docs/design/02_domain/product_definition/routing-foundation-contract.md` | Referenced in MMD-AUDIT-00 and MMD-FULLSTACK-01; not re-read |
| `docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md` | Referenced; not re-read |

---

## 3. Workspace / Git State

**Branch:** `autocode`  
**HEAD commit:** `9a3da0de` — `feat(mmd): link routing operations to resource requirements` (MMD-FULLSTACK-04)

### MMD Slice Commit History (most recent first)

| Commit | Message | Slice |
|---|---|---|
| `9a3da0de` | feat(mmd): link routing operations to resource requirements | MMD-FULLSTACK-04 |
| `a4f80e36` | feat(mmd): connect resource requirements read view | MMD-FULLSTACK-03 |
| `28468219` | feat(mmd): connect routing operation detail read view | MMD-FULLSTACK-02 |
| `50c785cc` | fix(mmd): align routing operation extended fields contract | MMD-FULLSTACK-01 |
| `a7b7e7eb` | docs(mmd): align audit baseline with P0-B scope | MMD-AUDIT-00 |

**All MMD-FULLSTACK-01 through 04 FE changes are committed.** No uncommitted changes in:

- `frontend/src/app/pages/RoutingOperationDetail.tsx`
- `frontend/src/app/pages/ResourceRequirements.tsx`
- `frontend/src/app/i18n/registry/en.ts`
- `frontend/src/app/i18n/registry/ja.ts`

### ⚠ Working Tree — Uncommitted Changes

**Unrelated to MMD FE read pages (safe for freeze):**

| File | Status | Domain |
|---|---|---|
| `backend/app/api/v1/station.py` | Modified | Execution / Station |
| `backend/app/schemas/station.py` | Modified | Execution / Station |
| `backend/app/services/station_claim_service.py` | Modified | Execution / Station |
| `backend/app/services/operation_service.py` | Modified | Execution / Operation |
| Various backend test files | Modified/Deleted | Execution / Station |
| `frontend/src/app/api/stationApi.ts` | Modified | Execution / Station |
| `frontend/src/app/pages/ActionRegistry.tsx` etc. | Modified | Governance / Admin UI |
| `frontend/src/app/persona/personaLanding.ts` | Modified | Persona/Navigation |

**⚠ MMD-related — uncommitted (MMD-BE-01):**

| File | Status | Notes |
|---|---|---|
| `backend/app/models/routing.py` | Modified (working tree only) | Adds `setup_time`, `run_time_per_unit`, `work_center_code` to `RoutingOperation` |
| `backend/app/schemas/routing.py` | Modified (working tree only) | Adds same 3 fields to `RoutingOperationItem` response schema |
| `backend/app/services/routing_service.py` | Modified (working tree only) | Routing service update for MMD-BE-01 |
| `backend/alembic/versions/0003_routing_operation_extended_fields.py` | Untracked (not committed) | Alembic migration to add 3 columns to `routing_operations` table |
| `backend/tests/test_routing_operation_extended_fields.py` | Untracked (not committed) | MMD-BE-01 model/schema/API test |

**Impact of MMD-BE-01 uncommitted state:**  
At runtime with committed-only backend, the API response for routing operations will **not** include `setup_time`, `run_time_per_unit`, `work_center_code`. The FE type declares these as optional/nullable (`?`) and the UI uses `?? "—"` null guards. The display is safe — these fields render as `"—"` until the backend changes are committed and deployed.

**This freeze covers committed source state. MMD-BE-01 backend changes must be committed in a separate slice before they are considered part of the operational baseline.**

---

## 4. Source / Report Drift Resolution

### Drift A — Resource Requirements status

**Older audit said:** Resource Requirements is SHELL/mock and FE does not consume backend API.  
**Current source:** `ResourceRequirements.tsx` (committed HEAD) fully replaced with backend API integration. `screenStatus.ts` marks `resourceRequirements` as `phase: "PARTIAL", dataSource: "BACKEND_API"`.  
**Resolution: DRIFT RESOLVED — MMD-FULLSTACK-03 committed. Resource Requirements is PARTIAL/BACKEND_API.** No mock data remains in this page.

### Drift B — Routing Operation Detail status

**Older audit said:** Routing Operation Detail is SHELL/mock and uses incorrect `work_center` field.  
**Current source:** `RoutingOperationDetail.tsx` (committed HEAD) reads backend routing API by `routeId`/`operationId`. `work_center_code` used correctly. Rejected fields (`required_skill`, `required_skill_level`, `qc_checkpoint_count`) removed. `screenStatus.ts` marks as `phase: "PARTIAL", dataSource: "BACKEND_API"`.  
**Resolution: DRIFT RESOLVED — MMD-FULLSTACK-01 contract alignment and MMD-FULLSTACK-02 read integration both committed.**

### Drift C — Backend extended fields deployment state

**Audit reports said (MMD-FULLSTACK-01):** Backend model/schema/alembic for `setup_time`, `run_time_per_unit`, `work_center_code` were confirmed present per MMD-BE-01.  
**Git HEAD (committed backend):** These 3 fields are NOT in the committed routing model/schema. They are in the working tree only.  
**Resolution: PARTIAL DRIFT — MMD-BE-01 backend changes are in the working tree, documented in audit reports, but the model/schema/alembic migration are not yet committed. This is a deployment gap, not a regression. The FE API type correctly declares these as optional; null-guards prevent display breakage. MMD-BE-01 backend commit must be a prerequisite before any slice that relies on these fields having non-null runtime values.**

### Drift D — Product Version

**Correct freeze decision:** Product Version is required by P0-B baseline but not yet implemented in either FE or BE. It is a planned future narrow slice, not an accidental omission. `screenStatus.ts` has no `productVersion` entry; there is no `/product-versions` route.

### Drift E — BOM and Reason Codes

**BOM:** `BomList.tsx` and `BomDetail.tsx` use inline mock fixtures (confirmed by source inspection). `screenStatus.ts` marks both as `phase: "SHELL", dataSource: "MOCK_FIXTURE"`. No backend BOM API or migration exists in this codebase at this time.  
**Reason Codes:** `ReasonCodes.tsx` uses inline mock fixtures. `screenStatus.ts` marks as `phase: "SHELL", dataSource: "MOCK_FIXTURE"`. No unified reason-code backend API exists. `downtime_reasons` is a separate operational reference table, not the unified MMD reason-code system.

---

## 5. Frozen MMD Route Inventory

| Route | Page File | Current Data Source | Screen Status | Backend API Used | Freeze Status | Notes |
|---|---|---|---|---|---|---|
| `/products` | `ProductList.tsx` | `BACKEND_API` | `PARTIAL` | `GET /v1/products` | ✅ PARTIAL_BACKEND_READ | Create action disabled |
| `/products/:productId` | `ProductDetail.tsx` | `BACKEND_API` | `PARTIAL` | `GET /v1/products/{id}` | ✅ PARTIAL_BACKEND_READ | Lifecycle mutation disabled |
| `/routes` | `RouteList.tsx` | `BACKEND_API` | `PARTIAL` | `GET /v1/routings` | ✅ PARTIAL_BACKEND_READ | Create/release actions disabled |
| `/routes/:routeId` | `RouteDetail.tsx` | `BACKEND_API` | `PARTIAL` | `GET /v1/routings/{id}` | ✅ PARTIAL_BACKEND_READ | Operations list read; mutation disabled |
| `/routes/:routeId/operations/:operationId` | `RoutingOperationDetail.tsx` | `BACKEND_API` | `PARTIAL` | `GET /v1/routings/{id}` (selects op from result) | ✅ PARTIAL_BACKEND_READ | Extended fields null-guarded; context link to RR present |
| `/resource-requirements` | `ResourceRequirements.tsx` | `BACKEND_API` | `PARTIAL` | `GET /v1/routings`, `GET /v1/routings/{id}/operations/{opId}/resource-requirements` | ✅ PARTIAL_BACKEND_READ | Scope filtering by routeId/operationId; clear-filter link |
| `/bom` | `BomList.tsx` | `MOCK_FIXTURE` | `SHELL` | None | 🔴 SHELL | Inline mock data; no backend BOM API |
| `/bom/:bomId` | `BomDetail.tsx` | `MOCK_FIXTURE` | `SHELL` | None | 🔴 SHELL | Inline mock data; no backend BOM API |
| `/reason-codes` | `ReasonCodes.tsx` | `MOCK_FIXTURE` | `SHELL` | None | 🔴 SHELL | Inline mock data; no unified reason-code API |

---

## 6. Frontend Read Integration Baseline

| Screen | Route | FE File | API Client / Helper | Reads Backend? | Mock Remaining? | Read-Only? | Status |
|---|---|---|---|---|---|---|---|
| Product List | `/products` | `ProductList.tsx` | `productApi.listProducts()` | ✅ Yes | None | ✅ | PARTIAL/BACKEND_API |
| Product Detail | `/products/:productId` | `ProductDetail.tsx` | `productApi.getProduct()` | ✅ Yes | None (main fields) | ✅ | PARTIAL/BACKEND_API |
| Route List | `/routes` | `RouteList.tsx` | `routingApi.listRoutings()` | ✅ Yes | None | ✅ | PARTIAL/BACKEND_API |
| Route Detail | `/routes/:routeId` | `RouteDetail.tsx` | `routingApi.getRouting()` | ✅ Yes | None | ✅ | PARTIAL/BACKEND_API |
| Routing Operation Detail | `/routes/:routeId/operations/:operationId` | `RoutingOperationDetail.tsx` | `routingApi.getRouting()` + operation selection | ✅ Yes | None (displays `"—"` for uncommitted extended fields at runtime) | ✅ | PARTIAL/BACKEND_API |
| Resource Requirements | `/resource-requirements` | `ResourceRequirements.tsx` | `routingApi.listRoutings()`, `routingApi.listResourceRequirements()` | ✅ Yes | None | ✅ | PARTIAL/BACKEND_API |
| BOM List | `/bom` | `BomList.tsx` | None | ❌ No | All data is inline mock | ✅ (no writes either) | SHELL/MOCK_FIXTURE |
| BOM Detail | `/bom/:bomId` | `BomDetail.tsx` | None | ❌ No | All data is inline mock | ✅ (no writes either) | SHELL/MOCK_FIXTURE |
| Reason Codes | `/reason-codes` | `ReasonCodes.tsx` | None | ❌ No | All data is inline mock | ✅ (no writes either) | SHELL/MOCK_FIXTURE |

---

## 7. Backend API / Contract Baseline

| Capability | Backend Path / Handler | Model | Schema | Tests | Status | Notes |
|---|---|---|---|---|---|---|
| Product | `GET /v1/products`, `POST /v1/products`, `GET /v1/products/{id}`, `PATCH`, lifecycle transitions | `Product` | `ProductItem`, `ProductCreateRequest`, `ProductUpdateRequest` | `test_product_foundation_api.py`, `test_product_foundation_service.py` | ✅ IMPLEMENTED | Read + write lifecycle; FE only uses read |
| Routing | `GET /v1/routings`, `POST`, `GET /v1/routings/{id}`, `PATCH`, lifecycle | `Routing` | `RoutingItem`, create/update requests | `test_routing_foundation_api.py`, `test_routing_foundation_service.py` | ✅ IMPLEMENTED | Read + write lifecycle; FE only uses read |
| Routing Operation | Embedded in Routing responses; CRUD under `/v1/routings/{id}/operations` | `RoutingOperation` | `RoutingOperationItem` (committed: 5 fields; working tree: +3 extended) | `test_routing_foundation_api.py`, `test_routing_operation_extended_fields.py` (untracked) | ✅ COMMITTED (base); ⚠️ WORKING TREE (extended fields) | Extended fields uncommitted; FE null-guards handle this safely |
| Routing Operation Extended Fields | Same API, fields in model/schema | `RoutingOperation.setup_time`, `.run_time_per_unit`, `.work_center_code` | `RoutingOperationItem.setup_time` etc. | `test_routing_operation_extended_fields.py` (untracked) | ⚠️ WORKING TREE ONLY — not committed | Alembic 0003 also untracked; must commit before relying on non-null values |
| Resource Requirement | `GET /v1/routings/{id}/operations/{opId}/resource-requirements`, CRUD | `ResourceRequirement` | `ResourceRequirementItem`, create/update | `test_resource_requirement_api.py`, `test_resource_requirement_service.py` | ✅ IMPLEMENTED | Full CRUD in BE; FE uses read only |
| BOM | None | None | None | None | 🔴 NOT IMPLEMENTED | No backend BOM entity, migration, or API exists |
| Unified Reason Codes | None | `DowntimeReason` (operational reference only) | None (unified system) | `test_downtime_reasons_endpoint.py` (operational reasons only) | 🔴 NOT IMPLEMENTED | `downtime_reasons` is execution domain; not MMD unified reason-code registry |
| Product Version | None | None | None | None | 🔴 NOT IMPLEMENTED | Required by P0-B; deferred |
| Work Center Entity | None | None | None | None | 🔴 NOT IMPLEMENTED | `work_center_code` is a free-text string field on RoutingOperation; no Work Center master entity |

---

## 8. Database / Migration Baseline

| Migration | File | Scope | Status | Notes |
|---|---|---|---|---|
| `0014_products.sql` | `backend/scripts/migrations/0014_products.sql` | Products table | ✅ Committed | Product foundation |
| `0015_routings.sql` | `backend/scripts/migrations/0015_routings.sql` | Routings + routing_operations tables | ✅ Committed | Routing foundation (base fields only) |
| `0016_resource_requirements.sql` | `backend/scripts/migrations/0016_resource_requirements.sql` | Resource requirements table | ✅ Committed | Full resource requirement schema |
| Alembic 0001 baseline | `backend/alembic/versions/0001_baseline.py` | No-op stamp | ✅ Committed | Baseline stamp |
| Alembic 0003 routing extended fields | `backend/alembic/versions/0003_routing_operation_extended_fields.py` | `routing_operations`: adds `setup_time`, `run_time_per_unit`, `work_center_code` | ⚠️ UNTRACKED — not committed | Must be committed and applied before runtime extended fields work |

**BOM, Product Version, Work Center, Unified Reason Codes: no migrations exist.**

---

## 9. Contract Corrections Locked

| Correction | Slice | Current Locked Decision | Why It Matters |
|---|---|---|---|
| `work_center` → `work_center_code` | MMD-FULLSTACK-01 | FE API type uses `work_center_code`; `work_center` field removed from all FE displays | `work_center` was a fabricated field not present in any backend model/schema |
| `setup_time`, `run_time_per_unit`, `work_center_code` added to `RoutingOperationItemFromAPI` | MMD-FULLSTACK-01 | FE type has all 3 as optional nullable; null-guards in display | Aligns FE type with MMD-BE-01 working-tree schema (committed when MMD-BE-01 is committed) |
| `required_skill` / `required_skill_level` removed from Routing Operation display | MMD-FULLSTACK-01 | Not rendered in RoutingOperationDetail; not in FE API type | Deferred to Resource Requirement domain; not in committed routing schema |
| `qc_checkpoint_count` removed from Routing Operation display | MMD-FULLSTACK-01 | Quality section removed from RoutingOperationDetail | Quality domain owns this truth; not in MMD routing operation schema |
| Routing Operation Detail reads route detail API | MMD-FULLSTACK-02 | `routingApi.getRouting(routeId)` then find op by `operationId`; no new endpoint needed | Previous implementation was shell/mock |
| Resource Requirements reads backend nested API | MMD-FULLSTACK-03 | `routingApi.listResourceRequirements(routingId, operationId)` via nested REST path | Previous implementation was shell/mock |
| Routing Operation Detail links to Resource Requirements with `routeId`/`operationId` | MMD-FULLSTACK-04 | Link uses `encodeURIComponent`; navigation only; no auth or execution claim | Enables contextual UX between two connected MMD read views |
| Resource Requirements has clear-filter escape | MMD-FULLSTACK-04 | Clear-filter link in scope banner when any query param present | Ensures user can always return to global RR view |

---

## 10. Navigation / Context Link Baseline

| Source | Target | Params | Behavior | Slice |
|---|---|---|---|---|
| `/routes/:routeId` | `/routes/:routeId/operations/:operationId` | `routeId`, `operationId` from list click | Navigate to op detail | Pre-existing |
| `/routes/:routeId/operations/:operationId` | `/resource-requirements?routeId=:routeId&operationId=:operationId` | Both URL-encoded | View operation's resource requirements | MMD-FULLSTACK-04 |
| `/resource-requirements?routeId=...` | `/resource-requirements` | Strips all params | Clear filter to global mode | MMD-FULLSTACK-04 |
| `/products/:productId` | `/routes` (filtered by product? — not yet) | None | No contextual link yet | Gap — deferred |

---

## 11. Screen Status Baseline

As of HEAD commit (`9a3da0de`), `frontend/src/app/screenStatus.ts`:

| Screen ID | Route | Phase | Data Source | Notes |
|---|---|---|---|---|
| `productList` | `/products` | `PARTIAL` | `BACKEND_API` | Create disabled |
| `productDetail` | `/products/:productId` | `PARTIAL` | `BACKEND_API` | Mutation disabled |
| `routeList` | `/routes` | `PARTIAL` | `BACKEND_API` | Create/release disabled |
| `routeDetail` | `/routes/:routeId` | `PARTIAL` | `BACKEND_API` | Mutation disabled |
| `routingOpDetail` | `/routes/:routeId/operations/:operationId` | `PARTIAL` | `BACKEND_API` | Mutation disabled; context link to RR present |
| `resourceRequirements` | `/resource-requirements` | `PARTIAL` | `BACKEND_API` | Mutation disabled; scope filtering active |
| `bomList` | `/bom` | `SHELL` | `MOCK_FIXTURE` | No backend BOM |
| `bomDetail` | `/bom/:id` | `SHELL` | `MOCK_FIXTURE` | No backend BOM |
| `reasonCodes` | `/reason-codes` | `SHELL` | `MOCK_FIXTURE` | No unified reason code API |

---

## 12. Boundary Guardrails

| Boundary | Current Decision | Enforcement / Evidence | Risk if Violated |
|---|---|---|---|
| MMD vs Execution | MMD defines manufacturing definitions. Execution confirms operational reality. | `RoutingOperationDetail` MockWarningBanner: "Operation execution eligibility is determined by backend execution system." | Future agent adds execution dispatch button to Routing Operation Detail. |
| MMD vs Quality | Quality domain owns quality evaluation truth. | Quality section removed from RoutingOperationDetail (MMD-FULLSTACK-01); `qc_checkpoint_count` not in schema. | Future agent re-adds Quality section to Routing Operation Detail with fabricated data. |
| MMD vs Resource Requirement | Resource Requirement is an MMD sub-domain. All RR write-path is backend-governed. | All RR write action buttons remain `disabled` with lock icons. Assign/Edit remain disabled. | Future agent enables Assign Resource button with FE-only logic. |
| MMD vs Material / Backflush | BOM and material consumption are backend truths. | BOM pages are SHELL; no backflush API exists in FE. | Future agent adds BOM write to FE without backend API. |
| MMD vs ERP / PLM | ERP master data sync, product version approval, and PLM import are out of scope. | Not implemented; no API for these in current codebase. | Future agent adds "Sync to ERP" button to Product or Routing pages. |
| MMD vs Work Center entity | `work_center_code` is a free-text field. No Work Center master entity exists. | `work_center_code` rendered as `font-mono` text with `?? "—"` guard. No link to Work Center page. | Future agent treats `work_center_code` as a foreign-key reference to a non-existent Work Center API. |
| Frontend route/link vs authorization truth | Navigation links are UX-only. No authorization is implied or granted by link presence. | All mutation buttons remain `disabled`; server-side RBAC unchanged. Context link uses `<Link>` only (no POST). | Future agent adds a link that implies execution authorization or quality pass/fail. |
| MMD-BE-01 deployment gap | Backend extended fields in working tree, not committed. FE null-guards safe at runtime. | `setup_time`, `run_time_per_unit`, `work_center_code` render as `"—"` until committed+deployed. | Future agent assumes extended fields have runtime values without first committing MMD-BE-01. |

---

## 13. Verification Commands

### Frontend (run from `frontend/`)

All results are from the committed HEAD state.

| Command | Invocation Used | Result |
|---|---|---|
| i18n registry parity | `node scripts/check_i18n_registry_parity.mjs` | ✅ PASS — 1702 keys, en.ts = ja.ts |
| Route smoke | `node scripts/route-smoke-check.mjs` | ✅ PASS — all gates passed |
| Vite build | `node node_modules/vite/bin/vite.js build` | ✅ PASS — built in ~8s (pre-existing chunk-size warning, not caused by MMD slices) |
| ESLint | `node node_modules/eslint/bin/eslint.js src/ --ext .ts,.tsx` | ✅ PASS — no output = no errors |
| TypeScript | VS Code language server | ✅ PASS — no TS errors in changed files |

### Backend (run from `backend/`, working tree including MMD-BE-01)

| Command | Result |
|---|---|
| `python -m pytest -q tests/test_product_foundation_api.py tests/test_product_foundation_service.py tests/test_routing_foundation_api.py tests/test_routing_foundation_service.py tests/test_routing_operation_extended_fields.py tests/test_resource_requirement_api.py tests/test_resource_requirement_service.py` | ✅ **33 passed** in 2.86s |

> Note: `test_routing_operation_extended_fields.py` runs against the working-tree model/schema (which includes MMD-BE-01 changes). This test will need Alembic 0003 to be applied against the live database before passing in a deployed environment.

---

## 14. Remaining Gaps / Deferred Items

| Gap | Current State | Why Deferred | Recommended Future Slice | Priority |
|---|---|---|---|---|
| MMD-BE-01 backend commit (extended fields + Alembic 0003) | Working tree only; not committed | Held as separate working-tree change pending review/commit | Commit as `MMD-BE-01-COMMIT` or include in a broader backend stabilization pass | **High** — blocks extended field display |
| Product Version entity | Not implemented (no model, schema, API, migration, FE page, or route) | P0-B requires it; not yet scoped for a slice | `MMD-BE-03 — Product Version Foundation Contract / Minimal Read Model` | High |
| BOM backend | No BE entity or migration exists; FE is SHELL | BOM requires product versioning design decisions first | After Product Version is stable | Medium |
| Unified Reason Codes | No unified API exists; `downtime_reasons` is execution domain only | Requires domain separation design | Separate MMD reason-code slice | Medium |
| Work Center entity | `work_center_code` is free-text string; no Work Center master entity | Deferred per MMD-BE-00 (F9); no FK relationship designed | Future narrow slice after BOM/Version stabilized | Low |
| RBAC `admin.master_data.*` action codes | Action codes for MMD mutations not defined; placeholder `admin.user.manage` in some paths | MMD mutation paths not yet exposed in FE | `MMD-BE-02 — RBAC Action Code Fix for MMD Master Data Mutations` | Medium |
| Resource Requirement write-path UI | All RR write actions remain `disabled` | Backend write API exists but FE governance workflow not designed | Future write-path slice after RBAC action codes are defined | Medium |
| Routing Operation extended fields write-path | No FE or BE write-path for `setup_time`, `run_time_per_unit`, `work_center_code` | Explicitly deferred per MMD-BE-01 | Future write-path slice after RBAC | Medium |
| Server-side pagination/filtering | Not implemented for any MMD read endpoint | Product/Routing list sizes are manageable in P0-B scope | Future scalability slice | Low |
| Runtime visual QA for MMD read pages | Not performed in these slices (only build/lint/smoke verified) | Requires a live backend environment | `MMD-FE-QA-01 — MMD Read Pages Runtime Visual QA + Responsive Sweep` | Medium |
| MMD read integration regression tests | No dedicated FE-level regression tests for query-param routing, context link, or load behaviors | Requires test framework decisions | `MMD-FULLSTACK-05 — MMD Read Integration Regression Tests` | High |

---

## 15. Recommended Next Slices

| Candidate Slice | Intent | In Scope | Out of Scope | Why / When |
|---|---|---|---|---|
| `MMD-BE-01-COMMIT` | Commit the working-tree MMD-BE-01 backend changes (model, schema, alembic 0003) | Commit `routing.py` model, `routing.py` schema, `routing_service.py`, alembic `0003`, `test_routing_operation_extended_fields.py` | Any new fields, endpoints, or FE changes | Must precede any slice that depends on extended fields having runtime non-null values |
| `MMD-FULLSTACK-05` | MMD Read Integration Regression Tests | FE behavioral tests: query-param routing, context link, scope filtering, error states | Write-path, execution, quality, BOM | Lock current read integration before opening new domains |
| `MMD-BE-02` | RBAC Action Code Fix for MMD Master Data Mutations | Define `admin.master_data.manage` or equivalent action codes | Write-path UI | Must precede write-path FE; resolves RBAC placeholder issue |
| `MMD-BE-03` | Product Version Foundation Contract / Minimal Read Model | Product Version model, schema, minimal API, migration | Full version lifecycle, approval workflow, ERP sync | P0-B requires Product Version; needed before BOM design |
| `MMD-FE-QA-01` | MMD Read Pages Runtime Visual QA + Responsive Sweep | Visual QA of all 6 PARTIAL/BACKEND_API MMD pages; responsive breakpoints | New features, write-path | Validates UX correctness before scope expansion |

### Final Next Slice Recommendation

**Recommended: `MMD-FULLSTACK-05 — MMD Read Integration Regression Tests`**

**Rationale:**  
All 4 MMD read integration slices are committed. Before opening new backend domains (Product Version, BOM) or write-path flows, the current read integration should be locked with behavioral regression tests. This prevents future agents from reintroducing mock data, breaking query-param filtering, removing null guards, or severing the contextual navigation link.  

MMD-BE-01 backend commit should happen concurrently or immediately before MMD-FULLSTACK-05 so that extended fields can be tested with non-null values.

---

## 16. Do-Not-Do Rules for Next Agents

Future agents working on MMD read screens **MUST NOT**:

1. **Reintroduce mock/fixture data** into `RoutingOperationDetail.tsx`, `ResourceRequirements.tsx`, `RouteList.tsx`, `RouteDetail.tsx`, `ProductList.tsx`, or `ProductDetail.tsx`. These are PARTIAL/BACKEND_API.

2. **Remove `encodeURIComponent` from the context link** in `RoutingOperationDetail.tsx`. This prevents URL injection.

3. **Add execution dispatch buttons** or any action that implies execution readiness to Routing Operation Detail or Resource Requirements pages.

4. **Add quality truth claims** (pass/fail, QC checkpoint counts, quality hold status) to any MMD read page.

5. **Treat `work_center_code` as a foreign-key reference** to a Work Center entity. It is a free-text string field with no backend entity.

6. **Assume extended fields (`setup_time`, `run_time_per_unit`, `work_center_code`) have non-null runtime values** until MMD-BE-01 backend changes (model, schema, alembic 0003) are committed and deployed.

7. **Enable write actions** on Resource Requirements (`Assign Resource`, `Edit`) without first establishing RBAC action codes and backend-governed mutation API.

8. **Implement BOM backend** without first completing Product Version foundation (`MMD-BE-03`).

9. **Claim a screen is `CONNECTED`** in `screenStatus.ts` unless all displayed fields are live, all write-path is functional, and no disabled placeholders remain.

10. **Modify backend source** in any FE-only navigation or read integration slice.

---

## 17. Final Freeze Verdict

**FREEZE ACCEPTED — with one open prerequisite.**

### Accepted

| Item | Evidence |
|---|---|
| MMD-FULLSTACK-01 through 04 all committed | `git log --oneline` confirms 4 commits |
| 6 MMD FE screens PARTIAL/BACKEND_API | Confirmed by `screenStatus.ts` + source inspection |
| Resource Requirements field drift resolved | MMD-FULLSTACK-03 committed |
| Routing Operation Detail field drift resolved | MMD-FULLSTACK-01 + 02 committed |
| Contract corrections locked | Section 9 inventoried |
| Navigation context link present | MMD-FULLSTACK-04 committed |
| Backend MMD test suite passes | 33 passed (working tree) |
| All FE verification gates pass | i18n parity 1702 keys, route smoke, build, lint all PASS |

### Open Prerequisite

| Item | Risk | Action Required |
|---|---|---|
| MMD-BE-01 backend changes (model/schema/alembic 0003) uncommitted | Extended fields show `"—"` in production until committed | Commit MMD-BE-01 working-tree changes as a dedicated slice before any reliance on non-null extended field values |

This freeze covers committed source state only. The MMD-BE-01 working-tree state is documented here as a known deployment gap, not a regression.

---

*Report created: 2026-05-02. Source basis: `autocode` branch HEAD `9a3da0de`.*
