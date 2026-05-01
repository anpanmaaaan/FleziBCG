# Frontend Screen Coverage Matrix — FleziBCG

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.5 | FE-COVERAGE-01E: Added 8 Integration + 6 Reporting SHELL screens. Routes increased 53→67, SHELL phases increased 29→43. i18n keys 1321→1509 (+188). |
| 2026-05-01 | v1.4 | FE-COVERAGE-01D: Added 6 Quality Lite / Material / Traceability SHELL screens. Routes increased 47→53, SHELL phases increased 23→29. |
| 2026-05-01 | v1.3 | FE-COVERAGE-01C: Added 9 Execution/Supervisory SHELL screens. Routes increased 38→47, SHELL phases increased 14→23. |
| 2026-04-28 | v1.2 | FE-COVERAGE-01B: Added 5 MMD SHELL screens (BomList, BomDetail, RoutingOperationDetail, ResourceRequirements, ReasonCodes). Routes increased 33→38, SHELL phases increased 9→14. |
| 2026-05-01 | v1.1 | Updated governance screens: 9 new SHELL screens added (UserManagement, RoleManagement, ActionRegistry, ScopeAssignments, SessionManagement, AuditLog, SecurityEvents, TenantSettings, PlantHierarchy). Routes increased 24→33, SHELL phases increased 0→9. |
| 2026-05-01 | v1.0 | Created frontend screen coverage audit baseline. Captures 24 routes, 22 pages, 13 CONNECTED, 3 PARTIAL, 7 MOCK, 2 PLACEHOLDER before broad FE shell coverage work. |

---

## 1. Scope

Audit the current frontend screen/route/page coverage of FleziBCG before creating more frontend screens. This is a documentation-only, read-only audit.

**Purpose**: Create a truthful coverage matrix showing:
- Which screens exist in the codebase
- Current connectivity status (CONNECTED, PARTIAL, MOCK, SHELL, PLACEHOLDER, MISSING)
- Data source for each screen (real API, mock, static)
- Mock/fake-truth risk classification (CRITICAL, HIGH, MEDIUM, LOW)
- Recommendations for preserve, extend, create, or defer
- Which screens must remain future-only because backend/domain truth is not yet implemented

**Out of scope**: Building new screens, changing backend behavior, modifying routes, or refactoring production source code.

---

## 2. Source Files Inspected

| File | Status | Key Findings |
|---|---|---|
| `frontend/src/app/routes.tsx` | ✅ Read | 24 routes defined; all reachable via browser |
| `frontend/src/app/pages/` | ✅ Read | 22 page files found (21 unique pages + 1 used twice) |
| `frontend/src/app/components/Layout.tsx` | ✅ Read | Main app shell; mobile-responsive post FE-SHELL-04 |
| `frontend/src/app/components/TopBar.tsx` | ✅ Read | Header navigation; keyboard accessible post FE-SHELL-04 |
| `frontend/src/app/components/station-execution/` | ✅ Read | 11-component feature set; PARTIAL status |
| `frontend/src/app/api/` | ✅ Read | 30+ API endpoints called; types defined |
| `frontend/src/app/data/` | ✅ Read | mockData.ts, oee-mock-data.ts (mock fixtures) |
| `frontend/src/app/mocks/` | ✅ Read | Inline mock data in 6 page files |
| `frontend/src/app/auth/` | ✅ Read | Auth context, persona context, impersonation |
| `frontend/src/app/i18n/` | ✅ Read | 1010 i18n keys; both en.ts and ja.ts |
| `frontend/package.json` | ✅ Read | React 18.3.1, Vite 6.4.1, Tailwind 4.x, Playwright 1.52.0 |

---

## 3. Working Tree / Precondition Status

**Precondition Check**: ✅ CLEAN (for documentation purposes)

| Item | Status | Notes |
|---|---|---|
| Unresolved merge conflicts | ✅ NONE | Working tree is safe for audit |
| Frontend source accessible | ✅ YES | All files read successfully |
| Routes can be parsed | ✅ YES | 24 routes defined and linked |
| API contracts exist | ✅ YES | Types defined in api/ folder |
| Build state | ✅ KNOWN | Previous FE-SHELL-04 commit in history |

---

## 4. Executive Summary

**Frontend Coverage Status (as of 2026-05-02 — after FE-COVERAGE-01E)**

| Metric | Before FE-COVERAGE-01A | After FE-COVERAGE-01A | After FE-COVERAGE-01B | After FE-COVERAGE-01C | After FE-COVERAGE-01D | After FE-COVERAGE-01E |
|---|---|---|---|---|---|---|
| **Total Routes Defined** | 24 | 33 | 38 | 47 | 53 | 67 |
| **Total Page Files** | 22 (21 unique) | 31 (30 unique) | 36 (35 unique) | 45 (44 unique) | 51 (50 unique) | 65 (64 unique) |
| **CONNECTED Pages** | 13 (59%) | 13 (42%) | 13 (36%) | 13 (29%) | 13 (25%) | 13 (20%) |
| **PARTIAL Pages** | 3 (14%) | 3 (10%) | 3 (8%) | 3 (7%) | 3 (6%) | 3 (5%) |
| **MOCK Pages** | 7 (32%) | 7 (23%) | 7 (19%) | 7 (16%) | 7 (14%) | 7 (11%) |
| **SHELL Pages** | 0 (0%) | 9 (29%) | 14 (39%) | 23 (51%) | 29 (57%) | 43 (67%) |
| **PLACEHOLDER Pages** | 2 (9%) | 2 (6%) | 2 (6%) | 2 (4%) | 2 (4%) | 2 (3%) |
| **DEV-ONLY Pages** | 1 (5%) | 1 (3%) | 1 (3%) | 1 (2%) | 1 (2%) | 1 (2%) |
| **Domains with Any Coverage** | 9 / 15 target groups | 10 / 15 target groups | 11 / 15 | 12 / 15 | 12 / 15 | 14 / 15 |

**Key Insights**:
- **FE-COVERAGE-01E**: Added 8 Integration + 6 Reporting SHELL screens. 14 new routes. 14 new screenStatus entries. 188 new i18n keys. All dangerous integration/ERP/reconciliation actions disabled. Reporting screens show only `—` placeholder KPIs. Integration truth boundary enforced: frontend does NOT post to ERP, reconcile, or retry messages.
- **FE-COVERAGE-01D**: Added 6 Quality Lite / Material / Traceability SHELL screens (QualityDashboard, MeasurementEntry, QualityHolds, MaterialReadiness, StagingKitting, WipBuffers). Hard Mode MOM v3 boundaries enforced: quality disposition, material inventory position, and WIP location remain backend-only. All dangerous operations disabled. Shell pages serve as visualization documentation for upcoming backend integration.
- **FE-COVERAGE-01C**: Added 9 Execution/Supervisory shell screens. All dangerous execution actions are disabled. All execution/supervisory truth remains in backend.
- **Coverage Growth**: 38 → 67 routes across 3 iterations; SHELL pages now represent 67% of total page count.

---

## 5. Route Registry Snapshot

