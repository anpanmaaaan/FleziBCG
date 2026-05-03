# BACKEND-QA-BASELINE-02 — Ruff Lint Gate

**Status:** COMPLETE — All checks green  
**Date:** 2025-05-02  
**Slice:** Pure tooling / CI alignment — no domain, execution, auth, or migration changes  

---

## Routing

- **Selected brain:** Generic Brain  
- **Selected mode:** QA Mode — PR Gate / Tooling Alignment  
- **Hard Mode MOM:** OFF  
- **Reason:** No execution state machine, projections, auth, or tenant changes. Pure lint tooling wired to CI.

---

## Objective

Add `ruff check .` as an explicit, reproducible lint gate to the backend CI pipeline, after the green pytest baseline established in BACKEND-QA-BASELINE-01 (634 passed, 4 skipped).

---

## Context Gathered

| File | Purpose |
|------|---------|
| `backend/requirements.txt` | Dependency list — no `ruff`, no `pyproject.toml` |
| `backend/pyproject.toml` | Does not exist |
| `.github/workflows/backend-ci.yml` | Existing CI workflow — insert point identified |
| `.github/workflows/pr-gate.yml` | PR gate workflow — insert point identified |
| `backend/scripts/verify_backend.py` | BASELINE-01 verify script — extended for BASELINE-02 |

---

## Decisions

### 1. Dependency

`ruff>=0.9.0` added to `backend/requirements.txt`. This is the only dependency file; CI installs from it via `pip install -r requirements.txt`. No `pyproject.toml` exists to update.

**Installed version in dev environment:** ruff 0.15.12

### 2. Lint configuration — `backend/ruff.toml`

Created `backend/ruff.toml` with minimal conservative config:

```toml
# Ruff lint configuration — FleziBCG backend
# BACKEND-QA-BASELINE-02: minimal conservative lint gate.
target-version = "py312"
exclude = [
    ".venv",
    "alembic/versions",
]

[lint]
# Use ruff's default selection (E4, E7, E9, F) — avoids E501 line-length and
# other stylistic rules that would trigger a mass reformat requirement.
select = ["E4", "E7", "E9", "F"]

[lint.per-file-ignores]
# alembic/env.py must manipulate sys.path before importing app modules.
"alembic/env.py" = ["E402"]
# test_user_lifecycle_status.py imports app models after module-level conditional setup
"tests/test_user_lifecycle_status.py" = ["E402"]
# SQLAlchemy ORM boolean column comparison — intentional pattern
"app/repositories/reason_code_repository.py" = ["E712"]
# Pytest fixture re-import pattern — F811 redefinition is intentional
"tests/test_station_queue_session_aware_migration.py" = ["F811"]
# Pre-existing WIP file from product-version feature slice
"tests/test_product_version_foundation_api.py" = ["F841", "F811"]
```

**Rule selection rationale:** `["E4", "E7", "E9", "F"]` is ruff's built-in default. It avoids E501 (line length) and other stylistic rules that would require a mass reformat. Full `["E", "F"]` selection caused 507 errors because E501 triggered on 88-char lines across the entire codebase.

**Format check stop condition:** `ruff format --check .` reports 123 files would reformat. Format enforcement is **explicitly deferred** to BACKEND-QA-BASELINE-03 to avoid conflating lint gating with bulk reformatting in a single slice.

### 3. Per-file-ignores summary

| File | Rules | Justification |
|------|-------|---------------|
| `alembic/env.py` | E402 | `sys.path` manipulation required before app imports |
| `tests/test_user_lifecycle_status.py` | E402 | Module-level conditional setup requires late imports |
| `app/repositories/reason_code_repository.py` | E712 | SQLAlchemy ORM boolean column comparison — intentional |
| `tests/test_station_queue_session_aware_migration.py` | F811 | pytest fixture re-import for discovery — intentional |
| `tests/test_product_version_foundation_api.py` | F841, F811 | Pre-existing WIP feature file; clean-up deferred to product-version slice |

