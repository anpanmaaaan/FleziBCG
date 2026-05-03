# MMD-PV-WRITE-BASELINE-01 — Product Version Write Baseline Freeze / Handoff

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Frozen Product Version write baseline after backend write API, frontend write intent, server-derived row-level capability guard, product-level create capability, and capability truth patch. |

---

## Routing
- **Selected brain:** MOM Brain
- **Selected mode:** Full-stack baseline freeze / Critical reviewer / Authorization capability projection review
- **Hard Mode MOM:** v3 ON
- **Reason:** This report freezes Product Version write behavior, authorization capability projection, lifecycle transitions, and MMD boundary guardrails before expanding write paths to BOM or Reason Codes. Hard Mode MOM v3 is mandatory for any freeze that touches execution state machine adjacency, authorization truth, and operational event ownership.

---

## Pre-Writing Evidence

### Design Evidence Extract

All eight input slices were read before writing this report:

| Input | Status |
|---|---|
| `docs/audit/mmd-be-08-product-version-write-governance-contract.md` | Inspected |
| `docs/audit/mmd-be-08a-product-version-action-code-registry-patch.md` | Inspected |
| `docs/audit/mmd-be-11-product-version-write-api-foundation.md` | Inspected |
| `docs/audit/mmd-fullstack-11-product-version-fe-write-intent.md` | Inspected |
| `docs/audit/mmd-fullstack-11b-product-version-server-derived-capability-guard.md` | Inspected |
| `docs/audit/mmd-fullstack-11c-product-version-product-level-create-capability.md` | Inspected (includes 11C-A patch note) |
| `docs/audit/mmd-write-gov-01-command-boundary.md` | Inspected |
| `docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md` | Inspected |

Design source read:

| Input | Status |
|---|---|
| `docs/design/02_domain/product_definition/product-version-write-governance-contract.md` | Inspected |
| `docs/design/02_domain/product_definition/product-version-foundation-contract.md` | Inspected |
| `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` | Inspected |
| `docs/design/02_registry/action-code-registry.md` | Confirmed `admin.master_data.product_version.manage` registered |
| `docs/design/00_platform/product-business-truth-overview.md` | Inspected |

Source files inspected (not modified):

| File | Key Finding |
|---|---|
| `backend/app/security/rbac.py` | `admin.master_data.product_version.manage` registered, maps to ADMIN family |
| `backend/app/schemas/product.py` | `ProductVersionAllowedActions`, `ProductVersionItem.allowed_actions`, `ProductVersionProductCapabilities`, `ProductItem.product_version_capabilities` all present |
| `backend/app/services/product_version_service.py` | `_compute_allowed_actions`, lifecycle invariants enforced |
| `backend/app/services/product_service.py` | `has_pv_manage` parameter on all 4 write functions; default `False` |
| `backend/app/api/v1/products.py` | All 4 Product write handlers compute `has_pv_manage` from `has_action(db, identity, "admin.master_data.product_version.manage")` |
| `backend/app/repositories/product_version_repository.py` | CRUD mutations for product versions |
| `frontend/src/app/api/productApi.ts` | `ProductVersionAllowedActions`, `ProductVersionProductCapabilities`, `ProductVersionItemFromAPI.allowed_actions`, `ProductItemFromAPI.product_version_capabilities` present |
| `frontend/src/app/pages/ProductDetail.tsx` | Create button: `disabled={... \|\| !product.product_version_capabilities.can_create}`; row buttons: `can_update/can_release/can_retire` |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | 105 checks G1–G24 and section H |

### Event Map

| Product Version Action | Backend Endpoint | Backend Event | Audit Behavior | Forbidden Side Effects |
|---|---|---|---|---|
| create draft | `POST /products/{id}/versions` | `PRODUCT_VERSION.CREATED` | Written to `SecurityEventLog` | No execution event, no material event, no ERP post, no backflush, no quality decision |
| update draft metadata | `PATCH /products/{id}/versions/{vid}` | `PRODUCT_VERSION.UPDATED` | Written to `SecurityEventLog` | No lifecycle side-effect; only DRAFT allowed |
| release | `POST /products/{id}/versions/{vid}/release` | `PRODUCT_VERSION.RELEASED` | Written to `SecurityEventLog` | No BOM/Routing binding; no execution trigger |
| retire | `POST /products/{id}/versions/{vid}/retire` | `PRODUCT_VERSION.RETIRED` | Written to `SecurityEventLog` | Blocked if `is_current=True`; no traceability event |

