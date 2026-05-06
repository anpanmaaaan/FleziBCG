# MMD-BE-14B — Product Version Release BOM Binding Validation Policy Contract

## Audit Report

| Date | Version | Change |
|---|---:|---|
| 2026-05-06 | v1.0 | Audit report for MMD-BE-14B. Policy contract generated. No runtime source changed. |

---

## 1. Scope

**Slice:** MMD-BE-14B — Product Version Release BOM Binding Validation Policy Contract

**Objective:** Define the binding validation policy contract for Product Version release. Determine where the policy flag lives, what conditions must be met when it is set, and what authorizations and events apply.

**Output artifacts:**
- `docs/design/02_domain/product_definition/product-version-release-bom-binding-validation-policy-contract.md`
- `docs/audit/mmd-be-14b-product-version-release-bom-binding-validation-policy-contract.md` (this file)

**No runtime source changed in this slice.**

---

## 2. Baseline Evidence Used

| Baseline Source | Key Evidence |
|---|---|
| `docs/audit/mmd-be-14a-bom-product-version-binding-boundary-release-validation.md` | Decision to defer release validation to MMD-BE-14B; no policy config in runtime source; boundary clean |
| `docs/audit/mmd-bom-write-02-bom-product-version-binding-governance-contract.md` | `release_product_version_with_bom_validation` proposed; `admin.master_data.product_version.manage` only for release |
| `docs/design/02_domain/product_definition/product-version-write-governance-contract.md` | PV release: DRAFT → RELEASED; no binding requirement in current design |
| `docs/audit/mmd-bom-write-baseline-01-bom-write-freeze-handoff.md` | PV release baseline frozen; `release_product_version()` has no binding check |
| `backend/app/models/product_version.py` | No `bom_binding_required_for_release` field; lifecycle_status, is_current, effective_from/to present |
| `backend/app/models/product_version_bom_binding.py` | binding_type (PRIMARY only), binding_status (ACTIVE/REMOVED), bom_id, product_version_id, product_id, tenant_id |
| `backend/app/models/product.py` | No binding_required policy field; lifecycle_status only |
| `grep_search(binding_required)` | Zero occurrences in any runtime source file |

---

## 3. Source Inspection Summary

### 3.1 `bom_binding_required_for_release` Field Existence Audit

| Location | Field Present? | Evidence |
|---|---|---|
| `backend/app/models/product_version.py` | ❌ No | Inspected — not present |
| `backend/app/models/product.py` | ❌ No | Inspected — not present |
| `backend/app/models/product_version_bom_binding.py` | ❌ No | Inspected — not present |
| `backend/app/schemas/product_version.py` | ❌ No | Inspected — not present |
| `backend/app/services/product_version_service.py` | ❌ No | Inspected — no binding check in release_product_version() |
| `backend/app/services/product_version_bom_binding_service.py` | ❌ No | Inspected — no release validation logic |
| Any other runtime source file | ❌ No | grep_search confirmed zero occurrences of "binding_required" |

**Conclusion:** The field does not exist anywhere in runtime source. This contract is creating the governance specification for a future implementation.

### 3.2 Existing ProductVersion Release Behavior

`release_product_version()` in `product_version_service.py`:

- Checks `row.lifecycle_status != "DRAFT"` → raises ValueError
- Calls `record_security_event("PRODUCT_VERSION.RELEASED", ...)`
- Sets `row.lifecycle_status = "RELEASED"`
- **No BOM binding check of any kind exists**

### 3.3 BOM Binding Behavior (MMD-BE-14)

`bind_bom_to_product_version()` in `product_version_bom_binding_service.py`:

- Allowed bind states: `_ALLOWED_PV_BIND_STATUSES = {"DRAFT"}`
- Forbidden BOM states: `_FORBIDDEN_BOM_BIND_STATUSES = {"RETIRED"}`
- Binding cardinality: one ACTIVE PRIMARY per PV (enforced by service)
- Emits `ProductVersionBomBinding.CREATED`

The existing binding constraint means: a DRAFT PV can be bound to a DRAFT or RELEASED BOM. An ACTIVE PRIMARY binding exists when a valid bind has been established and not yet unbound.

---

## 4. Policy Decision

### Selected: Option B — ProductVersion-level `bom_binding_required_for_release`

| Option | Decision | Reason |
|---|---|---|
| **A. Global mandatory binding** | ❌ REJECT | Breaks existing RELEASED PVs; no rollback; no migration default strategy |
| **B. ProductVersion-level flag** | ✅ **SELECTED** | Minimal; backward safe; locally scoped; upgradeable to tenant/plant policy |
| **C. Product-level policy** | ⚠️ DEFER | Natural long-term but requires product governance update |
| **D. Tenant/plant/manufacturing profile** | ⚠️ DEFER | Best long-term MOM but requires manufacturing profile governance |
| **E. Defer implementation** | ❌ WEAK | No gate; binding advisory only |

**Primary rationale:** Option B delivers a concrete, testable, backward-compatible policy gate with minimal blast radius. It is the smallest delivery that enables the use case.