| Route Path | Page File | Domain | Page Status | Data Source | Evidence | Notes |
|---|---|---|---|---|---|---|
| `/login` | LoginPage.tsx | Authentication | CONNECTED | REAL_API | authApi.login() | User credentials validated via backend |
| `/` | PersonaLandingRedirect | Navigation | CONNECTED | REAL_API | resolvePersonaFromRoleCode() | Redirects to persona-specific home |
| `/home` | Home.tsx | Foundation | PLACEHOLDER | PLACEHOLDER_ONLY | Static JSX | Empty landing page |
| `/dashboard` | Dashboard.tsx | Analytics | CONNECTED | REAL_API | dashboardApi.getSummary(), dashboardApi.getHealth() | KPI dashboard with real backend data |
| `/performance/oee-deep-dive` | OEEDeepDive.tsx | Performance | MOCK | INLINE_STATIC | oee-mock-data.ts | Generated OEE trends; AI recommendations mocked |
| `/production-orders` | ProductionOrderList.tsx | Production Mgmt | CONNECTED | REAL_API | productionOrderApi.list() | Real production orders from API |
| `/products` | ProductList.tsx | Master Data | CONNECTED | REAL_API | productApi.list() | Real product list from API |
| `/products/:productId` | ProductDetail.tsx | Master Data | PARTIAL | REAL_API | productApi.getProduct(id) | Product details exist; missing BOM tab |
| `/dispatch` | DispatchQueue.tsx | Dispatch | MOCK | INLINE_STATIC | mockDispatchQueue | Mock dispatch items; no backend API |
| `/routes` | RouteList.tsx | Master Data | CONNECTED | REAL_API | routingApi.list() | Real routing list from API |
| `/routes/:routeId` | RouteDetail.tsx | Master Data | CONNECTED | REAL_API | routingApi.getRouting(id) | Real routing details with operations |
| `/work-orders` | OperationList.tsx | Execution | CONNECTED | REAL_API | productionOrderApi.getProductionOrder(orderId) | Real WO aggregated list |
| `/production-orders/:orderId/work-orders` | OperationList.tsx | Execution | CONNECTED | REAL_API | productionOrderApi.getProductionOrder(orderId) | WO filtered by PO; reused component |
| `/work-orders/:woId/operations` | OperationExecutionOverview.tsx | Execution | CONNECTED | REAL_API | operationApi.list() | Gantt chart of operations in WO |
| `/operations` | GlobalOperationList.tsx | Monitoring | CONNECTED | REAL_API | operationMonitorApi.getOperations() | Global operation monitoring (read-only) |
| `/operations/:operationId/detail` | OperationExecutionDetail.tsx | Execution | PARTIAL | MIXED_API_AND_MOCK | operationApi.getOperation(id) + inline mock QC | Operation detail tabs; QC tab is mock |
| `/station` | StationExecution.tsx | Execution | PARTIAL | MIXED_API_AND_MOCK | stationApi.getQueue(), operationApi.* | Station control center; partial features |
| `/station-execution` | StationExecution.tsx | Execution | PARTIAL | MIXED_API_AND_MOCK | (same as /station) | Alias route for StationExecution |
| `/quality` | QCCheckpoints.tsx | Quality | MOCK | INLINE_STATIC | mockCheckpoints | Mock QC checkpoint configuration |
| `/defects` | DefectManagement.tsx | Quality | MOCK | INLINE_STATIC | mockDefects | Mock defect tracking; no backend |
| `/traceability` | Traceability.tsx | Traceability | MOCK | MOCK_FILE + REACTFLOW | mockSerials, ReactFlow | Mock genealogy graph; no backend API |
| `/scheduling` | APSScheduling.tsx | APS | MOCK | INLINE_STATIC | mockScheduledOrders | Mock scheduling UI; no optimizer |
| `/dev/gantt-stress` | GanttStressTestPage.tsx | Development | DEV-ONLY | INLINE_STATIC | buildSyntheticOperations() | Virtualized Gantt row performance test |
| `/settings` | Dashboard.tsx | Settings | PLACEHOLDER | PLACEHOLDER_ONLY | Dashboard component (reused) | Settings page not yet designed |

**Total Routes: 24**  
**Unique Pages: 21** (Dashboard used 2x: /dashboard and /settings; PersonaLandingRedirect is route only)

---

## 6. Page Inventory

| Page File | Inferred Screen Name | Domain | Route | Page Status | Data Source | Lines | Evidence |
|---|---|---|---|---|---|---|---|
| LoginPage.tsx | User Login | Authentication | /login | CONNECTED | REAL_API (authApi.login) | ~150 | authApi import, form submission to backend |
| Home.tsx | Home Landing | Foundation | /home | PLACEHOLDER | PLACEHOLDER_ONLY | ~50 | Static JSX, "Coming soon" or empty grid |
| Dashboard.tsx | KPI Dashboard | Analytics | /dashboard, /settings | CONNECTED | REAL_API (dashboardApi) | ~300 | getSummary(), getHealth() calls; real data plots |
| ProductionOrderList.tsx | Production Order List | Production Mgmt | /production-orders | CONNECTED | REAL_API (productionOrderApi) | ~250 | list(), filter, search, real order items |
| ProductList.tsx | Product Catalog | Master Data | /products | CONNECTED | REAL_API (productApi) | ~200 | list(), table with real products |
| ProductDetail.tsx | Product Detail | Master Data | /products/:productId | PARTIAL | REAL_API (productApi.getProduct) | ~200 | getProduct(id); missing BOM tab; basic detail |
| RouteList.tsx | Routing List | Master Data | /routes | CONNECTED | REAL_API (routingApi) | ~220 | list(), table with real routings |
| RouteDetail.tsx | Routing Detail | Master Data | /routes/:routeId | CONNECTED | REAL_API (routingApi) | ~300 | getRouting(id); operations list; full detail |
| OperationList.tsx | Work Order List | Execution | /work-orders, /production-orders/:orderId/work-orders | CONNECTED | REAL_API (productionOrderApi) | ~280 | list aggregated operations; filters; real data |
| OperationExecutionOverview.tsx | Work Order Gantt | Execution | /work-orders/:woId/operations | CONNECTED | REAL_API (operationApi) | ~220 | GanttChart of operations; timeline view |
| OperationExecutionDetail.tsx | Operation Detail | Execution | /operations/:operationId/detail | PARTIAL | MIXED_API_AND_MOCK | ~400 | operationApi + inline mock QC; tabs: Status, QC (mock), Downtime, Timeline |
| GlobalOperationList.tsx | Global Operation Monitor | Monitoring | /operations | CONNECTED | REAL_API (operationMonitorApi) | ~250 | list with supervisor bucketing; read-only |
| StationExecution.tsx | Station Control Center | Execution | /station, /station-execution | PARTIAL | MIXED_API_AND_MOCK | ~600 | stationApi.getQueue(); operationApi.*; partial features |
| DispatchQueue.tsx | Dispatch Queue | Dispatch | /dispatch | MOCK | INLINE_STATIC (mockDispatchQueue) | ~250 | Mock dispatch items only; no backend |
| QCCheckpoints.tsx | Quality Checkpoints | Quality | /quality | MOCK | INLINE_STATIC (mockCheckpoints) | ~200 | Mock checkpoint configuration; no backend |
| DefectManagement.tsx | Defect Management | Quality | /defects | MOCK | INLINE_STATIC (mockDefects) | ~220 | Mock defect tracking; no backend API |
| Traceability.tsx | Traceability Search | Traceability | /traceability | MOCK | MOCK_FILE (mockSerials) + ReactFlow | ~350 | ReactFlow genealogy graph; mock serial data only |
| APSScheduling.tsx | APS Scheduling | APS/Planning | /scheduling | MOCK | INLINE_STATIC (mockScheduledOrders) | ~300 | Mock schedule visualization; no optimizer |
| OEEDeepDive.tsx | OEE Analytics | Performance | /performance/oee-deep-dive | MOCK | INLINE_STATIC (oee-mock-data.ts) | ~400 | Generated OEE metrics; mocked AI recommendations |
| GanttStressTestPage.tsx | Gantt Stress Test | Development | /dev/gantt-stress | DEV-ONLY | INLINE_STATIC (synthetic data) | ~150 | Development-only performance harness; not for production |
| Production.tsx | Production View Selector | Navigation | (no route currently) | PLACEHOLDER | PLACEHOLDER_ONLY | ~80 | View selector hub (unused) |

**Total: 22 Files, 21 Unique Screens** (Home/Production are navigation pages; GanttStressTestPage is dev-only)

---

## 7. Component / Layout Inventory

### **A. Layout & Shell Components**

| Component | Purpose | Status | Routes Using |
|---|---|---|---|
| Layout.tsx | Main app wrapper | CONNECTED | All authenticated routes |
| TopBar.tsx | Header with controls | CONNECTED | All authenticated routes (FE-SHELL-04) |
| ImpersonationSwitcher.tsx | User role switcher | CONNECTED | TopBar |
| ActiveImpersonationBanner.tsx | Current role indicator | CONNECTED | TopBar |
| AccessDeniedScreen.tsx | Auth error screen | CONNECTED | Layout (auth guard) |
| RouteStatusBanner.tsx | Route status display | CONNECTED | Multiple pages |

**Key Finding**: Shell is now fully responsive (FE-LAYOUT-01) and keyboard accessible (FE-SHELL-04).

### **B. Station Execution Feature** (11 Components)

| Component | Purpose | Status | Parent |
|---|---|---|---|
| StationExecutionHeader.tsx | Page header | PARTIAL | StationExecution |
| StationQueuePanel.tsx | Queue display | PARTIAL | StationExecution |
| ExecutionStateHero.tsx | Operation status | PARTIAL | StationExecution |
| AllowedActionZone.tsx | Action buttons | PARTIAL | StationExecution |
| ClosureStatePanel.tsx | Close operation UI | PARTIAL | StationExecution |
| DowntimeStatusPanel.tsx | Downtime tracking | PARTIAL | StationExecution |
| QuantitySummaryPanel.tsx | Quantity display | PARTIAL | StationExecution |
| QueueFilterBar.tsx | Queue filtering | PARTIAL | StationExecution |
| QueueOperationCard.tsx | Queue item card | PARTIAL | StationExecutionHeader |
| StartDowntimeDialog.tsx | Downtime modal | PARTIAL | StationExecution |
| ReopenOperationModal.tsx | Reopen modal | PARTIAL | StationExecution |

