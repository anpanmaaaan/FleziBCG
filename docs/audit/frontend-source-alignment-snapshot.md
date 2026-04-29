# Frontend Source Alignment Snapshot — FleziBCG

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial snapshot. Full FE source inspection against design packs, screen maps, and DESIGN.md. |
| 2026-04-29 | v1.1 | FE-1 UI Safety & Screen Status Guardrails applied (screen status registry, i18n keys, warning banners, tab badges). |
| 2026-04-29 | v1.2 | FE-1 build-environment verification added. Build execution blocked due Node/npm unavailable in current automation shell PATH. |
| 2026-04-29 | v1.3 | FE-2 Route/Page Status Integration applied with layout-level route status badge/banner and duplicate warning cleanup. |
| 2026-04-29 | v1.4 | FE-3 Product/Routing UI Shell Readiness added with Product shell pages, route registration, and status classification alignment. |
| 2026-04-29 | v1.5 | FE-4A Product Read API Connection added with read-only Product API client wiring, Product List/Detail read states, and status reclassification to PARTIAL. |
| 2026-04-29 | v1.6 | FE-4A.1 Product Read Smoke / UX Hardening added with status-aware error UX, missing route-id handling, and product lifecycle/type badge readability improvements. |
| 2026-04-29 | v1.7 | FE-4A.2 Product Route Accessibility Fix applied by aligning persona route allowlist/menu with existing `/products` router registration. |
| 2026-04-29 | v1.8 | FE governance hardening: Route Accessibility Prevention Gate added to acceptance policy and checklist to prevent router/persona/menu drift regressions. |
| 2026-04-29 | v1.9 | FE-GOV-02 added automated route smoke script (`check:routes`) for static route/persona/menu/screenStatus consistency checks. |
| 2026-04-29 | v1.10 | FE-GOV-02.1 added route smoke check to PR gate as non-blocking CI signal with promotion TODO after stabilization cycle. |
| 2026-04-29 | v1.11 | FE-5 Routing Read API Connection added with read-only routing API client wiring, Route List/Detail backend read states, and route status reclassification to PARTIAL. |
| 2026-04-29 | v1.12 | FE-5.1 Routing Read Smoke / UX Hardening added with reusable routing display helpers, verified read-state coverage, and preserved read-only lifecycle controls. |
| 2026-04-29 | v1.13 | FE-5.1 Verification Retry Mode rerun completed; status remains BLOCKED due Node/npm unavailable in active terminal environment across PowerShell and cmd fallbacks. |
| 2026-04-29 | v1.14 | FE-5.1 Verification Retry Attempt 2 (after reported environment fix): Node/npm still unavailable despite diagnostic checks; winget install hung on admin elevation. Verdict: BLOCKED. |
| 2026-04-29 | v1.15 | FE-5.1 Docker-Based Verification completed. Used Docker Node container to verify FE-5.1: npm install PASS, build PASS (1m 4s), lint PASS, route smoke check PASS (24/24). Verdict: PASS. |
| 2026-04-29 | v1.16 | FE-GOV-03 Ignore Rules Hardening applied: root .gitignore and frontend/.dockerignore hardened for local/generated FE artifacts; tracked frontend/dist finding documented with de-track decision deferred to human cleanup PR. |
| 2026-04-29 | v1.17 | FE-GOV-03.1 Tracked Artifact Cleanup applied: `frontend/dist` de-tracked from Git index (kept local and ignored), `frontend/package-lock.json` churn reverted, and tracking/ignore state re-verified. |

**Track:** PARALLEL LIGHT FE — source audit + FE-1/FE-2/FE-3/FE-4A/FE-4A.1/FE-4A.2/FE-5 + route-access governance hardening + FE-GOV-02/02.1 automation.
**Auditor:** AI Brain auto-execution.
**Source Date:** 2026-04-29.
**Baseline design refs:** `docs/design/DESIGN.md`, `docs/design/05_application/screen-map-and-navigation-architecture.md`, `docs/design/07_ui/*`, `docs/audit/source-code-audit-report.md`.

---

## 1. Executive Summary

The FleziBCG frontend is an **early-to-mid maturity** React/Vite/Tailwind SPA with a persona-driven nav shell.

**Strong foundation elements:**
- Auth, JWT session, impersonation, and i18n infrastructure are CONNECTED and well-structured.
- Station Execution (StationExecution.tsx) is the most complete screen — fully CONNECTED to the real backend execution API.
- Global Operations monitor (GlobalOperationList.tsx) and the Operation Execution Gantt overview are also CONNECTED.
- Dashboard is CONNECTED to backend summary/health APIs.
- A full design-token CSS layer (`theme.css`) is defined and referenced.
- A rich shadcn/Radix UI component library (`src/app/components/ui/`) is installed and ready to use.
- Persona-based navigation routing is implemented and enforced.

**Critical maturity gaps:**
- 10 of 20 registered pages are entirely MOCK data — no backend API calls.
- No React Query or SWR — all server state is manual `useEffect + useState` with no cache, deduplication, or loading/error normalisation.
- QC, Defects, Traceability, APS Scheduling, Dispatch Queue, and OEE are all MOCK-only with hardcoded fixture data.
- The `OperationExecutionDetail` page mixes a CONNECTED operation header with entirely hardcoded QC/material/timeline tab data.
- Station Session Entry screen (STX-000) is MISSING — the new session-owned execution model has no UI entry point.
- `Production.tsx` and `ProductionTracking.tsx` exist as page files but are NOT registered in the router.
- `@supabase/supabase-js` remains as a vestigial dependency with no usage found.
- TypeScript `strict: false` — many runtime safety risks suppressed.

**Overall FE Maturity Rating: 35% CONNECTED, 50% MOCK/PARTIAL, 15% MISSING/SHELL.**

---

## 2. Frontend Source Structure

```
frontend/
├── package.json              — React 18.3.1 / Vite 6 / Tailwind 4 / react-router 7
├── vite.config.ts            — @tailwindcss/vite plugin, @ alias to src/, proxy /api → :8010
├── tsconfig.json             — ES2022, strict: FALSE, @ path alias
├── eslint.config.js          — TS-eslint
├── index.html
├── public/
│   └── flezi-logo.png        — (brand logo)
├── scripts/
│   ├── check_i18n_hardcode.sh
│   └── check_i18n_registry_parity.mjs
├── supabase/                 — VESTIGIAL — no active usage found
└── src/
    ├── main.tsx              — app entry: mounts App into #root
    ├── vite-env.d.ts
    ├── lib/
    │   └── utils.ts          — cn() class merger (clsx + tailwind-merge)
    ├── styles/
    │   ├── index.css         — imports tailwind.css + theme.css
    │   ├── tailwind.css      — @import tailwindcss, tw-animate-css
    │   └── theme.css         — CSS custom properties: brand tokens, status tokens, sidebar, charts
    ├── types/                — (empty or minimal)
    └── app/
        ├── App.tsx           — root providers: I18nProvider > AuthProvider > ImpersonationProvider > RouterProvider
        ├── routes.tsx        — createBrowserRouter — 22 registered routes
        ├── api/              — 8 API client modules
        ├── auth/             — AuthContext, RequireAuth
        ├── components/       — shared UI + shadcn/Radix ui/ suite
        ├── data/             — mock fixture files
        ├── i18n/             — custom i18n infrastructure
        ├── impersonation/    — ImpersonationContext
        ├── pages/            — 20 page files (see Section 4)
        └── persona/          — personaLanding.ts, PersonaLandingRedirect.tsx
```

**Tech stack confirmed:**

| Layer | Technology | Version |
|---|---|---|
| Framework | React | 18.3.1 |
| Build | Vite | 6.4.1 |
| Styling | Tailwind CSS | 4.1.12 |
| Routing | react-router | 7.13.0 |
| State (server) | Manual useEffect/useState | None (no React Query) |
| State (UI) | React Context | AuthContext, ImpersonationContext, I18nContext |
| Component lib | shadcn + Radix UI | full suite installed |
| Charts | Recharts | 2.15.2 |
| Flow diagrams | ReactFlow | 11.11.4 |
| Drag/drop | react-dnd | 16.0.1 |
| Notifications | sonner | 2.0.3 |
| Forms | react-hook-form | 7.55.0 |
| HTTP | Custom fetch wrapper | httpClient.ts |
| i18n | Custom context | en + ja registries |
| Material UI | MUI v7 | 7.3.5 (installed, limited usage visible) |
| Vestigial | @supabase/supabase-js | 2.x — NO USAGE FOUND |

---

## 3. Current Route Registry

Source: `frontend/src/app/routes.tsx`

