# MMD-FULLSTACK-11B — Product Version Server-Derived Write Capability Guard Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Added server-derived Product Version write capability guard for frontend controls. |

## 1. Scope

In scope:
- `ProductVersionAllowedActions` schema added to backend (`can_update`, `can_release`, `can_retire`, `can_create_sibling`)
- `ProductVersionItem` read response extended with `allowed_actions` field
- `product_version_service` updated: `_compute_allowed_actions` helper, `has_manage_permission` param on list/get functions
- Read route handlers (`list_product_versions`, `get_product_version`) call `has_action()` to compute capabilities without enforcing
- Frontend `ProductVersionAllowedActions` interface and `allowed_actions` field in `ProductVersionItemFromAPI`
- `ProductDetail.tsx` write buttons now gated by `v.allowed_actions.can_update/can_release/can_retire`
- Create button gated by `versions[0].allowed_actions.can_create_sibling` (falls back to backend-authoritative for empty version list)
- Backend tests: 8 new capability tests (lifecycle matrix, with/without manage, read endpoint accessibility)
- Regression guard updated: 7 new checks (G13–G19) for capability contract

Out of scope:
- Product Version delete, reactivate, set_current, clone/copy
- BOM/Routing/ResourceRequirement binding
- ERP/PLM sync, Acceptance Gate, Backflush, Quality, Material movement
- Traceability genealogy
- Database migrations
- New write commands

## 2. Baseline Evidence Used

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/audit/mmd-fullstack-11-product-version-fe-write-intent.md`
- `backend/app/security/rbac.py` — confirmed `has_action()` is pure bool, safe for read handler use
- `backend/app/security/dependencies.py` — confirmed `RequestIdentity` structure
- `backend/app/schemas/product.py` — pre-11B `ProductVersionItem` shape
- `backend/app/services/product_version_service.py` — retire policy: blocks `is_current` and non-DRAFT/RELEASED
- `backend/app/api/v1/products.py` — confirmed read endpoints use `require_authenticated_identity`
- `frontend/src/app/api/productApi.ts` — pre-11B `ProductVersionItemFromAPI` shape
- `frontend/src/app/pages/ProductDetail.tsx` — pre-11B lifecycle-plausible button enabling

## 3. Capability Contract

| Lifecycle | is_current | has_manage | can_update | can_release | can_retire | can_create_sibling |
|---|---|---|---|---|---|---|
| DRAFT | false | true | T | T | T | T |
| DRAFT | true | true | T | T | F | T |
| RELEASED | false | true | F | F | T | T |
| RELEASED | true | true | F | F | F | T |
| RETIRED | any | true | F | F | F | T |
| any | any | false | F | F | F | F |

## 4. Backend Changes

### `backend/app/schemas/product.py`
- Added `ProductVersionAllowedActions(BaseModel)` with `can_update`, `can_release`, `can_retire`, `can_create_sibling` fields
- Added `allowed_actions: ProductVersionAllowedActions` field to `ProductVersionItem`

### `backend/app/services/product_version_service.py`
- Added import for `ProductVersionAllowedActions`
- Added `_compute_allowed_actions(row, has_manage) -> ProductVersionAllowedActions` helper
- Updated `_to_version_item(row, has_manage=False)` to call `_compute_allowed_actions`
- Updated `list_product_versions(…, has_manage_permission=False)` to accept and pass capability flag
- Updated `get_product_version(…, has_manage_permission=False)` to accept and pass capability flag
- Updated all write service functions (`create`, `update`, `release`, `retire`) to call `_to_version_item(row, has_manage=True)` since callers already hold manage permission

### `backend/app/api/v1/products.py`
- Added `from app.security.rbac import has_action` import
- Updated `list_product_versions` handler: calls `has_action(db, identity, "admin.master_data.product_version.manage")` (no enforcement, pure bool) and passes result to service
- Updated `get_product_version` handler: same pattern

## 5. Frontend Changes

### `frontend/src/app/api/productApi.ts`
- Added `ProductVersionAllowedActions` interface: `{ can_update, can_release, can_retire, can_create_sibling }`
- Added `allowed_actions: ProductVersionAllowedActions` field to `ProductVersionItemFromAPI`

### `frontend/src/app/api/index.ts`
- Added `ProductVersionAllowedActions` to the re-export type list

### `frontend/src/app/pages/ProductDetail.tsx`
- Edit button: `disabled={mutationBusyKey !== null || !v.allowed_actions.can_update}`
- Release button: `disabled={mutationBusyKey !== null || !v.allowed_actions.can_release}`
- Retire button: `disabled={mutationBusyKey !== null || !v.allowed_actions.can_retire}`
- Create submit button: `disabled={mutationBusyKey !== null || (versions.length > 0 && !versions[0].allowed_actions.can_create_sibling)}`
  - When version list is empty: button remains backend-authoritative (enabled; 403 handled by existing error handler)

### `frontend/scripts/mmd-read-integration-regression-check.mjs`
- Added 7 new guards (G13–G19):
  - G13: `ProductVersionAllowedActions` type defined in `productApi.ts`
  - G14: `ProductVersionItemFromAPI` includes `allowed_actions` field
  - G15: `ProductDetail` consumes `allowed_actions.can_update`
  - G16: `ProductDetail` consumes `allowed_actions.can_release`
  - G17: `ProductDetail` consumes `allowed_actions.can_retire`
  - G18: `ProductDetail` does NOT use raw `lifecycle_status !== "DRAFT"` on write button disabled
  - G19: `ProductDetail` does NOT use raw `v.is_current` on write button disabled

## 6. Authorization / Permission Decision

`has_action(db, identity, "admin.master_data.product_version.manage")` is called inside the two read handlers **without enforcement**. It:
- Returns `bool` — does not raise 403
- Uses the same `db` session from `Depends(get_db)`
- Handles impersonation path internally (checks `acting_role_code` first)
- Returns `False` for unauthenticated users

Read endpoints remain accessible to all authenticated users. Non-manage users receive data with all capability flags set to `False`. The frontend disables buttons based on these flags. Backend mutation endpoints remain final authority.

## 7. State Transition Guardrails

- `can_retire = False` when `is_current = True` — mirrors `retire_product_version` service invariant that rejects retire for current version
- `can_update = False` and `can_release = False` for RELEASED and RETIRED — mirrors service invariants
- `can_create_sibling` = `has_manage` regardless of version lifecycle — product-level action, not version-lifecycle-dependent

## 8. Boundary Guardrails

- No `lifecycle_status` or `is_current` write payload accepted (enforced by `extra="forbid"` on request schemas)
- No new write endpoints added
- No delete / reactivate / set_current / clone / binding controls added
- No database migration modified
- No frontend persona-based permission inference

## 9. Tests Added / Updated

### `backend/tests/test_product_version_foundation_api.py`
- `_make_session()`: patched `product_router_module.has_action` in `_build_app` to return `False` by default (no RBAC tables in test SQLite)
- `_build_app_with_manage(session_local, has_manage)`: dedicated builder that patches `has_action` to return the specified bool
- 8 new capability tests:
  - `test_list_versions_includes_allowed_actions_field`
  - `test_get_version_includes_allowed_actions_field`
  - `test_allowed_actions_all_false_for_user_without_manage`
  - `test_allowed_actions_draft_with_manage`
  - `test_allowed_actions_released_not_current_with_manage`
  - `test_allowed_actions_released_is_current_with_manage`
  - `test_allowed_actions_retired_with_manage`
  - `test_read_endpoints_return_200_for_non_manage_user`

## 10. Regression Coverage

`frontend/scripts/mmd-read-integration-regression-check.mjs`: 100 checks pass (up from 93).

New checks added:
| Guard | Check |
|---|---|
| G13 | `ProductVersionAllowedActions` type exists in productApi.ts |
| G14 | `ProductVersionItemFromAPI` includes `allowed_actions` field |
| G15 | ProductDetail consumes `allowed_actions.can_update` |
| G16 | ProductDetail consumes `allowed_actions.can_release` |
| G17 | ProductDetail consumes `allowed_actions.can_retire` |
| G18 | ProductDetail does not use raw `lifecycle_status !== "DRAFT"` on disabled write buttons |
| G19 | ProductDetail does not use raw `v.is_current` on disabled write buttons |

## 11. Verification Commands

All commands ran and confirmed:

```
# Backend
cd backend
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q \
  tests/test_product_version_foundation_api.py \
  tests/test_product_version_foundation_service.py \
  tests/test_mmd_rbac_action_codes.py
