# Manufacturing Master Data Current-State Report — FleziBCG

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Created current-state report for Manufacturing Master Data frontend coverage and product meaning. Based on source inspection of all 9 MMD screens, API clients, screenStatus registry, persona/navigation config, and i18n registry. |

---

## 1. Purpose

This report documents the current state of the Manufacturing Master Data (MMD) area of the FleziBCG MOM/MES frontend. It serves as:

- a factual baseline for Product Owner and Solution Architect review;
- a reference for coding agents before implementing any MMD changes;
- a gap analysis input for the next MMD backend and frontend slices;
- a truth-boundary disclosure for all SHELL and MOCK screens.

This is a read-only audit. No production source code was modified in producing this report.

---

## 2. Executive Summary

The FleziBCG frontend currently covers **9 core MMD screens** across two tiers:

**Tier 1 — Backend-Connected (PARTIAL):**  
Product List, Product Detail, Routing List, Routing Detail are connected to real backend APIs (`/v1/products`, `/v1/routings`). Data is live. Lifecycle mutation actions (create, release, retire, edit) are disabled in the UI pending MMD governance workflow implementation.

**Tier 2 — Frontend Shell (SHELL/MOCK_FIXTURE):**  
BOM List, BOM Detail, Routing Operation Detail, Resource Requirement Mapping, and Reason Code Management are UI shells using inline mock fixture data. No backend BOM API, resource requirements API, or reason code management API exists in the frontend client layer. Backend MMD system remains the source of truth for all these domains.

**One additional backend-connected service:**  
Downtime Reasons (`/v1/downtime-reasons`) is consumed by the Station Execution `StartDowntimeDialog` component. This is a live read-only API call for operational downtime coding — distinct from the Reason Code Management shell screen which covers all reason code domains.

**Key truth boundary:**  
The SHELL screens are for internal visualization and product owner review only. They must not be used as sources of released manufacturing truth. All BOM, resource, and reason-code lifecycle decisions are governed exclusively by the backend MMD system.

---

## 3. MMD Scope in FleziBCG

Manufacturing Master Data is the shared definition layer for the entire MOM platform. It defines:

| MMD Sub-Domain | Definition | Downstream Consumers |
|---|---|---|
| **Product** | Product identity, type, lifecycle status, and display metadata | Execution, Production Orders, APS, Reporting, ERP Integration |
| **BOM** | Component structure for each product version — materials, quantities, UOM, scrap factors | Material/Inventory, Backflush, Kitting, ERP BOM posting |
| **Routing** | Ordered sequence of manufacturing operations for a product or variant | Execution scheduling, Work Order creation, APS capacity load, Resource allocation |
| **Routing Operations** | Individual operation step — timing, work center, resource type, QC checkpoints | Operation execution at station, resource applicability check, QC linkage |
| **Resource Requirements** | Operation ↔ station/equipment capability and qualification mapping | Resource scheduling, Station Execution eligibility, Maintenance |
| **Reason Codes** | Reason code registry across domains (downtime, scrap, pause, reopen, quality hold) | Station Execution downtime coding, Quality events, Traceability event tagging, Reporting |

**Backend is source of truth for all of the above.** Frontend may display and navigate this data but must not make lifecycle decisions or claim released truth without backend confirmation.

---

## 4. Source Files Inspected

| File | Type | Purpose |
|---|---|---|
| `frontend/src/app/pages/ProductList.tsx` | React page | Product list screen |
| `frontend/src/app/pages/ProductDetail.tsx` | React page | Product detail screen |
| `frontend/src/app/pages/RouteList.tsx` | React page | Routing list screen |
| `frontend/src/app/pages/RouteDetail.tsx` | React page | Routing detail screen |
| `frontend/src/app/pages/BomList.tsx` | React page | BOM list shell |
| `frontend/src/app/pages/BomDetail.tsx` | React page | BOM detail shell |
| `frontend/src/app/pages/RoutingOperationDetail.tsx` | React page | Routing operation detail shell |
| `frontend/src/app/pages/ResourceRequirements.tsx` | React page | Resource requirement mapping shell |
| `frontend/src/app/pages/ReasonCodes.tsx` | React page | Reason code management shell |
| `frontend/src/app/api/productApi.ts` | API client | Backend product API (`/v1/products`) |
| `frontend/src/app/api/routingApi.ts` | API client | Backend routing API (`/v1/routings`) |
| `frontend/src/app/api/downtimeReasons.ts` | API client | Backend downtime reasons API (`/v1/downtime-reasons`) |
| `frontend/src/app/routes.tsx` | Router config | All registered routes |
| `frontend/src/app/screenStatus.ts` | Screen registry | Phase/data-source classification per route |
| `frontend/src/app/persona/personaLanding.ts` | Persona config | Menu items and route access per persona |
| `frontend/src/app/components/Layout.tsx` | Layout | Sidebar navigation and icon mapping |
| `frontend/src/app/i18n/registry/en.ts` | i18n | English string registry (1092 keys) |
| `frontend/src/app/i18n/registry/ja.ts` | i18n | Japanese string registry (1092 keys, parity maintained) |
| `frontend/src/app/i18n/namespaces.ts` | i18n | i18n namespace declarations |
| `docs/audit/frontend-coverage-mmd-report.md` | Audit | FE-COVERAGE-01B delivery report |
| `docs/audit/frontend-screen-coverage-matrix.md` | Audit | Full route/screen coverage matrix |

No BOM API client file was found under `frontend/src/app/api/`. No resource requirements API client file was found. No reason code management API client file was found. Evidence confirms all three domains are currently SHELL only.

---

## 5. Current MMD Screen Inventory