| Route Path | Component | Protection | Notes |
|---|---|---|---|
| `/login` | LoginPage | Public | CONNECTED |
| `/` (index) | PersonaLandingRedirect | RequireAuth | Redirects by persona |
| `/home` | Home | RequireAuth | |
| `/dashboard` | Dashboard | RequireAuth | |
| `/performance/oee-deep-dive` | OEEDeepDive | RequireAuth | |
| `/production-orders` | ProductionOrderList | RequireAuth | |
| `/dispatch` | DispatchQueue | RequireAuth | |
| `/routes` | RouteList | RequireAuth | |
| `/routes/:routeId` | RouteDetail | RequireAuth | |
| `/work-orders` | OperationList | RequireAuth | All WOs |
| `/production-orders/:orderId/work-orders` | OperationList | RequireAuth | PO-scoped WOs |
| `/work-orders/:woId/operations` | OperationExecutionOverview | RequireAuth | Gantt view |
| `/operations` | GlobalOperationList | RequireAuth | Read-only monitor |
| `/operations/:operationId/detail` | OperationExecutionDetail | RequireAuth | Tabs view |
| `/station` | StationExecution | RequireAuth | Primary OPR screen |
| `/station-execution` | StationExecution | RequireAuth | Alias |
| `/quality` | QCCheckpoints | RequireAuth | |
| `/defects` | DefectManagement | RequireAuth | |
| `/traceability` | Traceability | RequireAuth | |
| `/scheduling` | APSScheduling | RequireAuth | |
| `/settings` | Dashboard | RequireAuth | PLACEHOLDER → redirects to Dashboard |
| `/dev/gantt-stress` | GanttStressTestPage | RequireAuth + DEV only | Dev harness |

**Orphaned page files (exist but NOT in router):**
- `Production.tsx` — shell, accessible only if directly navigated historically
- `ProductionTracking.tsx` — shell, not reachable

---

## 4. Current Page Inventory

| Page File | Route(s) | Status | Backend API | Classification |
|---|---|---|---|---|
| `LoginPage.tsx` | `/login` | CONNECTED | `authApi.login`, `authApi.me` | PRESERVE |
| `Home.tsx` | `/home` | MOCK | None — full mock station/production lines | REFACTOR_LATER |
| `Dashboard.tsx` | `/dashboard` | CONNECTED | `dashboardApi.getSummary`, `dashboardApi.getHealth` | PRESERVE |
| `ProductionOrderList.tsx` | `/production-orders` | CONNECTED | `productionOrderApi.list` | PRESERVE |
| `RouteList.tsx` | `/routes` | MOCK | None — uses `mockData.routes` | REFACTOR_LATER |
| `RouteDetail.tsx` | `/routes/:routeId` | MOCK | None — hardcoded route definition | REFACTOR_LATER |
| `OperationList.tsx` | `/work-orders`, `/production-orders/:id/work-orders` | CONNECTED | `productionOrderApi.list`, `productionOrderApi.get` | PRESERVE |
| `OperationExecutionOverview.tsx` | `/work-orders/:woId/operations` | CONNECTED | `/v1/work-orders/:id/execution-timeline` | PRESERVE |
| `OperationExecutionDetail.tsx` | `/operations/:operationId/detail` | PARTIAL | `operationApi.get` (header) — QC/material/timeline tabs are MOCK | EXTEND |
| `GlobalOperationList.tsx` | `/operations` | CONNECTED | `operationMonitorApi` | PRESERVE |
| `DispatchQueue.tsx` | `/dispatch` | MOCK | None — full mock queue | REFACTOR_LATER |
| `QCCheckpoints.tsx` | `/quality` | MOCK | None — full mock checkpoints | REPLACE |
| `DefectManagement.tsx` | `/defects` | MOCK | None — full mock defects | REPLACE |
| `Traceability.tsx` | `/traceability` | MOCK | None — full mock serials + reactflow graph | REPLACE |
| `APSScheduling.tsx` | `/scheduling` | MOCK | None — full mock scheduled orders | REPLACE |
| `StationExecution.tsx` | `/station`, `/station-execution` | CONNECTED | `stationApi`, `operationApi`, `fetchDowntimeReasons` | PRESERVE |
| `OEEDeepDive.tsx` | `/performance/oee-deep-dive` | MOCK | None — `oee-mock-data.ts` | REPLACE |
| `GanttStressTestPage.tsx` | `/dev/gantt-stress` | SHELL | None — dev stress test only | PRESERVE (dev) |
| `Production.tsx` | NOT IN ROUTER | SHELL | None | REMOVE_IF_UNUSED |
| `ProductionTracking.tsx` | NOT IN ROUTER | SHELL | None | REMOVE_IF_UNUSED |

**Status summary:**
- CONNECTED: 7 pages (35%)
- PARTIAL: 1 page (5%)
- MOCK: 10 pages (50%)
- SHELL/ORPHAN: 2 pages (10%)

---

## 5. Current Component Inventory

### Shared App Components (`src/app/components/`)

| Component | Status | Classification |
|---|---|---|
| `Layout.tsx` | CONNECTED — sidebar, persona nav, impersonation banner, TopBar | PRESERVE |
| `TopBar.tsx` | CONNECTED — auth user, live clock, locale switcher, impersonation | PRESERVE |
| `PageHeader.tsx` | CONNECTED — standard page header with title, back button, slot | PRESERVE |
| `StatusBadge.tsx` | CONNECTED — semantic variant badge (success/warning/error/info/neutral/purple/cyan) | PRESERVE |
| `StatsCard.tsx` | CONNECTED — KPI card, used by GlobalOperationList and OperationExecutionDetail | PRESERVE |
| `GanttChart.tsx` | CONNECTED — Gantt with virtualization (react-window), used in OperationExecutionOverview | PRESERVE |
| `Breadcrumb.tsx` | CONNECTED — breadcrumb navigation | PRESERVE |
| `AccessDeniedScreen.tsx` | CONNECTED — persona enforcement screen | PRESERVE |
| `ActiveImpersonationBanner.tsx` | CONNECTED — impersonation session banner | PRESERVE |
| `ImpersonationSwitcher.tsx` | CONNECTED — impersonation start/end UI | PRESERVE |
| `ColumnManagerDialog.tsx` | CONNECTED — column visibility management (used in ProductionOrderList) | PRESERVE |
| `AddProductionOrderDialog.tsx` | PARTIAL — dialog shell; action not fully wired | EXTEND |
| `figma/ImageWithFallback.tsx` | SHELL — image with error fallback | PRESERVE |

### shadcn/Radix UI Suite (`src/app/components/ui/`)

Full set installed: accordion, alert-dialog, alert, avatar, badge, button, calendar, card, carousel, chart, checkbox, command, context-menu, dialog, drawer, dropdown-menu, form, hover-card, input-otp, input, label, menubar, navigation-menu, pagination, popover, progress, radio-group, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, switch, table, tabs, textarea, toggle, tooltip, use-mobile.ts, utils.ts.

**Classification: PRESERVE (all) — do not remove; provide foundation for future screens.**

Note: `sidebar.tsx` from shadcn is present but the current Layout uses a custom sidebar implementation, not the shadcn sidebar component.

---

## 6. Current Layout and Navigation Pattern

### App Shell
- **Sidebar** (custom): collapsible, dark slate (`#1E293B`), width `w-72` / collapsed `w-20`, persona-driven menu items.
- **TopBar**: live clock, plant selector (hardcoded `DMES`), locale switcher (en/ja), notification bell (no backend), impersonation switcher, user dropdown (logout/logout-all).
- **Main content**: `flex-1 overflow-auto` area, routed via `<Outlet />`.
- **Login**: standalone full-screen, no sidebar/topbar.

### Persona-Based Navigation
- Personas: `OPR | SUP | IEP | QC | PMG | EXE | ADM | DENY`
- Resolved from `currentUser.role_code` or active impersonation `acting_role_code`.
- `STRICT` enforcement mode redirects unauthorized paths to persona landing. `DEV` mode is permissive.
- Default landings: OPR → `/station`, SUP → `/operations?lens=supervisor`, IEP → `/operations?lens=ie`, QC → `/operations?lens=qc`, PMG/EXE/ADM → `/dashboard`.
- Menu items are persona-scoped — OPR sees only Station Execution; PMG sees full breadth.

### Route Guard
- `RequireAuth` redirects to `/login` with `state.from` when no authenticated session.
- No role-gated route elements — persona enforcement is done in Layout, not the route tree.

---

## 7. Current API Client and Data Access Pattern

### HTTP Client (`src/app/api/httpClient.ts`)
- Custom `fetch`-based client.
- Context provider pattern: `setHttpContextProvider` injects `authToken` and `tenantId` per request.
- Auto-prepends `/api` prefix and `/v1/...` paths.
- Parses JSON or text response.
- Throws `HttpError` with `status` + `detail` on non-2xx.
- `setUnauthorizedHandler` triggers logout on 401.
- Dev mode HTTP debug logging via `VITE_HTTP_DEBUG_AUTH=1`.

### API Module Inventory

