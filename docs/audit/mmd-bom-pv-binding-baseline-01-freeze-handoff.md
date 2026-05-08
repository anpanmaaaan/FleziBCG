# MMD-BOM-PV-BINDING-BASELINE-01 — BOM Product Version Binding Baseline Freeze / Handoff

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-08 | v1.0 | Frozen BOM ↔ Product Version binding baseline after backend API, release validation, frontend integration, and server-derived capability guard. |

---

## 1. Scope

This document freezes the complete BOM ↔ Product Version binding baseline as implemented across eight slices:

- **MMD-BOM-WRITE-02** — Governance contract
- **MMD-BE-14** — Backend API foundation (GET/POST/DELETE)
- **MMD-BE-14A** — Boundary audit and release validation decision
- **MMD-BE-14B** — Release validation policy contract
- **MMD-BE-14C** — Release validation implementation (`bom_binding_required_for_release`, migration 0014)
- **MMD-BE-14D** — Boundary audit regression lock
- **MMD-FULLSTACK-14** — Frontend integration (binding UI, readiness display)
- **MMD-FULLSTACK-14B** — Server-derived capability guard (frontend consumes backend capabilities)

**What is frozen:**
- Binding entity (`ProductVersionBomBinding`), cardinality (one ACTIVE PRIMARY per PV), and lifecycle rules
- Backend APIs (GET/POST/DELETE `bom-binding`)
- Product Version release validation (`bom_binding_required_for_release`)
- Server-derived capability contract (`can_bind`, `can_unbind`, `can_toggle_bom_binding_required_for_release`)
- Authorization rules (AND semantics for mutation; authenticated-read for GET)
- Frontend UI contract (capability-gated binding/unbinding/toggle intent)
- Audit/event behavior (CREATED, REMOVED events)
- Alembic migration chain (0013, 0014)
- Test/regression coverage (74 backend tests, 209 frontend regression checks)

**What is NOT in scope of this freeze document:**
- No new backend APIs, frontend UI, tests, migrations, or runtime source changes
- No commands listed in Section 14 (deferred/forbidden)

---

## 2. Baseline Inputs Reviewed

| Document | Status | Key Finding |
|---|---|---|
| `docs/audit/mmd-bom-write-02-bom-product-version-binding-governance-contract.md` | ✅ Read | Governance contract: ONE ACTIVE PRIMARY per PV; both action codes required; event/boundary map established |
| `docs/audit/mmd-be-14-bom-product-version-binding-api-foundation.md` | ✅ Read | 3 routes (GET/POST/DELETE) implemented; 23 tests pass; AND auth enforced; soft-delete (REMOVED); events CREATED/REMOVED |
| `docs/audit/mmd-be-14a-bom-product-version-binding-boundary-release-validation.md` | ✅ Read | Boundary verified clean; no forbidden imports; release validation deferred to 14B |
| `docs/audit/mmd-be-14b-product-version-release-bom-binding-validation-policy-contract.md` | ✅ Read | Option B (PV-level flag) selected; migration 0014 planned; backward compatible; release auth = pv.manage only |
| `docs/audit/mmd-be-14c-product-version-release-bom-binding-validation-implementation.md` | ✅ Read | `bom_binding_required_for_release` added to model/schema/service; migration 0014 applied; 15 new release validation tests |
| `docs/audit/mmd-be-14d-product-version-release-bom-binding-validation-boundary-audit.md` | ✅ Read | All release validation scenarios verified; blocked release emits no event; no forbidden domain imports; alembic head = 0014 |
| `docs/audit/mmd-fullstack-14-bom-product-version-binding-fe-integration.md` | ✅ Read | FE binding/unbinding/toggle intent; release readiness display; 201 regression checks pass; i18n 1902 keys |
| `docs/audit/mmd-fullstack-14b-bom-product-version-binding-capability-guard.md` | ✅ Read | Server-derived capabilities; frontend no longer uses lifecycle-only gating; 74 backend tests pass; 209 FE checks pass |

Adjacent baselines also reviewed:

| Document | Status | Key Finding |
|---|---|---|
| `docs/design/02_registry/action-code-registry.md` | ✅ Inspected | `admin.master_data.bom.manage` and `admin.master_data.product_version.manage` registered, ADMIN family |
| `docs/design/02_domain/product_definition/bom-product-version-binding-governance-contract.md` | ✅ Present | Design source for binding entity, cardinality, and event boundaries |
| `docs/design/02_domain/product_definition/product-version-release-bom-binding-validation-policy-contract.md` | ✅ Present | Policy design source for release gate |