| Screen | Route | Source File | Status | Main Purpose | Data Source | Backend Connected? | Notes |
|---|---|---|---|---|---|---|---|
| Product List | `/products` | `ProductList.tsx` | **PARTIAL** | Browse real product catalog | `productApi.listProducts()` → `GET /v1/products` | ✅ Yes (read) | Create action disabled |
| Product Detail | `/products/:productId` | `ProductDetail.tsx` | **PARTIAL** | View product identity, type, lifecycle | `productApi.getProduct(id)` → `GET /v1/products/:id` | ✅ Yes (read) | Release, Retire disabled; BOM tab missing |
| Routing List | `/routes` | `RouteList.tsx` | **PARTIAL** | Browse real routing catalog with operations | `routingApi.listRoutings()` → `GET /v1/routings` | ✅ Yes (read) | Create/Export actions: Export enabled in UI but may not post |
| Routing Detail | `/routes/:routeId` | `RouteDetail.tsx` | **PARTIAL** | View routing + ordered operation sequence | `routingApi.getRouting(id)` → `GET /v1/routings/:id` | ✅ Yes (read) | Save/edit action disabled |
| BOM List | `/bom` | `BomList.tsx` | **SHELL** | Visualize BOM definitions linked to products | Inline `mockBoms` fixture (4 records) | ❌ No | Create BOM, Import BOM disabled; data is mock |
| BOM Detail | `/bom/:bomId` | `BomDetail.tsx` | **SHELL** | Visualize BOM header + component lines | Inline `mockBomHeaders` + `mockBomComponents` fixtures | ❌ No | Edit, Release, Retire, Add Component disabled |
| Routing Operation Detail | `/routes/:routeId/operations/:operationId` | `RoutingOperationDetail.tsx` | **SHELL** | Visualize single operation timing, resources, quality | Inline `mockOperations` fixture (2 records) | ❌ No | Edit, Release disabled; linked from `/routes/:routeId` |
| Resource Requirement Mapping | `/resource-requirements` | `ResourceRequirements.tsx` | **SHELL** | Visualize operation ↔ station/capability mapping | Inline `mockRequirements` fixture (4 records) | ❌ No | Assign Resource, Edit (per row) disabled |
| Reason Code Management | `/reason-codes` | `ReasonCodes.tsx` | **SHELL** | Visualize reason code registry across all domains | Inline `mockReasonCodes` fixture (8 records) | ❌ No | Create, Edit, Retire disabled; domain filter is functional |
| Downtime Reasons *(operational, not a dedicated screen)* | *(in `/station` — dialog)* | `downtimeReasons.ts` + `StartDowntimeDialog.tsx` | **CONNECTED** | Provide live downtime reason codes during station execution | `fetchDowntimeReasons()` → `GET /v1/downtime-reasons` | ✅ Yes (read) | This is a station-execution operational call, not an MMD management screen |

---

## 6. Screen-by-Screen Explanation

---

### Product List

**Route:** `/products`  
**Source file:** `frontend/src/app/pages/ProductList.tsx`  
**Current status:** PARTIAL  
**What this screen is for:**  
Provides a browsable catalog of all products registered in the FleziBCG system. Allows operators, supervisors, IE engineers, and planners to see which products exist, their product codes, types, and lifecycle statuses (DRAFT / RELEASED / RETIRED). This is the entry point into the product master data hierarchy.

**What it currently does:**  
- Calls `productApi.listProducts()` → `GET /v1/products` on mount with AbortController lifecycle
- Renders a live table with real product data from the backend
- Displays `ProductLifecycleBadge` per row (product status visual indicator)
- Handles 401/403/load errors with localized error messages and retry
- Shows `BackendRequiredNotice` (blue info box)
- Has a disabled "Create Product" button (cursor-not-allowed)
- Row click navigates to `/products/:productId`
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No product search or filter (field exists in i18n but may not be fully wired)
- No product creation, edit, or lifecycle mutation (backend governance workflow required)
- No BOM linkage from product list

**Main user/persona:** IEP (IE Engineer), SUP (Supervisor), PMG (Plant Manager), QC, ADM  
**Backend dependency:** `GET /v1/products` — EXISTS and connected  
**Recommended next step:** Add client-side search/filter by product code, name, type. Low risk; no backend change needed.

---

### Product Detail

**Route:** `/products/:productId`  
**Source file:** `frontend/src/app/pages/ProductDetail.tsx`  
**Current status:** PARTIAL  
**What this screen is for:**  
Shows full detail for a single product: identity fields (product_id, product_code, product_name), type, lifecycle status, description, and timestamps. It is the canonical product view for product owners reviewing master data. Intended to eventually host BOM linkage tabs.

**What it currently does:**  
- Calls `productApi.getProduct(productId)` → `GET /v1/products/:id` on mount
- Handles 404 not found, 401/403, missing productId, and load error states
- Renders product identity section with `ProductLifecycleBadge`, `ProductTypeBadge`, `ScreenStatusBadge` (PARTIAL phase)
- Shows disabled Release and Retire action buttons
- Shows `BackendRequiredNotice` for lifecycle actions
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No BOM tab — BOM data for this product is not linked (BOM screen is separate shell at `/bom`)
- No routing linkage from this view
- No lifecycle mutation (Release/Retire require backend MMD governance workflow)
- No product edit form

**Main user/persona:** IEP, PMG, ADM  
**Backend dependency:** `GET /v1/products/:id` — EXISTS and connected  
**Recommended next step:** MMD-FE-02A — Once BOM backend API is available, add BOM tab to ProductDetail showing components for this product's released BOM.

---

### Routing List

**Route:** `/routes`  
**Source file:** `frontend/src/app/pages/RouteList.tsx`  
**Current status:** PARTIAL  
**What this screen is for:**  
Provides a browsable catalog of all manufacturing routings. A routing is a named sequence of manufacturing operations associated with a product. Supervisors and IE engineers use this to confirm which process flow a production order will follow.