---

## 5. Policy Field Decision

### Selected Field Name: `bom_binding_required_for_release`

| Property | Value |
|---|---|
| Model | `ProductVersion` |
| Column name | `bom_binding_required_for_release` |
| SQLAlchemy type | `Boolean` |
| Nullable | NOT NULL |
| Default | `false` |
| Alembic server_default | `sa.false()` |
| Read schema | `ProductVersionItem` |
| Write schema | `ProductVersionCreateRequest` (optional, default false) and `ProductVersionUpdateRequest` (optional) |
| Authorization for write | `admin.master_data.product_version.manage` |

**Key invariant:** NOT NULL DEFAULT false guarantees no existing rows are invalidated.

---

## 6. Release Validation Decision

### Release Validation Matrix

| `bom_binding_required_for_release` | PV Status | Binding State | Bound BOM Status | Release Decision |
|---|---|---|---|---|
| `false` | DRAFT | Any or none | Any | ✅ ALLOW (unchanged behavior) |
| `true` | DRAFT | No ACTIVE PRIMARY | — | ❌ BLOCK → 422 |
| `true` | DRAFT | ACTIVE PRIMARY | RELEASED | ✅ ALLOW |
| `true` | DRAFT | ACTIVE PRIMARY | DRAFT | ❌ BLOCK → 422 |
| `true` | DRAFT | ACTIVE PRIMARY | RETIRED | ❌ BLOCK → 422 |
| `true` | DRAFT | REMOVED (no ACTIVE) | — | ❌ BLOCK → 422 |
| `false` or `true` | RELEASED | — | — | ❌ BLOCK → 422 (existing invariant) |
| `false` or `true` | RETIRED | — | — | ❌ BLOCK → 422 (existing invariant) |

### Key Ruling: Backward Compatibility

> Setting `bom_binding_required_for_release = false` (the default) must produce exactly identical behavior to Product Version release before this feature was implemented.

All existing Product Version release tests must pass without modification after MMD-BE-14C.

### Key Ruling: BOM and Binding are Read-Only

Validation must not mutate BOM lifecycle, binding status, or any other entity.

---

## 7. Authorization Decision

### Release Command

| Command | Required Action Code | Notes |
|---|---|---|
| `release_product_version` | `admin.master_data.product_version.manage` | Unchanged; binding validation is service-internal read |

Release validation does **not** require `admin.master_data.bom.manage`.

**Rationale:** The release command reads BOM binding and BOM lifecycle as part of internal validation. It does not mutate BOM. Requiring BOM manage would impose unnecessary permission escalation.

### Flag Toggle

| Command | Required Action Code | Notes |
|---|---|---|
| Set/update `bom_binding_required_for_release` | `admin.master_data.product_version.manage` | Covered by existing PV manage |

---

## 8. Migration / Compatibility Decision

### Migration Rule

