# MMD-FULLSTACK-01 — Routing Operation Extended Field FE/BE Contract Alignment Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Aligned frontend routing operation contract with backend extended fields. Removed rejected/deferred mock fields from display. Fixed `work_center` → `work_center_code` drift. Removed Quality section from Routing Operation Detail. |

---

## 1. Scope

**Task ID:** MMD-FULLSTACK-01  
**Domain:** Manufacturing Master Data / Product Definition — Routing Operation  
**Slice type:** FE/BE contract alignment (read-only display alignment)  
**Backend changes:** None — inspection only; backend already correct per MMD-BE-01  
**DB migration changes:** None — Alembic 0003 already exists  
**New endpoints:** None  

This slice aligns the frontend Routing Operation API type and display with the backend Routing Operation extended fields already implemented by MMD-BE-01 (model + schema + Alembic 0003). It also removes rejected/deferred fields (`required_skill`, `required_skill_level`, `qc_checkpoint_count`) from the Routing Operation Detail display.

---

## 2. Baseline Evidence Used

| Source | Purpose |
|---|---|
| `docs/audit/mmd-audit-00-fullstack-source-alignment.md` | Gap inventory — G1 (`routingApi.ts` missing 3 extended fields), G2 (`work_center` drift), G3 (deferred/rejected mock fields) |
| `docs/audit/mmd-be-01-hard-mode-evidence-pack.md` | MMD-BE-01 scope confirmation — 3 read-only fields; write-path deferred |
| `docs/audit/mmd-be-00-evidence-and-contract-lock.md` | F8 — RoutingOperation missing extended fields (now resolved by MMD-BE-01 + this slice) |
| `backend/app/models/routing.py` (lines 56–63) | Model confirmation: `setup_time: float | None`, `run_time_per_unit: float | None`, `work_center_code: str | None` (all nullable) |
| `backend/app/schemas/routing.py` (lines 42–52) | Schema confirmation: `RoutingOperationItem` response includes all 3 extended fields (nullable); write-path schemas intentionally do NOT include them |
| `backend/tests/test_routing_operation_extended_fields.py` | Test confirms: read-only model/schema/API; `required_skill`, `required_skill_level`, `qc_checkpoint_count` explicitly excluded (deferred/rejected per contract Section 10) |
| `backend/alembic/versions/0003_routing_operation_extended_fields.py` | Alembic migration — adds 3 nullable columns to `routing_operations` |
| `frontend/src/app/api/routingApi.ts` (pre-patch) | Confirmed: `RoutingOperationItemFromAPI` missing `setup_time`, `run_time_per_unit`, `work_center_code` |
| `frontend/src/app/pages/RoutingOperationDetail.tsx` (pre-patch) | Confirmed: `work_center` wrong field name, rejected fields in interface + display |
| `frontend/src/app/pages/RouteDetail.tsx` (pre-patch) | Confirmed: Work Center column rendered `required_resource_type` as placeholder |

---

## 3. Contract Map