**What it currently does:**  
- Calls `routingApi.listRoutings()` → `GET /v1/routings` on mount
- Renders a live table of real routings: routing_code, routing_name, product linkage, lifecycle_status, operations count
- Client-side search by routing code or name (functional, no backend call)
- Displays `RoutingLifecycleBadge` per row
- Export button rendered (present in UI but not confirmed to post to backend)
- Handles 401/403/load errors with retry
- Row click navigates to `/routes/:routeId`
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No routing creation, edit, or lifecycle mutation
- Export button presence in UI — status is **not confirmed as a backend call** in source inspection; it may be cosmetic

**Main user/persona:** IEP, SUP, PMG, QC, ADM  
**Backend dependency:** `GET /v1/routings` — EXISTS and connected  
**Recommended next step:** Verify export button backend integration. Low priority for now.

---

### Routing Detail

**Route:** `/routes/:routeId`  
**Source file:** `frontend/src/app/pages/RouteDetail.tsx`  
**Current status:** PARTIAL  
**What this screen is for:**  
Shows full detail for a single routing: routing code, name, product linkage, lifecycle status, and the complete ordered operation sequence. This is the canonical view for IE engineers and planners reviewing how a product is manufactured step by step.

**What it currently does:**  
- Calls `routingApi.getRouting(routeId)` → `GET /v1/routings/:id` on mount
- Returns routing header + `operations[]` array (sorted by sequence_no)
- Displays `RoutingLifecycleBadge` for routing status
- Displays `RoutingOperationSequenceBadge` for each operation in sequence
- Shows operation code, name, sequence, standard_cycle_time, required_resource_type per row
- Handles 404, 401/403, missing routeId, and load errors
- Save/edit action button disabled
- i18n-enabled (en + ja)
- Each operation row can link to `/routes/:routeId/operations/:operationId` (via `RoutingOperationDetail`)

**What it does not do yet:**  
- No routing lifecycle mutation (edit, release, retire)
- Operations shown as a list; deep-dive into timing/resource/quality for each operation requires navigation to `RoutingOperationDetail` shell
- No BOM-routing cross-reference view

**Main user/persona:** IEP, SUP, PMG, ADM  
**Backend dependency:** `GET /v1/routings/:id` — EXISTS and connected  
**Recommended next step:** MMD-FE-02A — Polish operation row linking to `RoutingOperationDetail`. Once backend exposes per-operation endpoints, this becomes CONNECTED.

---

### BOM List

**Route:** `/bom`  
**Source file:** `frontend/src/app/pages/BomList.tsx`  
**Current status:** SHELL  
**What this screen is for:**  
Provides a central view of all Bill of Materials definitions. Each BOM links a product to its component structure: what materials, sub-assemblies, and purchased parts are needed to manufacture that product. Product owners, IE engineers, and planners use this screen to review which BOMs exist, their versions, and whether they have been released.

**What it currently does:**  
- Renders a table of 4 mock BOM records (BOM code, name, product linkage, version, status, component count, last updated)
- Client-side search by BOM code, name, or product code (functional filter on mock data)
- Status badges (RELEASED / DRAFT / RETIRED) with color coding
- Row link to `/bom/:bomId` (BOM Detail)
- Disabled: Create BOM button, Import BOM button (Lock icon + cursor-not-allowed)
- `MockWarningBanner` (SHELL phase) visible
- `ScreenStatusBadge` (SHELL) visible
- `BackendRequiredNotice` visible
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No real API call — no BOM API client exists (`frontend/src/app/api/` has no BOM file)
- No BOM creation, import, versioning, release, retire
- Mock data has no relationship to real products in the backend

**Main user/persona:** IEP, SUP, PMG, ADM  
**Backend dependency:** BOM API (`GET /v1/boms`, `GET /v1/boms/:id`) — **DOES NOT EXIST in frontend API client layer**. Requires backend BOM domain implementation + frontend API client before this can be connected.  
**Recommended next step:** MMD-BE-01 — Implement backend BOM read model and `/v1/boms` endpoint. Then MMD-FE-02B to connect BOM List to real API.

---

### BOM Detail

**Route:** `/bom/:bomId`  
**Source file:** `frontend/src/app/pages/BomDetail.tsx`  
**Current status:** SHELL  
**What this screen is for:**  
Shows the full Bill of Materials for a specific BOM version: header information (BOM code, product, version, status, effective date) and the complete component line table (sequence, component code/name, quantity, UOM, scrap factor, item type). This is the key engineering record that tells manufacturing what to issue from stores for each production order.

**What it currently does:**  
- Reads `bomId` from URL params
- Looks up mock data in `mockBomHeaders` and `mockBomComponents` fixture dictionaries (keyed by bomId)
- Renders BOM header section and component table if fixture record found
- Falls back to "not found" message for unknown bomIds
- Back link to `/bom`
- Disabled: Edit BOM, Release BOM, Retire BOM, Add Component (Lock icon + cursor-not-allowed)
- `MockWarningBanner` (SHELL phase) and `ScreenStatusBadge` (SHELL) visible
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No real API call
- Cannot show real component data
- Cannot navigate between BOM versions
- No cross-reference to product detail

**Main user/persona:** IEP, PMG, ADM  
**Backend dependency:** BOM detail API (`GET /v1/boms/:id`) — **does not exist**  
**Recommended next step:** Pair with MMD-BE-01. Once backend BOM read model exists, connect to real API and integrate BOM tab into ProductDetail.

---

### Routing Operation Detail

**Route:** `/routes/:routeId/operations/:operationId`  
**Source file:** `frontend/src/app/pages/RoutingOperationDetail.tsx`  
**Current status:** SHELL  
**What this screen is for:**  
Shows full detail for a single manufacturing operation within a routing: operation code, name, routing context, sequence, work center, standard timing (cycle time, setup time, run time per unit), required resource type, required skill/level, and QC checkpoint count. IE engineers use this to review and verify operation definitions before routing is released for production use.

