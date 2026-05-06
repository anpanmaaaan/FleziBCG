# Product Version Release BOM Binding Validation Policy Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-06 | v1.0 | Defined policy-gated Product Version release validation against BOM binding. |

---

## Routing

- Selected brain: MOM Brain
- Selected mode: Architecture Mode + Lifecycle Governance Mode + Product Mode (policy decision)
- Hard Mode MOM: v3 ON
- Reason: This contract decides whether Product Version release is blocked by BOM binding state. It touches lifecycle invariants, manufacturing definition readiness, authorization boundary for release, event semantics, backward compatibility, and future implementation scope. Hard Mode MOM v3 is mandatory for any slice defining lifecycle gate behavior affecting manufacturing definition applicability and future execution traceability.

---

## 1. Scope

### In Scope

- Define the policy contract for whether Product Version release should require an active PRIMARY BOM binding to a RELEASED BOM.
- Decide where the policy flag lives (entity, granularity, field name).
- Define release validation rules when the policy is active.
- Define lifecycle compatibility matrix for existing RELEASED Product Versions.
- Define authorization requirements for the flag and for validated release.
- Define audit/event expectations.
- Define backward compatibility and migration rules.
- Define boundary guardrails.
- Define the required test matrix for the implementation slice.
- Recommend the next implementation slice.

### Out of Scope

This is a **documentation-only governance contract**.

- No backend runtime source changes.
- No frontend source changes.
- No database migrations.
- No tests.
- No `bom_binding_required_for_release` field added to models.
- No Product Version release behavior changed.
- No BOM binding API behavior changed.
- No Product Version `set_current`.
- No BOM Product Version binding frontend UI.
- No material allocation, consumption, reservation, backflush, ERP posting.
- No traceability genealogy, quality acceptance, execution dispatch.
- No production order creation, APS selection, automatic current-version selection.

---

## 2. Current Baseline

### 2.1 Product Version Release (Current State)

| Aspect | Current Behavior |
|---|---|
| Release endpoint | `POST /api/v1/products/{product_id}/versions/{version_id}/release` |
| Required action code | `admin.master_data.product_version.manage` |
| Source guard | `release_product_version()` in `product_version_service.py` |
| Lifecycle check | Source state must be DRAFT |
| BOM binding check | **None** — release succeeds without binding |
| is_current behavior | `is_current` not mutated by release |
| Event emitted | `PRODUCT_VERSION.RELEASED` to SecurityEventLog |

### 2.2 BOM Binding (Current State)

| Aspect | Current Behavior |
|---|---|
| Binding API | GET/POST/DELETE `/{product_id}/versions/{version_id}/bom-binding` |
| Required action codes | `admin.master_data.bom.manage` AND `admin.master_data.product_version.manage` (AND-gated) |
| Binding cardinality | One ACTIVE PRIMARY binding per Product Version |
| Allowed bind states | DRAFT PV + RELEASED or DRAFT BOM |
| Forbidden bind | RETIRED BOM; non-DRAFT PV |
| Unbind | Only allowed on DRAFT PV |
| `bom_binding_required_for_release` | **Field does not exist** |

### 2.3 Product Version Model (Current State)

No `bom_binding_required_for_release` field exists on `ProductVersion` model or any other entity.

---

## 3. Business Purpose

A Product Version represents a versioned snapshot of manufacturing definition context for a product. Before a Product Version can be used to direct manufacturing execution, it should reference a valid, complete BOM structure.

The purpose of BOM binding validation at release is to ensure that:

1. A Product Version that transitions to RELEASED carries a reference to a structurally complete, released BOM.
2. Manufacturing execution, planning, and traceability consumers can trust that a RELEASED Product Version has an approved material structure.
3. Validation is not imposed globally — it is policy-gated so existing workflows are not broken.

This contract does not govern:

- Whether a RELEASED BOM is complete by item count.
- Whether BOM items reference valid current components.
- BOM explosion or material planning readiness.
- Execution assignment or dispatch eligibility.

---

## 4. Policy Decision

### Selected Policy: Option B — Product Version-level `bom_binding_required_for_release`

| Option | Decision | Reason |
|---|---|---|
| **A. Global mandatory binding** | ❌ REJECT | Breaks existing RELEASED Product Versions; no migration/default strategy; no manufacturing profile policy defined |
| **B. ProductVersion-level `bom_binding_required_for_release`** | ✅ **SELECTED** | Minimal; locally scoped; NOT NULL DEFAULT false does not break existing PVs; can be superseded by product/plant/manufacturing profile policy |
| **C. Product-level policy** | ⚠️ DEFER | Natural long-term; less flexible for version-specific exceptions; requires product write governance update |
| **D. Tenant/plant/manufacturing profile** | ⚠️ DEFER | Best long-term MOM architecture; requires manufacturing profile governance; too broad for immediate MMD-BE slice |
| **E. Defer implementation** | ❌ WEAK | Binding remains advisory; release readiness is never enforced |

