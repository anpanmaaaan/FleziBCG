# Frontend Mechanical Refactor Plan

> **Scope:** File moves/renames, import path updates, non-functional re-exports,
> theme token centralization. **No logic changes, no behavior changes, no UI
> layout changes, no dependency upgrades.**
>
> **Baseline:** `npm run build` passes (`✓ built in 8s`, zero TS errors).
> All PRs must preserve this baseline.

---

## PR 1 — Remove Dead Directories & Orphan Files

### Rationale
Three directories contain no code or documentation that is imported by any
source file. Removing them reduces surface area and confusion.

### File-by-File Change List

| Action | Path | Reason |
|--------|------|--------|
| DELETE dir | `frontend/src/utils/` | Empty directory; zero files inside |
| DELETE dir | `frontend/src/imports/` | Contains 6 `.md` spec files; zero imports from any `.ts`/`.tsx` |
| DELETE file | `frontend/src/styles/fonts.css` | Empty file (0 bytes); `index.css` imports it, import must be removed |

### Representative Diff

```diff
--- a/frontend/src/styles/index.css
+++ b/frontend/src/styles/index.css
-@import './fonts.css';
 @import './tailwind.css';
 @import './theme.css';
```

### ESLint Boundary Rules

*No ESLint rules needed for PR 1 — deletion only.*

### Verification Checklist

| # | Command | Expected |
|---|---------|----------|
| 1 | `cd frontend && npm run build` | `✓ built` with zero errors |
| 2 | `test ! -d src/utils` | exit 0 |
| 3 | `test ! -d src/imports` | exit 0 |
| 4 | `test ! -f src/styles/fonts.css` | exit 0 |
| 5 | `grep -r "fonts.css" src/` | no output (zero matches) |
| 6 | `grep -r "pasted_text" src/` | no output |

---

## PR 2 — Establish `@/` Path Alias Convention & Barrel Re-Exports

### Rationale
`vite.config.ts` already defines `@` → `./src`, but zero files use it. The
codebase uses relative paths exclusively (`../`, `../../`). This PR:

1. Adds a `paths` entry to `tsconfig.json` so TS resolves `@/`.
2. Creates barrel `index.ts` files for core modules.
3. Does NOT rewrite existing imports (PR 3 does that).

### File-by-File Change List

| Action | Path | Change |
|--------|------|--------|
| EDIT | `frontend/tsconfig.json` | Add `"paths": { "@/*": ["./src/*"] }`, add `"baseUrl": "."` |
| CREATE | `frontend/src/app/api/index.ts` | Re-export all API modules |
| CREATE | `frontend/src/app/auth/index.ts` | Re-export `AuthContext`, `RequireAuth` |
| CREATE | `frontend/src/app/impersonation/index.ts` | Re-export `ImpersonationContext` |
| CREATE | `frontend/src/app/persona/index.ts` | Re-export `PersonaLandingRedirect`, `personaLanding` |
| CREATE | `frontend/src/app/components/index.ts` | Re-export non-UI shared components |
| CREATE | `frontend/src/types/index.ts` | Re-export `database.ts` types |

### Representative Diffs

```diff
--- a/frontend/tsconfig.json
+++ b/frontend/tsconfig.json
 {
   "compilerOptions": {
     "target": "ES2022",
+    "baseUrl": ".",
     ...
-    "types": ["vite/client"]
+    "types": ["vite/client"],
+    "paths": {
+      "@/*": ["./src/*"]
+    }
   },
   "include": ["src"]
 }
```

```typescript
// frontend/src/app/api/index.ts  (NEW)
export { authApi } from "./authApi";
export type { AuthUser, LoginRequest, LoginResponse } from "./authApi";
export { request, HttpError } from "./httpClient";
export type { HttpContext } from "./httpClient";
export { dashboardApi } from "./dashboardApi";
export { operationApi } from "./operationApi";
export { operationMonitorApi } from "./operationMonitorApi";
export { productionOrderApi } from "./productionOrderApi";
export { stationApi } from "./stationApi";
export { impersonationApi } from "./impersonationApi";
```

```typescript
// frontend/src/app/auth/index.ts  (NEW)
export { AuthProvider, useAuth } from "./AuthContext";
export { RequireAuth } from "./RequireAuth";
```