### Invariant Map

| # | Invariant | Enforcement |
|---|---|---|
| I-01 | create always sets DRAFT, `is_current=False` | `product_version_service.create_product_version` |
| I-02 | `version_code` unique per product (scoped, not global) | service + `get_product_version_by_code` repo guard |
| I-03 | update only allowed in DRAFT status | service rejects non-DRAFT |
| I-04 | `lifecycle_status` / `is_current` fields forbidden in write payload | `extra="forbid"` on `ProductVersionCreateRequest` and `ProductVersionUpdateRequest` |
| I-05 | release only allowed from DRAFT | service rejects non-DRAFT |
| I-06 | retire allowed from DRAFT or RELEASED | service rejects RETIRED |
| I-07 | retire blocked when `is_current=True` | service explicit check |
| I-08 | `effective_from ≤ effective_to` when both provided | service validation helper |
| I-09 | parent product must exist under same tenant | service + product repo lookup |
| I-10 | `is_current` not mutated by create/update/release | service never touches `is_current` |
| I-11 | all Product Version write routes require `admin.master_data.product_version.manage` | `require_action(...)` at route layer |
| I-12 | read routes remain `require_authenticated_identity` only | confirmed in `products.py` |
| I-13 | deferred commands absent (delete/reactivate/set-current/clone/bind-*) | source-level route enumeration test |
| I-14 | `product_version_capabilities.can_create` derived only from `product_version.manage` | handlers compute `has_pv_manage = has_action(db, identity, "admin.master_data.product_version.manage")` |
| I-15 | `product.manage` does NOT imply `product_version_capabilities.can_create` | product write handlers compute `has_pv_manage` independently |
| I-16 | FE create button uses `product.product_version_capabilities.can_create` | confirmed in `ProductDetail.tsx:510` |
| I-17 | FE row buttons use `v.allowed_actions.can_update/can_release/can_retire` | confirmed in `ProductDetail.tsx:578,586,594` |

### State Transition Map

| Command | Source Status | Target Status | Supported | Notes |
|---|---|---|---|---|
| create | (new) | DRAFT | ✅ YES | `is_current=False` always |
| update | DRAFT | DRAFT | ✅ YES | metadata only |
| update | RELEASED | — | ❌ BLOCKED | service rejects |
| update | RETIRED | — | ❌ BLOCKED | service rejects |
| release | DRAFT | RELEASED | ✅ YES | |
| release | RELEASED | — | ❌ BLOCKED | |
| release | RETIRED | — | ❌ BLOCKED | |
| retire | DRAFT | RETIRED | ✅ YES | only if `is_current=False` |
| retire | RELEASED | RETIRED | ✅ YES | only if `is_current=False` |
| retire | RETIRED | — | ❌ BLOCKED | already retired |
| retire (is_current=True) | any | — | ❌ BLOCKED | service guard |
| delete | any | — | ❌ DEFERRED | not implemented |
| reactivate | RETIRED | — | ❌ DEFERRED | not implemented |
| set_current | any | — | ❌ DEFERRED | not implemented |
| clone/copy | any | — | ❌ DEFERRED | not implemented |

### Authorization / Capability Map

| Area | Backend Truth | FE Behavior | Evidence |
|---|---|---|---|
| Create new version | `has_action(db, identity, "admin.master_data.product_version.manage")` → `product_version_capabilities.can_create` | Create button `disabled={... \|\| !product.product_version_capabilities.can_create}` | `products.py:56,68`, `ProductDetail.tsx:510` |
| Update draft | `allowed_actions.can_update` from `_compute_allowed_actions` | Edit save button `disabled={... \|\| !v.allowed_actions.can_update}` | `ProductDetail.tsx:578` |
| Release | `allowed_actions.can_release` | Release button `disabled={... \|\| !v.allowed_actions.can_release}` | `ProductDetail.tsx:586` |
| Retire | `allowed_actions.can_retire` | Retire button `disabled={... \|\| !v.allowed_actions.can_retire}` | `ProductDetail.tsx:594` |
| Product.manage ≠ PV.manage | Verified: separate `has_action` calls | N/A — FE does not derive from product response | 11C-A patch, `products.py` write handlers |