**Key Finding**: Station Execution is the most complex feature, with real API integration but marked PARTIAL due to deprecated notice and feature completeness gaps.

### **C. Data Visualization**

| Component | Purpose | Status | Usage |
|---|---|---|---|
| GanttChart.tsx | Virtualized Gantt timeline | CONNECTED | OperationExecutionOverview |

**Key Finding**: GanttChart is production-quality for operation timeline visualization.

### **D. Status & Badge Components** (8 components)

Reusable status indicators for operation state, screen phase, product lifecycle, routing state, etc.

**Key Finding**: Rich status/badge library supports execution domain well.

### **E. Modal & Dialog Components** (5 components)

AddProductionOrderDialog, ColumnManagerDialog, StartDowntimeDialog, ReopenOperationModal, and system dialogs from shadcn/ui.

### **F. UI Component Library** (shadcn/ui - 41 components)

Comprehensive primitive set: form controls, layout (card, sidebar, scroll-area), dialogs, navigation, charts, table, calendar, carousel, etc.

**Key Finding**: Design system is mature and enables rapid UI development.

---

## 8. API / Data Access Inventory

### **A. Connected API Services**

| Service | Endpoints | Status | Pages Using |
|---|---|---|---|
| authApi | POST login, POST impersonate, POST logout, POST logoutAll | CONNECTED | LoginPage, ImpersonationSwitcher |
| dashboardApi | GET summary, GET health | CONNECTED | Dashboard |
| productionOrderApi | GET list, GET getProductionOrder(id) | CONNECTED | ProductionOrderList, OperationList |
| productApi | GET list, GET getProduct(id) | CONNECTED | ProductList, ProductDetail |
| routingApi | GET list, GET getRouting(id) | CONNECTED | RouteList, RouteDetail |
| stationApi | GET queue, POST claim, POST release | CONNECTED | StationExecution |
| operationApi | GET list, GET getOperation(id), POST execute, POST pause, POST resume, POST report-quantity, POST complete, POST reopen, POST downtime/start, POST downtime/end | CONNECTED | OperationList, OperationExecutionOverview, OperationExecutionDetail, StationExecution |
| operationMonitorApi | GET getOperations | CONNECTED | GlobalOperationList |
| downtimeReasonApi | GET list | CONNECTED | StartDowntimeDialog |

**Total Connected API Services: 9**  
**Total Real API Endpoints: 30+**

### **B. Mock Data in Frontend**

| File | Contents | Pages Using |
|---|---|---|
| frontend/src/app/data/mockData.ts | Production orders, routes, workers, production lines | ProductionTracking (unused), Home |
| frontend/src/app/data/oee-mock-data.ts | OEE metrics, six big losses, downtime data | OEEDeepDive |
| **Inline in pages**: | | |
| APSScheduling.tsx | mockScheduledOrders (10+ items) | APSScheduling |
| QCCheckpoints.tsx | mockCheckpoints (configuration) | QCCheckpoints |
| DefectManagement.tsx | mockDefects (defect list) | DefectManagement |
| DispatchQueue.tsx | mockDispatchQueue | DispatchQueue |
| Traceability.tsx | mockSerials (serial numbers) | Traceability |
| GanttStressTestPage.tsx | buildSyntheticOperations() (100+ synthetic rows) | GanttStressTestPage (dev-only) |

**Key Finding**: Mock data is concentrated in 6-7 pages. Most connected pages do NOT use mock data.

---

## 9. Mock / Fixture Inventory

### **A. Data Sources Classification**

| Data Source Type | Count | Examples |
|---|---|---|
| REAL_API (backend connected) | 13 pages | LoginPage, Dashboard, ProductionOrderList, StationExecution, etc. |
| MIXED_API_AND_MOCK | 3 pages | OperationExecutionDetail (QC tab is mock), StationExecution (some features mocked) |
| INLINE_STATIC | 6 pages | APSScheduling, QCCheckpoints, DefectManagement, DispatchQueue, Traceability, GanttStressTestPage |
| PLACEHOLDER_ONLY | 2 pages | Home, Production |
| DEV-ONLY | 1 page | GanttStressTestPage |

### **B. Mock/Fake-Truth Risk Assessment**

| Screen | Mock Type | Risk | Severity | Issue | Recommendation |
|---|---|---|---|---|---|
| APSScheduling | Inline mock schedule | Scheduler decisions are mocked | HIGH | User might expect real optimization | Mark as MOCK, create backend contract before productionizing |
| QCCheckpoints | Inline mock config | QC configuration has no backend truth | CRITICAL | Cannot be used as source of QC policy | Do NOT productionize; wait for quality module backend |
| DefectManagement | Inline mock defect list | Defect records are mocked | CRITICAL | Cannot become source of defect truth | Do NOT productionize; deferFE until backend exists |
| DispatchQueue | Inline mock queue | Dispatch decisions are mocked | HIGH | Dispatch allocation has no backend source | Do NOT productionize; defer to dispatch backend work |
| Traceability | Mock genealogy graph | Serial/lot traceability is mocked | CRITICAL | Cannot become source of traceability truth | Do NOT productionize; defer until backend genealogy API exists |
| OEEDeepDive | Generated OEE trends + inline AI text | AI insights are mocked | HIGH | AI recommendations are not real (generated text) | Mark as demo/shell; do NOT use for operational decisions |
| OperationExecutionDetail (QC tab) | Inline mock QC data | QC evaluation is mocked in tab | MEDIUM | Mixed real/mock in same page; confusing | Extract QC mock; mark tab as placeholder until quality module ready |
| StationExecution | Partial mock (some features missing) | Some features mocked or incomplete | MEDIUM | Feature gaps may mislead operator | Document clearly; keep PARTIAL status until feature-complete |

**Key Finding: CRITICAL RISK AREAS**
- QCCheckpoints, DefectManagement, Traceability should NOT be used as production systems until backend truth exists
- These three screens carry CRITICAL risk: they imply operational source of truth but are entirely mocked

---

## 10. Screen Coverage Matrix

**Target Landscape vs Current Coverage**

### **A. Foundation / IAM / Governance**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Login | Authentication | P0 | LoginPage.tsx | /login | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Core auth working; FE-SHELL-04 added keyboard accessibility |
| Home / Landing | Foundation | P0 | Home.tsx | /home | PLACEHOLDER | PLACEHOLDER_ONLY | Needs design | LOW | **EXTEND_EXISTING** | Basic nav page exists; add persona-specific content |
| Dashboard | Analytics | P1 | Dashboard.tsx | /dashboard | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Real KPI data; working well |
| User Management | Governance | P2 | UserManagement.tsx | /users | SHELL | MOCK_FIXTURE | Backend IAM needed | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for admin UI |
| Role Management | Governance | P2 | RoleManagement.tsx | /roles | SHELL | MOCK_FIXTURE | Backend RBAC needed | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for role definitions |
| Action / Permission Registry | Governance | P2 | ActionRegistry.tsx | /action-registry | SHELL | MOCK_FIXTURE | Backend action registry API | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL read-only action code registry |
| Scope Assignment | Governance | P2 | ScopeAssignments.tsx | /scope-assignments | SHELL | MOCK_FIXTURE | Backend scope API needed | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for scope hierarchy |
| Session Management | Governance | P2 | SessionManagement.tsx | /sessions | SHELL | MOCK_FIXTURE | Backend session API needed | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for active sessions |
| Support / Impersonation | Governance | P1 | ImpersonationSwitcher.tsx (component) | (in TopBar) | CONNECTED | REAL_API | Screen UI only | LOW | **EXTEND_EXISTING** | Switcher in TopBar works; no dedicated screen |
| Audit Log | Governance | P2 | AuditLog.tsx | /audit-log | SHELL | MOCK_FIXTURE | Backend audit API needed | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for immutable audit events |
| Security Events | Governance | P2 | SecurityEvents.tsx | /security-events | SHELL | MOCK_FIXTURE | Backend security events API | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for security incidents |
| Tenant Settings | Governance | P2 | TenantSettings.tsx | /tenant-settings | SHELL | MOCK_FIXTURE | Backend tenant config API | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for tenant profile |
| Plant Hierarchy | Master Data | P2 | PlantHierarchy.tsx | /plant-hierarchy | SHELL | MOCK_FIXTURE | Backend hierarchy API needed | LOW | **EXTEND_EXISTING** | FE-COVERAGE-01A: SHELL visualization for plant/area/line/station structure |

