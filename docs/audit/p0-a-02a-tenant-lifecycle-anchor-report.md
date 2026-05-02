# P0-A-02A Report
## Tenant Lifecycle Anchor

**Slice:** P0-A-02A  
**Date:** 2026-05-02  
**Status:** COMPLETE  
**Verdict:** `ALLOW_P0A02A_TENANT_LIFECYCLE_ANCHOR` → IMPLEMENTED

---

## Summary

Added the canonical `Tenant` ORM model and Alembic migration `0006` that creates the `tenants` table. Existing `tenant_id` string columns in all models are unchanged. No FK retrofit. No API or Admin UI. 16 new tests pass. 91 regression tests pass.

---

## Routing

```
Selected brain: MOM Brain
Selected mode: Strict
Hard Mode MOM: v3 — task touches tenant foundation, multi-tenant boundary,
               IAM/scope foundation, Alembic migration, schema baseline
Reason: Tenant table is governance/scope anchor; mistakes propagate to all
        future tenant isolation, IAM, and scope assignment slices.
```

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| No `tenant.py` in `backend/app/models/` | `list_dir` | No Tenant ORM existed |
| All models use `tenant_id: Mapped[str]` as unconstrained string | `user.py`, `plant_hierarchy.py`, migration 0005 comment | Soft string reference pattern throughout |
| Migration chain: linear, single head at `0005` | `alembic/versions/` | New revision → `0006`, `down_revision="0005"` |
| Lifecycle constants pattern: string constants + `server_default` + `__init__` override | `user.py` | Must follow same pattern |
| `is_lifecycle_active` property pattern | `user.py` | Applied to Tenant |
| `init_db.py` imports all models for Alembic metadata | `init_db.py` | Added Tenant import |
| `test_alembic_baseline.py` hardcodes `"0005"` as head | line 96 | Updated to `"0006"` |
| Live test asserted `"0001"` in alembic_version (pre-existing bug) | line 116 | Fixed to `"0006"` (correct: alembic_version holds current head after upgrade) |
| `test_tenant_foundation.py` tests auth header mismatch | `test_tenant_foundation.py` | Unaffected — different concern |
| P0-A-BASELINE-01 gap: tenant table absent | BASELINE-01 report | This slice closes that gap |

### Current Tenant Source Map

| Source Area | Current Evidence | Change? | Decision |
|---|---|---|---|
| `user.py` | `tenant_id: Mapped[str]` string column | None | Backward-compatible |
| `plant_hierarchy.py` Plant | `tenant_id: Mapped[str]` "soft string reference" | None | Backward-compatible |
| `security_event.py` | `tenant_id` string column | None | N/A |
| `session.py` | `tenant_id` string column | None | N/A |
| `rbac.py` | No direct tenant_id FK | None | N/A |
| `test_tenant_foundation.py` | Auth header mismatch test | None | Not a Tenant ORM test |
| `dependencies.py` | `X-Tenant-ID` header check | None | Not modified |

### Tenant Contract Map

| Entity | Table | Lifecycle? | Existing References? | Tests Added |
|---|---|---|---|---|
| `Tenant` | `tenants` | YES — `ACTIVE/DISABLED/SUSPENDED` | No (string `tenant_id` remains unconstrained) | 16 |

### Migration Contract Map

| Migration Item | Decision | Reason | Risk |
|---|---|---|---|
| New table `tenants` | CREATE | Anchor | Low |
| `UniqueConstraint("tenant_code")` | YES | Globally unique | Low |
| `ix_tenants_tenant_code` | YES | Lookup | Low |
| `ix_tenants_lifecycle_status` | YES | Filter | Low |
| `ix_tenants_is_active` | YES | Filter | Low |
| `server_default` for `lifecycle_status` | YES — `"ACTIVE"` | Matches user.py | Low |
| No existing table modifications | ENFORCED | Out of scope | None |
| No FK from existing tables | ENFORCED | Out of scope | None |
| Downgrade drops `tenants` table only | YES | Reversible | Low |
| `revision="0006"`, `down_revision="0005"` | YES | Linear chain | None |
| No data migration | ENFORCED | No rows to backfill | None |