### Rationale for Selection

- **Minimal safe policy gate.** Adding a per-Product Version boolean is the smallest implementation that enables opt-in release validation without imposing global behavior.
- **Backward compatible.** Existing RELEASED Product Versions remain valid. The migration default is `false`.
- **Upgradeable.** If a future tenant/plant/manufacturing-profile policy is introduced (Option D), it can override the per-PV default via a policy resolution layer. The field can serve as an explicit local override.
- **Aligned with existing MMD patterns.** Per-entity boolean flags for controlled capability are used elsewhere in the platform (e.g., `is_current` on ProductVersion, `lifecycle_status` on all MMD entities).

---

## 5. Policy Field Decision

### Canonical Field Name

```
bom_binding_required_for_release
```

### Rationale

`bom_binding_required_for_release` is preferred over alternatives:

| Candidate | Verdict | Reason |
|---|---|---|
| `binding_required` | ❌ AVOID | Ambiguous — could refer to routing, quality plan, recipe, or scope applicability bindings |
| `bom_required` | ❌ AVOID | Does not specify which BOM assertion is required |
| `require_bom_on_release` | ❌ AVOID | Non-standard naming pattern for this codebase |
| `bom_binding_required_for_release` | ✅ **SELECTED** | Explicit; scoped to BOM binding; scoped to release action; follows codebase conventions |

### Field Specification

| Property | Value |
|---|---|
| Model | `ProductVersion` |
| Column name | `bom_binding_required_for_release` |
| SQLAlchemy type | `Boolean` |
| Nullable | NOT NULL |
| Default | `false` |
| Alembic migration default | `server_default=false()` |
| Read visibility | Included in `ProductVersionItem` schema response |
| Write visibility | Settable on create (optional, default false) and update (optional) |
| Authorization for write | `admin.master_data.product_version.manage` |
| Audit on change | Change included in `PRODUCT_VERSION.UPDATED` event `changed_fields` |

### Schema Impact

The following future schema changes will be needed in the implementation slice:

`ProductVersionCreateRequest`:
```python
bom_binding_required_for_release: bool = False
```

`ProductVersionUpdateRequest`:
```python
bom_binding_required_for_release: bool | None = None
```

`ProductVersionItem` (response):
```python
bom_binding_required_for_release: bool
```

---

## 6. Release Validation Rules

The following rules apply **only when `bom_binding_required_for_release = true`**.

When `bom_binding_required_for_release = false`, existing release logic is unchanged.

### 6.1 Required Conditions for Release to Succeed

All of the following must be true:

1. Product Version is DRAFT (existing invariant).
2. Active PRIMARY `ProductVersionBomBinding` exists for this `(tenant_id, product_version_id)`.
3. Bound BOM belongs to the same tenant.
4. Bound BOM belongs to the same product.
5. Bound BOM `lifecycle_status = RELEASED`.
6. Binding `binding_status = ACTIVE`.
7. Binding `binding_type = PRIMARY`.

### 6.2 Release Rejection Cases

Release is blocked when `bom_binding_required_for_release = true` and any of:

| Condition | Error | HTTP Status |
|---|---|---|
| No active PRIMARY binding exists | "Product Version requires an active PRIMARY BOM binding bound to a RELEASED BOM before release" | 422 |
| Binding exists but bound BOM is DRAFT | "Bound BOM must be RELEASED before releasing Product Version" | 422 |
| Binding exists but bound BOM is RETIRED | "Bound BOM must be RELEASED before releasing Product Version" | 422 |
| Binding references wrong product | Prevented by binding creation invariant | (unreachable) |
| Binding references wrong tenant | Prevented by binding creation invariant | (unreachable) |
| Binding is REMOVED (no ACTIVE binding) | Same as "no active PRIMARY binding" | 422 |

### 6.3 Non-Blocking Cases

The following do not block release even when `bom_binding_required_for_release = true`:

| Condition | Behavior |
|---|---|
| PV has no binding (flag = false) | Release proceeds unchanged |
| PV has a binding but flag = false | Release proceeds; binding is informational |
| PV has ACTIVE PRIMARY binding to RELEASED BOM (flag = true) | Release succeeds |

### 6.4 Effect on Other Entities

Validation is **read-only**:

