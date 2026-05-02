# Stop Condition Triggered — P0-A-06A

## Summary

Two stop conditions are active before coding can begin:

1. **Existing scope model already exists and conflicts with the proposed plan.**
   `backend/app/models/rbac.py` already contains `Scope`, `UserRoleAssignment`, and `RoleScope` — directly covering the `ScopeNode` / `ScopeAssignment` concept. Creating new `scope_nodes` / `scope_assignments` tables would duplicate these existing tables.

2. **Alembic head is stale — source structure differs materially from task assumptions.**
   The task assumes current head = `"0007"`, but `backend/alembic/versions/0008_boms.py` exists (revises `"0007"`). The head is now `"0008"`. Additionally, `test_alembic_baseline.py` still asserts `head == "0007"`, so it is stale and will fail against the actual migration chain.

---

## Mandatory Files Status

| File | Status |
|---|---|
| `.github/copilot-instructions.md` | Read ✅ |
| `.github/agent/AGENT.md` | Read ✅ |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Read ✅ |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | Read ✅ |

All four mandatory files present and read.

---

## Source Evidence

### Stop Condition 1: Existing Scope Models

**File:** `backend/app/models/rbac.py`

The following models already exist and are registered in `init_db.py`:

#### `Scope` (table: `scopes`)

Covers the `ScopeNode` concept:

| Field | Type | Notes |
|---|---|---|
| `id` | Integer PK (autoincrement) | Not a string PK as task proposes |
| `tenant_id` | String(64), indexed | ✅ tenant-scoped |
| `scope_type` | String(32), indexed | ✅ scope type discriminator |
| `scope_value` | String(128), indexed | ≈ `scope_ref_id` in task proposal |
| `parent_scope_id` | FK → scopes.id, nullable | ✅ self-reference hierarchy |
| `created_at` | DateTime | ✅ |

**Missing vs. task proposal:** `scope_code`, `scope_name`, `is_active`, `metadata_json`, `updated_at`, `scope_ref_id` (uses `scope_value` instead), string PK.

**Unique constraint:** `(tenant_id, scope_type, scope_value)` — equivalent to proposed `(tenant_id, scope_type, scope_ref_id)`.

#### `UserRoleAssignment` (table: `user_role_assignments`)

Covers the `ScopeAssignment` concept:

| Field | Type | Notes |
|---|---|---|
| `id` | Integer PK | Not a string PK as task proposes |
| `user_id` | String(64), indexed | ≈ `principal_id` when principal_type=USER |
| `role_id` | FK → roles.id, indexed | ≈ `principal_id` when principal_type=ROLE, but FK-constrained to roles.id |
| `scope_id` | FK → scopes.id, indexed | ✅ points to scope node |
| `is_primary` | Boolean | Extra field |
| `is_active` | Boolean | ✅ |
| `valid_from` / `valid_to` | DateTime | Extra fields |
| `created_at` | DateTime | ✅ |

**Missing vs. task proposal:** `tenant_id` directly on assignment, `principal_type` as a string discriminator (USER/ROLE), `metadata_json`, string PK.

**Note:** `user_id` and `role_id` are separate fields, not a `principal_type` + `principal_id` generic pair. Role is FK-constrained, not a free string.

#### `RoleScope` (table: `role_scopes`)

An additional scope-assignment-style model connecting `UserRole` → (scope_type, scope_value). No equivalent in the task proposal.

| Field | Notes |
|---|---|
| `user_role_id` | FK → user_roles.id |
| `scope_type` | String |
| `scope_value` | String |
| `is_active` | Boolean |
| `created_at` | DateTime |

**Unique constraint:** `(user_role_id, scope_type, scope_value)`.

#### How these models are registered

`backend/app/db/init_db.py` imports:
```python
from app.models.rbac import (
    Role, Permission, RolePermission, UserRole, RoleScope, Scope, UserRoleAssignment,
)
```
All scope-related tables are already registered with SQLAlchemy's `Base.metadata`.

#### Where these tables were created

The `0001_baseline.py` revision is a **no-op** representing the pre-Alembic schema created by `Base.metadata.create_all()`. The `scopes`, `user_role_assignments`, and `role_scopes` tables were created by that `create_all()` call. There is no dedicated Alembic migration that creates them.

---

### Stop Condition 2: Alembic Head Stale

#### Actual migration chain (inspected from `alembic/versions/`):

```
0001 (baseline, no-op)
0002 (add_refresh_tokens)
0003 (routing_operation_extended_fields)
0004 (add_user_lifecycle_status)
0005 (add_plant_hierarchy)
0006 (add_tenant_lifecycle_anchor)
0007 (product_versions)
0008 (boms)   ← CURRENT HEAD
```

**Revision 0008** (`0008_boms.py`): creates `boms` and `bom_items` tables. `down_revision = "0007"`. This is the current head.

#### Stale test assertion in `test_alembic_baseline.py`:

```python
def test_alembic_head_is_baseline():
    ...
    assert "0007" in heads, f"Expected 0007 as head, got: {heads}"

def test_alembic_upgrade_head_live(db_engine):
    ...
    assert "0007" in rows, f"Expected 0007 in alembic_version, got: {rows}"
```

These will fail because the head is now `"0008"`. This is a pre-existing stale assertion from a prior session (P0-A-02B updated it to 0007, before 0008_boms.py was added by P0-B).

---

## Why Continuing Is Unsafe