---

## 3. Source Inspection Summary

| File | Finding | Status |
|---|---|---|
| `backend/app/models/product_version_bom_binding.py` | `ProductVersionBomBinding` entity; PRIMARY only; ACTIVE/REMOVED status; no execution/material imports | ✅ |
| `backend/app/models/product_version.py` | `bom_binding_required_for_release: Mapped[bool]`, `nullable=False`, `default=False` | ✅ |
| `backend/app/schemas/product.py` | `ProductVersionBomBindingData`, `ProductVersionBomBindingCapabilities`, `ProductVersionBomBindingResponse` (wrapper) | ✅ |
| `backend/app/services/product_version_bom_binding_service.py` | `_compute_capabilities()` pure function; `_ALLOWED_PV_BIND_STATUSES = {"DRAFT"}`; `_FORBIDDEN_BOM_BIND_STATUSES = {"RETIRED"}`; no forbidden domain imports | ✅ |
| `backend/app/services/product_version_service.py` | Release validation reads binding + BOM lifecycle; no mutation of binding/BOM; no forbidden domain imports | ✅ |
| `backend/app/api/v1/products.py` | GET: `require_authenticated_identity`; POST/DELETE: `require_action(bom.manage)` + inner `has_action(pv.manage)`; Release: `require_action(pv.manage)` only | ✅ |
| `backend/alembic/versions/0013_product_version_bom_bindings.py` | Creates `product_version_bom_bindings` table; `down_revision="0011"` | ✅ |
| `backend/alembic/versions/0014_add_bom_binding_required_for_release_to_product_versions.py` | Adds `bom_binding_required_for_release`; `server_default=sa.false()`; `down_revision="0013"` | ✅ |
| `backend/tests/test_bom_binding_api.py` | 35 tests; all binding API behaviors + 11 capability tests | ✅ |
| `backend/tests/test_mmd_rbac_action_codes.py` | Source-level contract tests for action codes + schema contract | ✅ |
| `frontend/src/app/api/productApi.ts` | `ProductVersionBomBindingData`, `ProductVersionBomBindingCapabilities`, wrapper `ProductVersionBomBindingResponse` | ✅ |
| `frontend/src/app/pages/ProductDetail.tsx` | `capabilities` state; all three capability fields consumed; no lifecycle-only inference for binding buttons | ✅ |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | Sections A–P; 209 checks; Section P guards capability consumption pattern | ✅ |

**Adjacent boundary inspection (read only, confirmed absent):**

| Category | Models / Services Present? |
|---|---|
| Material / Inventory | ❌ No material/inventory models or services in backend/app |
| Backflush / ERP | ❌ Not present |
| Traceability / Genealogy | ❌ Not present |
| Quality | ❌ Not present |
| Production Order / APS | ❌ Not present |

---

## 4. Implemented Binding Baseline

### Entity

**`ProductVersionBomBinding`** — association entity stored in `product_version_bom_bindings` table.

| Property | Value |
|---|---|
| Scope | Tenant + Product |
| Cardinality (first phase) | Zero or one ACTIVE PRIMARY per Product Version |
| Binding type (implemented) | `PRIMARY` only |
| Binding status | `ACTIVE` (live) or `REMOVED` (soft-deleted) |
| Fields | `binding_id`, `tenant_id`, `product_id`, `product_version_id`, `bom_id`, `binding_type`, `binding_status`, `notes`, `created_at`, `updated_at`, `created_by`, `updated_by` |
| Deferred fields | `effective_from`, `effective_to` (effective dating deferred) |
| Deferred behavior | Plant/scope-specific binding, secondary/alternate types, binding replace |

### Cardinality Invariant

One and only one ACTIVE PRIMARY binding per Product Version is enforced at service layer. Creating a second binding when one exists raises `ValueError("already exists")` → HTTP 409.

---

## 5. Backend API Baseline

### Implemented Routes