---

## Fixes Applied

### Auto-fixed by `ruff check --fix` (F401 — unused imports)

29 auto-fixable unused import removals across ~20 test files including:

- `tests/test_audit_security_event_tenant_isolation.py`
- `tests/test_auth_security_event_routes.py`
- `tests/test_auth_session_api_alignment.py`
- `tests/test_close_operation_auth.py`
- `tests/test_close_reopen_operation_foundation.py`
- `tests/test_closure_status_invariant.py`
- `tests/test_downtime_reasons_endpoint.py`
- `tests/test_init_db_bootstrap_guard.py`
- `tests/test_plant_hierarchy_orm_foundation.py`
- `tests/test_rbac_action_registry_alignment.py`
- `tests/test_reason_code_foundation_api.py`
- `tests/test_refresh_token_foundation.py`
- `tests/test_reopen_operation_claim_continuity_hardening.py`
- `tests/test_routing_operation_extended_fields.py`
- `tests/test_scope_rbac_foundation_alignment.py`
- `tests/test_start_pause_resume_command_hardening.py`
- `tests/test_station_session_diagnostic_bridge.py`
- `tests/test_user_lifecycle_status.py`
- (plus others via auto-fix)

All are mechanical import removals — no logic change.

### Manual fixes (F841 — unused variable assignments)

| File | Fix |
|------|-----|
| `tests/test_reason_code_foundation_service.py` | Removed `codes = ` assignment (return value unused) |
| `tests/test_security_events_endpoint.py` | Removed `captured = {}` (never used) |
| `tests/test_station_session_diagnostic_bridge.py` | Removed `opr_role = ` and `scope = ` assignments |
| `tests/test_station_session_command_context_diagnostic.py` | Removed `detail = ` at line 219 only (lines 274 and 421 **retained** — their `detail` variable is used by `assert detail.status` at lines 278/326/424 respectively) |
| `backend/scripts/seed/seed_products_and_routing.py` | Added `# noqa: F841` at line 487 — `init_db` alias required for the existing pattern |

### WSL/Windows filesystem cache note

The dev environment runs ruff in WSL against files on an NTFS `/mnt/g/` mount. WSL caches NTFS file contents, causing `ruff check .` (with cache) to sometimes report stale results after VS Code edits. Resolution pattern used throughout:

1. Use `sed -i` in WSL terminal to write file changes directly (bypasses NTFS cache)
2. Use `ruff check . --no-cache` to confirm actual file state
3. CI is unaffected — each CI job starts with a clean checkout, no stale cache

---

## Audit Results

### Ruff check progression

| Stage | Errors |
|-------|--------|
| Initial (no config, `select = ["E", "F"]`) | 507 |
| After narrowing to `select = ["E4", "E7", "E9", "F"]` | 51 |
| After per-file-ignores (ruff.toml) | 37 |
| After `ruff check --fix` (auto-fix F401) | 6 (all F841) |
| After manual F841 fixes | 0 |
| **Final: `ruff check .`** | **All checks passed!** |

### verify_backend.py --testenv-only

```
============================================================
FleziBCG Backend Verification (BACKEND-QA-BASELINE-02)
============================================================

[1/5] Backend import check ...
[2/5] Ruff lint check ...
[3/5] DB connectivity check ...
[4/5] Focused testenv tests ...

  [PASS] Backend import (app.main)
  [PASS] Ruff lint (ruff check .)
  [PASS] DB connectivity (postgresql+psycopg://mes:***@localhost:5432/mes)
  [PASS] Testenv safety + connectivity contract

OK: testenv-only checks passed.
```

### Full pytest suite

```
642 passed, 4 skipped, 2 warnings in 66.50s (0:01:06)
```

**Note:** BASELINE-01 recorded 634 passed. The +8 tests are from `test_product_version_foundation_api.py` (pre-existing WIP file for the product-version feature slice) which now collects cleanly after unused import fixes. Zero failures in both baselines.

---

## Deliverables

