# MMD-FULLSTACK-08 — Reason Codes FE Read Integration Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Connected Reason Codes frontend screen to backend read APIs (MMD-BE-07). |

---

## Routing

- **Selected brain:** MOM Brain (reason codes are manufacturing master data reference classification truth)
- **Selected mode:** Strict (frontend read integration touching manufacturing reference data with boundary invariant contract)
- **Hard Mode MOM:** v3 ON (reason codes interface with execution downtime, quality, material — UI boundary must be enforced)
- **Reason:** Reason Codes are multi-domain reference classification data. Hard Mode v3 pre-coding evidence was required to prevent boundary violations at the UI layer.

---

## 1. Scope

Connect `frontend/src/app/pages/ReasonCodes.tsx` to the Unified Reason Codes backend read API created in MMD-BE-07 (`GET /v1/reason-codes`, `GET /v1/reason-codes/{id}`).

**Narrow read-only slice.** No write, release, retire, downtime_reason integration, or operational side effects.

---

## 2. Baseline Evidence Used

| Document | Status | Key Finding |
|---|---|---|
| `.github/copilot-instructions.md` | ✅ Read | Entry rule, Hard Mode MOM v3 triggers confirmed |
| `.github/agent/AGENT.md` | ✅ Read | Behavioral guidelines: simplicity, surgical changes |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | ✅ Read | MOM Brain selected for manufacturing domain work |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | ✅ Read | v3 discipline: design evidence extraction before implementation |
| `docs/ai-skills/stitch-design-md-ui-ux/SKILL.md` | ✅ Read | UI/UX boundary principles confirmed |
| `docs/audit/mmd-be-07-reason-code-minimal-read-model.md` | ✅ Read | MMD-BE-07 confirmed complete; 22/22 tests passing |
| `docs/audit/mmd-be-06-reason-code-foundation-contract-boundary-lock.md` | ✅ Read | Boundary decisions: unified catalog, separate from downtime_reason |
| `backend/app/api/v1/reason_codes.py` | ✅ Inspected | API: `GET /reason-codes?domain=&category=&lifecycle_status=&include_inactive=`, `GET /reason-codes/{id}` |
| `backend/app/schemas/reason_code.py` | ✅ Inspected | `ReasonCodeItem`: 14 fields; `lifecycle_status` plain str (DRAFT/RELEASED/RETIRED) |
| `frontend/src/app/pages/ReasonCodes.tsx` | ✅ Inspected | Shell/mock page with inline `mockReasonCodes` array as primary data source |
| `frontend/src/app/screenStatus.ts` | ✅ Inspected | `reasonCodes`: phase=SHELL, dataSource=MOCK_FIXTURE |
| `frontend/src/app/api/index.ts` | ✅ Inspected | Pattern: separate API modules (`productApi`, `routingApi`) exported from index |
| `frontend/src/app/i18n/registry/en.ts` | ✅ Inspected | Existing reason-code keys; missing: col.name, filter.includeInactive, notice.readonly, error.load |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | ✅ Inspected | 67 checks passing; no Reason Codes section existed |

---

## 3. FE/BE Read Contract

| Backend Field | FE Type | UI Display | Decision |
|---|---|---|---|
| `reason_code_id` | `string` | Row key (`key` prop) | Maps from mock `code_id` |
| `tenant_id` | `string` | Not displayed | Internal only, filtered by backend |
| `reason_domain` | `string` | Domain badge (uppercase color map) | Backend value displayed directly |
| `reason_category` | `string` | Category column | Direct display |
| `reason_code` | `string` | Code column (monospaced) | Maps from mock `code` |
| `reason_name` | `string` | Name column (new) | New field; not in mock |
| `description` | `string \| null` | Description column, null-safe (`?? ""`) | Existing column |
| `lifecycle_status` | `"DRAFT" \| "RELEASED" \| "RETIRED"` | LifecycleBadge (green/yellow/gray) | Replaces mock ACTIVE/RETIRED |
| `requires_comment` | `boolean` | Amber/gray dot indicator | Direct map |
| `is_active` | `boolean` | Drives `include_inactive` filter (checkbox) | Not shown as column |
| `sort_order` | `number` | Backend-ordered (not displayed) | Ordering handled server-side |
| `created_at` | `string` | Not displayed | Available for future use |
| `updated_at` | `string` | Not displayed | Available for future use |

**Domain filter:** Dynamic — derived from `reason_domain` values in loaded data. Does not hardcode domain names. Backend default returns RELEASED + active codes only. Frontend default (`include_inactive=false`) aligns with backend default.

---

## 4. Files Changed