### Test Matrix

| Test / Gate | Expected Result | Actual (2026-05-03) |
|---|---|---|
| `test_list_product_versions_returns_200_with_versions` | GET list returns versions with `allowed_actions` | PASS |
| `test_get_product_version_returns_200_with_correct_data` | GET detail returns version with `allowed_actions` | PASS |
| `test_create_product_version_requires_manage_action` | 403 without manage action | PASS |
| `test_create_product_version_creates_draft` | creates DRAFT, `is_current=False` | PASS |
| `test_create_product_version_rejects_is_current_payload` | 422 on `is_current` in payload | PASS |
| `test_update_product_version_rejects_lifecycle_status_patch` | 422 on `lifecycle_status` in payload | PASS |
| `test_release_product_version_changes_draft_to_released` | DRAFT → RELEASED | PASS |
| `test_retire_product_version_rejects_current_version_if_policy_applies` | retire blocked on `is_current=True` | PASS |
| `test_no_delete_reactivate_set_current_clone_binding_routes_exist` | route enumeration: forbidden routes absent | PASS |
| `test_product_detail_can_create_false_for_non_manage_user` | `can_create=false` when no `product_version.manage` | PASS |
| `test_product_detail_can_create_true_for_manage_user` | `can_create=true` when has `product_version.manage` | PASS |
| `test_product_write_response_can_create_false_when_no_pv_manage` | write response `can_create=false` without PV manage | PASS |
| `test_product_write_response_can_create_true_when_has_pv_manage` | write response `can_create=true` with PV manage | PASS |
| `test_product_version_manage_action_code_exists` | `admin.master_data.product_version.manage` in registry | PASS |
| Backend pytest (4 test files) | 69 passed, 1 warning | PASS — run 2026-05-03 |
| `npm run check:mmd:read` (105 checks) | 105 passed, 0 failed | PASS — run 2026-05-03 |
| `npm run build` | Clean build | PASS — built in 18.80s |
| `npm run lint` | 0 ESLint errors | PASS |
| `npm run lint:i18n:registry` | 1770 keys EN/JA synchronized | PASS |
| `npm run check:routes` | All route smoke checks pass | PASS |

### Verdict Before Writing

All required invariants verified against live source. No stop condition triggered. Report may proceed.

---

## 1. Scope

This report freezes the complete Product Version write baseline as of 2026-05-03, after completion of:

| Slice | Type | Summary |
|---|---|---|
| MMD-BE-08 | Governance / documentation | Product Version write governance contract |
| MMD-BE-08A | Backend registry patch | `admin.master_data.product_version.manage` added to action-code registry |
| MMD-BE-11 | Backend implementation | Product Version write API: create/update/release/retire |
| MMD-BE-11A | Backend guardrail patch | `SecurityEventLog` audit event boundary enforcement |
| MMD-FULLSTACK-11 | Full-stack write intent | FE write intent wired to governed backend APIs |
| MMD-FULLSTACK-11B | Full-stack capability | Server-derived row-level `allowed_actions` in FE controls |
| MMD-FULLSTACK-11C | Full-stack capability | Product-level `product_version_capabilities.can_create` for empty-version first-use case |
| MMD-FULLSTACK-11C-A | Backend guardrail patch | Capability truth fix: `product.manage` no longer implies `can_create=true` |

**Out of scope for this freeze:**
- Product Version delete, reactivate, set_current, clone/copy
- BOM/Routing/Resource Requirement binding
- ERP/PLM sync, engineering change workflow
- `is_current` assignment
- Execution, quality, material, backflush, traceability

---

## 2. Baseline Inputs Reviewed

| Input | Status | Key Finding |
|---|---|---|
| `mmd-be-08-product-version-write-governance-contract.md` | ✅ | Governance contract locked before implementation |
| `mmd-be-08a-product-version-action-code-registry-patch.md` | ✅ | Action code registered in `rbac.py` |
| `mmd-be-11-product-version-write-api-foundation.md` | ✅ | 4 write endpoints with invariants |
| `mmd-fullstack-11-product-version-fe-write-intent.md` | ✅ | FE write intent wired; no mock; error handling in place |
| `mmd-fullstack-11b-product-version-server-derived-capability-guard.md` | ✅ | `allowed_actions` on every version item |
| `mmd-fullstack-11c-product-version-product-level-create-capability.md` | ✅ | Product-level `can_create` added; 11C-A truth patch applied |
| `mmd-write-gov-01-command-boundary.md` | ✅ | Command boundary matrix |
| `mmd-read-baseline-02-complete-read-integration-freeze-handoff.md` | ✅ | Read baseline confirmed before write began |

