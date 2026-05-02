# P0-A-02C: Strict Tenant Existence Enforcement

**Slice:** P0-A-02C
**Date:** 2026-05-02
**Verdict:** `ALLOW_P0A02C_STRICT_TENANT_EXISTENCE_ENFORCEMENT` → IMPLEMENTED

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Strict / Auth-context hardening
- **Hard Mode MOM:** v3 ON
- **Reason:** Touches tenant lifecycle governance, auth/request security boundary, multi-tenant isolation, IAM lifecycle, CI foundation gate

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Evidence | Source |
|---|---|
| Policy B (missing row → allow) was implemented in P0-A-02B | `p0-a-02b-tenant-lifecycle-enforcement-report.md` |
| `is_tenant_lifecycle_active()` in `tenant_repository.py` returns True for missing rows | Inspected source |
| `require_authenticated_identity` calls `is_tenant_lifecycle_active` after session check | `dependencies.py` lines 104–108 |
| Tests that rely on Policy B behavior (missing-row → allow): 4 tests across 3 files | Inspected sources |
| No existing test creates a Tenant row for the "default"/"tenant_a" strings in tenant foundation / authorization tests | Confirmed by inspection |
| `test_qa_foundation_authorization.py` uses `_DummyDb` (no `scalar` method) — would fail with AttributeError under strict enforcement without monkeypatch | Inspected source |

### Current Transitional Enforcement Map

| Area | Current (Policy B) | Target (Policy A) | Change Needed |
|---|---|---|---|
| Missing tenant row | Allow (return True) | Reject (return False → 403) | Yes |
| Active tenant (ACTIVE + is_active=True) | Allow | Allow | No change |
| DISABLED tenant | Reject (403) | Reject (403) | No change |
| SUSPENDED tenant | Reject (403) | Reject (403) | No change |
| Inactive tenant (is_active=False) | Reject (403) | Reject (403) | No change |
| Tenant header mismatch | Reject (403) | Reject (403) | No change |

### Tenant Seed / Fixture Source Map

| Test / Source Area | Requires Tenant Row? | Existing Override? | Action Taken |
|---|---|---|---|
| `test_tenant_lifecycle_enforcement.py::test_missing_tenant_row_*` | Yes (via `_make_factory()`) | `_get_security_db` overridden | Renamed + assertion flipped to 403 |
| `test_tenant_foundation.py::allows_missing_tenant_header` | No (was Policy B passthrough) | None | Added `is_tenant_lifecycle_active` monkeypatch |
| `test_tenant_foundation.py::rejects_tenant_header_mismatch` | No (fails at header check first) | None | Added `is_tenant_lifecycle_active` monkeypatch for defense-in-depth |
| `test_qa_foundation_authorization.py::missing_action/action_present` | No (uses `_DummyDb`, would AttributeError) | `_get_security_db` → `_DummyDb` | Added `is_tenant_lifecycle_active` monkeypatch |
| All other tests (override `require_authenticated_identity` entirely) | Not reached | Bypassed completely | No change needed |

### Strict Enforcement Decision

- Missing Tenant row → `is_tenant_lifecycle_active` returns `False` → 403 "Tenant is not active"
- Status code/message: same as DISABLED/SUSPENDED (403 "Tenant is not active") — consistent with existing convention
- This is now safe because all tests that relied on missing-row Policy B are updated with explicit monkeypatches or in-memory Tenant rows
- No production seed/backfill was added — this is intentional; production operators must create Tenant rows before onboarding (future Tenant Admin API slice)
- No auto-seed at app startup was added

### Backward Compatibility Decision

- Policy B (missing row → allow) is fully retired
- Tests updated to monkeypatch `is_tenant_lifecycle_active` where they test behavior unrelated to tenant lifecycle (e.g., header mismatch, action guard, missing action)
- **Production implication:** any existing deployment using string tenant_id without a corresponding Tenant row will reject authenticated requests. Operational follow-up: create Tenant rows via direct DB seed before cutover to production.