| File | Status |
|------|--------|
| `backend/ruff.toml` | Created |
| `backend/requirements.txt` | Modified — `ruff>=0.9.0` added |
| `backend/scripts/verify_backend.py` | Modified — ruff step (2/5), BASELINE-02 banner |
| `.github/workflows/backend-ci.yml` | Modified — `Backend lint (ruff check)` step added |
| `.github/workflows/pr-gate.yml` | Modified — `Backend lint (ruff check)` step added |
| Test/seed files (~25 files) | Modified — F401/F841 lint fixes, behavior-neutral |
| `docs/audit/backend-qa-baseline-02-ruff-lint-gate.md` | This file |

---

## CI Integration

### backend-ci.yml (added after Backend import check step)

```yaml
- name: Backend lint (ruff check)
  shell: bash
  run: |
    cd backend
    python -m ruff check .
```

### pr-gate.yml (added after Backend import check step)

```yaml
- name: Backend lint (ruff check)
  shell: bash
  run: |
    if [ -d backend ]; then
      cd backend
      python -m ruff check .
    fi
```

---

## Residual Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Format check deferred: 123 files would reformat | LOW | Explicitly out of scope; address in BACKEND-QA-BASELINE-03 |
| WSL NTFS cache can mask stale lint errors in local dev | LOW | Use `--no-cache` flag in local debugging; CI is unaffected |
| `test_product_version_foundation_api.py` has 12 deferred F841/F811 issues | LOW | Per-file-ignore with comment; clean-up belongs to product-version slice owner |
| `_seed_running_op` in test_station_session_command_context_diagnostic.py has `detail = start_operation(` at lines 274/421 that ruff flags as F841 if the cache is stale | LOW | Lines 274/421 ARE used by `assert detail.status` at lines 278/326/424; ruff correctly passes with clean cache |

---

## Recommended Next Slice

**BACKEND-QA-BASELINE-03 — Format gate**

Deliverables:
1. `ruff format .` run on entire backend codebase
2. `ruff format --check .` added to `backend-ci.yml` and `pr-gate.yml`
3. Updated `verify_backend.py` with format check step
4. Audit doc confirming 0 format violations after reformat

Pre-condition: BACKEND-QA-BASELINE-02 must be merged and CI green before starting.

---

## Suggested Commit

```bash
git add backend/ruff.toml
git add backend/requirements.txt
git add backend/scripts/verify_backend.py
git add .github/workflows/backend-ci.yml
git add .github/workflows/pr-gate.yml
git add docs/audit/backend-qa-baseline-02-ruff-lint-gate.md
git add backend/tests/test_reason_code_foundation_service.py
git add backend/tests/test_security_events_endpoint.py
git add backend/tests/test_station_session_diagnostic_bridge.py
git add backend/tests/test_station_session_command_context_diagnostic.py
git add backend/scripts/seed/seed_products_and_routing.py
# Plus all other test files modified by ruff --fix (check git diff --name-only)

git commit -m "feat(qa): BACKEND-QA-BASELINE-02 — wire ruff lint gate to backend CI

- Add backend/ruff.toml: conservative config (E4,E7,E9,F rules), Python 3.12,
  excludes .venv and alembic/versions, 5 per-file-ignores for justified patterns
- Add ruff>=0.9.0 to backend/requirements.txt (CI-installable)
- Update backend/scripts/verify_backend.py: add ruff check step (step 2/5),
  update banner to BASELINE-02
- Update .github/workflows/backend-ci.yml: add ruff check step after import check
- Update .github/workflows/pr-gate.yml: add ruff check step after import check
- Fix 29 auto-fixable F401 unused import issues across test files (ruff --fix)
- Fix 6 F841 unused variable assignments in test/seed files (manual)
- ruff check: All checks passed (0 errors)
- ruff format --check: 123 files, deferred to BACKEND-QA-BASELINE-03
- Full backend pytest: 642 passed, 4 skipped, 0 failures
- verify_backend.py --testenv-only: 4/4 PASS
"
```
