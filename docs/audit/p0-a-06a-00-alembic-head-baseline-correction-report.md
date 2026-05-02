# P0-A-06A-00R: Alembic Head Baseline Correction

**Slice:** P0-A-06A-00R  
**Date:** 2026-05-02  
**Verdict:** `ALLOW_P0A06A00R_ALEMBIC_HEAD_BASELINE_CORRECTION` -> IMPLEMENTED

---

## Routing
- **Selected brain:** MOM Brain
- **Selected mode:** Backend foundation correction / Alembic baseline alignment
- **Hard Mode MOM:** v3 ON
- **Reason:** Touches migration head truth and baseline gate assertions that protect schema/test invariants

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source |
|---|---|
| Current migration files include `0009_drop_station_claims.py` | `backend/alembic/versions/` |
| `0009_drop_station_claims.py` declares `revision = "0009"` and `down_revision = "0008"` | `backend/alembic/versions/0009_drop_station_claims.py` |
| Runtime Alembic head resolves to `0009` | `g:/Work/FleziBCG/.venv/Scripts/alembic.exe heads` |
| Baseline test previously asserted stale head (`0007`, then intermediate `0008`) | `backend/tests/test_alembic_baseline.py` |
| CI summary string still says `linear chain to 0007` | `.github/workflows/backend-ci.yml` |

### Event Map

No execution domain events added/changed. This slice changes test assertions and documentation only.

### Invariant Map

| Invariant | Enforcement |
|---|---|
| Alembic migration graph must have exactly one head | `assert len(heads) == 1` in baseline test |
| Expected head must match authoritative latest revision | baseline assertions updated to `0009` |
| Live upgrade stamps `alembic_version` with current head | `test_alembic_upgrade_head_live` expects `0009` |

### State Transition Map

Not applicable. No runtime state machine changes.

### Test Matrix

| Test Command | Result |
|---|---|
| `python -m pytest -q tests/test_alembic_baseline.py` | `6 passed, 1 skipped` |
| `python -m pytest -q tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | `8 passed, 2 skipped` |
| `alembic heads` | `0009 (head)` |

### Verdict Before Coding

Proceed approved under **WORKSPACE ISOLATION OVERRIDE** because:
- unrelated workspace noise existed but was left untouched,
- target file had no conflicting pre-edit diff,
- migration truth was verified before modifying assertions.

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_alembic_baseline.py` | Updated stale head/doc assertions to current revision `0009` |
| `docs/audit/p0-a-06a-00-alembic-head-baseline-correction-report.md` | New implementation report |

---

## Implementation Notes

- The original correction intent was `0007 -> 0008`, but validation showed head had already advanced to `0009`.
- Assertions were aligned to the actual authoritative head to keep baseline checks truthful.
- `.github/workflows/backend-ci.yml` still contains an informational stale summary string (`0007`), but it was intentionally not edited in this retry to honor strict two-file isolation scope.

---

## Scope Compliance

- ✅ Edited only allowed code target: `backend/tests/test_alembic_baseline.py`
- ✅ Added only required report file
- ✅ No migration files changed
- ✅ No backend runtime/business logic changed
- ✅ No auth/tenant/execution/quality/material behavior changed

---

## Verification Commands Executed

```bash
cd backend
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_alembic_baseline.py
# 6 passed, 1 skipped

g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
# 8 passed, 2 skipped

g:/Work/FleziBCG/.venv/Scripts/alembic.exe heads
# 0009 (head)
```