| File | Change | Notes |
|---|---|---|
| `frontend/src/app/api/reasonCodeApi.ts` | **Created** | New API module: `ReasonCodeItemFromAPI`, `ListReasonCodesParams`, `reasonCodeApi.listReasonCodes()`, `reasonCodeApi.getReasonCode()` |
| `frontend/src/app/api/index.ts` | **Modified** | Added export of `reasonCodeApi`, `ReasonCodeItemFromAPI`, `ListReasonCodesParams` |
| `frontend/src/app/pages/ReasonCodes.tsx` | **Modified** | Replaced mock data source with backend API; added loading/error/empty states; dynamic domain filter; lifecycle badges; include_inactive checkbox; read-only enforced |
| `frontend/src/app/i18n/registry/en.ts` | **Modified** | Added: `reasonCodes.col.name`, `reasonCodes.filter.includeInactive`, `reasonCodes.notice.readonly`, `reasonCodes.error.load` |
| `frontend/src/app/i18n/registry/ja.ts` | **Modified** | Same 4 keys in Japanese |
| `frontend/src/app/screenStatus.ts` | **Modified** | `reasonCodes` → `PARTIAL / BACKEND_API` |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | **Modified** | Added Section I (17 new checks for Reason Codes read integration) |
| `docs/audit/mmd-fullstack-08-reason-codes-fe-read-integration.md` | **Created** | This audit report |

**No backend files were modified.**

---

## 5. Frontend Changes

### reasonCodeApi.ts (new)
- `ReasonCodeItemFromAPI` interface — 14 fields matching backend `ReasonCodeItem` schema
- `ListReasonCodesParams` — `domain?`, `category?`, `lifecycle_status?`, `include_inactive?`
- `reasonCodeApi.listReasonCodes(params?, signal?)` — builds query string, calls `GET /v1/reason-codes`
- `reasonCodeApi.getReasonCode(reasonCodeId, signal?)` — calls `GET /v1/reason-codes/{id}` with `encodeURIComponent`

### ReasonCodes.tsx (rewritten)
- Removed: `mockReasonCodes` inline array, `useState(mockReasonCodes)`, `MockWarningBanner`, `BackendRequiredNotice`, hardcoded `DOMAINS` array, `Domain` type alias, `StatusBadge`
- Added: `useEffect` with `AbortController` for API call; `loading`, `error`, `codes` state; `useMemo` for domain derivation and filter; `LifecycleBadge` (DRAFT/RELEASED/RETIRED); `includeInactive` checkbox; `reason_name` column; `ScreenStatusBadge phase="PARTIAL"`
- Preserved: All write-action buttons remain `disabled`; layout structure unchanged; column ordering matches user expectation

### Domain filter behavior
- Dropdown options derived from backend-returned `reason_domain` values (not hardcoded)
- Default `"all"` option always present
- When backend returns empty array, dropdown shows only "All Domains"

---

## 6. Backend Verification / Changes

**No backend files were modified.**

Backend verification:
```
cd backend
python -m pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
Result: ✅ 22 passed in 1.42s
```

API contract confirmed from source:
- `GET /v1/reason-codes` — returns `list[ReasonCodeItem]`, filters: `domain`, `category`, `lifecycle_status`, `include_inactive`
- `GET /v1/reason-codes/{reason_code_id}` — returns single `ReasonCodeItem` or 404
- Default: RELEASED + active codes only (aligned with FE default)
- Authentication: `require_authenticated_identity` — tenant-scoped

---

## 7. Screen Status Decision

| Screen | Previous | New | Justification |
|---|---|---|---|
| `reasonCodes` | `SHELL / MOCK_FIXTURE` | `PARTIAL / BACKEND_API` | Backend API read integration active. Create/edit/retire write UI remains disabled (deferred to MMD-BE-08+). `CONNECTED` not claimed — write lifecycle governance not yet implemented. |

---

## 8. Boundary Guardrails

| Invariant | Status | Evidence |
|---|---|---|
| Reason Code is reference/classification truth only | ✅ MAINTAINED | No operational transitions triggered from UI |
| UI does not execute operational transitions | ✅ MAINTAINED | No enabled `onClick` on write-style buttons |
| UI does not own downtime start/end | ✅ MAINTAINED | No `downtime_reason` import; no execution API calls |
| UI does not own quality pass/fail | ✅ MAINTAINED | No quality API calls; no scrap/hold buttons enabled |
| UI does not move material/inventory | ✅ MAINTAINED | No material/inventory API calls |
| UI does not create audit events | ✅ MAINTAINED | Read-only API calls only |
| UI does not replace downtime_reason | ✅ MAINTAINED | `downtime_reason` API untouched; no import in ReasonCodes.tsx |
| Frontend filters are not authorization truth | ✅ MAINTAINED | Filter params passed to backend; backend enforces tenant scope |
| Screen remains read-only | ✅ MAINTAINED | All write buttons remain `disabled` |
| No backend or migration changes | ✅ MAINTAINED | Zero backend files modified |

