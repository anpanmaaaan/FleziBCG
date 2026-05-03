# BACKEND-QA-BASELINE-01 — Backend Green Test Baseline Freeze

**Slice ID:** BACKEND-QA-BASELINE-01  
**Status:** COMPLETE — Baseline Frozen  
**Date:** 2025-07-11  
**Pre-requisite slices:** TECH-DEBT-TESTENV-01, TECH-DEBT-TESTENV-02

---

## 1. Purpose

This document freezes the backend QA baseline after the TESTENV-01 and TESTENV-02 test environment hardening work. It establishes:

- The expected green state of the full backend pytest suite
- A PR gate contract that all future agents must respect
- Recovery procedures for the most common local test environment failure modes
- Tooling availability and lint gate status

---

## 2. Baseline Test Result

**Full backend suite — Run 1:**

```
PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 -m pytest tests/ -q
634 passed, 4 skipped, 2 warnings in 78.48s (0:01:18)
```

**Full backend suite — Run 2:**

```
PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 -m pytest tests/ -q
634 passed, 4 skipped, 2 warnings in 63.51s (0:01:03)
```

**Baseline:** `634 passed, 4 skipped, 0 failures`  
**Stability:** ✅ Stable across both runs  
**Python:** 3.12.3  
**pytest:** 9.0.2  
**psycopg:** 3.3.3  
**SQLAlchemy:** 2.0.48 (sync)

### Known skips (4 total)

| Test | File | Skip reason |
|------|------|-------------|
| `TestPgShowActiveConnections.test_live_connection_count` | `test_testenv_db_safety.py` | `skipif: FLEZIBCG_RUN_LIVE_DB_TEST != 1` |
| `TestCheckTestDbReadinessLive.test_live_connectivity_passes` | `test_testenv_db_connectivity_contract.py` | `skipif: FLEZIBCG_RUN_LIVE_DB_TEST != 1` |
| 2 domain tests | various | Pre-existing skips; no regression |

---

## 3. Verification Commands (Full Checklist)

### 3a. Docker DB health

```bash
# Check DB container is running and port-bound
docker ps | grep db

# Expected (active container from root docker-compose.yml):
# flezibcg-db-1   Up (healthy)   0.0.0.0:5432->5432/tcp

# Check pg_isready inside container
docker exec flezibcg-db-1 pg_isready -U mes -d mes
# Expected: /var/run/postgresql:5432 - accepting connections

# Quick SQL check
docker exec flezibcg-db-1 psql -U mes -d mes -c "SELECT 1;"
# Expected: 1 row
```

> **Note:** Two container names exist depending on which compose file started the DB:
> - `flezibcg-db-1` — started by root `docker-compose.yml` (currently active)
> - `flezi-dev-db` — started by `docker/docker-compose.db.yml` (dev-specific)
>
> `docker compose -f docker/docker-compose.db.yml ps` does **NOT** show `flezibcg-db-1`.
> Use `docker ps` directly to confirm the active container and port binding.

### 3b. Backend import

```bash
cd backend
PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 -c "import app.main; print('import ok')"
# Expected: import ok
```

### 3c. Testenv contract tests

```bash
cd backend
PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 -m pytest \
  tests/test_testenv_db_safety.py \
  tests/test_testenv_db_connectivity_contract.py \
  -q --tb=short
# Expected: 35 passed, 1 skipped
```

### 3d. Full backend suite

```bash
cd backend
PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 -m pytest tests/ -q
# Expected: 634 passed, 4 skipped, 0 failures
```

### 3e. Canonical verification script (new)

```bash
cd backend
PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 scripts/verify_backend.py --testenv-only
# Runs: import → DB → testenv tests (fast, ~10s)

PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 scripts/verify_backend.py
# Runs: import → DB → testenv → full suite (~90s)

PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 scripts/verify_backend.py --full-suite-twice
# Runs: import → DB → testenv → full suite × 2 (~180s)
```

---

## 4. PR Gate Contract

### Tier 1 — Required for ALL backend changes

