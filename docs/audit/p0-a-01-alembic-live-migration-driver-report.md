# P0-A-01 — Alembic Live Migration Driver / SQL Runner Retirement

**Status:** COMPLETE  
**Slice:** P0-A-01  
**Date:** 2026-05-01  
**HMM Gate:** v3  
**Verdict:** `ALLOW_P0A01_MIGRATION_HARDENING` (issued prior to coding)

---

## Problem Statement (GAP-01)

`backend/app/db/init_db.py` contained a custom SQL runner
(`_apply_sql_migrations()`) that executed raw `.sql` files from
`backend/scripts/migrations/` on **every** production app startup.  This is a
P0-BLOCKER because:

- Alembic was already present and structurally wired but was **not** the live
  migration driver.
- Schema changes deployed via the SQL runner bypassed Alembic's migration
  history (`alembic_version` table), breaking the ability to track schema state
  or run future migrations safely.
- The custom runner executed DDL on every startup; any future statement
  incompatibility would crash production startup.

---

## Invariants Enforced

| # | Invariant | Before | After |
|---|---|---|---|
| I-01 | Default `init_db()` must NOT call `create_all()` | ✓ (guarded) | ✓ (unchanged) |
| I-02 | Default `init_db()` must NOT call the legacy SQL runner | ✗ VIOLATED | ✓ FIXED |
| I-03 | Default `init_db()` MUST call Alembic `upgrade head` | ✗ VIOLATED | ✓ FIXED |
| I-04 | Dev/test bootstrap must be explicitly guarded | Partial | ✓ FIXED |
| I-05 | Importing `init_db` module must not mutate schema | ✓ | ✓ (unchanged) |
| I-06 | `_apply_sql_migrations` must not be reachable from production startup | ✗ VIOLATED | ✓ FIXED |

---

## Changes Made

### `backend/app/db/init_db.py`

**Added `run_alembic_upgrade()`** — the canonical production migration path:

```python
def run_alembic_upgrade() -> None:
    """Run alembic upgrade head programmatically."""
    global _ALEMBIC_UPGRADE_RAN
    if _ALEMBIC_UPGRADE_RAN:
        return
    with _ALEMBIC_UPGRADE_LOCK:
        if _ALEMBIC_UPGRADE_RAN:
            return
        from alembic import command
        from alembic.config import Config
        cfg = Config(str(_ALEMBIC_INI))
        command.upgrade(cfg, "head")
        _ALEMBIC_UPGRADE_RAN = True
```

Safety properties:
- Double-checked locking pattern prevents duplicate upgrades in multithreaded
  WSGI environments.
- `alembic upgrade head` is idempotent — no-op when schema is already at head.
- Uses the real `alembic.ini` path resolved relative to the `init_db.py`
  module file, so it is correct regardless of working directory.

**Modified `init_db()`** signature and body:

```python
def init_db(*, bootstrap_schema: bool = False, _use_sql_runner: bool = False) -> None:
```

- **Default path** (`init_db()`): calls `run_alembic_upgrade()`.
- **`_use_sql_runner=True`**: calls `_apply_sql_migrations()` instead of
  Alembic.  Gated flag — must not be used in production or CI.
- **`bootstrap_schema=True`**: unchanged — calls `create_all()` before
  migration step.

**Deprecated `_apply_sql_migrations()`** — retained for dev/test CLI bootstrap
only with docstring marking it a governance violation to call from production.

---

### `backend/tests/test_init_db_bootstrap_guard.py`

Rewrote to cover all four invariants:

| Test | Invariant |
|---|---|
| `test_init_db_default_does_not_call_create_all` | I-01 |
| `test_init_db_bootstrap_true_calls_create_all` | I-01 (explicit path) |
| `test_init_db_default_does_not_call_sql_runner` | I-02 |
| `test_init_db_default_calls_alembic_upgrade` | I-03 |
| `test_init_db_sql_runner_flag_calls_sql_runner` | I-04 + I-06 |

Added `_reset_upgrade_flag` autouse fixture to reset
`_ALEMBIC_UPGRADE_RAN` between tests to prevent flag from leaking.

Added `_common_patches()` helper to reduce boilerplate and ensure consistent
isolation across all tests.

---

### `backend/tests/test_qa_foundation_migration_smoke.py`

Added three structural (no-DB) smoke tests:

| Test | Purpose |
|---|---|
| `test_run_alembic_upgrade_is_exported` | `run_alembic_upgrade` is importable |
| `test_alembic_ini_path_resolves_from_init_db` | `_ALEMBIC_INI` path exists at runtime |
| `test_init_db_module_import_does_not_mutate_schema` | Import is side-effect-free |

Live DB tests (`test_upgrade_head_smoke`, `test_conditional_downgrade_...`)
are unchanged — still skip when DB is unreachable.

---

## Test Results

### Targeted tests (14 passed, 3 skipped)

```
tests/test_init_db_bootstrap_guard.py    .....   (5 passed)
tests/test_qa_foundation_migration_smoke.py  ...ss  (3 passed, 2 skipped — DB)
tests/test_alembic_baseline.py           ......s  (6 passed, 1 skipped — DB)

14 passed, 3 skipped in 4.47s
```

### Full suite

**333 passed, 3 skipped** in 75.82s — no regressions. Added 6 new tests (+6 vs prior baseline of 327).

---

## Scope Boundary

This slice touched **only**:

- `backend/app/db/init_db.py` — migration driver swap + deprecation guard
- `backend/tests/test_init_db_bootstrap_guard.py` — invariant tests
- `backend/tests/test_qa_foundation_migration_smoke.py` — structural smoke

No changes to:
- Domain models, routes, services, repositories
- RBAC, sessions, execution state machine
- Alembic migration history (no new revision added)
- Frontend
- CI workflow

---

## Governance

- Hard Mode MOM v3 gate was produced and recorded in session before coding.
- Design Evidence Extract, Migration/Runtime DB Contract Map, Invariant Map,
  and Test Matrix were all produced and approved before any file was modified.
- Verdict: `ALLOW_P0A01_MIGRATION_HARDENING`.
