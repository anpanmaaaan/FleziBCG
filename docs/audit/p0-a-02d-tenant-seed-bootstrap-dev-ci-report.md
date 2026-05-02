# P0-A-02D: Tenant Seed / Bootstrap for Dev + CI

**Slice:** P0-A-02D
**Date:** 2026-05-02
**Verdict:** `ALLOW_P0A02D_TENANT_SEED_BOOTSTRAP_DEV_CI` → IMPLEMENTED

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Strict / Tenant bootstrap / Dev + CI runtime readiness
- **Hard Mode MOM:** v3 ON
- **Reason:** Touches tenant lifecycle governance, strict tenant existence enforcement (P0-A-02C), multi-tenant isolation boundary, IAM/auth runtime readiness, CI/dev bootstrap safety

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Evidence | Source |
|---|---|
| P0-A-02C Policy A: missing Tenant row → reject (403) | `p0-a-02c-strict-tenant-existence-enforcement-report.md` |
| `auth_default_users_json` uses `tenant_id="default"` | `backend/app/config/settings.py` line 49 |
| `TENANT_ID = "default"` in seed scripts | `backend/scripts/seed/common.py` line 24 |
| `seed_test_data.py` uses `TENANT_ID = "default"` | `backend/scripts/seed/seed_test_data.py` line 26 |
| `settings.app_env` field exists with default `"dev"` | `backend/app/config/settings.py` line 8 |
| All targeted test files use SQLite in-memory or monkeypatch — CI does NOT need a global seed step for existing tests | Confirmed by inspection of all `_make_db()` and `_make_factory()` patterns |
| `SessionLocal` from `app.db.session` is the established script session pattern | `backend/scripts/seed/seed_all.py`, `seed_test_data.py` |
| Existing scripts live at `backend/scripts/` (standalone Python scripts) | Directory listing |

### Current Strict Tenant Enforcement Map

| Area | Current Behavior | Seed Need? | Decision |
|---|---|---|---|
| `require_authenticated_identity` | Policy A: missing row → 403 | Dev: yes (demo user `tenant_id="default"` needs row) | Seed script resolves |
| `test_tenant_lifecycle_enforcement.py` | Creates own Tenant via `_make_factory()` | No CI seed needed | No change |
| `test_auth_refresh_token_runtime.py` | Uses SQLite in-memory, no `require_authenticated_identity` called directly | No CI seed needed | No change |
| `test_auth_session_api_alignment.py` | Uses SQLite in-memory, monkeypatches session/tenant | No CI seed needed | No change |
| Local dev demo login (`username=demo`, `tenant_id="default"`) | Would 403 without Tenant row after P0-A-02C | Yes — seed script resolves | `seed_default_tenant.py` |
| Future integration tests | May need a real Tenant row against Postgres | Future CI can call seed script | Seed script ready |

### Seed / Bootstrap Source Map

| Source Area | Existing Seed Pattern | Decision |
|---|---|---|
| `backend/scripts/seed/seed_test_data.py` | Standalone Python, imports `SessionLocal`, `TENANT_ID = "default"` | Follow same pattern |
| `backend/scripts/seed/common.py` | `TENANT_ID = "default"`, `SessionLocal` | Confirms canonical tenant ID |
| `backend/app/db/init_db.py` | Has `_apply_sql_migrations()` tagged "DEPRECATED PRODUCTION PATH" — no production auto-seed | Confirms: do NOT add to `init_db` |
| `backend/scripts/` root level | Other standalone scripts (`verify_approval.py`, etc.) | Place seed script here |
| CI `backend-ci.yml` | Runs `alembic upgrade head` then targeted tests | Add seed bootstrap test step ONLY — no global seed run needed |

### Seed Strategy Decision

**Strategy A** chosen: `backend/scripts/seed_default_tenant.py`

- Follows established pattern of standalone Python seed scripts at `backend/scripts/`
- Imports `SessionLocal` from `app.db.session` — same pattern as `seed_test_data.py`
- Core `seed_tenant_row(db, ...)` function is pure and injectable — used directly in tests
- `check_production_guard(app_env, allow_override)` is separately testable
- CLI `__main__` block handles production guard + session management for direct invocation
- Default: `tenant_id="default"`, `tenant_code="DEFAULT"`, `tenant_name="Default Tenant"`
- Env var overrides: `FLEZIBCG_SEED_TENANT_ID`, `FLEZIBCG_SEED_TENANT_CODE`, `FLEZIBCG_SEED_TENANT_NAME`
- Production guard: raises `RuntimeError` when `settings.app_env == "production"` unless `FLEZIBCG_ALLOW_PRODUCTION_SEED=true`
- **No CI global seed step added** — current targeted tests create their own Tenant rows via SQLite in-memory