```typescript
// frontend/src/app/impersonation/index.ts  (NEW)
export { ImpersonationProvider, useImpersonation } from "./ImpersonationContext";
```

```typescript
// frontend/src/app/persona/index.ts  (NEW)
export { PersonaLandingRedirect } from "./PersonaLandingRedirect";
export {
  resolvePersonaFromRoleCode,
  getDefaultLanding,
  getMenuItemsForPersona,
  isRouteAllowedForPersona,
} from "./personaLanding";
export type { Persona, PersonaMenuItem } from "./personaLanding";
```

```typescript
// frontend/src/app/components/index.ts  (NEW)
export { PageHeader } from "./PageHeader";
export { StatusBadge } from "./StatusBadge";
export { StatsCard } from "./StatsCard";
export { Breadcrumb } from "./Breadcrumb";
export { GanttChart } from "./GanttChart";
export { ColumnManagerDialog } from "./ColumnManagerDialog";
export { AccessDeniedScreen } from "./AccessDeniedScreen";
export { ActiveImpersonationBanner } from "./ActiveImpersonationBanner";
export { ImpersonationSwitcher } from "./ImpersonationSwitcher";
export { Layout } from "./Layout";
export { TopBar } from "./TopBar";
```

```typescript
// frontend/src/types/index.ts  (NEW)
export type {
  ProductionOrder,
  Route,
  Operation,
} from "./database";
```

### ESLint Boundary Rules

*No enforcement rules yet — barrels only re-export; existing imports continue
to work. PR 3 introduces the linting.*

### Verification Checklist

| # | Command | Expected |
|---|---------|----------|
| 1 | `cd frontend && npm run build` | `✓ built` with zero errors |
| 2 | `node -e "require('path').resolve('./src')"` in tsconfig context | `paths` resolves |
| 3 | Barrel files exist: `ls src/app/{api,auth,impersonation,persona,components}/index.ts` | all exist |
| 4 | `grep -c "export" src/app/api/index.ts` | ≥ 8 lines |
| 5 | Each barrel file only contains `export` / `export type` statements (no logic) | manual review |

---

## PR 3 — Migrate Imports to `@/` Alias

### Rationale
Rewrite all cross-module relative imports (`../auth/AuthContext`) to use the
`@/` alias (`@/app/auth`). Intra-folder relative imports (`./httpClient`)
stay as-is.

**Rule:** Only change import paths that cross module boundaries (parent `../`).
Do NOT touch `./` same-folder imports.

### File-by-File Change List

> Affected files (every `.tsx`/`.ts` under `src/app/` that uses `../`):

| File | Old Import | New Import |
|------|-----------|------------|
| `app/App.tsx` | `./routes` | stays `./routes` (same folder) |
| `app/App.tsx` | `./auth/AuthContext` | `@/app/auth` |
| `app/App.tsx` | `./impersonation/ImpersonationContext` | `@/app/impersonation` |
| `app/App.tsx` | `./components/ui/sonner` | `@/app/components/ui/sonner` |
| `app/routes.tsx` | `./pages/Dashboard` | stays (same level) |
| `app/routes.tsx` | `./components/Layout` | `@/app/components` |
| `app/routes.tsx` | `./auth/RequireAuth` | `@/app/auth` |
| `app/routes.tsx` | `./persona/PersonaLandingRedirect` | `@/app/persona` |
| `app/pages/*.tsx` | `../components/PageHeader` | `@/app/components` |
| `app/pages/*.tsx` | `../api/operationApi` | `@/app/api` |
| `app/pages/*.tsx` | `../auth/AuthContext` | `@/app/auth` |
| `app/pages/*.tsx` | `../impersonation/ImpersonationContext` | `@/app/impersonation` |
| `app/pages/*.tsx` | `../data/mockData` | `@/app/data/mockData` |
| `app/pages/*.tsx` | `../components/ui/*` | `@/app/components/ui/*` |
| `app/pages/*.tsx` | `../i18n` | `@/app/i18n` |
| `app/components/Layout.tsx` | `../auth/AuthContext` | `@/app/auth` |
| `app/components/Layout.tsx` | `../persona/personaLanding` | `@/app/persona` |
| `app/components/Layout.tsx` | `../impersonation/ImpersonationContext` | `@/app/impersonation` |
| `app/components/TopBar.tsx` | `../auth/AuthContext` | `@/app/auth` |
| `app/components/TopBar.tsx` | `../impersonation/ImpersonationContext` | `@/app/impersonation` |
| `app/auth/RequireAuth.tsx` | `./AuthContext` | stays (same folder) |
| `app/auth/AuthContext.tsx` | `../api/authApi` | `@/app/api` |
| `app/impersonation/ImpersonationContext.tsx` | `../auth/AuthContext` | `@/app/auth` |
| `app/impersonation/ImpersonationContext.tsx` | `../api/impersonationApi` | `@/app/api` |
| `app/persona/PersonaLandingRedirect.tsx` | `../auth/AuthContext` | `@/app/auth` |
| `main.tsx` | `./app/App.tsx` | `@/app/App` |
| `main.tsx` | `./styles/index.css` | `@/styles/index.css` |