**What it currently does:**  
- Reads `routeId` + `operationId` from URL params
- Looks up mock data in `mockOperations` fixture (2 records)
- Renders identity section, timing panel, resources section, quality section, and description
- Uses `RoutingLifecycleBadge` and `RoutingOperationSequenceBadge` (shared components with real routing screens)
- Back link navigates to `/routes/:routeId`
- Disabled: Edit Operation, Release (Lock icon + cursor-not-allowed)
- `MockWarningBanner` (SHELL phase) and `ScreenStatusBadge` (SHELL) visible
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No real API call — the routing API returns operations as nested items within `RoutingItemFromAPI` but does NOT have a dedicated per-operation endpoint
- Cannot render real operation data from backend
- Backend `RoutingOperationItemFromAPI` (from routingApi.ts) lacks: setup_time, run_time_per_unit, work_center, required_skill, required_skill_level, qc_checkpoint_count — these fields exist only in mock fixture
- No real linkage from RouteDetail row to this screen yet

**Main user/persona:** IEP, ADM  
**Backend dependency:** Per-operation detail API (`GET /v1/routings/:routeId/operations/:operationId` or extended routing response) — **partially exists** (operations are returned within routing, but detail fields are not exposed)  
**Recommended next step:** MMD-BE-02 — Extend routing API to expose richer operation-level fields (setup_time, work_center, etc.). Then connect RoutingOperationDetail to real routing data. Low risk: extend existing PARTIAL screen.

---

### Resource Requirement Mapping

**Route:** `/resource-requirements`  
**Source file:** `frontend/src/app/pages/ResourceRequirements.tsx`  
**Current status:** SHELL  
**What this screen is for:**  
Provides a cross-reference view showing which operations require which stations/equipment, with what capability, qualification level, and setup constraints. This is essential for production schedulers and IE engineers to verify that station capabilities match the operations being planned. It is the master definition used by the Station Execution eligibility check — an operator can only claim an operation at a station if the station has the required resource type registered.

**What it currently does:**  
- Renders a table of 4 mock resource requirement records
- Shows operation → station/equipment → capability → qualification → setup constraint → status
- Domain-specific type badge (e.g., CNC_LATHE, CYLINDRICAL_GRINDER, OUTSOURCE)
- Disabled: Assign Resource button, Edit per row (Lock icon + cursor-not-allowed)
- Scope explanation notice (blue info box)
- `MockWarningBanner` (SHELL phase) and `ScreenStatusBadge` (SHELL) visible
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No real API call — no resource requirements API client exists
- No connection to station master data
- No connection to operation-resource applicability check used by Station Execution

**Main user/persona:** IEP, PMG, ADM  
**Backend dependency:** Resource requirements API — **does not exist in frontend API client layer**. Backend likely has station/resource configuration but is not yet exposed for MMD management.  
**Recommended next step:** MMD-BE-03 — Define and expose resource requirement read model from backend. High business value: directly enables correct station assignment in execution.

---

### Reason Code Management

**Route:** `/reason-codes`  
**Source file:** `frontend/src/app/pages/ReasonCodes.tsx`  
**Current status:** SHELL  
**What this screen is for:**  
Provides a registry view of all reason codes across all operational domains: downtime, scrap, pause, reopen, and quality hold. Reason codes are the controlled vocabulary that operators must select when recording non-standard events during production. A centralized reason code screen allows product owners and plant managers to review the configured reason vocabulary, understand which domains each code applies to, and verify that all codes requiring supervisor review or comment are correctly configured.

This screen is distinct from the operational downtime reason dropdown in `StartDowntimeDialog.tsx`, which reads live from `/v1/downtime-reasons` and covers only the downtime domain.

**What it currently does:**  
- Renders a table of 8 mock reason code records across 5 domains
- Domain filter dropdown (functional state filter — downtime / scrap / pause / reopen / qualityHold / All)
- Text search by code, category, or description (functional filter on mock data)
- Color-coded domain badges per row
- `requires_comment` visual indicator (amber dot = required, gray = optional)
- Disabled: Create Reason Code, Edit (per row), Retire (per row)
- `MockWarningBanner` (SHELL phase) and `ScreenStatusBadge` (SHELL) visible
- i18n-enabled (en + ja)

**What it does not do yet:**  
- No real API call — no reason code management API client exists
- Covers all 5 domains in mock data; operational system only has downtime reasons connected
- No reason code creation, update, or lifecycle management
- Mock data has no relationship to the live downtime reason codes served by `/v1/downtime-reasons`

**Important note on the live downtime reason data:**  
`frontend/src/app/api/downtimeReasons.ts` exports `fetchDowntimeReasons()` → `GET /v1/downtime-reasons`. This is used in `StartDowntimeDialog.tsx` within Station Execution. It is a **live backend call** returning `DowntimeReasonOption[]` with fields: `reason_code`, `reason_name`, `reason_group`, `planned_flag`, `requires_comment`, `requires_supervisor_review`. This is operationally active and must not be disrupted. It serves only the downtime domain, not the full reason code registry.

**Main user/persona:** IEP, SUP, PMG, ADM  
**Backend dependency:** Reason code management API — **does not exist in frontend API client layer** (only downtime-specific endpoint exists)  
**Recommended next step:** MMD-BE-04 — Implement reason code read model and management API across all domains. Then connect ReasonCodes screen.

---

## 7. Route / Navigation Coverage

### Routes Registered (`routes.tsx`)

All 9 MMD routes are registered in `createBrowserRouter`:

