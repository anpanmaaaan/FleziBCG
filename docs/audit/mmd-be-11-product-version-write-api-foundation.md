# MMD-BE-11 — Product Version Write API Foundation Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Implement ProductVersion write API: create/update/release/retire with governance invariants. |

## 1. Scope

In scope:
- POST `/products/{product_id}/versions` — create Product Version (DRAFT only)
- PATCH `/products/{product_id}/versions/{version_id}` — update DRAFT metadata
- POST `/products/{product_id}/versions/{version_id}/release` — release DRAFT → RELEASED
- POST `/products/{product_id}/versions/{version_id}/retire` — retire DRAFT or RELEASED
- New Pydantic request schemas: `ProductVersionCreateRequest`, `ProductVersionUpdateRequest`
- Repository mutations: `create_product_version`, `update_product_version`, `get_product_version_by_code`
- Service layer: `create_product_version`, `update_product_version`, `release_product_version`, `retire_product_version`
- Authorization: all four write routes enforce `require_action("admin.master_data.product_version.manage")`
- API test suite expansion to cover write behaviors and scope guards
- Service test suite expansion to cover mutation invariants
- RBAC source-level test reconciliation for allowed write routes

Out of scope:
- DELETE / reactivate / set-current / clone / bind-bom / bind-routing / bind-resource-requirement
- `is_current` assignment (deferred)
- BOM/Routing binding lifecycle (deferred)
- Frontend changes
- DB migrations or schema changes

## 2. Baseline Evidence Used

Mandatory evidence inspected:
- docs/audit/mmd-be-08-product-version-write-governance-contract.md
- docs/audit/mmd-be-08a-product-version-action-code-registry-patch.md
- docs/design/02_domain/product_definition/product-version-write-governance-contract.md
- docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md
- docs/governance/CODING_RULES.md
- backend/app/security/rbac.py (action code registry)
- backend/app/api/v1/products.py (pre-edit state)
- backend/app/services/product_version_service.py (pre-edit state)
- backend/app/schemas/product.py (pre-edit state)
- backend/app/repositories/product_version_repository.py (pre-edit state)

## 3. Pre-Coding Evidence Maps

### 3.1 Event Map
| Action | Event type recorded |
|---|---|
| create_product_version | `PRODUCT_VERSION.CREATED` |
| update_product_version | `PRODUCT_VERSION.UPDATED` |
| release_product_version | `PRODUCT_VERSION.RELEASED` |
| retire_product_version | `PRODUCT_VERSION.RETIRED` |

All events written to `SecurityEventLog` via `_emit_product_version_event`.
Product Version write path changes MMD manufacturing definition truth and must remain isolated from execution state machine behavior. No execution command, execution state transition, material movement, backflush, ERP posting, quality decision, or traceability genealogy is triggered by this slice.

### 3.2 Invariant Map
| # | Invariant | Enforcement layer |
|---|---|---|
| I-01 | create always sets DRAFT, `is_current=False` | service |
| I-02 | version_code unique per product (not globally) | service + repo query |
| I-03 | update only allowed in DRAFT status | service |
| I-04 | lifecycle_status / is_current fields rejected in update schema | Pydantic `extra="forbid"` + explicit field exclusion |
| I-05 | release only allowed in DRAFT status | service |
| I-06 | retire allowed in DRAFT or RELEASED | service |
| I-07 | retire rejected if `is_current=True` | service |
| I-08 | effective_from must be ≤ effective_to if both provided | service validation helper |
| I-09 | parent product must exist under same tenant | service + product repo lookup |
| I-10 | is_current not mutated by create/update/release | service (not touched) |
| I-11 | all write routes require `admin.master_data.product_version.manage` | API layer |
| I-12 | read routes remain `require_authenticated_identity` only | API layer |
| I-13 | deferred commands (delete/reactivate/set-current/clone/bind-*) absent | source-level test + route enumeration test |

