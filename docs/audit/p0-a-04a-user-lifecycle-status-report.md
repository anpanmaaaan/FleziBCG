# P0-A-04A — User Lifecycle Status: Evidence Report

**Slice:** P0-A-04A — User Lifecycle Status Enum Evidence + Minimal Schema  
**Date:** 2026-05-02  
**Status:** COMPLETE — All tests pass, no regressions

---

## Summary

Added a `lifecycle_status` field to the `User` model and Alembic migration `0004`
to support foundation-grade IAM beyond the single boolean `is_active` flag.

Lifecycle values: **ACTIVE**, **DISABLED**, **LOCKED** (string, not DB-native enum).

Auth eligibility now requires **both** `is_active = True` **and**
`lifecycle_status = 'ACTIVE'`. The `is_active` column is retained for
backward compatibility.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Strict Mode
- **Hard Mode MOM:** v3 ON
- **Reason:** Task touches IAM lifecycle, authentication eligibility,
  auth/session foundation, DB migration, tenant/scope/auth boundary, and
  critical account-state invariants.

---

## HMM v3 Gate Verdict

`ALLOW_P0A04A_USER_LIFECYCLE_STATUS_SCHEMA`

Gate produced in full before any implementation began. All 5 artifacts generated:
Design Evidence Extract, Event Map, Invariant Map, State Transition Map, Test Matrix.

Key invariants verified:
- `is_active` column retained (backward compat)
- `lifecycle_status` must be `ACTIVE` for login and refresh-token eligibility
- Backfill maps `is_active=true → ACTIVE`, `is_active=false → DISABLED`
- Only the `users` table is modified by migration 0004
- Alembic head advances from 0003 to 0004

---

## Backward Compatibility Decision

| Item | Decision | Reason |
|---|---|---|
| `is_active` column | Retained, unchanged | Existing tests and code depend on it |
| Login gate | `is_active=True` AND `lifecycle_status=ACTIVE` | Additive — does not change existing active-user behavior |
| API response shape | Unchanged | `lifecycle_status` not exposed in this slice |
| Existing users | Backfilled by migration | Safe: `is_active=true → ACTIVE`, `is_active=false → DISABLED` |
| New users | Default `ACTIVE` via ORM `__init__` and `server_default` | Safe |

---

## Files Inspected

| File | Why |
|---|---|
| `backend/app/models/user.py` | User model baseline |
| `backend/app/security/auth.py` | Auth eligibility functions (login + refresh) |
| `backend/app/services/user_lifecycle_service.py` | activate_user / deactivate_user |
| `backend/app/repositories/user_repository.py` | set_user_active repository function |
| `backend/alembic/versions/` (0001–0003) | Migration chain baseline |
| `backend/tests/test_alembic_baseline.py` | Head pin assertion |
| `backend/tests/test_user_lifecycle_service.py` | Service test baseline |
| `backend/tests/test_auth_refresh_token_runtime.py` | Auth refresh runtime test |
| `backend/tests/test_qa_foundation_migration_smoke.py` | Smoke test baseline |

---

## Files Changed

### Modified

| File | Change |
|---|---|
| [backend/app/models/user.py](../../backend/app/models/user.py) | Added `LIFECYCLE_STATUS_ACTIVE/DISABLED/LOCKED` constants; added `lifecycle_status: Mapped[str]` field with `default`/`server_default="ACTIVE"`; added `is_lifecycle_active` property; added `Index("ix_users_lifecycle_status")` in `__table_args__`; added `__init__` override to set Python-construction default |
| [backend/app/security/auth.py](../../backend/app/security/auth.py) | `authenticate_user_db`: added `User.lifecycle_status == LIFECYCLE_STATUS_ACTIVE` to WHERE clause; `get_identity_by_user_id`: same change — refresh-token path now checks lifecycle status |
| [backend/app/services/user_lifecycle_service.py](../../backend/app/services/user_lifecycle_service.py) | `activate_user`: calls `set_user_lifecycle_status(…, ACTIVE)` after `set_user_active`; `deactivate_user`: calls `set_user_lifecycle_status(…, DISABLED)` after `set_user_active` |
| [backend/app/repositories/user_repository.py](../../backend/app/repositories/user_repository.py) | Added `set_user_lifecycle_status` function |
| [backend/tests/test_alembic_baseline.py](../../backend/tests/test_alembic_baseline.py) | Updated `test_alembic_head_is_baseline` to assert head == `"0004"` |