```python
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

| Rule | Value |
|---|---|
| Default for existing rows | `false` |
| Nullable | No — NOT NULL |
| Server default | `false` |
| Backfill required | No |
| Existing RELEASED PVs invalidated | **No** |
| Migration sequence | After 0013 (product_version_bom_bindings); will be 0014 |

### Backward Compatibility Guarantee

All currently RELEASED and DRAFT Product Versions receive `bom_binding_required_for_release = false` after migration. No Product Version requires re-release.

---

## 9. Audit / Event Decision

### On Successful Release (binding_required=true)

| Event | Decision |
|---|---|
| `PRODUCT_VERSION.RELEASED` | ✅ MANDATORY — existing event |
| `ProductVersionBomBinding.VALIDATED_ON_RELEASE` | ⚠️ OPTIONAL — future enhancement |

### On Blocked Release

| Condition | Event |
|---|---|
| Binding validation fails | **No event emitted** — silent rejection via ValueError → 422 |
| Existing DRAFT-only rule fails | **No event emitted** (unchanged) |

### On Flag Toggle

| Condition | Event |
|---|---|
| `bom_binding_required_for_release` changed | `PRODUCT_VERSION.UPDATED` with `bom_binding_required_for_release` in changed_fields |

### Forbidden Events on Release

The following must never be emitted by `release_product_version()`:

MaterialReserved, MaterialConsumed, BackflushPosted, ERPPosted, GenealogyCreated, QualityAccepted, ExecutionStarted, OperationConfirmed, APSSelected, ProductionOrderCreated

---

## 10. Boundary Guardrails

| Boundary | Rule | Enforcement |
|---|---|---|
| Release validation is read-only | BOM and binding must not be mutated | Unit test: no binding CREATED/REMOVED events emitted |
| No material side effects | No material/inventory/ERP/traceability/quality/execution service calls | Service import audit |
| Backend is source of truth | Release eligibility must not be decided by frontend | FE contract in policy doc §12 |
| No OR permission semantics | Release requires only `pv.manage` | Route action code check |
| No forbidden routes | No `/release-binding`, `/validate-bom`, `/reserve-material` etc. | Route existence test |
| Binding cardinality unchanged | One ACTIVE PRIMARY binding per PV | Unchanged; MMD-BE-14 service invariant |

---

## 11. Future Test Requirements

The following 12 tests are **required** in MMD-BE-14C before implementation is considered complete:

| Test Name | Scenario | Expected Outcome |
|---|---|---|
| `test_release_pv_without_binding_required_flag_succeeds` | `bom_binding_required_for_release=false`, no binding | 200 — release unchanged |
| `test_release_pv_with_binding_required_and_released_bom_succeeds` | `bom_binding_required_for_release=true`, ACTIVE PRIMARY, BOM=RELEASED | 200 — release succeeds |
| `test_release_pv_with_binding_required_and_no_binding_returns_422` | `bom_binding_required_for_release=true`, no binding | 422 — blocked |
| `test_release_pv_with_binding_required_and_draft_bom_returns_422` | `bom_binding_required_for_release=true`, DRAFT BOM | 422 — blocked |
| `test_release_pv_with_binding_required_and_retired_bom_returns_422` | `bom_binding_required_for_release=true`, RETIRED BOM | 422 — blocked |
| `test_release_pv_with_binding_required_and_removed_binding_returns_422` | `bom_binding_required_for_release=true`, REMOVED binding | 422 — blocked |
| `test_release_blocked_by_binding_validation_emits_no_event` | `bom_binding_required_for_release=true`, no binding | SecurityEventLog empty |
| `test_release_with_valid_binding_emits_released_event` | Success path | `PRODUCT_VERSION.RELEASED` in SecurityEventLog |
| `test_update_pv_binding_required_flag_requires_pv_manage` | PATCH flag without pv.manage | 403 |
| `test_update_pv_binding_required_flag_succeeds_with_pv_manage` | PATCH flag with pv.manage | 200 + updated event |
| `test_create_pv_with_binding_required_true` | POST with `bom_binding_required_for_release=true` | 201, field stored correctly |
| `test_create_pv_default_binding_required_is_false` | POST without field | 201, field = false |

---

## 12. Recommended Next Slice

### MMD-BE-14C — Product Version Release BOM Binding Validation Implementation

**Deliverables:**

1. `ProductVersion.bom_binding_required_for_release` field
2. Alembic migration `0014_product_version_bom_binding_required.py`
3. `ProductVersionItem` schema: expose field
4. `ProductVersionCreateRequest`/`ProductVersionUpdateRequest`: accept field
5. `release_product_version()`: add binding validation when flag is true
6. `update_product_version()`: accept flag + include in changed_fields
7. 12 tests from §11
8. Alembic baseline test: updated HEAD
9. Regression pass: all existing PV + BOM tests pass

**Gate before MMD-FULLSTACK-14 BOM binding frontend integration.**

---

## 13. Verification / Diff

### Files Created in This Slice

| File | Type | Status |
|---|---|---|
| `docs/design/02_domain/product_definition/product-version-release-bom-binding-validation-policy-contract.md` | Documentation | ✅ Created |
| `docs/audit/mmd-be-14b-product-version-release-bom-binding-validation-policy-contract.md` | Audit Report | ✅ Created (this file) |

### Files Changed in This Slice

**None.** This is a documentation-only slice.

| Category | Changed? |
|---|---|
| Runtime source (`backend/app/`) | ❌ No |
| Tests (`backend/tests/`) | ❌ No |
| Alembic migrations | ❌ No |
| Frontend source (`frontend/src/`) | ❌ No |
| Docker / config | ❌ No |
| Stashed changes (`pre-mmd-be-14-unrelated-changes`) | ❌ Untouched |

### Source Integrity Checks

| Check | Result |
|---|---|
| `bom_binding_required_for_release` in runtime source (before) | ❌ Not found (confirmed by grep) |
| `bom_binding_required_for_release` in runtime source (after) | ❌ Still not found (documentation only) |
| Test baseline passed | N/A — no implementation in this slice |

---

## 14. Final Verdict

### Verdict: COMPLETE — Documentation Only

| Criterion | Status |
|---|---|
| Policy option selected | ✅ Option B (ProductVersion-level flag) |
| Field name defined | ✅ `bom_binding_required_for_release` |
| Field type / default defined | ✅ Boolean NOT NULL DEFAULT false |
| Backward compatibility guaranteed | ✅ Default false; no existing PVs invalidated |
| Release validation rules specified | ✅ Validation matrix complete (6 scenarios) |
| Authorization defined | ✅ `pv.manage` only; no `bom.manage` required |
| Event expectations defined | ✅ RELEASED event on success; no event on block |
| Migration contract specified | ✅ 0014 migration; server_default=false |
| Future tests required | ✅ 12 tests documented |
| Next slice defined | ✅ MMD-BE-14C |
| No runtime source changed | ✅ Confirmed |
| No migrations changed | ✅ Confirmed |
| No tests changed | ✅ Confirmed |
| Stash untouched | ✅ Confirmed |

**Slice MMD-BE-14B is CLOSED.**

**Recommended next action: Begin MMD-BE-14C.**
