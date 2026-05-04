# BACKEND-QA-BASELINE-03 — Ruff Format Mechanical Baseline

**Date:** 2025-07-15
**Scope:** `backend/` — all Python source files
**Type:** Mechanical-only (whitespace / style normalization, zero logic change)
**Status:** COMPLETE ✅

---

## Objective

Apply `ruff format` as a one-time mechanical baseline across all backend Python
files, then enforce `ruff format --check .` in:

- `backend/scripts/verify_backend.py` — local developer gate
- `.github/workflows/backend-ci.yml` — CI pipeline gate
- `.github/workflows/pr-gate.yml` — PR merge gate

---

## Format Pass Summary

| Metric | Value |
|--------|-------|
| Total Python files scanned | 235 |
| Files actually reformatted | ~130 (whitespace / trailing comma / blank-line normalization) |
| Files already conformant | ~105 |
| Logic changes | **0** |
| Import changes | **0** |
| Test logic changes | **0** |

Tool: `ruff format` v0.15.12
Config: `ruff.toml` — `select=["E4","E7","E9","F"]`, excludes `.venv` and `alembic/versions`

---

## Gates Added

### `backend/scripts/verify_backend.py`

New check step inserted as `[2b/5]` between lint and DB:

```python
def check_ruff_format() -> Check:
    """Run ruff format --check . and return pass/fail (BACKEND-QA-BASELINE-03)."""
    cmd = [sys.executable, "-m", "ruff", "format", "--check", "."]
    result = subprocess.run(cmd, capture_output=True, text=True)
    ...
```

Banner updated to `BACKEND-QA-BASELINE-03`.

### `.github/workflows/backend-ci.yml`

New step after lint:

```yaml
- name: Backend format check (ruff format --check)
  run: cd backend && python -m ruff format --check .
```

### `.github/workflows/pr-gate.yml`

New step after lint:

```yaml
- name: Backend format check (ruff format --check)
  run: if [ -d backend ]; then cd backend && python -m ruff format --check . ; fi
```

---

## Verification Results

### `verify_backend.py --testenv-only`

```
[PASS] Backend import (app.main)
[PASS] Ruff lint (ruff check .)
[PASS] Ruff format (ruff format --check .)
[PASS] DB connectivity (postgresql+psycopg://mes:***@localhost:5432/mes)
[PASS] Testenv safety + connectivity contract

OK: testenv-only checks passed.
```

Exit code: 0 ✅

### `ruff format --check .`

```
235 files already formatted
```

Exit code: 0 ✅

### `ruff check .`

```
All checks passed!
```

Exit code: 0 ✅

---

## Test Baseline (Pre vs Post Format)

| Suite | Passed | Skipped | Failed |
|-------|--------|---------|--------|
| Pre-format (stable) | 818 | 4 | 1 |
| Post-format (stable) | 819 | 4 | 1 |

Delta: +1 passed — from conftest formatting or test discovery order change.
No regressions introduced.

**Known pre-existing failure (not in scope):**
- `test_user_lifecycle_status.py::test_user_status_migration_does_not_touch_unrelated_tables`
- Cause: `UnicodeDecodeError: 'cp932'` — Windows-only encoding issue when reading
  alembic migration files. Tracked as **BACKEND-QA-WINDOWS-ENCODING-01**.

---

## Working-Tree Classification

After format, the working tree contains the following categories:

| Category | Files | Notes |
|----------|-------|-------|
| `M backend/**` (ruff format) | ~130 | Whitespace-only. All files included in this commit. |
| `M backend/scripts/verify_backend.py` | 1 | Gate update — part of this commit. |
| `M .github/workflows/backend-ci.yml` | 1 | Gate update — part of this commit. |
| `M .github/workflows/pr-gate.yml` | 1 | Gate update — part of this commit. |
| `M frontend/tsconfig.json` | 1 | Real content change (types field removed). **NOT** part of this commit — frontend slice. |
| `M frontend/src/...` | 4 | CRLF-only changes. **NOT** part of this commit. |
| `?? CLAUDE.md` | 1 | Human-owned note. Leave untracked. |
| `?? backend/tests/test_approval_rule_scope_aware_matching.py` | 1 | P0-A-15B test — formatted, separate commit. |
| `?? backend/tests/test_reason_code_allowed_actions_13b.py` | 1 | New test slice — formatted, separate commit. |
| `?? docs/audit/p0-a-15b-01-...md` | 1 | Separate slice audit doc. |

---

## CRLF Stability Note

On Windows, `ruff format` writes LF line endings. Git's `core.autocrlf` may
convert files back to CRLF on checkout, causing `ruff format --check .` to
report failures in subsequent runs.

**Mitigation options (deferred, tracked as BACKEND-QA-CRLF-STABILITY-01):**

1. Add `.gitattributes` with `*.py text eol=lf` to enforce LF for Python files
2. OR: set `git config core.autocrlf false` in the developer environment

Until this is resolved, developers on Windows should run `ruff format .` before
committing to normalize line endings.

---

## Suggested Commit Commands

```bash
# Stage all backend format changes + CI/verify gate updates
git add backend/
git add .github/workflows/backend-ci.yml
git add .github/workflows/pr-gate.yml
git add docs/audit/backend-qa-baseline-03-ruff-format-baseline.md

git commit -m "chore(backend): BACKEND-QA-BASELINE-03 apply ruff format mechanical baseline + format gate"
```

> Note: Do NOT stage `frontend/tsconfig.json`, `CLAUDE.md`, or the new untracked
> test files in this commit.

---

## Next Steps

| Task | ID | Notes |
|------|----|-------|
| Fix Windows cp932 encoding failure | BACKEND-QA-WINDOWS-ENCODING-01 | test_user_lifecycle_status.py |
| Add .gitattributes for LF enforcement | BACKEND-QA-CRLF-STABILITY-01 | Prevents format regression on checkout |
| Commit P0-A-15B tests | P0-A-15B-COMMIT | test_approval_rule_scope_aware_matching.py |
| Commit reason code 13B tests | 13B-COMMIT | test_reason_code_allowed_actions_13b.py |
| Fix frontend tsconfig.json | FE-TSCONFIG-01 | Removed `"types": ["vite/client"]` needs review |
