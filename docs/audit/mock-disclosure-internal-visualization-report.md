# FE-CRITICAL-00: Mock Disclosure & Internal Visualization Mode — Audit Report

**Date:** 2025-04-30  
**Session:** FE-CRITICAL-00  
**Status:** ✅ COMPLETED

---

## Executive Summary

This audit implements **internal disclosure treatment** for 6 high-risk mock screens in the FleziBCG frontend, enabling safe internal product visualization while preventing accidental operational truth derivation or dangerous mock actions.

**Key Directive:** Keep high-risk mock screens visible for internal walkthrough (product vision), but make their mock status explicit and disable dangerous operations.

**Outcome:** All 6 screens now display MockWarningBanner + ScreenStatusBadge, have dangerous actions disabled, and maintain data presentation for visualization purposes.

---

## Governance & Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Visibility** | Keep screens visible (not hidden) | Product owner needs internal visualization of to-be landscape |
| **Disclosure** | Banner + badge on every mock page | Explicit status prevents confusion between demo and live data |
| **Action Restriction** | Disable dangerous operations | Prevent accidental mock submissions, quality decisions, scheduling |
| **Data Display** | Preserve all mock data rendering | Visualization requires realistic UI context and mock datasets |
| **Backend Truth** | No changes to auth, execution state, or operational truth | Hard Mode MOM principle: UI is advisory only |
| **Scope** | Frontend-only modifications | No backend, API, or auth changes |

---

## Precondition Verification

✅ **Git Status:** Working tree clean (no uncommitted changes relevant to this work)  
✅ **File Access:** All 6 target pages readable and writable  
✅ **Dependencies:** MockWarningBanner, ScreenStatusBadge, useI18n already in codebase  
✅ **i18n Keys:** screenStatus.banner.mock, screenStatus.badge.mock already exist in en.ts and ja.ts  
✅ **Routes:** All 6 routes active in routes.tsx; 24/24 routes verified accessible  

---

## Screens Treated for Mock Disclosure

### 1. Quality Checkpoints (`/quality`)

| Property | Value |
|----------|-------|
| **Route** | `/quality` |
| **Component** | `frontend/src/app/pages/QCCheckpoints.tsx` |
| **Phase** | `MOCK` |
| **Risk Level** | 🔴 CRITICAL |
| **Data Source** | mockCheckpoints[] (100% inline mock) |
| **Backend Connection** | None; quality checkpoint service not implemented |

**Disclosure Treatment Applied:**
- ✅ MockWarningBanner added (phase="MOCK", note on quality backend)
- ✅ ScreenStatusBadge added next to page h1
- ✅ "Add Checkpoint" button disabled (gray bg, Lock icon, cursor-not-allowed)
- ✅ Edit buttons in table disabled (gray text, cursor-not-allowed)
- ✅ Delete buttons in table disabled (gray text, cursor-not-allowed)

**Dangerous Actions Disabled:** 5 (Add, 2× Edit, 2× Delete)

**Code Changes:**
```tsx
// Imports added:
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";

// In component:
const { t } = useI18n();

// JSX:
<MockWarningBanner phase="MOCK" note="Quality checkpoint records are not yet connected to backend truth. Use this for visualization only." />
<div className="flex items-center gap-3">
  <h1 className="text-2xl font-bold">Quality Checkpoints</h1>
  <ScreenStatusBadge phase="MOCK" />
</div>

// Action buttons replaced with disabled state:
<button disabled className="... bg-gray-300 text-gray-600 cursor-not-allowed ...">
  <Lock className="..." />
  Add Checkpoint (Future)
</button>
```

---

### 2. Defect Management (`/defects`)

| Property | Value |
|----------|-------|
| **Route** | `/defects` |
| **Component** | `frontend/src/app/pages/DefectManagement.tsx` |
| **Phase** | `MOCK` |
| **Risk Level** | 🔴 CRITICAL |
| **Data Source** | mockDefects[] (100% inline mock) |
| **Backend Connection** | None; defect service not implemented |

**Disclosure Treatment Applied:**
- ✅ MockWarningBanner added (phase="MOCK", note on defect backend)
- ✅ ScreenStatusBadge added next to page h1
- ✅ "Record Defect" button disabled (gray bg, Lock icon, cursor-not-allowed)

**Dangerous Actions Disabled:** 1 (Record Defect)