| Check | Command | Expected |
|-------|---------|----------|
| Backend import | `python3 -c "import app.main; print('import ok')"` | `import ok` |
| Focused tests for changed area | `python3 -m pytest tests/<test_file>.py -q` | 0 failures |
| Git status | `git status --short` | No unintended changes |

### Tier 2 — Required for DB / migration / testenv changes

| Check | Command | Expected |
|-------|---------|----------|
| DB container health | `docker ps \| grep db` | `0.0.0.0:5432->5432` + `(healthy)` |
| pg_isready | `docker exec <container> pg_isready -U mes -d mes` | `accepting connections` |
| Testenv contract | `python3 -m pytest tests/test_testenv_db_safety.py tests/test_testenv_db_connectivity_contract.py -q` | 35 passed, 1 skipped |
| Full suite × 2 | `python3 scripts/verify_backend.py --full-suite-twice` | 634 passed, 4 skipped each run |

### Tier 3 — Required for domain / governance / execution / auth / audit changes

| Check | Required |
|-------|---------|
| Hard Mode MOM v3 Design Evidence Extract | ✅ Mandatory before coding |
| Event Map + Invariant Map | ✅ Mandatory before coding |
| State Transition Map (if stateful) | ✅ Mandatory for stateful work |
| Full backend suite pass | ✅ |
| Test Matrix coverage | ✅ |

---

## 5. Stale DB / Testenv Recovery Contract

### Symptom: `Connection refused` on `psycopg.connect()`

**Root cause:** Docker container exists but port 5432 is not bound to host (common after host restart or `docker start` without compose).

**Diagnosis:**

```bash
docker ps       # Check if flezibcg-db-1 or flezi-dev-db shows 0.0.0.0:5432->5432
docker ps -a    # Check if container exists but is stopped or port-unbound
```

**Fix A — preferred (root compose container active):**

```bash
cd /path/to/FleziBCG
docker compose up -d --force-recreate db
# Then verify:
docker ps | grep db
docker exec flezibcg-db-1 pg_isready -U mes -d mes
```

**Fix B — dev compose only:**

```bash
cd /path/to/FleziBCG
docker compose -f docker/docker-compose.db.yml up -d --force-recreate db
# Then verify:
docker exec flezi-dev-db pg_isready -U mes -d mes
```

**Key principle:** Always verify port binding via `docker ps`, not `docker compose ps`.

### Symptom: `+psycopg` dialect in URL

Already fixed in `backend/tests/conftest.py` via `_to_psycopg_url()`. If psycopg connect fails due to URL format, see TESTENV-02 audit.

### Symptom: DB name warning (`Running tests against a DB that does not look test-specific`)

This is by design. The dev DB is named `mes`, not `mes_test`. To suppress:

```bash
FLEZIBCG_ALLOW_TEST_DB_RESET=1 python3 -m pytest tests/ -q
```

This does NOT change behavior; it only silences the warning.

---

## 6. Lint / Static Analysis Gate Status

| Tool | In `requirements.txt` | Status |
|------|----------------------|--------|
| `ruff` | ❌ No | Not available as local dev gate |
| `pyright` | ❌ No | Not available as local dev gate |
| `mypy` | Not checked | Not in standard gate |

**Current state:** No lint or typecheck step is configured for local dev or CI.

**Recommendation (future slice):** Add `ruff` to `backend/requirements.txt` (or `backend/requirements-dev.txt`) and wire into `backend-ci.yml` as a pre-test step.

---

## 7. CI Workflow Alignment

### `backend-ci.yml`

- **DB:** PostgreSQL 16 CI service (`flezibcg_ci:flezibcg_ci@localhost:5432/flezibcg_test`)
- **Env override:** `DATABASE_URL` env var (bypasses `.env` defaults)
- **Steps:** pip install → import check → Alembic heads check → `alembic upgrade head` → P0-A foundation tests
- **Does NOT run full suite** — only named P0-A tests
- **Named tests:** Alembic chain, migration smoke, bootstrap, refresh token, auth session, user lifecycle

### `pr-gate.yml`

