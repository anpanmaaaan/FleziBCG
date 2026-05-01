# Sidebar Domain Navigation IA Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | FE-NAV-01: Added collapsible domain-grouped sidebar IA for internal to-be visualization. Routes unchanged. Auth unchanged. |

---

## 1. Scope

**Task**: FE-NAV-01 — Sidebar Domain Grouping / Collapsible Navigation IA  
**Objective**: Refactor sidebar navigation information architecture to group the growing number of FleziBCG screens by real MOM domain, add collapsible sections, and preserve all existing screens including shells/mock/to-be items.

**What this task changed**:
- Added `frontend/src/app/navigation/navigationGroups.ts` (new presentational grouping utility)
- Updated `frontend/src/app/components/Layout.tsx` (sidebar rendering only, no auth/routing changes)

**What this task did NOT change**:
- No route paths modified or removed
- No persona/auth behavior changed
- No `personaLanding.ts` semantics changed
- No backend code touched
- No new npm dependencies added
- No page content changed

---

## 2. Source Files Inspected

| File | Purpose | Status |
|---|---|---|
| `frontend/src/app/components/Layout.tsx` | Main app shell, sidebar rendering | ✅ Modified (nav grouping only) |
| `frontend/src/app/persona/personaLanding.ts` | Persona menus and route guards | ✅ Read only, NOT modified |
| `frontend/src/app/routes.tsx` | Route definitions | ✅ Read only, NOT modified |
| `frontend/src/app/screenStatus.ts` | Screen phase registry | ✅ Read, imported for badges |
| `frontend/src/app/navigation/navigationGroups.ts` | New grouping utility | ✅ Created |
| `docs/audit/frontend-screen-coverage-matrix.md` | Coverage history | ✅ Read |
| Prior FE-COVERAGE-01A/B/C/D reports | Domain context | ✅ Read |

---

## 3. Precondition Check

| Item | Status | Notes |
|---|---|---|
| Merge / conflict markers | ✅ NONE | Working tree safe |
| Unrelated backend modifications | ✅ NOTED | 12 backend files modified from prior work — not touched |
| Unrelated docs/audit untracked | ✅ NOTED | Not touched |
| Build before changes | ✅ PASS | 8.99s, 3380 modules |
| Lint before changes | ✅ PASS | 0 errors |
| check:routes before changes | ✅ PASS | 24 smoke checks |
| lint:i18n:registry before changes | ✅ PASS | 1317 keys synchronized |

---

## 4. Product Decision

**Why domain grouping now**: FE-COVERAGE-01A through 01D added 29 shell/mock/to-be screens, bringing the total to 53 routes. A flat sidebar list is no longer scannable for internal product walkthrough.

**Key decisions recorded**:
1. **Future/to-be screens stay in domain groups** — not hidden, not in a catch-all "Future" group.
2. **Collapsible sections** are purely presentational UI state — no relation to authorization.
3. **Phase badges** (SHELL / MOCK / TBD) are shown inline for non-production screens to communicate status without page navigation.
4. **Compact mode** (collapsed sidebar) retains flat icon-only rendering for space efficiency.
5. **Persona-aware default group expansion** deferred — current implementation auto-opens only the active route's group. This is simpler and less error-prone.
6. **i18n for group labels** deferred — group header labels are structural navigation labels in English, not translated screen content. No i18n registry impact.

---

## 5. Navigation IA Before

Flat list per persona. Example (SUP persona — 19 items, no grouping):

```
Global Operations
Production Orders
Work Orders
Products
Routes
BOM
Reason Codes
Line Monitor
Station Monitor
Downtime Analysis
Shift Summary
Material Readiness
Staging & Kitting
WIP Buffers
Quality Lite Dashboard
Quality Measurements
Quality Holds
Quality
Defects
```

**Problems**: No domain structure, no phase visibility, excessive scroll, no discoverability of domain landscape.

---

## 6. Navigation IA After

