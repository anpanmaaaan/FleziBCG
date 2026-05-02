# P0-A-02B: Tenant Lifecycle Enforcement in Auth / Request Context

**Slice:** P0-A-02B
**Date:** 2026-05-02
**Verdict:** `ALLOW_P0A02B_TENANT_LIFECYCLE_ENFORCEMENT` → IMPLEMENTED

---

## 1. Design Evidence Extract

- Tenant ORM model with `lifecycle_status` and `is_active` fields exists (`backend/app/models/tenant.py`) from P0-A-02A.
- `is_lifecycle_active` property: `True` only when `is_active=True` AND `lifecycle_status == "ACTIVE"`.
- `require_authenticated_identity` in `backend/app/security/dependencies.py` is the mandatory gate for all authenticated requests — has `db` (from `_get_security_db`) already available.
- The `tenants` table was created with no backfill (P0-A-02A intent: no FK retrofit). Existing `tenant_id` strings may have no corresponding row.

---

## 2. Invariant Map

| Invariant | Enforcement Point | Status |
|---|---|---|
| DISABLED tenant cannot use authenticated request context | `require_authenticated_identity` | ENFORCED |
| SUSPENDED tenant cannot use authenticated request context | `require_authenticated_identity` | ENFORCED |
| `is_active=False` tenant cannot use authenticated request context | `require_authenticated_identity` | ENFORCED |
| Missing tenant row → allowed (Policy B transitional) | `is_tenant_lifecycle_active()` returns True | DOCUMENTED DEBT → P0-A-02C |
| Header mismatch check runs before lifecycle check | order in `require_authenticated_identity` | PRESERVED |
| Unauthenticated request → 401 | unchanged | PRESERVED |
| Session validity check runs before tenant check | order in `require_authenticated_identity` | PRESERVED |

---

## 3. Policy Decision

**Policy B (transitional) chosen.**

Reason: The `tenants` table starts empty. No existing tenant_id strings (e.g., `"default"`, `"tenant_a"`) have corresponding rows. Strict Policy A would reject all authenticated requests until a seed/backfill creates rows — breaking all existing tests and the running system.

Policy B: if no Tenant row exists → `is_tenant_lifecycle_active()` returns `True` (allow). A row that exists MUST pass `Tenant.is_lifecycle_active`.

**Policy A (strict enforcement) cutover:** P0-A-02C — after seed/fixture creates Tenant rows for all active tenants in dev/CI environments.

---

## 4. Files Changed

| File | Change |
|---|---|
| `backend/app/repositories/tenant_repository.py` | NEW — `get_tenant_by_id`, `is_tenant_lifecycle_active` (Policy B) |
| `backend/app/security/dependencies.py` | MODIFIED — tenant lifecycle check added after session check in `require_authenticated_identity` |
| `backend/tests/test_tenant_lifecycle_enforcement.py` | NEW — 7 tests |
| `.github/workflows/backend-ci.yml` | MODIFIED — added P0-A-02B enforcement step, updated summary |
| `.github/workflows/pr-gate.yml` | MODIFIED — added `test_tenant_lifecycle_enforcement.py` to targeted list |
| `backend/tests/test_tenant_lifecycle_anchor.py` | MODIFIED — `test_alembic_head_is_updated_to_new_revision` updated for migration 0007 (pre-existing staleness) |
| `backend/tests/test_alembic_baseline.py` | MODIFIED — head assertions updated to `0007` (pre-existing staleness — `0007_product_versions.py` exists) |

---

## 5. Test Matrix

| Test | Covers | Result |
|---|---|---|
| `test_active_tenant_request_context_allowed` | ACTIVE + is_active=True → 200 | PASS |
| `test_disabled_tenant_request_context_rejected` | DISABLED → 403 "Tenant is not active" | PASS |
| `test_suspended_tenant_request_context_rejected` | SUSPENDED → 403 "Tenant is not active" | PASS |
| `test_is_active_false_request_context_rejected` | ACTIVE + is_active=False → 403 | PASS |
| `test_missing_tenant_row_policy_b_allows` | No row → 200 (Policy B) | PASS |
| `test_tenant_header_mismatch_still_rejected` | Header mismatch runs before lifecycle check | PASS |
| `test_unauthenticated_request_still_rejected` | No auth_identity → 401 | PASS |

---

## 6. Verification Results

```
tests/test_tenant_lifecycle_enforcement.py: 7 passed (0 failures)

Full regression (82 tests):
  test_tenant_lifecycle_enforcement.py  — 7 pass
  test_tenant_foundation.py             — 3 pass
  test_tenant_lifecycle_anchor.py       — 16 pass
  test_alembic_baseline.py              — 3 pass (1 skip — Postgres-live)
  test_auth_session_api_alignment.py    — pass
  test_refresh_token_foundation.py      — pass
  test_refresh_token_rotation.py        — pass
  test_auth_refresh_token_runtime.py    — pass
Total: 82 passed, 1 skipped (expected), 0 failed
```

---

## 7. Pre-existing Issue Resolved

`test_alembic_head_is_updated_to_new_revision` (in `test_tenant_lifecycle_anchor.py`) and `test_alembic_head_is_baseline` (in `test_alembic_baseline.py`) were asserting Alembic head = `0006`. Migration `0007_product_versions.py` was created by a concurrent slice (P0-B MMD-BE-03), making these assertions stale. Both were updated as a factual correction to unblock CI. The `0007` chain is linear with a single head.

---

## 8. Not in Scope

- No FK retrofit to `tenants` table
- No Admin API or UI for tenant lifecycle management
- No Alembic migration
- No change to refresh token API response shape
- No frontend changes
- No enforcement at token-issuance time (login/refresh endpoints) — deferred to future slice
- `test_station_queue_session_aware_migration.py` pre-existing failure — untouched

---

## 9. Next Recommended Slice

**P0-A-02C — Strict Tenant Existence Enforcement (Policy A Cutover)**

Prerequisites:
1. Create `seed_default_tenant()` helper in `app/db/init_db.py` or a separate seed module
2. Add fixture/seed to create a Tenant row for `"default"` (the demo user tenant)
3. Update relevant test setups that use `require_authenticated_identity` to seed a Tenant row
4. Update `is_tenant_lifecycle_active` to Policy A (no row → reject)
5. Update CI Postgres seed to create default tenant row