### Representative Diff

```diff
--- a/frontend/src/app/pages/StationExecution.tsx
+++ b/frontend/src/app/pages/StationExecution.tsx
-import { useAuth } from '../auth/AuthContext';
-import { useImpersonation } from '../impersonation/ImpersonationContext';
-import { PageHeader } from '../components/PageHeader';
-import { stationApi } from '../api/stationApi';
-import { operationApi } from '../api/operationApi';
-import { Card } from '../components/ui/card';
-import { Button } from '../components/ui/button';
+import { useAuth } from '@/app/auth';
+import { useImpersonation } from '@/app/impersonation';
+import { PageHeader } from '@/app/components';
+import { stationApi, operationApi } from '@/app/api';
+import { Card } from '@/app/components/ui/card';
+import { Button } from '@/app/components/ui/button';
```

### ESLint Boundary Rules

Install ESLint + `eslint-plugin-import` (dev dependency) and add config:

```javascript
// frontend/eslint.config.js  (NEW — flat config)
import importPlugin from "eslint-plugin-import";

export default [
  {
    files: ["src/**/*.{ts,tsx}"],
    plugins: { import: importPlugin },
    rules: {
      // Ban parent-relative cross-module imports
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["../**/auth/*"],
              message: "Use @/app/auth barrel instead.",
            },
            {
              group: ["../**/api/*"],
              message: "Use @/app/api barrel instead.",
            },
            {
              group: ["../**/impersonation/*"],
              message: "Use @/app/impersonation barrel instead.",
            },
            {
              group: ["../**/persona/*"],
              message: "Use @/app/persona barrel instead.",
            },
          ],
        },
      ],
    },
  },
];
```

Add script to `package.json`:

```diff
 "scripts": {
   "build": "vite build",
-  "dev": "vite"
+  "dev": "vite",
+  "lint": "eslint src/"
 },
```

**New devDependencies:** `eslint`, `eslint-plugin-import`, `@eslint/js`, `typescript-eslint`

### Verification Checklist

| # | Command | Expected |
|---|---------|----------|
| 1 | `cd frontend && npm run build` | `✓ built` with zero errors |
| 2 | `grep -rn "from '\.\./auth/" src/app/` | zero matches |
| 3 | `grep -rn "from '\.\./api/" src/app/` | zero matches |
| 4 | `grep -rn "from '\.\./impersonation/" src/app/` | zero matches |
| 5 | `grep -rn "from '\.\./persona/" src/app/` | zero matches |
| 6 | `npx eslint src/` | zero errors, zero warnings |
| 7 | `npm run dev` → navigate all routes | no console errors, no blank pages |

---

## PR 4 — Theme Token Centralization: Define Semantic CSS Variables

### Rationale
Hardcoded hex values (`#3b82f6`, `#33B2C1`, `#ef4444`) and raw Tailwind shade
classes (`bg-blue-500`, `text-red-600`) are scattered across 20+ files.
This PR defines semantic CSS custom properties and maps them into Tailwind's
`@theme` block so they can be used as `bg-status-blocked`, `text-status-ok`, etc.

**Phase 1 only:** Define tokens and wire into `@theme`. Do NOT replace usages
(that is PR 5).

### File-by-File Change List