### Created

| File | Purpose |
|---|---|
| [backend/alembic/versions/0004_add_user_lifecycle_status.py](../../backend/alembic/versions/0004_add_user_lifecycle_status.py) | Alembic migration adding `lifecycle_status VARCHAR(32)` to `users` table with backfill and index |
| [backend/tests/test_user_lifecycle_status.py](../../backend/tests/test_user_lifecycle_status.py) | 20 tests covering all lifecycle status invariants |

---

## Migration Added

**File:** `backend/alembic/versions/0004_add_user_lifecycle_status.py`

| Property | Value |
|---|---|
| Revision | `0004` |
| down_revision | `0003` |
| Alembic head after | `0004` |
| Table modified | `users` only |
| Column added | `lifecycle_status VARCHAR(32) NULLABLE` (SQLite); `NOT NULL` (Postgres via `alter_column`) |
| server_default | `'ACTIVE'` |
| Backfill SQL | `UPDATE users SET lifecycle_status = 'ACTIVE' WHERE is_active = true` + `UPDATE … 'DISABLED' WHERE is_active = false` |
| Index added | `ix_users_lifecycle_status` on `users.lifecycle_status` |
| Downgrade | Drops index + drops column (is_active unchanged) |
| SQLite compat | Column added nullable; `alter_column` for NOT NULL skipped for SQLite dialect |

---

## Tests Added / Updated

### New: `backend/tests/test_user_lifecycle_status.py` — 20 tests

| Test | Area | Expected |
|---|---|---|
| `test_user_lifecycle_status_field_exists` | Model | `User.lifecycle_status` attribute exists |
| `test_user_lifecycle_status_default_is_active` | Model | `User()` without explicit status → `ACTIVE` |
| `test_user_is_lifecycle_active_property_active` | Model | `is_lifecycle_active = True` when both active |
| `test_user_is_lifecycle_active_property_disabled` | Model | `is_lifecycle_active = False` when DISABLED |
| `test_user_is_lifecycle_active_property_locked` | Model | `is_lifecycle_active = False` when LOCKED |
| `test_user_is_lifecycle_active_property_inactive` | Model | `is_lifecycle_active = False` when is_active=False |
| `test_user_lifecycle_status_field_persisted` | Model+DB | DISABLED value persists through SQLite round-trip |
| `test_user_status_migration_revision_exists` | Migration | Revision 0004 discoverable by ScriptDirectory |
| `test_user_status_migration_down_revision_is_0003` | Migration | down_revision == "0003" |
| `test_user_status_migration_backfills_from_is_active` | Migration | active→ACTIVE, inactive→DISABLED via raw SQLite |
| `test_user_status_migration_does_not_touch_unrelated_tables` | Migration | Only `users` table in migration AST |
| `test_active_user_can_login` | Auth | ACTIVE user → `authenticate_user_db` returns identity |
| `test_disabled_user_cannot_login` | Auth | DISABLED user → returns None |
| `test_locked_user_cannot_login` | Auth | LOCKED user → returns None |
| `test_inactive_user_maps_to_disabled_and_cannot_login` | Auth | `is_active=False` → returns None |
| `test_refresh_token_flow_does_not_bypass_disabled_user` | Auth | DISABLED user → `get_identity_by_user_id` returns None |
| `test_refresh_token_flow_does_not_bypass_locked_user` | Auth | LOCKED user → `get_identity_by_user_id` returns None |
| `test_activate_user_sets_status_active` | Service | `activate_user` → `lifecycle_status == ACTIVE` |
| `test_deactivate_user_sets_status_disabled` | Service | `deactivate_user` → `lifecycle_status == DISABLED` |
| `test_activate_user_unknown_user_returns_none` | Service | Non-existent user → None |

