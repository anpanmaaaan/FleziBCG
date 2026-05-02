# FE-GOVADMIN-02 — Governance/Admin Runtime Visual QA + Responsive Sweep Report

## History

| Date | Version | Change |
|---|---|---|
| 2026-05-02 | v1.0 | Completed runtime visual QA, responsive sweep, accessibility sanity check, and safety verification for Governance & Admin screens after FE-GOVADMIN-01. |

---

## 1. Scope

Runtime visual QA, responsive sweep (4 viewports), accessibility sanity check, and governance safety verification for all 9 Governance & Admin screens introduced in FE-GOVADMIN-01.

**Routes in scope:**
- `/users` — User Management
- `/roles` — Role Management
- `/action-registry` — Action Registry
- `/scope-assignments` — Scope Assignments
- `/sessions` — Session Management
- `/audit-log` — Audit Log
- `/security-events` — Security Events
- `/tenant-settings` — Tenant Settings
- `/plant-hierarchy` — Plant Hierarchy

---

## 2. Prerequisites Checked

| Check | Result |
|---|---|
| FE-GOVADMIN-01 completed | ✓ Confirmed — `docs/audit/fe-govadmin-01-report.md` present |
| All 9 pages use `GovernancePageShell` | ✓ Verified via source inspection |
| Dev server running at `http://localhost:5173` | ✓ Confirmed |
| Playwright available | ✓ `playwright ^1.52.0` in `package.json` |
| No backend changes required | ✓ Frontend-only task |

---

## 3. Runtime QA Environment

| Property | Value |
|---|---|
| Dev server | `http://localhost:5173` |
| Screenshot harness | `frontend/scripts/govadmin-responsive-screenshots.mjs` |
| Mock persona | `role_code: "ADM"` (mocked at `/v1/auth/me`) |
| Output directory | `docs/audit/fe-govadmin-02-runtime-qa/` |
| Total screenshots | 36 (9 routes × 4 viewports) |
| Errors | 0 |

**Critical bug discovered and fixed during setup:**
`isRouteAllowedForPersona` in `personaLanding.ts` did not include governance routes — all 9 routes redirected for all personas. Fixed by adding ADM-only block. This is a UX routing fix only; backend authorization is unchanged.

---

## 4. Routes Tested

| Route | Page | Shell | Disclosure Banner | Status |
|---|---|---|---|---|
| `/users` | User Management | ✓ GovernancePageShell | ✓ "Not Implemented" × 2 | ✓ Passed |
| `/roles` | Role Management | ✓ GovernancePageShell | ✓ "Not Implemented" × 1 | ✓ Passed |
| `/action-registry` | Action Registry | ✓ GovernancePageShell | ✓ "Not Implemented" × 2 | ✓ Passed |
| `/scope-assignments` | Scope Assignments | ✓ GovernancePageShell | ✓ "Not Implemented" × 2 | ✓ Passed |
| `/sessions` | Session Management | ✓ GovernancePageShell | ✓ "Not Implemented" × 2 | ✓ Passed |
| `/audit-log` | Audit Log | ✓ GovernancePageShell | ✓ "Not Implemented" × 1 | ✓ Passed |
| `/security-events` | Security Events | ✓ GovernancePageShell | ✓ "Not Implemented" × 2 | ✓ Passed |
| `/tenant-settings` | Tenant Settings | ✓ GovernancePageShell | ✓ "Not Implemented" × 2 | ✓ Passed |
| `/plant-hierarchy` | Plant Hierarchy | ✓ GovernancePageShell | ✓ "Not Implemented" × 2 | ✓ Passed |

---

## 5. Viewport Matrix Results

| Route | 1440×900 | 1180×820 | 820×1180 | 430×932 | Issues Found | Fix Applied |
|---|---|---|---|---|---|---|
| `/users` | ✓ | ✓ | ✓ | ✓ (scrollable) | Search overflow, filter nowrap, table nowrap | ✓ |
| `/roles` | ✓ | ✓ | ✓ | ✓ | None — card grid wraps naturally | — |
| `/action-registry` | ✓ | ✓ | ✓ | ✓ (scrollable) | Table nowrap | ✓ |
| `/scope-assignments` | ✓ | ✓ | ✓ | ✓ (scrollable) | Table nowrap | ✓ |
| `/sessions` | ✓ | ✓ | ✓ | ✓ (scrollable) | Table nowrap | ✓ |
| `/audit-log` | ✓ | ✓ | ✓ | ✓ (scrollable) | Filter nowrap, table nowrap | ✓ |
| `/security-events` | ✓ | ✓ | ✓ | ✓ (scrollable) | Table nowrap | ✓ |
| `/tenant-settings` | ✓ | ✓ | ✓ | ✓ | None after fix | ✓ |
| `/plant-hierarchy` | ✓ | ✓ | ✓ | ✓ (scrollable) | Table nowrap | ✓ |

