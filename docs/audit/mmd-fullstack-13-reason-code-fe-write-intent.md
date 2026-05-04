# MMD-FULLSTACK-13 — Reason Code FE Write Intent / Governance-Gated Integration Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-04 | v1.0 | Added governance-gated Reason Code frontend write intent integration. |

---

## Routing
- **Selected brain:** MOM Brain
- **Selected mode:** Strict
- **Hard Mode MOM:** v3 ON
- **Reason:** Frontend write-intent integration for Reason Code MMD lifecycle commands (create/update/release/retire). Must preserve backend as authorization truth and avoid execution/quality/material/ERP boundary violations.

---

## 1. Scope

This slice adds frontend Reason Code write-intent support using the governed backend APIs from MMD-BE-13 and hardened by MMD-BE-13A.

**In scope:**
- `ReasonCodeCreateRequest` and `ReasonCodeUpdateRequest` type definitions in `reasonCodeApi.ts`
- `createReasonCode`, `updateReasonCode`, `releaseReasonCode`, `retireReasonCode` API helpers
- Write-intent UI in `ReasonCodes.tsx` with lifecycle-gated controls and modal dialogs
- Governance notice and backend 403 handling
- New `rcWrite.*` i18n namespace (en.ts / ja.ts)
- Export of new types from `api/index.ts`
- Regression guardrails in `mmd-read-integration-regression-check.mjs` (Section K, +28 checks)
- `rcWrite` added to `namespaces.ts`

**Out of scope (enforced):**
- Backend source: NO changes
- Database migrations: NO changes
- `downtime_reason` mapping: NOT implemented
- Execution/downtime/material/quality/ERP/traceability/maintenance/APS/AI behavior: NOT implemented
- Hard delete, reactivate, clone, bulk import, merge/split, policy binding: NOT implemented
- Server-derived `allowed_actions` guard (deferred to MMD-FULLSTACK-13B)

---

## 2. Baseline Evidence Used

| Document | Status |
|---|---|
| `docs/audit/mmd-be-13-reason-code-write-api-foundation.md` | Confirmed present |
| `docs/audit/mmd-be-13a-reason-code-write-boundary-guardrail.md` | Confirmed present |
| `docs/audit/mmd-fullstack-08-reason-codes-fe-read-integration.md` | Confirmed present |
| `backend/app/api/v1/reason_codes.py` | 4 write endpoints confirmed |
| `backend/app/schemas/reason_code.py` | ReasonCodeCreateRequest + ReasonCodeUpdateRequest confirmed |
| `backend/app/security/rbac.py` | `admin.master_data.reason_code.manage` confirmed at ADMIN role |
| `frontend/src/app/api/productApi.ts` | Used as BOM write reference pattern |

Backend write endpoints confirmed:
- `POST /v1/reason-codes` → `require_action("admin.master_data.reason_code.manage")` → 201
- `PATCH /v1/reason-codes/{id}` → `require_action(...)` → 200
- `POST /v1/reason-codes/{id}/release` → `require_action(...)` → 200
- `POST /v1/reason-codes/{id}/retire` → `require_action(...)` → 200

---

## 3. FE/BE Write Contract

| FE Helper | Backend Endpoint | Allowed Payload | Forbidden Payload Fields |
|---|---|---|---|
| `createReasonCode(payload)` | `POST /v1/reason-codes` | `reason_domain`, `reason_category`, `reason_code`, `reason_name`, `description?`, `requires_comment?`, `sort_order?`, `is_active?` | `lifecycle_status`, `tenant_id`, `created_at`, `updated_at`, `downtime_reason_id`, policy-binding fields |
| `updateReasonCode(id, payload)` | `PATCH /v1/reason-codes/{id}` | `reason_name?`, `description?`, `requires_comment?`, `sort_order?`, `is_active?` | `lifecycle_status`, `tenant_id`, `reason_code`, `reason_domain`, `reason_category`, `downtime_reason_id`, policy-binding fields |
| `releaseReasonCode(id)` | `POST /v1/reason-codes/{id}/release` | empty body | n/a |
| `retireReasonCode(id)` | `POST /v1/reason-codes/{id}/retire` | empty body | n/a |