### Updated: `backend/tests/test_alembic_baseline.py`

- `test_alembic_head_is_baseline`: Updated to assert head == `"0004"`

---

## Verification Commands Run

```bash
# New lifecycle status tests
python3.12 -m pytest tests/test_user_lifecycle_status.py --tb=short
# → 20 passed, 1 warning

# Service and baseline regression
python3.12 -m pytest tests/test_user_lifecycle_service.py tests/test_alembic_baseline.py --tb=short
# → 8 passed, 1 skipped

# Auth refresh + rotation regression
python3.12 -m pytest tests/test_auth_refresh_token_runtime.py tests/test_refresh_token_rotation.py --tb=short
# → 19 passed + 8 passed

# Init DB and migration smoke
python3.12 -m pytest tests/test_init_db_bootstrap_guard.py tests/test_qa_foundation_migration_smoke.py --tb=short
# → 5 passed + 3 passed, 2 skipped
```

---

## Results

| Test Suite | Result |
|---|---|
| `test_user_lifecycle_status.py` (20 tests) | ✅ 20 PASS |
| `test_user_lifecycle_service.py` (2 tests) | ✅ 2 PASS |
| `test_alembic_baseline.py` (7 tests) | ✅ 6 PASS, 1 SKIP (live-DB test) |
| `test_auth_refresh_token_runtime.py` (19 tests) | ✅ 19 PASS |
| `test_refresh_token_rotation.py` (8 tests) | ✅ 8 PASS |
| `test_init_db_bootstrap_guard.py` (5 tests) | ✅ 5 PASS |
| `test_qa_foundation_migration_smoke.py` (5 tests) | ✅ 3 PASS, 2 SKIP (live-DB tests) |

**No regressions. No test failures. 63 passed, 3 skipped (all skips are pre-existing live-DB tests).**

---

## Existing Gaps / Known Debts

| Gap | Severity | Deferred To |
|---|---|---|
| `lifecycle_status` not exposed in User API response | Low | Future slice — P0-A-04B or admin IAM slice |
| LOCKED state has no enforcement path (no lock trigger) | Medium | Future slice — account lock policy |
| `is_active` redundant with `lifecycle_status=DISABLED` | Low | Future slice — deprecation of `is_active` boolean after all callers migrated |
| Admin API to set `lifecycle_status` directly | Medium | Future slice — admin IAM |
| Audit event not recorded when lifecycle_status changes via DB seed/migration | Low | Acceptable — only automated service calls emit audit events |

---

## Scope Compliance

| Constraint | Complied? |
|---|---|
| No invitation/password-reset/MFA workflows | ✅ Not touched |
| No admin UI / frontend changes | ✅ No frontend files modified |
| No new IAM endpoints | ✅ No new routes |
| No migration 0001/0002/0003 changes | ✅ Those files unchanged |
| Vertical slice only | ✅ Backend-only, minimal surface area |
| Behavior-based tests | ✅ All tests validate behavior, not implementation detail |
| `is_active` backward compat preserved | ✅ Column retained, existing tests pass |

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Production backfill (is_active=false → DISABLED) missing an edge case | Low | Both UPDATE statements are exhaustive — `is_active` is always true or false, no third state |
| SQLite test environment's nullable column differs from production Postgres NOT NULL | Low | ORM Python default + `__init__` override handles this; Postgres gets NOT NULL via `alter_column` |
| Existing code constructing `User()` without `lifecycle_status` (outside tests) | Low | `__init__` override sets `LIFECYCLE_STATUS_ACTIVE` as default; `server_default` covers DB-direct inserts |

---

## Recommended Next Slice

**P0-A-04B** or equivalent: Expose `lifecycle_status` in the User read schema (API response). Add an admin endpoint to set `lifecycle_status` directly (with audit). Add test for `LOCKED` state enforcement path (lock trigger).

---

## Stop Conditions Hit

None. Implementation proceeded cleanly within scope. Gate was produced, verdict was ALLOW, implementation completed, all tests pass.