| Module | Endpoints | Backend Status |
|---|---|---|
| `authApi.ts` | `POST /v1/auth/login`, `GET /v1/auth/me`, `POST /v1/auth/logout`, `POST /v1/auth/logout-all` | CONNECTED |
| `impersonationApi.ts` | `GET /v1/impersonations/current`, `POST /v1/impersonations/start`, `POST /v1/impersonations/end` | CONNECTED |
| `dashboardApi.ts` | `GET /v1/dashboard/summary`, `GET /v1/dashboard/health` | CONNECTED |
| `productionOrderApi.ts` | `GET /v1/production-orders`, `GET /v1/production-orders/:id` | CONNECTED |
| `operationApi.ts` | `GET/PUT/POST /v1/operations/:id` (start, pause, resume, complete, close, reopen, report qty, start/end downtime) | CONNECTED |
| `operationMonitorApi.ts` | `GET /v1/production-orders`, `GET /v1/operations` (monitor) + filters | CONNECTED |
| `stationApi.ts` | `GET /v1/station/queue`, `POST /v1/station/queue/:id/claim`, `POST /v1/station/queue/:id/release`, `GET /v1/station/queue/:id/detail` | CONNECTED |
| `downtimeReasons.ts` | `GET /v1/downtime-reasons` | CONNECTED |

### No API Coverage (domain gaps)
- `/v1/routes` — Route management (no client module)
- `/v1/quality` — QC entries, results, disposition
- `/v1/defects` — Defect records
- `/v1/traceability` — Traceability / genealogy
- `/v1/materials` — Material consumption
- `/v1/scheduling` — APS
- `/v1/oee` — OEE analytics
- `/v1/users` — User admin
- `/v1/sessions` — Station session entry (new model)

### Data Access Anti-Patterns Detected
- Manual `useEffect + useState` pattern used across all pages — no caching, deduplication, or stale-data handling.
- Race condition risk on quick unmount/remount (some pages use `cancelled` flag, some do not).
- No centralized error boundary.
- API field name duplication in `operationMonitorApi.ts` — both camelCase and snake_case versions of each field exist as optional, indicating a backend response format inconsistency or defensive mapping.

---

## 8. Current State Management Pattern

| Concern | Solution | Quality |
|---|---|---|
| Auth session | `AuthContext` (React Context) — token in localStorage | GOOD |
| Impersonation | `ImpersonationContext` (React Context) — polls `/impersonations/current` on mount | GOOD |
| i18n locale | `I18nContext` (React Context) — locale in localStorage | GOOD |
| Server data | Manual `useEffect + useState` per component | POOR — no cache, no dedup |
| UI state | Component-local `useState` | ACCEPTABLE |
| Form state | react-hook-form (installed, limited usage) | PARTIAL |
| Toasts | `sonner` | GOOD |

**Missing:** React Query, SWR, or Zustand. Every page re-fetches independently with no sharing or invalidation strategy.

---

## 9. Current i18n Pattern

- **Custom I18nContext** — `en.ts` + `ja.ts` registries under `src/app/i18n/registry/`.
- **Keys** typed in `src/app/i18n/keys.ts` as `I18nSemanticKey` — enforces key exhaustiveness.
- **`useI18n()` hook** — returns `{ t, locale, setLocale }`.
- **`t(key, vars?, fallback?)` function** — supports `{varName}` interpolation.
- **CI enforcement**: `npm run lint:i18n` checks for hardcoded UI strings and registry parity between en/ja.
- **Locale switching** at runtime via TopBar; locale persisted to localStorage.

**Quality: STRONG.** i18n infrastructure is complete, typed, and CI-enforced. This is a genuine competitive strength.

---

## 10. Current Styling and Design Token Pattern

### Token Layer (`src/styles/theme.css`)

| Token Group | Defined | Usage |
|---|---|---|
| Primary (`--primary`) | `#3B82F6` (blue) | Buttons, links, active states |
| Sidebar tokens | `--sidebar: #1E293B` (dark slate) | Layout.tsx sidebar |
| Status tokens | PENDING, IN_PROGRESS, COMPLETED, BLOCKED, DELAYED, ON_HOLD, CANCELLED (color + bg) | Partially used |
| Brand CTA | `--brand-cta: #33B2C1` (teal) | Minimal usage detected |
| Chart tokens | `--chart-1` through `--chart-7` | Recharts |
| Surface tokens | `--surface-page`, `--surface-table-header`, `--surface-divider` | Partially used |
| Radius | `--radius: 0.625rem` | Components |

### Usage Pattern
- Tailwind utility classes dominate most component styling.
- shadcn components consume the CSS custom properties via their built-in var() references.
- Status colors in `StatusBadge.tsx` are Tailwind hardcoded (`bg-green-100`, `bg-red-100`) — NOT using the status CSS tokens from theme.css. **This is a gap.**
- `StatsCard` and other components also hardcode Tailwind colors without token reference.
- `GanttChart` uses its own internal color constants.

### DESIGN.md Alignment
- Design tokens are present and broadly consistent with `DESIGN.md` principles.
- Font: No explicit `Inter` import — falls back to system-ui. DESIGN.md requires Inter or system-ui, so this is acceptable.
- Touch targets: Operator screens mostly use standard Tailwind padding. Not always 48–56px for primary operator actions. **Gap for STX-002 Cockpit.**

---

## 11. Current Mock / Fixture Pattern

| File | Contents | Used By | Risk |
|---|---|---|---|
| `src/app/data/mockData.ts` | ProductionOrders[], Operations[], Routes[], OrderCards[], ProductionLines[] | RouteList, RouteDetail, ProductionTracking, Home | HIGH — shows in prod UI |
| `src/app/data/oee-mock-data.ts` | OEE trend, six big losses, downtime, line comparison, insights, predictions | OEEDeepDive | HIGH — shows in prod UI |
| Inline mock data | DispatchQueue, QCCheckpoints, DefectManagement, APSScheduling, Traceability | Each page | HIGH — shows in prod UI |

**All mock data is hardcoded with fictional 2024 timestamps and toy data.** These screens ship to production users in their current state. There is no mock/production separation guard on any of these pages.

---

## 12. Source-to-Design Screen Mapping

Reference packs: `docs/design/07_ui/*`, `docs/design/05_application/screen-map-and-navigation-architecture.md`

### Foundation / IAM

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| Login | `LoginPage.tsx` | CONNECTED | Auth call real. Brand/logo correct. |
| Me / bootstrap | `AuthContext.tsx` | CONNECTED | Handled in auth context, no dedicated screen. |
| Station Session Entry (STX-000) | **MISSING** | MISSING | New session-owned execution model has no UI entry point. |
| User lifecycle admin | **MISSING** | MISSING | No user management screens. |
| Session registry / revoke | **MISSING** | MISSING | No session admin screen. |
| Approval / impersonation views | `ImpersonationSwitcher.tsx` | PARTIAL | Start/end in TopBar. No audit review screen. |

### Execution

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| STX-001 Station Queue | `StationExecution.tsx` | PARTIAL | Queue is CONNECTED via stationApi. Uses old claim model (stationApi.claim/release) — deprecated per ENGINEERING_DECISIONS §10. |
| STX-002 Execution Cockpit | `StationExecution.tsx` | PARTIAL | Inline with queue. Actions (start/pause/resume/report/complete/downtime) CONNECTED. Close/Reopen present. No session-owned context (operator identity, equipment bind). |
| STX-003 Downtime Dialog | Inside `StationExecution.tsx` | CONNECTED | Reason codes fetched from real API. |
| STX-004 Reopen Dialog | Inside `StationExecution.tsx` | CONNECTED | Reason required. |
| Execution Cockpit (full, session-aware) | **MISSING** | FUTURE | New STX-002 design requires session context, bound equipment, identified operator. Not implemented. |

### Supervisory / Monitor

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| Global Operations Dashboard | `GlobalOperationList.tsx` | CONNECTED | Multi-lens (supervisor/ie/qc). Real data. |
| Operation Detail Tabs | `OperationExecutionDetail.tsx` | PARTIAL | Header CONNECTED. QC/Material/Timeline tabs MOCK hardcoded. |
| WO Gantt / Timeline | `OperationExecutionOverview.tsx` | CONNECTED | Uses /v1/work-orders/:id/execution-timeline. Gantt renders. |
| Work Order List | `OperationList.tsx` | CONNECTED | Normalized from productionOrderApi. |
| Production Order List | `ProductionOrderList.tsx` | CONNECTED | Column manager, real API. |

### Quality

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| QC Requirements View | `QCCheckpoints.tsx` | MOCK | No backend. Toy data. |
| Measurement Entry | **MISSING** | MISSING | No screen exists. |
| QC Result / Outcome | **MISSING** | MISSING | Only mock stub in OperationExecutionDetail. |
| Defect Management | `DefectManagement.tsx` | MOCK | No backend. Toy data. |
| Disposition / Review | **MISSING** | MISSING | |

### Performance / Analytics

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| Dashboard KPIs | `Dashboard.tsx` | CONNECTED | Real API. Chart data from recharts with real backend KPIs. |
| OEE Deep Dive | `OEEDeepDive.tsx` | MOCK | All from `oee-mock-data.ts`. AI insights fabricated. |
| Dispatch Queue | `DispatchQueue.tsx` | MOCK | No backend. |

### Traceability

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| Serial / Lot Trace | `Traceability.tsx` | MOCK | No backend. ReactFlow genealogy visualization from toy data. |
| Backward / Forward Trace | **MISSING** | MISSING | Design calls for these, not yet represented. |