---

## Invariant Map

| Invariant | Evidence | Test |
|---|---|---|
| Missing Tenant row rejects | `is_tenant_lifecycle_active` returns False → 403 | `test_missing_tenant_row_rejected` |
| Active Tenant allows | `tenant.is_lifecycle_active` True → allow | `test_active_tenant_request_context_allowed` |
| Disabled Tenant rejects | `lifecycle_status=DISABLED` → 403 | `test_disabled_tenant_request_context_rejected` |
| Suspended Tenant rejects | `lifecycle_status=SUSPENDED` → 403 | `test_suspended_tenant_request_context_rejected` |
| Inactive Tenant rejects | `is_active=False` → 403 | `test_inactive_tenant_request_context_rejected` |
| Tenant header mismatch rejects | `_assert_tenant_header_matches_identity` before lifecycle | `test_tenant_header_mismatch_still_rejected` |
| Unauthenticated request rejects | No `auth_identity` → 401 | `test_unauthenticated_request_still_rejected` |
| No FK retrofit added | No migration, no schema change | Source inspection |
| No production auto-seed | No app startup seed | Source inspection |
| No API endpoints added | No new routes | Source inspection |

---

## Files Inspected

- `backend/app/repositories/tenant_repository.py`
- `backend/app/security/dependencies.py`
- `backend/tests/test_tenant_lifecycle_enforcement.py`
- `backend/tests/test_tenant_foundation.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_auth_refresh_token_runtime.py`
- `backend/tests/test_auth_session_api_alignment.py`
- `.github/workflows/pr-gate.yml`
- `.github/workflows/backend-ci.yml`

---

## Files Changed

| File | Change |
|---|---|
| `backend/app/repositories/tenant_repository.py` | `is_tenant_lifecycle_active`: remove Policy B, missing row returns False |
| `backend/app/security/dependencies.py` | Comment updated: Policy A annotation |
| `backend/tests/test_tenant_lifecycle_enforcement.py` | Module docstring updated; `test_missing_tenant_row_policy_b_allows` → `test_missing_tenant_row_rejected` (403); `test_is_active_false_request_context_rejected` → `test_inactive_tenant_request_context_rejected` |
| `backend/tests/test_tenant_foundation.py` | Added `is_tenant_lifecycle_active` monkeypatch to `rejects_tenant_header_mismatch` and `allows_missing_tenant_header` |
| `backend/tests/test_qa_foundation_authorization.py` | Added `is_tenant_lifecycle_active` monkeypatch to `test_missing_required_action_returns_403` and `test_action_guard_allows_request_when_action_present` |

---

## Tests Added / Updated

| Test | File | Change |
|---|---|---|
| `test_missing_tenant_row_rejected` | `test_tenant_lifecycle_enforcement.py` | Renamed; now expects 403 (was 200 Policy B) |
| `test_inactive_tenant_request_context_rejected` | `test_tenant_lifecycle_enforcement.py` | Renamed from `test_is_active_false_request_context_rejected` |
| `test_require_authenticated_identity_allows_missing_tenant_header` | `test_tenant_foundation.py` | Added `is_tenant_lifecycle_active` monkeypatch |
| `test_require_authenticated_identity_rejects_tenant_header_mismatch` | `test_tenant_foundation.py` | Added `is_tenant_lifecycle_active` monkeypatch (defense-in-depth) |
| `test_missing_required_action_returns_403` | `test_qa_foundation_authorization.py` | Added `is_tenant_lifecycle_active` monkeypatch |
| `test_action_guard_allows_request_when_action_present` | `test_qa_foundation_authorization.py` | Added `is_tenant_lifecycle_active` monkeypatch |

---

## CI Gate Changes

None — no new test files were added. All changes are within existing test files already referenced in the CI targeted lists.

---

## Verification Commands Run