### Backward Compatibility Decision

- P0-A-02C strict enforcement unchanged — this slice adds no enforcement changes
- `seed_tenant_row` is additive only — no modification to existing code
- Production operators must still explicitly create Tenant rows before deployment
- No production auto-seed is introduced
- No API endpoints are added
- No migration is added

### Invariant Map

| Invariant | Evidence | Test |
|---|---|---|
| Seed creates ACTIVE Tenant row | `seed_tenant_row` sets `lifecycle_status=ACTIVE, is_active=True` | `test_seed_default_tenant_creates_active_tenant` |
| Seed is idempotent | `select` before `add`; update in-place if exists | `test_seed_default_tenant_is_idempotent` |
| Seed updates existing row fields | Upsert logic updates `tenant_code`, `tenant_name`, `lifecycle_status`, `is_active` | `test_seed_default_tenant_updates_existing_row` |
| Seed does not create users/sessions/roles | Only Tenant table exists in test DB; any attempt would raise | `test_seed_default_tenant_does_not_create_users_sessions_or_roles` |
| Env vars override defaults | `_resolve_tenant_values()` reads env vars | `test_seed_default_tenant_uses_custom_env_values_if_supported` |
| Defaults are canonical "default" values | Falls back to `"default"/"DEFAULT"/"Default Tenant"` | `test_seed_default_tenant_uses_defaults_when_env_not_set` |
| Production guard rejects without override | `check_production_guard("production", "")` raises RuntimeError | `test_seed_default_tenant_refuses_production_without_explicit_override` |
| Production guard rejects partial override | `check_production_guard("production", "yes")` raises | `test_seed_default_tenant_refuses_production_with_wrong_override` |
| Production guard allows with `true` | `check_production_guard("production", "true")` passes | `test_seed_default_tenant_allows_production_with_explicit_override` |
| Dev/staging environments not guarded | `check_production_guard("dev"/"test"/"staging", "")` passes | `test_seed_default_tenant_allows_dev_environment` |
| Strict enforcement still rejects missing row | `is_tenant_lifecycle_active` returns False without seed | `test_strict_tenant_enforcement_still_rejects_missing_tenant` |
| Strict enforcement allows seeded row | `is_tenant_lifecycle_active` returns True after seed | `test_strict_tenant_enforcement_allows_seeded_active_tenant` |

### Test Matrix

| Test Area | Test Case | Expected Result | File |
|---|---|---|---|
| Seed correctness | `test_seed_default_tenant_creates_active_tenant` | ACTIVE, is_active=True | `test_tenant_seed_bootstrap.py` |
| Idempotency | `test_seed_default_tenant_is_idempotent` | Exactly 1 row after 2 runs | `test_tenant_seed_bootstrap.py` |
| Upsert | `test_seed_default_tenant_updates_existing_row` | Fields updated on re-seed | `test_tenant_seed_bootstrap.py` |
| Env vars | `test_seed_default_tenant_uses_custom_env_values_if_supported` | Custom values used | `test_tenant_seed_bootstrap.py` |
| Defaults | `test_seed_default_tenant_uses_defaults_when_env_not_set` | "default/DEFAULT/Default Tenant" | `test_tenant_seed_bootstrap.py` |
| No side effects | `test_seed_default_tenant_does_not_create_users_sessions_or_roles` | Only tenants table exists | `test_tenant_seed_bootstrap.py` |
| Production guard — no override | `test_seed_default_tenant_refuses_production_without_explicit_override` | RuntimeError | `test_tenant_seed_bootstrap.py` |
| Production guard — wrong override | `test_seed_default_tenant_refuses_production_with_wrong_override` | RuntimeError | `test_tenant_seed_bootstrap.py` |
| Production guard — correct override | `test_seed_default_tenant_allows_production_with_explicit_override` | No exception | `test_tenant_seed_bootstrap.py` |
| Production guard — dev env | `test_seed_default_tenant_allows_dev_environment` | No exception | `test_tenant_seed_bootstrap.py` |
| Enforcement regression | `test_strict_tenant_enforcement_still_rejects_missing_tenant` | False | `test_tenant_seed_bootstrap.py` |
| Enforcement + seed integration | `test_strict_tenant_enforcement_allows_seeded_active_tenant` | True | `test_tenant_seed_bootstrap.py` |