---

## 3. Source Inspection Summary

### Backend

| File | Status | Key State |
|---|---|---|
| `backend/app/security/rbac.py` | ✅ Inspected | `admin.master_data.product_version.manage` registered; `has_action()` is pure bool |
| `backend/app/schemas/product.py` | ✅ Inspected | `ProductVersionAllowedActions`, `ProductVersionProductCapabilities`, `ProductVersionCreateRequest(extra=forbid)`, `ProductVersionUpdateRequest(extra=forbid)` |
| `backend/app/repositories/product_version_repository.py` | ✅ Inspected | CRUD for versions |
| `backend/app/services/product_version_service.py` | ✅ Inspected | `_compute_allowed_actions`, lifecycle invariants, `has_manage_permission` param |
| `backend/app/services/product_service.py` | ✅ Inspected | `has_pv_manage: bool = False` on all write functions; default conservative |
| `backend/app/api/v1/products.py` | ✅ Inspected | All 4 Product write handlers compute `has_pv_manage` independently from `product_version.manage`; all 4 PV write routes require `product_version.manage` |

### Frontend

| File | Status | Key State |
|---|---|---|
| `frontend/src/app/api/productApi.ts` | ✅ Inspected | `ProductVersionAllowedActions`, `ProductVersionProductCapabilities` defined; `ProductVersionItemFromAPI.allowed_actions` and `ProductItemFromAPI.product_version_capabilities` present |
| `frontend/src/app/api/index.ts` | ✅ Inspected | Both types exported |
| `frontend/src/app/pages/ProductDetail.tsx` | ✅ Inspected | Create: `!product.product_version_capabilities.can_create`; row actions: `can_update/can_release/can_retire` |
| `frontend/src/app/screenStatus.ts` | ✅ Inspected | `productDetail: { phase: "PARTIAL", dataSource: "BACKEND_API" }` |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | ✅ Inspected | 105 checks including G13–G24 capability contract locks |

---

## 4. Implemented Product Version Write Baseline

### 4.1 Implemented Command Matrix

| Command | Backend Route | FE Control | Auth Action Code | Lifecycle Rule | Status |
|---|---|---|---|---|---|
| create draft | `POST /products/{id}/versions` | Create form + button in `ProductDetail` | `admin.master_data.product_version.manage` | Sets DRAFT, `is_current=False`; unique `version_code` per product | ✅ IMPLEMENTED |
| update draft metadata | `PATCH /products/{id}/versions/{vid}` | Inline edit form per-row in `ProductDetail` | `admin.master_data.product_version.manage` | DRAFT only; rejects `lifecycle_status` / `is_current` payload | ✅ IMPLEMENTED |
| release | `POST /products/{id}/versions/{vid}/release` | Release button per-row in `ProductDetail` | `admin.master_data.product_version.manage` | DRAFT → RELEASED only | ✅ IMPLEMENTED |
| retire | `POST /products/{id}/versions/{vid}/retire` | Retire button per-row in `ProductDetail` | `admin.master_data.product_version.manage` | DRAFT/RELEASED → RETIRED; blocked for `is_current=True` | ✅ IMPLEMENTED |

### 4.2 Forbidden / Deferred Command Matrix