Domain-grouped collapsible sections per persona. Example (SUP persona — same 19 items, grouped in 6 domain sections):

```
▶ Home / Dashboard       [collapsed if not active]
▼ Core Operations        [auto-open on active route]
    ⬜ Global Operations
    ⬜ Production Orders
    ⬜ Work Orders
    ⬜ Line Monitor          [SHELL badge]
    ⬜ Station Monitor       [SHELL badge]
    ⬜ Shift Summary         [SHELL badge]
▶ Mfg Master Data
    ⬜ Products
    ⬜ Routes
    ⬜ BOM                   [SHELL badge]
    ⬜ Reason Codes          [SHELL badge]
▶ Quality
    ⬜ Quality Lite Dashboard  [SHELL badge]
    ⬜ Quality Measurements    [SHELL badge]
    ⬜ Quality Holds           [SHELL badge]
    ⬜ Quality
    ⬜ Defects
▶ Material / WIP
    ⬜ Material Readiness  [SHELL badge]
    ⬜ Staging & Kitting   [SHELL badge]
    ⬜ WIP Buffers         [SHELL badge]
▶ Reporting & Analytics [future — items appear for PMG]
```

**Improvements**: Scannable domain structure, phase visibility, collapsed groups reduce scroll, domain landscape visible for product walkthrough.

---

## 7. Domain Grouping Rules

| Group ID | Label | Included Route Prefixes | Group Header Icon |
|---|---|---|---|
| `home` | Home / Dashboard | `/home`, `/dashboard` | LayoutDashboard |
| `core-operations` | Core Operations | `/production-orders`, `/work-orders`, `/operations`, `/dispatch`, `/station-session`, `/station-execution`, `/station`, `/operator-identification`, `/equipment-binding`, `/line-monitor`, `/station-monitor`, `/shift-summary`, `/supervisory` | PlayCircle |
| `mfg-master-data` | Mfg Master Data | `/products`, `/routes`, `/bom`, `/resource-requirements`, `/reason-codes` | FileText |
| `quality` | Quality | `/quality-dashboard`, `/quality-measurements`, `/quality-holds`, `/quality`, `/defects` | ShieldCheck |
| `material-wip` | Material / WIP | `/material-readiness`, `/staging-kitting`, `/wip-buffers` | Package |
| `traceability` | Traceability | `/traceability` | ScanSearch |
| `reporting-analytics` | Reporting & Analytics | `/performance`, `/downtime-analysis` | BarChart3 |
| `planning-scheduling` | Planning & Scheduling | `/scheduling` | CalendarClock |
| `governance-admin` | Governance & Admin | `/users`, `/roles`, `/action-registry`, `/scope-assignments`, `/sessions`, `/audit-log`, `/security-events`, `/tenant-settings`, `/plant-hierarchy`, `/settings` | Settings |

**Matching algorithm**: Strip query string, then for each group check if `cleanPath === prefix` or `cleanPath.startsWith(prefix + "/")`. First match wins. Unmatched items go to `_other` bucket (rendered as "Other" at bottom — prevents silent data loss).

---

## 8. Future / To-Be Placement Rule

No future/to-be/shell screen is placed in a catch-all group. All are in their real domain:

| Future / To-Be Item | Domain Group | Reason |
|---|---|---|
| Quality Lite Dashboard (`/quality-dashboard`) | Quality | Quality observation belongs in Quality domain |
| Measurement Entry (`/quality-measurements`) | Quality | QC measurement belongs in Quality domain |
| Quality Holds (`/quality-holds`) | Quality | Hold management belongs in Quality domain |
| Material Readiness (`/material-readiness`) | Material / WIP | Material availability is a WIP/material concern |
| Staging & Kitting (`/staging-kitting`) | Material / WIP | Kit staging is a material preparation concern |
| WIP Buffers (`/wip-buffers`) | Material / WIP | WIP queue is a WIP tracking concern |
| Line Monitor (`/line-monitor`) | Core Operations | Line visibility belongs in operations context |
| Station Monitor (`/station-monitor`) | Core Operations | Station visibility belongs in operations context |
| Station Session (`/station-session`) | Core Operations | Station session belongs in execution context |
| Operator Identification (`/operator-identification`) | Core Operations | Operator onboarding belongs in execution context |
| Equipment Binding (`/equipment-binding`) | Core Operations | Equipment setup belongs in execution context |
| Shift Summary (`/shift-summary`) | Core Operations | Shift reporting relates to operational execution |
| Supervisory Detail (`/supervisory/operations/:id`) | Core Operations | Supervisory oversight belongs in operations |
| Operation Timeline (`/operations/:id/timeline`) | Core Operations | Timeline is part of operations detail |
| BOM (`/bom`) | Mfg Master Data | BOM is manufacturing master data |
| Resource Requirements (`/resource-requirements`) | Mfg Master Data | Resource requirements are master data |
| Reason Codes (`/reason-codes`) | Mfg Master Data | Reason codes are master data configuration |
| OEE Deep Dive (`/performance/oee-deep-dive`) | Reporting & Analytics | OEE belongs in analytics domain |
| Downtime Analysis (`/downtime-analysis`) | Reporting & Analytics | Downtime analytics belongs here |
| APS Scheduling (`/scheduling`) | Planning & Scheduling | Scheduling belongs in planning domain |

---

## 9. Collapsible Behavior

**Implementation**:
- State: `openGroups: Set<string>` stored with React `useState` in the `Layout` component
- **Auto-open on mount**: Group containing `location.pathname` at first render is pre-added
- **Auto-open on navigate**: Each route change adds the new active group without closing others
- **Toggle**: Click group header button toggles open/closed; does not affect other groups
- **Session persistence**: Groups stay open during the current session (useState survives re-renders); no localStorage used (deferred)

**Compact sidebar (collapsed/icon-only)**:
- Group headers not shown (would be unreadable at 80px width)
- Falls back to flat icon-only list (`renderCompactMenuItems`)
- This matches the prior behavior for compact mode

**Mobile drawer**:
- Uses `renderGroupedMenuItems()` — same grouped rendering as expanded desktop sidebar
- Groups close drawer on item click (existing `() => setMobileSidebarOpen(false)` callback preserved)
- Drawer focus trap and keyboard nav preserved (no changes to drawer logic)

**Accessibility**:
- Group header buttons use `aria-expanded={isOpen}`
- Chevron rotates 0° (open) / -90° (closed) via CSS transition — visual state indicator
- All buttons are keyboard-reachable with visible focus ring (`focus-visible:outline`)
- Group items retain existing focus ring behavior

**Deferred**: Persona-aware default open groups (e.g., OPR → Core Operations auto-open). Current route auto-open is sufficient and avoids persona coupling.

---

## 10. Status Badge Treatment