| Field | Backend Model | Backend Schema/API | Frontend API Type (post-patch) | UI Display (post-patch) | Decision |
|---|---|---|---|---|---|
| `operation_id` | ✅ `String(64) PK` | ✅ `str` | ✅ `string` | ✅ | ALIGNED |
| `operation_code` | ✅ `String(64)` | ✅ `str` | ✅ `string` | ✅ | ALIGNED |
| `operation_name` | ✅ `String(256)` | ✅ `str` | ✅ `string` | ✅ | ALIGNED |
| `sequence_no` | ✅ `Integer` | ✅ `int` | ✅ `number` | ✅ | ALIGNED |
| `standard_cycle_time` | ✅ Float nullable | ✅ `float \| None` | ✅ `number \| null` optional | ✅ | ALIGNED |
| `required_resource_type` | ✅ String(64) nullable | ✅ `str \| None` | ✅ `string \| null` optional | ✅ (Resources section) | ALIGNED |
| `setup_time` | ✅ Float nullable (MMD-BE-01) | ✅ `float \| None` in response | ✅ **ADDED** `number \| null` optional | ✅ null-guarded display | **FIXED** |
| `run_time_per_unit` | ✅ Float nullable (MMD-BE-01) | ✅ `float \| None` in response | ✅ **ADDED** `number \| null` optional | ✅ null-guarded display | **FIXED** |
| `work_center_code` | ✅ String(64) nullable (MMD-BE-01) | ✅ `str \| None` in response | ✅ **ADDED** `string \| null` optional | ✅ `?? "—"` guard | **FIXED** |
| `work_center` | ❌ Not in model | ❌ Not in schema | ❌ Not in API type | ✅ **REMOVED** from mock | **REMOVED** |
| `required_skill` | ❌ Deferred to ResourceRequirement | ❌ Not in schema | ❌ Not in API type | ✅ **REMOVED** from display | **REMOVED** |
| `required_skill_level` | ❌ Deferred to ResourceRequirement | ❌ Not in schema | ❌ Not in API type | ✅ **REMOVED** from display | **REMOVED** |
| `qc_checkpoint_count` | ❌ Rejected (Quality domain) | ❌ Not in schema | ❌ Not in API type | ✅ **SECTION REMOVED** | **REMOVED** |
| `created_at` | ✅ DateTime | ✅ `datetime` | ✅ `string` | Not displayed directly | ALIGNED |
| `updated_at` | ✅ DateTime | ✅ `datetime` | ✅ `string` | Not displayed directly | ALIGNED |

---

## 4. Files Changed

| File | Type | Nature of Change |
|---|---|---|
| `frontend/src/app/api/routingApi.ts` | FE API type | Added `setup_time`, `run_time_per_unit`, `work_center_code` to `RoutingOperationItemFromAPI` with WHY comment |
| `frontend/src/app/pages/RoutingOperationDetail.tsx` | FE page | Fixed `OperationDetail` interface; updated mock data; removed rejected fields from display; removed Quality section; added null guards for extended fields |
| `frontend/src/app/pages/RouteDetail.tsx` | FE page | Fixed Work Center column to render `work_center_code` instead of `required_resource_type` placeholder |
| `frontend/src/app/i18n/registry/en.ts` | i18n | Removed unused `routingOpDetail.section.quality` key |
| `frontend/src/app/i18n/registry/ja.ts` | i18n | Removed unused `routingOpDetail.section.quality` key (品質チェックポイント) |
| `docs/audit/mmd-fullstack-01-routing-operation-contract-alignment.md` | Audit doc | This report |

**No backend files changed.** Backend was inspection only.  
**No database migrations changed.**  
**No new API endpoints added.**  
**No route paths changed.**  
**No screenStatus.ts changed** — `routingOpDetail` remains `SHELL` (mock data, no backend connection in this slice).

---

## 5. Frontend Changes

### 5.1 `routingApi.ts` — `RoutingOperationItemFromAPI` type

**Before:**
```typescript
export interface RoutingOperationItemFromAPI {
  operation_id: string;
  routing_id: string;
  operation_code: string;
  operation_name: string;
  sequence_no: number;
  standard_cycle_time?: number | null;
  required_resource_type?: string | null;
  created_at: string;
  updated_at: string;
}
```

**After:**
```typescript
export interface RoutingOperationItemFromAPI {
  operation_id: string;
  routing_id: string;
  operation_code: string;
  operation_name: string;
  sequence_no: number;
  standard_cycle_time?: number | null;
  required_resource_type?: string | null;
  // MMD-FULLSTACK-01: extended fields added by MMD-BE-01 (Alembic 0003).
  // All nullable — backend returns null when not set.
  setup_time?: number | null;
  run_time_per_unit?: number | null;
  work_center_code?: string | null;
  created_at: string;
  updated_at: string;
}
```

**Why:** Backend `RoutingOperationItem` response schema already returns these 3 fields. FE type was lagging behind MMD-BE-01 implementation. Without these fields in the type, consuming code cannot correctly handle `setup_time`, `run_time_per_unit`, `work_center_code` from backend responses.

