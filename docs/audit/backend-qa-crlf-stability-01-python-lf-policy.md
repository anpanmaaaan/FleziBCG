# BACKEND-QA-CRLF-STABILITY-01 — Python LF Line Ending Policy / Windows Format Stability

**Date:** 2026-05-06
**Scope:** `.gitattributes` — repository root policy file
**Type:** Repository hygiene / Windows platform stability
**Status:** COMPLETE ✅

---

## Summary

Extended `.gitattributes` with explicit `eol=lf` rules for Python, TOML, YAML,
INI, shell, and text files. No backend test failures introduced. Full suite
remains 856 passed, 4 skipped, 0 failed. No mass renormalization triggered.

---

## Root Cause / Motivation

Three consecutive post-BASELINE-03 slices observed recurring CRLF instability on
Windows:

| Slice | Symptom |
|-------|---------|
| BACKEND-QA-BASELINE-03 | `products.py` reverted to CRLF after commit; format check failed on next run |
| BACKEND-QA-WINDOWS-ENCODING-01 | `products.py` + `reason_codes.py` were CRLF again before suite run |
| BACKEND-QA-RBAC-CODES-FMT-01 | `products.py` CRLF caused intermittent substring-match failure |

**Root mechanism:**

1. Files are committed with LF (from `ruff format .` which writes LF).
2. On Windows, git's `core.autocrlf=true` converts LF → CRLF on checkout.
3. The existing `.gitattributes` had only `* text=auto` (let git decide) and
   `*.md text eol=lf`. There was no explicit override for `*.py`.
4. After any `git` operation (merge, cherry-pick, rebase, new clone), Python files
   were checked out as CRLF, causing `ruff format --check .` to see "files would be
   reformatted" before any code was written.

**Fix:** Explicit `*.py text eol=lf` in `.gitattributes` forces LF on Python files
regardless of `core.autocrlf`, on all platforms. This is the standard practice for
Python repos targeting cross-platform CI.

---

## .gitattributes Decision

### Before

```
* text=auto
*.md text eol=lf
```

### After

```
* text=auto

# Backend formatting stability — BACKEND-QA-CRLF-STABILITY-01
# Enforce LF for all source/config files to prevent ruff format churn on Windows.
*.py   text eol=lf
*.toml text eol=lf
*.yml  text eol=lf
*.yaml text eol=lf
*.md   text eol=lf
*.ini  text eol=lf
*.cfg  text eol=lf
*.txt  text eol=lf
*.sh   text eol=lf
```

**Why these extensions:**

| Extension | Reason |
|-----------|--------|
| `*.py` | Primary target — prevents ruff format CRLF churn |
| `*.toml` | `ruff.toml`, `pyproject.toml` — ruff reads these |
| `*.yml` / `*.yaml` | CI workflow files — consistent line endings |
| `*.md` | Already in policy, kept |
| `*.ini` | `alembic.ini` — Alembic configuration |
| `*.cfg` | Config files |
| `*.txt` | `requirements.txt` |
| `*.sh` | Shell scripts — must be LF to execute on Linux |

**What was NOT added:**

- No rule for `*.ts`, `*.tsx`, `*.json` — frontend files are managed separately
- No binary file rules — not needed
- No `*.env` or `Dockerfile` — these are not Python-toolchain-adjacent

### Renormalization impact

Adding these rules did **not** cause mass renormalization. `git status --short`
after the `.gitattributes` change showed the same 5 files as before:

```
 M .gitattributes
 M backend/app/api/v1/products.py          (pre-existing CRLF revert)
 M backend/tests/test_reason_code_allowed_actions_13b.py  (pre-existing)
 M backend/tests/test_scope_rbac_foundation_alignment.py  (pre-existing)
 M frontend/tsconfig.json                  (user decision: leave)
?? CLAUDE.md                               (untracked: leave)
```

No Python files were newly marked as dirty. The stop condition was not triggered.

**Note on residual CRLF working copies:**