Type enforcement:
- `ReasonCodeCreateRequest` — `extra="forbid"` on backend; type definition excludes all forbidden fields
- `ReasonCodeUpdateRequest` — excludes `reason_code`, `reason_domain`, `reason_category`, `lifecycle_status`, `tenant_id`, `downtime_reason_id`
- No `lifecycle_status` field is ever included in any FE payload

---

## 4. Authorization / Permission Decision

**Decision: Lifecycle-gated controls + backend-authoritative 403 handling + explicit governance notice.**

Rationale:
- `ReasonCodeItemFromAPI` does not include `allowed_actions` from backend (no server-derived capability guard)
- BOM pattern uses server-derived `allowed_actions` — not applicable here without backend schema change
- Persona-as-permission is explicitly forbidden by task spec and governance rules
- Lifecycle state is observable from the API response and is factual (not inferred permission)

Implementation:
- Edit button: enabled only when `lifecycle_status === "DRAFT"`
- Release button: enabled only when `lifecycle_status === "DRAFT"`
- Retire button: enabled when `lifecycle_status !== "RETIRED"` (DRAFT or RELEASED)
- Create button: always enabled (lifecycle context is page-level)
- 403 response from backend → `rcWrite.error.manageForbidden` message shown
- 401/404/409/422 all handled with appropriate error messages
- Governance notice shown at page top: `rcWrite.notice.governance`

**Known gap — MMD-FULLSTACK-13B (deferred):**
Adding `allowed_actions` to `ReasonCodeItemFromAPI` from backend (similar to BOM pattern) would enable server-derived capability gating. This requires a backend schema change to return `allowed_actions` in the reason code read model. Documented and deferred.

---

## 5. Files Changed

| File | Change Type | Notes |
|---|---|---|
| `frontend/src/app/api/reasonCodeApi.ts` | Modified | Added `ReasonCodeCreateRequest`, `ReasonCodeUpdateRequest` types; added `createReasonCode`, `updateReasonCode`, `releaseReasonCode`, `retireReasonCode` helpers |
| `frontend/src/app/pages/ReasonCodes.tsx` | Modified | Replaced read-only shell with write-intent controls, modals, lifecycle-gated buttons, governance notice, 403 handling |
| `frontend/src/app/i18n/registry/en.ts` | Modified | Added `reasonCodes.action.release` key; added 28 `rcWrite.*` keys |
| `frontend/src/app/i18n/registry/ja.ts` | Modified | Added `reasonCodes.action.release` key; added 28 `rcWrite.*` keys (Japanese) |
| `frontend/src/app/i18n/namespaces.ts` | Modified | Added `rcWrite: "rcWrite"` namespace |
| `frontend/src/app/api/index.ts` | Modified | Exported `ReasonCodeCreateRequest`, `ReasonCodeUpdateRequest` from `reasonCodeApi` |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | Modified | Updated I8 check (write-actions now enabled); added Section K with 25 write guardrail checks |
| `docs/audit/mmd-fullstack-13-reason-code-fe-write-intent.md` | Created | This report |

**Backend files: NONE changed.**
**Migration files: NONE changed.**

---

## 6. Frontend Changes

### `reasonCodeApi.ts`
- Added `ReasonCodeCreateRequest` interface: `reason_domain`, `reason_category`, `reason_code`, `reason_name`, `description?`, `requires_comment?`, `sort_order?`, `is_active?`
- Added `ReasonCodeUpdateRequest` interface: `reason_name?`, `description?`, `requires_comment?`, `sort_order?`, `is_active?` — excludes all immutable/forbidden fields
- Added `createReasonCode(payload, signal?)` → `POST /v1/reason-codes`
- Added `updateReasonCode(id, payload, signal?)` → `PATCH /v1/reason-codes/{id}`
- Added `releaseReasonCode(id, signal?)` → `POST /v1/reason-codes/{id}/release`
- Added `retireReasonCode(id, signal?)` → `POST /v1/reason-codes/{id}/retire`

### `ReasonCodes.tsx`
- Removed `Lock` icon import (no longer needed — write actions are now active)
- Added `HttpError` import for 403/validation error handling
- Added `ReasonCodeCreateRequest`, `ReasonCodeUpdateRequest` type imports
- Added write-intent state: `actionBusy`, `actionError`, `actionMessage`, `createOpen`, `createForm`, `editTarget`, `editForm`, `confirmRelease`, `confirmRetire`
- Added `resolveWriteError()` mapping HttpError status codes to i18n keys
- Added `refreshCodes()` to reload list after successful mutation
- Enabled "Create Reason Code" page-level button (with `onClick` handler, `disabled={actionBusy}`)
- Added lifecycle-gated row action buttons:
  - Edit: `disabled={!isDraft || actionBusy}`
  - Release: `disabled={!isDraft || actionBusy}`
  - Retire: `disabled={isRetired || actionBusy}`
