# BACKEND-QA-WINDOWS-ENCODING-01 — User Lifecycle Migration Encoding Stabilization

**Date:** 2026-05-06
**Scope:** `backend/tests/test_user_lifecycle_status.py` — one-line change
**Type:** Test platform compatibility fix (Windows-only encoding stabilization)
**Status:** COMPLETE ✅

---

## Summary

Fixed a Windows-only `UnicodeDecodeError: 'cp932'` in the user lifecycle migration
test by adding an explicit `encoding="utf-8"` to a `Path.read_text()` call. The
migration file is correct UTF-8; the test had no explicit encoding, causing Python
to use the Windows locale default (`cp932`), which cannot decode the UTF-8 byte
sequence for the `→` arrow character in the migration docstring.

---

## Root Cause

**File causing failure:**
`backend/alembic/versions/0004_add_user_lifecycle_status.py`

**Why it fails on Windows:**

The migration file's docstring contains the UTF-8 arrow character `→` (U+2192),
encoded as three bytes `\xe2\x86\x92`. The test read:

```python
source = migration_path.read_text()   # no encoding arg — uses locale default
```

On Windows with a Japanese locale, `locale.getpreferredencoding()` returns `cp932`
(Shift-JIS variant). `cp932` cannot decode the byte `0x92` appearing at position
362 in the file (part of the UTF-8 sequence for `→`):

```
UnicodeDecodeError: 'cp932' codec can't decode byte 0x92 in position 362:
illegal multibyte sequence
```

Python 3.12+ emits a `DeprecationWarning` for `read_text()` without encoding;
Python 3.14 uses `io.text_encoding()` which still falls through to locale.

**This is a Windows platform issue, not a product behavior issue.**

---

## Changes Made

### `backend/tests/test_user_lifecycle_status.py` — line 252

```diff
-    source = migration_path.read_text()
+    source = migration_path.read_text(encoding="utf-8")
```

One line changed. No test intent altered. No migration logic touched. No
auth/tenant/lifecycle behavior touched.

---

## Files Changed

| File | Change |
|------|--------|
| `backend/tests/test_user_lifecycle_status.py` | Added `encoding="utf-8"` to `Path.read_text()` call |

---

## Verification Results

### Failing test — before fix

```
FAILED tests/test_user_lifecycle_status.py::test_user_status_migration_does_not_touch_unrelated_tables
UnicodeDecodeError: 'cp932' codec can't decode byte 0x92 in position 362: illegal multibyte sequence
```

### Failing test — after fix

```
20 passed, 1 warning in 2.44s
EXIT=0
```

### `ruff format --check .`

```
235 files already formatted
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
1 failed, 838 passed, 4 skipped, 1 warning in 88.03s
```

The remaining failure is **pre-existing from BACKEND-QA-BASELINE-03** — not
caused by this fix:

```
FAILED tests/test_mmd_rbac_action_codes.py::test_product_version_write_routes_use_product_version_action_code
```

**Root cause of this failure:** `ruff format` (BACKEND-QA-BASELINE-03) changed
the `@router.post(...)` decorator in `products.py` from a single line to
multi-line format. The governance test uses substring matching and now fails to
find `@router.post("/{product_id}/versions/{version_id}/release"` as a single
contiguous string. This requires a separate governance-test slice.

**Net result of BACKEND-QA-WINDOWS-ENCODING-01:**

| Metric | Before | After |
|--------|--------|-------|
| Test failures | 2 (cp932 + rbac-codes) | 1 (rbac-codes pre-existing) |
| cp932 failure | ❌ FAIL | ✅ PASS |
| test_user_lifecycle_status.py | 19/20 | 20/20 |

---

## Scope Compliance