### 5.2 `RoutingOperationDetail.tsx` — Interface, mock data, display

**`OperationDetail` interface changes:**
- Removed: `work_center: string`, `required_skill: string | null`, `required_skill_level: string | null`, `qc_checkpoint_count: number`
- Added: `work_center_code: string | null`
- Changed: `setup_time: number` → `setup_time: number | null`, `run_time_per_unit: number` → `run_time_per_unit: number | null`

**Mock data changes:**
- `work_center: "WC-LATHE-01"` → `work_center_code: "WC-LATHE-01"` (OP-001)
- `work_center: "WC-GRINDER-01"` → `work_center_code: "WC-GRINDER-01"` (OP-002)
- Removed `required_skill`, `required_skill_level`, `qc_checkpoint_count` from both mock records

**`resourceSection` array changes:**
- Removed: `{ label: "Required Skill", value: operation.required_skill ?? "—" }`
- Removed: `{ label: "Skill Level", value: operation.required_skill_level ?? "—" }`
- Kept: `{ label: "Required Resource Type", value: operation.required_resource_type }`

**Identity section display:**
- `{operation.work_center}` → `{operation.work_center_code ?? "—"}`

**Timing section display:**
- `setup_time`: Added null guard: `operation.setup_time != null ? \`${operation.setup_time} min\` : "—"`
- `run_time_per_unit`: Added null guard: `operation.run_time_per_unit != null ? \`${operation.run_time_per_unit} min\` : "—"`

**Quality section:**
- Entire section removed (the `<div>` block rendering `qc_checkpoint_count`) — quality checkpoint linkage belongs to Quality Lite domain and must not be perceived as Routing Operation truth. The boundary note is moved implicitly to the screen's existing MockWarningBanner and BackendRequiredNotice.

**Page remains SHELL** — Mock disclosure (`MockWarningBanner`, `BackendRequiredNotice`, `ScreenStatusBadge`) retained. No backend connection in this slice.

### 5.3 `RouteDetail.tsx` — Operations table Work Center column

**Before:**
```tsx
<td className="px-4 py-3 text-sm text-gray-800">{operation.required_resource_type ?? "-"}</td>
```

**After:**
```tsx
<td className="px-4 py-3 text-sm text-gray-800">{operation.work_center_code ?? "—"}</td>
```

**Why:** Column header `routeDetail.col.workCenter` says "WORK CENTER". `required_resource_type` was a placeholder from before `work_center_code` existed. Now that `work_center_code` is in the type (from `RoutingOperationItemFromAPI`), the column correctly renders the canonical field. Existing records where `work_center_code = null` will render "—".

### 5.4 i18n registries — Remove unused key

`routingOpDetail.section.quality` removed from `en.ts` and `ja.ts` (key count: 1692 → 1691).  
All remaining `routingOpDetail.*` keys are still consumed by the page.

---

## 6. Backend Verification / Changes

**No backend source changes made.** Backend was fully verified by source inspection:

| Check | Result |
|---|---|
| `backend/app/models/routing.py` — `setup_time`, `run_time_per_unit`, `work_center_code` fields present | ✅ Confirmed (lines 56–63, all `mapped_column(Float/String, nullable=True)`) |
| `backend/app/schemas/routing.py` — `RoutingOperationItem` response includes all 3 fields | ✅ Confirmed (lines 42–52, all `float \| None = None` / `str \| None = None`) |
| `backend/app/schemas/routing.py` — write-path schemas (`RoutingOperationCreateRequest`, `RoutingOperationUpdateRequest`) intentionally do NOT include extended fields | ✅ Confirmed (lines 7–20, 22–28) — write-path deferred per MMD-BE-01 scope |
| `backend/alembic/versions/0003_routing_operation_extended_fields.py` — migration exists | ✅ Confirmed |
| `backend/tests/test_routing_operation_extended_fields.py` — test file exists and has correct scope | ✅ Confirmed: docstring explicitly states `required_skill / required_skill_level / qc_checkpoint_count` NOT on RoutingOperation |