### 3.3 State Transition Map
```
DRAFT → RELEASED  (release)
DRAFT → RETIRED   (retire)
RELEASED → RETIRED (retire)

Blocked transitions:
RELEASED → RELEASED (release rejected with 400)
RETIRED → RELEASED  (release rejected with 400)
RETIRED → DRAFT     (reactivate — deferred, not implemented)
```

### 3.4 Test Matrix
| Test | Target | Layer |
|---|---|---|
| test_create_product_version_requires_manage_action | POST /versions | API |
| test_create_product_version_creates_draft | create lifecycle | API |
| test_create_product_version_rejects_duplicate_code_for_same_product | I-02 | API |
| test_create_product_version_allows_same_code_for_different_product | I-02 per-product isolation | API |
| test_update_product_version_requires_manage_action | PATCH | API |
| test_update_product_version_allows_draft_metadata_update | DRAFT update | API |
| test_update_product_version_rejects_released | I-03 | API |
| test_update_product_version_rejects_retired | I-03 | API |
| test_update_product_version_rejects_lifecycle_status_patch | I-04 | API |
| test_release_product_version_requires_manage_action | POST /release | API |
| test_release_product_version_changes_draft_to_released | I-05/transition | API |
| test_release_product_version_rejects_released_or_retired | I-05 | API |
| test_retire_product_version_requires_manage_action | POST /retire | API |
| test_retire_product_version_changes_draft_or_released_to_retired | I-06/transition | API |
| test_retire_product_version_rejects_current_version_if_policy_applies | I-07 | API |
| test_write_routes_return_404_for_wrong_product | cross-product isolation | API |
| test_no_delete_reactivate_set_current_clone_binding_routes_exist | I-13 scope guard | API |
| test_read_endpoints_do_not_require_manage_action | I-12 | API source |
| test_create_product_version_validates_product_exists | I-09 | Service |
| test_create_product_version_sets_draft_default | I-01 | Service |
| test_create_product_version_enforces_unique_code_per_product | I-02 | Service |
| test_update_product_version_only_draft | I-03 | Service |
| test_release_only_draft | I-05 | Service |
| test_retire_draft_or_released | I-06 | Service |
| test_effective_date_range_validation | I-08 | Service |
| test_no_is_current_change_in_create_update_release | I-10 | Service |
| test_product_version_tenant_and_product_isolation_reads | isolation | Service |
| test_product_version_write_routes_use_product_version_action_code | I-11 | RBAC source |
| test_no_product_version_delete_reactivate_set_current_clone_binding_routes_exist | I-13 | RBAC source |

### 3.5 Verdict Before Coding
PROCEED — all required invariants mapped, test matrix defined, state transitions enumerated. No deferred commands allowed in scope.

## 4. Files Changed

### Backend implementation
- `backend/app/schemas/product.py` — added `ProductVersionCreateRequest`, `ProductVersionUpdateRequest`
- `backend/app/repositories/product_version_repository.py` — added `get_product_version_by_code`, `create_product_version`, `update_product_version`
- `backend/app/services/product_version_service.py` — added `create_product_version`, `update_product_version`, `release_product_version`, `retire_product_version`, `_validate_effective_date_range`, `_emit_product_version_event`
- `backend/app/api/v1/products.py` — added four write endpoints with `require_action("admin.master_data.product_version.manage")`

### Test files
- `backend/tests/test_product_version_foundation_api.py` — full rewrite for BE-11 write coverage
- `backend/tests/test_product_version_foundation_service.py` — full rewrite for BE-11 service invariants
- `backend/tests/test_mmd_rbac_action_codes.py` — replaced `test_no_product_version_write_routes_exist_yet` with write-route action-code assertions and deferred-command scope guard

## 5. Invariant Enforcement Details

### create — DRAFT default (I-01, I-10)
Service forces `lifecycle_status="DRAFT"` and `is_current=False` regardless of payload. Schema does not expose these fields (extra="forbid").

### Unique version_code per product (I-02)
Service calls `get_product_version_by_code(db, tenant_id, product_id, version_code)` before insert. Raises `ValueError("Duplicate version_code")` on conflict → API returns HTTP 409.

