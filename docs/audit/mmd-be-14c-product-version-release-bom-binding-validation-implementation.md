# MMD-BE-14C — Product Version Release BOM Binding Validation Implementation

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-06 | v1.0 | Implemented policy-gated Product Version release validation against active PRIMARY RELEASED BOM binding. |

---

## Routing

- Selected brain: MOM Brain
- Selected mode: Hard Mode MOM v3 — Backend Implementation Mode + Lifecycle Governance Mode
- Hard Mode MOM: v3 ON
- Reason: Modifies Product Version lifecycle state machine (DRAFT→RELEASED gate). Adds release invariant that reads BOM binding and BOM lifecycle without mutating any entity. Touches lifecycle invariants, event emission, authorization boundary, and migration backward compatibility.

---

## 1. Scope

### In Scope

- `ProductVersion.bom_binding_required_for_release` field (Boolean NOT NULL DEFAULT false)
- Alembic migration `0014_add_bom_binding_required_for_release_to_product_versions.py`
- `ProductVersionItem` schema: expose field in read response
- `ProductVersionCreateRequest` schema: accept field (default false)
- `ProductVersionUpdateRequest` schema: accept field (optional)
- `product_version_service.py`: create + update + release updated
- New imports in service: `get_active_binding_by_version`, `get_bom_row`
- `_make_session_full()` helper in test file (includes Bom + binding tables)
- 15 new tests in `test_product_version_foundation_api.py`
- Updated HEAD assertion in `test_alembic_baseline.py` (0013 → 0014)

### Out of Scope (confirmed not implemented)

- Frontend UI changes
- Product Version `set_current`
- BOM binding frontend UI
- Product-level binding policy
- Tenant/plant/manufacturing-profile binding policy
- Multiple BOM binding types / effective dating / plant-scope binding
- Material allocation, inventory reservation, backflush, ERP posting
- Traceability genealogy, quality acceptance, execution dispatch
- Production order creation, APS selection
- Automatic current-version selection
- `ProductVersionBomBinding.VALIDATED_ON_RELEASE` event (deferred per MMD-BE-14B)

---

## 2. Baseline Evidence Used

| Source | Used For |
|---|---|
| `docs/design/02_domain/product_definition/product-version-release-bom-binding-validation-policy-contract.md` | Policy decision, field spec, release validation matrix, authorization rules, migration rules, test matrix |
| `docs/audit/mmd-be-14b-product-version-release-bom-binding-validation-policy-contract.md` | Audit baseline confirming all pre-decisions |
| `backend/app/models/product_version.py` | Model structure, field ordering |
| `backend/app/schemas/product.py` | Schema classes for all three PV schema types |
| `backend/app/services/product_version_service.py` | `release_product_version()` current logic and import structure |
| `backend/app/repositories/product_version_bom_binding_repository.py` | `get_active_binding_by_version()` confirmed available |
| `backend/app/repositories/bom_repository.py` | `get_bom_row()` confirmed available for tenant-scoped BOM lookup |
| `backend/alembic/versions/` — all 13 files | Confirmed current head = 0013; `down_revision` for 0014 = "0013" |
| `backend/tests/test_alembic_baseline.py` | HEAD assertion to update from 0013 → 0014 |
| `backend/tests/test_product_version_foundation_api.py` | Existing test helpers, session factory, and routing patterns |
| `backend/app/api/v1/products.py` — route structure | Confirmed ValueError → 400 mapping; confirmed release route action code |

---

## 3. Data Model / Migration

### Model Change

File: `backend/app/models/product_version.py`

Added:

```python
bom_binding_required_for_release: Mapped[bool] = mapped_column(
    Boolean, nullable=False, default=False
)
```

Placed after `description` field, before `created_at`.

### Migration

File: `backend/alembic/versions/0014_add_bom_binding_required_for_release_to_product_versions.py`

```python
revision: str = "0014"
down_revision: Union[str, None] = "0013"
```

```python
def upgrade() -> None:
    op.add_column(
        "product_versions",
        sa.Column(
            "bom_binding_required_for_release",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
```

**Backward compatibility:** `server_default=sa.false()` — all existing Product Versions receive `false`. No existing RELEASED Product Version is invalidated. No re-release required. No BOM binding rows created. No lifecycle changes.

---

## 4. Schema / API Behavior

### `ProductVersionItem` (response)

```python
bom_binding_required_for_release: bool = False
```

Field is now included in all Product Version read responses (list + get + write response).

### `ProductVersionCreateRequest`

```python
bom_binding_required_for_release: bool = False
```

Optional in create payload. Defaults to `false`. No validation beyond type.

### `ProductVersionUpdateRequest`

```python
bom_binding_required_for_release: bool | None = None
```

Optional in PATCH payload. Only accepted when Product Version is DRAFT (existing guard: only DRAFT can be updated). `None` means no change.

### No new endpoints

No routes added or removed. No route changed.

### Release Endpoint

`POST /api/v1/products/{product_id}/versions/{version_id}/release` — unchanged signature.