| Command | Decision | Reason | Future Requirement |
|---|---|---|---|
| delete | ❌ DEFERRED | No Product Version delete governance established; traceability / genealogy impact unresolved | Full governance contract + safety analysis required |
| reactivate | ❌ DEFERRED | RETIRED state is intended to be terminal in this phase | Governance contract + lifecycle proof required |
| set_current | ❌ DEFERRED | `is_current` semantics not yet governed for write; ERP/PLM truth boundary undefined | Dedicated MMD-PV-WRITE-02 governance slice required |
| clone/copy | ❌ DEFERRED | Engineering change workflow out of scope | PLM/engineering workflow governance required |
| bind_to_bom | ❌ DEFERRED | BOM write governance not yet established | MMD-BE-09 BOM write governance first |
| bind_to_routing | ❌ DEFERRED | Routing binding lifecycle undefined | BOM and Routing write governance first |
| bind_to_resource_requirement | ❌ DEFERRED | Resource Requirement binding contract not established | After Routing binding governance |
| bulk_import | ❌ DEFERRED | No bulk write governance | Dedicated bulk import contract required |
| bulk_retire | ❌ DEFERRED | No bulk lifecycle governance | Same |
| ERP/PLM sync | ❌ OUT OF SCOPE | Product Version is MMD master data, not ERP revision truth | ERP integration contract required |
| engineering change workflow | ❌ OUT OF SCOPE | ECO/ECN not in current platform scope | Separate domain contract |

---

## 5. Backend API Baseline

### Routes registered at `GET|POST /api/v1/products/{product_id}/versions`

| Method | Path | Auth | Response Model |
|---|---|---|---|
| `GET` | `/products/{product_id}/versions` | `require_authenticated_identity` | `list[ProductVersionItem]` |
| `POST` | `/products/{product_id}/versions` | `require_action("admin.master_data.product_version.manage")` | `ProductVersionItem` |
| `GET` | `/products/{product_id}/versions/{version_id}` | `require_authenticated_identity` | `ProductVersionItem` |
| `PATCH` | `/products/{product_id}/versions/{version_id}` | `require_action("admin.master_data.product_version.manage")` | `ProductVersionItem` |
| `POST` | `/products/{product_id}/versions/{version_id}/release` | `require_action("admin.master_data.product_version.manage")` | `ProductVersionItem` |
| `POST` | `/products/{product_id}/versions/{version_id}/retire` | `require_action("admin.master_data.product_version.manage")` | `ProductVersionItem` |

### Confirmed absent routes (verified by `test_no_delete_reactivate_set_current_clone_binding_routes_exist`):

DELETE, reactivate, set_current, clone, bind_to_bom, bind_to_routing, bind_to_resource_requirement — not registered.

### Request Schema Guards (`extra="forbid"`)

| Schema | Forbidden Fields |
|---|---|
| `ProductVersionCreateRequest` | `lifecycle_status`, `is_current`, any extra field |
| `ProductVersionUpdateRequest` | `lifecycle_status`, `is_current`, `version_code`, any extra field |

---

## 6. Frontend UI Baseline

### ProductDetail.tsx

| Control | Governing Capability | Condition |
|---|---|---|
| Create version button | `product.product_version_capabilities.can_create` | `disabled={mutationBusyKey !== null \|\| !product.product_version_capabilities.can_create}` |
| Save edit button (per-row) | `v.allowed_actions.can_update` | `disabled={mutationBusyKey !== null \|\| !v.allowed_actions.can_update}` |
| Release button (per-row) | `v.allowed_actions.can_release` | `disabled={mutationBusyKey !== null \|\| !v.allowed_actions.can_release}` |
| Retire button (per-row) | `v.allowed_actions.can_retire` | `disabled={mutationBusyKey !== null \|\| !v.allowed_actions.can_retire}` |

**Screen status:** `productDetail: { phase: "PARTIAL", dataSource: "BACKEND_API" }` — PARTIAL because routing/BOM/quality sections remain placeholder.

**FE invariants confirmed:**
- No `lifecycle_status` or `is_current` in write payload
- No persona/role inference for capability
- No set_current/delete/reactivate/clone controls
- Error handling for 400/401/403/404/409/422

---

## 7. Authorization / Capability Baseline

### 7.1 Capability Matrix

| Capability | Level | Backend Source | FE Consumer | Rule |
|---|---|---|---|---|
| `allowed_actions.can_update` | Row (version) | `_compute_allowed_actions(row, has_manage)` → `DRAFT and not is_current is not required, just DRAFT` → `lifecycle_status == "DRAFT" and has_manage` | `ProductDetail` per-row edit save button | True iff DRAFT and has manage |
| `allowed_actions.can_release` | Row (version) | `_compute_allowed_actions` → `lifecycle_status == "DRAFT" and has_manage` | `ProductDetail` per-row release button | True iff DRAFT and has manage |
| `allowed_actions.can_retire` | Row (version) | `_compute_allowed_actions` → `lifecycle_status in (DRAFT, RELEASED) and not is_current and has_manage` | `ProductDetail` per-row retire button | True iff DRAFT/RELEASED, not current, has manage |
| `allowed_actions.can_create_sibling` | Row (version) | `_compute_allowed_actions` → `has_manage` | Not used as primary create gate (superseded by 11C) | True iff has manage; row-scoped |
| `product_version_capabilities.can_create` | Product | `has_action(db, identity, "admin.master_data.product_version.manage")` in `list_products` / `get_product_by_id` / all 4 product write handlers | `ProductDetail` create button (primary gate) | True iff `product_version.manage` — independent of `product.manage` |

