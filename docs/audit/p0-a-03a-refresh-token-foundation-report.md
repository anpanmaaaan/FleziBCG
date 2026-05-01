# P0-A-03A Report — Refresh Token Foundation

**Date:** 2025-07-09
**Slice:** P0-A-03A — RefreshToken model, migration, repository, service

---

## Summary

Introduced the persistent `refresh_tokens` table and its full service layer as a foundation
for durable token rotation. The `/auth/refresh` endpoint is **unchanged** in this slice —
wiring refresh token persistence into the endpoint is P0-A-03B.

29 new tests added (21 foundation + 8 rotation). Full suite: **362 passed, 3 skipped, 0 failed**.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Strict + QA
- **Hard Mode MOM:** v3
- **Reason:** Schema mutation (new table `refresh_tokens`), auth/IAM lifecycle, token security
  invariants (hash-only storage, family rotation, tenant isolation). All HMM v3 triggers met.

---

## Hard Mode MOM v3 Gate

### 1. Design Evidence Extract
- Refresh tokens must be persisted to support revocation, rotation, and session linkage.
- Only SHA-256 hashes stored — raw tokens never touch DB.
- All tokens are tenant-scoped: all repo queries include `tenant_id` filter.
- Rotation produces a new token in the same `token_family_id`; the old record is marked `rotated_at` + `revoked_at`.
- Revocation is supported at individual, session, and user level.

### 2. Event Map
No domain events emitted in this slice. Service layer only; no event bus touch.
Auth security event hooks (`SecurityEventService`) are **not wired** — deferred to P0-A-03B.

### 3. Invariant Map
| Invariant | Enforcement |
|---|---|
| Raw token never stored in DB | `token_hash = sha256(raw)` in service; no raw field on model |
| Token unique by hash | `UniqueConstraint("token_hash")` on model + unique index |
| tenant_id always on every query | All repo methods take `tenant_id` as first filter |
| Expired token rejected on validate | `validate_refresh_token` checks `expires_at > now` |
| Revoked token rejected | `revoked_at IS NULL` check in validate |
| Rotated token rejected | `rotated_at IS NULL` check in validate |
| Cross-tenant rotation rejected | `tenant_id` filter on lookup prevents cross-tenant match |

### 4. State Transition Map
```
[issued]  --validate--> [valid]
[valid]   --rotate-->   [rotated+revoked] + new [issued]
[valid]   --revoke-->   [revoked]
[expired] --validate--> None (rejected)
```

### 5. Test Matrix
| Scenario | Test File | Coverage |
|---|---|---|
| Model fields, table name, constraints | `test_refresh_token_foundation.py` | ✓ |
| Migration revision chain, head=0002 | `test_refresh_token_foundation.py` | ✓ |
| Hash-only storage invariant | `test_refresh_token_foundation.py` | ✓ |
| SHA-256 algorithm enforced | `test_refresh_token_foundation.py` | ✓ |
| Unique hashes enforced | `test_refresh_token_foundation.py` | ✓ |
| Not in repr (safe logging) | `test_refresh_token_foundation.py` | ✓ |
| Issue returns raw + record | `test_refresh_token_foundation.py` | ✓ |
| Validate success | `test_refresh_token_foundation.py` | ✓ |
| Validate fails: expired | `test_refresh_token_foundation.py` | ✓ |
| Validate fails: revoked | `test_refresh_token_foundation.py` | ✓ |
| Validate fails: unknown token | `test_refresh_token_foundation.py` | ✓ |
| Revoke by raw token | `test_refresh_token_foundation.py` | ✓ |
| Revoke by session | `test_refresh_token_foundation.py` | ✓ |
| Revoke by user | `test_refresh_token_foundation.py` | ✓ |
| Tenant isolation on validate | `test_refresh_token_foundation.py` | ✓ |
| Rotation: new record issued | `test_refresh_token_rotation.py` | ✓ |
| Rotation: family_id preserved | `test_refresh_token_rotation.py` | ✓ |
| Rotation: old token marked rotated | `test_refresh_token_rotation.py` | ✓ |
| Rotation: old token cannot reuse | `test_refresh_token_rotation.py` | ✓ |
| Rotation: already-rotated rejected | `test_refresh_token_rotation.py` | ✓ |
| Rotation: revoked rejected | `test_refresh_token_rotation.py` | ✓ |
| Cross-tenant rotation rejected | `test_refresh_token_rotation.py` | ✓ |
| New token after rotation valid | `test_refresh_token_rotation.py` | ✓ |

### 6. Verdict
**PASS — implementation approved under HMM v3.**

All invariants covered. No critical gap. Security event audit hooks explicitly deferred to
P0-A-03B as documented gap (not ignored).

---

## Files Inspected