| Route | Component | Status |
|---|---|---|
| `products` | `ProductList` | Active |
| `products/:productId` | `ProductDetail` | Active |
| `routes` | `RouteList` | Active |
| `routes/:routeId` | `RouteDetail` | Active |
| `routes/:routeId/operations/:operationId` | `RoutingOperationDetail` | Active (SHELL) |
| `bom` | `BomList` | Active (SHELL) |
| `bom/:bomId` | `BomDetail` | Active (SHELL) |
| `resource-requirements` | `ResourceRequirements` | Active (SHELL) |
| `reason-codes` | `ReasonCodes` | Active (SHELL) |

### Persona Menu Visibility (`personaLanding.ts`)

| Screen | OPR | SUP | IEP | QC | PMG | ADM |
|---|---|---|---|---|---|---|
| Products | — | ✅ | ✅ | ✅ | ✅ | — |
| Routes | — | ✅ | ✅ | ✅ | ✅ | — |
| BOM | — | ✅ | ✅ | — | ✅ | — |
| Resource Requirements | — | — | ✅ | — | ✅ | — |
| Reason Codes | — | ✅ | ✅ | — | ✅ | — |

ADM has access to all routes via the `isRouteAllowedForPersona` guard (ADM is included in MMD route guards). ADM menu focuses on governance screens; MMD screens are accessible to ADM but not shown as primary menu items.

### Icon Mapping (`Layout.tsx`)

| Route prefix | Icon | Import status |
|---|---|---|
| `/products` | `Package` | ✅ Imported |
| `/routes` | `GitBranch` | ✅ Imported |
| `/bom` | `FileText` | ✅ Imported |
| `/resource-requirements` | `Server` | ✅ Imported |
| `/reason-codes` | `Tag` | ✅ Imported |

---

## 8. Data Source / Backend Connectivity

### Connected API Clients

| API Client | File | Endpoint | Used By | Status |
|---|---|---|---|---|
| `productApi.listProducts()` | `productApi.ts` | `GET /v1/products` | ProductList | ✅ CONNECTED |
| `productApi.getProduct(id)` | `productApi.ts` | `GET /v1/products/:id` | ProductDetail | ✅ CONNECTED |
| `routingApi.listRoutings()` | `routingApi.ts` | `GET /v1/routings` | RouteList | ✅ CONNECTED |
| `routingApi.getRouting(id)` | `routingApi.ts` | `GET /v1/routings/:id` | RouteDetail | ✅ CONNECTED |
| `fetchDowntimeReasons()` | `downtimeReasons.ts` | `GET /v1/downtime-reasons` | StartDowntimeDialog (operational) | ✅ CONNECTED |

### Missing API Clients (no file in `frontend/src/app/api/`)

| Domain | Required Endpoint | Missing API Client | Impact |
|---|---|---|---|
| BOM | `GET /v1/boms`, `GET /v1/boms/:id` | `bomApi.ts` — does not exist | BomList + BomDetail remain SHELL |
| Routing Operations (per-op) | `GET /v1/routings/:id/operations/:opId` (extended fields) | Not in `routingApi.ts` | RoutingOperationDetail remains SHELL |
| Resource Requirements | `GET /v1/resource-requirements` | `resourceRequirementsApi.ts` — does not exist | ResourceRequirements remains SHELL |
| Reason Code Management | `GET /v1/reason-codes` | `reasonCodesApi.ts` — does not exist | ReasonCodes screen remains SHELL |

### Backend API Contract Quality (Connected Screens)

**`ProductItemFromAPI`** (from `productApi.ts`):  
`product_id`, `tenant_id`, `product_code`, `product_name`, `product_type`, `lifecycle_status`, `description`, `display_metadata`, `created_at`, `updated_at` — all fields present and used.

**`RoutingItemFromAPI`** (from `routingApi.ts`):  
`routing_id`, `tenant_id`, `product_id`, `routing_code`, `routing_name`, `lifecycle_status`, `operations[]`, `created_at` — all used.

**`RoutingOperationItemFromAPI`** (from `routingApi.ts`, nested in routing response):  
`operation_id`, `routing_id`, `operation_code`, `operation_name`, `sequence_no`, `standard_cycle_time`, `required_resource_type`, `created_at`, `updated_at` — NOTE: `setup_time`, `run_time_per_unit`, `work_center`, `required_skill`, `required_skill_level`, `qc_checkpoint_count` are **NOT present** in the API contract. These exist only in mock fixture.

---

## 9. Current Actions and Disabled Future Actions