| Constraint | Status |
|-----------|--------|
| No production business logic changed | ✅ Confirmed |
| No migration semantics changed | ✅ Confirmed — read_text is test-only, migration file unchanged |
| No auth/tenant/scope semantics changed | ✅ Confirmed |
| No frontend changed | ✅ Confirmed |
| No tests skipped/xfail-added | ✅ Confirmed |
| Unrelated residual files not staged | ✅ Confirmed — only test_user_lifecycle_status.py staged |
| test_approval_rule_scope_aware_matching.py not touched | ✅ Confirmed (now committed) |
| test_reason_code_allowed_actions_13b.py not touched | ✅ Confirmed (now committed) |
| frontend/tsconfig.json not touched | ✅ Confirmed |
| CLAUDE.md not touched | ✅ Confirmed |

---

## Remaining Working-Tree Residuals (not staged in this commit)

| File | Category | Notes |
|------|----------|-------|
| `M .github/workflows/backend-ci.yml` | BASELINE-03 ruff format gate | Already in separate slice |
| `M .github/workflows/pr-gate.yml` | BASELINE-03 ruff format gate | Already in separate slice |
| `M backend/app/api/v1/products.py` | CRLF revert | Re-normalizes on next ruff format run |
| `M backend/app/api/v1/reason_codes.py` | CRLF revert | Re-normalizes on next ruff format run |
| `M backend/app/schemas/approval.py` | CRLF revert | Re-normalizes on next ruff format run |
| `M backend/app/schemas/reason_code.py` | CRLF revert | Re-normalizes on next ruff format run |
| `M backend/app/services/approval_service.py` | CRLF revert | Re-normalizes on next ruff format run |
| `M backend/tests/test_pr_gate_workflow_config.py` | CRLF revert | Re-normalizes on next ruff format run |
| `M docs/design/.../manufacturing-master-data-...md` | Design doc edit | Separate design slice |
| `M frontend/**` | Frontend changes | Frontend slice, do not touch |
| `M frontend/tsconfig.json` | Per user decision | Leave as-is |
| `?? CLAUDE.md` | Human-owned note | Leave untracked |
| `?? backend/tests/test_approval_create_governed_context_bridge.py` | New test slice | Separate commit |

---

## Backend QA Baseline Status

| Check | Status |
|-------|--------|
| `ruff format --check .` | ✅ PASS (235 files) |
| `ruff check .` | ✅ PASS |
| `verify_backend.py --testenv-only` | ✅ PASS (5/5) |
| `test_user_lifecycle_status.py` | ✅ 20/20 PASS |
| Full suite | 838 passed, 4 skipped, 1 pre-existing failure |
| Windows cp932 encoding issue | ✅ RESOLVED |

---

## Recommended Next Slice

**BACKEND-QA-RBAC-CODES-FMT-01** — Fix `test_product_version_write_routes_use_product_version_action_code`

The governance test uses exact substring matching on route decorator source. Ruff
format (BACKEND-QA-BASELINE-03) changed the decorator to multi-line. Fix options:

1. **Preferred:** Update the test to check for route path without requiring
   single-line format (e.g., check `"/{product_id}/versions/{version_id}/release"`
   appears in the source, not the full decorator as a single line).
2. **Alternative:** Add a `# fmt: skip` comment to the specific decorators, but
   this weakens the format baseline.

Option 1 is preferred — adjusts the test to be format-agnostic without losing
governance intent.

**Also pending:**

- **BACKEND-QA-CRLF-STABILITY-01** — Add `.gitattributes` `*.py text eol=lf` to
  prevent CRLF reversion on Windows checkout
- Commit `backend/tests/test_approval_create_governed_context_bridge.py` as its
  own governance slice

---

## Suggested Commit Commands

```bash
# Stage ONLY the encoding fix
git add backend/tests/test_user_lifecycle_status.py

git commit -m "fix(test): BACKEND-QA-WINDOWS-ENCODING-01 add encoding=utf-8 to migration read_text"
```

> Do NOT stage CRLF-reverted backend files, frontend files, tsconfig.json,
> CLAUDE.md, or the untracked new test file in this commit.