# Result: 60 passed, 1 warning

# Frontend
cd frontend
npm.cmd run check:mmd:read   # 100 passed, 0 failed
npm.cmd run build            # built in 9.75s
npm.cmd run lint             # PASS (0 errors)
npm.cmd run lint:i18n:registry  # 1770 keys EN/JA synchronized
npm.cmd run check:routes     # FAIL: 0
```

Note: `npm run lint:i18n` not run — pre-existing Windows CRLF issue in bash script (documented in MMD-FULLSTACK-11, non-blocking). No changes to hardcoded strings.

## 12. Remaining Risks / Deferred Items

1. **Create button for empty version list**: When a product has no versions yet, `can_create_sibling` cannot be derived from the list response. The create button remains backend-authoritative in this case (enabled, handles 403). A product-level capability endpoint could close this gap in a future slice.
2. **`lint:i18n` blocked by pre-existing CRLF issue on Windows**: Not introduced by this slice.
3. **No i18n strings added**: No new visible UI strings were needed for this slice.

## 13. Final Verdict

COMPLETE. All Definition of Done criteria are satisfied:

- ✓ Product Version read response includes server-derived `allowed_actions` capability
- ✓ Capabilities reflect backend permission (`has_action`) and lifecycle state
- ✓ `ProductDetail` consumes capability fields to enable/disable write controls
- ✓ `ProductDetail` does not infer write permission from persona or local lifecycle
- ✓ `ProductDetail` still handles backend 403/validation errors
- ✓ No new Product Version write command added
- ✓ No forbidden controls added
- ✓ No `lifecycle_status`/`is_current` FE payload
- ✓ Backend targeted tests pass (60/60)
- ✓ Frontend build/lint/i18n/routes pass (100/100 regression checks)
- ✓ Audit report created
- ✓ No migration modified
- ✓ No auto-commit performed