| Screen | Action | Current Treatment | Real Backend Needed? | Notes |
|---|---|---|---|---|
| Product List | View product | ✅ Active — navigates to `/products/:productId` | No | Working |
| Product List | Create Product | ❌ Disabled — `cursor-not-allowed`, locked button | Yes — product creation API + governance | FE-4A decision; awaits MMD governance workflow |
| Product Detail | View product fields | ✅ Active — reads from backend | No | Working |
| Product Detail | Release Product | ❌ Disabled — locked button | Yes — lifecycle mutation endpoint | Backend lifecycle governance required |
| Product Detail | Retire Product | ❌ Disabled — locked button | Yes — lifecycle mutation endpoint | Backend lifecycle governance required |
| Product Detail | Edit Product | ❌ Disabled — no edit button present | Yes — product update endpoint | Not yet exposed |
| Routing List | View routing | ✅ Active — navigates to `/routes/:routeId` | No | Working |
| Routing List | Search routings | ✅ Active — client-side filter on real data | No | Working |
| Routing List | Export | ⚠️ Present in UI — not confirmed as backend call | Possibly | Verify export endpoint before marking CONNECTED |
| Routing List | Create Routing | ❌ Not present | Yes | Not built yet |
| Routing Detail | View routing + operations | ✅ Active — reads from backend | No | Working |
| Routing Detail | Save/Edit routing | ❌ Disabled — locked button | Yes — routing update endpoint | Backend lifecycle governance required |
| BOM List | View BOM list | ✅ Active — mock fixture only | — | Shell: mock data only |
| BOM List | Search BOMs | ✅ Active — client-side filter on mock data | — | Functional filter on mock |
| BOM List | View BOM detail | ✅ Active — navigates to `/bom/:bomId` | — | Links to BOM detail shell |
| BOM List | Create BOM | ❌ Disabled — Lock + `cursor-not-allowed` | Yes — BOM creation API | Backend BOM domain + governance required |
| BOM List | Import BOM | ❌ Disabled — Lock + `cursor-not-allowed` | Yes — BOM import API | Backend BOM domain + governance required |
| BOM Detail | View BOM header | ✅ Active — mock fixture only | — | Shell: mock data only |
| BOM Detail | View component lines | ✅ Active — mock fixture only | — | Shell: mock data only |
| BOM Detail | Edit BOM | ❌ Disabled | Yes — BOM update endpoint | Backend BOM governance required |
| BOM Detail | Release BOM | ❌ Disabled | Yes — BOM lifecycle endpoint | Backend BOM governance required |
| BOM Detail | Retire BOM | ❌ Disabled | Yes — BOM lifecycle endpoint | Backend BOM governance required |
| BOM Detail | Add Component | ❌ Disabled | Yes — BOM component API | Backend BOM governance required |
| Routing Op Detail | View operation fields | ✅ Active — mock fixture only | — | Shell: mock data only |
| Routing Op Detail | Edit Operation | ❌ Disabled | Yes — operation update endpoint + extended routing API | Backend required |
| Routing Op Detail | Release | ❌ Disabled | Yes — lifecycle endpoint | Backend required |
| Resource Requirements | View mapping table | ✅ Active — mock fixture only | — | Shell: mock data only |
| Resource Requirements | Assign Resource | ❌ Disabled | Yes — resource assignment API | Backend required |
| Resource Requirements | Edit (per row) | ❌ Disabled | Yes — resource update API | Backend required |
| Reason Codes | View reason code table | ✅ Active — mock fixture only | — | Shell: mock data only |
| Reason Codes | Search codes | ✅ Active — client-side filter on mock data | — | Functional filter on mock |
| Reason Codes | Domain filter | ✅ Active — client-side filter on mock data | — | Functional filter on mock |
| Reason Codes | Create Reason Code | ❌ Disabled | Yes — reason code creation API | Backend required |
| Reason Codes | Edit (per row) | ❌ Disabled | Yes — reason code update API | Backend required |
| Reason Codes | Retire (per row) | ❌ Disabled | Yes — reason code lifecycle API | Backend required |

---

## 10. Product / MOM Meaning of Each Screen

| Screen | MOM Meaning | Downstream Consumers | Why It Matters |
|---|---|---|---|
| Product List | The authoritative catalog of manufacturable products. Every Production Order must reference a valid, released product. | Production Orders, Work Orders, APS, ERP posting, Traceability | Without product catalog, PO creation has no valid target |
| Product Detail | Full product specification: type (discrete/batch/continuous), lifecycle status, display configuration. Determines what manufacturing mode applies. | Work Order creation, routing lookup, BOM lookup, ERP item master | Product type controls which execution model is used |
| Routing List | The catalog of all available process flows for manufacturing products. Each routing is a named ordered operation sequence. | Work Order routing selection, APS scheduling, Resource planning, OEE reporting | Routing selection determines which stations, resources, and cycle times apply to a production run |
| Routing Detail | The complete process definition: which operations in which sequence, with what resource type and cycle time targets. | Station Execution eligibility, APS capacity load, Work center loading, OEE target setting | Operation sequence defines execution topology; standard_cycle_time is the benchmark for OEE |
| BOM List | Registry of all Bill of Materials definitions linked to products, with versioning and lifecycle status. | Material issuance, Kitting, Backflush, ERP BOM posting, Material variance reporting | Without released BOM, material consumption cannot be planned or verified |
| BOM Detail | Component-level manufacturing recipe: what materials in what quantities with what scrap allowances. | Material requirements calculation, Component issuance at station, WIP inventory moves, ERP backflush | BOM components define the material truth for each production event |
| Routing Operation Detail | Per-operation engineering definition: work center, timing standards, resource type, skill requirements, QC checkpoint linkage. | Station assignment eligibility (resource type match), Operator skill check, QC checkpoint activation, Time standard for OEE | Operation detail is the contract between MMD and the execution system for how an operation must be performed |
| Resource Requirement Mapping | Cross-reference of operation ↔ station capability ↔ qualification. Defines which stations can run which operations. | Station Execution eligibility validation, Maintenance planning, Resource scheduling | Without resource requirements, station assignment is based only on physical location, not capability |
| Reason Code Management | The controlled vocabulary registry for non-standard operational events across all domains. | Downtime recording (StationExecution), Scrap declaration, Quality hold activation, Reopen justification, Traceability event tagging, OEE reporting | Reason codes enable structured root-cause analysis; without them, reporting is uncategorized text |

---

## 11. Current Gaps