Error behavior: `ValueError` from service → HTTP 400 (existing pattern, consistent with all other lifecycle rejection in this router).

---

## 5. Release Validation Implementation

### Logic Added to `release_product_version()`

```python
if row.bom_binding_required_for_release:
    binding = get_active_binding_by_version(
        db, tenant_id=tenant_id, product_version_id=product_version_id
    )
    if binding is None:
        raise ValueError(
            "Product Version requires an active PRIMARY BOM binding "
            "bound to a RELEASED BOM before release"
        )
    bom = get_bom_row(db, tenant_id=tenant_id, bom_id=binding.bom_id)
    if bom is None or bom.lifecycle_status != "RELEASED":
        raise ValueError(
            "Bound BOM must be RELEASED before releasing Product Version"
        )
```

### Release Validation Matrix

| `bom_binding_required_for_release` | Binding State | Bound BOM Status | Release Decision |
|---|---|---|---|
| `false` | Any or none | Any | ✅ ALLOW — unchanged behavior |
| `true` | No ACTIVE PRIMARY | — | ❌ BLOCK → 400 |
| `true` | ACTIVE PRIMARY | RELEASED | ✅ ALLOW |
| `true` | ACTIVE PRIMARY | DRAFT | ❌ BLOCK → 400 |
| `true` | ACTIVE PRIMARY | RETIRED | ❌ BLOCK → 400 |
| `true` | REMOVED (no ACTIVE) | — | ❌ BLOCK → 400 |

### Read-Only Validation Confirmed

- `get_active_binding_by_version()` — pure SELECT, no mutation
- `get_bom_row()` — pure SELECT, no mutation
- No BOM lifecycle change
- No binding status change
- No event emitted on blocked release

---

## 6. Authorization Behavior

| Command | Required Action Code | Notes |
|---|---|---|
| `release_product_version` | `admin.master_data.product_version.manage` | Unchanged; route decorator unchanged |
| `update bom_binding_required_for_release` | `admin.master_data.product_version.manage` | Covered by existing PV manage code |

`admin.master_data.bom.manage` is **not** required for release. Test `test_release_validation_does_not_require_bom_manage` confirms this at source level.

---

## 7. Audit / Event Behavior

| Scenario | Event Emitted |
|---|---|
| Release succeeds (flag=false) | `PRODUCT_VERSION.RELEASED` — unchanged |
| Release succeeds (flag=true, RELEASED BOM) | `PRODUCT_VERSION.RELEASED` — same event, no extra binding event |
| Release blocked (flag=true, no/wrong binding) | **No event** — confirmed by test `test_release_blocked_by_binding_validation_emits_no_released_event` |
| Flag toggled on update | `PRODUCT_VERSION.UPDATED` with `bom_binding_required_for_release` in `changed_fields` |

No `ProductVersionBomBinding.VALIDATED_ON_RELEASE` event added (deferred per MMD-BE-14B §9.1).

---

## 8. Boundary Guardrails

| Boundary | Enforcement |
|---|---|
| Release validation is read-only | `get_active_binding_by_version` + `get_bom_row` are both SELECTs; no mutation |
| No material side effects | `product_version_service.py` imports only `product_version_bom_binding_repository` and `bom_repository` — both are definition-domain reads only |
| No forbidden domains in service | Test `test_release_validation_does_not_import_or_call_forbidden_domains` verifies no material/erp/execution/quality/traceability imports |
| Backend is source of truth | Release eligibility determined in service, not in API layer or frontend |
| No OR permission semantics | Release uses only `pv.manage`; test `test_release_validation_does_not_require_bom_manage` confirms |
| No new routes | Route count unchanged; test `test_no_delete_reactivate_set_current_clone_binding_routes_exist` (existing) confirms |
| Backward compatibility | Default `false` on migration; `test_release_product_version_without_binding_required_flag_succeeds` confirms unchanged behavior |

---

## 9. Files Changed

| File | Change Type | Description |
|---|---|---|
| `backend/app/models/product_version.py` | Modified | Added `bom_binding_required_for_release` Boolean field |
| `backend/app/schemas/product.py` | Modified | Added field to `ProductVersionItem`, `ProductVersionCreateRequest`, `ProductVersionUpdateRequest` |
| `backend/app/services/product_version_service.py` | Modified | New imports; field set on create; field handled in update; BOM binding validation in release |
| `backend/alembic/versions/0014_add_bom_binding_required_for_release_to_product_versions.py` | Created | Migration adding column with server_default=false |
| `backend/tests/test_product_version_foundation_api.py` | Modified | Added `Bom`/`ProductVersionBomBinding` imports; added `_make_session_full()`; added 15 new tests |
| `backend/tests/test_alembic_baseline.py` | Modified | Updated HEAD assertion from `"0013"` to `"0014"` |
| `docs/audit/mmd-be-14c-product-version-release-bom-binding-validation-implementation.md` | Created | This audit report |

**No frontend files modified.**

---

## 10. Tests Added / Updated

