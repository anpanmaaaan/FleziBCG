# BACKEND-QA-RBAC-CODES-FMT-01 — Format-Agnostic RBAC Route Action Code Test

**Date:** 2026-05-06
**Scope:** `backend/tests/test_mmd_rbac_action_codes.py` — one function rewritten
**Type:** Test technique hardening (format-agnostic governance assertion)
**Status:** COMPLETE ✅

---

## Summary

Replaced a format-sensitive exact substring check in the RBAC route action-code
governance test with a regex-based check that is robust to single-line vs
multi-line decorator formatting. The governance invariant (all 4 product-version
write routes must use `admin.master_data.product_version.manage`) is fully
preserved. Backend full suite is now **856 passed, 4 skipped, 0 failed**.

---

## Root Cause

### Why it failed

`test_product_version_write_routes_use_product_version_action_code` checked for
exact literal substrings including the opening `(` of the decorator:

```python
'@router.post("/{product_id}/versions/{version_id}/release"'
```

After BACKEND-QA-BASELINE-03 applied `ruff format`, some decorator lines in
`products.py` exceed ruff's 88-character default limit. Ruff can split:

```python
@router.post("/{product_id}/versions/{version_id}/release", response_model=ProductVersionItem)
```

into:

```python
@router.post(
    "/{product_id}/versions/{version_id}/release", response_model=ProductVersionItem
)
```

In the split form, `@router.post("/{product_id}/versions/{version_id}/release"` does
**not** appear as a contiguous substring, breaking the assertion.

### Why it was intermittent

The test `PRODUCTS_SRC` variable is read at module import time. On Windows, git's
`core.autocrlf` converts LF-committed files back to CRLF on checkout. When
`ruff format .` had been run immediately before the test, the file had LF and
single-line decorators. When the CRLF version was on disk at the time of the full
suite run, the file content differed, causing the failure.

### Structural fragility

Even ignoring CRLF, the test was fragile: any ruff version or configuration change
that decides to split long decorator lines would silently break the governance
assertion. The fix makes the assertion format-agnostic.

---

## Design Evidence Extract (Hard Mode MOM v3 — advisory)

No design document change required. The governance invariant being tested is:

> All product-version write routes (`POST /versions`, `PATCH /versions/{id}`,
> `POST /versions/{id}/release`, `POST /versions/{id}/retire`) must use the
> `admin.master_data.product_version.manage` action code, not the parent product
> code or any IAM placeholder.

This invariant is unchanged. The test technique for detecting it is hardened.

---

## Test Strategy

**Option B selected: Regex matching with `\s*` whitespace flexibility**

Pattern:
```python
rf'@router\.{method}\s*\(\s*"{re.escape(path)}"'
```

- `\s*` between `(` and the path string matches both single-line and multi-line formats
- `re.escape(path)` handles any regex metacharacters in the path
- `re` is already imported at the top of the test file — no new dependency

This is the smallest robust option. The regex pattern:
- Matches single-line: `@router.post("/{product_id}/versions/{version_id}/release"`
- Matches multi-line: `@router.post(\n    "/{product_id}/versions/{version_id}/release"`
- Robust to CRLF: `\s*` matches `\r\n    ` correctly

The action-code count assertion (`count >= 4`) is unchanged — it is already
format-agnostic since it counts a string literal value, not a decorator pattern.

---

## Changes Made

### `backend/tests/test_mmd_rbac_action_codes.py`

Replaced `test_product_version_write_routes_use_product_version_action_code`:

```python
# BEFORE — format-sensitive exact substring check
required_markers = [
    '@router.post("/{product_id}/versions"',
    '@router.patch("/{product_id}/versions/{version_id}"',
    '@router.post("/{product_id}/versions/{version_id}/release"',
    '@router.post("/{product_id}/versions/{version_id}/retire"',
]
for marker in required_markers:
    assert marker in PRODUCTS_SRC, (
        f"Missing Product Version write route marker: {marker}"
    )

# AFTER — format-agnostic regex check
required_routes = [
    ("post", r"/{product_id}/versions"),
    ("patch", r"/{product_id}/versions/{version_id}"),
    ("post", r"/{product_id}/versions/{version_id}/release"),
    ("post", r"/{product_id}/versions/{version_id}/retire"),
]
for method, path in required_routes:
    pattern = rf'@router\.{method}\s*\(\s*"{re.escape(path)}"'
    assert re.search(pattern, PRODUCTS_SRC), (
        f"Missing Product Version write route: {method.upper()} {path}"
    )
```

The action-code count assertion is unchanged.

---

## Files Changed

| File | Change |
|------|--------|
| `backend/tests/test_mmd_rbac_action_codes.py` | One test function replaced with format-agnostic regex approach |

---

## Verification Results

### Focused failing test

```
1 passed, 1 warning in 1.25s
EXIT=0
```

### Focused RBAC/action-code suite (4 files)

```
77 passed, 1 warning in 3.60s
EXIT=0
```

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
856 passed, 4 skipped, 1 warning in 104.38s (0:01:44)
EXIT=0
```

**Full backend suite is GREEN. Zero failures.**

---

## Scope Compliance

| Constraint | Status |
|-----------|--------|
| No production route behavior changed | ✅ Confirmed — test-only change |
| No RBAC runtime behavior changed | ✅ Confirmed |
| No action-code values changed | ✅ Confirmed |
| No frontend changed | ✅ Confirmed |
| No tests skipped/xfail-added | ✅ Confirmed |
| Governance assertions preserved | ✅ Confirmed — same 4 routes verified + count ≥ 4 action code assertion |
| Unrelated residual files not staged | ✅ Confirmed |

---

## Backend QA Baseline Status

| Check | Status |
|-------|--------|
| `ruff format --check .` | ✅ PASS (236 files) |
| `ruff check .` | ✅ PASS |
| `verify_backend.py --testenv-only` | ✅ PASS (5/5) |
| Full backend suite | ✅ **856 passed, 4 skipped, 0 failed** |
| Windows cp932 encoding issue (BASELINE-03 residual) | ✅ RESOLVED (prev. slice) |
| RBAC route action-code format sensitivity | ✅ RESOLVED (this slice) |

**Backend QA baseline is now fully green on Windows.**

---

## Recommended Next Slice

**BACKEND-QA-CRLF-STABILITY-01** — Add `.gitattributes` to enforce LF line endings for all Python files:

```
*.py text eol=lf
```

This prevents the recurring CRLF reversion issue on Windows checkout that caused
the intermittent failures in BASELINE-03, WINDOWS-ENCODING-01, and this slice.
Without it, any `git checkout` or merge on Windows may revert LF files to CRLF,
requiring developers to run `ruff format .` before every commit.

---

## Suggested Commit Commands

```bash
# Stage the governance test fix
git add backend/tests/test_mmd_rbac_action_codes.py

git commit -m "fix(test): BACKEND-QA-RBAC-CODES-FMT-01 format-agnostic route action code assertion"
```

> Do NOT stage `frontend/tsconfig.json`, `CLAUDE.md`, or any untracked test files
> in this commit.