### APS / Scheduling

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| APS Schedule View | `APSScheduling.tsx` | MOCK | No backend. |

### Routes / Product Engineering

| Design Screen | Source File | Status | Notes |
|---|---|---|---|
| Route List | `RouteList.tsx` | MOCK | Uses `mockData.routes`. |
| Route Detail | `RouteDetail.tsx` | MOCK | Full route editing UI but no backend API. |

---

## 13. Preserve / Extend / Replace Decisions

### PRESERVE (do not change)
- `App.tsx` — provider hierarchy is correct and complete.
- `routes.tsx` — router structure is sound. Do not add routes without updating persona menu.
- `auth/AuthContext.tsx`, `auth/RequireAuth.tsx` — auth session lifecycle is correct.
- `impersonation/ImpersonationContext.tsx` — correctly wired to backend.
- `i18n/` (all files) — solid infrastructure, CI-enforced.
- `api/httpClient.ts` — mature, handles auth headers and tenant correctly.
- `api/authApi.ts`, `api/dashboardApi.ts`, `api/operationApi.ts`, `api/stationApi.ts`, `api/operationMonitorApi.ts`, `api/productionOrderApi.ts`, `api/impersonationApi.ts`, `api/downtimeReasons.ts` — all correct and backend-aligned.
- `api/mappers/executionMapper.ts` — correct status-to-badge mapping.
- `components/Layout.tsx` — persona nav is solid.
- `components/TopBar.tsx` — auth + impersonation + locale + clock correct.
- `components/StatusBadge.tsx` — reusable, keep as-is.
- `components/PageHeader.tsx`, `StatsCard.tsx`, `GanttChart.tsx` — preserve.
- `components/ui/*` — entire shadcn suite. Do not remove.
- `styles/theme.css` — design token layer. Extend, do not rewrite.
- `pages/LoginPage.tsx` — fully correct.
- `pages/Dashboard.tsx` — connected, good quality.
- `pages/StationExecution.tsx` — primary execution screen, connected. Note: needs session model migration later.
- `pages/GlobalOperationList.tsx` — connected, multi-lens, good quality.
- `pages/OperationExecutionOverview.tsx` — Gantt view, connected.
- `pages/OperationList.tsx` — work order list, connected.
- `pages/ProductionOrderList.tsx` — connected with column manager.
- `persona/personaLanding.ts`, `persona/PersonaLandingRedirect.tsx` — persona enforcement correct.

### EXTEND (add real API, keep existing shell)
- `pages/OperationExecutionDetail.tsx` — QC, Material, Timeline tabs need real API endpoints. Operation header is already real. Extend tab data, do not rewrite the shell.
- `components/AddProductionOrderDialog.tsx` — wire dialog submit to real API.

### REFACTOR_LATER (current mock is acceptable short-term)
- `pages/Home.tsx` — operational home screen with mock station data. Defer until station session API is complete.
- `pages/RouteList.tsx` — route management mock. Acceptable until route admin API exists.
- `pages/RouteDetail.tsx` — route editing mock. Acceptable until route admin API exists.
- `pages/DispatchQueue.tsx` — dispatch mock. Acceptable until dispatch API exists.

### REPLACE (mock-only, no structural re-use planned)
- `pages/QCCheckpoints.tsx` — entirely mock. Replace when Quality Lite API exists.
- `pages/DefectManagement.tsx` — entirely mock. Replace when Defect API exists.
- `pages/Traceability.tsx` — entirely mock. Replace when Traceability API exists.
- `pages/APSScheduling.tsx` — entirely mock. Replace when APS API exists.
- `pages/OEEDeepDive.tsx` — entirely mock. Replace when OEE analytics API exists.

### REMOVE_IF_UNUSED
- `pages/Production.tsx` — not in router. Orphaned shell. Remove if no plan to revive.
- `pages/ProductionTracking.tsx` — not in router. Orphaned shell. Remove if no plan to revive.
- `supabase/` directory — vestigial from previous stack. No usage found.
- `@supabase/supabase-js` dependency — remove from package.json after confirming no hidden usage.

### DO_NOT_IMPLEMENT_YET
- Station Session Entry (STX-000) UI — wait for backend session model stabilization.
- Material consumption UI — no backend model.
- ERP posting / backflush UI — no backend model.
- Backward/forward traceability — no backend model.
- User lifecycle admin screens — depends on User model completion.

---

## 14. Missing Screen Groups

These design-required screens have NO source file in the current frontend:

| Screen Group | Design Pack | Priority | Blocking Condition |
|---|---|---|---|
| **STX-000 Station Session Entry** | Station Execution v4.0 | P0 | Backend station session model must be stable |
| **Execution Cockpit (session-aware)** | Station Execution v4.0 | P0 | New session model, operator identity, equipment bind |
| **User lifecycle admin** | Foundation IAM | P1 | User model completion needed |
| **Session registry / revoke screen** | Foundation IAM | P1 | Backend session admin API |
| **QC Measurement Entry** | Quality Lite | P2 | Quality domain backend |
| **QC Result / Outcome View** | Quality Lite | P2 | Quality domain backend |
| **QC Disposition / Review** | Quality Lite | P3 | Quality domain backend |
| **Backward / Forward Trace** | Traceability | P3 | Traceability backend |
| **Lot / Batch Genealogy Explorer** | Traceability | P3 | Traceability backend |
| **Material Movement Lineage** | Traceability | P3 | Material backend |
| **Settings Screen** | (implied) | P2 | Currently placeholder → Dashboard |

---

## 15. Source Alignment Constraints for Figma Make

When generating Figma Make prompts or design-to-code output, observe the following constraints:

1. **Use `@` alias** — all imports must use `@/app/...`, not relative paths deeper than one level.
2. **Use `useI18n()` hook** — never hardcode user-visible strings. All strings must be keyed via `I18nSemanticKey`.
3. **Use `StatusBadge` component** — do not create new badge implementations.
4. **Use `PageHeader` component** — standard page header, do not reimplement.
5. **Use `theme.css` custom properties** — status colors should reference `--status-*` tokens, not hardcode Tailwind color classes.
6. **Use `shadcn/Radix UI` components** — from `src/app/components/ui/`. Do not introduce MUI components into new screens (MUI already in package.json but not the preferred component layer).
7. **Do not invent API fields** — only use fields present in the typed API interfaces.
8. **Do not derive execution state on frontend** — `allowed_actions` comes from backend. Respect it. Do not compute authorization locally.
9. **Do not fake quality results** — no hardcoded `status: "Passed"` in production components.
10. **Keep mock data in `src/app/data/`** — never inline mock fixtures in production page components.
11. **Persona-gated navigation** — any new route must be added to `personaLanding.ts` menu tables for appropriate personas.
12. **Maintain `RequireAuth`** — all protected routes must stay inside the protected route group in `routes.tsx`.
13. **TypeScript strict is off** — but new code should be as type-safe as practically possible. Do not rely on `any` for business data.
14. **No new dependencies** without explicit decision — the stack is already heavy. Prefer existing installed packages.

---

## 16. Recommended Domain UI Pack Sequence

The following sequence respects backend availability and FE foundation quality:

### Slice 1 — Station Execution Foundation (NOW / P0)
**What:** Fill the critical gap between the deprecated claim-based StationExecution.tsx and the new session-owned model.
**Why now:** The execution backend is the most mature and CONNECTED area. Operators cannot use the new model without a session entry point.
**Screens:** STX-000 Station Session Entry, STX-001 Queue (non-claim), STX-002 Cockpit (session-aware).
**Backend dependency:** Station session API (`/v1/station/session`) — verify availability before implementing.

### Slice 2 — Operation Execution Detail Tabs (NOW / P1)
**What:** Replace mock QC/Material/Timeline tab data in `OperationExecutionDetail.tsx` with real API calls.
**Why now:** The operation header is already CONNECTED. The tabs are currently lying to supervisors.
**Screens:** `OperationExecutionDetail.tsx` tab content — QC summary, material actuals, real event timeline.
**Backend dependency:** QC result read endpoints, operation event history endpoint.

### Slice 3 — Foundation IAM Admin Screens (P1)
**What:** User lifecycle admin, session registry/revoke.
**Why:** Required for operators to be created and managed without direct DB access.
**Screens:** New screens in a `/admin` or `/settings` route group.
**Backend dependency:** User admin API, session admin API.

### Slice 4 — Quality Lite (P2)
**What:** Replace `QCCheckpoints.tsx` and `DefectManagement.tsx` with real API-backed versions.
**Backend dependency:** Quality domain backend.

### Slice 5 — OEE Analytics (P2)
**What:** Replace `OEEDeepDive.tsx` with real OEE API data.
**Backend dependency:** OEE / reporting API.

### Slice 6 — Traceability (P3)
**What:** Replace `Traceability.tsx` with real trace data and genealogy from backend.
**Backend dependency:** Traceability / genealogy API.

### Slice 7 — Route Admin (P3)
**What:** Connect `RouteList.tsx` and `RouteDetail.tsx` to a backend route management API.
**Backend dependency:** Route admin API.