| Action | Path | Change |
|--------|------|--------|
| EDIT | `frontend/src/styles/theme.css` | Add semantic CSS variables under `:root` and `@theme inline` |

### New Tokens

```css
/* ── Status tokens ──────────────────────────────────── */
--status-pending:            #94a3b8;  /* slate-400  */
--status-pending-bg:         #f1f5f9;  /* slate-100  */
--status-in-progress:        #3b82f6;  /* blue-500   */
--status-in-progress-bg:     #eff6ff;  /* blue-50    */
--status-completed:          #10b981;  /* green-500  */
--status-completed-bg:       #ecfdf5;  /* green-50   */
--status-blocked:            #ef4444;  /* red-500    */
--status-blocked-bg:         #fef2f2;  /* red-50     */
--status-delayed:            #f59e0b;  /* amber-500  */
--status-delayed-bg:         #fffbeb;  /* amber-50   */
--status-on-hold:            #8b5cf6;  /* violet-500 */
--status-on-hold-bg:         #f5f3ff;  /* violet-50  */
--status-cancelled:          #6b7280;  /* gray-500   */
--status-cancelled-bg:       #f3f4f6;  /* gray-100   */

/* ── Brand / CTA tokens ────────────────────────────── */
--brand-cta:                 #33B2C1;  /* teal CTA   */
--brand-cta-hover:           #2a9aa8;

/* ── Surface tokens ─────────────────────────────────── */
--surface-page:              #f8fafc;  /* slate-50   */
--surface-table-header:      #f8fafc;
--surface-table-stripe:      #f9fafb;  /* gray-50    */
--surface-divider:           #e5e7eb;  /* gray-200   */

/* ── Chart extended tokens ──────────────────────────── */
--chart-6:                   #8b5cf6;  /* violet-500 */
--chart-7:                   #9333ea;  /* purple-600 */
--chart-grid:                #e5e7eb;  /* gray-200   */
--chart-axis:                #6b7280;  /* gray-500   */
--chart-tooltip-bg:          #ffffff;
--chart-tooltip-border:      #e5e7eb;

/* ── Focus / interaction tokens ─────────────────────── */
--focus-ring:                var(--ring);  /* already #3B82F6 */
```

### Representative Diff

```diff
--- a/frontend/src/styles/theme.css
+++ b/frontend/src/styles/theme.css
 :root {
   /* ... existing variables ... */
   --sidebar-ring: #3B82F6;
+
+  /* ── Status tokens ── */
+  --status-pending: #94a3b8;
+  --status-pending-bg: #f1f5f9;
+  --status-in-progress: #3b82f6;
+  --status-in-progress-bg: #eff6ff;
+  --status-completed: #10b981;
+  --status-completed-bg: #ecfdf5;
+  --status-blocked: #ef4444;
+  --status-blocked-bg: #fef2f2;
+  --status-delayed: #f59e0b;
+  --status-delayed-bg: #fffbeb;
+  --status-on-hold: #8b5cf6;
+  --status-on-hold-bg: #f5f3ff;
+  --status-cancelled: #6b7280;
+  --status-cancelled-bg: #f3f4f6;
+
+  /* ── Brand / CTA ── */
+  --brand-cta: #33B2C1;
+  --brand-cta-hover: #2a9aa8;
+
+  /* ── Surface ── */
+  --surface-page: #f8fafc;
+  --surface-table-header: #f8fafc;
+  --surface-table-stripe: #f9fafb;
+  --surface-divider: #e5e7eb;
+
+  /* ── Chart extended ── */
+  --chart-6: #8b5cf6;
+  --chart-7: #9333ea;
+  --chart-grid: #e5e7eb;
+  --chart-axis: #6b7280;
+  --chart-tooltip-bg: #ffffff;
+  --chart-tooltip-border: #e5e7eb;
+
+  /* ── Focus ── */
+  --focus-ring: var(--ring);
 }

 @theme inline {
   /* ... existing entries ... */
   --color-sidebar-ring: var(--sidebar-ring);
+
+  --color-status-pending: var(--status-pending);
+  --color-status-pending-bg: var(--status-pending-bg);
+  --color-status-in-progress: var(--status-in-progress);
+  --color-status-in-progress-bg: var(--status-in-progress-bg);
+  --color-status-completed: var(--status-completed);
+  --color-status-completed-bg: var(--status-completed-bg);
+  --color-status-blocked: var(--status-blocked);
+  --color-status-blocked-bg: var(--status-blocked-bg);
+  --color-status-delayed: var(--status-delayed);
+  --color-status-delayed-bg: var(--status-delayed-bg);
+  --color-status-on-hold: var(--status-on-hold);
+  --color-status-on-hold-bg: var(--status-on-hold-bg);
+  --color-status-cancelled: var(--status-cancelled);
+  --color-status-cancelled-bg: var(--status-cancelled-bg);
+
+  --color-brand-cta: var(--brand-cta);
+  --color-brand-cta-hover: var(--brand-cta-hover);
+
+  --color-surface-page: var(--surface-page);
+  --color-surface-table-header: var(--surface-table-header);
+  --color-surface-table-stripe: var(--surface-table-stripe);
+  --color-surface-divider: var(--surface-divider);
+
+  --color-chart-6: var(--chart-6);
+  --color-chart-7: var(--chart-7);
+  --color-chart-grid: var(--chart-grid);
+  --color-chart-axis: var(--chart-axis);
+  --color-chart-tooltip-bg: var(--chart-tooltip-bg);
+  --color-chart-tooltip-border: var(--chart-tooltip-border);
+
+  --color-focus-ring: var(--focus-ring);
 }
```