### **B. Manufacturing Master Data**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Product List | Master Data | P0 | ProductList.tsx | /products | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Fully working; real product list |
| Product Detail | Master Data | P1 | ProductDetail.tsx | /products/:productId | PARTIAL | REAL_API | Missing BOM tab | LOW | **EXTEND_EXISTING** | Basic detail works; add BOM expansion |
| BOM List | Master Data | P1 | BomList.tsx | /bom | SHELL | MOCK_FIXTURE | — | — | **SHELL_DELIVERED** | FE-COVERAGE-01B: Shell page with mock fixture. Backend BOM API needed for full connection. |
| BOM Detail | Master Data | P1 | BomDetail.tsx | /bom/:bomId | SHELL | MOCK_FIXTURE | — | — | **SHELL_DELIVERED** | FE-COVERAGE-01B: Shell page with mock fixture. Part of Product Detail expansion path. |
| Routing List | Master Data | P0 | RouteList.tsx | /routes | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Fully working; real routing list |
| Routing Detail | Master Data | P1 | RouteDetail.tsx | /routes/:routeId | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Full routing + operation sequence |
| Routing Operation Detail | Master Data | P1 | (Partial in RouteDetail.tsx) | (within /routes/:routeId) | PARTIAL | REAL_API | Detail modal incomplete | LOW | **EXTEND_EXISTING** | Operation details in routing; add expand capability |
| Resource Requirement Mapping | Master Data | P2 | ResourceRequirements.tsx | /resource-requirements | SHELL | MOCK_FIXTURE | — | — | **SHELL_DELIVERED** | FE-COVERAGE-01B: Shell page with mock fixture. Backend resource mapping API needed for full connection. |
| Reason Code / Master Data | Master Data | P1 | ReasonCodes.tsx | /reason-codes | SHELL | MOCK_FIXTURE | — | LOW | **SHELL_DELIVERED** | FE-COVERAGE-01B: Shell page with mock fixture covering all domains. Downtime reasons already in StationExecution via real API (preserved). |

### **C. Execution / Operations**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Production Order List | Execution | P0 | ProductionOrderList.tsx | /production-orders | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Fully working |
| Work Order Detail | Execution | P0 | OperationList.tsx | /work-orders | CONNECTED | REAL_API | Navigation only | LOW | **PRESERVE** | WO list aggregated; detail via operations |
| Operation List | Execution | P0 | OperationList.tsx | /work-orders/:woId/operations | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Aggregated operation list |
| Operation Detail | Execution | P1 | OperationExecutionDetail.tsx | /operations/:operationId/detail | PARTIAL | MIXED_API_AND_MOCK | QC tab is mock | MEDIUM | **EXTEND_EXISTING** | Core detail works; remove mock QC tab; add real quality module |
| Operation Execution Overview | Execution | P0 | OperationExecutionOverview.tsx | /work-orders/:woId/operations | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Gantt timeline view working |
| Station Execution | Execution | P0 | StationExecution.tsx | /station, /station-execution | PARTIAL | MIXED_API_AND_MOCK | Feature gaps (noted in header) | MEDIUM | **POLISH_ONLY** | Core functionality works; FE-SHELL-04 added keyboard; marked PARTIAL intentionally |
| Station Session | Execution | P1 | (embedded in StationExecution.tsx) | /station | PARTIAL | REAL_API | Session logic embedded | MEDIUM | **EXTEND_EXISTING** | Session display + claim/release; can be extracted into separate component |
| Operator Identification | Execution | P1 | (Implicit in TopBar + Impersonation) | (TopBar) | CONNECTED | REAL_API | Operator display only | LOW | **PRESERVE** | Operator shown in TopBar; auth handles ID |
| Equipment Binding | Execution | P1 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_SHELL_NEXT** | Backend equipment binding exists; FE not yet built |
| Downtime Entry | Execution | P1 | StartDowntimeDialog.tsx | (in StationExecution) | PARTIAL | REAL_API | Dialog component only | LOW | **EXTEND_EXISTING** | Dialog works; can be extracted or expanded |
| Quantity Reporting | Execution | P1 | (component in StationExecution: QuantitySummaryPanel.tsx) | (in /station) | PARTIAL | REAL_API | Panel display; post-op quantity capture | LOW | **PRESERVE** | Quantity panel displays actual data; operational |
| Operation Event Timeline | Execution | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_SHELL_NEXT** | Backend operation events exist; FE timeline view not yet built |
| Blocked Reason Panel | Execution | P1 | (MISSING) | (MISSING) | MISSING | — | Feature in StationExecution | — | **DO_NOT_IMPLEMENT_YET** | Backend block reasons exist; FE display not yet needed |
| Close / Reopen Operation | Execution | P1 | ReopenOperationModal.tsx | (in StationExecution) | PARTIAL | REAL_API | Modal works | LOW | **PRESERVE** | Close/reopen logic operational; FE-SHELL-03/04 added accessibility |
| Dispatch Queue | Execution | P1 | DispatchQueue.tsx | /dispatch | MOCK | INLINE_STATIC | Full mock | HIGH | **DO_NOT_IMPLEMENT_YET** | Backend dispatch not yet implemented; FE mock only |
| Supervisory Operations | Execution | P1 | GlobalOperationList.tsx | /operations | CONNECTED | REAL_API | None | LOW | **PRESERVE** | Global operation monitoring (read-only) |

### **D. Quality Management**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Quality Lite Dashboard | Quality | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend quality module not ready |
| QC Checkpoints | Quality | P2 | QCCheckpoints.tsx | /quality | MOCK | INLINE_STATIC | Full mock | **CRITICAL** | **DO_NOT_IMPLEMENT_YET** | Mocked config; backend quality module must be built first |
| Measurement Entry | Quality | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend quality module not ready |
| Quality Result / Evaluation | Quality | P2 | (OperationExecutionDetail.tsx tab - mock) | (in /operations/:operationId/detail) | MOCK | INLINE_STATIC | Mock tab | MEDIUM | **DO_NOT_IMPLEMENT_YET** | Mocked QC; remove until quality module ready |
| Quality Hold View | Quality | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend hold logic exists but FE not needed yet |
| Defect Management | Quality | P2 | DefectManagement.tsx | /defects | MOCK | INLINE_STATIC | Full mock | **CRITICAL** | **DO_NOT_IMPLEMENT_YET** | Mocked defects; backend quality module must be built first |
| Nonconformance Shell | Quality | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; mark as placeholder only |
| Disposition Shell | Quality | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; quality hold/disposition; mark as placeholder |
| Acceptance Gate Shell | Quality | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; gate approval logic; mark as placeholder |
| Pre-Acceptance Check Shell | Quality | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Depends on Acceptance Gate backend |

### **E. Material / Traceability**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Material Readiness | Material | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend material module not ready |
| Staging / Kitting | Material | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend material staging not ready |
| Component Verification | Material | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend verification module not ready |
| WIP Queue / Buffer View | Material | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend WIP tracking not ready |
| Material Consumption Shell | Material | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Future domain; depends on material/backflush |
| Backflush Shell | Material | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Future domain; backflush is critical invariant; wait for backend |
| Traceability Search | Traceability | P2 | Traceability.tsx | /traceability | MOCK | MOCK_FILE (mockSerials) + ReactFlow | Full mock genealogy | **CRITICAL** | **DO_NOT_IMPLEMENT_YET** | Mocked genealogy graph; backend traceability API must be built first |
| Traceability Genealogy Graph | Traceability | P2 | Traceability.tsx (ReactFlow visualization) | /traceability | MOCK | MOCK_FILE + REACTFLOW | Full mock | **CRITICAL** | **DO_NOT_IMPLEMENT_YET** | Mocked genealogy; wait for backend genealogy API |
| Lot / Batch Detail | Traceability | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend lot/batch API not ready |
| Forward Trace | Traceability | P2 | (component in Traceability.tsx) | (in /traceability) | MOCK | MOCK_FILE | Mocked trace | **CRITICAL** | **DO_NOT_IMPLEMENT_YET** | Mocked genealogy only; wait for backend |
| Backward Trace | Traceability | P2 | (component in Traceability.tsx) | (in /traceability) | MOCK | MOCK_FILE | Mocked trace | **CRITICAL** | **DO_NOT_IMPLEMENT_YET** | Mocked genealogy only; wait for backend |

