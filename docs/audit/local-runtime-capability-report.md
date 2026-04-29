# Local Runtime Capability Report

| Field | Value |
|---|---|
| **Report ID** | LOCAL-RUNTIME-AUDIT-001 |
| **Date** | 2026-04-29 |
| **Version** | v1.2 |
| **Auditor** | GitHub Copilot / FleziBCG Local Runtime Capability Auditor |
| **Scope** | Local Windows developer workstation — backend dev + integration test runtime |
| **Verdict** | `CAN_START_NOW` — DB runtime started, Alembic baseline bookkeeping aligned, full backend verification executed (1 failing test remains) |

---

## History

| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-04-29 | Initial audit |
| v1.1 | 2026-04-29 | Human-approved DB compose start executed; DB health/connectivity and DB-backed tests verified |
| v1.2 | 2026-04-29 | Alembic baseline bookkeeping executed; full backend pytest run completed with one failure |

---

## 1. Audit Scope

Determine whether this repo can start the required local runtime services for backend development and integration tests:

- PostgreSQL test DB (via Docker Compose)
- Backend server (FastAPI / uvicorn)
- Docker Compose services (db-only stack)

Hard constraints:
- AUDIT-ONLY — no containers started, no code modified
- Docker daemon NOT started without explicit human approval
- No destructive Git commands

---

## 2. Environment Baseline

| Property | Value | Status |
|---|---|---|
| OS | Windows (PowerShell terminal) | - |
| Python virtual env | `g:/Work/FleziBCG/.venv/Scripts/python.exe` | ✓ EXISTS |
| Docker CLI | v29.4.0 | ✓ INSTALLED |
| Docker Compose plugin | v5.1.2 | ✓ INSTALLED |
| Docker daemon | Docker Desktop Linux Engine — **RUNNING** | ✓ READY |
| Backend import check | `import app.main` → `import ok` | ✓ PASSES |

---

## 3. Compose Files

| File | Status | Notes |
|---|---|---|
| `docker-compose.yml` | ✓ EXISTS | Full stack: db + backend + frontend + cloudbeaver (dev-tools profile) |
| `docker/docker-compose.db.yml` | ✓ EXISTS | DB-only stack: postgres:15 + cloudbeaver |
| `docker compose config` (db-only) | ✓ EXIT 0 | Config parses without error |

Preferred local dev stack: `docker/docker-compose.db.yml` — starts PostgreSQL only without frontend/backend containers.

---

## 4. Database Configuration

| Property | Value | Source |
|---|---|---|
| Engine | PostgreSQL 15 (Docker image `postgres:15`) | `docker/docker-compose.db.yml` |
| Container name | `flezi-dev-db` | - |
| Host (from backend perspective) | `localhost` | `backend/.env` |
| Port | `5432` | `backend/.env` + `docker/.env.db` exposed port |
| Database | `mes` | `docker/.env.db` + `backend/.env` |
| User | `mes` | `docker/.env.db` + `backend/.env` |
| Password | (set in `docker/.env.db` and `backend/.env`) | REDACTED |
| Named volume | `postgres_data` (persistent) | `docker/docker-compose.db.yml` |
| Healthcheck | `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB` | - |
| DB runtime state | **RUNNING / HEALTHY** (`flezi-dev-db`) | Verified via `docker compose ... ps` |

---

## 5. Backend Configuration

| Property | Value | Source |
|---|---|---|
| Framework | FastAPI 0.135.2 + uvicorn 0.42.0 | `requirements.txt` |
| Python | 3.14.4 | `.venv` |
| Entrypoint | `uvicorn app.main:app --host 0.0.0.0 --port 8010` | `backend/Dockerfile` CMD |
| Port | 8010 | `backend/Dockerfile` EXPOSE |
| Health endpoint | `GET /api/v1/ping` → `{"message":"pong"}` | `app/api/v1/router.py` |
| OpenAPI | `GET /openapi.json` | FastAPI default |
| DB URL (resolved) | `postgresql+psycopg://mes:mes@localhost:5432/mes` | Settings at startup |
| DB driver | `psycopg 3.3.3` (psycopg-binary) | `requirements.txt` |
| CORS | Configurable via `settings.cors_allow_origins_list` | `app/main.py` |
| Startup hook | `init_db()` — runs SQL migrations + seeds RBAC/users | `app/main.py` lifespan |
| Import check | ✓ PASSES | Terminal diagnostic |
| Settings load | ✓ PASSES | Terminal diagnostic |
| Backend runtime state | **NOT STARTED** | Requires live DB first |

---

## 6. Environment Files

| File | Exists | Purpose |
|---|---|---|
| `docker/.env.db` | ✓ YES | DB credentials for Docker Compose (POSTGRES_USER, PASSWORD, DB) |
| `backend/.env` | ✓ YES | Local backend overrides — APP_NAME, APP_ENV, DEBUG, POSTGRES_*, JWT_SECRET_KEY, JWT_ALGORITHM |
| `.env.example` (root) | ✓ YES | Docker image overrides only (PYTHON_IMAGE, NGINX_IMAGE, NODE_IMAGE) — NOT for secrets |
| `backend/.env.example` | ✗ MISSING | No example for backend env (gap for new developer onboarding) |