### Conflict 1: Table duplication if new scope_nodes / scope_assignments are created

If P0-A-06A creates `scope_nodes` and `scope_assignments` tables as new migration 0009, two problems arise:

1. **Duplication of purpose:** `scopes` and `scope_nodes` both represent scope boundaries; `user_role_assignments` and `scope_assignments` both represent scope memberships. Future developers would not know which to use.

2. **Import/registration confusion:** `init_db.py` already registers `Scope` and `UserRoleAssignment`. Adding new `ScopeNode` and `ScopeAssignment` models would co-exist with them under the same Base registry.

3. **No migration guard:** The 0001 baseline is a no-op — the existing scope tables were created by `create_all()`. A new migration 0009 that creates `scope_nodes` would succeed, but developers would now have BOTH `scopes` (from baseline) AND `scope_nodes` (from 0009), which is architecturally incorrect.

### Conflict 2: Stale head assertion blocks CI before scope work begins

`test_alembic_baseline.py` asserts `head == "0007"` but actual head is `"0008"`. This pre-existing issue must be resolved independently before the P0-A-06A scope migration (0009) is added, or the stale assertion would introduce layered confusion.

---

## Options

### Option A — Recommended: Adapt P0-A-06A to the existing scope foundation

**What this means:**
- Treat `Scope` (table: `scopes`) as the canonical `ScopeNode` equivalent.
- Treat `UserRoleAssignment` (table: `user_role_assignments`) as the canonical `ScopeAssignment` equivalent.
- Do NOT create new `scope_nodes` / `scope_assignments` tables.
- Add `SCOPE_TYPE_*` and `PRINCIPAL_TYPE_*` constants (currently absent) to a new `backend/app/models/scope_constants.py` or to `rbac.py`.
- Add missing fields to `scopes` via a new migration 0009: `scope_code` (nullable String), `scope_name` (nullable String), `is_active` (Boolean, default True), `metadata_json` (nullable Text/JSON).
- Write tests for the existing scope model baseline (fields, constraints, constants).
- Fix the stale `test_alembic_baseline.py` head assertion to `"0009"` once migration 0009 is added.

**Minimal adaptation for the task:**
- All existing runtime behavior is preserved (existing tests pass).
- No new table duplication.
- The "scope foundation" exists and is documented/tested.
- The migration enhancement adds the missing fields the task proposed for `ScopeNode` without creating a duplicate table.

**Risk:** Modifying the existing `scopes` table requires verifying no existing tests/seeds depend on the absence of those columns. This is safe — adding nullable columns is backward-compatible.

### Option B: Test-only, no migration

- Recognize the existing scope models as the scope foundation.
- Write tests only.
- Add constants only.
- No migration.
- The task's migration requirement is documented as "N/A — existing tables cover scope foundation."

**Risk:** The task's required test `test_scope_migration_revision_exists` cannot pass without a real migration.

### Option C: New scope tables as distinct models (follow task literally)

- Create `scope_nodes` + `scope_assignments` tables as migration 0009.
- These exist ALONGSIDE `scopes` / `user_role_assignments`.
- Document the dual-scope model as a known architectural debt.
- Hard reject for P0-A: this creates duplication that will confuse every future slice.

**Decision: STOP. Do not implement Option C.**

---

## Recommended Decision

**Implement Option A with two pre-requisites:**

1. **Pre-requisite A1 (stale head fix):** Update `test_alembic_baseline.py` head assertion from `"0007"` to the correct head after any new migration. Since 0008 already exists, this fix must be to `"0008"` before any new migration, then updated again to `"0009"` after.

2. **Pre-requisite A2 (task redefinition):** The task plan should be adapted to:
   - Enhance the existing `Scope` and `UserRoleAssignment` models instead of creating duplicates.
   - Treat `ScopeNode` ≡ `Scope` (table: `scopes`).
   - Treat `ScopeAssignment` ≡ `UserRoleAssignment` (table: `user_role_assignments`).
   - Add migration 0009 to add missing fields to `scopes`: `scope_code`, `scope_name`, `is_active`, `metadata_json`.
   - Add `SCOPE_TYPE_*` / `PRINCIPAL_TYPE_*` constants.
   - Write baseline tests for existing scope model.

**Alternatively:** If the task author intends the "scope node/assignment" to be a *completely separate* design from the RBAC scope tables, explicit written authorization is required before proceeding, since it would create intentional table duplication.

---

## Immediate Safe Actions (before any scope work)

These pre-existing issues should be fixed regardless of which option is chosen:

1. **Fix stale `test_alembic_baseline.py` head assertion** — change `"0007"` to `"0008"` (current actual head). This is a pre-existing regression introduced when `0008_boms.py` was added.

2. **Document that `scopes` / `user_role_assignments` / `role_scopes` tables exist under the 0001 no-op baseline** — a future slice may want to create a dedicated Alembic migration for them.

---

## Stop Conditions Active

| Stop Condition | Triggered? |
|---|---|
| Mandatory files missing | No |
| Current Alembic head is unclear or multiple heads exist | Partial — head is 0008 but task assumes 0007 |
| Existing scope model already exists and conflicts with this plan | YES — `Scope` + `UserRoleAssignment` in `rbac.py` |
| Implementation requires auth/RBAC runtime enforcement | No |
| Implementation requires API/Admin UI | No |
| Source structure differs materially from assumptions | YES — head=0008, existing scope models present |