- **Classifier:** Detects `mom_critical`, `db_or_migration`, `frontend_only`, `docs_only` file sets
- **Backend test job:** Runs named subset OR falls back to `python -m pytest -q`
- **Includes:** `test_scope_rbac_foundation_alignment.py` in explicitly named subset

**Gap:** CI does not run the full 634-test suite. Full suite is a local gate only. Agents must run full suite locally before committing domain or testenv changes.

---

## 8. Files Changed in This Baseline

| File | Change | Purpose |
|------|--------|---------|
| `backend/tests/conftest.py` | Modified (TESTENV-01 + TESTENV-02) | DB safety guard, `_to_psycopg_url()`, `check_test_db_readiness()`, dev DB hint |
| `backend/tests/test_testenv_db_safety.py` | New (TESTENV-01) | 18 unit + 1 live skip — safety guard contract |
| `backend/tests/test_testenv_db_connectivity_contract.py` | New (TESTENV-02) | 21 tests — connectivity contract, psycopg URL handling |
| `docker/README.dev.md` | Modified (TESTENV-02) | Stale container port binding fix documented |
| `docs/audit/tech-debt-testenv-01-backend-test-db-safety.md` | New (TESTENV-01) | Audit report for TESTENV-01 |
| `docs/audit/tech-debt-testenv-02-backend-test-db-connectivity.md` | New (TESTENV-02) | Audit report for TESTENV-02 |
| `backend/scripts/verify_backend.py` | New (BASELINE-01) | Canonical verification script |
| `docs/audit/backend-qa-baseline-01-green-test-baseline-freeze.md` | New (BASELINE-01) | This document |

---

## 9. Residual Risks

| Risk | Severity | Mitigation |
|------|---------|-----------|
| DB named `mes` (not `mes_test`) | Low | Warning is printed. Safety guard in conftest. Add `FLEZIBCG_ALLOW_TEST_DB_RESET=1` env var to silence. |
| CI does not run full suite | Medium | Agents must run full suite locally before merging domain changes. Document in PR checklist. |
| No lint/typecheck gate | Medium | Add ruff to requirements in a future slice. |
| Two DB container names | Low | Documented in this file and `docker/README.dev.md`. |
| `ruff` in transitive `.venv` deps but not in `requirements.txt` | Low | Does not affect functionality. Clean up in future dep audit. |
| Uncommitted changes from multiple in-progress tasks | Info | Normal during active development. Each task should commit its own files. |

---

## 10. Recommended Next Slice

**BACKEND-QA-BASELINE-02** (suggested): Wire backend lint gate

- Add `ruff` to `backend/requirements.txt`
- Add `ruff check .` step to `backend-ci.yml` before pytest
- Add `ruff check .` to `verify_backend.py`
- Document lint baseline (zero violations or documented exceptions)

---

## 11. Suggested Commit Commands

```bash
# BACKEND-QA-BASELINE-01 files
git add backend/scripts/verify_backend.py
git add docs/audit/backend-qa-baseline-01-green-test-baseline-freeze.md

# TECH-DEBT-TESTENV-02 files (if not already committed)
git add backend/tests/conftest.py
git add backend/tests/test_testenv_db_connectivity_contract.py
git add docker/README.dev.md
git add docs/audit/tech-debt-testenv-02-backend-test-db-connectivity.md

git commit -m "feat(qa): BACKEND-QA-BASELINE-01 — freeze backend green test baseline

- Add backend/scripts/verify_backend.py: canonical verification script
  following verify_*.py pattern; runs import -> DB -> testenv -> full suite;
  supports --testenv-only and --full-suite-twice flags; passwords masked
- Add docs/audit/backend-qa-baseline-01-green-test-baseline-freeze.md:
  baseline audit, 3-tier PR gate contract, stale DB recovery, CI alignment
- Baseline: 634 passed, 4 skipped, 0 failures (stable, 2 runs)
- DB readiness: docker compose up -d db (or --force-recreate if port not bound)
- verify_backend.py self-test: all checks PASS confirmed
"
```