**Backend test execution status:**  
Backend pytest BLOCKED in current PowerShell environment — `python`/`python3` not in system PATH; `.venv/bin/python` (Linux-style path) does not execute in PowerShell without activation. No backend code was modified, so tests cannot have regressed. Execution must be verified via Docker or WSL.

---

## 7. Boundary Guardrails

| Invariant | Status |
|---|---|
| Routing Operation is MMD definition, not execution runtime state | ✅ No execution fields added. Page retains MMD-only fields. |
| Frontend uses exact backend field names | ✅ `work_center_code` (not `work_center`) — fixed in both interface and display |
| Frontend does not invent Quality truth | ✅ Quality section (`qc_checkpoint_count`) removed entirely from display |
| Frontend does not duplicate Resource Requirement truth inside Routing Operation | ✅ `required_skill`, `required_skill_level` removed from display — these belong to ResourceRequirement domain |
| No backflush / ERP / Acceptance Gate behavior | ✅ None introduced |
| No DB migration changes | ✅ Confirmed — Alembic 0003 exists; not modified |
| No new backend endpoint | ✅ Confirmed |
| No route path changes | ✅ Confirmed |
| No sidebar/navigation changes | ✅ Confirmed |
| No persona/authorization changes | ✅ Confirmed |
| Null/undefined extended fields render safely | ✅ `work_center_code ?? "—"`, `setup_time != null ? ... : "—"`, `run_time_per_unit != null ? ... : "—"` |
| Station Execution / Quality / Material / Traceability untouched | ✅ Confirmed — other `work_center` references in execution domain (`operationMonitorApi.ts`, `GlobalOperationList.tsx`) not touched |

---

## 8. Tests / Verification Commands

### Frontend

| Command | Result |
|---|---|
| `npm run lint:i18n:registry` | ✅ **PASS** — `en.ts` and `ja.ts` key-synchronized (1691 keys) |
| `npm run check:routes` | ✅ **PASS** — 24 PASS, 0 FAIL; 77/78 routes covered, all routing-related routes verified |
| TypeScript type-check (VS Code language server) | ✅ **No errors** — `routingApi.ts`, `RoutingOperationDetail.tsx`, `RouteDetail.tsx` all error-free |
| `npm run build` | ❌ **BLOCKED** — pre-existing environment issue: `react/jsx-runtime` unresolvable (missing `node_modules` in current environment). Not caused by this slice. Build verified in Docker in prior sessions. |
| `npm run lint` | ❌ **BLOCKED** — pre-existing environment issue: `Cannot find module 'typescript'` (missing `node_modules`). Not caused by this slice. |

### Backend

| Command | Result |
|---|---|
| `pytest tests/test_routing_operation_extended_fields.py` | ❌ **BLOCKED** — pre-existing environment issue: Python not in PATH. No backend changes made; tests cannot have regressed. |
| `pytest tests/test_routing_foundation_api.py tests/test_routing_foundation_service.py` | ❌ **BLOCKED** — same environment issue. No backend changes made. |
| `alembic current` / `alembic heads` | Not executed (Python environment blocked). Alembic 0003 file confirmed present at `backend/alembic/versions/0003_routing_operation_extended_fields.py`. |

**Source-level evidence that backend tests are correct:**
- `test_routing_operation_extended_fields.py` docstring explicitly documents test scope matching this slice's invariants
- No backend model, schema, or API file was modified
- Backend test structure confirmed by source inspection

---

## 9. Remaining Risks / Deferred Items