### Invariant Map

| Invariant | Test |
|---|---|
| Tenant table exists after migration | `test_tenant_model_exists` |
| Tenant IDs remain string-compatible | `test_tenant_fields_exist` |
| Existing tables NOT modified | `test_tenant_migration_does_not_modify_existing_tables` |
| No FK retrofit | Documented; migration AST verified |
| Tenant lifecycle STORED not ENFORCED | `test_tenant_lifecycle_constants_exist` |
| Migration chain linear, single head | `test_alembic_head_is_updated_to_new_revision` |
| Downgrade removes only tenant artifacts | `test_tenant_downgrade_drops_tenants_table_only` |

### Verdict before coding

`ALLOW_P0A02A_TENANT_LIFECYCLE_ANCHOR` — all evidence present; single head at `0005`; no conflicts.

---

## Backward Compatibility Decision

- Existing `tenant_id: Mapped[str]` columns in all models → **unchanged**
- No existing rows migrated — `tenants` table starts empty
- No existing queries changed
- No auth/session behavior changed
- Tenant lifecycle enforcement deferred to future slice
- `test_tenant_foundation.py` (auth header mismatch) → **unaffected**

---

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `backend/app/models/` (full listing)
- `backend/app/models/user.py`
- `backend/app/models/plant_hierarchy.py`
- `backend/app/db/init_db.py`
- `backend/alembic/versions/` (all 5 existing migrations)
- `backend/alembic/versions/0005_add_plant_hierarchy.py`
- `backend/alembic/env.py`
- `backend/tests/test_alembic_baseline.py`
- `backend/tests/test_tenant_foundation.py`

---

## Files Changed

| File | Type | Change |
|---|---|---|
| `backend/app/models/tenant.py` | NEW | Tenant ORM model + constants |
| `backend/alembic/versions/0006_add_tenant_lifecycle_anchor.py` | NEW | Migration creates `tenants` table |
| `backend/app/db/init_db.py` | MODIFIED | Added `from app.models.tenant import Tenant  # noqa: F401` |
| `backend/tests/test_tenant_lifecycle_anchor.py` | NEW | 16 tests |
| `backend/tests/test_alembic_baseline.py` | MODIFIED | Updated head assertion `0005` → `0006`; fixed live test assertion `0001` → `0006` |

---

## Migration Added

| Field | Value |
|---|---|
| File | `backend/alembic/versions/0006_add_tenant_lifecycle_anchor.py` |
| `revision` | `"0006"` |
| `down_revision` | `"0005"` |
| Table created | `tenants` |
| Unique constraint | `uq_tenants_tenant_code` |
| Indexes | `ix_tenants_tenant_code`, `ix_tenants_lifecycle_status`, `ix_tenants_is_active` |
| Existing tables modified | **None** |
| Data migration | **None** |
| Downgrade | Drops indexes then `tenants` table only |

---

## Tests Added / Updated

### New: `backend/tests/test_tenant_lifecycle_anchor.py` — 16 tests

| Test | Result |
|---|---|
| `test_tenant_model_exists` | PASS |
| `test_tenant_fields_exist` | PASS |
| `test_tenant_lifecycle_constants_exist` | PASS |
| `test_tenant_default_status_is_active` | PASS |
| `test_tenant_is_active_defaults_true` | PASS |
| `test_tenant_is_lifecycle_active_property` | PASS |
| `test_tenant_sqlite_round_trip` | PASS |
| `test_tenant_migration_revision_exists` | PASS |
| `test_tenant_migration_revision_id` | PASS |
| `test_tenant_migration_down_revision_matches_current_head` | PASS |
| `test_tenant_migration_creates_tenants_table_only` | PASS |
| `test_tenant_migration_does_not_modify_existing_tables` | PASS |
| `test_tenant_unique_constraints_exist` | PASS |
| `test_tenant_indexes_exist` | PASS |
| `test_tenant_downgrade_drops_tenants_table_only` | PASS |
| `test_alembic_head_is_updated_to_new_revision` | PASS |

