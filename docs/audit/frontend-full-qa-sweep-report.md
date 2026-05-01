# Full Frontend Route / Responsive / Accessibility Sweep Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Created full frontend QA sweep after broad screen coverage expansion (FE-COVERAGE-01A through 01F, FE-NAV-01, FE-NAV-01B, FE-NAV-03, FE-QA-ROUTES-01). |

---

## Routing

- **Selected brain:** FleziBCG AI Brain Enterprise v4
- **Selected mode:** FE QA Sweep — Safe Fixes Only
- **Hard Mode MOM:** Read and boundary-checked; no Hard Mode contract intervention required.
- **Reason:** This is a QA/audit/small-fix task. No backend/API/auth/execution/persona behavior changed.

---

## 1. Scope

Full sweep of all frontend routes, pages, navigation, sidebar, disclosures, and dangerous actions after FE-COVERAGE-01A–01F, FE-NAV-01, FE-NAV-01B, FE-NAV-03, FE-QA-ROUTES-01.

The app has **78 registered routes** across 15 MOM domains.

---

## 2. Source Files Inspected

| File | Purpose |
|---|---|
| `frontend/src/app/routes.tsx` | Route registry |
| `frontend/src/app/components/Layout.tsx` | App shell, sidebar, GROUP_ICONS, getIconForPath |
| `frontend/src/app/components/TopBar.tsx` | Mobile menu, header |
| `frontend/src/app/components/SidebarSearch.tsx` | Sidebar quick search |
| `frontend/src/app/components/RouteStatusBanner.tsx` | Auto-disclosure banner for MOCK/SHELL/PARTIAL routes |
| `frontend/src/app/components/MockWarningBanner.tsx` | Warning banner component |
| `frontend/src/app/navigation/navigationGroups.ts` | Sidebar group/prefix mapping |
| `frontend/src/app/persona/personaLanding.ts` | Persona menu + route guards |
| `frontend/src/app/screenStatus.ts` | Screen phase/datasource registry |
| `frontend/src/app/pages/` (76 files) | All page files swept |
| `frontend/src/app/i18n/registry/en.ts` | English i18n keys |
| `frontend/src/app/i18n/registry/ja.ts` | Japanese i18n keys |
| `frontend/scripts/route-smoke-check.mjs` | Route smoke script |

---

## 3. Precondition Check

| Check | Result | Notes |
|---|---|---|
| `git status --short` — no conflict markers | PASS | Unrelated modified files: 6 station-execution files (p0-c-08h2 ongoing work), 3 docs/implementation files, 2 screenshots — not touched |
| Route registry readable | PASS | 78 routes, `routes.tsx` healthy |
| Navigation group file readable | PASS | 12 groups in NAV_GROUPS |
| Screen status registry readable | PASS | All 78 routes registered |
| All required audit reports present | PASS | FE-COVERAGE-01A–01F, FE-NAV-01/01B/03 reports present |
| Baseline build | PASS | Built in ~7.7s |
| Baseline lint | PASS | 0 errors |
| Baseline check:routes | PASS | 78 routes, 0 fail |
| Baseline lint:i18n:registry | PASS | 1692 keys, en/ja parity |

---

## 4. Route Registry / Smoke Coverage Review