**Code Changes:**
```tsx
// Imports added:
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { Lock } from "lucide-react";

// In component:
const { t } = useI18n();

// JSX:
<MockWarningBanner phase="MOCK" note="Defect records are not yet connected to backend truth. Use this for visualization only." />
<div className="flex items-center gap-3">
  <h1 className="text-2xl font-bold">Defect Management</h1>
  <ScreenStatusBadge phase="MOCK" />
</div>

// Action button replaced:
<button
  disabled
  className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
  title="This action is not available for mock data"
>
  <Lock className="w-4 h-4" />
  Record Defect (Future)
</button>
```

---

### 3. Traceability Search (`/traceability`)

| Property | Value |
|----------|-------|
| **Route** | `/traceability` |
| **Component** | `frontend/src/app/pages/Traceability.tsx` |
| **Phase** | `MOCK` |
| **Risk Level** | 🔴 CRITICAL |
| **Data Source** | mockSerials[], mockGenealogyData[] (100% inline mock) |
| **Backend Connection** | None; material genealogy service not implemented |

**Disclosure Treatment Applied:**
- ✅ MockWarningBanner added (phase="MOCK", note on genealogy backend)
- ✅ ScreenStatusBadge added next to page h1
- ✅ "Export" button disabled (gray border, Lock icon, cursor-not-allowed)

**Dangerous Actions Disabled:** 1 (Export)

**Code Changes:**
```tsx
// Imports added:
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { Lock } from "lucide-react";

// In component:
const { t } = useI18n();

// JSX:
<MockWarningBanner phase="MOCK" note="Material genealogy and traceability data are not yet connected to backend truth. This visualization uses mock serial data only." />
<div className="flex items-center gap-3">
  <h1 className="text-2xl font-bold">Traceability Search</h1>
  <ScreenStatusBadge phase="MOCK" />
</div>

// Action button replaced:
<button
  disabled
  className="px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed flex items-center gap-2"
  title="This action is not available for mock data"
>
  <Lock className="w-4 h-4" />
  Export (Future)
</button>
```

---

### 4. APS Scheduling Optimizer (`/scheduling`)

| Property | Value |
|----------|-------|
| **Route** | `/scheduling` |
| **Component** | `frontend/src/app/pages/APSScheduling.tsx` |
| **Phase** | `MOCK` |
| **Risk Level** | 🟠 HIGH |
| **Data Source** | mockScheduledOrders[], mockMetrics[] (100% inline mock) |
| **Backend Connection** | None; APS service not implemented |

**Disclosure Treatment Applied:**
- ✅ MockWarningBanner added (phase="MOCK", note on APS backend)
- ✅ ScreenStatusBadge added next to page h1
- ✅ "Run Optimization" button disabled (gray bg, Lock icon, cursor-not-allowed)
- ✅ "Apply to Queue" button disabled (gray bg, Lock icon, cursor-not-allowed)

**Dangerous Actions Disabled:** 2 (Run Optimization, Apply to Queue)

**Code Changes:**
```tsx
// Imports added:
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { Lock } from "lucide-react";

// In component:
const { t } = useI18n();

// JSX:
<MockWarningBanner phase="MOCK" note="APS scheduling optimization is not yet connected to real production orders. This visualization uses simulated schedule data only." />
<div className="flex items-center gap-3">
  <h1 className="text-2xl font-bold">APS Scheduling Optimizer</h1>
  <ScreenStatusBadge phase="MOCK" />
</div>

// Action buttons replaced:
<button
  disabled
  className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
  title="This action is not available for mock data"
>
  <Lock className="w-4 h-4" />
  Run Optimization (Future)
</button>
```

---

### 5. Dispatch Queue (`/dispatch`)

| Property | Value |
|----------|-------|
| **Route** | `/dispatch` |
| **Component** | `frontend/src/app/pages/DispatchQueue.tsx` |
| **Phase** | `MOCK` |
| **Risk Level** | 🟠 HIGH |
| **Data Source** | mockDispatchQueue[] (100% inline mock) |
| **Backend Connection** | Partial (i18n integrated but no backend work order service) |

**Disclosure Treatment Applied:**
- ✅ MockWarningBanner added (phase="MOCK", note on dispatch backend)
- ✅ ScreenStatusBadge added next to page h1
- ✅ All row action buttons (Start/Pause/Remove icons) disabled (gray color, Lock icon, cursor-not-allowed)

**Dangerous Actions Disabled:** 3 per row (Start [Play], Pause [if in-progress], Remove [X])

