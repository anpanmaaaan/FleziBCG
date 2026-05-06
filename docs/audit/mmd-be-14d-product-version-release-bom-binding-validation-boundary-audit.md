# MMD-BE-14D — Product Version Release BOM Binding Validation Boundary Audit / Regression Lock

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-06 | v1.0 | Verified and locked Product Version release BOM binding validation boundaries after MMD-BE-14C. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Hard Mode MOM v3 — Lifecycle Governance Audit Mode
- **Hard Mode MOM:** v3 ON
- **Reason:** Verifies lifecycle gate invariants (PV release), authorization boundary, event behavior, and side-effect boundaries for a governed manufacturing definition lifecycle transition. All criteria for v3 apply.

---

## 1. Scope

This audit verifies and regression-locks the implementation from MMD-BE-14C:

- `ProductVersion.bom_binding_required_for_release` field existence, default, and migration correctness
- Unchanged PV release behavior when flag is `false`
- Release block when flag is `true` and no active PRIMARY binding exists
- Release block when flag is `true` and bound BOM is DRAFT or RETIRED
- Release success when flag is `true` and active PRIMARY binding points to RELEASED BOM
- Blocked release emits no `PRODUCT_VERSION.RELEASED` event
- Release validation does not require `admin.master_data.bom.manage`
- Release validation does not mutate BOM or binding
- Release validation does not call material / backflush / ERP / traceability / quality / execution / APS code
- No frontend source modified

**Out of scope:** Frontend binding UI, Product Version `set_current`, multiple binding types, effective dating, material allocation, backflush, ERP posting, traceability, quality acceptance, execution dispatch, production order, APS.

---

## 2. Baseline Evidence Used

| Document | Status |
|---|---|
| `docs/design/02_domain/product_definition/product-version-release-bom-binding-validation-policy-contract.md` | ✅ Present |
| `docs/audit/mmd-be-14b-product-version-release-bom-binding-validation-policy-contract.md` | ✅ Present |
| `docs/audit/mmd-be-14c-product-version-release-bom-binding-validation-implementation.md` | ✅ Present |
| `docs/design/02_domain/product_definition/bom-product-version-binding-governance-contract.md` | ✅ Present |
| `docs/audit/mmd-be-14-bom-product-version-binding-api-foundation.md` | ✅ Present |
| `docs/audit/mmd-be-14a-bom-product-version-binding-boundary-release-validation.md` | ✅ Present |

---

## 3. Source Inspection Summary

| File | Verdict |
|---|---|
| `backend/app/models/product_version.py` | ✅ `bom_binding_required_for_release: Mapped[bool]`, `nullable=False`, `default=False` |
| `backend/app/schemas/product.py` | ✅ Field in `ProductVersionItem`, `CreateRequest` (default False), `UpdateRequest` (optional None) |
| `backend/app/services/product_version_service.py` | ✅ Release validation correct; no forbidden imports |
| `backend/app/repositories/product_version_bom_binding_repository.py` | ✅ `get_active_binding_by_version()` is read-only |
| `backend/app/repositories/bom_repository.py` | ✅ `get_bom_row()` is read-only, tenant-scoped |
| `backend/app/api/v1/products.py` | ✅ Release route uses only `admin.master_data.product_version.manage`; `ValueError → 400` |
| `backend/alembic/versions/0014_add_bom_binding_required_for_release_to_product_versions.py` | ✅ `revision="0014"`, `down_revision="0013"`, `server_default=sa.false()`, `nullable=False` |

**Defect found and fixed:** `test_alembic_upgrade_head_live` asserted `"0010"` in `alembic_version` rows after `upgrade head`; the correct head is `"0014"`. Stale assertion from an earlier migration round. Fixed to assert `"0014"`.

---

## 4. Data Model / Migration Findings

| Check | Result |
|---|---|
| `ProductVersion.bom_binding_required_for_release` exists | ✅ Confirmed at `product_version.py` lines 61–63 |
| Field type | ✅ `Boolean`, `nullable=False`, `default=False` |
| Migration adds column with `server_default=sa.false()` | ✅ Confirmed in 0014 migration |
| Migration `down_revision = "0013"` | ✅ Chain intact |
| Migration does NOT create binding rows | ✅ Only `add_column` in upgrade |
| Migration does NOT change `lifecycle_status` | ✅ No such operation |
| Migration does NOT change `is_current` | ✅ No such operation |
| Migration does NOT change BOM lifecycle | ✅ No such operation |
| Alembic head test points to `"0014"` | ✅ After defect fix |
| Existing Product Versions unaffected (default false) | ✅ `server_default=sa.false()` preserves all existing PVs |