| Domain | Routes | Smoke Result | Notes |
|---|---|---|---|
| Home / Dashboard | `/home`, `/dashboard` | PASS | Both covered |
| Core Operations | `/production-orders`, `/work-orders`, `/operations`, `/dispatch`, `/station`, `/station-session`, `/operator-identification`, `/equipment-binding`, `/line-monitor`, `/station-monitor`, `/shift-summary`, `/supervisory`, `/station-execution`, `/scheduling` | PASS | All covered |
| Mfg Master Data | `/products`, `/products/:productId`, `/routes`, `/routes/:routeId`, `/bom`, `/bom/:bomId`, `/routing-operations/:opId`, `/resource-requirements`, `/reason-codes` | PASS | Dynamic routes have sample docs |
| Quality | `/quality`, `/defects`, `/quality-dashboard`, `/quality-measurements`, `/quality-holds` | PASS | All covered |
| Material / WIP | `/material-readiness`, `/staging-kitting`, `/wip-buffers` | PASS | All covered |
| Traceability | `/traceability` | PASS | Covered |
| Planning | `/scheduling` | PASS | Covered |
| Reporting & Analytics | `/performance/oee-deep-dive`, `/reports/downtime`, `/reports/production-performance`, `/reports/quality-performance`, `/reports/shift`, `/reports/material-wip`, `/reports/integration-status`, `/ai/insights`, `/ai/shift-summary`, `/ai/anomaly-detection`, `/ai/bottleneck-explanation`, `/ai/natural-language-insight` | PASS | AI routes now under Reporting (FE-NAV-03) |
| Integration | `/integration`, `/integration/systems`, `/integration/erp-mapping`, `/integration/inbound`, `/integration/outbound`, `/integration/posting-requests`, `/integration/reconciliation`, `/integration/retry-queue` | PASS | All covered |
| Digital Twin | `/digital-twin`, `/digital-twin/state-graph`, `/digital-twin/what-if` | PASS | All covered |
| Compliance | `/compliance/record-package`, `/compliance/e-signature`, `/compliance/electronic-batch-record` | PASS | All covered |
| Governance & Admin | `/users`, `/roles`, `/action-registry`, `/scope-assignments`, `/sessions`, `/audit-log`, `/security-events`, `/tenant-settings`, `/plant-hierarchy` | PASS | All covered |

**Total: 78 routes registered, 0 FAIL**

---

## 5. Navigation / Sidebar Review

| Check | Result | Notes |
|---|---|---|
| Grouped sidebar groups render | PASS | 12 groups: Home, Core Operations, Mfg Master Data, Quality, Material/WIP, Traceability, Reporting & Analytics, Integration, Planning & Scheduling, Digital Twin, Compliance, Governance & Admin |
| No "Future / To-Be" catch-all group | PASS | No such group exists |
| AI routes under Reporting & Analytics | PASS | Merged in FE-NAV-03; `/ai` prefix in `reporting-analytics.routePrefixes` |
| Digital Twin as separate group | PASS | `digital-twin` group present |
| Compliance as separate group | PASS | `compliance` group present |
| `ai-intelligence` group removed | PASS | No such group in `NAV_GROUPS` |
| Active route auto-opens correct group | PASS | `useEffect` watches `location.pathname`, calls `getGroupIdForPath` |
| GROUP_ICONS — `integration` entry | **FIX APPLIED** | Was missing → falling back to `Layers`. Added `Server` icon. |
| GROUP_ICONS — `digital-twin` entry | **FIX APPLIED** | Was missing → falling back to `Layers`. Added `Cpu` icon. |
| GROUP_ICONS — `compliance` entry | **FIX APPLIED** | Was missing → falling back to `Layers`. Added `Shield` icon. |
| getIconForPath — `/ai/*` routes | **FIX APPLIED** | Was defaulting to `PlayCircle`. Added `TrendingUp`. |
| getIconForPath — `/integration/*` routes | **FIX APPLIED** | Was defaulting to `PlayCircle`. Added `Server`. |
| getIconForPath — `/digital-twin/*` routes | **FIX APPLIED** | Was defaulting to `PlayCircle`. Added `Cpu`. |
| getIconForPath — `/compliance/*` routes | **FIX APPLIED** | Was defaulting to `PlayCircle`. Added `Shield`. |
| Sidebar search works with AI routes | PASS | Search uses route path prefix matching; group prefix changed not path |
| Compact sidebar mode (icon-only) | PASS | renderCompactMenuItems uses same getIconForPath; now fixed |
| Mobile drawer grouping | PASS | renderGroupedMenuItems used in both desktop and mobile |
| PHASE badges in sidebar | PASS | SHELL/MOCK/TBD badges shown for non-CONNECTED pages |

---

## 6. Responsive Review

Static code review was performed. Screenshot harness (`npm run qa:station-execution:screenshots`) exists and covers Station Execution at 4 viewports; deferred as it requires a running dev server and targets that specific page.

| Viewport | Result | Issues Found | Fixes Applied / Deferred |
|---|---|---|---|
| 1440 × 900 | PASS (code review) | No overflow issues in app shell found | None needed |
| 1180 × 820 | PASS (code review) | No new overflow patterns introduced | None needed |
| 820 × 1180 (tablet portrait) | PASS (code review) | Layout uses `hidden lg:flex` for sidebar; mobile drawer used on mobile | None needed |
| 430 × 932 (mobile) | PASS (code review) | Mobile drawer uses `w-[min(20rem,85vw)]` for safe width | None needed |