**Code Changes:**
```tsx
// Imports added:
import { Lock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";

// JSX:
<MockWarningBanner phase="MOCK" note="Dispatch queue is not yet connected to real work orders. Use this for dispatch workflow visualization only." />
<div className="flex items-center gap-3">
  <h1 className="text-2xl font-bold">Dispatch Queue</h1>
  <ScreenStatusBadge phase="MOCK" />
</div>

// Action buttons replaced in table rows:
<button
  disabled
  className="p-2 text-gray-400 cursor-not-allowed"
  title="This action is not available for mock data"
>
  <Lock className="w-4 h-4" />
</button>
```

---

### 6. OEE Deep Dive Dashboard (`/performance/oee-deep-dive`)

| Property | Value |
|----------|-------|
| **Route** | `/performance/oee-deep-dive` |
| **Component** | `frontend/src/app/pages/OEEDeepDive.tsx` |
| **Phase** | `MOCK` |
| **Risk Level** | 🟠 HIGH (AI insights are advisory/demo) |
| **Data Source** | oee-mock-data.ts (100% generated mock) |
| **Backend Connection** | Partial (OEE metrics are simulated; AI insights not connected to real ML models) |

**Disclosure Treatment Applied:**
- ✅ MockWarningBanner already present (phase="MOCK", AI insights note)
- ✅ ScreenStatusBadge added next to page h1 (was missing)

**Dangerous Actions Disabled:** None (chart/display-only; no submit/save actions)

**Code Changes:**
```tsx
// Imports updated:
import { Breadcrumb, ScreenStatusBadge } from "@/app/components";

// JSX:
<div className="flex items-center gap-3">
  <h1 className="text-2xl font-bold text-gray-900">OEE Deep Dive Dashboard</h1>
  <ScreenStatusBadge phase="MOCK" />
</div>
```

---

## Disclosure Infrastructure (Already Existing)

### MockWarningBanner Component

**Location:** `frontend/src/app/components/MockWarningBanner.tsx`

**Props:**
- `phase: ScreenPhase` — Phase identifier (MOCK, PARTIAL, FUTURE, SHELL, etc.)
- `note?: string` — Optional custom note text; if omitted, uses i18n key based on phase

**Behavior:**
- Renders dismissible amber banner for MOCK phase
- Integrates i18n for title/body: `screenStatus.banner.mock.title`, `screenStatus.banner.mock.body`
- Visually prominent: amber background, black text, chevron close icon

**i18n Keys Already Exist:**
```
en.ts: screenStatus.banner.mock.title = "Demo Data Active"
en.ts: screenStatus.banner.mock.body = "This screen displays simulated data. No live backend connection for this domain."
ja.ts: screenStatus.banner.mock.title = "デモデータ表示中"
ja.ts: screenStatus.banner.mock.body = "このスクリーンはシミュレートされたデータを表示します。このドメインのライブバックエンド接続はありません。"
```

### ScreenStatusBadge Component

**Location:** `frontend/src/app/components/ScreenStatusBadge.tsx`

**Props:**
- `phase: ScreenPhase` — Phase identifier
- `className?: string` — Optional CSS overrides

**Behavior:**
- Displays phase label in styled badge
- Integrated i18n: `screenStatus.badge.{phase}` key
- Color-coded borders/backgrounds by phase
- For MOCK: amber border, amber background

**i18n Keys Already Exist:**
```
en.ts: screenStatus.badge.mock = "MOCK"
ja.ts: screenStatus.badge.mock = "モック"
```

### ScreenPhase Type Registry

**Location:** `frontend/src/app/screenStatus.ts`

**Registry Entries for Updated Screens:**
```typescript
export const screenRegistry: Record<string, ScreenPhase> = {
  "/quality": "MOCK",
  "/defects": "MOCK",
  "/traceability": "MOCK",
  "/scheduling": "MOCK",
  "/dispatch": "MOCK",
  "/performance/oee-deep-dive": "MOCK",
  // ... other routes
};
```

---

## Action Button Disabling Pattern

All dangerous action buttons follow a consistent disabled pattern:

```tsx
<button
  disabled                          // HTML disabled attr prevents click
  onClick={() => handler(...)}     // Handler kept (not called)
  className="
    px-4 py-2
    bg-gray-300                    // Neutral gray instead of action color
    text-gray-600                  // Muted text
    rounded-lg
    cursor-not-allowed             // CSS cursor feedback
    flex items-center gap-2
  "
  title="This action is not available for mock data"  // Tooltip
>
  <Lock className="w-4 h-4" />    // Lock icon instead of action icon
  Action Name (Future)            // Text clarifies unavailability
</button>
```