The pre-existing `M` backend files (`products.py`, etc.) are CRLF-reverted copies
of already-committed LF files. These will normalize to LF on next checkout after
this `.gitattributes` commit lands. They do not need to be force-staged now.
`git add --renormalize backend/` can be run as a follow-up cleanup after merge
if desired, but is not required for the QA baseline to function.

---

## Changes Made

### `.gitattributes`

Extended with 8 new `eol=lf` rules. The existing `* text=auto` and `*.md text eol=lf`
are preserved (deduplication: `*.md` now covered by explicit rule, old line replaced).

---

## Files Changed

| File | Change |
|------|--------|
| `.gitattributes` | Added `*.py`, `*.toml`, `*.yml`, `*.yaml`, `*.ini`, `*.cfg`, `*.txt`, `*.sh` `text eol=lf` rules |

---

## Verification Results

### git status after .gitattributes change

No mass renormalization. Only `.gitattributes` added to dirty set. ✅

### `ruff format --check .`

```
236 files already formatted
```
Exit 0 ✅

### `ruff check .`

```
All checks passed!
```
Exit 0 ✅

### `verify_backend.py --testenv-only`

```
[PASS] Backend import (app.main)
[PASS] Ruff lint (ruff check .)
[PASS] Ruff format (ruff format --check .)
[PASS] DB connectivity (postgresql+psycopg://mes:***@localhost:5432/mes)
[PASS] Testenv safety + connectivity contract

OK: testenv-only checks passed.
```
Exit 0 ✅

### Full backend suite

```
856 passed, 4 skipped, 1 warning in 104.52s
EXIT=0
```
✅ **Zero failures. Baseline unchanged.**

---

## Scope Compliance

| Constraint | Status |
|-----------|--------|
| No production business logic changed | ✅ `.gitattributes` only |
| No backend domain code changed | ✅ Confirmed |
| No frontend changed | ✅ Confirmed — no frontend extensions added |
| No tests skipped/xfail-added | ✅ Confirmed |
| Unrelated residual files not staged | ✅ Confirmed |

---

## Backend QA Baseline Status

### Post BACKEND-QA-CRLF-STABILITY-01

| Check | Status |
|-------|--------|
| `ruff format --check .` | ✅ PASS (236 files) |
| `ruff check .` | ✅ PASS |
| `verify_backend.py --testenv-only` | ✅ 5/5 PASS |
| Full suite | ✅ **856 passed, 4 skipped, 0 failed** |
| Windows CRLF stability | ✅ Policy enforced |

### BACKEND-QA slice completion

| Slice | Status |
|-------|--------|
| BACKEND-QA-BASELINE-03 | ✅ Ruff format baseline applied |
| BACKEND-QA-WINDOWS-ENCODING-01 | ✅ cp932 encoding fix |
| BACKEND-QA-RBAC-CODES-FMT-01 | ✅ Format-agnostic governance test |
| BACKEND-QA-CRLF-STABILITY-01 | ✅ LF policy enforced |

**The BACKEND-QA stabilization series is complete.**

---

## Recommended Next Slice

The backend QA baseline is fully green and stable. Options for next work:

1. **BACKEND-QA-RENORMALIZE-01** *(optional cleanup)* — Run
   `git add --renormalize backend/` to normalize the pre-existing CRLF-reverted
   working copies into a clean committed state. Low risk, purely cosmetic.

2. **Pyright type-checking discovery** — Backend QA baseline is now a clean
   starting point for adding static type checking.

3. **Commit pending untracked test slices** — `test_approval_rule_scope_aware_matching.py`,
   `test_reason_code_allowed_actions_13b.py` each need their own slice.

4. **Frontend tsconfig.json** — The real content change (`"types": ["vite/client"]`
   removed) needs a frontend slice review.

---

## Suggested Commit Commands

```bash
git add .gitattributes

git commit -m "chore(repo): BACKEND-QA-CRLF-STABILITY-01 enforce eol=lf for py/toml/yml/sh files"
```

> Do NOT stage `frontend/tsconfig.json`, `CLAUDE.md`, or any untracked backend
> test files in this commit.