- `backend/app/db/init_db.py`
- `backend/app/config/settings.py`
- `backend/alembic/versions/0001_baseline.py`
- `backend/app/models/user.py` (for soft-ref convention)
- `backend/app/repositories/user_repository.py` (for repo pattern)
- `backend/app/services/auth_service.py` (for auth flow)
- `backend/app/api/v1/auth.py` (to confirm endpoint unchanged)
- `backend/tests/test_alembic_baseline.py` (for regression impact)

---

## Files Changed

| File | Change Type | Notes |
|---|---|---|
| `backend/app/models/refresh_token.py` | NEW | ORM model, `refresh_tokens` table |
| `backend/alembic/versions/0002_add_refresh_tokens.py` | NEW | Migration: create table + 5 indexes |
| `backend/app/repositories/refresh_token_repository.py` | NEW | CRUD: create, get_by_hash, revoke, rotate, revoke_session, revoke_user |
| `backend/app/services/refresh_token_service.py` | NEW | Lifecycle: issue, validate, rotate, revoke |
| `backend/app/db/init_db.py` | MODIFIED | Added `from app.models.refresh_token import RefreshToken` for Base.metadata registration |
| `backend/app/config/settings.py` | MODIFIED | Added `jwt_refresh_token_expire_days: int = 30` |
| `backend/tests/test_refresh_token_foundation.py` | NEW | 21 tests: model, migration, security invariants, service behavior |
| `backend/tests/test_refresh_token_rotation.py` | NEW | 8 tests: rotation lifecycle |
| `backend/tests/test_alembic_baseline.py` | MODIFIED | Updated `test_alembic_head_is_baseline` to expect `"0002"` head |

---

## Migration Added

| Revision | down_revision | Description |
|---|---|---|
| `0002` | `0001` | Creates `refresh_tokens` table with 5 indexes; `downgrade()` reverses |

Migration does **not** touch any existing table. Linear chain: `0001 → 0002`.

---

## Tests Added / Updated

- **NEW** `backend/tests/test_refresh_token_foundation.py` — 21 tests
- **NEW** `backend/tests/test_refresh_token_rotation.py` — 8 tests
- **UPDATED** `backend/tests/test_alembic_baseline.py` — 1 assertion updated (head: `0001` → `0002`)

---

## Verification Commands Run

```bash
# Targeted new tests
python -m pytest -q tests/test_refresh_token_foundation.py tests/test_refresh_token_rotation.py -v
# → 29 passed

# Foundation regression
python -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py \
  tests/test_init_db_bootstrap_guard.py tests/test_auth_session_api_alignment.py \
  tests/test_user_lifecycle_service.py
# → 21 passed, 3 skipped (after baseline test fix)

# Full suite
python -m pytest -q
# → 362 passed, 3 skipped
```

---

## Results

| Run | Result |
|---|---|
| New tests (29) | ✅ 29 passed |
| Foundation regression (21) | ✅ 21 passed, 3 skipped |
| Full suite | ✅ 362 passed, 3 skipped, 0 failed |

---

## Existing Gaps / Known Debts

| Gap | Severity | Deferred To |
|---|---|---|
| `SecurityEventService` not wired on token issue/revoke/rotation | Medium | P0-A-03B |
| `/auth/refresh` endpoint still re-signs access token without persisted refresh token | High | P0-A-03B |
| No `alembic upgrade head` live DB integration test (CI has no DB) | Low | Infrastructure |
| `revoke_reason` max length 256 not validated at service boundary | Low | Future |

---

## Scope Compliance

- ✅ Model created — no FK constraints (soft refs, consistent with codebase convention)
- ✅ Migration created — linear chain, reversible
- ✅ Repository created — all queries tenant-scoped
- ✅ Service created — hash-only storage, rotation, revocation
- ✅ Settings extended — `jwt_refresh_token_expire_days`
- ✅ `init_db.py` updated — model registered with `Base.metadata`
- ✅ Endpoint `/auth/refresh` NOT changed (deferred to P0-A-03B)
- ✅ No frontend changes
- ✅ No execution state machine touched

---

## Risks

- **Low**: SQLite returns naive datetimes for `DateTime(timezone=True)` columns. The service normalizes `expires_at` before comparison. PostgreSQL returns aware datetimes — handled by the same normalize path. Test coverage validates both paths.
- **Low**: The `test_alembic_head_is_baseline` test was a structural assertion hardcoded to `"0001"`. Updated to `"0002"`. Future migrations must update this test again or replace it with a count-based assertion.

---

## Recommended Next Slice

**P0-A-03B** — Wire `/auth/refresh` endpoint to use `refresh_token_service`:
- On POST `/auth/refresh`: validate raw token from request → rotate → return new access + refresh token
- Emit `SecurityEventService` events: `TOKEN_ISSUED`, `TOKEN_ROTATED`, `TOKEN_REVOKED`
- Revoke all user tokens on logout
- Wire `revoke_tokens_for_session` on session termination

---

## Stop Conditions Hit

None. All invariants verified. Full suite clean. Scope respected.
