# MMD-FULLSTACK-14 Audit Report
## BOM Product Version Binding Frontend Integration

**Date**: 2026-05-06  
**Branch**: autocode  
**Slice**: MMD-FULLSTACK-14  
**Depends on**: MMD-BE-14, MMD-BE-14A, MMD-BE-14C, MMD-BE-14D, MMD-FULLSTACK-11

---

## 1. Objective

Integrate Product Version BOM binding intent and release-readiness visibility into Product Detail while preserving backend authority.

This slice adds:

- Product Version BOM binding API client types/helpers (GET/POST/DELETE)
- Product Version field support for `bom_binding_required_for_release` in FE create/update/read contracts
- Product Detail UI for:
  - Selecting a target Product Version
  - Viewing current BOM binding and BOM lifecycle
  - Toggling release policy flag (`required` vs `not required`) for DRAFT versions
  - Binding/unbinding PRIMARY BOM for DRAFT versions only
  - Displaying release-readiness status from backend-truth-derived fields
- Regression checks to lock this behavior and guard forbidden routes/labels

---

## 2. Design Evidence Inspected

| Document/Source | Finding |
|---|---|
| backend/app/api/v1/products.py | BOM binding routes are GET/POST/DELETE at `/{product_id}/versions/{version_id}/bom-binding`; no PATCH/PUT for binding path |
| backend/app/schemas/product.py | Product Version schema includes `bom_binding_required_for_release`; binding response shape is a direct object with `allowed_actions.can_remove` |
| backend/app/services/product_version_bom_binding_service.py | Binding lifecycle guardrails: DRAFT-only mutation, active PRIMARY singleton, BOM lifecycle constraints |
| docs governance + design baseline | Frontend sends intent only; backend is source of truth for authz and state transitions |

---

## 3. Hard Mode MOM Assessment

**MOM v3: ON** (governed domain touchpoint)

Reason:

- Slice touches lifecycle-release gating visibility and binding intent around Product Version release readiness.
- Backend contracts remain unchanged; FE-only implementation follows existing authoritative behavior.

Design packet was completed before coding in-session (evidence/event/invariant/state/test/verdict), and implementation stayed within FE intent boundaries.

---

## 4. Files Changed

### frontend/src/app/api/productApi.ts

- Added `bom_binding_required_for_release` to `ProductVersionItemFromAPI`.
- Added optional `bom_binding_required_for_release` to:
  - `ProductVersionCreateRequest`
  - `ProductVersionUpdateRequest`
- Added binding contracts:
  - `ProductVersionBomBindingAllowedActions`
  - `ProductVersionBomBindingResponse`
  - `ProductVersionBomBindingCreateRequest`
- Added API helpers:
  - `getProductVersionBomBinding(productId, versionId)`
  - `bindBomToProductVersion(productId, versionId, payload)`
  - `unbindBomFromProductVersion(productId, versionId)`

### frontend/src/app/api/index.ts

- Exported:
  - `ProductVersionBomBindingCreateRequest`
  - `ProductVersionBomBindingResponse`

### frontend/src/app/pages/ProductDetail.tsx

- Added selected version state and BOM/binding state loaders.
- Added release policy toggle intent for DRAFT version (`bom_binding_required_for_release`).
- Added binding/unbinding intent actions for DRAFT version.
- Added release-readiness computation and messaging based on:
  - required flag
  - active binding existence
  - bound BOM lifecycle
- Added binding section UI with backend-auth notice.
- Extended backend error mapping for binding and release preconditions.
- Added `bindingRequired` column in Product Versions table.

### frontend/src/app/i18n/registry/en.ts

- Added Product Detail binding/readiness/policy/action/success/error keys.
- Added Product Version release error keys for binding preconditions.
- Updated edit scope notice text to keep only truly out-of-scope actions.

### frontend/src/app/i18n/registry/ja.ts

- Added JA equivalents for all new binding/readiness/policy/action/success/error keys.
- Added JA equivalents for Product Version release error keys.
- Updated edit scope notice text to match EN scope.

### frontend/scripts/mmd-read-integration-regression-check.mjs

- Updated legacy forbidden command guard to allow BOM binding for this slice.
- Added MMD-FULLSTACK-14 checks:
  - Binding helpers exist in API
  - Product Version binding-required field exists
  - Product Detail references policy and readiness keys
  - Product Detail excludes forbidden route fragments
  - Product Detail excludes forbidden runtime labels

---

## 5. Verification Results

| Check | Result |
|---|---|
| `npm.cmd run check:mmd:read` | **201 PASS, 0 FAIL** |
| `npm.cmd run build` | **PASS** (vite build complete) |
| `npm.cmd run lint` | **PASS** (no eslint errors emitted) |
| `npm.cmd run lint:i18n:registry` | **PASS** (`en.ts` and `ja.ts` synchronized, 1902 keys) |
| `npm.cmd run check:routes` | **PASS** (24 PASS, 0 FAIL) |
| `npm.cmd run lint:i18n` | **FAIL (environment script compatibility)** `check_i18n_hardcode.sh` failed in PowerShell due CRLF/`bash` line ending handling; unrelated to FULLSTACK-14 slice logic |
| Backend evidence tests | **Not executable in current shell** (`python` and `pytest` unavailable in this environment) |

---

## 6. Governance Invariants Verified

| Invariant | Status |
|---|---|
| Backend remains source of truth | Yes |
| Frontend sends intent only | Yes |
| Frontend does not derive authorization truth | Yes |
| FE does not introduce forbidden binding routes | Yes (guarded in regression script) |
| FE does not introduce execution runtime labels | Yes (guarded in regression script) |
| Release gating relies on backend lifecycle and binding truth | Yes |

---

## 7. Risks and Remaining Items

| Risk | Severity | Status |
|---|---|---|
| Optional `lint:i18n` command is shell-sensitive in PowerShell (`bash` + CRLF issue) | Low | Known infra/script portability issue, not logic regression |
| Backend evidence tests could not run in this terminal due missing Python/pytest runtime | Medium | Needs run in configured backend environment (uv/venv) |

---

## 8. Definition of Done

- [x] FE API supports Product Version binding required flag and binding endpoints
- [x] Product Detail can select version and show binding state
- [x] Product Detail can send bind/unbind/toggle-required intents (DRAFT-only gating in UI)
- [x] Release readiness is visible from backend-truth-aligned signals
- [x] EN/JA i18n keys added and parity check passes
- [x] Regression script extended for FULLSTACK-14 and passing
- [x] Build/lint/route checks pass
- [ ] Backend evidence tests rerun in configured Python test environment
