# P0-A-CI-01 — Backend CI / Alembic Migration Gate
## Audit Report

**Slice:** P0-A-CI-01  
**Date:** 2026-05-02  
**Status:** COMPLETE  
**Verdict:** `P0_A_CI_01_ALEMBIC_GATE_IMPLEMENTED`

---

## 1. Routing

```
Selected brain: flezibcg-ai-brain-v6-auto-execution
Selected mode: Hard Execute
Hard Mode MOM: v3 — CI workflow touches migration, alembic, db, schema paths (MOM_CRITICAL=true, DB_OR_MIGRATION=true in pr-gate classification)
Reason: Adding Postgres service and Alembic gate to CI is a DB/migration-adjacent change. HMM v3 required for evidence-first execution.
```

---

## 2. Design Evidence Extract

| Evidence | Source | Verdict |
|---|---|---|
| DB URL built from `postgres_user/password/host/port/db` env vars | `backend/app/config/settings.py` | CI must set these or `DATABASE_URL` directly |
| `database_url` field overrides the builder if non-null | `set_database_url` validator | Setting `DATABASE_URL` env var is sufficient |
| `alembic.ini` does NOT hardcode `sqlalchemy.url` | `backend/alembic.ini` | DB URL comes exclusively from `app.config.settings` |
| `env.py` reads URL from `app.db.session.engine` | `backend/alembic/env.py` | `DATABASE_URL` env var flows into engine correctly |
| Existing `pr-gate.yml` backend-tests job: no Postgres service | `.github/workflows/pr-gate.yml` | DB-dependent tests skip in pr-gate CI |
| `requirements.txt` includes `psycopg`, `psycopg-binary`, `alembic`, `pytest` | `backend/requirements.txt` | No new runtime dependencies required |
| Migration chain: linear, single head at `0005` | Alembic versions dir | Single head confirmed |

---

## 3. HMM v3 Gate

### Invariant Map

| Invariant | Enforcement |
|---|---|
| Never hardcode production DB credentials in CI | CI uses throwaway credentials (`flezibcg_ci/flezibcg_ci`) scoped to ephemeral container |
| Migration chain must be single linear head | `alembic heads` check gates the build — fails if HEAD_COUNT != 1 |
| `alembic upgrade head` must succeed on clean DB | Runs against disposable Postgres before any tests |
| `test_station_queue_session_aware_migration.py` is a pre-existing failure | Excluded from P0-A gate — not fixed in this slice |
| No backend app code modifications | Zero app code changed in this slice |
| No new migrations | Zero new migration files added |

### State Transition Map

N/A — no execution state machine involved.

### Event Map

N/A — no domain events involved.

### Test Matrix (see §6 for results)

| Test | Coverage | Notes |
|---|---|---|
| `test_alembic_baseline.py` | Alembic head assertion; live upgrade if Postgres reachable | head=0005; live test skips without Postgres |
| `test_qa_foundation_migration_smoke.py` | Migration SQL smoke | SQLite-based |
| `test_init_db_bootstrap_guard.py` | Bootstrap guard | SQLite-based |
| `test_refresh_token_foundation.py` | Refresh token ORM | SQLite-based |
| `test_refresh_token_rotation.py` | Rotation logic | SQLite-based |
| `test_auth_refresh_token_runtime.py` | Auth runtime | SQLite-based |
| `test_auth_session_api_alignment.py` | Session API contract | SQLite-based |
| `test_user_lifecycle_status.py` | Lifecycle ORM fields | SQLite-based |
| `test_user_lifecycle_service.py` | Lifecycle service | SQLite-based |
| `test_plant_hierarchy_orm_foundation.py` | 5-model hierarchy ORM | SQLite-based |
| `test_security_event_service.py` | Security event service | SQLite-based |
| `test_security_events_endpoint.py` | Security events endpoint | SQLite-based |
| `test_cors_policy.py` | CORS allow-list | App-level |
| `test_pr_gate_workflow_config.py` | Workflow YAML content assertions | File-level |

### Verdict before coding

`PROCEED` — all evidence present; no backend app code changes; no new migrations; credentials CI-only throwaway; single head confirmed; excluded test documented.

---

## 4. Changes Made

### Created: `.github/workflows/backend-ci.yml`

New dedicated backend CI workflow with:

- **Trigger:** `push` and `pull_request` to `main`/`develop`; path-filtered to `backend/**` and self
- **Postgres service:** `postgres:16`; CI-only credentials (`flezibcg_ci`/`flezibcg_ci`/`flezibcg_test`); health check via `pg_isready`
- **`DATABASE_URL` env var:** `postgresql+psycopg://flezibcg_ci:flezibcg_ci@localhost:5432/flezibcg_test` — inherited by all steps
- **Python 3.12** with `pip` cache on `backend/requirements.txt`
- **Install:** `pip install -r backend/requirements.txt` (no new deps)
- **Backend import check:** `python -c "import app.main; print('import ok')"` (consistent with pr-gate)
- **Alembic single linear head check:** `alembic heads | grep -c "(head)"` — fails build if != 1
- **Alembic upgrade to head:** `alembic upgrade head` against disposable Postgres
- **Alembic current verification:** logs `alembic current` for traceability
- **P0-A foundation test suite:** 14 test files in 7 named steps
- **CI gate summary:** written to `$GITHUB_STEP_SUMMARY`
- **Excluded test documented in comments:** `test_station_queue_session_aware_migration.py`

### Modified: `.github/workflows/pr-gate.yml`

Extended `backend-tests` job targeted test list to include missing P0-A tests:

- Added: `tests/test_user_lifecycle_status.py`
- Added: `tests/test_refresh_token_foundation.py`
- Added: `tests/test_refresh_token_rotation.py`
- Added: `tests/test_plant_hierarchy_orm_foundation.py`

No other changes to `pr-gate.yml`. All content assertions in `test_pr_gate_workflow_config.py` continue to pass.

---

## 5. Design Decisions

| Decision | Rationale |
|---|---|
| New `backend-ci.yml` rather than extending `pr-gate.yml` | `pr-gate.yml` mixes change classification logic with test execution; adding a Postgres service there would add it to a job that's conditionally skipped for docs-only PRs; cleaner separation of concerns |
| CI credentials differ from defaults (`flezibcg_ci` vs `mes`) | Explicit CI-specific identity; avoids accidental confusion with local dev defaults |
| Set `DATABASE_URL` at job level (not per-step) | All steps inherit; `settings.set_database_url()` validator respects it; no per-step override needed |
| `psycopg` (v3) driver in URL | Matches `requirements.txt`; `psycopg-binary` bundled |
| Path filter on `backend/**` | Prevents workflow from running on frontend-only or docs-only changes |
| `alembic heads | grep -c "(head)"` for head count | Portable bash; tolerates extra blank lines; explicit error message on failure |
| `--tb=short` on all pytest steps | Concise failure output in CI logs |
| Steps split by concern (migration smoke, refresh token, lifecycle, hierarchy, security events, CORS/workflow) | Easier to identify which P0-A concern failed in CI |

---

## 6. Local Verification Results

### Run 1 — Alembic baseline + refresh token + plant hierarchy + pr-gate workflow

```
tests/test_alembic_baseline.py
tests/test_refresh_token_foundation.py
tests/test_plant_hierarchy_orm_foundation.py
tests/test_pr_gate_workflow_config.py

50 passed, 1 skipped in 7.50s
```

### Run 2 — Auth runtime + session alignment + user lifecycle + security events + CORS + migration smoke + bootstrap

```
tests/test_auth_refresh_token_runtime.py
tests/test_auth_session_api_alignment.py
tests/test_user_lifecycle_service.py
tests/test_security_event_service.py
tests/test_security_events_endpoint.py
tests/test_cors_policy.py
tests/test_qa_foundation_migration_smoke.py
tests/test_init_db_bootstrap_guard.py

38 passed, 2 skipped, 1 warning in 13.08s
```

**Combined P0-A gate result: 88 passed, 3 skipped, 0 failures**

Note: skips are `test_alembic_upgrade_head_live` (no Postgres in local run) and DB-health-check skips — both are expected and will pass in CI with Postgres service active.

---

## 7. Gaps NOT Fixed in This Slice

| Gap | Status | Next Slice |
|---|---|---|
| `test_station_queue_session_aware_migration.py` pre-existing failure | Excluded, documented | Must be fixed in a dedicated slice with a focused design analysis |
| No lint/type step in CI | Not added (out of scope) | P0-A-CI-02 or lint slice |
| `jwt_secret_key: "change-me"` default | Not changed (out of scope) | P0-A-SEC-01 |
| Tenant table absent | Not addressed | P0-A-02A |
| Plant hierarchy CRUD API absent | Not addressed | Post-baseline P1 |

---

## 8. Next Recommended Slice

**P0-A-02A — Tenant Table / Tenant Lifecycle Anchor**

Per BASELINE-01 report: absence of a tenant table means tenant_id is used as an unconstrained string throughout. P0-A-02A adds the `tenants` ORM model, migration 0006, and foundational tests.