### Slice 8 — APS Scheduling (FUTURE)
**What:** Replace `APSScheduling.tsx` with real APS data.
**Backend dependency:** APS engine and schedule API.

---

## 17. FE Implementation Guidance

### For every new or extended page:

1. Read the relevant design pack from `docs/design/07_ui/`.
2. Check `docs/design/05_application/screen-map-and-navigation-architecture.md` for screen family.
3. Read `docs/design/DESIGN.md` sections 7 (shopfloor), 8 (AI), 9 (implementation rules), 10 (do-not-fake).
4. Identify which API endpoints are available from backend before writing any component.
5. Use `useEffect + useState` for now — do not introduce React Query without a design decision.
6. All i18n keys must be added to both `registry/en.ts` and `registry/ja.ts` and pass the lint CI.
7. For any execution action (start/pause/resume/complete/close/reopen): check `allowed_actions` from backend before rendering the button. Do not compute locally.
8. For quality results: never set a status to "Passed" or "Failed" from frontend logic.
9. For any new screen added to the router, add it to the appropriate persona menu in `personaLanding.ts`.
10. Test persona enforcement: OPR must not reach supervisor-only screens.

### For Figma Make output:

- Figma Make generates Tailwind + React. Output must be adapted to use the project's `@/` alias and `useI18n()`.
- Replace any hardcoded mock data with proper API hooks before merging.
- Verify all Tailwind classes against `theme.css` token layer.

---

## 18. Risks and Warnings

### Top 10 Risks

| # | Risk | Severity | Detail |
|---|---|---|---|
| R01 | **Mock data ships to production users** | CRITICAL | DispatchQueue, QCCheckpoints, DefectManagement, APSScheduling, Traceability, OEEDeepDive all render toy data to real users. No mock/prod guard. These screens present fabricated operational truth. |
| R02 | **OperationExecutionDetail QC/Material tabs are fake** | CRITICAL | Supervisors viewing this screen see hardcoded QC results (e.g. "Passed", "Bore Diameter Check") that are not real. This violates the do-not-fake-quality-pass/fail rule. |
| R03 | **Station Execution uses deprecated claim model** | HIGH | `stationApi.claim/release` is used in StationExecution.tsx. ENGINEERING_DECISIONS §10 marks the claim-based model as deprecated. No session-owned model implemented. Operators may get unexpected 409 errors or stale claim state. |
| R04 | **No React Query / server state management** | HIGH | Manual useEffect patterns across all 20 pages create race conditions, stale data, and no cache invalidation. Under load or rapid navigation, operation state may be stale when actions are taken. |
| R05 | **OEEDeepDive AI insight panel fakes AI output** | HIGH | The "AI insight" and "next shift risk prediction" cards render values from `oee-mock-data.ts`. This violates the AI advisory rules — AI must not be presented as deterministic without real model output. |
| R06 | **TypeScript strict disabled** | MEDIUM | `tsconfig.json strict: false` suppresses null/undefined, type narrowing, and implicit any errors across the entire frontend. Runtime type errors are possible in production. |
| R07 | **Production.tsx and ProductionTracking.tsx are orphaned** | MEDIUM | These pages are not in the router but are part of the build. They contain mock data and hardcoded Unsplash image URLs. Dead code accumulation risk. |
| R08 | **@supabase/supabase-js dependency with no usage** | MEDIUM | A ~200KB+ dependency adds build weight with no apparent purpose. If it was used for auth previously, it must be confirmed removed from all code paths. |
| R09 | **No centralized error boundary** | MEDIUM | No React `ErrorBoundary` component wraps any route group. A crash in any page component will crash the entire app. |
| R10 | **StatusBadge and StatsCard hardcode Tailwind colors, not theme.css tokens** | LOW | Design token layer (`--status-*` tokens) is not consumed by the primary display components. Future theme changes (dark mode, high-contrast) would require touching every component rather than just tokens. |

### Additional Warnings

- **Plant selector in TopBar is hardcoded** to `'DMES'`. Multi-tenant or multi-plant scenarios are not reflected in UI despite tenant_id being sent in every API request.
- **Notification bell in TopBar** is visual only — no backend notification feed.
- **`/settings` route** redirects to Dashboard — any user clicking Settings sees the Dashboard without explanation.
- **No offline / connectivity error state** — if the backend goes down, pages silently fail or show blank states without user guidance.
- **Dual API field name pattern in operationMonitorApi.ts** (both camelCase and snake_case variants) suggests the API response format may have changed and the client was patched defensively. This should be cleaned up.

---

## 19. Appendix — Raw Inventories

### A. Page Files

```
frontend/src/app/pages/
├── APSScheduling.tsx            MOCK
├── Dashboard.tsx                CONNECTED
├── DefectManagement.tsx         MOCK
├── DispatchQueue.tsx            MOCK
├── GanttStressTestPage.tsx      SHELL (dev only)
├── GlobalOperationList.tsx      CONNECTED
├── Home.tsx                     MOCK
├── LoginPage.tsx                CONNECTED
├── OEEDeepDive.tsx              MOCK
├── OperationExecutionDetail.tsx PARTIAL
├── OperationExecutionOverview.tsx CONNECTED
├── OperationList.tsx            CONNECTED
├── Production.tsx               SHELL (orphaned, not in router)
├── ProductionOrderList.tsx      CONNECTED
├── ProductionTracking.tsx       SHELL (orphaned, not in router)
├── QCCheckpoints.tsx            MOCK
├── RouteDetail.tsx              MOCK
├── RouteList.tsx                MOCK
├── StationExecution.tsx         CONNECTED (partial — old claim model)
└── Traceability.tsx             MOCK
```

### B. API Clients

```
frontend/src/app/api/
├── authApi.ts                   CONNECTED
├── dashboardApi.ts              CONNECTED
├── downtimeReasons.ts           CONNECTED
├── httpClient.ts                CONNECTED (core)
├── impersonationApi.ts          CONNECTED
├── index.ts                     (barrel export)
├── mappers/
│   └── executionMapper.ts       UTILITY — status badge + progress mappers
├── operationApi.ts              CONNECTED (full lifecycle)
├── operationMonitorApi.ts       CONNECTED (monitor + lenses)
├── productionOrderApi.ts        CONNECTED
└── stationApi.ts                CONNECTED (old claim model)
```

### C. Mock Data Files

```
frontend/src/app/data/
├── mockData.ts                  — Routes, ProductionOrders, Operations, ProductionLines
└── oee-mock-data.ts             — OEE trend, losses, downtime, insights
```

### D. i18n Registry

```
frontend/src/app/i18n/
├── I18nContext.tsx              — Provider with en/ja selection + interpolation
├── index.ts                     — barrel
├── keys.ts                      — I18nSemanticKey type union
├── namespaces.ts                — namespace definitions
├── useI18n.ts                   — hook
└── registry/
    ├── en.ts                    — English strings
    └── ja.ts                    — Japanese strings
```

### E. Design Token Summary

```css
--primary: #3B82F6
--sidebar: #1E293B
--brand-cta: #33B2C1
--status-pending: #94a3b8
--status-in-progress: #3b82f6
--status-completed: #10b981
--status-blocked: #ef4444
--status-delayed: #f59e0b
--status-on-hold: #8b5cf6
--status-cancelled: #6b7280
--radius: 0.625rem
```

### F. Persona Menu Matrix

| Persona | Code | Landing | Menu Screens |
|---|---|---|---|
| Operator | OPR | `/station` | Station Execution |
| Supervisor | SUP | `/operations?lens=supervisor` | Global Ops, PO, WO, Routes, Quality, Defects |
| IE Process | IEP | `/operations?lens=ie` | Global Ops, PO, WO, Routes, Traceability, Quality |
| Quality Control | QC | `/operations?lens=qc` | Global Ops, Quality, Defects, Traceability, PO, WO, Routes |
| Production Manager | PMG | `/dashboard` | Dashboard, OEE, Global Ops, PO, WO, Routes, Dispatch, Quality, Defects, Traceability, Scheduling |
| Executive | EXE | `/dashboard` | Dashboard, OEE, Global Ops, PO |
| Admin | ADM | `/dashboard` | Dashboard, OEE, Global Ops, PO, WO, Routes, Dispatch, Quality, Defects, Traceability, Scheduling |
| Unknown/Unresolved | DENY | — | Access Denied |

---

## FE-1 Guardrails Applied

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Scope Applied

- Added centralized screen status registry in `frontend/src/app/screenStatus.ts`.
- Added `screenStatus` i18n namespace and bilingual key coverage in:
    - `frontend/src/app/i18n/namespaces.ts`
    - `frontend/src/app/i18n/registry/en.ts`
    - `frontend/src/app/i18n/registry/ja.ts`
- Added reusable UI guardrail components:
    - `frontend/src/app/components/ScreenStatusBadge.tsx`
    - `frontend/src/app/components/MockWarningBanner.tsx`
    - exported via `frontend/src/app/components/index.ts`

### Screens Updated