| Method | Path | Auth | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/v1/products/{product_id}/versions/{version_id}/bom-binding` | `require_authenticated_identity` | 200 (wrapper with `binding` + `capabilities`), 404 (PV not found) | Returns 200 + `binding: null` when no active binding |
| `POST` | `/api/v1/products/{product_id}/versions/{version_id}/bom-binding` | `require_action(bom.manage)` + inner `has_action(pv.manage)` | 201 (`ProductVersionBomBindingData`), 404, 409, 422 | Emits CREATED event |
| `DELETE` | `/api/v1/products/{product_id}/versions/{version_id}/bom-binding` | `require_action(bom.manage)` + inner `has_action(pv.manage)` | 204, 404, 422 | Soft-delete; emits REMOVED event |

### Forbidden Routes (confirmed absent)

`PATCH bom-binding`, `PUT bom-binding`, `/replace`, `/set-current`, `/material-reserve`, `/backflush`, `/erp-post`, `/genealogy`, `/quality-accept`

### GET Response Shape (current)

```json
{
  "product_id": "...",
  "product_version_id": "...",
  "binding": {
    "binding_id": "...",
    "tenant_id": "...",
    "product_id": "...",
    "product_version_id": "...",
    "bom_id": "...",
    "binding_type": "PRIMARY",
    "binding_status": "ACTIVE",
    "notes": null,
    "created_at": "...",
    "updated_at": "...",
    "created_by": "...",
    "updated_by": null,
    "allowed_actions": {
      "can_remove": true
    }
  },
  "capabilities": {
    "can_bind": false,
    "can_unbind": true,
    "can_toggle_bom_binding_required_for_release": true,
    "reason": null
  }
}
```

When no active binding: `"binding": null`. `capabilities` always present.

### POST Response Shape

`ProductVersionBomBindingData` — same shape as `binding` object above.

---

## 6. Data Model / Migration Baseline

| Migration | File | Chain | Key Change |
|---|---|---|---|
| 0013 | `0013_product_version_bom_bindings.py` | `down_revision = "0011"` | Creates `product_version_bom_bindings` table with 4 indexes |
| 0014 | `0014_add_bom_binding_required_for_release_to_product_versions.py` | `down_revision = "0013"` | Adds `bom_binding_required_for_release` to `product_versions`; `server_default=sa.false()`, `nullable=False` |

**Current Alembic head:** `"0014"`  
**Backward compatibility:** All existing Product Versions receive `bom_binding_required_for_release = false` after migration 0014. No RELEASED PV is invalidated. No re-release required.

**No additional migrations are in scope for this baseline.**

---

## 7. Product Version Release Validation Baseline

### Policy Field

`ProductVersion.bom_binding_required_for_release` — Boolean, NOT NULL, DEFAULT `false`.

Set via `PATCH /api/v1/products/{product_id}/versions/{version_id}` using `ProductVersionUpdateRequest.bom_binding_required_for_release`. Requires `admin.master_data.product_version.manage`. Only accepted when PV is DRAFT.

### 9.4 Release Validation Matrix

| `bom_binding_required_for_release` | Binding State | Bound BOM State | Release Decision |
|---|---|---|---|
| `false` | Any or none | Any | ✅ ALLOW (no binding check performed) |
| `true` | No ACTIVE PRIMARY binding | — | ❌ BLOCK → HTTP 400 |
| `true` | ACTIVE PRIMARY | DRAFT | ❌ BLOCK → HTTP 400 |
| `true` | ACTIVE PRIMARY | RETIRED | ❌ BLOCK → HTTP 400 |
| `true` | ACTIVE PRIMARY | RELEASED | ✅ ALLOW → HTTP 200 |
| `true` | REMOVED binding only (no ACTIVE) | — | ❌ BLOCK → HTTP 400 |
| `false` or `true` | Any | Any | ❌ BLOCK → HTTP 422 (if PV not DRAFT — existing invariant) |

**Key rules:**
- Release validation is read-only: does not mutate BOM, binding, or any other entity
- Release does NOT require `admin.master_data.bom.manage`
- Blocked release emits no `PRODUCT_VERSION.RELEASED` event
- `ProductVersionBomBinding.VALIDATED_ON_RELEASE` event is deferred (not emitted)

---

## 8. Frontend UI Baseline

### ProductDetail.tsx (binding section)

| Feature | Behavior | Backend Source |
|---|---|---|
| Binding state display | Shows `binding.binding.*` fields or empty message when `binding: null` | GET wrapper response |
| Release readiness display | `NOT_REQUIRED` / `READY` / `BLOCKED_NO_BINDING` / `BLOCKED_DRAFT_BOM` / `BLOCKED_RETIRED_BOM` / `BLOCKED_BOM_NOT_RELEASED` / `UNKNOWN` | Derived from `binding?.binding`, `bom_binding_required_for_release`, `selectedBoundBom.lifecycle_status` |
| Bind BOM button | Shown and enabled when `capabilities.can_bind = true` | Server-derived |
| Unbind button | Shown and enabled when `capabilities.can_unbind = true` | Server-derived |
| Toggle "required" button | Enabled when `capabilities.can_toggle_bom_binding_required_for_release = true` | Server-derived |
| POST/DELETE error mapping | 400/403/404/409/422 errors displayed | Backend error detail pass-through |

**Non-negotiable FE rule:** Frontend never infers bind/unbind enablement from `lifecycle_status` alone. All button states derive from `capabilities?.can_*` fields.

---

## 9. Authorization / Capability Baseline

### 9.1 Implemented Command Matrix

| Command | Backend Route | FE Control | Auth | Lifecycle Rule | Status |
|---|---|---|---|---|---|
| get binding | `GET .../bom-binding` | — (background load) | `require_authenticated_identity` | None | ✅ IMPLEMENTED |
| bind BOM to PV | `POST .../bom-binding` | "Bind" button (when `can_bind`) | `bom.manage` AND `pv.manage` | PV=DRAFT, BOM≠RETIRED, 0 active | ✅ IMPLEMENTED |
| unbind BOM from PV | `DELETE .../bom-binding` | "Unbind" button (when `can_unbind`) | `bom.manage` AND `pv.manage` | PV=DRAFT, active binding exists | ✅ IMPLEMENTED |
| toggle `bom_binding_required_for_release` | `PATCH .../versions/{vid}` | Toggle buttons (when `can_toggle`) | `pv.manage` | PV=DRAFT | ✅ IMPLEMENTED |
| release PV with validation | `POST .../versions/{vid}/release` | Release button | `pv.manage` | If flag=true: ACTIVE PRIMARY → RELEASED BOM | ✅ IMPLEMENTED |

### 9.3 Capability Matrix

| Capability | Backend Condition | FE Consumer | Rule |
|---|---|---|---|
| `can_bind` | DRAFT PV + no active binding + BOTH `pv.manage` AND `bom.manage` | `canShowBindIntent = Boolean(capabilities?.can_bind)` | All three conditions must be true |
| `can_unbind` | DRAFT PV + active binding + BOTH `pv.manage` AND `bom.manage` | `canShowUnbindIntent = Boolean(capabilities?.can_unbind)` | All three conditions must be true |
| `can_toggle_bom_binding_required_for_release` | DRAFT PV + `pv.manage` | `selectedVersionCanToggleFlag = Boolean(capabilities?.can_toggle_bom_binding_required_for_release)` | Only requires `pv.manage`; does not require `bom.manage` |

### Capability Derivation by State

| Condition | `can_bind` | `can_unbind` | `can_toggle` |
|---|---|---|---|
| DRAFT + no binding + both perms | ✅ | ❌ | ✅ |
| DRAFT + active binding + both perms | ❌ | ✅ | ✅ |
| DRAFT + only `pv.manage` | ❌ | ❌ | ✅ |
| DRAFT + only `bom.manage` | ❌ | ❌ | ❌ |
| DRAFT + no manage perms | ❌ | ❌ | ❌ |
| RELEASED (any perms) | ❌ | ❌ | ❌ |
| RETIRED (any perms) | ❌ | ❌ | ❌ |

---

## 10. Lifecycle Rules Baseline

| Rule | Enforcement Location | Evidence |
|---|---|---|
| Bind requires DRAFT PV | `_ALLOWED_PV_BIND_STATUSES = {"DRAFT"}` in binding service | `test_bind_released_pv_returns_422`, `test_bind_retired_pv_returns_422` |
| Bind forbids RETIRED BOM | `_FORBIDDEN_BOM_BIND_STATUSES = {"RETIRED"}` in binding service | `test_bind_retired_bom_returns_422` |
| One ACTIVE PRIMARY per PV | Service: `get_active_binding_by_version()` check before create | `test_duplicate_bind_returns_409` |
| Unbind requires DRAFT PV | Same `_ALLOWED_PV_BIND_STATUSES` check in unbind service | `test_unbind_released_pv_returns_422` |
| Bind/unbind does NOT change PV lifecycle | Service: only `binding_status` mutated, not `lifecycle_status` | Confirmed by source inspection (MMD-BE-14A) |
| Bind/unbind does NOT change BOM lifecycle | BOM not touched | Confirmed by source inspection (MMD-BE-14A) |
| Release gate: flag=true requires ACTIVE PRIMARY → RELEASED BOM | `product_version_service.release_product_version()` | Full test matrix in `test_product_version_foundation_api.py` |
| Release gate: flag=false is unchanged behavior | Early return in release service | `test_release_draft_pv_*` existing tests pass |

---

## 11. Audit / Event Baseline

| Action | Security Event Type | When Emitted |
|---|---|---|
| `bind_bom_to_product_version` | `PRODUCTVERSIONBOMBINDING.CREATED` | On successful bind |
| `unbind_bom_from_product_version` | `PRODUCTVERSIONBOMBINDING.REMOVED` | On successful unbind |
| `release_product_version` (success) | `PRODUCT_VERSION.RELEASED` | On successful release (flag=false or flag=true+valid binding) |
| `release_product_version` (blocked) | (none) | Blocked release emits no event |

**Deferred:** `ProductVersionBomBinding.VALIDATED_ON_RELEASE` — not yet emitted; deferred per MMD-BE-14B policy contract.

All events stored via `record_security_event()` which applies `.strip().upper()`.

---

## 12. Cross-Domain Boundary Guardrails

### 9.5 Boundary Guardrails

| Boundary | Current Decision | Evidence | Risk if Violated |
|---|---|---|---|
| Binding vs Material / Inventory | No material/inventory models exist; binding service imports none | Source inspection (MMD-BE-14A, 14D) | Inventory drift; accounting errors |
| Binding vs Backflush | No backflush models or services exist | Source inspection (MMD-BE-14D); `backend/app/models/` listing | Incorrect BOM-driven consumption records |
| Binding vs ERP | No ERP services exist | Source inspection | External SoR conflict |
| Binding vs Traceability / Genealogy | No traceability models exist | Source inspection | Genealogy contamination; audit trail errors |
| Binding vs Quality | No quality models or services exist | Source inspection | Quality governance breach |
| Binding vs Execution | Execution services/models exist but binding service imports none | `product_version_bom_binding_service.py` imports confirmed | Execution state machine corruption |
| Binding vs APS | No APS service exists | Source inspection | Scheduling interference |
| Frontend UI vs Authorization Truth | All button states use `capabilities?.can_*` from backend | Regression P4–P7; ProductDetail.tsx lines 103–105 | Privilege bypass via frontend persona inference |
| Product Version release vs BOM mutation | Release validation is read-only; does not mutate BOM or binding | MMD-BE-14D source inspection | False release or phantom binding |
| BOM binding vs PV set_current | `is_current` is advisory; partial-unique enforcement deferred; binding does not depend on `is_current` | Model comment; MMD-BOM-WRITE-02 | Stale `is_current` could mislead if later used as capability gate |

---

## 13. Regression Coverage Baseline

### 9.6 Regression Coverage Baseline

| Area | Coverage | Command / Evidence | Status |
|---|---|---|---|
| Backend binding API tests | 35 tests in `test_bom_binding_api.py` | `pytest tests/test_bom_binding_api.py` | ✅ 35 passed (confirmed MMD-FULLSTACK-14B session) |
| Backend PV release validation | 15 tests in `test_product_version_foundation_api.py` | `pytest tests/test_product_version_foundation_api.py` | ✅ All pass (confirmed MMD-BE-14D) |
| Backend RBAC/action-code tests | 39 tests in `test_mmd_rbac_action_codes.py` (including schema contract) | `pytest tests/test_mmd_rbac_action_codes.py` | ✅ 39 passed (confirmed MMD-FULLSTACK-14B session) |
| Backend Alembic baseline | `test_alembic_baseline.py` HEAD = `"0014"` | `pytest tests/test_alembic_baseline.py` | ✅ Confirmed MMD-BE-14D |
| BOM foundation | `test_bom_foundation_api.py`, `test_bom_foundation_service.py` | Adjacent regression | ✅ Pass (no changes in this slice chain) |
| Total backend binding suite | 74 tests | `pytest -q tests/test_bom_binding_api.py tests/test_mmd_rbac_action_codes.py` | ✅ 74 passed, 0 failed (confirmed MMD-FULLSTACK-14B session) |
| Frontend MMD regression | 209 checks (Sections A–P) | `npm run check:mmd:read` | ✅ 209 passed, 0 failed (confirmed MMD-FULLSTACK-14B session) |
| Frontend build | Vite production build; 3409 modules | `npm run build` | ✅ Exit 0 (confirmed MMD-FULLSTACK-14B session) |
| Frontend lint | ESLint `src/` | `npm run lint` | ✅ Exit 0 (confirmed MMD-FULLSTACK-14B session) |
| Frontend i18n registry | en.ts / ja.ts parity; 1902 keys | `npm run lint:i18n:registry` | ✅ 1902 keys parity (confirmed MMD-FULLSTACK-14B session) |
| Frontend route check | Route accessibility gate | `npm run check:routes` | ✅ Exit 0 (confirmed MMD-FULLSTACK-14B session) |
| `lint:i18n` full check | **PowerShell/CRLF caveat:** `lint:i18n` is a bash script; fails on Windows PowerShell due to CRLF line endings. Use `lint:i18n:registry` (Node.js) as the equivalent on Windows. | `npm run lint:i18n:registry` | ✅ Node.js equivalent passes |

**Note on reuse:** Verification results from the MMD-FULLSTACK-14B session are reused here. The same branch, no intervening source changes between that session and this freeze document (confirmed by git commit log). Results are attributable to the current source state.

---

## 14. Known Gaps / Deferred Items

| Item | Decision | Governing Slice |
|---|---|---|
| `ProductVersionBomBinding.VALIDATED_ON_RELEASE` event | DEFERRED — not emitted on release | Future enhancement; no governing slice yet |
| Product Version `is_current` partial-unique enforcement | DEFERRED — advisory field only | `is_current` noted as advisory in model comment |
| Binding `effective_from` / `effective_to` | DEFERRED — effective dating not implemented | Future effective-dating governance slice |
| Multiple BOM binding types (SECONDARY, ALTERNATE, etc.) | DEFERRED — PRIMARY only | Future type-semantics governance slice |
| Binding replace (atomic swap of PRIMARY BOM) | DEFERRED — no replace command | Requires atomic replacement policy contract |
| Plant/scope-specific binding | DEFERRED | Requires MMD-SCOPE-APPLICABILITY-01 |
| Product-level binding policy | DEFERRED | Requires product-level governance update |
| Tenant/plant/manufacturing-profile policy | DEFERRED | Requires manufacturing profile governance |
| BOM binding `allowed_actions.can_remove` logic | Currently: DRAFT PV + has_both_permissions; semantically equivalent to `can_unbind`; future may diverge | If divergence needed, treat separately |
| Automatic current-version selection | DEFERRED | Not governed; `is_current` is advisory |

---

## 15. Do-Not-Do Rules for Future Agents

These are hard guardrails. Future agents MUST NOT implement any of the following without first creating a new governance contract and obtaining a Hard Mode MOM v3 verdict:

1. **Do NOT implement Product Version `set_current`** — `is_current` is advisory; enforcement deferred; full governance required before implementation.
2. **Do NOT implement binding replace** — Atomic replacement requires a new policy contract for rollback behavior, authorization, and event semantics.
3. **Do NOT implement multiple BOM binding types** (SECONDARY, ALTERNATE, etc.) — requires type-semantics governance slice before any schema/API change.
4. **Do NOT implement `effective_from` / `effective_to` binding** — effective dating adds time-bounded applicability semantics; requires separate governance.
5. **Do NOT implement plant/scope-specific binding** — requires MMD-SCOPE-APPLICABILITY-01 first.
6. **Do NOT implement product-level or tenant/plant/manufacturing-profile policy** for binding — requires manufacturing profile governance first.
7. **Do NOT implement material reservation, material consumption, inventory movement, scrap posting, or backflush** in binding service or trigger them from bind/unbind/release events.
8. **Do NOT implement ERP posting** from binding mutations — binding is definition applicability only.
9. **Do NOT implement traceability genealogy, quality acceptance, or execution dispatch** triggered by binding state.
10. **Do NOT implement production order creation or APS selection** from binding state.
11. **Do NOT implement automatic current-version selection** from binding or release events.
12. **Do NOT infer authorization from lifecycle status alone** in the frontend — always use `capabilities?.can_*` fields from the backend.
13. **Do NOT add migrations after 0014** in this binding baseline — the next migration must be scoped to its own governance slice.
14. **Do NOT change the GET response schema** to remove `capabilities` or `binding` wrapper — breaking this would invalidate all frontend capability consumption.
15. **Do NOT weaken the AND-authorization semantics** for POST/DELETE bom-binding — both `bom.manage` AND `pv.manage` are required; reducing to one is a privilege escalation risk.

---

## 16. Recommended Next Slice

### Primary Recommendation

**MMD-FE-QA-03 — BOM Product Version Binding Runtime Visual QA / Screenshot Evidence**

Backend + frontend + capability guard are now frozen and passing all regression gates. Before the full MMD Foundation Closeout, browser/runtime visual evidence should be captured for the new binding UI and release readiness behavior in a live or seeded environment.

**Rationale:**
- All code is implemented and tested; but no browser-captured screenshots exist for the binding section, toggle behavior, or release readiness states
- Visual QA will catch rendering regressions, i18n label gaps, and UX issues not visible in unit/regression tests
- Full MMD Foundation Closeout (MMD-MASTER-BASELINE-01) should not proceed before visual QA of this significant new binding UI surface

**Do not proceed to:**
- MMD-PV-WRITE-02 (Product Version `set_current`) — governance contract required first
- MMD-SCOPE-APPLICABILITY-01 — wider scope; binding visual QA first
- MMD-ISA88-00 — unrelated; binding freeze must complete before scope expansion
- MMD-MASTER-BASELINE-01 (Full MMD Foundation Closeout) — binding visual QA required first

---

## 17. Verification Commands

**Backend (run from `backend/` directory):**

```powershell
# Windows PowerShell — use .venv python directly
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q `
  tests/test_bom_binding_api.py `
  tests/test_mmd_rbac_action_codes.py `
  tests/test_product_version_foundation_api.py `
  tests/test_alembic_baseline.py