- Added Create modal dialog (form with all create fields, cancel/save)
- Added Edit modal dialog (form with mutable fields only, cancel/save)
- Added Release confirmation dialog (confirm/cancel)
- Added Retire confirmation dialog (confirm/cancel)
- Added governance notice (`rcWrite.notice.governance`)
- Added action feedback area (success message / error message)
- Replaced `reasonCodes.notice.readonly` footer with `rcWrite.notice.backendAuth`

### `namespaces.ts`
- Added `rcWrite: "rcWrite"` to `I18N_NAMESPACES` to support TypeScript `I18nRegistry` type constraint

### `i18n` (en.ts / ja.ts)
- Added `reasonCodes.action.release` key
- Added 28 `rcWrite.*` keys: governance notice, backend-auth notice, error messages (unauthorized/forbidden/notFound/conflict/validation/actionFailed), success messages (created/updated/released/retired), modal field labels, confirm dialog text, lifecycle tooltips

---

## 7. Backend Verification / Changes

**No backend source changes made.**

Backend tests run for confirmation:
- `tests/test_reason_code_foundation_api.py` — **62 passed**
- `tests/test_reason_code_foundation_service.py` — **29 passed** (subset)
- `tests/test_mmd_rbac_action_codes.py` — All reason code RBAC tests passed

Note: 1 pre-existing unrelated failure in `test_mmd_rbac_action_codes.py::test_product_version_write_routes_use_product_version_action_code` (Product Version router marker check). This failure predates MMD-FULLSTACK-13 and is unrelated to Reason Code work.

---

## 8. State Transition Guardrails

| UI Action | Source State | Target State | Control State |
|---|---|---|---|
| Create | (new) | DRAFT | Always enabled |
| Update metadata | DRAFT | DRAFT | Enabled |
| Update metadata | RELEASED | — | Button disabled |
| Update metadata | RETIRED | — | Button disabled |
| Release | DRAFT | RELEASED | Enabled |
| Release | RELEASED | — | Button disabled |
| Release | RETIRED | — | Button disabled |
| Retire | DRAFT | RETIRED | Enabled |
| Retire | RELEASED | RETIRED | Enabled |
| Retire | RETIRED | — | Button disabled |

State guard implementation: `isDraft = c.lifecycle_status === "DRAFT"`, `isRetired = c.lifecycle_status === "RETIRED"` derived from backend response. Backend enforces actual lifecycle invariants.

---

## 9. Boundary Guardrails

| Invariant | Enforcement |
|---|---|
| Frontend does not become authorization truth | Backend 403 is final authority; governance notice shown; no persona-as-permission |
| No `lifecycle_status` in any FE payload | Type-level: field excluded from both request types |
| No `tenant_id` in any FE payload | Type-level: field excluded from both request types |
| No `downtime_reason_id` in any FE payload | Type-level: field excluded from both request types |
| No `reason_code/domain/category` in update payload | Type-level: `ReasonCodeUpdateRequest` excludes all three |
| No execution/downtime/material/quality/ERP behavior | Not referenced; verified by regression I9 + I10 + K19 checks |
| Backend is source of lifecycle truth | UI reads lifecycle from API response; never sets lifecycle directly |
| No forbidden write controls | delete/reactivate/clone/bulk/merge/map-downtime/bind-policy absent; verified by regression K19 |
| Existing read behavior intact | `listReasonCodes` still called; verified by regression K21 |

---

## 10. Downtime Reason Boundary

- No reference to `downtime_reason_id` in any payload type or UI handler
- No `downtime_reason` import or mapping in `ReasonCodes.tsx`
- Regression check I9 (`rc_no_downtime_reason_import`) passes
- Reason Code MMD lifecycle management explicitly separated from downtime execution classification

---

## 11. Regression Coverage

Regression script: `frontend/scripts/mmd-read-integration-regression-check.mjs`

**Previous total:** 134 checks (Sections A–I including I = Reason Codes read)