- BOM lifecycle is **NOT changed** by release validation.
- Binding status is **NOT changed** by release validation.
- No BOM event is emitted.
- No binding event is emitted.

---

## 7. Lifecycle Compatibility

### 7.1 Compatibility Matrix

| PV `bom_binding_required_for_release` | PV Status | Binding State | Bound BOM Status | Release Decision |
|---|---|---|---|---|
| `false` | DRAFT | Any or none | Any | ✅ ALLOW (unchanged behavior) |
| `true` | DRAFT | No ACTIVE PRIMARY | — | ❌ BLOCK → 422 |
| `true` | DRAFT | ACTIVE PRIMARY | RELEASED | ✅ ALLOW |
| `true` | DRAFT | ACTIVE PRIMARY | DRAFT | ❌ BLOCK → 422 |
| `true` | DRAFT | ACTIVE PRIMARY | RETIRED | ❌ BLOCK → 422 |
| `true` | DRAFT | REMOVED (no ACTIVE) | — | ❌ BLOCK → 422 |
| `false` or `true` | RELEASED | — | — | ❌ BLOCK → 422 (existing invariant) |
| `false` or `true` | RETIRED | — | — | ❌ BLOCK → 422 (existing invariant) |

### 7.2 Existing Released Product Versions

All currently RELEASED Product Versions have no `bom_binding_required_for_release` field.

After migration:

- All existing RELEASED Product Versions receive `bom_binding_required_for_release = false`.
- **No re-release is required.**
- **No backfill of BOM binding is required.**
- No invalidation of any existing RELEASED Product Version.

### 7.3 Interaction with `is_current`

- `is_current` is not affected by this validation.
- A Product Version with `is_current = true` cannot be retired (existing invariant); this is unchanged.
- BOM binding validation does not interact with `is_current`.

### 7.4 Interaction with BOM Lifecycle

When a Product Version has been released with an active PRIMARY binding to a RELEASED BOM, the bound BOM should generally not be retired while the Product Version is RELEASED. However:

- This constraint is **not enforced in this slice**.
- Deferred governance: if a RELEASED BOM is retired after a Product Version has been released with it as PRIMARY, the Product Version remains RELEASED. The binding row records historical state.
- Future slice `MMD-BE-14D` (or equivalent) may add a "retire BOM blocked if referenced by RELEASED PV with bom_binding_required_for_release = true" rule.

---

## 8. Authorization Requirements

### 8.1 Release Command

| Command | Required Action Code | Notes |
|---|---|---|
| `release_product_version` | `admin.master_data.product_version.manage` | Unchanged; binding validation is service-internal read |

Release validation **does not require `admin.master_data.bom.manage`**.

Reason: The release command reads BOM binding and BOM lifecycle as part of internal validation. It does not mutate BOM. Requiring BOM manage would impose unnecessary permission escalation on a Product Version release operation.

### 8.2 Flag Toggle

| Command | Required Action Code | Notes |
|---|---|---|
| Set/update `bom_binding_required_for_release` on PV | `admin.master_data.product_version.manage` | Covered by the existing PV manage code; no new code required |

The flag is mutable via the existing `PATCH /products/{product_id}/versions/{version_id}` endpoint (once exposed in the ProductVersionUpdateRequest schema).

### 8.3 Frontend Authorization

If a future frontend UI exposes the `bom_binding_required_for_release` toggle:

- The value must be derived from the server-side `ProductVersionItem.bom_binding_required_for_release`.
- The toggle must be gated on `ProductVersionAllowedActions.can_update`.
- Frontend must not derive eligibility from local lifecycle state.
- Backend is the only source of truth for authorization and flag state.

---

## 9. Audit / Event Expectations

### 9.1 On Successful Release (binding_required=true)

| Event | Emitted | Destination |
|---|---|---|
| `PRODUCT_VERSION.RELEASED` | ✅ YES | SecurityEventLog |
| `ProductVersionBomBinding.VALIDATED_ON_RELEASE` | ⚠️ OPTIONAL | SecurityEventLog |

The validation success event `ProductVersionBomBinding.VALIDATED_ON_RELEASE` is **optional for first implementation**. Only `PRODUCT_VERSION.RELEASED` is mandatory.

If emitted in a future slice, the validation event must include:

```json
{
  "product_version_id": "...",
  "bom_id": "...",
  "binding_id": "...",
  "occurred_at": "..."
}
```

### 9.2 On Blocked Release (binding_required=true, validation fails)

| Condition | Event | Behavior |
|---|---|---|
| Binding validation fails | **No event emitted** | ValueError → HTTP 422 |
| Existing DRAFT-only rule fails | **No event emitted** | ValueError → HTTP 422 (unchanged) |