### ESLint Boundary Rules

*None for this PR — CSS-only changes.*

### Verification Checklist

| # | Command | Expected |
|---|---------|----------|
| 1 | `cd frontend && npm run build` | `✓ built` with zero errors |
| 2 | `grep "status-pending" src/styles/theme.css` | matches found |
| 3 | `grep "brand-cta" src/styles/theme.css` | matches found |
| 4 | Visual smoke: open any route — UI must look **identical** | no visual diff |

---

## PR 5 — Theme Token Adoption: Replace Hardcoded Colors

### Rationale
Replace hardcoded hex values and raw Tailwind shade classes with the semantic
tokens defined in PR 4. Split into sub-PRs if the diff is large.

**Scope boundary:** Only replace colors that map 1:1 to a defined token. Any
ambiguous value is deferred (see Deferred Items at bottom).

### File-by-File Change List

#### 5A — Brand CTA color (`#33B2C1` / `#2a9aa8`)

| File | Old | New |
|------|-----|-----|
| `components/AddProductionOrderDialog.tsx` | `bg-[#33B2C1] hover:bg-[#2a9aa8]` (×3) | `bg-brand-cta hover:bg-brand-cta-hover` |
| `components/TopBar.tsx` | `bg-[#33B2C1]` | `bg-brand-cta` |
| `components/ColumnManagerDialog.tsx` | `bg-[#33B2C1] hover:bg-[#2a9aa8]` | `bg-brand-cta hover:bg-brand-cta-hover` |

#### 5B — Chart hex values

| File | Old | New |
|------|-----|-----|
| `pages/Dashboard.tsx` | `stroke="#3b82f6"` | `stroke="var(--chart-1)"` |
| `pages/Dashboard.tsx` | `fill: '#3b82f6'` (dot) | `fill: 'var(--chart-1)'` |
| `pages/Dashboard.tsx` | `stroke="#10b981"` | `stroke="var(--chart-2)"` |
| `pages/Dashboard.tsx` | `fill: '#10b981'` (dot) | `fill: 'var(--chart-2)'` |
| `pages/Dashboard.tsx` | `stroke="#9333ea"` | `stroke="var(--chart-7)"` |
| `pages/Dashboard.tsx` | `stroke="#e5e7eb"` | `stroke="var(--chart-grid)"` |
| `pages/Dashboard.tsx` | `stroke="#6b7280"` | `stroke="var(--chart-axis)"` |
| `pages/Dashboard.tsx` | `backgroundColor: '#fff', border: '1px solid #e5e7eb'` | `backgroundColor: 'var(--chart-tooltip-bg)', border: '1px solid var(--chart-tooltip-border)'` |
| `pages/OEEDeepDive.tsx` | `fill="#3b82f6"` | `fill="var(--chart-1)"` |
| `pages/OEEDeepDive.tsx` | `stroke="#ef4444"` | `stroke="var(--chart-5)"` |
| `pages/OEEDeepDive.tsx` | `stroke="#94a3b8"` | `stroke="var(--status-pending)"` |
| `pages/OEEDeepDive.tsx` | `fill="#8b5cf6"`, `stroke="#8b5cf6"` | `fill="var(--chart-6)"`, `stroke="var(--chart-6)"` |
| `pages/OEEDeepDive.tsx` | `stroke="#3b82f6"` | `stroke="var(--chart-1)"` |
| `pages/OEEDeepDive.tsx` | `stroke="#10b981"` | `stroke="var(--chart-2)"` |
| `pages/OEEDeepDive.tsx` | `stroke="#6366f1"` | `stroke="var(--chart-3)"` |
| `pages/Traceability.tsx` | `border: '2px solid #3b82f6'` | `border: '2px solid var(--chart-1)'` |
| `pages/Traceability.tsx` | `color: '#3b82f6'` | `color: 'var(--chart-1)'` |
| `pages/Traceability.tsx` | `stroke: '#3b82f6'` | `stroke: 'var(--chart-1)'` |
| `pages/Traceability.tsx` | `background: '#fff'` | `background: 'var(--background)'` |