### Risk / Stop Condition Map

| Risk | Mitigation |
|---|---|
| Accidental production auto-seed | Production guard in CLI path; `seed_tenant_row()` is pure and requires explicit call |
| Wrong tenant ID seeded | Defaults match `auth_default_users_json` (`"default"`); env var override documented |
| CI seed ordering before migration | No global CI seed step added — tests use SQLite in-memory; no ordering issue |
| Duplicate tenant rows | Upsert logic does `select` first; PK on `tenant_id` prevents duplicates at DB level |
| Scope drift into tenant onboarding | Seed only creates Tenant row; no users/roles/sessions/plants |
| Import error in test (script path) | `scripts.seed_default_tenant` is importable from `PYTHONPATH=/mnt/g/Work/FleziBCG/backend` |

---

## Files Inspected

- `backend/app/models/tenant.py`
- `backend/app/repositories/tenant_repository.py`
- `backend/app/config/settings.py`
- `backend/app/db/init_db.py`
- `backend/app/db/session.py`
- `backend/scripts/seed/common.py`
- `backend/scripts/seed/seed_test_data.py`
- `backend/scripts/seed/seed_all.py`
- `backend/tests/test_tenant_lifecycle_enforcement.py`
- `backend/tests/test_tenant_lifecycle_anchor.py`
- `backend/tests/test_tenant_foundation.py`
- `backend/tests/test_auth_refresh_token_runtime.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`
- `docs/audit/p0-a-02c-strict-tenant-existence-enforcement-report.md`

---

## Files Changed

| File | Change |
|---|---|
| `backend/scripts/seed_default_tenant.py` | NEW — idempotent seed script (Strategy A) |
| `backend/tests/test_tenant_seed_bootstrap.py` | NEW — 12 seed tests covering all invariants |
| `.github/workflows/backend-ci.yml` | Added `P0-A tests — tenant seed bootstrap` step; updated CI summary |
| `.github/workflows/pr-gate.yml` | Added `tests/test_tenant_seed_bootstrap.py` to targeted test list |

---

## Tests Added / Updated

| Test | File | Coverage |
|---|---|---|
| `test_seed_default_tenant_creates_active_tenant` | `test_tenant_seed_bootstrap.py` | Seed creates ACTIVE row |
| `test_seed_default_tenant_is_idempotent` | `test_tenant_seed_bootstrap.py` | Exactly 1 row after 2 runs |
| `test_seed_default_tenant_updates_existing_row` | `test_tenant_seed_bootstrap.py` | Upsert updates fields |
| `test_seed_default_tenant_uses_custom_env_values_if_supported` | `test_tenant_seed_bootstrap.py` | Env var overrides |
| `test_seed_default_tenant_uses_defaults_when_env_not_set` | `test_tenant_seed_bootstrap.py` | Default values |
| `test_seed_default_tenant_does_not_create_users_sessions_or_roles` | `test_tenant_seed_bootstrap.py` | No side effects |
| `test_seed_default_tenant_refuses_production_without_explicit_override` | `test_tenant_seed_bootstrap.py` | Production guard |
| `test_seed_default_tenant_refuses_production_with_wrong_override` | `test_tenant_seed_bootstrap.py` | Production guard partial |
| `test_seed_default_tenant_allows_production_with_explicit_override` | `test_tenant_seed_bootstrap.py` | Production override |
| `test_seed_default_tenant_allows_dev_environment` | `test_tenant_seed_bootstrap.py` | Dev/staging unguarded |
| `test_strict_tenant_enforcement_still_rejects_missing_tenant` | `test_tenant_seed_bootstrap.py` | P0-A-02C regression |
| `test_strict_tenant_enforcement_allows_seeded_active_tenant` | `test_tenant_seed_bootstrap.py` | Seed + enforcement integration |