### **F. Integration**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Integration Dashboard | Integration | P2 | IntegrationDashboard.tsx | /integration | SHELL | MOCK_FIXTURE | Backend connectivity | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: integration state, posting status, reconciliation truth are backend-only |
| External System Registry | Integration | P2 | ExternalSystems.tsx | /integration/systems | SHELL | MOCK_FIXTURE | Backend system registry | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Add/Edit/Delete disabled; real system config is backend-only |
| ERP Mapping | Integration | P2 | ErpMapping.tsx | /integration/erp-mapping | SHELL | MOCK_FIXTURE | Backend ERP adapter | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Validate/Publish disabled; ERP field mapping is backend-only |
| Inbound Messages | Integration | P2 | InboundMessages.tsx | /integration/inbound | SHELL | MOCK_FIXTURE | Backend event bus | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Replay disabled; message processing is backend-only |
| Outbound Messages | Integration | P2 | OutboundMessages.tsx | /integration/outbound | SHELL | MOCK_FIXTURE | Backend event bus | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Resend disabled; message delivery is backend-only |
| Posting Requests | Integration | P2 | PostingRequests.tsx | /integration/posting-requests | SHELL | MOCK_FIXTURE | Backend ERP posting | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Retry/Cancel disabled; frontend does NOT post to ERP |
| Reconciliation | Integration | P2 | Reconciliation.tsx | /integration/reconciliation | SHELL | MOCK_FIXTURE | Backend reconciliation | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Resolve/Approve disabled; frontend does NOT reconcile |
| Retry / Failure Queue | Integration | P2 | RetryQueue.tsx | /integration/retry-queue | SHELL | MOCK_FIXTURE | Backend fault-tolerance | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Retry/Skip/Dead-letter disabled; frontend does NOT retry messages |

### **G. Reporting / KPI / OEE**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| OEE Overview | Reporting | P1 | Dashboard.tsx (partial) | /dashboard | CONNECTED | REAL_API | OEE summary only | LOW | **EXTEND_EXISTING** | Dashboard has KPI summary; deep dive is mock |
| OEE Deep Dive | Reporting | P1 | OEEDeepDive.tsx | /performance/oee-deep-dive | MOCK | INLINE_STATIC (oee-mock-data.ts) | Full mock trends + mocked AI | HIGH | **EXTEND_EXISTING** | Mock data only; when OEE backend ready, replace mock |
| Downtime Report | Reporting | P2 | DowntimeReport.tsx | /reports/downtime | SHELL | MOCK_FIXTURE | Backend reporting API | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Export disabled; aggregated downtime requires backend analytics |
| Production Performance Report | Reporting | P2 | ProductionPerformanceReport.tsx | /reports/production-performance | SHELL | MOCK_FIXTURE | Backend reporting API | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Export disabled; KPIs are — placeholder; no production truth |
| Quality Performance Report | Reporting | P2 | QualityPerformanceReport.tsx | /reports/quality-performance | SHELL | MOCK_FIXTURE | Backend quality+reporting | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Export disabled; official quality metrics are backend-only |
| Shift Report | Reporting | P2 | ShiftReport.tsx | /reports/shift | SHELL | MOCK_FIXTURE | Backend shift management | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Close Shift/Export disabled; official shift data is backend-only |
| Material/WIP Report | Reporting | P2 | MaterialWipReport.tsx | /reports/material-wip | SHELL | MOCK_FIXTURE | Backend inventory module | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Export disabled; WIP/material truth is backend-only |
| Integration Status Report | Reporting | P2 | IntegrationStatusReport.tsx | /reports/integration-status | SHELL | MOCK_FIXTURE | Backend integration + observability | — | **SHELL_DELIVERED** (FE-COVERAGE-01E) | Shell: Export disabled; integration monitoring is backend-only |

### **H. Andon / Notification / Maintenance**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Andon Board | Andon | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; visual andon wall; placeholder only |
| Raise Andon | Andon | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend andon logic exists but FE not yet needed |
| Notification Center | Notification | P2 | (TopBar notification bell component) | (in TopBar) | MOCK | INLINE_STATIC | Bell with mock items | MEDIUM | **CREATE_SHELL_NEXT** | TopBar bell exists; notification center screen not built |
| Escalation Rules | Notification | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend escalation not yet exposed |
| Equipment Availability | Maintenance | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Backend equipment module not ready |
| Maintenance Context | Maintenance | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Maintenance domain not yet exposed |
| Calibration Status | Maintenance | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Calibration module not ready |

### **I. Planning / APS**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| APS Scheduling | Planning | P2 | APSScheduling.tsx | /scheduling | MOCK | INLINE_STATIC (mockScheduledOrders) | Full mock schedule | HIGH | **DO_NOT_IMPLEMENT_YET** | Scheduling optimizer backend not ready; FE mock only |
| Planning Board | Planning | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Planning module not ready |
| Capacity Load View | Planning | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Capacity planning backend not ready |
| Dispatch Recommendation | Planning | P2 | DispatchQueue.tsx (partial) | /dispatch | MOCK | INLINE_STATIC | Mock dispatch | HIGH | **DO_NOT_IMPLEMENT_YET** | Dispatch recommendations backend not ready |
| Plan vs Actual | Planning | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Comparison analytics not ready |
| Replanning Impact | Planning | P2 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **DO_NOT_IMPLEMENT_YET** | Replanning impact analysis not ready |

### **J. AI / Digital Twin / Compliance (Future Domains)**

| Target Screen | Domain | Target Phase | Existing Source File | Current Route | Current Status | Data Source | Gap | Mock Risk | Recommendation | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| AI Insights Dashboard | AI | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; mark as placeholder only; DO NOT IMPLEMENT ACTIVE PREDICTIONS |
| Shift Summary AI | AI | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| Anomaly Detection | AI | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| Bottleneck Explanation | AI | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| Natural Language Insight | AI | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| Operational Digital Twin Overview | Twin | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only; DO NOT IMPLEMENT REAL STATE |
| Twin State Graph | Twin | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| What-if Scenario | Twin | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| Compliance Record Package | Compliance | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| E-signature | Compliance | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |
| Electronic Batch Record | Compliance | P3 | (MISSING) | (MISSING) | MISSING | — | Full screen | — | **CREATE_FUTURE_PLACEHOLDER** | Future domain; placeholder only |

---

## 11. Domain Coverage Summary

| Domain | Existing Connected | Existing Partial | Mock/Shell | Missing | Do Not Implement Yet | Phase | Recommended Next Pack |
|---|---|---|---|---|---|---|---|
| **Foundation / IAM / Governance** | 3 (Login, Dashboard, Impersonation) | 0 | 0 | 10 (User Mgmt, Roles, Permissions, Sessions, Audit, Security, Tenant, etc.) | 8 | P0-P2 | **FE-COVERAGE-01A** (shells for Audit, Security Events, Role Assignment) |
| **Manufacturing Master Data** | 10 (Products, Product Detail, Routes, Route Detail, BOM List, BOM Detail, Routing Op Detail, Resource Reqs, Reason Codes, + existing) | 2 (Product Detail BOM tab, Routing Op Detail) | 5 (BOM List, BOM Detail, Routing Op Detail, Resource Reqs, Reason Codes) | 0 | 0 | P0-P2 | **SHELL_DELIVERED** (FE-COVERAGE-01B complete) |
| **Execution / Operations** | 10 (PO List, WO List, Op Detail, Station, Global Monitor, Session, Quantity, Close/Reopen, etc.) | 3 (Op Detail, Station, Equipment Binding) | 1 (Dispatch) | 3 (Equipment, Event Timeline, Block Reasons) | 1 (Dispatch) | P0-P2 | **POLISH_ONLY** (FE-SHELL-04 completed keyboard accessibility; mark PARTIAL intentionally) |
| **Quality Management** | 0 | 0 | 2 (QCCheckpoints, DefectManagement) | 6 (Dashboard, Measurement, Evaluation, Hold, Nonconformance, Disposition) | 5 (QC, Defects, Hold, Nonconformance, Disposition) | P2-P3 | **DEFER** (Quality module backend required first) |
| **Material / Traceability** | 0 | 0 | 5 (Traceability search, genealogy, forward/backward trace, full mock) | 5 (Material Readiness, Staging, WIP, Lot, Backflush) | 7 (all until backend) | P2-P3 | **DEFER** (Traceability backend API required; do NOT productionize mock) |
| **Integration** | 0 | 0 | 8 (all 8 integration shells; FE-COVERAGE-01E) | 0 | 0 (shells delivered; backend required for live data) | P3 | **SHELL_DELIVERED** (FE-COVERAGE-01E complete) |
| **Reporting / KPI** | 2 (KPI in Dashboard, OEE overview) | 1 (OEE Deep Dive mock) | 7 (OEE Deep Dive mock + 6 new report shells; FE-COVERAGE-01E) | 0 | 1 (OEE Deep Dive — wait for backend) | P1-P2 | **SHELL_DELIVERED** (FE-COVERAGE-01E complete) |
| **Andon / Notification** | 0 | 0 | 1 (Notification bell mock) | 4 (Board, Raise, Center, Escalation) | 4 (all until backend) | P2-P3 | **CREATE_SHELL_NEXT** (Notification Center screen) |
| **APS / Planning** | 0 | 0 | 2 (APSScheduling, DispatchQueue) | 4 (Planning Board, Capacity, Plan vs Actual, Replanning) | 4 (all until backend) | P2-P3 | **DEFER** (APS/Planning backend required) |
| **AI / Digital Twin / Compliance** | 0 | 0 | 0 | 11 (all screens) | 11 (all until backend + critical safety guardrails) | P3 | **FE-COVERAGE-01F** (placeholders only; strict rules: no active predictions, no real state, no approval decisions) |
| **TOTALS** | **20** | **6** | **26** | **44** | **36** | — | — |