**Gap noted:** New developers have no `backend/.env.example` to copy. The `docker/README.dev.md` documents the required variables but there is no machine-readable template.

---

## 7. Migration System

| Component | Status | Notes |
|---|---|---|
| Manual SQL scripts (`backend/scripts/migrations/`) | ✓ 14 files (0001–0014) | Applied idempotently by `init_db()` at startup |
| Alembic | ✓ CONFIGURED | `backend/alembic/`, `backend/alembic.ini`, `env.py` reads DB URL from settings |
| Alembic versions | 1 revision: `0001_baseline.py` | **Intentional no-op** — represents pre-Alembic schema state |
| Alembic baseline intent | `alembic stamp 0001` on existing DB | New installs: `python -m app.db.init_db` + `alembic stamp 0001` |
| Alembic `sqlalchemy.url` in ini | NOT SET | Correct — env.py provides URL from app settings |

**Migration approach for a fresh DB:**
1. Run `python -m app.db.init_db` — creates schema (14 SQL migrations) + seeds RBAC + demo users
2. Run `alembic stamp 0001` — registers baseline in `alembic_version` table
3. Future changes: `alembic revision --autogenerate` + `alembic upgrade head`

---

## 8. Seed Data

| Component | Status | Notes |
|---|---|---|
| `seed_rbac_core(db)` | Called by `init_db()` | RBAC roles, permissions, scopes |
| `seed_approval_rules(db)` | Called by `init_db()` | Approval rules referencing role codes |
| `seed_demo_users(db)` | Called by `init_db()` | Demo user accounts (see `DEMO_ACCOUNTS.md`) |
| `backend/scripts/seed/` | 4 scenario scripts + `seed_all.py` | Production scenario seeds — run manually, not in `init_db()` |

---

## 9. Test Suite DB Dependency

| Category | Count | DB Required | Notes |
|---|---|---|---|
| Fast / mock tests (TestClient, monkeypatch) | ~15 | ✗ NO | Run without DB; use `TestClient` only |
| DB-integration tests | ~112+ | ✓ YES | Use `SessionLocal()` directly; hang without live PostgreSQL |
| Total collected | 127 | - | `pytest --collect-only` exit 0 |

Pre-existing constraint: DB-integration tests cannot run until PostgreSQL is accessible at `localhost:5432`. This is not a code bug — it is the expected integration test requirement.

---

## 10. Port Map

| Service | Port | Protocol | Notes |
|---|---|---|---|
| PostgreSQL | 5432 | TCP | Docker host-mapped from container |
| Backend API | 8010 | HTTP | `uvicorn` on localhost |
| Frontend | 80 | HTTP | nginx (full stack only) |
| CloudBeaver | 8978 | HTTP | DB admin UI (db-only stack optional) |

---

## 11. Identified Gaps / Risks

| # | Gap | Severity | Recommendation |
|---|---|---|---|
| G-01 | Docker daemon startup is a required precondition on each machine reboot/login | INFO | Ensure Docker Desktop is running before DB-backed tests |
| G-02 | `backend/.env.example` missing | LOW | Create template file for new developer onboarding |
| G-03 | `JWT_ALGORITHM` line in `backend/.env` has no value (trailing key only) | MEDIUM | Verify settings handles missing value gracefully; confirm default is applied |
| G-04 | `README.dev.md` uses Codespaces-style paths (`/workspaces/...`) | LOW | Update local Windows paths for Windows dev onboarding |
| G-05 | `alembic stamp 0001` not documented in Windows dev setup instructions | LOW | Add to dev setup checklist |
| G-06 | Full backend pytest has one failing DB-backed reopen/resume test | MEDIUM | Investigate `STATE_STATION_BUSY` in full-suite context before claiming all-green backend verification |

---

## 12. DB Connectivity Test

Executed successfully from backend environment:

```powershell
Set-Location g:/Work/FleziBCG/backend
g:/Work/FleziBCG/.venv/Scripts/python.exe -c "from app.db.session import engine; conn = engine.connect(); print('db connect ok'); conn.close()"
```

Observed output:
- `db connect ok`

Schema readiness check:
- `public_table_count: 23`
- `has_alembic_version: False`

Interpretation:
- Schema is present (not a fresh empty DB), so first-time bootstrap was **not required** for this run.
- `alembic_version` baseline table is not stamped yet; this does not block DB-backed tests, but should be stamped when aligning migration bookkeeping.

---

## 13. Proposed Start Plan

> **HUMAN APPROVAL REQUIRED before running any of the following commands.**

### Step 1 — Start Docker Desktop

Launch Docker Desktop from the Windows Start Menu. Wait for the Docker engine to be fully started (system tray icon becomes steady).

Verify daemon is running:
```powershell
docker info
```

### Step 2 — Start the DB-only stack

```powershell
Set-Location g:/Work/FleziBCG
docker compose -f docker/docker-compose.db.yml up -d
```

Wait for the DB to pass its health check:
```powershell
docker compose -f docker/docker-compose.db.yml ps
```
Expected: `flezi-dev-db` status = `healthy`.