### 9.3 On Flag Toggle

| Condition | Event | Behavior |
|---|---|---|
| `bom_binding_required_for_release` changed | `PRODUCT_VERSION.UPDATED` (changed_fields includes `"bom_binding_required_for_release"`) | Standard PV update event |

### 9.4 Forbidden Events

The following events must never be emitted from release validation:

- `MaterialReserved`
- `MaterialConsumed`
- `BackflushPosted`
- `ERPPosted`
- `GenealogyCreated`
- `QualityAccepted`
- `ExecutionStarted`
- `OperationConfirmed`
- `APSSelected`
- `ProductionOrderCreated`

---

## 10. Migration / Backward Compatibility

### 10.1 Required Future Migration

One Alembic migration will be required in MMD-BE-14C:

```python
# Candidate migration pseudocode
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

### 10.2 Migration Rules

| Rule | Value |
|---|---|
| Default for existing rows | `false` |
| Nullable | No — NOT NULL |
| Server default | `false` |
| Backfill required | No |
| Existing RELEASED PVs invalidated | No |
| Existing DRAFT PVs behavior changed | No (default false → release unchanged) |
| Migration sequence | After 0013 (product_version_bom_bindings); will be 0014 or next sequential |

### 10.3 Backward Compatibility Guarantee

> Setting `bom_binding_required_for_release = false` (the default) must produce exactly identical behavior to Product Version release before this feature was implemented.

No existing Product Version release test may fail due to this migration.

---

## 11. API / Schema Expectations

### 11.1 ProductVersionItem Response (future)

```python
class ProductVersionItem(BaseModel):
    # ... existing fields ...
    bom_binding_required_for_release: bool  # NEW
```

### 11.2 ProductVersionCreateRequest (future)

```python
class ProductVersionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # ... existing fields ...
    bom_binding_required_for_release: bool = False  # NEW — optional, default false
```

### 11.3 ProductVersionUpdateRequest (future)

```python
class ProductVersionUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # ... existing fields ...
    bom_binding_required_for_release: bool | None = None  # NEW — optional
```

### 11.4 Release Endpoint Changes

The `POST /products/{product_id}/versions/{version_id}/release` endpoint signature does not change.

The service `release_product_version()` acquires a new internal path:

```python
if row.bom_binding_required_for_release:
    # Validate active PRIMARY binding to RELEASED BOM
    binding = get_active_binding_by_version(db, ...)
    if binding is None:
        raise ValueError("...")
    bom = get_bom_by_id(db, ...)
    if bom.lifecycle_status != "RELEASED":
        raise ValueError("...")