#### 5C — Focus ring unification

| File | Old | New |
|------|-----|-----|
| `pages/GlobalOperationList.tsx` (×5) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/Production.tsx` (×1) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/QCCheckpoints.tsx` (×3) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/OEEDeepDive.tsx` (×2) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/APSScheduling.tsx` (×1) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/LoginPage.tsx` (×3) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/ProductionOrderList.tsx` (×6) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/RouteList.tsx` (×4) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/DefectManagement.tsx` (×4) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/RouteDetail.tsx` (×13) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/DispatchQueue.tsx` (×2) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/Traceability.tsx` (×1) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/OperationList.tsx` (×2) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `pages/ProductionTracking.tsx` (×1) | `focus:ring-blue-500` | `focus:ring-focus-ring` |
| `components/GanttChart.tsx` (×2) | `focus:ring-blue-300` / `ring-blue-300` | `focus:ring-focus-ring` / `ring-focus-ring` |

#### 5D — Surface & divider tokens

| File | Old | New |
|------|-----|-----|
| `pages/QCCheckpoints.tsx` | `bg-white divide-y divide-gray-200` | `bg-background divide-y divide-surface-divider` |
| `pages/APSScheduling.tsx` | `bg-white divide-y divide-gray-200` | `bg-background divide-y divide-surface-divider` |
| `pages/DefectManagement.tsx` | `bg-white divide-y divide-gray-200` | `bg-background divide-y divide-surface-divider` |
| `pages/DispatchQueue.tsx` | `bg-white divide-y divide-gray-200` | `bg-background divide-y divide-surface-divider` |
| `pages/Traceability.tsx` | `bg-white divide-y divide-gray-200` | `bg-background divide-y divide-surface-divider` |
| `pages/OEEDeepDive.tsx` | `bg-white divide-y divide-gray-200` | `bg-background divide-y divide-surface-divider` |

### Representative Diff (5A — CTA)

```diff
--- a/frontend/src/app/components/TopBar.tsx
+++ b/frontend/src/app/components/TopBar.tsx
-            className="bg-[#33B2C1] text-white ..."
+            className="bg-brand-cta text-white ..."
```

### Representative Diff (5B — Charts)

```diff
--- a/frontend/src/app/pages/Dashboard.tsx
+++ b/frontend/src/app/pages/Dashboard.tsx
             <CartesianGrid
-              stroke="#e5e7eb"
+              stroke="var(--chart-grid)"
             />
             <XAxis
-              stroke="#6b7280"
+              stroke="var(--chart-axis)"
             />
             <Line
-              stroke="#3b82f6"
+              stroke="var(--chart-1)"
               ...
-              dot={{ fill: '#3b82f6', r: 4 }}
+              dot={{ fill: 'var(--chart-1)', r: 4 }}
             />
```

### Representative Diff (5C — Focus rings)

```diff
--- a/frontend/src/app/pages/GlobalOperationList.tsx
+++ b/frontend/src/app/pages/GlobalOperationList.tsx
-          className="... focus:ring-blue-500 ..."
+          className="... focus:ring-focus-ring ..."
```