| Gap ID | Gap | Impact | Recommended Slice |
|---|---|---|---|
| GAP-MMD-01 | No BOM backend API or frontend client — BomList + BomDetail are SHELL only | Cannot plan or verify material requirements for production | MMD-BE-01 (BOM read model + API), then MMD-FE-02B (connect BOM screens) |
| GAP-MMD-02 | Routing operation detail API fields are incomplete — `setup_time`, `work_center`, `required_skill`, etc. not in `RoutingOperationItemFromAPI` | RoutingOperationDetail cannot show real data; engineers see mock only | MMD-BE-02 (extend routing operation API response), then update RoutingOperationDetail |
| GAP-MMD-03 | No resource requirements backend API or frontend client — ResourceRequirements screen is SHELL only | Station assignment eligibility cannot be verified from UI; risk of wrong station assignments | MMD-BE-03 (resource requirement read model), then MMD-FE-02C (connect screen) |
| GAP-MMD-04 | No reason code management API — ReasonCodes screen is SHELL only; only downtime domain is live | No unified reason code registry visible; users cannot verify codes across all domains | MMD-BE-04 (reason code management API), then connect ReasonCodes screen |
| GAP-MMD-05 | Product lifecycle mutations (create, release, retire, edit) are disabled | Product owners cannot perform MMD lifecycle governance through FE | Backend product lifecycle governance workflow (engineering/approval workflow required) |
| GAP-MMD-06 | Routing lifecycle mutations (create, release, retire, edit) are disabled | IE engineers cannot maintain routing definitions through FE | Backend routing lifecycle governance workflow required |
| GAP-MMD-07 | BOM Detail is disconnected from Product Detail — product and BOM screens are standalone, not cross-linked | Product owners must navigate separately; no unified product → BOM view | MMD-FE-02A: add BOM tab to ProductDetail once BOM API exists |
| GAP-MMD-08 | Routing Operation Detail is not linked from RouteDetail operation rows | IE engineers cannot drill down from routing to per-operation detail | MMD-FE-02A: wire operation row click in RouteDetail to RoutingOperationDetail once operation API is extended |
| GAP-MMD-09 | RoutingOperationDetail has no live operation data — backend `RoutingOperationItemFromAPI` lacks timing and work center fields | Engineers see mock-only operation definitions; cannot verify standard cycle times against backend | MMD-BE-02: extend routing API to include richer operation fields |
| GAP-MMD-10 | Live downtime reasons (`/v1/downtime-reasons`) cover only downtime domain — no coverage of scrap, pause, reopen, quality hold in FE at all | Operators recording non-downtime events have no validated reason code selection | MMD-BE-04: extend reason code API to all domains, then connect ReasonCodes and extend event recording dialogs |

---

## 12. Risks / Truth-Boundary Notes

### SHELL screens must not be treated as released manufacturing truth

The following screens display mock fixture data that has **no relationship to real backend records**:

| Screen | Risk | Mitigation in place |
|---|---|---|
| BOM List | 4 mock BOMs shown; not real backend BOMs | `MockWarningBanner` + `ScreenStatusBadge(SHELL)` + `BackendRequiredNotice` |
| BOM Detail | Mock components shown; not real backend BOM components | Same disclosure components; disabled actions |
| Routing Operation Detail | 2 mock operations shown; real operations are in routingApi but with fewer fields | Same disclosure components; linked from RouteDetail context |
| Resource Requirements | 4 mock resource mappings; no real backend resource requirements | Same disclosure components |
| Reason Codes | 8 mock reason codes; only downtime codes are actually live | Same disclosure components |

### Live downtime codes must not be disrupted

`fetchDowntimeReasons()` → `GET /v1/downtime-reasons` is operationally active and consumed by Station Execution. Any future work on the Reason Code Management screen **must not modify or shadow this API call**. The Reason Code Management shell at `/reason-codes` is completely independent of this live API.

### PARTIAL screens have real data — lifecycle mutations are correctly disabled

Product and Routing screens read real backend data. Lifecycle mutations (create, release, retire, edit) are disabled by design — not a bug. These require backend governance workflow implementation before they can be enabled. The disabled buttons reflect correct product governance boundary enforcement.

### No mock data in execution-critical paths

Mock fixture data exists only in BOM, RoutingOpDetail, ResourceRequirements, and ReasonCodes pages. No mock data is present in the connected product/routing API paths. Station Execution, Operation Execution, Work Orders, and Production Orders all use real backend APIs.

---

## 13. Recommended Next MMD Slices

### Frontend Polish (Low Risk, Based on Existing Backend)

**MMD-FE-02A — Product + Routing Connected Screen Polish**  
- Wire operation row click in RouteDetail to RoutingOperationDetail (requires URL construction: `/routes/:routeId/operations/:operationId`)
- Add product search/filter client-side to ProductList if not already fully wired
- Verify Routing List export button — either remove it or connect to a real export endpoint
- Risk: LOW — no backend change; uses existing connected screens

**MMD-FE-02B — BOM Shell UX Polish**  
- Polish BOM List and BOM Detail shell visuals and user guidance
- Add explicit "backend not available" state for production use
- Risk: LOW — documentation/disclosure changes only; no source code changes needed for shell improvement

**MMD-FE-02C — Reason Code Governance Shell Polish**  
- Extend Reason Code shell to show governance metadata (requires_supervisor_review, reason_group) once backend fields are confirmed
- Risk: LOW — cosmetic only

### Backend First (Must Precede Frontend Connection)

**MMD-BE-01 — BOM Backend Contract + Read Model Foundation**  
- Implement BOM domain backend: product_id → BOM → components read model
- Expose `GET /v1/boms` (list) and `GET /v1/boms/:id` (detail with components)
- Required before BomList and BomDetail can be connected
- Impact: HIGH — unlocks material planning, backflush, ERP posting

**MMD-BE-02 — Routing Operation Detail API Extension**  
- Extend routing API to return richer operation-level fields: `setup_time`, `run_time_per_unit`, `work_center`, `required_skill`, `required_skill_level`, `qc_checkpoint_count`
- Could be a separate endpoint `GET /v1/routings/:id/operations/:opId` or extended nested response
- Required before RoutingOperationDetail can show real data
- Impact: MEDIUM — directly enables IE engineers to verify operation definitions against backend truth

**MMD-BE-03 — Resource Requirement Read Model**  
- Define resource requirement domain: operation → station/equipment capability mapping
- Expose `GET /v1/resource-requirements` (with routing/operation filter)
- Required before ResourceRequirements screen can be connected
- Impact: HIGH — directly enables correct station assignment validation in execution