**Layout observations:**
- Sidebar: `w-72` expanded / `w-20` collapsed, `hidden lg:flex` — correct
- Mobile drawer: `role="dialog" aria-modal="true"`, keyboard trap implemented, focus returns to menu button on close
- Content area: `min-w-0 flex-1 overflow-auto` — prevents horizontal overflow bleed
- Shell pages use `overflow-auto` containers for long content — no horizontal overflow risk identified

---

## 7. Accessibility Review

| Area | Result | Notes |
|---|---|---|
| Sidebar group headers (`aria-expanded`) | PASS | `aria-expanded={isOpen}` present on every group button |
| Sidebar group toggle keyboard | PASS | `focus-visible:outline` ring on all toggle buttons |
| Sidebar search input | PASS | `ariaLabel` prop passed via i18n key; `SidebarSearch` renders `aria-label` |
| Sidebar search clear button | PASS | `clearLabel` i18n key used as `aria-label` on clear button |
| Mobile drawer open | PASS | `aria-label="Close navigation drawer"` on backdrop and close button |
| Mobile drawer keyboard trap | PASS | `handleDrawerTab` useEffect implements Tab/Shift+Tab trap within `drawerRef` |
| Mobile drawer close focus | PASS | Focus returns to `menuButtonRef` on close |
| TopBar mobile menu button | PASS | `aria-label` present; `aria-expanded` reflects drawer state |
| Nav links keyboard navigation | PASS | `focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500` on all Link items |
| Disabled shell action buttons | PASS | All dangerous actions use `disabled` attribute + `title` tooltip |
| Compact sidebar icon-only links | PASS | `title={item.label}` on every compact Link for screen readers and hover |
| PHASE badges in sidebar | PASS | SHELL/MOCK/TBD badges are decorative; not sole indicator |
| Shell pages heading structure | PASS | All new shell pages use `<h1>` for page title |
| Focus ring visibility | PASS | `focus-visible:outline-blue-500` used consistently throughout Layout |

**Note:** Deep per-page keyboard tab order was not tested in-browser. This is deferred to FE-QA-03 when a full Playwright accessibility run is available.

---

## 8. Disclosure / Truth Boundary Review

**Auto-disclosure system:** `RouteStatusBanner` in `Layout.tsx` reads `SCREEN_STATUS_REGISTRY` and auto-renders `MockWarningBanner` for every route with `MOCK`, `SHELL`, `PARTIAL`, or `FUTURE` phase — unless the screen ID is in `BANNER_SUPPRESSED_SCREEN_IDS`. This means **pages do NOT need inline banners** to get disclosure — the layout handles it globally.

Pages with *additionally* inline `MockWarningBanner` have belt-and-suspenders disclosure inside their scrollable content area.

| Domain | Screens Reviewed | Disclosure Result | Remaining Risk |
|---|---|---|---|
| Quality / QC | QCCheckpoints, DefectManagement, QualityDashboard, QualityHolds, MeasurementEntry | PASS | All have MockWarningBanner + ScreenStatusBadge; dangerous actions disabled |
| Material / WIP | MaterialReadiness, StagingKitting, WipBuffers | PASS | All have MockWarningBanner + ScreenStatusBadge + BackendRequiredNotice |
| Traceability / Genealogy | Traceability | PASS | MockWarningBanner present; Download disabled; genealogy graph is mock |
| APS / Dispatch | APSScheduling, DispatchQueue | PASS | Both have MockWarningBanner; Optimize disabled; Resequence now disabled (fix applied) |
| Integration | IntegrationDashboard, ExternalSystems, ErpMapping, InboundMessages, OutboundMessages, PostingRequests, Reconciliation, RetryQueue | PASS | All SHELL with BackendRequiredNotice; all dangerous actions disabled |
| Reporting | DowntimeReport, ProductionPerfReport, QualityPerfReport, ShiftReport, MaterialWipReport, IntegrationStatusReport | PASS | All SHELL; Export disabled on all |
| AI / Advisory | AIInsightsDashboard, AIShiftSummary, AnomalyDetection, BottleneckExplanation, NaturalLanguageInsight | PASS | All SHELL; Advisory Only labeled; Apply/Dispatch/Execute disabled |
| Digital Twin | DigitalTwinOverview, TwinStateGraph, WhatIfScenario | PASS | All SHELL; Not Live labeled; Sync/Refresh/Run disabled |
| Compliance / Legal | ComplianceRecordPackage, ESignature, ElectronicBatchRecord | PASS | All SHELL; Red legal disclaimers; all finalize/sign/submit disabled |
| Home | Home | **MEDIUM** | Home is MOCK phase; RouteStatusBanner auto-shows disclosure at top. No in-page banner. `handleLineControl` defined but never called — no active mock operations. |