```
# Enforcement tests alone
python -m pytest tests/test_tenant_lifecycle_enforcement.py -q --tb=short
→ 7 passed, 1 warning

# Tenant + auth + QA authorization regression
python -m pytest tests/test_tenant_foundation.py tests/test_tenant_lifecycle_enforcement.py tests/test_tenant_lifecycle_anchor.py tests/test_alembic_baseline.py tests/test_auth_session_api_alignment.py tests/test_auth_refresh_token_runtime.py tests/test_refresh_token_foundation.py tests/test_refresh_token_rotation.py tests/test_qa_foundation_authorization.py -q --tb=short
→ 85 passed, 1 skipped (Postgres-live), 1 warning

# Full pr-gate targeted list
python -m pytest -q tests/test_cors_policy.py tests/test_alembic_baseline.py tests/test_init_db_bootstrap_guard.py tests/test_auth_session_api_alignment.py tests/test_tenant_foundation.py tests/test_user_lifecycle_status.py tests/test_user_lifecycle_service.py tests/test_access_service.py tests/test_security_event_service.py tests/test_session_service_security_events.py tests/test_auth_security_event_routes.py tests/test_admin_audit_security_events.py tests/test_downtime_reason_admin_routes.py tests/test_security_events_endpoint.py tests/test_refresh_token_foundation.py tests/test_refresh_token_rotation.py tests/test_plant_hierarchy_orm_foundation.py tests/test_tenant_lifecycle_anchor.py tests/test_tenant_lifecycle_enforcement.py tests/test_pr_gate_workflow_config.py --tb=short
→ 132 passed, 1 skipped (Postgres-live), 1 warning
```

---

## Existing Gaps / Known Debts

| Gap | Notes |
|---|---|
| Production deployments with no Tenant rows will reject all authenticated requests | Operational follow-up required before production cutover: create Tenant row(s) via direct seed or future Tenant Admin API |
| No Tenant Admin API exists to create/manage Tenant rows | Out of scope for P0-A; future slice |
| Dev seed (`auth_default_users_json`) creates user with `tenant_id="default"` but no Tenant row | Tests that exercise the full stack against a seeded Postgres would need a Tenant row for "default" in their seed scripts |
| `test_station_queue_session_aware_migration.py` pre-existing failure | Unrelated to P0-A-02C; excluded from all gates |

---

## Scope Compliance

- ✅ No Tenant CRUD API added
- ✅ No Tenant Admin UI added
- ✅ No FK retrofit
- ✅ No schema migration added
- ✅ No production auto-seed at app startup
- ✅ No frontend changes
- ✅ No refresh-token API response shape changes
- ✅ No MMD/Execution/Quality/Material changes
- ✅ No Plant hierarchy changes
- ✅ Minimal surgical changes only

---

## Risks

| Risk | Mitigation |
|---|---|
| Production DB has no Tenant rows — all auth requests would 403 | Document as operational requirement; add Tenant row before deploying strict enforcement to production |
| New tests added in future that call `require_authenticated_identity` without `_get_security_db` override | Pattern established: monkeypatch `is_tenant_lifecycle_active` in tests focused on non-tenant behavior |
| CI gate runs broad `python -m pytest -q` as fallback if targeted list fails | `test_qa_foundation_authorization.py` was fixed — should not block fallback run |

---

## Recommended Next Slice

**Tenant Seed / Bootstrap for Dev + CI**

Prerequisites met now (strict enforcement is live). Next:
1. Create a `seed_default_tenant()` function in `backend/scripts/seed/` or `backend/app/db/init_db.py` that creates the `"default"` tenant row idempotently
2. Add it to the CI Postgres seed step in `backend-ci.yml` so live DB tests work without Postgres-level tenant setup
3. Update `scripts/seed/seed_demo_data.py` (if exists) to create default tenant row

This unblocks future integration tests that need authenticated requests against a real Postgres DB.

---

## Stop Conditions Hit

None.