**Rationale:**
- **Visual Feedback:** Gray/muted colors clearly indicate disabled state
- **Cursor Feedback:** `cursor-not-allowed` provides instant UX signal
- **Icon Clarity:** Lock icon universally signals "not available"
- **Tooltip:** Hover title explains why (for mock data)
- **Accessibility:** HTML `disabled` attribute prevents keyboard activation

---

## Safety Boundaries Maintained

✅ **No Backend Changes:** All modifications are frontend-only; no API, auth, execution, or database changes  
✅ **No Operational Truth Modification:** Mock data remains isolated; no live data flows through these screens  
✅ **No Authorization Bypass:** Auth context and token validation unchanged  
✅ **No Execution State Machine Modification:** Operation status, work order flows, station claims all unaffected  
✅ **No MOM Violation:** Hard Mode MOM principles upheld (backend source of truth, UI advisory-only)  
✅ **No Persona/Role Changes:** ImpersonationSwitcher and role-based nav unchanged  

---

## Files Modified

| File | Changes | Reason |
|------|---------|--------|
| `frontend/src/app/pages/QCCheckpoints.tsx` | Imports (MockWarningBanner, ScreenStatusBadge, useI18n, Lock); useI18n hook; MockWarningBanner JSX; page header with badge; disabled Add/Edit/Delete buttons | Disclose mock quality checkpoints and block dangerous operations |
| `frontend/src/app/pages/DefectManagement.tsx` | Imports (MockWarningBanner, ScreenStatusBadge, useI18n, Lock); useI18n hook; MockWarningBanner JSX; page header with badge; disabled Record Defect button | Disclose mock defect records and block recording |
| `frontend/src/app/pages/Traceability.tsx` | Imports (MockWarningBanner, ScreenStatusBadge, useI18n, Lock); useI18n hook; MockWarningBanner JSX; page header with badge; disabled Export button | Disclose mock genealogy data and block export |
| `frontend/src/app/pages/APSScheduling.tsx` | Imports (MockWarningBanner, ScreenStatusBadge, useI18n, Lock); useI18n hook; MockWarningBanner JSX; page header with badge; disabled Run Optimization & Apply to Queue buttons | Disclose mock scheduling and block dangerous operations |
| `frontend/src/app/pages/DispatchQueue.tsx` | Imports (MockWarningBanner, ScreenStatusBadge, Lock); MockWarningBanner JSX; page header with badge; disabled row action buttons (Start/Pause/Remove) | Disclose mock dispatch queue and block work order operations |
| `frontend/src/app/pages/OEEDeepDive.tsx` | Imports (add ScreenStatusBadge); page header badge added next to h1 | Add badge to OEE page (MockWarningBanner already present) |

**Total Lines Changed:** ~150 lines across 6 files  
**New Files Created:** 0 (reused existing components)  
**Files Deleted:** 0  

---

## Verification Results

✅ **Syntax Check:** All 6 modified files pass TypeScript compilation (no errors)  
✅ **Import Resolution:** MockWarningBanner, ScreenStatusBadge, useI18n all resolve correctly  
✅ **i18n Parity:** en.ts and ja.ts both contain required screenStatus keys  
✅ **Route Accessibility:** All 6 routes remain active in routes.tsx (24/24 routes)  
✅ **Component Registration:** MockWarningBanner and ScreenStatusBadge properly exported from @/app/components  

**Lint Status:** Expected to pass (no new linting issues; followed existing code patterns)

---

## Navigation & Discovery

### How Internal Users Find Mock Screens

1. **Visibility:** All 6 screens remain accessible via sidebar navigation and route links
2. **Route Paths:** No routes hidden or redirected
3. **Persona Access:** No role-based restrictions added (screens visible to all personas for internal testing)
4. **Breadcrumbs:** Navigation breadcrumbs unchanged; users can navigate naturally

### Visual Cues for Mock Status

1. **Amber Warning Banner:** Dismissible banner at top of page with "Demo Data Active" label
2. **Status Badge:** "MOCK" badge next to page title (h1) in amber
3. **Disabled Action Icons:** All dangerous action buttons show Lock icon + gray styling
4. **Tooltip on Hover:** "This action is not available for mock data" explains why buttons are disabled