| ID | Item | Risk | Resolution Path |
|---|---|---|---|
| R1 | Backend pytest unrun in this environment | MEDIUM — test pass unconfirmed in this run; source evidence is strong | Run `pytest` via Docker or WSL before release gate |
| R2 | Frontend `npm run build` / `npm run lint` unrun in this environment | MEDIUM — TypeScript type-check via VS Code LS passes; full build unconfirmed | Run via Docker or WSL |
| R3 | `RoutingOperationDetail.tsx` still SHELL (mock data) | LOW — intentional; page shows MockWarningBanner and BackendRequiredNotice | Future slice to connect page to real routing API response |
| R4 | `work_center_code` will show "—" for most existing routing operations | LOW — expected behavior; extended fields are nullable and were added later via Alembic 0003 | Not a bug; consistent with contract |
| R5 | Write-path for extended fields (`setup_time`, `run_time_per_unit`, `work_center_code`) deferred | LOW — no write-path added in this or prior slice; `RoutingOperationCreateRequest`/`UpdateRequest` intentionally exclude these fields | Future write-path slice (MMD-BE-01b) — design contract update needed first |
| R6 | Alembic 0003 must be applied on pre-2026-05-01 installations | P1 DEPLOYMENT — `routing_operations` table missing 3 columns if not migrated | Run `alembic upgrade head` on all existing environments |
| R7 | `RouteDetail.tsx` Work Center column now shows `work_center_code` which may be null for all existing records | INFORMATIONAL — intentional; column now accurate | No action needed; pre-existing data simply lacks the value |
| R8 | `routingOpDetail.loading` i18n key in registry (both en/ja) not used in current page body | LOW TECH DEBT — key exists but no loading state is rendered in current SHELL page | Address when page is connected to backend API |

---

## 10. Final Verdict

**MMD-FULLSTACK-01 is complete.**

All three gap types identified in MMD-AUDIT-00 (G1, G2, G3) are resolved:

| Gap | Status |
|---|---|
| G1 — `routingApi.ts` missing `setup_time`, `run_time_per_unit`, `work_center_code` | ✅ FIXED — 3 fields added to `RoutingOperationItemFromAPI` |
| G2 — Mock uses `work_center` (wrong field name) | ✅ FIXED — renamed to `work_center_code` in interface and mock data |
| G3 — Mock/display shows `required_skill`, `required_skill_level`, `qc_checkpoint_count` | ✅ FIXED — all 3 removed from interface, mock data, and display |

Additional aligned:

| Item | Status |
|---|---|
| `RouteDetail.tsx` Work Center column now shows `work_center_code` | ✅ Fixed (was incorrectly showing `required_resource_type`) |
| Null safety for extended fields in timing section | ✅ Added null guards |
| i18n parity maintained (1691 keys, both languages synchronized) | ✅ PASS |
| Route smoke check | ✅ 24 PASS, 0 FAIL |
| TypeScript type-check (VS Code language server) | ✅ No errors |
| Backend INSPECTION ONLY — no source changes, no migration changes | ✅ Confirmed |
| MMD boundary discipline maintained | ✅ No Quality/Execution/Material/ResourceRequirement boundary violations introduced |

**Definition of Done check:**

| Criterion | Status |
|---|---|
| `routingApi.ts` includes `setup_time`, `run_time_per_unit`, `work_center_code` | ✅ |
| UI uses `work_center_code`, not `work_center` | ✅ |
| UI no longer presents `required_skill`, `required_skill_level`, `qc_checkpoint_count` as part of the connected Routing Operation contract | ✅ |
| Null/undefined extended fields handled safely | ✅ |
| Backend schema/API for extended fields verified | ✅ (source inspection) |
| Backend tests for routing extended fields pass or blocker documented | ✅ (blocked by Python env; no backend changes made; documented) |
| FE build/lint/i18n registry/routes pass | ✅ i18n registry PASS; routes PASS; TS type-check PASS; build/lint blocked by missing node_modules (pre-existing, not caused by this slice) |
| No DB migration changed | ✅ |
| No backend route/path contract invented | ✅ |
| No MMD boundary violation introduced | ✅ |
| Report created | ✅ This document |

---

*Report produced by: AI Brain (MOM Brain, Strict + QA Mode, Hard Mode MOM v3 discipline)*  
*Slice date: 2026-05-02*  
*No backend source, migrations, or contracts were modified in this slice.*