### ESLint Boundary Rules

Add to the existing `eslint.config.js` from PR 3:

```javascript
{
  files: ["src/**/*.{ts,tsx}"],
  rules: {
    "no-restricted-syntax": [
      "warn",
      {
        selector: "Literal[value=/#[0-9a-fA-F]{3,8}/]",
        message:
          "Avoid hardcoded hex colors. Use a CSS variable from theme.css or a semantic Tailwind token.",
      },
    ],
  },
},
```

### Verification Checklist

| # | Command | Expected |
|---|---------|----------|
| 1 | `cd frontend && npm run build` | `✓ built` with zero errors |
| 2 | `grep -rn "#33B2C1\|#2a9aa8" src/app/` | zero matches |
| 3 | `grep -rn 'stroke="#3b82f6"\|fill="#3b82f6"' src/app/pages/` | zero matches |
| 4 | `grep -rn "focus:ring-blue-500" src/app/` | zero matches |
| 5 | `grep -rn 'divide-gray-200' src/app/pages/` | zero matches |
| 6 | `npx eslint src/` | zero errors |
| 7 | Visual smoke: open Dashboard, OEE, Station, GlobalOperations — colors identical | no visual diff |

---

## PR 6 — Relocate `ui/utils.ts` to `src/lib/utils.ts`

### Rationale
`cn()` is the only shared utility. It currently lives inside the UI component
folder (`components/ui/utils.ts`), making it part of the shadcn layer. Moving
it to a dedicated `lib/` folder aligns with shadcn/ui conventions and allows
non-UI code to import it without reaching into `components/ui/`.

### File-by-File Change List

| Action | Path | Change |
|--------|------|--------|
| MOVE | `src/app/components/ui/utils.ts` → `src/lib/utils.ts` | Move file |
| CREATE | `src/app/components/ui/utils.ts` | Re-export: `export { cn } from "@/lib/utils"` |
| UPDATE | All 47 `ui/*.tsx` files | No change needed — they import `./utils` which now re-exports |

### Representative Diff

```diff
--- /dev/null
+++ b/frontend/src/lib/utils.ts
@@ -0,0 +1,4 @@
+import { clsx, type ClassValue } from "clsx";
+import { twMerge } from "tailwind-merge";
+
+export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
```

```diff
--- a/frontend/src/app/components/ui/utils.ts
+++ b/frontend/src/app/components/ui/utils.ts
-import { clsx, type ClassValue } from "clsx"
-import { twMerge } from "tailwind-merge"
-
-export function cn(...inputs: ClassValue[]) {
-  return twMerge(clsx(inputs))
-}
+// Re-export for backward compatibility with shadcn/ui components
+export { cn } from "@/lib/utils";
```

### ESLint Boundary Rules

*No new rules. The re-export preserves all existing imports.*

### Verification Checklist

| # | Command | Expected |
|---|---------|----------|
| 1 | `cd frontend && npm run build` | `✓ built` with zero errors |
| 2 | `test -f src/lib/utils.ts` | exists |
| 3 | `grep "cn" src/lib/utils.ts` | function definition present |
| 4 | `grep "export.*cn" src/app/components/ui/utils.ts` | re-export present |

---

## Deferred Items (DO NOT INCLUDE IN ANY PR)

These items were identified during audit but are **uncertain, risky, or
out of scope** for a mechanical refactor.

