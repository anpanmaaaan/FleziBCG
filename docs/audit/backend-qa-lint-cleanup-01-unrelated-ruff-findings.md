# BACKEND-QA-LINT-CLEANUP-01: Unrelated Ruff Findings Cleanup

**Date:** 2025-01-27  
**Scope:** Remove stale lint failures in 3 test files + lint issues in new untracked seed script  
**Blocker for:** BACKEND-QA-BASELINE-03 (ruff format baseline)  
**Status:** COMPLETE

---

## Hard Mode MOM v3 Gate

**Trigger:** `test_approval_security_events.py` touches approval governance scope.

| Evidence | Finding |
|---|---|
| Design Evidence | Change removes `import pytest` (F401). No approval event contract, authorization logic, or service call modified. |
| Event Map | No event contracts or emission paths touched. |
| Invariant Map | No invariants touched. |
| State Transition | N/A — no stateful entity modified. |
| Test Matrix | No test behavior changes; same assertions, same covered paths. |
| **Verdict** | **ALLOW_IMPLEMENTATION** — purely mechanical unused-import removal. |

---

## Findings Fixed

### Test Files (6 findings)

| File | Line | Code | Finding | Fix Applied |
|---|---|---|---|---|
| `tests/test_approval_security_events.py` | 15 | F401 | `import pytest` unused | Removed import |
| `tests/test_bom_foundation_service.py` | 18 | F401 | `BomItemUpdateRequest` unused | Removed from import block |
| `tests/test_bom_foundation_service.py` | 29 | F401 | `remove_bom_item` unused | Removed from import block |
| `tests/test_bom_foundation_service.py` | 32 | F401 | `update_bom_item` unused | Removed from import block |
| `tests/test_bom_foundation_service.py` | 272 | F841 | `product_id` assigned but unused | Dropped assignment, kept call |
| `tests/test_station_queue_session_aware_migration.py` | 75 | F401 | `RequestIdentity` unused inside function | Removed import line |

### Seed Script (13 findings — `ruff check --fix` applied)

`scripts/seed/seed_station_session_scenarios.py` — untracked dev/manual seed tool

| Code | Finding |
|---|---|
| F401 | `import uuid` unused |
| F401 | `datetime.timezone` unused |
| F541 ×9 | f-strings without placeholders in print statements across ss1/ss2/ss3/ss4 scenarios |

All 13 fixed automatically via `ruff check --fix`.

---

## Verification Results

```
ruff check . --no-cache → All checks passed!

pytest tests/test_approval_security_events.py \
       tests/test_bom_foundation_service.py \
       tests/test_station_queue_session_aware_migration.py -q
→ 31 passed, 2 warnings in 10.86s

verify_backend.py --testenv-only
→ [PASS] Backend import (app.main)
→ [PASS] Ruff lint (ruff check .)
→ [PASS] DB connectivity
→ [PASS] Testenv safety + connectivity contract
```

---

## BASELINE-03 Pre-Conditions Remaining

After this cleanup, the remaining blockers for BACKEND-QA-BASELINE-03 are:

1. **Commit station-session test hardening files** (separate slice):
   - `tests/test_station_session_command_context_diagnostic.py` (modified)
   - `tests/test_station_session_lifecycle.py` (modified)
   - `tests/test_station_session_open_start_hardening.py`

2. **Commit this lint cleanup + seed script + audit reports**:
   - `tests/test_approval_security_events.py`
   - `tests/test_bom_foundation_service.py`
   - `tests/test_station_queue_session_aware_migration.py`
   - `scripts/seed/seed_station_session_scenarios.py`
   - `docs/audit/backend-qa-lint-cleanup-01-unrelated-ruff-findings.md`
   - `docs/audit/station-session-test-hardening-01-isolation-report.md`

3. **Confirm clean git status for backend/** before running `ruff format .`

After pre-conditions clear, BASELINE-03 proceeds with:
- `ruff format .` (mechanical only)
- Wire `ruff format --check .` into `verify_backend.py` and CI workflows