```

No new route is added. No existing route is removed.

---

## 12. Frontend Expectations

### 12.1 Consumption

Frontend shall:

- Read `bom_binding_required_for_release` from `ProductVersionItem` in the product API response.
- Display the flag value as informational in the Product Version detail view.
- Gate the toggle control on `ProductVersionAllowedActions.can_update`.
- Send the flag value in `ProductVersionCreateRequest` or `ProductVersionUpdateRequest` if the user changes it.

Frontend shall not:

- Infer release eligibility from BOM binding state alone.
- Block release attempts locally based on binding state.
- Derive authorization from frontend state.

### 12.2 Capability Guard

A future `can_release` calculation in `_compute_allowed_actions()` **may optionally** include a hint when `bom_binding_required_for_release = true` and no RELEASED BOM binding exists. However, this is advisory only — the backend remains the source of truth. The hint must be derived from the server, not local FE inference.

---

## 13. Boundary Guardrails

### 13.1 Hard Boundary Locks

| Boundary | Rule |
|---|---|
| Release validation is read-only | BOM lifecycle must not be changed; binding must not be mutated |
| No material side effects | Validation must not call material, inventory, ERP, traceability, quality, or execution services |
| Backend is source of truth | Release eligibility must not be decided by frontend |
| No OR permission semantics | Release requires only `pv.manage`; BOM manage is not required |
| No forbidden routes | No `/release-binding`, `/validate-bom`, `/reserve-material`, etc. |
| Binding cardinality unchanged | One ACTIVE PRIMARY binding per PV; this contract does not change that |

### 13.2 Forbidden Implementation Patterns

The following patterns are forbidden in the MMD-BE-14C implementation:

- Calling `bom_service.release_bom()` from `release_product_version()`.
- Calling `product_version_bom_binding_service.bind_bom_to_product_version()` from `release_product_version()`.
- Emitting material, execution, ERP, or traceability events on release.
- Inferring binding readiness from version code or naming conventions.
- Creating a new route for release-with-binding.
- Requiring BOM manage permission at the release route layer.

---

## 14. Explicit Non-Goals

The following are explicitly **not governed by this contract** and must not be implemented in MMD-BE-14C:

- Routing binding requirement for release
- Quality plan binding requirement for release
- Recipe binding requirement for release
- Scope applicability requirement for release
- Effective-dating of BOM binding for release
- Plant/scope-specific BOM binding requirement
- Multiple BOM binding types for release
- Atomic BOM binding replacement on RELEASED PV
- Material structure completeness check (component count/availability)
- BOM item validation at release
- Circular component reference validation at release
- Production Order creation on release
- APS dispatch on release
- ERP posting on release
- Digital Twin initialization on release
- Product Version `set_current` automation
- Product Version archive or supersede
- Quality gate on release

---

## 15. Required Tests for Future Implementation

### 15.1 Core Validation Tests (to be added in MMD-BE-14C)

| Test Name | Scenario | Expected Outcome |
|---|---|---|
| `test_release_pv_without_binding_required_flag_succeeds` | `bom_binding_required_for_release=false`, no binding | 200 — release unchanged |
| `test_release_pv_with_binding_required_and_released_bom_succeeds` | `bom_binding_required_for_release=true`, ACTIVE PRIMARY binding, BOM=RELEASED | 200 — release succeeds |
| `test_release_pv_with_binding_required_and_no_binding_returns_422` | `bom_binding_required_for_release=true`, no binding | 422 — blocked |
| `test_release_pv_with_binding_required_and_draft_bom_returns_422` | `bom_binding_required_for_release=true`, binding to DRAFT BOM | 422 — blocked |
| `test_release_pv_with_binding_required_and_retired_bom_returns_422` | `bom_binding_required_for_release=true`, binding to RETIRED BOM | 422 — blocked |
| `test_release_pv_with_binding_required_and_removed_binding_returns_422` | `bom_binding_required_for_release=true`, binding exists but REMOVED | 422 — blocked |
| `test_release_blocked_by_binding_validation_emits_no_event` | `bom_binding_required_for_release=true`, no binding | SecurityEventLog empty |
| `test_release_with_valid_binding_emits_released_event` | Success path | `PRODUCT_VERSION.RELEASED` in SecurityEventLog |

### 15.2 Flag Mutation Tests

| Test Name | Scenario | Expected Outcome |
|---|---|---|
| `test_update_pv_binding_required_flag_requires_pv_manage` | PATCH flag without pv.manage | 403 |
| `test_update_pv_binding_required_flag_succeeds_with_pv_manage` | PATCH flag with pv.manage | 200 + `PRODUCT_VERSION.UPDATED` event with `bom_binding_required_for_release` in changed_fields |
| `test_create_pv_with_binding_required_true` | POST with `bom_binding_required_for_release=true` | 201, field stored correctly |
| `test_create_pv_default_binding_required_is_false` | POST without field | 201, field = false |

### 15.3 Regression Tests

All 96 existing PV and BOM foundation tests must continue to pass without modification after MMD-BE-14C migration and implementation.

---

## 16. Recommended Next Slice

### Selected: MMD-BE-14C — Product Version Release BOM Binding Validation Implementation

**Rationale:**

Once this policy-gated validation contract is defined, the correct next step is backend implementation. The implementation slice (MMD-BE-14C) should deliver:

1. `ProductVersion.bom_binding_required_for_release` field + Alembic migration (`0014_product_version_bom_binding_required.py`)
2. `ProductVersionItem` schema: expose `bom_binding_required_for_release`
3. `ProductVersionCreateRequest`/`ProductVersionUpdateRequest`: accept `bom_binding_required_for_release`
4. `product_version_service.release_product_version()`: add binding validation when flag is true
5. `product_version_service.update_product_version()`: accept flag update + include in changed_fields
6. Tests: 12+ tests from §15 above
7. Alembic baseline test: updated HEAD
8. Regression pass: all existing PV and BOM tests continue to pass

**After MMD-BE-14C, the recommended sequence is:**

```
MMD-BE-14C (this contract's implementation)
→ MMD-FULLSTACK-14 (BOM binding frontend integration, if not already done)
→ MMD-PV-WRITE-02 (Product Version set_current governance, if needed)
→ MMD-SCOPE-APPLICABILITY-01 (Scope-specific binding, manufacturing profile)
```

**Do not recommend MMD-FULLSTACK-14 before MMD-BE-14C.**

Reason: Binding frontend UI should not expose a release-readiness signal until the backend policy-gated validation exists.