---

## 9. Dangerous Action Review

| Finding ID | Screen | Action | Risk | Treatment | Status |
|---|---|---|---|---|---|
| DA-01 | DispatchQueue | Resequence button | MEDIUM — MOCK page, active blue button misleading | `disabled` + `cursor-not-allowed` + `title` tooltip | **FIXED** |
| DA-02 | QCCheckpoints | Edit/Delete buttons | LOW — `disabled` with tooltip | Already disabled | OK |
| DA-03 | APSScheduling | Run Optimization, Apply to Queue | MEDIUM — MOCK page | Already `disabled` with Lock icon | OK |
| DA-04 | Traceability | Export/Download | MEDIUM — MOCK page | Already `disabled` | OK |
| DA-05 | All AI screens | Apply Recommendation, Execute, Publish, Dispatch | HIGH — advisory only | Already `disabled` with tooltips | OK |
| DA-06 | All Digital Twin screens | Sync, Refresh, Validate, Run Scenario, Apply Scenario | HIGH — no live state | Already `disabled` with tooltips | OK |
| DA-07 | All Compliance screens | Sign, Approve, Finalize, Submit, Generate | HIGH — legal boundary | Already `disabled` with red legal disclaimers | OK |
| DA-08 | Home | "Start/Pause/Stop Line" | LOW — function defined but **never called from any button** | No onClick wires to handleLineControl in JSX | No fix needed |

---

## 10. i18n Review

| Check | Result | Notes |
|---|---|---|
| `lint:i18n:registry` passes | PASS — 1692 keys, en/ja parity | No keys added or removed by this task |
| New icon-only items in sidebar need accessible labels | PASS | All compact sidebar Links use `title` attribute with `item.label` |
| GROUP_ICONS labels are hardcoded (no i18n) | PASS | Group labels are hardcoded strings in `navigationGroups.ts`; no i18n required |
| Home.tsx in-page text hardcoded | LOW | Several strings like "Production Lines" appear hardcoded; existing convention allows it for mock screens |

---

## 11. Fixes Applied

| # | File | Fix | Reason |
|---|---|---|---|
| 1 | `frontend/src/app/components/Layout.tsx` | Added `"integration": Server`, `"digital-twin": Cpu`, `"compliance": Shield` to `GROUP_ICONS` | Groups rendered with generic `Layers` fallback instead of domain-specific icons |
| 2 | `frontend/src/app/components/Layout.tsx` | Added `getIconForPath` entries for `/ai`, `/integration`, `/digital-twin`, `/compliance` path prefixes | Individual menu items for 22 new routes all defaulted to `PlayCircle` |
| 3 | `frontend/src/app/pages/DispatchQueue.tsx` | Added `disabled` attribute, changed class to `bg-gray-300 text-gray-600 cursor-not-allowed`, added `title` tooltip to Resequence button | Active blue button on MOCK page misleadingly suggested functional resequencing |

**No i18n keys added. No route changes. No auth/persona changes. No backend changes.**

---

## 12. Remaining Issues