### DRAFT-only update (I-03, I-04)
Service checks `version.lifecycle_status == "DRAFT"` before any mutation. `lifecycle_status` and `is_current` are not fields in `ProductVersionUpdateRequest`; Pydantic `extra="forbid"` rejects them at request validation → HTTP 422.

### Release DRAFT-only (I-05)
Service checks `lifecycle_status == "DRAFT"` before transitioning to `RELEASED`. Any other status raises `ValueError("Only DRAFT versions can be released")` → HTTP 400.

### Retire DRAFT or RELEASED (I-06, I-07)
Service checks `lifecycle_status in ("DRAFT", "RELEASED")`. If `is_current=True`, raises `ValueError("Cannot retire the current version")` → HTTP 400.

### Date range validation (I-08)
`_validate_effective_date_range` compares parsed dates. Raises `ValueError` with `effective_from > effective_to` message → HTTP 400.

### Parent product validation (I-09)
Service calls `product_repository.get_product(db, tenant_id, product_id)`. Returns `None` → raises `LookupError("Product not found")` → HTTP 404.

## 6. Authorization Summary

| Route | Method | Guard |
|---|---|---|
| `/products/{product_id}/versions` | GET | `require_authenticated_identity` |
| `/products/{product_id}/versions/{version_id}` | GET | `require_authenticated_identity` |
| `/products/{product_id}/versions` | POST | `require_action("admin.master_data.product_version.manage")` |
| `/products/{product_id}/versions/{version_id}` | PATCH | `require_action("admin.master_data.product_version.manage")` |
| `/products/{product_id}/versions/{version_id}/release` | POST | `require_action("admin.master_data.product_version.manage")` |
| `/products/{product_id}/versions/{version_id}/retire` | POST | `require_action("admin.master_data.product_version.manage")` |

## 7. Verification Results

### Backend — Product Version API + Service tests
```
31 passed in 2.12s
```
Files: `tests/test_product_version_foundation_api.py`, `tests/test_product_version_foundation_service.py`

### Backend — RBAC action-code tests
```
18 passed in 0.62s
```
File: `tests/test_mmd_rbac_action_codes.py`

### Backend — Adjacent MMD regression
```
24 passed in 2.08s
```
Files: `tests/test_product_foundation_api.py`, `tests/test_bom_foundation_api.py`, `tests/test_reason_code_foundation_api.py`

### Frontend — MMD read regression check
```
84 passed, 0 failed — PASS all checks
```

### Frontend — Route smoke check
```
PASS: 24 / 0 failed
```

## 8. Boundary Guardrails Verified

- No delete / reactivate / set-current / clone / bind-* routes added.
- Product Version events remain MMD lifecycle/audit entries in `SecurityEventLog` only; no execution command/event, material movement, backflush, ERP posting, quality decision, or traceability/genealogy side effect is emitted.
- No `is_current` mutation in create/update/release.
- No frontend source changed.
- No DB migration/schema changes.
- Read endpoints remain `require_authenticated_identity` only.
- Existing product/BOM/reason-code tests unaffected.

## 9. Remaining Risks / Deferred Items

- `is_current` assignment logic is deferred to a dedicated release-management slice.
- BOM/Routing/Resource-Requirement binding commands remain deferred.
- Reactivate (RETIRED → DRAFT) is deferred.
- Role seed review for `admin.master_data.product_version.manage` in environment-specific data is an operational follow-up if needed.

## 10. Final Verdict

PASS — MMD-BE-11 completed as the minimal Product Version write API foundation.

Definition of done status:
- Four write endpoints implemented with correct action-code guard.
- All lifecycle invariants enforced at service layer.
- Schema rejects forbidden fields at boundary.
- Full API and service test coverage for every invariant in scope.
- RBAC source tests updated and passing.
- No deferred commands added.
- No frontend changes.
- No migrations.
- No auto-commit.