### 7.2 Capability Truth Invariant (11C-A)

> `product_version_capabilities.can_create == true` **iff** `has_action(db, identity, "admin.master_data.product_version.manage") == true`
>
> `admin.master_data.product.manage` does **not** imply `can_create == true`.
>
> Default for `has_pv_manage` in all product service write functions is `False`.

---

## 8. Lifecycle Transition Baseline

```
                    create
                      │
                   [DRAFT] ──── retire (not is_current) ──► [RETIRED]
                      │
                   release
                      │
                 [RELEASED] ──── retire (not is_current) ──► [RETIRED]

Blocked:
  [RETIRED] → any    (no reactivate)
  retire when is_current=True
  release when RELEASED or RETIRED
  update when RELEASED or RETIRED
  set_current (deferred)
  delete (deferred)
```

---

## 9. Audit / Event Baseline

| Event | Source Table | Triggered By | Payload Fields |
|---|---|---|---|
| `PRODUCT_VERSION.CREATED` | `SecurityEventLog` | `create_product_version` service | `product_version_id`, `version_code`, `product_id`, `lifecycle_status`, `changed_fields`, `occurred_at` |
| `PRODUCT_VERSION.UPDATED` | `SecurityEventLog` | `update_product_version` service | same + changed field names |
| `PRODUCT_VERSION.RELEASED` | `SecurityEventLog` | `release_product_version` service | `changed_fields: ["lifecycle_status"]` |
| `PRODUCT_VERSION.RETIRED` | `SecurityEventLog` | `retire_product_version` service | `changed_fields: ["lifecycle_status"]` |

**No cross-domain side effects.** These events are isolated within the MMD audit boundary. No execution event, material event, quality event, ERP posting, backflush, or traceability genealogy entry is triggered.

---

## 10. Regression Coverage Baseline

### 10.1 Backend Tests

| Test File | Tests | Key Areas |
|---|---|---|
| `test_product_foundation_api.py` | 9 tests | Product CRUD + capability truth (11C, 11C-A) |
| `test_product_version_foundation_api.py` | 21 tests | All 4 write routes + RBAC gate + forbidden route absence + cross-product isolation + capability behavior |
| `test_product_version_foundation_service.py` | 12 tests | Service-level invariants: DRAFT-only update, retire policy, date validation, `is_current` immutability, event boundary |
| `test_mmd_rbac_action_codes.py` | ~15 tests | Action code registry: `product_version.manage` exists, ADMIN family, no `user.manage` on product routes |
| **Total** | **69 passed, 1 warning** | Warning: non-test-DB URL advisory; test isolation confirmed |

### 10.2 Frontend Regression

| Check | Count | Status |
|---|---|---|
| `npm run check:mmd:read` | 105 checks (G1–G24 + sections A–H) | **105 passed, 0 failed** — run 2026-05-03 |
| `npm run build` | — | **PASS** (built in 18.80s) |
| `npm run lint` | — | **PASS** (0 ESLint errors) |
| `npm run lint:i18n:registry` | 1770 keys | **PASS** (EN/JA synchronized) |
| `npm run check:routes` | All route smokes | **PASS** |

### 10.3 Key Regression Guards (G-section)