- Mock warning banner inserted on mock-backed pages:
    - `frontend/src/app/pages/QCCheckpoints.tsx`
    - `frontend/src/app/pages/DefectManagement.tsx`
    - `frontend/src/app/pages/Traceability.tsx`
    - `frontend/src/app/pages/DispatchQueue.tsx`
    - `frontend/src/app/pages/APSScheduling.tsx`
    - `frontend/src/app/pages/OEEDeepDive.tsx` (includes AI fixture note)
- Partial/deprecation warning inserted on station compatibility path:
    - `frontend/src/app/pages/StationExecution.tsx` (MODE A)
- Tab-level mock badges added on placeholder tabs:
    - `frontend/src/app/pages/OperationExecutionDetail.tsx` (`quality`, `materials`, `timeline`, `documents`)

### Guardrail Outcome

- Backend truth was not altered.
- No new backend/API integrations were introduced.
- Existing route structure and app shell were preserved.
- i18n parity maintained for new keys (en/ja).
- Guardrails now make mock/partial/shell/future status explicit in UI.

## FE-1 Build Verification

### Runtime Tooling

- Node: unavailable in current automation shell (`node --version` -> `CommandNotFoundException`)
- npm: unavailable in current automation shell (`npm --version` -> `CommandNotFoundException`)
- Command path:
    - `Get-Command node` -> not found
    - `Get-Command npm` -> not found
    - `where node` / `where npm` -> no matches

### Commands Run

From repo root (`G:\Work\FleziBCG`):

1. `node --version`
2. `npm --version`
3. `Get-Command node`
4. `Get-Command npm`
5. `where.exe node ; where.exe npm`

Frontend package context checks:

1. `frontend/package.json` inspected (build script = `vite build`)
2. `frontend/` contents inspected; `node_modules/` not present in current workspace view

### Build Result

BLOCKED

`npm run build` could not be executed because npm is unavailable in the current shell environment.

### Errors Found

Classification: `F. Environment/tooling issue`

- Tooling resolution failure in active shell PATH prevents dependency install and build execution.
- No FE-1 TypeScript diagnostics were reported by editor diagnostics on changed files.

### Fixes Applied

- No code fix applied for FE-1 logic/components (not required; build did not reach compile stage).
- Report metadata and verification evidence updated in this document.

### Remaining Risks

- FE-1 build status is not yet proven by actual Vite build output.
- Since `node_modules` is not present in current workspace view, dependency install still needs to run once npm is accessible.

### Can Proceed to FE-2?

No.

Proceed only after:

1. Node and npm are available in the same VS Code terminal environment used for verification.
2. `cd frontend && npm install` completes successfully.
3. `cd frontend && npm run build` passes.

## FE-2 Route/Page Status Integration

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Files Changed

- `frontend/src/app/screenStatus.ts`
- `frontend/src/app/components/RouteStatusBanner.tsx` (new)
- `frontend/src/app/components/Layout.tsx`
- `frontend/src/app/components/index.ts`
- `frontend/src/app/pages/QCCheckpoints.tsx`
- `frontend/src/app/pages/DefectManagement.tsx`
- `frontend/src/app/pages/Traceability.tsx`
- `frontend/src/app/pages/DispatchQueue.tsx`
- `frontend/src/app/pages/APSScheduling.tsx`

### Shell/Layout Integration Approach

- Added route-aware status integration component `RouteStatusBanner` in the shared app shell.
- `RouteStatusBanner` reads `location.pathname`, resolves it via `screenStatus` helpers, and renders:
    - a route-level `ScreenStatusBadge` on every screen (including `CONNECTED` and `UNKNOWN`), and
    - a route-level `MockWarningBanner` for mock/partial/future-like phases.
- Added lightweight helpers in `screenStatus.ts`:
    - `getScreenStatusMatchByRoute(pathname)`
    - `getScreenStatusByRoute(pathname)`
    - `getScreenStatusByScreenId(screenId)`
    - `isMockLikeStatus(phase)`
    - `isFutureLikeStatus(phase)`
- Added route alias normalization for `/station-execution` -> `/station`.

### Screens Covered Automatically

- QCCheckpoints (`/quality`)
- DefectManagement (`/defects`)
- Traceability (`/traceability`)
- DispatchQueue (`/dispatch`)
- APSScheduling (`/scheduling`)
- OEEDeepDive (`/performance/oee-deep-dive`)
- StationExecution (`/station`, `/station-execution`)
- OperationExecutionDetail (`/operations/:operationId/detail`)

### Duplicate Banner Handling

- Removed duplicate per-page generic mock banners from:
    - QCCheckpoints
    - DefectManagement
    - Traceability
    - DispatchQueue
    - APSScheduling
- Preserved special section-level warnings:
    - OEE static AI fixture note remains local to OEE page.
    - StationExecution compatibility/deprecation note remains local to StationExecution.
    - OperationExecutionDetail tab-level mock labels remain intact.
- Suppressed global route-level warning banner for `oeeDeepDive` and `stationExecution` to avoid duplicate warning blocks while still showing route-level badge.

### Build Result

- Baseline before FE-2 changes: `cd frontend && npm.cmd run build` -> PASS
- After FE-2 changes: `cd frontend && npm.cmd run build` -> PASS
- Additional check: `cd frontend && npm.cmd run lint` -> PASS

### Remaining Risks

- Route-level status is intentionally a UI maturity label and must not be used as permission/execution/quality truth.
- Vite chunk-size warning remains (`>500kB`), unchanged by this slice.

### Can Proceed to FE-3?

Yes.

## FE-3 Product/Routing UI Shell Readiness

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Files Changed

- `frontend/src/app/routes.tsx`
- `frontend/src/app/screenStatus.ts`
- `frontend/src/app/components/Layout.tsx`
- `frontend/src/app/pages/ProductList.tsx` (new)
- `frontend/src/app/pages/ProductDetail.tsx` (new)
- `frontend/src/app/pages/RouteList.tsx`
- `frontend/src/app/pages/RouteDetail.tsx`
- `frontend/src/app/i18n/namespaces.ts`
- `frontend/src/app/i18n/registry/en.ts`
- `frontend/src/app/i18n/registry/ja.ts`

### Screens Added / Aligned

- Added product shell routes and pages:
    - `/products` -> `ProductList`
    - `/products/:productId` -> `ProductDetail`
- Kept existing routing screens:
    - `/routes` -> `RouteList`
    - `/routes/:routeId` -> `RouteDetail`
- Added explicit backend-required notice labeling on routing screens to avoid implying connected mutating behavior.

### Data Source Status

- `Product List` -> `SHELL` (`NONE`)
- `Product Detail` -> `SHELL` (`NONE`)
- `Routing List` (`RouteList`) -> `MOCK` (`MOCK_FIXTURE`)
- `Routing Detail` (`RouteDetail`) -> `MOCK` (`MOCK_FIXTURE`)

Classification rule applied:

- `CONNECTED` only when real API client exists and screen uses it.
- Current frontend has no `product`/`routing` API clients under `frontend/src/app/api`.

### Backend Dependency

- Product UI shells depend on frontend integration to Product Foundation backend API before enabling real lifecycle actions.
- Routing UI remains mock until routing API client integration is implemented.

### Build/Lint Result

- `cd frontend && npm.cmd run build` -> PASS
- `cd frontend && npm.cmd run lint` -> PASS

### Remaining Risks

- Routing pages still use fixture/mock data and local-only interactions.
- Product screens are intentionally non-functional shells and must not be interpreted as lifecycle implementation complete.
- UI status labels remain maturity indicators only, not authorization/execution/quality truth.

### Can Proceed to FE-4?

Yes, if next slice is API-client integration with explicit backend contract verification.

## FE-4A Product Read API Connection

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Files Changed

- `frontend/src/app/api/productApi.ts` (new)
- `frontend/src/app/api/index.ts`
- `frontend/src/app/pages/ProductList.tsx`
- `frontend/src/app/pages/ProductDetail.tsx`
- `frontend/src/app/screenStatus.ts`
- `frontend/src/app/i18n/registry/en.ts`
- `frontend/src/app/i18n/registry/ja.ts`

### Backend API Shape Verified From

- `backend/app/api/v1/products.py`
- `backend/app/schemas/product.py`

Endpoints used by FE-4A:

- `GET /v1/products`
- `GET /v1/products/{product_id}`

### Product Data Source Status

- `Product List` (`/products`) -> `PARTIAL` / `BACKEND_API`
- `Product Detail` (`/products/:productId`) -> `PARTIAL` / `BACKEND_API`

Implemented behavior:

- Product List now loads from backend via `productApi.listProducts()`.
- Product Detail now loads from backend via `productApi.getProduct(productId)`.
- Both screens include explicit loading/error states; Product Detail includes not-found state handling.

### Lifecycle Action Status

- Product lifecycle mutation actions remain disabled by design in FE-4A.
- No create/release/retire API mutation wiring was added.

### Build/Lint Result

- `cd frontend && npm.cmd run build` -> PASS
- `cd frontend && npm.cmd run lint` -> PASS

### Remaining Risks

- Product pages are read-connected but still action-incomplete; do not treat as full product lifecycle implementation.
- Route/routing pages remain mock-backed and are not part of FE-4A.