### Step 3 — Bootstrap schema (first time only)

If this is a fresh database volume with no existing schema:
```powershell
Set-Location g:/Work/FleziBCG/backend
g:/Work/FleziBCG/.venv/Scripts/python.exe -m app.db.init_db
```

Then stamp Alembic baseline:
```powershell
g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic stamp 0001
```

If schema already exists (volume is persistent from a prior run), skip `init_db` and only verify Alembic state:
```powershell
g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic current
```

### Step 4 — Start backend server (local dev)

```powershell
Set-Location g:/Work/FleziBCG/backend
g:/Work/FleziBCG/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

Verify:
```powershell
Invoke-RestMethod http://localhost:8010/api/v1/ping
```
Expected: `{"message":"pong"}`

### Step 5 — Run integration tests (after DB is healthy)

```powershell
Set-Location g:/Work/FleziBCG/backend
g:/Work/FleziBCG/.venv/Scripts/pytest tests/ -x -v
```

---

## 14. Full Stack (Docker Compose) — Alternative

> **HUMAN APPROVAL REQUIRED before running.**

To run backend + frontend + DB all in Docker:
```powershell
Set-Location g:/Work/FleziBCG
docker compose up -d
```

This builds and starts `db`, `backend`, and `frontend` containers. Backend accessible at `http://localhost:8010`, frontend at `http://localhost`.

CloudBeaver (DB admin) available via `--profile dev-tools`:
```powershell
docker compose --profile dev-tools up -d
```

---

## 15. Verdict

```
VERDICT: CAN_START_NOW
```

| Question | Answer |
|---|---|
| Docker CLI installed? | ✓ YES — v29.4.0 |
| Docker Compose plugin installed? | ✓ YES — v5.1.2 |
| Docker daemon running? | ✓ YES |
| docker-compose.db.yml config valid? | ✓ YES — exit 0 |
| `backend/.env` present? | ✓ YES — all required variables set |
| `docker/.env.db` present? | ✓ YES — DB credentials present |
| Backend import check? | ✓ PASSES |
| Settings load check? | ✓ PASSES — DB URL resolves correctly |
| DB container running? | ✓ YES — `flezi-dev-db` healthy |
| DB connectivity tested? | ✓ PASSED — `db connect ok` |
| Backend server running? | ✗ NO — not started (requires DB first) |
| Can start DB? | ✓ YES — confirmed |
| Can start backend? | ✓ YES — after DB is healthy |
| Can run integration tests? | ✓ YES — after DB is healthy |
| Missing secrets or env files? | ✗ NONE — all env files present |
| Safe next command? | `g:/Work/FleziBCG/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload` |

## 16. Executed Runtime Verification (Approved)

1. Docker daemon check:
	- `docker info --format "{{.ServerVersion}}"` -> `29.4.0`
2. DB-only compose start:
	- `docker compose -f docker/docker-compose.db.yml up -d`
	- `docker compose -f docker/docker-compose.db.yml ps`
	- `flezi-dev-db` status: `Up ... (healthy)`
3. DB connectivity check:
	- Output: `db connect ok`
4. DB-backed previously blocked file:
	- `python -m pytest -q tests/test_claim_single_active_per_operator.py -vv`
	- Result: `6 passed in 1.99s`
5. Integration marker run:
	- `python -m pytest -q -m integration`
	- Result: `127 deselected in 2.18s` (no integration-marked tests currently selected)

Non-blocking runtime note:
- Compose emitted warning: existing `docker_postgres_data` volume was not created by current Compose project definition. Service still started healthy.

## 17. Migration Bookkeeping + Full Backend Verification

Executed commands:
1. `g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic heads`
2. `g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic current`
3. `g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic stamp 0001`
4. `g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic current`
5. `g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic upgrade head`
6. `g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic current`
7. `g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q`

Alembic status evidence:
- Before stamp:
	- `heads`: `0001 (head)`
	- `current`: no revision row shown (missing `alembic_version` table)
- Schema evidence before stamp decision:
	- `table_count: 23`
	- `has_alembic_version: False`
	- existing-schema baseline usage is explicitly documented in `backend/alembic/versions/0001_baseline.py`
- Stamp decision:
	- SAFE and EXECUTED (`stamp 0001`)
	- rationale: existing schema present, baseline is no-op for pre-existing schema, only one Alembic head exists, and docs specify stamping for already provisioned DBs
- After stamp:
	- `current`: `0001 (head)`
	- `upgrade head`: no pending changes
	- `current` remains `0001 (head)`

Full backend pytest result:
- Summary: `1 failed, 125 passed, 1 skipped, 24 warnings in 16.03s`
- Failing test:
	- `tests/test_close_reopen_operation_foundation.py::test_reopen_operation_success_updates_metadata_appends_event_and_projects_paused`
- Failure reason:
	- `ResumeExecutionConflictError: STATE_STATION_BUSY`
	- raised in `app/services/operation_service.py` during `resume_operation`

Scope guard confirmation:
- P0-B-02 Routing Foundation was not implemented.