---

## 9. Regression Coverage

Extended `frontend/scripts/mmd-read-integration-regression-check.mjs` with **17 new checks (Section I)**:

| Check ID | Description |
|---|---|
| I1 | `ReasonCodeItemFromAPI` type exists in `reasonCodeApi.ts` |
| I2 | `listReasonCodes` helper exists in `reasonCodeApi.ts` |
| I3 | `getReasonCode` helper exists in `reasonCodeApi.ts` |
| I4 | `ReasonCodes.tsx` consumes `listReasonCodes` |
| I5 | `ReasonCodes.tsx` does not use inline mock array as primary data source |
| I6 | `reasonCodeApi.ts` supports `domain` and `include_inactive` filters |
| I7 | `screenStatus.ts` `reasonCodes` is `PARTIAL / BACKEND_API` |
| I8 | Create/edit/delete/release/retire write actions remain disabled |
| I9 | No non-comment `downtime_reason` reference in `ReasonCodes.tsx` |
| I10 | No execution/quality/material mutation language in `ReasonCodes.tsx` |
| I11 | `/reason-codes` route still exists in `routes.tsx` |
| I12 | `reasonCodes.col.name` i18n key exists in `en.ts` |
| I13 | `reasonCodes.col.name` i18n key exists in `ja.ts` |
| I14 | `reasonCodes.error.load` i18n key exists in `en.ts` |
| I15 | `reasonCodes.error.load` i18n key exists in `ja.ts` |
| I16 | `reasonCodes.filter.includeInactive` i18n key exists in `en.ts` |
| I17 | `reasonCodes.filter.includeInactive` i18n key exists in `ja.ts` |

All previous 67 checks still pass.

---

## 10. Verification Commands

### MMD Read Regression Script
```
cd frontend
node scripts/mmd-read-integration-regression-check.mjs
Result: ✅ 84 passed, 0 failed
```

### Route Smoke Check
```
cd frontend
node scripts/route-smoke-check.mjs
Result: ✅ /reason-codes COVERED; 0 FAIL
```

### ESLint on Changed Files
```
cd frontend
node node_modules/eslint/bin/eslint.js src/app/api/reasonCodeApi.ts src/app/pages/ReasonCodes.tsx
Result: ✅ No errors
```

### Backend Reason Code Tests
```
cd backend
python -m pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
Result: ✅ 22 passed in 1.42s
```

### TypeScript Check (Scope)
TypeScript check was run across the full frontend codebase. All errors found were **pre-existing** in `AIInsightsDashboard.tsx`, `RouteStatusBanner.tsx`, and unrelated i18n files. **No TypeScript errors in any file modified by MMD-FULLSTACK-08.**

### Build
Full `vite build` was not run to avoid side effects in agent context. TypeScript check and lint on changed files confirm no compilation blockers introduced by this slice.

---

## 11. Remaining Risks / Deferred Items

| Item | Risk | Deferred To |
|---|---|---|
| Reason Code write UI (create/edit/retire) | Low — buttons remain disabled | MMD-BE-08+ |
| Lifecycle state transitions | Low — read model only | MMD-BE-08+ |
| `reason_name` column added — may need responsive treatment at narrow viewports | Very Low — cosmetic | UI polish |
| Domain filter names shown as raw backend values (e.g. "DOWNTIME" not "Downtime") | Low — backend is source of truth for domain names | Design decision; acceptable for PARTIAL phase |
| Pre-existing TypeScript errors in AIInsightsDashboard.tsx | Not introduced by this slice | Separate task |
| `GET /reason-codes/{id}` helper added but not consumed by UI — available for future use | Very Low | Future MMD slice |

---

## 12. Final Verdict

✅ **MMD-FULLSTACK-08 COMPLETE**

- MMD-BE-07 and SQL bootstrap patch confirmed present and verified.
- `ReasonCodeItemFromAPI` type and `reasonCodeApi` helpers created following existing API module pattern.
- `ReasonCodes.tsx` reads backend reason-code API; inline mock fixture removed as primary data source.
- Loading, error, and empty states handled.
- Domain filter (dynamic from backend data), lifecycle_status badge (DRAFT/RELEASED/RETIRED), include_inactive checkbox, and reason_name column all implemented.
- Screen remains read-only; all write-action buttons remain `disabled`.
- `downtime_reason` untouched; no operational side effects.
- `screenStatus.ts` updated to `PARTIAL / BACKEND_API` without overclaiming `CONNECTED`.
- MMD regression script extended: 84/84 checks pass (17 new + 67 existing).
- Backend 22/22 tests pass.
- Route smoke check passes.
- No backend files modified. No migration changes. No auto-commit performed.