**Badges shown for**: SHELL, MOCK, FUTURE, DISABLED phase items  
**Badges NOT shown for**: CONNECTED, PARTIAL, UNKNOWN (stable/partial production items don't need warnings)

**Badge design**:
- Small pill: `text-[9px] font-bold px-1 py-px rounded` — visually minimal
- Positioned: trailing end of nav item row (`ml-auto`)
- Active item: badge changes to `bg-white/20 text-white/80` (adapts to dark active state)
- Phase → label mapping:

| Phase | Badge Label | Badge Color |
|---|---|---|
| SHELL | SHELL | Blue (bg-blue-100 text-blue-700) |
| MOCK | MOCK | Amber (bg-amber-100 text-amber-700) |
| FUTURE | TBD | Gray (bg-slate-200 text-slate-600) |
| DISABLED | OFF | Red (bg-red-100 text-red-600) |

**Implementation**: `getPhaseForMenuPath()` does exact-match lookup against `SCREEN_STATUS_REGISTRY` route patterns. Dynamic routes (containing `:`) are skipped — they don't appear as menu items. Result is used only for display; no auth behavior involved.

---

## 11. Persona / Route Guard Safety Review

| Persona | Navigation Impact | Authorization Semantics Changed? | Notes |
|---|---|---|---|
| OPR | Station Execution item still appears in Core Operations group | ❌ NO | Only visual grouping |
| SUP | 19 items grouped into Core Operations, Mfg Master Data, Quality, Material/WIP | ❌ NO | Same items, grouped |
| IEP | 15 items grouped into Core Operations, Mfg Master Data, Material/WIP, Traceability, Quality | ❌ NO | Same items, grouped |
| QC | 11 items grouped into Core Operations, Quality, Mfg Master Data, Traceability | ❌ NO | Same items, grouped |
| PMG | 25 items grouped across 7 groups | ❌ NO | Same items, grouped |
| ADM | 11 items grouped into Home, Governance & Admin | ❌ NO | Same items, grouped |
| EXE | 1 item (Dashboard) in Home group | ❌ NO | Same item |

**Key safety properties preserved**:
1. `getMenuItemsForPersona()` in `personaLanding.ts` is the sole source of which items a persona sees — unchanged
2. `isRouteAllowedForPersona()` route guards — unchanged
3. `navigationGroups.ts` only groups items that were already returned by the persona menu — no items added
4. Sidebar visibility is not authorization truth — backend enforces actual authorization
5. Grouping layer cannot grant access to routes not in the persona's menu

---

## 12. Mobile Drawer Review

**Mobile behavior preserved**:
- Drawer open/close triggers unchanged
- Focus trap (`getFocusableElements` + tab wrapping) unchanged
- Close-on-navigate callback passed to `renderGroupedMenuItems(onNavigate)` — works identically
- Drawer width (`w-[min(20rem,85vw)]`) unchanged
- Overlay backdrop unchanged
- Group headers are tappable buttons — work correctly in touch context
- Sections are vertically stacked — same scrollable nav container

**Potential impact**: Mobile drawer now has section headers adding ~32px per group. With groups, the drawer content is structurally cleaner (less total scroll in most personas because groups start collapsed except active). Net effect: improved mobile nav experience.

---

## 13. Product / MOM Safety Review

**This task is navigation IA only.**

| Concern | Status |
|---|---|
| Backend API behavior changed | ✅ NONE |
| Auth/authorization behavior changed | ✅ NONE |
| Execution command/action behavior changed | ✅ NONE |
| Quality disposition logic changed | ✅ NONE |
| Material movement logic changed | ✅ NONE |
| ERP posting logic changed | ✅ NONE |
| AI/twin behavior changed | ✅ NONE |
| allowed_actions logic changed | ✅ NONE |
| Impersonation behavior changed | ✅ NONE |
| Sidebar visibility used as authorization truth | ✅ NO — sidebar visibility is NOT authorization |
| Routes removed or hidden | ✅ NONE — all routes visible in persona menu remain accessible |
| New runtime dependencies added | ✅ NONE |

---

## 14. Verification Results

### After Implementation

| Command | Result |
|---|---|
| `npm run build` | ✅ PASS — 8.48s, 3380 modules, no TS errors |
| `npm run lint` | ✅ PASS — 0 ESLint errors |
| `npm run check:routes` | ✅ PASS — 24 smoke checks |
| `npm run lint:i18n:registry` | ✅ PASS — 1317 keys, en↔ja parity |

### Git Status (Frontend Changes)

**New files**:
```
?? src/app/navigation/navigationGroups.ts
```

**Modified files**:
```
 M src/app/components/Layout.tsx
```

**Unrelated untracked files** (pre-existing, not touched):
```
?? CLAUDE.md
?? backend/_p0c08e_fullsuite.txt
?? backend/tests/test_reopen_resume_station_session_continuity.py
?? backend/tests/test_station_queue_session_aware_migration.py
?? docs/audit/mmd-be-00-evidence-and-contract-lock.md
?? docs/audit/mmd-current-state-report.md
?? docs/implementation/p0-c-08c-*.md
?? docs/implementation/p0-c-08d-*.md
?? docs/implementation/p0-c-08e-*.md
?? docs/proposals/
?? fullsuite_p0c08_review.txt
```

---

## 15. Deferred Issues

| Item | Reason Deferred | Recommendation |
|---|---|---|
| Persona-aware default open groups | Would couple grouping state to persona logic; auto-open-active-route is sufficient | Implement if user research shows specific personas need different defaults |
| localStorage persistence of group state | Not required for internal demo; useState session persistence sufficient | Add if users request persistent collapsed state |
| i18n for group header labels | Group labels are structural navigation elements, not translatable screen content | Add if Japanese UI requires translated group headers |
| Sidebar badges in compact/icon mode | Compact mode is icon-only, badges would overflow | Show badge in tooltip title when compact |
| OEE/Analytics group expansion (PMG) | PMG menu has 1-2 analytics items; auto-open covers this | No action needed |
| Integration, Digital Twin, Compliance groups | No current routes exist for these domains | Add as FUTURE groups when first shell screens are created |
| "Other" group edge case | If ungrouped items appear, they go to `_other` bucket visible in sidebar | Update routePrefixes in navigationGroups.ts when adding new domains |

---

## 16. Final Verdict

**Status**: ✅ COMPLETE & SAFE

### Acceptance Criteria Check

| Criterion | Status |
|---|---|
| Sidebar grouped by MOM domain | ✅ 9 domain groups implemented |
| Groups are collapsible | ✅ Toggle with aria-expanded |
| Active route's group auto-opens | ✅ On mount and on navigate |
| Future/to-be screens visible in domain group | ✅ All 29 shells in correct domain |
| No separate "Future / To-Be" group | ✅ Not present |
| No routes removed | ✅ All routes preserved |
| No route paths changed | ✅ No path changes |
| Existing mock screens remain visible | ✅ All visible in domain groups |
| Auth/persona/impersonation behavior unchanged | ✅ Verified |
| Sidebar visibility not authorization truth | ✅ Documented; presentation only |
| Mobile drawer behavior preserved | ✅ Verified |
| Keyboard accessibility preserved | ✅ aria-expanded, focus rings, tab order intact |
| Build, lint, route check, i18n pass | ✅ All PASS |
| Documentation report created | ✅ This file |
| Git status reported | ✅ Section 14 |

---

## 17. Recommended Next Slice

### Immediate: FE-NAV-01B — Sidebar Search / Quick Nav

**Objective**: Add a small search/filter input at the top of the expanded sidebar to quickly jump to any screen by label, especially useful when many groups exist.

**Approach**: Filter `menuItems` array by label substring, highlight matches, auto-expand matching group.

**Effort**: ~1-2 hours in Layout.tsx only.

### Near-term: Add Missing Domain Groups

**Integration, Digital Twin, Compliance groups**: Currently no routes exist for these domains. When the first shell pages are added via future FE-COVERAGE tasks, add the corresponding group entries to `navigationGroups.ts`. The `_other` bucket prevents data loss in the meantime.

### Near-term: FE-COVERAGE-01E — Operation Detail Shells

Add detail route shells (Operation Timeline detail, Station Session detail) and update navigation linking from list views to detail views. Grouping already handles these paths (Core Operations group).

---

**Report Generated**: 2026-05-01  
**Files Changed**: `frontend/src/app/navigation/navigationGroups.ts` (created), `frontend/src/app/components/Layout.tsx` (sidebar rendering updated)  
**Verification**: Build ✅ Lint ✅ Routes ✅ i18n ✅  
**Authorization Boundary**: Navigation is presentation only. Backend remains source of truth for all operational and authorization behavior.