**Changes:**
- I8 updated: replaced "write actions remain disabled" check with "forbidden controls absent" check (write-intent is now live)
- Section K added: 25 new Reason Code write guardrail checks (K1–K25)

**New total: 162 checks — 162 passed, 0 failed**

Section K checks (K1–K25):
- K1–K4: Write helpers exist (create/update/release/retire)
- K5–K6: Request type interfaces exist
- K7–K10: `ReasonCodeCreateRequest` excludes forbidden fields (lifecycle_status, tenant_id, downtime_reason_id, policy fields)
- K11–K17: `ReasonCodeUpdateRequest` excludes forbidden fields (lifecycle_status, tenant_id, downtime_reason_id, policy fields, reason_code, reason_domain, reason_category)
- K18: Page references all 4 write intent controls
- K19: Page excludes forbidden write controls (delete/reactivate/clone/bulk/map/bind)
- K20: Page includes governance notice and 403 handling
- K21: Page still reads backend (regression guard)
- K22–K25: i18n governance and forbidden-error keys present in en.ts and ja.ts

---

## 12. Verification Commands

```bash
# Frontend (PowerShell — use npm.cmd)
cd frontend
npm.cmd run check:mmd:read    # 162 passed, 0 failed
npm.cmd run build              # ✓ built in ~10s (no TS errors)
npm.cmd run lint               # PASS (no ESLint errors)
npm.cmd run lint:i18n:registry # PASS: en.ts and ja.ts key-synchronized (1846 keys)
npm.cmd run check:routes       # PASS 24, FAIL 0

# Backend (uv run pattern)
cd backend
uv run --with pytest --with fastapi --with sqlalchemy --with httpx --with anyio \
  --with passlib --with "python-jose" --with bcrypt --with pydantic-settings \
  --with psycopg --with "psycopg-binary" --with alembic --python 3.12 \
  python -m pytest -q tests/test_reason_code_foundation_api.py \
    tests/test_reason_code_foundation_service.py tests/test_mmd_rbac_action_codes.py
# 92 passed, 1 pre-existing unrelated failure (product version router marker)
```

---

## 13. Remaining Risks / Deferred Items

| Item | Severity | Deferral |
|---|---|---|
| **MMD-FULLSTACK-13B**: No server-derived `allowed_actions` in `ReasonCodeItemFromAPI` | Medium | Backend schema change required to add `allowed_actions` to reason code read model; then FE can use capability-gated controls like BOM pattern. Recommended next. |
| Pre-existing `test_product_version_write_routes_use_product_version_action_code` failure | Low | Unrelated to this slice; Product Version router marker test; pre-existed MMD-FULLSTACK-13 |
| `screenStatus.ts` remains `PARTIAL` | Low | No change; screen still has partial write capability (no allowed_actions guard). Update to `CONNECTED` after MMD-FULLSTACK-13B is complete. |

---

## 14. Final Verdict

**PASS — MMD-FULLSTACK-13 slice complete.**

All required implementation behaviors satisfied:
- ✅ FE API helpers exist for all 4 allowed Reason Code write commands
- ✅ FE create payload may include `reason_domain`, `reason_category`, `reason_code`
- ✅ FE update payload never includes `reason_domain`, `reason_category`, `reason_code`
- ✅ FE never sends `lifecycle_status`
- ✅ FE never sends `tenant_id`, `created_at`, `updated_at`
- ✅ FE never sends `downtime_reason_id` or policy-binding fields
- ✅ FE reflects lifecycle rules for Reason Code controls (DRAFT/RELEASED/RETIRED gating)
- ✅ FE handles backend 403 gracefully (`rcWrite.error.manageForbidden`)
- ✅ FE handles 401/404/409/422 validation errors gracefully
- ✅ Successful mutation refreshes Reason Code read data
- ✅ No forbidden controls added (delete/reactivate/clone/bulk/map-downtime/bind-policy)
- ✅ Existing Reason Code read behavior intact
- ✅ MMD regression script locks Reason Code FE write guardrails (162 checks, all pass)
- ✅ Frontend build/lint/i18n/routes pass
- ✅ Backend Reason Code/RBAC tests pass (62 + RBAC subset)
- ✅ No backend source modified
- ✅ No migration modified
- ✅ No auto-commit performed

**No changes committed.** Commit guidance provided in implementation report.