**MMD-BE-04 — Reason Code Management API Foundation**  
- Extend reason code domain to cover all domains: downtime, scrap, pause, reopen, quality hold
- Expose unified `GET /v1/reason-codes` with domain filter
- Maintain backward compatibility with `/v1/downtime-reasons` (operationally active)
- Required before ReasonCodes screen can be connected
- Impact: HIGH — enables structured root-cause analysis across all operational events

### Connected Screen Extensions (After Backend Slices)

**MMD-FE-03A — BOM List + Detail Backend Connection**  
- Create `frontend/src/app/api/bomApi.ts` 
- Connect BomList to `bomApi.listBoms()`
- Connect BomDetail to `bomApi.getBom(bomId)`
- Add BOM tab to ProductDetail
- Prerequisites: MMD-BE-01 complete

**MMD-FE-03B — Routing Operation Detail Backend Connection**  
- Update `routingApi.ts` or create per-operation API client
- Connect RoutingOperationDetail to real operation data
- Wire RouteDetail operation rows to RoutingOperationDetail
- Prerequisites: MMD-BE-02 complete

**MMD-FE-03C — Resource Requirements Backend Connection**  
- Create `frontend/src/app/api/resourceRequirementsApi.ts`
- Connect ResourceRequirements screen to real data
- Prerequisites: MMD-BE-03 complete

**MMD-FE-03D — Reason Code Management Backend Connection**  
- Create `frontend/src/app/api/reasonCodesApi.ts`
- Connect ReasonCodes screen to real data
- Extend event recording dialogs for non-downtime domains
- Prerequisites: MMD-BE-04 complete

---

## 14. Final Verdict

### MMD Frontend Coverage: ADEQUATE FOR VISUALIZATION, NOT YET ADEQUATE FOR MMD GOVERNANCE

| Criterion | Status | Evidence |
|---|---|---|
| Product catalog browsing | ✅ CONNECTED | Real API; live product data |
| Routing catalog browsing | ✅ CONNECTED | Real API; live routing + operations data |
| BOM visualization | ⚠️ SHELL ONLY | Mock fixture; no backend BOM API |
| Routing operation detail | ⚠️ SHELL ONLY | Mock fixture; routing API lacks operation detail fields |
| Resource requirement mapping | ⚠️ SHELL ONLY | Mock fixture; no backend resource API |
| Reason code registry | ⚠️ SHELL ONLY | Mock fixture; only downtime domain is live (operational path) |
| Lifecycle actions (create/release/retire/edit) | ❌ ALL DISABLED | Correctly disabled; backend governance workflow required |
| Truth-boundary disclosure | ✅ CORRECT | MockWarningBanner + ScreenStatusBadge + BackendRequiredNotice on all shell screens |
| i18n parity (en/ja) | ✅ VERIFIED | 1092 keys, synchronized |
| Build/lint health | ✅ PASSING | Build ✅, lint ✅, routes 0 FAIL, i18n PASS |

### Connected vs Shell Summary

| Category | Screens | Status |
|---|---|---|
| Backend-connected MMD screens | Product List, Product Detail, Routing List, Routing Detail | **PARTIAL** (read-only; mutations disabled) |
| Shell MMD screens | BOM List, BOM Detail, Routing Op Detail, Resource Requirements, Reason Codes | **SHELL** (mock fixture; no backend API) |
| Operationally connected (not a dedicated screen) | Downtime Reasons (in StartDowntimeDialog) | **CONNECTED** (live; must not be disrupted) |

### Product / MOM Meaning Summary

The 4 connected MMD screens (Product + Routing) provide the foundational product and process definition layer that currently supports Production Order creation, Work Order routing, Operation Execution, OEE benchmarking, and Station Execution. The 5 shell screens (BOM + Routing Op Detail + Resource Requirements + Reason Codes) represent the next MMD investment layer — they cover the material definition, operation detail, resource applicability, and reason code governance domains that must be built on the backend before they can become operational MOM truth.

### Priority Signal

The single highest-value next investment in MMD is **MMD-BE-01 (BOM backend)** — it unblocks material requirements planning, backflush, ERP BOM posting, and kitting. The second highest-value investment is **MMD-BE-03 (Resource Requirements)** — it enables correct station assignment validation, which directly improves production reliability in Station Execution.

---

## Appendix: Verification Commands Run

All verification commands were run successfully on 2026-05-01:

```
cd G:\Work\FleziBCG\frontend

npm.cmd run build
→ ✅ PASS — built in 8.74s (chunk size warning is pre-existing; not an error)

npm.cmd run lint
→ ✅ PASS — no lint errors

npm.cmd run check:routes
→ ✅ PASS — FAIL: 0

npm.cmd run lint:i18n:registry
→ ✅ PASS — en.ts and ja.ts are key-synchronized (1092 keys)
```

## Appendix: Git Status Summary

Pre-existing modified files (not from this reporting task):
- `backend/app/schemas/station.py`, `backend/app/services/station_claim_service.py` — backend changes (pre-existing)
- `backend/tests/test_*.py` — backend test modifications (pre-existing)
- `docs/audit/station-execution-responsive-qa/*.png` — QA screenshots (pre-existing)
- `docs/implementation/*.md` — implementation docs (pre-existing)
- `frontend/src/app/i18n/namespaces.ts` — modified during FE-COVERAGE-01B (MMD i18n namespaces)
- `frontend/tsconfig.json` — pre-existing modification

Untracked files: `CLAUDE.md`, `backend/tests/test_station_queue_session_aware_migration.py`, various `docs/implementation/` and `docs/proposals/` files, `fullsuite_p0c08_review.txt`

No source code was modified in producing this report.

---

**End of Manufacturing Master Data Current-State Report**