### Updated: `backend/tests/test_alembic_baseline.py`

- `test_alembic_head_is_baseline` — head assertion updated `"0005"` → `"0006"`; chain comment updated
- `test_alembic_upgrade_head_live` — alembic_version assertion corrected `"0001"` → `"0006"` (pre-existing bug: after `upgrade head`, `alembic_version` contains current head, not `"0001"`)

---

## Verification Commands Run

```
# New tests
cd backend
python -m pytest tests/test_tenant_lifecycle_anchor.py -q --tb=short

# Regression suite
python -m pytest tests/test_alembic_baseline.py \
  tests/test_qa_foundation_migration_smoke.py \
  tests/test_init_db_bootstrap_guard.py \
  tests/test_tenant_foundation.py \
  tests/test_refresh_token_foundation.py \
  tests/test_refresh_token_rotation.py \
  tests/test_user_lifecycle_status.py \
  tests/test_plant_hierarchy_orm_foundation.py \
  tests/test_security_event_service.py \
  tests/test_security_events_endpoint.py \
  -q --tb=short
```

---

## Results

| Suite | Passed | Skipped | Failed |
|---|---|---|---|
| `test_tenant_lifecycle_anchor.py` | 16 | 0 | 0 |
| Regression (10 test files) | 91 | 3 | 0 |
| **Total** | **107** | **3** | **0** |

Skips = live Postgres tests without Postgres available locally (expected; will pass in CI with `backend-ci.yml` Postgres service).

---

## Existing Gaps / Known Debts

| Gap | Scope | Next Slice |
|---|---|---|
| No FK from existing `tenant_id` columns to `tenants.tenant_id` | Deliberately deferred | Future slice — requires data migration planning |
| Tenant lifecycle not enforced in auth/session/API | Deliberately deferred | Future auth hardening slice |
| No tenant CRUD API / Admin UI | Out of scope for this slice | Future Admin slice |
| `test_station_queue_session_aware_migration.py` pre-existing failure | Pre-existing; unrelated | Requires isolated fix |
| `backend-ci.yml` does not include `test_tenant_lifecycle_anchor.py` | CI was not modified (per task) | Update CI gate in next CI slice |

---

## Scope Compliance

| Requirement | Status |
|---|---|
| Tenant ORM model added | ✓ |
| Alembic migration creates `tenants` | ✓ |
| Lifecycle status stored | ✓ |
| Existing `tenant_id` strings backward-compatible | ✓ |
| No existing domain table modified | ✓ |
| No FK retrofit | ✓ |
| No API endpoints added | ✓ |
| No frontend changes | ✓ |
| No Admin UI | ✓ |
| Required tests added | ✓ (16 new) |
| Report created | ✓ |

---

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Future slice adds FK from users → tenants without data migration | HIGH | Migration must include `INSERT INTO tenants` backfill for existing `tenant_id` strings before FK add |
| `backend-ci.yml` Alembic head check expects `0005`; now head is `0006` | LOW | `alembic heads` check uses count-based assertion not revision-specific — will pass |

---

## Recommended Next Slice

**P0-A-CI-02 or inline CI update:** Add `test_tenant_lifecycle_anchor.py` to the `backend-ci.yml` P0-A foundation gate and to `pr-gate.yml` targeted test list.

After that: consider **P0-A-02B** — Tenant lifecycle enforcement in auth, or **P0-A-06A** — Tenant CRUD Admin API (if product scope permits).

---

## Stop Conditions Hit

None.