| Severity | Issue | Impact | Recommended Follow-up |
|---|---|---|---|
| RESOLVED | `Home.tsx` in-page MockWarningBanner missing | ✓ RouteStatusBanner (layout) covers disclosure automatically; no user impact | ✓ Documented & verified in FE-CLEANUP-01; no fix needed |
| LOW | `Home.tsx` `handleLineControl` dead code (defined but never called) | No functional impact; function is unreachable from UI | Clean up in future maintenance slice |
| RESOLVED | `ProductionTracking.tsx` + `Production.tsx` are orphan files not connected to any route | ✓ Files deleted; build/lint/route-check all PASS | ✓ Cleaned up in FE-CLEANUP-01 |
| LOW | Station execution screenshots not re-run (screenshot harness requires live dev server) | Harness exists (`npm run qa:station-execution:screenshots`); station execution source was modified by separate p0-c-08h2 work | Run screenshot harness after p0-c-08h2 merge; deferred to FE-QA-03 |
| LOW | Deep keyboard tab order testing not performed in-browser | Code review shows correct `focus-visible` rings and `aria` attributes; actual tab order requires Playwright run | Deferred to FE-QA-03 with Playwright accessibility sweep |
| LOW | Responsive screenshot coverage limited to Station Execution | Other domains not yet screenshot-tested at 4 viewports | Expand screenshot harness in future QA slice |
| NONE | All SHELL/MOCK/FUTURE disclosure: complete | RouteStatusBanner covers all non-connected phases automatically | No action needed |
| NONE | All dangerous AI/Twin/Compliance actions: disabled | Verified across all 11 FE-COVERAGE-01F shell pages | No action needed |
| NONE | Route smoke: 78 routes, 0 FAIL | — | No action needed |

---

## 13. Product / MOM Safety Review

| Rule | Status |
|---|---|
| Backend not modified | ✓ |
| Database / migrations not modified | ✓ |
| API contracts not changed | ✓ |
| Auth / persona / impersonation behavior not changed | ✓ |
| Station Execution command/action behavior not changed | ✓ (p0-c-08h2 changes exist in working tree but are not from this task) |
| `allowed_actions` logic not changed | ✓ |
| No shell/mock/future screen converted to fake production truth | ✓ |
| No new runtime dependencies added | ✓ |
| RouteStatusBanner auto-disclosure remains active | ✓ |
| All shell AI/Twin/Compliance actions remain disabled | ✓ |

---

## 14. Verification Results

| Command | Before | After |
|---|---|---|
| `npm run build` | PASS | PASS |
| `npm run lint` | PASS | PASS |
| `npm run check:routes` | PASS — 78 routes, 0 fail | PASS — 78 routes, 0 fail |
| `npm run lint:i18n:registry` | PASS — 1692 keys | PASS — 1692 keys |
| `npm run qa:station-execution:screenshots` | Not run (requires live dev server) | Deferred |

---

## 15. Final Verdict

**FE-QA-02: COMPLETE — ALL ACCEPTANCE CRITERIA MET**

- ✓ Full route registry reviewed (78 routes, 0 fail)
- ✓ Route smoke documented
- ✓ Sidebar grouped navigation reviewed
- ✓ Sidebar search reviewed
- ✓ Mobile drawer reviewed (keyboard trap, focus return, aria attributes)
- ✓ Representative routes from all 15 domains reviewed
- ✓ Responsive behavior reviewed (code-level) for 4 viewports
- ✓ Accessibility behavior reviewed (aria, focus, keyboard trap)
- ✓ Disclosure / truth-boundary consistency reviewed
- ✓ Dangerous actions reviewed; 1 fix applied (DispatchQueue Resequence)
- ✓ 3 safe small fixes applied (GROUP_ICONS × 3, getIconForPath × 4, DispatchQueue Resequence)
- ✓ No backend/API behavior changed
- ✓ No auth/persona/impersonation behavior changed
- ✓ No Station Execution behavior changed
- ✓ No shell/mock screen converted to fake truth
- ✓ Build, lint, route check, i18n registry all PASS
- ✓ QA report created

---

## 16. Recommended Next Slice

| ID | Description | Priority |
|---|---|---|
| FE-QA-03 | Playwright accessibility sweep — full keyboard tab order, ARIA role coverage, focus management across all 78 routes | Medium |
| FE-QA-04 | Full responsive screenshot coverage for all domains (expand beyond Station Execution) | Medium |
| FE-QA-05 | Clean up orphan page files (ProductionTracking.tsx, Production.tsx) after confirming unused | Low |
| FE-QA-06 | Add MockWarningBanner inline to Home.tsx for belt-and-suspenders disclosure (currently covered by RouteStatusBanner) | Low |
| FE-QA-07 | Address chunk size warning (`1,722 kB` JS bundle) — investigate lazy loading / dynamic imports | Low |
| FE-NAV-04 | Review Planning & Scheduling group placement for APS/Dispatch routes | Medium |
| FE-QA-ROUTES-02 | Add persona-access smoke checks for `/ai/*`, `/digital-twin/*`, `/compliance/*` routes | Medium |