| Item | Reason for Deferral |
|------|-------------------|
| **Tailwind shade classes for status badges** (`bg-amber-100 text-amber-700`, `bg-red-100 text-red-700`, etc.) in GlobalOperationList, QCCheckpoints | These are used in dynamic status-mapping objects/functions. Replacing them with semantic tokens requires understanding the status enum mapping — **logic-adjacent**, not purely mechanical. |
| **Gradient classes** (`bg-gradient-to-br from-blue-50 to-blue-100`) in StatsCard, Home, Dashboard, APSScheduling | Each gradient has unique directional semantics. Tokenizing gradients requires a design decision on token naming, which is beyond mechanical scope. |
| **Flag SVG colors** in `flags/JapanFlag.tsx`, `flags/UKFlag.tsx` | National flag colors are specification-mandated. Tokenizing them would be incorrect. |
| **`supabase/` directory** deletion | May be needed for Phase 7+. Requires stakeholder decision. **Flag for product owner.** |
| **`data/mockData.ts` and `oee-mock-data.ts`** | Actively imported by pages. Removing requires backend API integration, which is a functional change. |
| **shadcn/ui component internals** (`chart.tsx` stroke colors) | Modifying vendored shadcn components risks breaking their update path. |
| **`use-mobile.ts` relocation** | Currently inside `ui/` but is a hook, not a component. Moving it changes its import semantics, but it's only used by `sidebar.tsx`, so risk/reward is poor. |
| **Dark mode token mapping** for new semantic tokens | Defining dark-mode equivalents for `--status-*`, `--brand-*`, etc. requires design input. |
| **`LoginPage.tsx` specific colors** (`bg-blue-600 hover:bg-blue-700`) | Could map to `bg-primary hover:bg-primary/90` but verifying visual parity requires design review. |
| **StatsCard variant colors** (`from-blue-50`, `from-green-50`, etc.) | Each variant uses a different color pair. Tokenizing these requires a variant token system design. |

---

## PR Dependency Graph

```
PR 1  (dead code cleanup)
  │
  v
PR 2  (barrels + tsconfig paths)
  │
  v
PR 3  (import migration + eslint)
  │
  v
PR 4  (define semantic tokens)  ──  PR 6  (move utils.ts)
  │                                   │
  v                                   v
PR 5  (adopt tokens)            (independent)
```

PRs 1→2→3 are sequential (each depends on prior).
PR 4→5 are sequential.
PR 6 is independent of 4/5 and can merge any time after PR 3.

---

## Global Verification (Run After All PRs Merged)

```bash
# 1. Build check
cd /workspaces/FleziBCG/frontend && npm run build
# Expected: ✓ built, zero errors

# 2. Lint check
cd /workspaces/FleziBCG/frontend && npx eslint src/
# Expected: zero errors, zero warnings

# 3. No hardcoded CTA colors
grep -rn "#33B2C1\|#2a9aa8" src/app/
# Expected: zero matches

# 4. No cross-module relative imports to barrels
grep -rn "from '\.\./auth/\|from '\.\./api/\|from '\.\./impersonation/\|from '\.\./persona/" src/app/
# Expected: zero matches

# 5. No focus:ring-blue-500 outside ui/
grep -rn "focus:ring-blue-500" src/app/pages/ src/app/components/ --include="*.tsx" | grep -v "/ui/"
# Expected: zero matches

# 6. No chart hex colors in pages
grep -rn 'stroke="#[0-9a-f]' src/app/pages/
# Expected: zero matches

# 7. Backend verification scripts (unchanged)
cd /workspaces/FleziBCG/backend
python scripts/verify_users_auth.py
python scripts/verify_approval.py
python scripts/verify_impersonation.py
# Expected: all 34 checks PASS

# 8. Visual smoke test
# Open: /dashboard, /operations, /station-execution, /login
# Verify: identical appearance to pre-refactor
```

## FE Mechanical Refactor – Alignment & Guardrails
```
Refactor này chỉ mang tính cơ học (mechanical): file move/rename, cập nhật import path, tạo barrel exports, thêm lint guardrails, và centralize theme tokens; không thay đổi logic/behavior/UI layout và không upgrade dependencies.
Preserve public APIs: Không thay đổi API contract giữa FE↔BE (endpoint, payload/DTO shape, error model). Nếu phát sinh nhu cầu đổi contract, phải tách thành PR riêng và gắn nhãn“behavior change / contract change” kèm before/after evidence.,
Mock data giữ nguyên trong refactor này: mockData.ts và oee-mock-data.ts vẫn đang được pages sử dụng; việc remove/replace cần backend integration nên không thuộc scope mechanical.
Một số hạng mục được defer vì “logic-adjacent / cần design decision” (status-mapping, gradients, dark-mode mapping, …) và không được đưa vào bất kỳ PR mechanical nào. 
Verification bắt buộc mỗi PR: tối thiểu npm run build pass, và các grep checks/ESLint checks tương ứng PR; cuối chuỗi PR có “global verification”.
```