*Scrollable = table horizontally scrollable inside overflow-auto container, which is the correct behavior for data tables on mobile.*

---

## 6. Screenshots / Evidence

All 36 screenshots saved to `docs/audit/fe-govadmin-02-runtime-qa/`.

Pattern: `{route-slug}-{viewport}.png`

| Route | Desktop | Laptop | Tablet | Mobile |
|---|---|---|---|---|
| users | `users-desktop.png` | `users-laptop.png` | `users-tablet.png` | `users-mobile.png` |
| roles | `roles-desktop.png` | `roles-laptop.png` | `roles-tablet.png` | `roles-mobile.png` |
| action-registry | `action-registry-desktop.png` | `action-registry-laptop.png` | `action-registry-tablet.png` | `action-registry-mobile.png` |
| scope-assignments | `scope-assignments-desktop.png` | `scope-assignments-laptop.png` | `scope-assignments-tablet.png` | `scope-assignments-mobile.png` |
| sessions | `sessions-desktop.png` | `sessions-laptop.png` | `sessions-tablet.png` | `sessions-mobile.png` |
| audit-log | `audit-log-desktop.png` | `audit-log-laptop.png` | `audit-log-tablet.png` | `audit-log-mobile.png` |
| security-events | `security-events-desktop.png` | `security-events-laptop.png` | `security-events-tablet.png` | `security-events-mobile.png` |
| tenant-settings | `tenant-settings-desktop.png` | `tenant-settings-laptop.png` | `tenant-settings-tablet.png` | `tenant-settings-mobile.png` |
| plant-hierarchy | `plant-hierarchy-desktop.png` | `plant-hierarchy-laptop.png` | `plant-hierarchy-tablet.png` | `plant-hierarchy-mobile.png` |

---

## 7. Governance Safety Checklist Results

| Route | Disclosure Visible | Dangerous Actions Disabled | Backend Truth Preserved | Notes |
|---|---|---|---|---|
| `/users` | ✓ | ✓ (Eye/Edit/Trash disabled, locked Create) | ✓ | IAM managed exclusively by backend |
| `/roles` | ✓ | ✓ (Edit/Trash disabled) | ✓ | Role definitions from backend |
| `/action-registry` | ✓ | ✓ (all actions disabled) | ✓ | Action codes read-only display |
| `/scope-assignments` | ✓ | ✓ (all actions disabled) | ✓ | Scope bindings read-only |
| `/sessions` | ✓ | ✓ (LogOut disabled) | ✓ | Session state from backend |
| `/audit-log` | ✓ | ✓ (no write actions) | ✓ | Audit log is append-only |
| `/security-events` | ✓ | ✓ (no write actions) | ✓ | Security events are read-only |
| `/tenant-settings` | ✓ | ✓ (Save Changes disabled, locked) | ✓ | Tenant config from backend |
| `/plant-hierarchy` | ✓ | ✓ (Add Node future, + buttons disabled) | ✓ | Hierarchy from master data system |

**All 9 routes pass governance safety check.**

---

## 8. Accessibility Sanity Results

| Check | Result | Notes |
|---|---|---|
| Disclosure banners present | ✓ | All 9 pages — `MockWarningBanner` visible at top |
| `ScreenStatusBadge` "Shell" visible | ✓ | Rendered in GovernancePageShell header |
| Icon-only buttons have `aria-label` | ✓ Fixed | Added to: UserManagement (Eye/Edit/Trash), SessionManagement (LogOut), PlantHierarchy (Plus), RoleManagement (Edit/Trash) |
| `<label>` associated with `<input>` | ✓ Fixed | TenantSettings: all 5 fields now have `htmlFor`/`id` pairs |
| `disabled` state communicated | ✓ | All placeholder action buttons use `disabled` + `cursor-not-allowed` |
| Focus targets visible | ✓ | No custom focus removal detected |

---

## 9. Responsive Issues Found

| Issue | Routes Affected | Severity |
|---|---|---|
| Search input `w-96` overflows at 430px | `UserManagement` | Medium |
| Filter bar `flex` without `flex-wrap` causes overflow at narrow viewports | `UserManagement`, `AuditLog` | Medium |
| Wide tables (5–8 columns) collapse without `min-w` | 7 routes with tables | Medium |
| `GovernancePageShell` padding `p-6` too large on mobile | All 9 routes | Low |
| Icon-only buttons missing `aria-label` | `UserManagement`, `SessionManagement`, `PlantHierarchy`, `RoleManagement` | Medium (a11y) |
| `<label>` not associated with `<input>` | `TenantSettings` | Medium (a11y) |

---

## 10. Fixes Applied