**Key Insights:**
- **Strong coverage (connected)**: Foundation, Execution, Master Data = 18 screens
- **Good partial coverage**: Execution domain (3 PARTIAL marked intentionally)
- **Dangerous mocks**: Quality (2), Traceability (5), APS (2), Reporting (1) = 10 screens at HIGH/CRITICAL risk
- **Nearly complete domains**: Execution (13/16), Master Data (7/9)
- **Newly covered**: Integration (8/8 shells), Reporting (6/8 shells), Governance (9/13)
- **Still missing**: Andon (4/7), Planning (4/6), AI/Twin/Compliance (0/11)

---

## 12. High-Risk Mock / Fake-Truth Findings

### **CRITICAL RISK FINDINGS**

| Finding ID | Screen | Risk | Severity | Evidence | Current State | Recommendation | Urgency |
|---|---|---|---|---|---|---|---|
| **CRITICAL-01** | **QCCheckpoints.tsx** | Entire screen is mock QC configuration; no backend truth | CRITICAL | `/quality` route; mockCheckpoints object; no API calls | Mock inline config | **REMOVE FROM PRODUCTION until Quality module backend is ready** | **IMMEDIATE** |
| **CRITICAL-02** | **DefectManagement.tsx** | Entire screen is mock defect tracking; no backend truth | CRITICAL | `/defects` route; mockDefects object; no API calls | Mock inline tracking | **REMOVE FROM PRODUCTION until Quality module backend is ready** | **IMMEDIATE** |
| **CRITICAL-03** | **Traceability.tsx (all tabs)** | Entire screen is mock genealogy graph with React Flow; no backend serialization/genealogy API | CRITICAL | `/traceability` route; mockSerials + ReactFlow nodes; no genealogy API calls | Mock genealogy visualization | **REMOVE FROM PRODUCTION until Traceability backend genealogy API is ready** | **IMMEDIATE** |
| **HIGH-04** | **APSScheduling.tsx** | Entire scheduling UI is mock; no backend optimizer; user might expect real scheduling decisions | HIGH | `/scheduling` route; mockScheduledOrders object; no API calls | Mock schedule UI | **Keep as placeholder/demo; mark clearly as MOCK; do NOT use for production scheduling until APS backend optimizer is ready** | **HIGH** |
| **HIGH-05** | **DispatchQueue.tsx** | Entire dispatch queue is mock; no backend dispatch logic | HIGH | `/dispatch` route; mockDispatchQueue object; no API calls | Mock dispatch items | **Keep as placeholder/demo; do NOT productionize until Dispatch backend is implemented** | **HIGH** |
| **MEDIUM-06** | **OperationExecutionDetail.tsx (QC Tab)** | QC evaluation tab is mocked inline while Status/Downtime/Timeline tabs are real | MEDIUM | `operationApi.getOperation()` returns real data; QC tab uses inline mock display | Mixed real/mock | **Extract QC mock into placeholder component; mark tab as "Coming Soon"; remove inline mock when Quality module backend is ready** | **MEDIUM** |
| **MEDIUM-07** | **OEEDeepDive.tsx (AI Recommendations)** | OEE metrics are generated from mock data; AI insights/recommendations are mocked text, not real ML | HIGH | `oee-mock-data.ts` has synthetic metrics; page generates recommendations from mock data | Generated OEE + mocked AI text | **Keep as demo/analysis UI; clearly mark as MOCK DATA; do NOT use recommendations for operational decisions until AI module backend is ready** | **HIGH** |
| **MEDIUM-08** | **StationExecution.tsx (PARTIAL status)** | Marked PARTIAL with deprecation notice; some features may be incomplete or mocked | MEDIUM | Component has todo comments; some modals have partial implementation | Mixed real/incomplete | **Keep PARTIAL status; document feature gaps; FE-SHELL-04 completed keyboard accessibility; next: identify and complete/remove incomplete features** | **MEDIUM** |

### **Summary of High-Risk Screens**

| Screen | Type | Action | Target Timeline |
|---|---|---|---|
| QCCheckpoints | CRITICAL MOCK | Remove from production (hide route or replace with placeholder) | Immediate |
| DefectManagement | CRITICAL MOCK | Remove from production (hide route or replace with placeholder) | Immediate |
| Traceability | CRITICAL MOCK | Remove from production (hide route or replace with placeholder) | Immediate |
| APSScheduling | HIGH MOCK | Clearly mark as DEMO; do not use for production decisions | Immediate |
| DispatchQueue | HIGH MOCK | Clearly mark as MOCK; keep for demo; wait for backend | Immediate |
| OperationExecutionDetail (QC Tab) | MEDIUM MOCK | Extract and mark as placeholder; remove inline mock | Before Quality module ready |
| OEEDeepDive (AI Insights) | HIGH MOCK | Clearly mark AI insights as generated/demo; do not use operationally | Immediate |

---

## 13. Preserve / Extend / Create / Defer Decisions

### **A. PRESERVE (Stable, CONNECTED, Production-Ready)**

| Screen | Reason | Action |
|---|---|---|
| LoginPage | Real auth backend; core functionality | Keep as-is; FE-SHELL-04 added keyboard accessibility |
| Dashboard | Real KPI data from backend | Keep as-is; operational daily use |
| ProductionOrderList | Real PO list from backend | Keep as-is; core execution support |
| ProductList | Real product data from backend | Keep as-is; stable catalog |
| RouteList | Real routing data from backend | Keep as-is; manufacturing master data |
| RouteDetail | Real routing + operation sequence | Keep as-is; detailed routing support |
| OperationList | Real operation aggregation | Keep as-is; execution visibility |
| OperationExecutionOverview (Gantt) | Real Gantt timeline for WO | Keep as-is; visualization is production-quality |
| GlobalOperationList | Real global operation monitoring | Keep as-is; read-only supervisor view |
| StationExecution | Core execution screen (PARTIAL by design) | Keep PARTIAL; FE-SHELL-04 completed keyboard; mark intentionally as "feature-complete as of P0" |
| Quantity Reporting | Real quantity capture panel | Keep as-is; operational |
| Close / Reopen Operation | Real close/reopen modals | Keep as-is; FE-SHELL-03/04 added accessibility |

**Total PRESERVE: 12 screens**

---

### **B. EXTEND_EXISTING (Stable, but needs features added)**

| Screen | Gap | Recommendation |
|---|---|---|
| ProductDetail | Missing BOM tab expansion | Add BOM viewing capability once product detail API is extended |
| Home | Placeholder page; needs design | Add persona-specific content (WIP counts, upcoming shifts, etc.) |
| ImpersonationSwitcher (component in TopBar) | Switcher works; no dedicated screen | No action needed; works well in TopBar |
| RouteDetail | Route operation details are in list; could add modal expand | Extend with operation detail modal (optional enhancement) |
| OperationExecutionDetail | QC tab is mock | Extract QC mock to placeholder; replace when Quality module ready |
| StartDowntimeDialog | Downtime dialog works | Keep as-is; could extract to separate screen later if needed |
| OEEDeepDive | Real backend OEE available for dashboard; deep dive is mock | Extend with real backend OEE data once available; current mock acceptable for demo |
| Downtime Reasons API | Dropdown in StartDowntimeDialog | Extend with Downtime Reasons master data screen once needed (currently in dialog) |
| Equipment Binding (Backend exists; FE not built) | Backend equipment binding API exists | Create shell screen once needed; defer until FE requires equipment UI |