### Can Proceed to FE-4B?

Yes, for product lifecycle write-action integration after explicit backend contract and authorization flow verification.

## FE-4A.1 Product Read Smoke / UX Hardening

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Files Changed

- `frontend/src/app/components/ProductBadges.tsx` (new)
- `frontend/src/app/components/index.ts`
- `frontend/src/app/pages/ProductList.tsx`
- `frontend/src/app/pages/ProductDetail.tsx`
- `frontend/src/app/i18n/registry/en.ts`
- `frontend/src/app/i18n/registry/ja.ts`

### Read States Verified

- Loading: Product List and Product Detail both render explicit loading state messages.
- Empty list: Product List renders a clear empty state (`No products found`).
- API error: Both pages show backend error detail when present, with localized fallback.
- Not found detail: Product Detail maps HTTP 404 to explicit not-found state.
- Missing productId: Product Detail shows explicit route-parameter-missing state.
- Unauthorized/forbidden: Product List and Product Detail map HTTP 401/403 to dedicated localized messages.

### Lifecycle Actions Status

- Product lifecycle actions remain disabled and backend-required by design.
- No release/retire/create mutation wiring was added.
- No local fake success/state mutation behavior was added for lifecycle actions.

### Build/Lint Result

- `cd frontend && npm.cmd run build` -> PASS
- `cd frontend && npm.cmd run lint` -> PASS

### Remaining Risks

- Product read UX is hardened, but write/lifecycle actions are still intentionally unimplemented.
- Routing domain remains mock-backed and is out of FE-4A.1 scope.
- Screen status remains `PARTIAL` until write-path and authorization-complete lifecycle coverage are delivered.

## FE-4A.2 Product Route Accessibility Fix

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Root Cause

- Product routes were already registered in `frontend/src/app/routes.tsx`.
- Access still failed because `frontend/src/app/persona/personaLanding.ts` route-gating did not include `/products` or `/products/:productId`.
- In `Layout`, `isRouteAllowedForPersona(...)` redirected users to persona landing when route was not allowed.

### Actual Route Path

- Product List: `/products`
- Product Detail: `/products/:productId`

### Files Changed

- `frontend/src/app/persona/personaLanding.ts`
- `docs/audit/frontend-source-alignment-snapshot.md`

### Sidebar/Menu Placement

- Added `Products` sidebar entry (UX navigation only) for personas that already manage adjacent production master data paths:
    - `SUP`, `IEP`, `QC`, `PMG`

### Auth / Redirect Behavior

- Route remains under `RequireAuth` and still requires authenticated session.
- Persona enforcement remains active; only allowlist was aligned with existing product routes.
- No auth bypass and no backend authorization changes were introduced.

### Build/Lint Result

- `cd frontend && npm.cmd run build` -> PASS
- `cd frontend && npm.cmd run lint` -> PASS

### Manual Verification Note

- Verified by route configuration + persona allowlist inspection that authenticated `SUP/IEP/QC/PMG` users can now navigate to `/products` without forced landing redirect.
- Product Detail route `/products/:productId` remains reachable and safely handles not-found/missing-id states from FE-4A.1.

## FE Route Accessibility Prevention Gate

Date: 2026-04-29  
Track: PARALLEL LIGHT FE governance/hardening

### Root Cause of `/products` Issue

- Route registration existed in `frontend/src/app/routes.tsx`.
- Layout-level persona enforcement in `frontend/src/app/components/Layout.tsx` redirected to persona landing when `isRouteAllowedForPersona(...)` returned false.
- Persona allowlist in `frontend/src/app/persona/personaLanding.ts` was not updated for `/products` and `/products/:productId`, causing access failure despite green build/lint.

### New Acceptance Rule

For all FE route/page additions and changes, build/lint is mandatory but not sufficient. Route Accessibility Gate must pass before the slice is considered complete.

Required checks:

1. Route registered in router tree.
2. Route nested under correct layout boundary.
3. No index/catch-all/fallback swallow behavior.
4. Auth guard behavior validated.
5. Persona allowlist updated when persona routing exists.
6. Sidebar/menu UX entry aligned for user-accessible screens.
7. `screenStatus` route entry aligned.
8. Direct URL smoke check completed (list/detail as applicable).

### Persona Allowlist Requirement

- Persona remains UX routing policy only and must not replace backend authorization truth.
- If frontend persona allowlists are present, new routes must update the persona accessibility matrix.
- If a route is intentionally hidden for a persona, rationale must be documented.
- If a route is registered but not in sidebar, classify it as internal/detail-only in task report.

### Manual Smoke Checklist

- Login state verified (unauthenticated -> expected auth redirect).
- Authenticated direct URL to list route.
- Authenticated direct URL to detail route with safe placeholder/id.
- Persona redirect behavior validated for at least one allowed and one disallowed persona.
- Sidebar/menu navigation reaches same route path as direct URL.
- Route-level status labeling (`screenStatus`) appears for the new path.

### Future FE Slice Checklist

- Include "Route Accessibility Verification" block in final FE report.
- Explicitly report route path, layout nesting, auth behavior, persona allowlist update, sidebar/menu update, `screenStatus` update, and direct URL checks.
- Do not close route/page slices as done with build/lint only.

## FE-GOV-02 Automated Route Smoke Script

Date: 2026-04-29  
Track: PARALLEL LIGHT FE governance/hardening

### Files Changed

- `frontend/scripts/route-smoke-check.mjs` (new)
- `frontend/package.json`
- `docs/audit/frontend-source-alignment-snapshot.md`

### Checks Added

- Required route registration check in router tree:
    - `/products`
    - `/products/:productId`
    - `/routes`
    - `/routes/:routeId`
- Required `screenStatus.routePattern` presence for the same routes.
- Persona enforcement presence check in Layout (`menu + allowlist + redirect` hooks).
- Persona allowlist route-guard checks for user-accessible list routes (`/products`, `/routes`).
- Persona access-function coverage checks for expected personas (`SUP`, `IEP`, `QC`, `PMG`).
- Sidebar/menu route entry checks for expected personas on list routes.
- Documented internal-only detail-route exceptions for:
    - `/products/:productId`
    - `/routes/:routeId`
- Basic catch-all risk check (`path: "*"`) in router file.

### Command

- `cd frontend && npm.cmd run check:routes`

### Result

- Route smoke summary: `PASS 24 / FAIL 0`
- Build: PASS (`npm.cmd run build`)
- Lint: PASS (`npm.cmd run lint`)

### Known Limitations

- Static consistency checks only; no browser/runtime navigation automation.
- Script currently validates selected critical routes and expected personas, not full route matrix coverage.
- Internal-only detail-route exceptions are script-documented and should stay aligned with design intent over time.

### CI-Blocking Recommendation

- Recommendation: enable as non-blocking CI signal first, then promote to blocking after one stabilization cycle.
- Rationale: low-cost guardrail with high value for preventing router/persona/menu drift regressions.

## FE-GOV-02.1 Route Smoke CI Signal

Date: 2026-04-29  
Track: PARALLEL LIGHT FE governance/hardening

### Workflow File Changed

- `.github/workflows/pr-gate.yml`

### Blocking Status

- Non-blocking signal (`continue-on-error: true`)

### Command Added

- `npm run check:routes --if-present`

Added as step: `Route smoke check (non-blocking signal)` in the existing frontend PR gate job after lint/typecheck/test.

### Promotion Rule

- Workflow includes TODO: promote route smoke to blocking after one stabilization cycle.
- Promotion should occur only after observing stable green route-smoke runs across representative FE PRs.

### Risks

- Non-blocking mode may allow regressions to merge if warnings are ignored.
- Current smoke scope is intentionally lightweight and route-focused, not full runtime navigation.
- Signal depends on reviewer discipline during stabilization period.

## FE-5 Routing Read API Connection

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Scope

- Frontend-only read integration for routing list/detail.
- No backend, DB, migration, or API contract changes.
- No routing create/update/release/retire execution in UI.

### Files Changed

- `frontend/src/app/api/routingApi.ts`
- `frontend/src/app/api/index.ts`
- `frontend/src/app/pages/RouteList.tsx`
- `frontend/src/app/pages/RouteDetail.tsx`
- `frontend/src/app/i18n/registry/en.ts`
- `frontend/src/app/i18n/registry/ja.ts`
- `frontend/src/app/screenStatus.ts`
- `docs/audit/frontend-source-alignment-snapshot.md`

### Endpoints Used by FE-5

- `GET /api/v1/routings`
- `GET /api/v1/routings/{routing_id}`

Frontend API wrapper calls through:

- `routingApi.listRoutings()` -> `/v1/routings`
- `routingApi.getRouting(routingId)` -> `/v1/routings/{routingId}`

### UX Behavior Added

- Route List now loads backend routing rows with loading, empty, retry, and 401/403-aware error states.
- Route Detail now loads backend routing header + operations with loading, missing-id, not-found, retry, and 401/403-aware error states.
- Mutation/lifecycle actions are explicitly non-operational in FE-5 (read-only slice).

### Screen Status Reclassification