---

## 5. Schema / API Findings

| Check | Result |
|---|---|
| `ProductVersionItem.bom_binding_required_for_release` exposed | ✅ `bool = False` |
| `ProductVersionCreateRequest` defaults field to `false` | ✅ `bool = False` |
| `ProductVersionUpdateRequest` allows optional PATCH | ✅ `bool \| None = None` |
| DRAFT PV can set field via PATCH | ✅ Covered by service guard (DRAFT only can update) |
| RELEASED PV PATCH rejected | ✅ Existing lifecycle guard — `Only DRAFT product versions can be updated` |
| RETIRED PV PATCH rejected | ✅ Same guard |
| PATCH cannot change `lifecycle_status` | ✅ Field not in `UpdateRequest` (`extra="forbid"`) |
| PATCH cannot change `tenant_id` / `product_id` | ✅ Not in `UpdateRequest` |

---

## 6. Release Validation Findings

| Scenario | Expected | Verified |
|---|---|---|
| `flag=false`, no binding | ALLOW release | ✅ |
| `flag=false`, any binding state | ALLOW release | ✅ (no check performed) |
| `flag=true`, no ACTIVE PRIMARY binding | BLOCK → 400 | ✅ |
| `flag=true`, REMOVED binding only | BLOCK → 400 | ✅ |
| `flag=true`, ACTIVE PRIMARY → DRAFT BOM | BLOCK → 400 | ✅ |
| `flag=true`, ACTIVE PRIMARY → RETIRED BOM | BLOCK → 400 | ✅ |
| `flag=true`, ACTIVE PRIMARY → RELEASED BOM | ALLOW → 200 | ✅ |

Validation is read-only: `get_active_binding_by_version()` + `get_bom_row()` — neither mutates.

---

## 7. Authorization Findings

| Check | Result |
|---|---|
| PV release requires only `admin.master_data.product_version.manage` | ✅ Confirmed at `products.py:255–263` |
| PV release does NOT require `admin.master_data.bom.manage` | ✅ Confirmed by source inspection and locked by test |
| Binding mutation (POST/DELETE bom-binding) requires both `bom.manage` AND `pv.manage` | ✅ Confirmed by `test_mmd_rbac_action_codes.py` |
| Read endpoints do not require `manage` | ✅ Existing tests |

---

## 8. Event / Audit Findings

| Check | Result |
|---|---|
| Successful release emits `PRODUCT_VERSION.RELEASED` | ✅ Locked by `test_release_with_valid_binding_emits_released_event` |
| Blocked release emits NO `PRODUCT_VERSION.RELEASED` | ✅ Locked by `test_release_blocked_by_binding_validation_emits_no_released_event` |
| No `ProductVersionBomBinding` mutation event emitted | ✅ Binding not mutated; no binding event wired in release path |
| No `ProductVersionBomBinding.VALIDATED_ON_RELEASE` event | ✅ Deferred per policy contract; not present in source |

---

## 9. Side-Effect Boundary Findings

Inspected `backend/app/services/product_version_service.py` imports:

| Import | Category | Used in release validation? |
|---|---|---|
| `product_version_bom_binding_repository.get_active_binding_by_version` | Binding read | ✅ Yes — read-only |
| `bom_repository.get_bom_row` | BOM read | ✅ Yes — read-only |
| `product_version_repository.*` | PV read/write | ✅ PV lifecycle update only |
| `security_event_service.record_security_event` | Audit event | ✅ Only on success path |
| `product_repository.get_product_by_id` | Product read | ✅ Parent validation |

**Forbidden domain imports — NONE found:**

| Pattern | Present? |
|---|---|
| `material` | ❌ Not present |
| `inventory` | ❌ Not present |
| `backflush` | ❌ Not present |
| `erp` | ❌ Not present |
| `traceability` | ❌ Not present |
| `genealogy` | ❌ Not present |
| `quality` | ❌ Not present |
| `execution` | ❌ Not present |
| `dispatch` | ❌ Not present |
| `aps` | ❌ Not present |
| `production_order` | ❌ Not present |

Locked by `test_release_validation_does_not_import_or_call_forbidden_domains`.

**No frontend source modified.**

---

## 10. Tests Added / Updated

### `backend/tests/test_alembic_baseline.py`

| Change | Type |
|---|---|
| Fixed `test_alembic_upgrade_head_live` assertion from `"0010"` → `"0014"` | Defect fix |
| Added `test_bom_binding_required_for_release_migration_default_false` | New guardrail test |

### `backend/tests/test_product_version_foundation_api.py`