| Fix | File | Change |
|---|---|---|
| GovernancePageShell mobile padding | `GovernancePageShell.tsx` | `p-6` → `p-4 sm:p-6` |
| Search input mobile width | `UserManagement.tsx` | `w-96` → `w-full sm:w-80` |
| Filter bar flex-wrap | `UserManagement.tsx` | Added `flex-wrap` |
| Filter bar flex-wrap | `AuditLog.tsx` | Added `flex-wrap` |
| Table min-width | `UserManagement.tsx` | `min-w-[700px]` |
| Table min-width | `AuditLog.tsx` | `min-w-[640px]` |
| Table min-width | `SessionManagement.tsx` | `min-w-[700px]` |
| Table min-width | `SecurityEvents.tsx` | `min-w-[720px]` |
| Table min-width | `ScopeAssignments.tsx` | `min-w-[800px]` |
| Table min-width | `ActionRegistry.tsx` | `min-w-[560px]` |
| Table min-width | `PlantHierarchy.tsx` | `min-w-[560px]` |
| aria-label icon buttons | `UserManagement.tsx` | Eye, Edit, Trash buttons |
| aria-label icon button | `SessionManagement.tsx` | LogOut button |
| aria-label icon button | `PlantHierarchy.tsx` | Plus button |
| aria-label icon buttons | `RoleManagement.tsx` | Edit, Trash buttons |
| label htmlFor/id pairs | `TenantSettings.tsx` | All 5 field pairs |
| UX routing bug (critical) | `personaLanding.ts` | Added ADM governance route block |

---

## 11. Files Changed

| File | Change Type |
|---|---|
| `frontend/scripts/govadmin-responsive-screenshots.mjs` | NEW — screenshot harness (ADM role, 9 routes, 4 viewports) |
| `frontend/src/app/persona/personaLanding.ts` | Bug fix — governance routes added to `isRouteAllowedForPersona` |
| `frontend/src/app/components/GovernancePageShell.tsx` | Responsive — mobile padding |
| `frontend/src/app/pages/UserManagement.tsx` | Responsive + a11y — search width, filter wrap, table min-w, aria-labels |
| `frontend/src/app/pages/AuditLog.tsx` | Responsive — filter wrap, table min-w |
| `frontend/src/app/pages/SessionManagement.tsx` | Responsive + a11y — table min-w, aria-label |
| `frontend/src/app/pages/SecurityEvents.tsx` | Responsive — table min-w |
| `frontend/src/app/pages/ScopeAssignments.tsx` | Responsive — table min-w |
| `frontend/src/app/pages/ActionRegistry.tsx` | Responsive — table min-w |
| `frontend/src/app/pages/PlantHierarchy.tsx` | Responsive + a11y — table min-w, aria-label |
| `frontend/src/app/pages/TenantSettings.tsx` | A11y — label htmlFor/id pairs |
| `frontend/src/app/pages/RoleManagement.tsx` | A11y — aria-labels on icon buttons |

---

## 12. Verification Commands

| Command | Result |
|---|---|
| `npm run build` | ✓ PASS — 3408 modules, 0 errors |
| `npm run lint` | ✓ PASS — clean (0 errors, 0 warnings) |
| `npm run lint:i18n:registry` | ✓ PASS — en.ts and ja.ts key-synchronized (1692 keys) |
| `npm run lint:i18n:hardcode` | ⚠ PRE-EXISTING — bash script CRLF issue on Windows; not caused by this task (same condition as FE-GOVADMIN-01) |
| `npm run check:routes` | ✓ PASS — 24/24 checks, 77/78 routes covered, 1 excluded (redirect-only) |
| Screenshot harness | ✓ PASS — 36/36 screenshots, 0 errors |

---

## 13. Remaining Risks / Deferred Items

| Item | Severity | Reason Deferred |
|---|---|---|
| All 9 pages are mock/shell — no backend data | Expected | Shell phase; backend IAM/governance APIs not yet implemented |
| `npm run lint:i18n:hardcode` CRLF issue | Low | Pre-existing Windows environment issue, not caused by this task |
| No keyboard navigation test performed | Low | Out of scope for this sprint; covered by global a11y audit |
| No contrast ratio verification | Low | Tailwind defaults meet WCAG AA; formal a11y audit deferred |
| `role_code: "ADM"` persona has no scope filter in mock | Expected | Shell phase; scope-based access managed by backend |

---

## 14. Final Verdict

**PASS**

All 9 governance/admin routes now:
- Render the correct page (ADM routing bug fixed)
- Display `GovernancePageShell` with proper title, `Shell` badge, and disclosure banners
- Respond correctly at all 4 viewports (desktop, laptop, tablet, mobile)
- Have horizontally scrollable tables on narrow viewports
- Preserve backend as source of truth — all write actions disabled
- Have `aria-label` on icon-only buttons
- Have properly associated `<label>`/`<input>` pairs
- Pass build, lint, i18n registry parity, and route accessibility gate

No governance safety violations. No disabled actions were re-enabled. No disclosure banners were removed. No route paths were changed.