g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q `
  tests/test_bom_foundation_api.py `
  tests/test_bom_foundation_service.py
```

**Frontend (run from `frontend/` directory):**

```powershell
npm.cmd run check:mmd:read
npm.cmd run build
npm.cmd run lint
npm.cmd run lint:i18n:registry
npm.cmd run check:routes
```

**Note:** `npm run lint:i18n` (bash script) fails in PowerShell due to CRLF. Use `lint:i18n:registry` (Node.js equivalent) on Windows.

**Expected results:**

| Command | Expected |
|---|---|
| Backend binding + RBAC suite | 74 passed, 0 failed |
| Frontend regression | 209 passed, 0 failed |
| Frontend build | Exit 0 |
| Frontend lint | Exit 0 |
| i18n registry | 1902 keys, en/ja parity |
| Route check | Exit 0 |

---

## 18. Final Freeze Verdict

### Invariant Check

| Invariant | Status |
|---|---|
| Backend owns binding truth | ✅ |
| Frontend sends intent only | ✅ |
| Frontend uses backend-derived capabilities | ✅ |
| Persona is not permission | ✅ (action codes; not role-only) |
| Binding mutation requires BOTH `product_version.manage` AND `bom.manage` | ✅ |
| Product Version release requires only `product_version.manage` | ✅ |
| Release validation does not require `bom.manage` | ✅ |
| Read binding endpoint remains authenticated-read | ✅ |
| No `lifecycle_status` payload from FE for bind/unbind | ✅ |
| No `set_current` | ✅ |
| No binding replace | ✅ |
| No material/backflush/ERP/traceability/quality/execution behavior | ✅ |
| No migration after 0014 in this slice | ✅ |

### Verdict

**BASELINE FROZEN — PROCEED TO MMD-FE-QA-03**

The BOM ↔ Product Version binding baseline is complete, verified, and frozen. All invariants pass. All regression gates pass. The implementation is safe for visual QA and subsequent full MMD Foundation Closeout.