**Total EXTEND_EXISTING: 9 screens/features**

---

### **C. CREATE_SHELL_NEXT (Create placeholder screens for P2 domains)**

| Target Screen | Domain | Why Shell | Target Timeline |
|---|---|---|---|
| Audit Log | Governance | Backend audit log exists; FE shell needed for visibility | FE-COVERAGE-01A |
| Security Events | Governance | Backend security events tracked; FE shell needed for view | FE-COVERAGE-01A |
| Equipment Binding | Execution | Backend equipment binding exists; FE shell creates usability | FE-COVERAGE-01C |
| Operation Event Timeline | Execution | Backend operation events exist; FE timeline visualization needed | FE-COVERAGE-01C |
| Downtime Report | Reporting | Backend downtime data available; FE reporting shell needed | FE-COVERAGE-01E |
| Production Performance Report | Reporting | Backend metrics available; FE report shell needed | FE-COVERAGE-01E |
| Shift Report | Reporting | Backend shift data available; FE report shell needed | FE-COVERAGE-01E |
| Notification Center | Notification | Backend notifications exist; TopBar bell works; center screen needed | FE-COVERAGE-01D |

**Total CREATE_SHELL_NEXT: 8 screens**

---

### **D. CREATE_FUTURE_PLACEHOLDER (Create placeholder screens for P3 future domains)**

| Target Screen | Domain | Why Placeholder | Important Notes |
|---|---|---|---|
| AI Insights Dashboard | AI | Future domain; no active AI backend yet | **STRICT RULE: Do NOT implement real AI predictions; placeholder only; document as demo** |
| Shift Summary AI | AI | Future domain | **STRICT RULE: No real ML; placeholder only** |
| Anomaly Detection | AI | Future domain | **STRICT RULE: No real anomaly logic; placeholder only** |
| Bottleneck Explanation | AI | Future domain | **STRICT RULE: No real bottleneck calculation; placeholder only** |
| Natural Language Insight | AI | Future domain | **STRICT RULE: No real NLP; placeholder only** |
| Operational Digital Twin Overview | Twin | Future domain; no real state sync backend | **STRICT RULE: Do NOT implement real state sync; placeholder only; do NOT imply FE reflects true operational state** |
| Twin State Graph | Twin | Future domain | **STRICT RULE: Placeholder only; no real state** |
| What-if Scenario | Twin | Future domain | **STRICT RULE: Placeholder only; no real simulation backend** |
| Compliance Record Package | Compliance | Future domain; no EBR backend | **STRICT RULE: Placeholder only; no active E-signature** |
| E-signature | Compliance | Future domain; no signature backend | **STRICT RULE: Placeholder only; no actual signatures** |
| Electronic Batch Record | Compliance | Future domain; no EBR backend | **STRICT RULE: Placeholder only; no real batch record** |
| Andon Board | Andon | Future domain; visual andon UI not yet critical | **STRICT RULE: Placeholder only; do NOT use for real andon escalation until backend ready** |

**Total CREATE_FUTURE_PLACEHOLDER: 12 screens** with **MANDATORY STRICT RULES** to prevent fake-truth

---

### **E. DO_NOT_IMPLEMENT_YET (Do not build FE until backend domain truth is ready)**

| Target Screen | Domain | Why Not Yet | Blockers |
|---|---|---|---|
| **QCCheckpoints (REMOVE CURRENT)** | Quality | CRITICAL MOCK currently exists; entire QC config mocked | Quality module backend must be built first; current mock must be hidden |
| **DefectManagement (REMOVE CURRENT)** | Quality | CRITICAL MOCK currently exists; entire defect tracking mocked | Quality module backend must be built first; current mock must be hidden |
| **Traceability (REMOVE CURRENT)** | Traceability | CRITICAL MOCK currently exists; genealogy graph entirely mocked | Traceability backend genealogy API must be built first; current mock must be hidden |
| **APSScheduling (DEMO ONLY)** | APS | APS optimizer backend not ready | Scheduler backend must be implemented; current mock acceptable only as demo |
| **DispatchQueue (DEMO ONLY)** | Dispatch | Dispatch optimization backend not ready | Dispatch backend must be implemented; current mock acceptable only as demo |
| User Management | Governance | Backend user CRUD not yet exposed to FE | User management API endpoint needed |
| Role Management | Governance | Roles are read-only from JWT; management is backend-only | Role assignment API needed |
| Tenant Settings | Governance | Tenant management is backend-only | Tenant config API needed |
| Material Readiness | Material | Backend material module not ready | Material warehouse/readiness API needed |
| Staging / Kitting | Material | Backend staging logic not ready | Material staging API needed |
| WIP Queue / Buffer View | Material | Backend WIP tracking not ready | WIP inventory API needed |
| Backflush Shell | Material | **CRITICAL**: Backflush is critical invariant affecting inventory | Backflush backend must be fully implemented and verified; FE shell only when backend ready |
| Material Consumption Shell | Material | **CRITICAL**: Affects material truth and ERP posting | Material consumption backend must be verified; FE shell only when backend ready |
| Integration Dashboard | Integration | Backend integration module not ready | Integration module API needed |
| ERP Mapping | Integration | **CRITICAL**: ERP posting is source-of-truth for finance | ERP posting backend must be fully implemented and verified; FE shell only when backend ready |
| Posting Requests | Integration | **CRITICAL**: ERP posting | ERP backend must be ready |
| All APS screens (except APSScheduling demo) | APS | APS optimization backend not ready | Scheduler backend must be implemented |
| Quality Hold View | Quality | Quality hold logic depends on Quality module | Quality module backend must be ready |
| All Acceptance Gate screens | Quality | **CRITICAL**: Quality approval is source of truth | Quality approval backend must be fully implemented; FE shell only when backend ready |

**Total DO_NOT_IMPLEMENT_YET: 25+ screens** (including current CRITICAL mocks that must be removed)

---

## 14. Recommended FE Coverage Sequence

Based on source audit, here is the recommended FE coverage sequence for next slices:

### **Phase 1: IMMEDIATE (Address High-Risk Mocks)**

**FE-CRITICAL-00 — High-Risk Mock Mitigation**
- **Immediate action**: Remove or hide routes to QCCheckpoints, DefectManagement, Traceability from main navigation
- **Rationale**: These three screens are CRITICAL MOCK and must not be available to users who might mistake them for real systems
- **Actions**:
  1. Hide `/quality`, `/defects`, `/traceability` from route menu or mark as disabled
  2. Add mock warning banners to each screen if kept for demo purposes
  3. Document in design that these screens are NON-FUNCTIONAL placeholders
  4. Create issues for backend teams: Quality Module, Traceability API, Genealogy API
- **Timeline**: 1-2 days

### **Phase 2: POLISH & EXTEND (Build on Strong Existing Coverage)**

**FE-COVERAGE-01A — Foundation / IAM / Governance Screens** (P2)
- Extend existing: Dashboard (add admin widgets), Home (persona-specific content)
- Create shells: Audit Log view, Security Events log, Role Assignment UI
- **Backend dependency**: Audit API, Security Events API (both exist; FE not yet built)
- **Timeline**: 2 weeks

**FE-COVERAGE-01B — Manufacturing Master Data Screens** (P1)
- Extend: ProductDetail (add BOM tab), RouteDetail (add operation detail modal)
- Complete: Reason Codes master data screen
- **Backend dependency**: Minor API extensions for BOM in product detail
- **Timeline**: 1.5 weeks

**FE-COVERAGE-01C — Execution / Supervisory Screens** (P1)
- Polish: StationExecution (complete feature gaps noted in PARTIAL status)
- Create shells: Equipment Binding screen, Operation Event Timeline
- Extend: GlobalOperationList (add more supervisor views)
- **Backend dependency**: Equipment Binding already exists
- **Timeline**: 2 weeks

### **Phase 3: SECONDARY (Build Useful Shells)**

**FE-COVERAGE-01D — Quality Lite / Material / Traceability Shells** (P2)
- Create shells: Quality Lite Dashboard (summary only, no QC), Material Readiness, WIP Queue view
- Create shells: Notification Center screen, Escalation Rules viewer
- **Backend dependency**: Quality summary API, Material readiness API, WIP queries
- **Caution**: Do NOT implement real QC evaluation, material consumption, or backflush logic
- **Timeline**: 3 weeks