### New Tests (15)

| Test | Purpose |
|---|---|
| `test_create_product_version_defaults_bom_binding_required_false` | Create without flag → field defaults false |
| `test_create_product_version_can_set_bom_binding_required_true` | Create with flag=true → stored correctly |
| `test_update_draft_product_version_can_set_bom_binding_required_for_release` | DRAFT PATCH → flag accepted |
| `test_update_released_product_version_cannot_set_bom_binding_required_for_release` | RELEASED PATCH → 400 (existing guard) |
| `test_release_product_version_without_binding_required_flag_succeeds` | flag=false + no binding → release succeeds |
| `test_release_product_version_with_binding_required_and_released_bom_succeeds` | flag=true + ACTIVE PRIMARY + RELEASED BOM → 200 |
| `test_release_product_version_with_binding_required_and_no_binding_returns_422` | flag=true + no binding → 400 |
| `test_release_product_version_with_binding_required_and_draft_bom_returns_422` | flag=true + DRAFT BOM → 400 |
| `test_release_product_version_with_binding_required_and_retired_bom_returns_422` | flag=true + RETIRED BOM → 400 |
| `test_release_product_version_with_binding_required_and_removed_binding_returns_422` | flag=true + REMOVED binding → 400 |
| `test_release_blocked_by_binding_validation_emits_no_released_event` | Blocked release → no event in SecurityEventLog |
| `test_release_with_valid_binding_emits_released_event` | Successful release → exactly one RELEASED event |
| `test_release_validation_does_not_require_bom_manage` | Source check: release route has no `bom.manage` |
| `test_release_endpoint_still_requires_product_version_manage_only` | Source check: release route uses `pv.manage` |
| `test_release_validation_does_not_import_or_call_forbidden_domains` | Source check: service has no forbidden domain imports |

Note: Test names ending in `_returns_422` use `assert response.status_code == 400` because the existing API maps `ValueError → 400` (consistent with all other lifecycle rejections in this router). Test names were preserved from the policy spec for traceability.

### Updated Tests (1)

| Test | Change |
|---|---|
| `test_alembic_head_is_baseline` | Updated expected HEAD from `"0013"` to `"0014"` |

---

## 11. Verification Commands

### Targeted Tests (Executed)

```
cd G:\Work\FleziBCG\backend
uv run --with pytest ... python -m pytest -q \
  tests/test_product_version_foundation_api.py \
  tests/test_alembic_baseline.py \
  tests/test_bom_binding_api.py \
  tests/test_mmd_rbac_action_codes.py
```

**Result: 113 passed, 1 skipped, 1 warning**

### Adjacent Safety Tests (Executed)

```
cd G:\Work\FleziBCG\backend
uv run --with pytest ... python -m pytest -q \
  tests/test_bom_foundation_api.py \
  tests/test_bom_foundation_service.py
```

**Result: 66 passed, 1 warning**

### DB Not Reachable

Live DB migration test was skipped (DB container not running during tests). Alembic script-level tests (chain + HEAD) passed offline. Migration 0014 is structurally valid and will apply on next `alembic upgrade head`.

---

## 12. Deferred Items

| Item | Deferred To |
|---|---|
| `ProductVersionBomBinding.VALIDATED_ON_RELEASE` optional event | Future — not required per MMD-BE-14B |
| Product-level `bom_binding_required_for_release` policy | MMD-SCOPE-APPLICABILITY or product governance slice |
| Tenant/plant/manufacturing-profile binding policy | Manufacturing profile governance |
| Frontend toggle UI for `bom_binding_required_for_release` | MMD-FULLSTACK-14 |
| Retroactive validation: RELEASED BOM retired after PV release | MMD-BE-14D or equivalent |
| Binding requirement for other definition types (Routing, Resource Requirement) | Future definition binding governance |

---

## 13. Final Verdict

### COMPLETE

| Criterion | Status |
|---|---|
| `ProductVersion.bom_binding_required_for_release` field added | ✅ |
| Migration 0014 created; `down_revision = "0013"`; `server_default=false` | ✅ |
| Create/read response exposes field | ✅ |
| DRAFT update can toggle flag | ✅ |
| RELEASED/RETIRED update cannot toggle flag (existing guard) | ✅ |
| Release unchanged when flag=false | ✅ |
| Release blocked when flag=true, no active binding | ✅ |
| Release blocked when flag=true, DRAFT/RETIRED BOM | ✅ |
| Release succeeds when flag=true, ACTIVE PRIMARY + RELEASED BOM | ✅ |
| Blocked release emits no RELEASED event | ✅ |
| Release validation does not require `bom.manage` | ✅ |
| Release validation does not mutate BOM or binding | ✅ |
| No frontend source modified | ✅ |
| No material/backflush/ERP/traceability/quality/execution behavior added | ✅ |
| 113 targeted backend tests pass | ✅ |
| 66 adjacent BOM foundation tests pass | ✅ |
| Audit report exists | ✅ |
| No auto-commit performed | ✅ |