| Test | Type |
|---|---|
| Added `test_update_retired_product_version_cannot_set_bom_binding_required_for_release` | New guardrail test |
| Added `test_release_validation_does_not_mutate_bom_or_binding` | New guardrail test |

### Pre-existing tests from MMD-BE-14C (retained, not modified):

| Test | Covers |
|---|---|
| `test_create_product_version_defaults_bom_binding_required_false` | Create default |
| `test_create_product_version_can_set_bom_binding_required_true` | Create set true |
| `test_update_draft_product_version_can_set_bom_binding_required_for_release` | DRAFT update |
| `test_update_released_product_version_cannot_set_bom_binding_required_for_release` | RELEASED update blocked |
| `test_release_product_version_without_binding_required_flag_succeeds` | flag=false path |
| `test_release_product_version_with_binding_required_and_released_bom_succeeds` | Happy path |
| `test_release_product_version_with_binding_required_and_no_binding_returns_422` | No binding → 400 |
| `test_release_product_version_with_binding_required_and_draft_bom_returns_422` | DRAFT BOM → 400 |
| `test_release_product_version_with_binding_required_and_retired_bom_returns_422` | RETIRED BOM → 400 |
| `test_release_product_version_with_binding_required_and_removed_binding_returns_422` | REMOVED binding → 400 |
| `test_release_blocked_by_binding_validation_emits_no_released_event` | No event on block |
| `test_release_with_valid_binding_emits_released_event` | Event on success |
| `test_release_validation_does_not_require_bom_manage` | Auth boundary (source) |
| `test_release_endpoint_still_requires_product_version_manage_only` | Auth boundary (source) |
| `test_release_validation_does_not_import_or_call_forbidden_domains` | Side-effect boundary |

---

## 11. Verification Commands

```text
# Targeted suite
cd backend
uv run --with pytest ... python -m pytest -q \
  tests/test_product_version_foundation_api.py \
  tests/test_alembic_baseline.py \
  tests/test_bom_binding_api.py \
  tests/test_mmd_rbac_action_codes.py

Result: 116 passed, 1 skipped

# Adjacent safety suite
uv run --with pytest ... python -m pytest -q \
  tests/test_bom_foundation_api.py \
  tests/test_bom_foundation_service.py \
  tests/test_reason_code_foundation_service.py

Result: 94 passed
```

---

## 12. Remaining Risks / Deferred Items

| Item | Severity | Status |
|---|---|---|
| `ProductVersionBomBinding.VALIDATED_ON_RELEASE` event not emitted | Low | Deferred per policy contract (MMD-BE-14B). Noted in audit. |
| Product-level or tenant-level binding policy | Medium | Deferred to future manufacturing profile governance slice. |
| Scope/plant-specific binding | Medium | Deferred to MMD-SCOPE-APPLICABILITY-01. |
| BOM retired after PV release (retroactive validity) | Low | No retroactive check currently. Deferred to MMD-BE-14E if needed. |
| Live DB `test_alembic_upgrade_head_live` skipped unless Docker DB reachable | Informational | Expected; skip is by design. |
| Frontend binding UI | None | Out of scope for all BE-14x slices. |

---

## 13. Final Verdict

**PASS. All MMD-BE-14D Definition of Done criteria are met.**

| Criterion | Status |
|---|---|
| Boundary report exists | ✅ This document |
| Migration/default behavior verified | ✅ Source + new migration structure test |
| Schema/API field behavior verified | ✅ Source + existing and new tests |
| Release validation matrix locked by tests | ✅ All 7 matrix rows covered |
| Authorization boundary locked by tests | ✅ Two source-level tests + route inspection |
| Event behavior locked by tests | ✅ No-event-on-block + event-on-success |
| Side-effect/import boundary locked by tests | ✅ Forbidden domain import test |
| No frontend source modified | ✅ Confirmed |
| No migration modified (only stale test fixed) | ✅ No migration file changed |
| Tests pass | ✅ 116 passed, 1 skipped (live DB) |
| No auto-commit performed | ✅ |

---

## Recommended Next Slice

**MMD-FULLSTACK-14 — BOM Product Version Binding Frontend Integration**

Backend binding API (`/bom-binding` CRUD), release validation policy, authorization boundary locks, and regression coverage are all complete. The frontend can now safely expose:

- Binding state display on Product Version detail
- Bind/Remove BOM action in Product Version UI
- `bom_binding_required_for_release` toggle on DRAFT PV
- Release readiness feedback when flag is `true` and binding is absent or BOM is not RELEASED

Prerequisite: Backend boundaries locked. ✅