| Guard | ID | What It Locks |
|---|---|---|
| G13 | `pv_api_allowed_actions_type_defined` | `ProductVersionAllowedActions` type in `productApi.ts` |
| G14 | `pv_api_version_item_has_allowed_actions` | `ProductVersionItemFromAPI.allowed_actions` field present |
| G15–G17 | Capability matrix checks | `can_update/can_release/can_retire` gates correct |
| G18 | `pv_product_detail_no_lifecycle_only_button_guard` | No raw `lifecycle_status` as sole write gate |
| G19 | `pv_product_detail_no_is_current_only_button_guard` | No raw `is_current` as sole write gate |
| G20 | `pv_api_product_caps_type_defined` | `ProductVersionProductCapabilities` type in `productApi.ts` |
| G21 | `pv_api_product_item_has_capabilities` | `ProductItemFromAPI.product_version_capabilities` field |
| G22 | `pv_product_detail_uses_product_level_can_create` | Create button uses `product.product_version_capabilities.can_create` |
| G23 | `pv_product_detail_no_version0_create_gate` | `versions[0].allowed_actions.can_create_sibling` no longer primary gate |
| G24 | `pv_product_detail_no_persona_create_inference` | No `role_code` inference for create capability |

---

## 11. Boundary Guardrails

| Boundary | Current Decision | Evidence | Risk if Violated |
|---|---|---|---|
| Product Version vs ERP/PLM | Product Version is MMD operational truth, NOT ERP revision truth | `product-business-truth-overview.md`, 11B/11C report non-negotiables | If treated as ERP revision, downstream manufacturing would use un-governed revision state |
| Product Version vs BOM | Product Version carries no BOM binding | No `bom_id` in `ProductVersion` schema; no bind route implemented | Premature BOM binding before contract would create orphaned BOM state |
| Product Version vs Routing | No Routing binding implemented or planned | No bind route; route absent in enumeration test | Premature binding would create unverified recipe/routing state |
| Product Version vs Resource Requirement | No RR binding implemented or planned | Same | Same |
| Product Version vs Execution | No execution trigger from any PV write | Event boundary test `test_product_version_events_stay_within_mmd_audit_boundary` | Station execution must not depend on volatile PV lifecycle state |
| Product Version vs Quality | No quality hold or quality link from PV write | No `quality_hold` or `quality_event` in event payload | Quality decisions must not derive from PV lifecycle transitions |
| Product Version vs Material / Backflush | No material movement or backflush trigger | No `material_event`, no `backflush_trigger` in any PV service | Backflush correctness depends on separate BOM/Routing bind governance |
| Product Version vs Traceability / Genealogy | No genealogy link from PV write | No `genealogy_entry` or `traceability_event` in service | Traceability is a separate domain; PV write must not create phantom genealogy |
| Frontend UI vs Authorization Truth | FE only consumes server-derived capabilities; never infers from persona | G22–G24 regression guards; no `role_code` inference pattern | If FE infers, unauthorized users see enabled controls |
| Product manage vs Product Version manage | Separate independent action codes | 11C-A patch; all write handlers compute `has_pv_manage` independently | If conflated, Product admin gets PV create capability they were not granted |

---

## 12. Known Gaps / Deferred Items

| Gap | Severity | Notes |
|---|---|---|
| `set_current` governance | HIGH — no implementation | Critical path before BOM/Routing bind; `is_current` semantics undefined for write | Requires MMD-PV-WRITE-02 |
| `allowed_actions.can_create_sibling` usage in first-use case | LOW — resolved by 11C | `can_create_sibling` still exists on row items; may be confusing but not a bug. Could be removed in future cleanup. |
| `productDetail` screen status `PARTIAL` | LOW — expected | Routing, BOM, and Quality sections remain placeholder. Not a regression. |
| ERP/PLM binding contract | OUT OF SCOPE | No contract exists for ERP-side sync. Remains deferred indefinitely. |
| `is_current` write governance | HIGH — deferred | `is_current` is immutable through current write commands. Only a dedicated `set_current` command (deferred) may change it. |
| i18n lint CRLF blocker | INFO | If `npm run lint:i18n` (not `lint:i18n:registry`) is blocked by CRLF in locale files, this is a known non-critical issue. `lint:i18n:registry` (1770 keys) is the governed gate. |
| Backend test DB isolation warning | INFO | Advisory warning: test suite points to non-test-named DB. Tests use SQLite in-memory; actual DB not affected. |

---

## 13. Do-Not-Do Rules for Future Agents

The following actions are **explicitly forbidden** without a separate governance slice and Hard Mode MOM v3 evidence:

1. **Do not add `set_current` to ProductVersion** without MMD-PV-WRITE-02 governance contract.
2. **Do not add delete/reactivate/clone/copy ProductVersion** without full delete governance and traceability impact analysis.
3. **Do not bind ProductVersion to BOM** without MMD-BE-09 BOM write governance established first.
4. **Do not bind ProductVersion to Routing or Resource Requirement** without BOM binding being governed first.
5. **Do not infer ProductVersion create capability from persona/role_code** — `product_version_capabilities.can_create` must always come from `has_action(db, identity, "admin.master_data.product_version.manage")`.
6. **Do not treat `product.manage` as implying `product_version.manage`** — these are separate action codes.
7. **Do not trigger execution events, material events, quality events, backflush, or ERP posts** from any ProductVersion write command.
8. **Do not add is_current to write payloads** — `is_current` is backend-controlled.
9. **Do not add lifecycle_status to write payloads** — `extra="forbid"` on request schemas is an active invariant.
10. **Do not bypass server-derived `allowed_actions`** by re-enabling write buttons via local lifecycle inference.
11. **Do not use `versions[0].allowed_actions.can_create_sibling` as the primary create gate** — `product.product_version_capabilities.can_create` is the governing field.
12. **Do not remove regression guards G13–G24** without replacing them with equivalent or stronger checks.
13. **Do not treat ProductVersion as ERP revision truth** — it is MMD manufacturing definition master data.

---

## 14. Recommended Next Slices

### Recommended: MMD-BE-09 — BOM Write Governance / Minimal Mutation Contract

**Reason:** Product Version write baseline is now governed and frozen. BOM is the next MMD read-complete domain with no write governance. BOM mutations (create/update BOM header and BOM components) are the next natural step in manufacturing master data completeness.

**Prerequisites satisfied:**
- MMD BOM read model exists (`mmd-be-05`, `mmd-fullstack-07`)
- BOM foundation contract locked (`mmd-be-04`)
- MMD-WRITE-GOV-01 command boundary matrix prepared BOM for write governance
- No BOM write endpoints currently exist (confirmed in route enumeration)

### Alternative: MMD-PV-WRITE-02 — Product Version set_current Governance Contract

**Choose if:** Business explicitly requires current-version switching for production order assignment before BOM write governance. Requires dedicated governance contract first; no implementation before contract.

### Alternative: MMD-FE-QA-02 — Browser Screenshot Runtime QA / Visual Evidence Pack

**Choose if:** Visual/runtime evidence of Product Version write controls is required before continuing backend domain work. Preferred when showing stakeholders current write-gated UI state.

---

## 15. Verification Commands

All commands ran on 2026-05-03 against current source. Evidence is live.

```bash
# Backend
cd backend
python -m pytest -q tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_product_version_foundation_service.py tests/test_mmd_rbac_action_codes.py
# Result: 69 passed, 1 warning

# Frontend
cd frontend
npm run check:mmd:read
# Result: 105 passed, 0 failed

npm run build
# Result: built in 18.80s (PASS)

npm run lint
# Result: 0 errors (PASS)

npm run lint:i18n:registry
# Result: 1770 keys EN/JA synchronized (PASS)

npm run check:routes
# Result: All route smoke checks PASS
```

---

## 16. Final Freeze Verdict

**FROZEN. Product Version write baseline is verified and locked as of 2026-05-03.**

All required invariants are enforced:

- ✅ Backend owns Product Version mutation truth
- ✅ Frontend sends intent only
- ✅ Frontend does not infer Product Version permission from persona
- ✅ Mutation endpoints require `admin.master_data.product_version.manage`
- ✅ Read endpoints remain `require_authenticated_identity` only
- ✅ FE row controls governed by server-derived `allowed_actions`
- ✅ FE create control governed by `product_version_capabilities.can_create`
- ✅ No `lifecycle_status` payload from FE
- ✅ No `is_current` payload from FE
- ✅ No set_current/delete/reactivate/clone/binding command implemented
- ✅ No BOM/Routing/Resource Requirement binding
- ✅ No execution/quality/material/backflush/ERP/traceability side effects
- ✅ `product.manage` does NOT imply Product Version create capability
- ✅ `product_version_capabilities.can_create` derived exclusively from `admin.master_data.product_version.manage`
- ✅ 69 backend tests passing
- ✅ 105 frontend regression guards passing
- ✅ Build, lint, i18n, and route checks all clean

**Recommended next slice: MMD-BE-09 — BOM Write Governance / Minimal Mutation Contract**