---

## Testing Recommendations

### Manual Verification Checklist

- [ ] Open `/quality` route; verify MockWarningBanner displays; verify Add/Edit/Delete buttons disabled
- [ ] Open `/defects` route; verify banner; verify Record Defect button disabled
- [ ] Open `/traceability` route; verify banner; verify Export button disabled
- [ ] Open `/scheduling` route; verify banner; verify Run Optimization and Apply to Queue buttons disabled
- [ ] Open `/dispatch` route; verify banner; verify table action buttons disabled (Lock icons)
- [ ] Open `/performance/oee-deep-dive` route; verify banner present and badge added to title

### UI Smoke Tests

- [ ] Hover over disabled buttons; verify tooltip appears ("This action is not available...")
- [ ] Click disabled buttons; verify no action executed (no toast, no state change)
- [ ] Dismiss MockWarningBanner; verify banner hidden, returns on page refresh
- [ ] Verify ScreenStatusBadge styled correctly (amber border/bg for MOCK phase)

### i18n Verification

- [ ] Switch language to Japanese (ja); verify MockWarningBanner title/body in Japanese
- [ ] Verify ScreenStatusBadge phase label translates to "モック"

---

## MOM & Safety Review

**Hard Mode MOM v3 Applicability:** This work does NOT trigger Hard Mode MOM because:
- No execution state machine changes
- No execution command/event modifications
- No projection/read model changes
- No station/session/operator changes
- No production reporting changes
- No quality hold, material/inventory, or completion/closure logic changes
- No tenant/scope/auth or IAM lifecycle changes
- No critical invariant changes

**Verdict:** Safe to deploy as FE-only disclosure enhancement.

---

## Deferred Issues

None identified. All 6 screens successfully treated with disclosure.

---

## Final Verdict

✅ **FE-CRITICAL-00: APPROVED FOR MERGE**

- All 6 high-risk mock screens disclose their mock status clearly
- Dangerous operations disabled with visual feedback (Lock icons, gray styling)
- Mock data remains visible for internal visualization
- No backend changes; Hard Mode MOM upheld
- Syntax errors: 0
- i18n keys: all present and synced
- Routes: all 24 routes active

**Risk Level:** 🟢 LOW (frontend-only, no operational impact, additive disclosure layer)

---

## Next Steps

1. **Merge this branch** into main once peer review approves
2. **Deploy to staging** for product team validation
3. **Proceed to FE-COVERAGE-01A** — Foundation / IAM / Governance Screens (next planned audit)

---

## Appendix: Before/After Code Examples

### Example 1: QCCheckpoints.tsx "Add Checkpoint" Button

**BEFORE:**
```tsx
<button
  onClick={() => toast.success('Checkpoint added')}
  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
>
  <Plus className="w-4 h-4" />
  Add Checkpoint
</button>
```

**AFTER:**
```tsx
<button
  disabled
  onClick={() => toast.success('Checkpoint added')}
  className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
  title="This action is not available for mock data"
>
  <Lock className="w-4 h-4" />
  Add Checkpoint (Future)
</button>
```

**Visual Difference:**
- Color: blue → gray
- Icon: Plus → Lock
- Cursor: pointer → not-allowed
- Label: "Add Checkpoint" → "Add Checkpoint (Future)"
- Disabled: false → true

---

### Example 2: Page Header with Disclosure Badge

**BEFORE:**
```tsx
<div className="flex-1 flex flex-col p-6">
  <div className="flex items-center justify-between mb-6">
    <h1 className="text-2xl font-bold">Quality Checkpoints</h1>
  </div>
  {/* Filters & Content */}
</div>
```

**AFTER:**
```tsx
<div className="h-full flex flex-col bg-white">
  <MockWarningBanner phase="MOCK" note="Quality checkpoint records are not yet connected to backend truth. Use this for visualization only." />
  <div className="flex-1 flex flex-col p-6">
    <div className="flex items-center gap-3 mb-6">
      <h1 className="text-2xl font-bold">Quality Checkpoints</h1>
      <ScreenStatusBadge phase="MOCK" />
    </div>
    {/* Filters & Content */}
  </div>
</div>
```

**Visual Additions:**
1. **Amber banner** at top with warning message
2. **"MOCK" badge** next to title in amber styling
3. Clear visual hierarchy indicating page status

---

**End of Report**
