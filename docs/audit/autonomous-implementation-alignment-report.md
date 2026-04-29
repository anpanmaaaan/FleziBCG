# Autonomous Implementation Alignment Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-28 | v1.0 | Initial autonomous repository alignment audit for P0-A planning. |

## Routing
- Selected brain: MOM
- Selected mode: Architecture
- Hard Mode MOM: ON
- Reason: The requested autonomous mission includes execution/auth/session/scope/event truth and governance-critical implementation planning.

## Current backend structure
- Entrypoint: backend/app/main.py
- API routing: backend/app/api/v1/router.py
- Layers present:
- Routes in backend/app/api/v1/
- Services in backend/app/services/
- Repositories in backend/app/repositories/
- Models in backend/app/models/
- Security in backend/app/security/
- Session/auth routes exist at backend/app/api/v1/auth.py.

## Current frontend structure
- Entrypoint: frontend/src/main.tsx
- App shell: frontend/src/app/App.tsx, frontend/src/app/routes.tsx
- API clients: frontend/src/app/api/
- Auth UX/state: frontend/src/app/auth/
- Page composition: frontend/src/app/pages/
- i18n infra exists and lint scripts are configured in frontend/package.json.

## Existing DB/migration setup
- SQLAlchemy sync engine/session: backend/app/db/session.py
- Startup/init path calls init_db from backend/app/main.py.
- init_db currently runs:
1. Base.metadata.create_all(bind=engine)
2. SQL file replay from backend/scripts/migrations/*.sql
3. seed routines
- SQL file migration chain exists in backend/scripts/migrations/0001..0012.
- Alembic package is present in backend/requirements.txt, but Alembic project files are missing (no alembic.ini, no backend/alembic/).

## Existing auth/session/tenant/scope support
- JWT identity + per-request authorization dependency model exists:
- backend/app/security/auth.py
- backend/app/security/dependencies.py
- backend/app/security/rbac.py
- Session governance tables/models exist:
- backend/app/models/session.py
- migration backend/scripts/migrations/0006_tier1_sessions.sql
- Scope hierarchy foundation exists via scopes + user_role_assignments:
- backend/app/models/rbac.py
- seeded hierarchy in backend/app/security/rbac.py
- Tenant context is explicit in most models and dependencies (tenant_id fields/headers).

## Existing test setup
- No centralized pytest.ini/conftest.py detected.
- Test suite is file-local fixture style under backend/tests/.
- Focused MOM foundation tests exist for claims, closure/reopen, downtime, allowed_actions, projection reconciliation.
- Frontend scripts include lint and i18n checks; no dedicated frontend unit test script currently present in package.json.

## Design gaps against authoritative baseline
1. Alembic mandatory rule not met:
- Governance hardening requires Alembic as canonical migration system.
- Current runtime relies on create_all + SQL script replay.
2. Production schema management path still uses create_all:
- Violates hardening direction that create_all must not be production migration path.
3. CORS hardening not applied in backend app startup:
- No CORSMiddleware setup detected in backend/app/main.py.
4. CloudBeaver appears in root docker-compose.yml:
- P0-A prompt calls out dev-only posture check; root compose currently includes cloudbeaver service.

## Implementation risks
- Introducing Alembic + changing init behavior can break local startup and tests if not sliced safely.
- Removing create_all abruptly can break first-run developer UX and test fixtures that assume implicit table creation.
- Scope/auth changes can cause cross-tenant regressions without explicit tests.
- Existing integration tests can fail due to dirty local DB state (observed station-busy test interference).

## Recommended first slice
- Slice: P0-A-01 CORS configuration hardening (small behavioral security slice).
- Why first:
- Explicitly in P0-A prompt scope.
- Low blast radius, independent of migration framework transition.
- Can be verified via targeted API tests without changing DB contract.
- Exclusions respected:
- No execution state-machine changes.
- No claim/session refactor.
- No ERP/quality/material/AI scope.

## Stop condition notes
- Full Alembic transition is high-risk and should be separate strict slice after small hardening slices pass.
- No conflicting design truths found for this first slice.