- `/routes`: `MOCK` -> `PARTIAL`, data source `BACKEND_API`.
- `/routes/:routeId`: `MOCK` -> `PARTIAL`, data source `BACKEND_API`.

### Verification Results

- `cd frontend && npm.cmd run build` -> PASS
- `cd frontend && npm.cmd run lint` -> PASS
- `cd frontend && npm.cmd run check:routes` -> PASS (`PASS 24 / FAIL 0`)

### Risks / Deferred Work

- FE-5 intentionally excludes routing write flows (create/update/release/retire).
- Status badges currently render backend lifecycle values directly; localization/mapping refinement can be added later if required.
- Route smoke gate remains non-blocking in CI until stabilization promotion.

## FE-5.1 Routing Read Smoke / UX Hardening

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Files Changed

- `frontend/src/app/components/RoutingDisplay.tsx` (new)
- `frontend/src/app/components/index.ts`
- `frontend/src/app/pages/RouteList.tsx`
- `frontend/src/app/pages/RouteDetail.tsx`
- `docs/audit/frontend-source-alignment-snapshot.md`

### Read States Verified

- Loading: Route List and Route Detail both render explicit loading states.
- Empty list: Route List renders explicit empty state when no routings match/return.
- API error: both screens surface backend error detail when available with localized fallback.
- Not found detail: Route Detail maps HTTP 404 to explicit not-found state.
- Missing routingId: Route Detail renders explicit missing-id state.
- Unauthorized/forbidden: Route List and Route Detail map HTTP 401/403 to dedicated localized messages.
- Retry: both screens include retry action that re-executes read requests.

### Lifecycle Actions Status

- Routing lifecycle/mutation behavior remains read-only in FE-5.1.
- Route Detail save action remains disabled and labeled backend-required.
- No create/update/release/retire action wiring was added.
- No local state mutation simulating lifecycle success was added.

### Build/Lint/Route Smoke Result

- `docker run --rm -v "G:\Work\FleziBCG\frontend:/app" -w /app node:20-bookworm bash -lc "npm install && npm run build && npm run lint && npm run check:routes"` → **PASS**

### Docker-Based Verification (2026-04-29)

**Environment**: Docker node:20-bookworm container with mounted frontend folder.

**npm install**
- ✅ PASS: added 7 packages, audited 424 packages in 5s
- 2 vulnerabilities (1 moderate, 1 high) — pre-existing, not FE-5.1-related
- npm version: 10.8.2 (newer 11.13.0 available)

**npm run build**
- ✅ PASS: Vite build completed in 1m 4s
- 3340 modules transformed
- Output files: index.html (0.44 kB), CSS (131.62 kB), JS (1,319.01 kB)
- Warning: Some chunks larger than 500 kB after minification (non-blocking, typical for this app size)

**npm run lint**
- ✅ PASS: eslint src/ ran without errors

**npm run check:routes**
- ✅ PASS: 24/24 route smoke checks passed, 0 failures
  - All routing, persona guards, sidebar menu entries, and detail route documentation verified
  - All required routes (/products, /products/:productId, /routes, /routes/:routeId) registered
  - Persona access functions correct for SUP, IEP, QC, PMG
  - No wildcard catch-all detected
  - Layout persona enforcement hooks present

**Files Generated**
- frontend/node_modules/ (created by npm install)
- frontend/dist/ (created by vite build)
- No manual code errors requiring fixes

**Package Lock**
- package-lock.json was modified during npm install (expected version metadata changes)

**Verdict**: **PASS** — All four verification commands executed successfully in Docker. FE-5.1 code is build/lint/route-smoke clean.

### Remaining Risks

- Routing remains PARTIAL because lifecycle/mutation backend integration is intentionally not implemented.
- Read-state UX is hardened, but contract-level write/action authorization flows remain deferred by design.
- Route smoke remains non-blocking in CI until governance promotion.

## FE-GOV-03 Ignore Rules Hardening

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Files Changed

- `.gitignore`
- `frontend/.dockerignore`
- `docs/audit/frontend-source-alignment-snapshot.md`

### Rules Added / Verified

**Root `.gitignore`**
- Added/verified frontend artifact coverage: `node_modules/`, `frontend/node_modules/`, `frontend/.vite/`, `frontend/.turbo/`, `frontend/coverage/`.
- Added frontend/local cache coverage: `frontend/.eslintcache`, `frontend/.stylelintcache`.
- Added npm/yarn/pnpm debug log patterns.
- Added local env override coverage: `.env.local`, `.env.*.local`, `frontend/.env.local`, `frontend/.env.*.local`.
- Removed `package-lock.json` ignore rule to avoid suppressing lockfile changes.

**`.dockerignore` strategy**
- Root `.dockerignore` was not created because Docker build contexts are `./frontend` and `./backend` (repo root is not used as build context in current compose setup).
- Hardened `frontend/.dockerignore` for local/editor/cache/log artifacts.
- Added explicit allow for `frontend/.env.example` using `!.env.example`.

### Generated Artifacts Covered

- `frontend/node_modules`: covered by `.gitignore` and `frontend/.dockerignore`.
- `frontend/dist`: covered by `.gitignore` and `frontend/.dockerignore` patterns, but tracked-file exception applies.
- `frontend/.vite`: covered by `.gitignore` and `frontend/.dockerignore`.
- `frontend/coverage`: covered by `.gitignore` and `frontend/.dockerignore`.
- logs/cache: npm/yarn/pnpm debug logs, `.eslintcache`, `.stylelintcache`, `.turbo` covered.

### Tracked Artifact Findings

- `frontend/node_modules` tracked: **No**.
    - Validation: `git check-ignore -v frontend/node_modules` -> `.gitignore` rule matched.
- `frontend/dist` tracked: **Yes**.
    - Validation: `git ls-files frontend/node_modules frontend/dist` returned `frontend/dist/index.html`.
    - `git check-ignore -v frontend/dist` did not report ignore match in current tracked-file status checks.
- `package-lock` changed: **Yes** (`frontend/package-lock.json` diff present from Docker npm metadata churn).

### Docker Build Context Risk Check

- Dockerfile inspected: `frontend/Dockerfile`.
- `frontend/dist` required from host build context: **No**.
    - Frontend image builds `dist` inside the Docker build stage and copies from `/app/dist` in-stage.
- Current risk: tracked `frontend/dist/index.html` can still appear in Git changes and should be handled by repository policy.

### Human Decisions Needed

1. Decide whether `frontend/dist` should remain intentionally tracked.
2. If not intentional, de-track `frontend/dist` in a separate cleanup PR (no destructive git commands were run in this slice).
3. Decide whether to keep or revert current `frontend/package-lock.json` metadata churn from Docker npm run.

## FE-GOV-03.1 Tracked Artifact Cleanup

Date: 2026-04-29  
Track: PARALLEL LIGHT FE

### Scope

- De-track `frontend/dist` from Git index only (local files preserved).
- Revert `frontend/package-lock.json` metadata churn only.
- Keep `frontend/package-lock.json` tracked and not ignored.
- No backend/database/API contract changes.

### Commands Run

- `git status --short`
- `git ls-files frontend/dist`
- `git diff -- frontend/package-lock.json`
- `git diff -- frontend/package.json`
- `git rm --cached -r frontend/dist`
- `git status --short frontend/dist`
- `git check-ignore -v frontend/dist`
- `git ls-files frontend/dist`
- `git restore frontend/package-lock.json`
- `git diff -- frontend/package-lock.json`
- `git status --short frontend/package-lock.json`
- `git check-ignore -v frontend/package-lock.json`

### Results

- `frontend/dist` de-tracked from Git index: **Yes**.
    - Evidence: `git rm --cached -r frontend/dist` removed `frontend/dist/index.html` from index.
    - Evidence: `git ls-files frontend/dist` returned no tracked files after cleanup.
- `frontend/dist` remains local build output: **Yes** (no local file deletion command executed).
- `frontend/dist` ignored going forward: **Yes** via `.gitignore` rule `frontend/dist/`.

- `frontend/package-lock.json` churn reverted: **Yes**.
    - Evidence: `git diff -- frontend/package-lock.json` returned no diff after restore.
- `frontend/package-lock.json` remains tracked: **Yes**.
    - Evidence: no ignore match from `git check-ignore -v frontend/package-lock.json`.

- `frontend/package.json` unchanged in dependencies: **Yes**.
    - Current diff is script-level only (`check:routes`), no dependency version mutation.

### Remaining Risks

- Workspace remains broadly dirty outside FE-GOV-03.1; commit staging must stay slice-focused.
- `frontend/package.json` still has pending script changes from other FE governance slices; ensure lockfile policy is reviewed when those are committed.

### Recommended Commit Split

1. FE-GOV-03/03.1 hygiene only:
     - `.gitignore`
     - `frontend/.dockerignore`
     - `docs/audit/frontend-source-alignment-snapshot.md`
     - staged delete from index for tracked `frontend/dist/index.html`
2. FE feature/source slices (routing/product/UI) in separate commits.
3. Backend/domain slices in separate commits.

*End of Frontend Source Alignment Snapshot v1.17 — 2026-04-29*