---

## CI Gate Changes

| File | Change |
|---|---|
| `.github/workflows/backend-ci.yml` | Added new step `P0-A tests — tenant seed bootstrap` after enforcement step; updated CI summary text |
| `.github/workflows/pr-gate.yml` | Added `tests/test_tenant_seed_bootstrap.py` to targeted test list |

**CI seed step decision:** No global tenant seed step was added to CI (no `python scripts/seed_default_tenant.py` step). All current targeted tests handle Tenant row creation themselves via SQLite in-memory. The seed script is available for CI to call if future integration tests require a real Postgres Tenant row.

---

## Verification Commands Run

```
# Seed bootstrap tests alone
cd backend
DATABASE_URL=sqlite+pysqlite:///:memory: PYTHONPATH=/mnt/g/Work/FleziBCG/backend \
    python3.12 -m pytest tests/test_tenant_seed_bootstrap.py -q --tb=short
→ 12 passed in 1.98s

# Tenant + enforcement + foundation regression
DATABASE_URL=sqlite+pysqlite:///:memory: PYTHONPATH=/mnt/g/Work/FleziBCG/backend \
    python3.12 -m pytest -q \
    tests/test_tenant_lifecycle_enforcement.py \
    tests/test_tenant_lifecycle_anchor.py \
    tests/test_tenant_foundation.py \
    tests/test_qa_foundation_authorization.py \
    tests/test_auth_session_api_alignment.py \
    tests/test_auth_refresh_token_runtime.py \
    --tb=short
→ 25 passed, 1 warning

# Broader gate including new seed tests + pr-gate config
DATABASE_URL=sqlite+pysqlite:///:memory: PYTHONPATH=/mnt/g/Work/FleziBCG/backend \
    python3.12 -m pytest -q \
    tests/test_tenant_seed_bootstrap.py \
    tests/test_pr_gate_workflow_config.py \
    tests/test_alembic_baseline.py \
    tests/test_tenant_lifecycle_enforcement.py \
    tests/test_tenant_lifecycle_anchor.py \
    tests/test_tenant_foundation.py \
    --tb=short
→ 17 passed, 1 skipped (Postgres-live), 1 warning
```

---

## Results

| Suite | Result |
|---|---|
| `test_tenant_seed_bootstrap.py` | **12 passed** |
| Tenant + auth regression (6 files) | **25 passed** |
| Core gate subset (6 files incl. seed) | **17 passed, 1 skipped** |
| Zero failures | ✅ |

---

## Existing Gaps / Known Debts

| Gap | Notes |
|---|---|
| No Tenant row in live Postgres for demo login | `seed_default_tenant.py` resolves this when run manually (`cd backend; python scripts/seed_default_tenant.py`) |
| CI Postgres job does not run seed script before tests | Not needed for current targeted tests; add CI step when first integration test requires a real Tenant row against Postgres |
| No Tenant Admin API | Out of scope; future slice |
| `FLEZIBCG_SEED_TENANT_ID` / `CODE` / `NAME` not in `.env.example` | Add when `.env.example` is created/updated in a future housekeeping slice |

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
- ✅ No users/sessions/roles created
- ✅ Strict tenant enforcement (P0-A-02C) unchanged

---

## Risks

| Risk | Mitigation |
|---|---|
| Accidental production invocation | Production guard in CLI; `seed_tenant_row()` is pure and requires explicit session injection |
| Wrong tenant ID seeded in dev | `tenant_id="default"` matches `auth_default_users_json` and all seed scripts |
| Test isolation: seed test uses shared SQLite | Each test creates its own `_make_db()` factory — isolated |

---

## Recommended Next Slice

**P0-A-03x or P0-B MMD next slice** — the P0-A tenant foundation is now complete:

- 02A: Tenant table / lifecycle anchor ✅
- 02B: Tenant lifecycle enforcement (Policy B, transitional) ✅
- 02C: Strict tenant existence enforcement (Policy A) ✅
- 02D: Tenant seed / bootstrap for dev + CI ✅

The recommended next move is either:
1. **P0-A housekeeping** — update `.env.example` with seed env vars, update `README.md` with seed instructions
2. **Next P0 slice** — as defined in `docs/roadmap/` or `docs/design/INDEX.md`

---

## Stop Conditions Hit

None.