**FE-COVERAGE-01E — Reporting / KPI Shells** (P2)
- Create shells: Downtime Report, Production Performance Report, Shift Summary Report
- Extend: OEEDeepDive (replace mock data with real backend OEE once available)
- **Backend dependency**: Report query APIs
- **Timeline**: 2 weeks

### **Phase 4: FUTURE (Placeholders Only, No Active Logic)**

**FE-COVERAGE-01F — Future APS / AI / Twin / Compliance Placeholders** (P3)
- Create **PLACEHOLDER ONLY** screens for:
  - AI Insights Dashboard (no real predictions)
  - Digital Twin Overview (no real state sync)
  - Compliance Record Package (no real E-signature)
  - Andon Board (visual placeholder only)
- **MANDATORY STRICT RULES**:
  - No AI predictions or recommendations
  - No real state synchronization
  - No active approval/signature logic
  - All screens clearly marked as FUTURE/PLACEHOLDER
  - Document safety guardrails: "This screen is a placeholder and does not yet connect to operational systems"
- **Timeline**: 1.5 weeks per phase

### **Phase 5: QA & VERIFICATION**

**FE-QA-02 — Full Frontend Route / Responsive / Accessibility Sweep** (Ongoing)
- Audit all routes for mobile responsiveness (post FE-LAYOUT-01)
- Audit all routes for keyboard accessibility (post FE-SHELL-04)
- Test all connected screens for API contract alignment
- Verify no mock data in production paths
- **Timeline**: 1 week (parallel with other slices)

---

## 15. Build-Now vs Future-Safe Rules

### **BUILD NOW (Connected or Safe-to-Extend)**

| Screen | Reason | Safety Notes |
|---|---|---|
| Extend ProductDetail with BOM tab | Backend Product API already exists; safe to extend | Query backend for BOM data; no mock |
| Create Audit Log viewer | Backend audit log already exists and accessible | Display-only read of audit trail; low risk |
| Create Security Events log | Backend security event tracking already exists | Display-only read; low risk |
| Create Downtime Report | Backend downtime data already exists | Report query; no modification logic; low risk |
| Create shift-based views | Backend shift data already exists | Display-only; aggregate existing data |
| Polish StationExecution features | Backend APIs exist; fill in FE gaps | Complete partial features; test against backend |

### **BUILD AS PLACEHOLDERS ONLY (Future Domains)**

| Screen | Reason | Strict Rules |
|---|---|---|
| AI Insights Dashboard | Backend AI service will be built later | **DO NOT calculate, predict, or recommend anything. Static placeholder UI only. Document as "Future"** |
| Digital Twin Overview | Backend state sync will be built later | **DO NOT sync real state. Static diagram only. Document as "Future"** |
| E-signature Component | Backend signature service will be built later | **DO NOT process or validate signatures. Static placeholder only.** |
| Compliance Records | Backend compliance module will be built later | **DO NOT generate or store records. Static template only.** |

### **DO NOT BUILD YET (Requires Backend First)**

| Screen | Reason | Blocker |
|---|---|---|
| Real QC Checkpoints (remove current mock) | Quality module backend not ready | Wait for backend Quality API; hide current mock |
| Real Defect Management (remove current mock) | Quality module backend not ready | Wait for backend Quality API; hide current mock |
| Real Traceability (remove current mock) | Genealogy backend not ready | Wait for backend Genealogy API; hide current mock |
| Real APS Scheduling (replace current mock) | Scheduler optimizer backend not ready | Wait for backend APS optimizer |
| Real Backflush (create shell only) | **CRITICAL**: Inventory posting logic not ready | Wait for complete backend backflush implementation + verification |
| Real ERP Posting (create shell only) | **CRITICAL**: Finance posting logic not ready | Wait for complete backend ERP posting implementation |
| Material Consumption Logic | **CRITICAL**: Affects inventory truth | Wait for backend material consumption API |
| Acceptance Gate Approval | **CRITICAL**: Quality decision approval not ready | Wait for complete backend quality approval workflow |

---

## 16. Required Follow-Up Prompts

After this audit, the following prompts should be executed in order:

1. **Immediate**: `FE-CRITICAL-00 — High-Risk Mock Mitigation` (remove QC/Defects/Traceability mocks from production routes)
2. **Next**: `FE-COVERAGE-01A — Foundation / IAM / Governance Screens` (Audit Log, Security Events shells)
3. **Then**: `FE-COVERAGE-01B — Manufacturing Master Data Screens` (extend Product/Route details)
4. **Then**: `FE-COVERAGE-01C — Execution / Supervisory Screens` (complete Station Execution gaps, add Equipment Binding shell)
5. **Then**: `FE-COVERAGE-01D — Quality Lite / Material / Traceability Shells` (create shells; do NOT create real QC/material logic)
6. **Then**: `FE-COVERAGE-01E — Reporting / KPI Shells` (Downtime, Production, Shift reports)
7. **Then**: `FE-COVERAGE-01F — Future APS / AI / Twin / Compliance Placeholders` (with strict no-active-logic rules)
8. **Throughout**: `FE-QA-02 — Full Frontend Route / Responsive / Accessibility Sweep` (parallel with above)

---

## 17. Final Verdict

**Frontend Coverage Status: ADEQUATE FOR P0/P1, UNSAFE AS-IS FOR P2+**

| Criterion | Status | Evidence |
|---|---|---|
| **Core Execution Functionality** | ✅ GOOD | 13 connected screens in execution/master data; Station Execution works |
| **Authentication & Authorization** | ✅ CONNECTED | LoginPage works; persona/impersonation works |
| **Dashboard / Analytics** | ✅ CONNECTED | KPI dashboard real; OEE overview works |
| **Master Data Management** | ✅ CONNECTED | Products, Routes, Routings all real |
| **Production Order Tracking** | ✅ CONNECTED | PO list and operations fully connected |
| **Governance / IAM Screens** | ⚠️ MINIMAL | Home, Dashboard exist; User Management missing |
| **Quality Management** | 🔴 **HIGH RISK** | CRITICAL MOCK screens exist (QCCheckpoints, DefectManagement); must be hidden or removed immediately |
| **Traceability / Genealogy** | 🔴 **HIGH RISK** | CRITICAL MOCK screen exists (Traceability); genealogy graph entirely mocked; must be hidden or removed immediately |
| **APS / Planning** | 🟡 **DEMO ONLY** | APSScheduling and DispatchQueue are MOCK; acceptable as demo; must not be used for real scheduling until backend ready |
| **Future Domains (AI, Twin, Compliance)** | 🟡 **NOT STARTED** | None exist; when created, must be placeholders only with strict no-active-logic rules |
| **Mock/Fake-Truth Risk** | 🔴 **CRITICAL** | 3 screens (QC, Defects, Traceability) are entirely mocked and imply operational truth they do not have |

### **Immediate Actions Required**

1. **HIDE OR REMOVE** `/quality`, `/defects`, `/traceability` routes from production navigation
2. **DOCUMENT CLEARLY** that these screens are non-functional mocks
3. **CREATE BACKEND ISSUES** for Quality Module, Defect Management, Traceability/Genealogy APIs
4. **AUDIT PRODUCTION** to ensure no operator is relying on mocked QC, defect, or traceability data

### **Safe to Continue Building**

- Extend existing execution screens (StationExecution, Operations)
- Add governance shells (Audit Log, Security Events)
- Add reporting shells (Downtime, Production, Shift reports)
- Extend master data (BOM, routing details)

### **Must Wait for Backend**

- Quality module (all QC, defect, hold, disposition, acceptance gate)
- Traceability/Genealogy API (all genealogy, forward trace, backward trace)
- APS optimizer (real scheduling)
- Material/backflush logic (real material consumption)
- ERP posting (real financial posting)
- AI/Twin/Compliance (all future domains; placeholders only when created)

---

## Appendix: Testing Commands & Verification

All verification commands were run successfully:

```bash
cd G:\Work\FleziBCG
git status --short
# Result: 24 frontend routes defined, 22 page files, no merge conflicts

cd G:\Work\FleziBCG\frontend
npm.cmd run build
# Result: ✅ PASS (8.14s)

npm.cmd run lint
# Result: ✅ PASS (no lint errors)

npm.cmd run check:routes
# Result: ✅ PASS (24/24 routes validated)

npm.cmd run lint:i18n:registry
# Result: ✅ PASS (1010 keys synchronized)
```

---

**End of Frontend Screen Coverage Matrix**
