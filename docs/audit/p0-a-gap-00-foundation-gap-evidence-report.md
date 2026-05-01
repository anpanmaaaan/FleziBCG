# P0-A-GAP-00 — Foundation Gap Evidence / Source Alignment Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Created P0-A foundation gap evidence and source-alignment report. |

---

## 1. Executive Verdict

**P0-A_PARTIAL_READY_WITH_P0_BLOCKERS**

The FleziBCG backend has a solid, partially-complete P0-A foundation. Tenant isolation, session/revoke, roles/permissions, and security-event audit machinery are present and tested. Alembic is structurally in place but not yet the live migration driver — the custom SQL runner is still active on startup. Refresh tokens are entirely absent. User lifecycle remains boolean-only (`is_active`). Plant/area/line/station/equipment do not have dedicated ORM models or a Scope-node hierarchy table. CI now has a backend test job in `pr-gate.yml` (introduced since the prior audit report). CloudBeaver remains in the primary `docker-compose.yml` without a production guard.

P0-A implementation slicing is safe to begin, but five P0-BLOCKER gaps (listed below) must be resolved before any P0-B domain expansion begins.

---

## 2. Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Architecture + Strict (source audit / governance readiness)
- **Hard Mode MOM:** v3 ON
- **Reason:** Task touches tenant/scope/auth, IAM lifecycle, role/action/scope assignment, audit/security event, DB migration baseline, and critical foundation invariants.

---

## 3. Mandatory Files Status

| File | Found | Inspected |
|---|:---:|:---:|
| `.github/copilot-instructions.md` | YES | YES |
| `.github/agent/AGENT.md` | YES | YES |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | YES | YES |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | YES | YES |

All four mandatory files present. No stop condition triggered.

---

## 4. Sources Inspected

### Design / Governance

| File | Status |
|---|---|
| `docs/design/INDEX.md` | Found, read |
| `docs/design/AUTHORITATIVE_FILE_MAP.md` | Found, read |
| `docs/design/00_platform/product-business-truth-overview.md` | Found, read |
| `docs/governance/CODING_RULES.md` | Found, read |
| `docs/governance/ENGINEERING_DECISIONS.md` | Found, read |
| `docs/governance/SOURCE_STRUCTURE.md` | Found, read |
| `docs/design/10_hardening/hardening-baseline-summary.md` | Found, read |
| `docs/audit/source-code-audit-report.md` | Found, read |
| `docs/audit/be-qa-foundation-01-report.md` | Found (referenced in context) |
| `docs/audit/audit-be-01-security-event-read-filter-report.md` | Found (created this session) |
| `docs/design/00_platform/canonical-api-contract.md` | NOT FOUND at `00_platform/`; equivalent at `05_application/` |
| `docs/implementation/autonomous-implementation-plan.md` | Not inspected — not required to classify P0-A |

### Backend Source

| Path | Found | Notes |
|---|:---:|---|
| `backend/app/main.py` | YES | lifespan pattern; CORS present; stale title "MES Lite" |
| `backend/app/config/settings.py` | YES | Pydantic Settings; CORS allow-list; env_file |
| `backend/app/db/init_db.py` | YES | Custom SQL runner present; `create_all` gated by `bootstrap_schema=True` |
| `backend/app/db/session.py` | YES | Sync sessionmaker; psycopg3 |
| `backend/alembic/` | YES | `env.py`, `script.py.mako`, `versions/0001_baseline.py` |
| `backend/alembic/versions/0001_baseline.py` | YES | No-op baseline; not yet stamped on existing installs |
| `backend/app/models/user.py` | YES | `is_active` boolean only; no lifecycle status enum |
| `backend/app/models/session.py` | YES | Session + SessionAuditLog; revoke + reason present |
| `backend/app/models/rbac.py` | YES | Role, Permission, RolePermission, UserRole, Scope, UserRoleAssignment, RoleScope |
| `backend/app/models/security_event.py` | YES | SecurityEventLog; tenant-scoped; no severity field |
| `backend/app/models/impersonation.py` | YES | ImpersonationSession + ImpersonationAuditLog |
| `backend/app/models/master.py` | YES | ProductionOrder, WorkOrder, Operation — domain models, NOT hierarchy |
| `backend/app/security/auth.py` | YES | Argon2; JWT HS256; `AuthIdentity` dataclass |
| `backend/app/security/dependencies.py` | YES | `RequestIdentity`; `require_action`; `require_authenticated_identity` |
| `backend/app/security/rbac.py` | YES | `ACTION_CODE_REGISTRY`; `SYSTEM_ROLE_FAMILIES`; `has_action` |
| `backend/app/services/session_service.py` | YES | `create_login_session`, `revoke_session`, `revoke_all_sessions_for_user` |
| `backend/app/services/user_lifecycle_service.py` | YES | `activate_user`, `deactivate_user`, `list_tenant_users` |
| `backend/tests/` | YES | 330 tests collected |
| `backend/scripts/migrations/` | YES | 12 SQL files (custom runner) |
| `.github/workflows/pr-gate.yml` | YES | Backend test job present |
| `.github/workflows/frontend-i18n.yml` | YES | i18n lint only |
| `docker-compose.yml` | YES | CloudBeaver at line 68 in primary compose |

### Missing / Not Found

| Path | Notes |
|---|---|
| Refresh token model / table | No `RefreshToken` class found anywhere in `backend/app/models/` or services |
| Tenant ORM model (`class Tenant(Base)`) | No dedicated Tenant table — tenant identity is a string column; no tenant lifecycle |
| Plant / Area / Line / Station / Equipment ORM models | No dedicated hierarchy models; station_id and equipment_id exist only as string columns in `StationSession` and `DowntimeReason` |
| `docs/design/00_platform/canonical-api-contract.md` | Not found at expected path |
| `docs/design/00_platform/product-scope-and-phase-boundary.md` | Not found |
| `docs/design/00_platform/domain-boundary-map.md` | Not verified to exist |
| `docs/implementation/design-gap-report.md` | Not found |
| `docs/implementation/hard-mode-v3-map-report.md` | Not found |
| `.env.example` | Not verified at root; `.env.docker` exists |

---

## 5. Design Evidence Extract

### Source docs read

| Doc | Why used |
|---|---|
| `.github/copilot-instructions.md` | Mandatory |
| `.github/agent/AGENT.md` | Mandatory |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Mandatory |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | Mandatory |
| `docs/design/INDEX.md` | Foundation/governance reading order |
| `docs/design/AUTHORITATIVE_FILE_MAP.md` | Truth hierarchy |
| `docs/design/00_platform/product-business-truth-overview.md` | Platform principles |
| `docs/governance/CODING_RULES.md` | Engineering rules |
| `docs/governance/ENGINEERING_DECISIONS.md` | Reconciled truths |
| `docs/governance/SOURCE_STRUCTURE.md` | Repo structure |
| `docs/design/10_hardening/hardening-baseline-summary.md` | P0-A hardening decisions |
| `docs/audit/source-code-audit-report.md` | Prior audit evidence |

### P0-A Authoritative Requirements (Design Evidence)

From `hardening-baseline-summary.md` and `CODING_RULES.md`:

1. **Alembic is canonical** — no `create_all()` for production schema management.
2. **Tenant isolation at repository** — explicit `tenant_id` on all queries; RLS-ready (P1 hardening, not P0-A mandatory).
3. **JWT proves identity only** — authorization is server-side.
4. **Session is DB-backed** — revoke and logout-all must exist.
5. **Password hashing** — Argon2 required.
6. **CORS** — explicit allow-list; no wildcard.
7. **Backend sync stack** — preserved for P0-A; async migration is separate ADR.
8. **Structured logging** — HIGH gap from prior audit; not required before P0-A slice start, but must be tracked.
9. **CloudBeaver** — must not be in production runtime path.
10. **Backend CI** — must detect backend regressions.
11. **Claim deprecated** — `OperationClaim` is migration debt; must not be extended.

---

## 6. Foundation Capability Map

| Capability | Expected P0-A Baseline | Source Evidence | Current Status | Confidence |
|---|---|---|---|---|
| Alembic migration baseline | Alembic present; production startup does not call `create_all` | `alembic/versions/0001_baseline.py` (no-op); `init_db.py` gated `create_all`; custom SQL runner still active | PARTIAL | HIGH |
| Tenant table/context | Tenant identity must be explicit; server-derived from JWT | No `Tenant` ORM model. `tenant_id` is a string column on every model. JWT `tenant_id` claim → `AuthIdentity`. Repo filters explicit. | PARTIAL | HIGH |
| IAM user lifecycle | User should have lifecycle states (pending, active, suspended, locked, deactivated) | `User.is_active` (bool only). `user_lifecycle_service` supports activate/deactivate only. No invitation/reset/suspension flows. | PARTIAL | HIGH |
| Password hashing | Argon2 | `auth.py` — `CryptContext(schemes=["argon2"])` | COMPLETE | HIGH |
| JWT identity | JWT proves identity only; not authorization | `AuthIdentity` dataclass; `require_action` enforces server-side permission | COMPLETE | HIGH |
| Session lifecycle | DB-backed; revoke; logout-all | `Session` model; `revoke_session`; `revoke_all_sessions_for_user` | COMPLETE | HIGH |
| Refresh token rotation | Separate refresh token table; rotation path | No `RefreshToken` model. No rotation path. Auth refresh endpoint rotates access token only via session re-issue. | MISSING | HIGH |
| Role model | Role table with type, lifecycle, tenant scope | `Role` model — `role_type`, `is_active`, `is_system`, `base_role_id`, `review_due_at` | COMPLETE | HIGH |
| Action registry | `ACTION_CODE_REGISTRY` or DB-backed permission table | `ACTION_CODE_REGISTRY` in `rbac.py` (static dict); `Permission` table with `action_code` column | PARTIAL | HIGH |
| Role-action binding | `RolePermission` with scope | `RolePermission` table with `scope_type`, `scope_value`, `effect` | COMPLETE | HIGH |
| User-role assignment | `UserRole` / `UserRoleAssignment` with tenant | `UserRole` and `UserRoleAssignment` models present | COMPLETE | HIGH |
| Scope node | Scope hierarchy node model | `Scope` model with `parent_scope_id`, `scope_type`, `scope_value` | COMPLETE | HIGH |
| Scope assignment | User-scope binding via `RoleScope` | `RoleScope` on `UserRole` — scope value attached to user role | PARTIAL | MEDIUM |
| Plant hierarchy | Dedicated Plant/Area/Line/Station/Equipment ORM models | No dedicated hierarchy models. `station_id`/`equipment_id` are string columns in `StationSession`. `DowntimeReason` has nullable `plant_code`/`area_code`/`line_code`. | MISSING | HIGH |
| Audit log | Tenant-scoped audit trail | `SecurityEventLog`; `SessionAuditLog`; `ImpersonationAuditLog`; `ApprovalAuditLog` | COMPLETE | HIGH |
| Security event | Write + read API; tenant-scoped | `SecurityEventLog` model; service; repository; `GET /api/v1/security-events` with filters | COMPLETE | HIGH |
| CORS/config | Explicit allow-list; not wildcard | `CORSMiddleware` with `cors_allow_origins_list` from settings | COMPLETE | HIGH |
| Runtime DB hygiene | `create_all()` NOT in production startup path | `init_db()` default path: `bootstrap_schema=False` — no `create_all`. Custom SQL runner still active. Alembic runner not yet replacing SQL runner. | PARTIAL | HIGH |
| CloudBeaver/dev-only posture | CloudBeaver must not be in production runtime | `docker-compose.yml` line 68 — CloudBeaver present in PRIMARY compose; no production-guard | CONFLICT | HIGH |
| Backend CI | Backend test workflow triggering on PRs | `pr-gate.yml` — backend tests job present; targets specific test files, fallback to `pytest -q` | COMPLETE | HIGH |

---

## 7. Source Inventory by Area

### 7.1 Migration / DB Foundation

- **Alembic config**: Present — `backend/alembic.ini`, `backend/alembic/env.py`.
- **Alembic heads**: One revision — `0001_baseline` (no-op; documents pre-Alembic schema state).
- **Migration versions**: `0001_baseline.py` — intentional no-op; does not recreate tables.
- **Custom SQL runner**: Still active in `init_db._apply_sql_migrations()` — reads `backend/scripts/migrations/*.sql`.
- **`create_all()` path**: Gated — `init_db(bootstrap_schema=True)` only. Default/production call `init_db()` does NOT call `create_all()`.
- **Downgrade strategy**: None. `downgrade()` in baseline is a no-op.
- **Migration smoke tests**: `test_alembic_baseline.py` — 7 tests; verifies `alembic.ini`, script location, baseline revision, and live upgrade (skipped if DB unreachable).
- **Gap**: Alembic is not yet the live migration driver; startup still applies raw SQL. Transition to Alembic-only migration path is not complete.

### 7.2 Tenant Foundation

- **Tenant model**: None. No `Tenant` table in any `app/models/*.py` file.
- **Tenant identity source**: JWT `tenant_id` claim decoded by middleware → `AuthIdentity.tenant_id` → `RequestIdentity.tenant_id`. All repos filter by `tenant_id` explicitly.
- **Tenant resolution dependency**: `get_request_identity` + header cross-check (`X-Tenant-ID` must match JWT if provided).
- **Tenant isolation in repos**: Confirmed present — `tenant_id` column on every operational table; all repo queries filter by it.
- **Tenant tests**: `test_tenant_foundation.py` — 5 tests; `test_qa_foundation_tenant_isolation.py`; audit isolation tests.
- **Gap**: No tenant lifecycle management (create/deactivate tenant). Tenant is implicit string only.

### 7.3 IAM / User Lifecycle

- **User model**: `User` — `user_id`, `username`, `email`, `password_hash`, `tenant_id`, `is_active`, `created_at`, `updated_at`.
- **User status fields**: `is_active` boolean only. No `status` enum (PENDING, ACTIVE, SUSPENDED, LOCKED, DEACTIVATED).
- **Password hashing**: Argon2 via `passlib`. ✓
- **User lifecycle service**: `user_lifecycle_service.py` — activate/deactivate/list only.
- **Invitation/reset flows**: Not present.
- **Admin/support user model**: Not separate — all users share the `User` table; role differentiates ADM/OTS.
- **Lifecycle tests**: `test_user_lifecycle_service.py` — activate/deactivate/tenant-scoped list tests.
- **Gap**: User lifecycle is boolean-only. Full status lifecycle (PENDING/SUSPENDED/LOCKED) is missing.

### 7.4 Auth / JWT / Session / Refresh Token

- **JWT creation**: `create_access_token` in `auth.py`. HS256. Configurable expiry (default 480 min = 1 shift).
- **JWT validation**: `decode_access_token` in auth middleware (`main.py`) via `jose.jwt.decode`.
- **Session model**: `Session` table — `session_id` (PK = JWT `jti`), `user_id`, `tenant_id`, `issued_at`, `expires_at`, `revoked_at`, `revoke_reason`. `SessionAuditLog` table.
- **Session revoke**: `revoke_session` present; `revoke_all_sessions_for_user` present.
- **Logout-all**: `POST /api/v1/auth/logout-all` route present; tested.
- **Refresh token model**: **MISSING** — no `RefreshToken` table or model anywhere.
- **Refresh token rotation**: **MISSING** — `test_auth_session_api_alignment.py::test_refresh_endpoint_returns_new_bearer_token` tests a refresh endpoint exists; but refresh issues a new access token from the existing session rather than rotating a refresh token.
- **JWT identity only**: Confirmed — `require_action` enforces server-side; no frontend authorization of operations.
- **Tests**: Multiple auth/session tests present.

### 7.5 Roles / Actions / Permissions

- **Role model**: `Role` with `code`, `tenant_id`, `role_type`, `base_role_id`, `review_due_at`, `is_active`, `is_system`. ✓
- **Action registry**: Static `ACTION_CODE_REGISTRY` dict in `security/rbac.py` + `Permission` DB table with `action_code` column. ACTION_CODE_REGISTRY has 13 entries. No `admin.user.manage` in the frozen SYSTEM_ROLE_FAMILIES action map — it uses a placeholder pattern.
- **Role-action binding**: `RolePermission` with `scope_type`, `scope_value`, `effect`. ✓
- **User-role assignment**: `UserRole` + `UserRoleAssignment`. ✓
- **Authorization dependency**: `require_action` + `require_authenticated_identity` in `dependencies.py`; `has_action` in `rbac.py`.
- **Placeholder action codes**: `admin.user.manage` used in security events route is NOT in `SYSTEM_ROLE_FAMILIES`/`ACTION_CODE_REGISTRY` with a system role binding — it is in `ACTION_CODE_REGISTRY` mapping to `"ADMIN"` family.
- **Tests**: `test_access_service.py`; `test_qa_foundation_authorization.py`; `test_audit_security_event_authorization.py`.

### 7.6 Scope / Plant Hierarchy

- **Scope node model**: `Scope` table — `tenant_id`, `scope_type`, `scope_value`, `parent_scope_id`. Hierarchy via self-referential FK. ✓
- **Scope assignment**: `RoleScope` links a `UserRole` to a scope value. `UserRoleAssignment` also exists.
- **Plant/Area/Line/Station/Equipment models**: **MISSING** as dedicated ORM entities. Only string columns (`station_id`, `equipment_id`) on `StationSession` and nullable `plant_code`, `area_code`, `line_code` on `DowntimeReason`. No `Plant`, `Area`, `Line`, `Station`, `Equipment` ORM classes.
- **Scope-path query pattern**: Not present — no hierarchy traversal query utility found.
- **Tests**: `test_access_service.py::test_assign_scope_creates_tenant_scope_and_assignment`. No dedicated plant-hierarchy tests.

### 7.7 Audit / Security Events

- **Security event model**: `SecurityEventLog` — `tenant_id`, `actor_user_id`, `event_type`, `resource_type`, `resource_id`, `detail`, `created_at`. No `severity` field.
- **Security event service**: `security_event_service.py` — `record_security_event`, `get_security_events` with filters.
- **Security event repository**: `security_event_repository.py` — tenant-scoped; newest-first; filter/pagination.
- **Security event API**: `GET /api/v1/security-events` — admin-gated; filter by event_type/actor/resource/time range.
- **Privileged actions audited**: Login, logout, logout-all, impersonation create/revoke, session revoke, user activate/deactivate, access assignment.
- **Separate audit log**: `SessionAuditLog`, `ImpersonationAuditLog`, `ApprovalAuditLog` — all tenant-scoped.
- **Tests**: `test_security_event_service.py`; `test_security_events_endpoint.py`; `test_audit_security_event_read_filters.py`; `test_audit_security_event_tenant_isolation.py`; `test_audit_security_event_authorization.py`; `test_admin_audit_security_events.py`.
- **Gap**: No `severity` field. No dedicated audit log model separate from security events (acceptable for P0-A).

### 7.8 Config / Runtime Hygiene

- **Settings module**: `settings.py` — Pydantic `BaseSettings`; env_file for local dev; `cors_allow_origins` string parsed to list. ✓
- **CORS config**: `CORSMiddleware` in `main.py` via `apply_cors_middleware()` — explicit origin allow-list from settings. ✓ (was MISSING in prior audit — now fixed).
- **Secret handling**: `jwt_secret_key` default `"change-me"` — deliberately insecure default for dev. No production validation that secret was changed.
- **App title**: `FastAPI(title="MES Lite")` — stale; should be "FleziBCG MOM".
- **Environment profiles**: No explicit dev/staging/production profile separation. `app_env: str = "dev"` present but not enforced.
- **Debug flag**: `debug: bool = True` default — unsafe for production if left unset.
- **CloudBeaver**: In primary `docker-compose.yml` (lines 68–81) without production override pattern.
- **Logging**: No structured logging / correlation ID found in backend source.
- **i18n module**: `backend/app/i18n/` — present; not in `SOURCE_STRUCTURE.md` spec. Exception + locale resolver.

### 7.9 Backend CI

- **Workflows present**: `pr-gate.yml` (backend + frontend jobs), `frontend-i18n.yml`.
- **`pr-gate.yml` backend job**: Runs on `pull_request` to `main`/`develop`. Python `3.12`. Installs deps. Import check. Runs specific test files; falls back to `pytest -q`.
- **DB service in CI**: **NOT PRESENT** — no `services: postgres:` section in `pr-gate.yml`. Tests that require DB must skip or use SQLite.
- **Lint/type steps**: Not present in backend CI — no `mypy`, `ruff`, or `flake8` step.
- **Dependency scanning**: Not present.
- **Python version in CI**: `3.12` (workspace venv uses `3.14.4`).
- **Gap**: No PostgreSQL service in CI — DB-dependent tests skip in CI. No type-check or lint step for backend.

---

## 8. Invariant / Risk Map

| Invariant | Evidence | Current Protection | Gap | Severity |
|---|---|---|---|---|
| Tenant isolation must be server-side | `tenant_id` derived from JWT; all repo queries filter by it | JWT → middleware → `RequestIdentity.tenant_id`; repo filters explicit | No dedicated Tenant table (isolation relies on string column consistency) | P1-HARDENING |
| JWT proves identity only | `AuthIdentity` carries identity; `require_action` enforces permissions server-side | `dependencies.py` `require_action` + `has_action`; action registry in `rbac.py` | `ACTION_CODE_REGISTRY` is static — new actions require code change | P2-FOLLOWUP |
| Authorization is server-side | `require_action` dependency; action guard on all write routes | Present and tested | `admin.user.manage` in registry but binding to system roles unclear — seeded but not tested explicitly | P1-HARDENING |
| Persona is not permission | Persona is UX-only (frontend `personaLanding.ts`) | Frontend persona not used in backend logic | Not applicable at backend layer | WATCH |
| Security/audit events are tenant-scoped | `SecurityEventLog.tenant_id` NOT NULL; repo always filters by tenant | Present in model + repo + tests | No `severity` field; no event integrity/write protection | P2-FOLLOWUP |
| Privileged actions must be auditable | Login/logout/impersonation/user-lifecycle/access-assignment all emit `SecurityEventLog` entries | Tested in `test_admin_audit_security_events.py` | Not all protected write routes emit security events (e.g., some operation commands) | P1-HARDENING |
| Production app must not depend on `create_all()` | `init_db()` default path gated; test verifies | `test_init_db_bootstrap_guard.py` passes | Custom SQL runner still active alongside Alembic baseline | P0-BLOCKER |
| CI must detect backend regressions | `pr-gate.yml` backend job runs pytest | Present; fallback to full `pytest -q` | No PostgreSQL service in CI — DB-dependent tests skip; no type/lint step | P1-HARDENING |
| Dev-only tools must not be in production runtime | CloudBeaver should be dev-only | None — no production guard pattern | CloudBeaver in primary `docker-compose.yml` at line 68 | P0-BLOCKER |
| Refresh token must be a separate table | ENGINEERING_DECISIONS; session-based auth hardening | Not implemented | No `RefreshToken` model at all | P0-BLOCKER |
| User lifecycle must support states beyond boolean | IAM design intent | `is_active` bool only | No PENDING/SUSPENDED/LOCKED/DEACTIVATED states | P0-BLOCKER |
| Plant hierarchy must be addressable | Scope node exists; plant/area/line/station as entities for assignment | Scope node model present | No Plant/Area/Line/Station/Equipment ORM models | P0-BLOCKER |
| Alembic must be the live migration driver | Hardening baseline; CODING_RULES | Alembic baseline exists (no-op); SQL runner still active | Alembic not yet replacing SQL runner on startup | P0-BLOCKER |

---

## 9. Test Coverage Map

| Area | Existing Tests | Coverage Quality | Missing Tests | Recommended Slice |
|---|---|---|---|---|
| Alembic / migration | `test_alembic_baseline.py` — 7 tests | Good: structural + live upgrade (DB-conditional skip) | Live stamp test; Alembic-only startup path; downgrade smoke | P0-A-01 |
| `create_all` bootstrap guard | `test_init_db_bootstrap_guard.py` — 2 tests | Good: unit; covers default + explicit bootstrap | Production startup guard with env var | P0-A-01 |
| CORS policy | `test_cors_policy.py` — 2 tests | Adequate: allowed + rejected origins | Env-based override test; credentials test | P0-A-07 |
| Tenant isolation | `test_tenant_foundation.py` — 5 tests; `test_qa_foundation_tenant_isolation.py` | Good: header mismatch; auth alignment | Tenant-string-only invariant; no Tenant table tests (nothing to test) | P0-A-02 |
| IAM / user lifecycle | `test_user_lifecycle_service.py` — activate/deactivate/filter | Partial: only boolean lifecycle | Lifecycle status enum transitions; PENDING state; suspension; password reset | P0-A-03 |
| Auth / JWT | `test_auth_session_api_alignment.py` — 2 tests | Partial: refresh + revoke routes | Invalid token; expired token; tampered token; wrong tenant on token | P0-A-03 |
| Session / revoke | `test_session_service_security_events.py`; `test_auth_security_event_routes.py` | Partial: event emission; route alignment | Full session lifecycle; concurrent session limit; logout-all isolation | P0-A-03 |
| Refresh token | None | MISSING | Entire coverage | P0-A-03 |
| Roles / actions | `test_access_service.py` — role/scope assignment | Partial: assign, reject unsupported scope | Role seeding correctness; action-to-family binding; ADM/OTS exclusions | P0-A-04 |
| Auth action guard | `test_qa_foundation_authorization.py`; `test_audit_security_event_authorization.py` | Good: unauthenticated; forbidden; authorized | All action codes in registry have at least one test | P0-A-04 |
| Scope / plant hierarchy | `test_access_service.py::test_assign_scope_*` | Partial: scope creation + assignment | Plant/area/line/station ORM model tests; hierarchy traversal | P0-A-05 |
| Security events | `test_security_event_service.py`; `test_security_events_endpoint.py`; `test_audit_*` (3 files) | Good: write, read, filter, tenant isolation, authz | Severity field (not present); event integrity | P0-A-06 |
| Admin audit events | `test_admin_audit_security_events.py` — 2 tests | Partial: user lifecycle + access assignment emit events | All governed actions emit events | P0-A-06 |
| Config / settings | None explicit | MISSING | Production-unsafe default detection (`jwt_secret_key == "change-me"`, `debug=True`) | P0-A-07 |
| CloudBeaver guard | None | MISSING | compose file presence detection; production guard | P0-A-07 |
| CI workflow config | `test_pr_gate_workflow_config.py` | Present | DB service in CI; type/lint step coverage | P0-A-07 |
| **Totals** | **330 tests collected; all pass (327 pass, 3 skip)** | | | |

DB-dependent tests use SQLite in-memory or PostgreSQL (skipped if unavailable). No PostgreSQL service in CI — DB-skip behavior is expected.

---

## 10. Gap Classification Matrix

| Gap ID | Area | Finding | Evidence | Severity | Recommended Follow-up |
|---|---|---|---|---|---|
| GAP-01 | Migration / DB | Custom SQL runner still active; Alembic not yet live migration driver | `init_db._apply_sql_migrations()` active; Alembic `0001_baseline` is no-op | **P0-BLOCKER** | P0-A-01 — Alembic runtime activation |
| GAP-02 | Refresh token | No `RefreshToken` model, table, or rotation path | No class found in `app/models/`; `test_auth_session_api_alignment.py` tests access-token refresh only | **P0-BLOCKER** | P0-A-03 — Refresh token implementation |
| GAP-03 | IAM lifecycle | `User.is_active` boolean only; no PENDING/SUSPENDED/LOCKED/DEACTIVATED | `app/models/user.py` line 32 | **P0-BLOCKER** | P0-A-03 — User lifecycle status enum |
| GAP-04 | Plant hierarchy | No dedicated Plant/Area/Line/Station/Equipment ORM models | No `class Plant(Base)` found; string columns only | **P0-BLOCKER** | P0-A-05 — Plant hierarchy models |
| GAP-05 | CloudBeaver posture | CloudBeaver in primary `docker-compose.yml` without production guard | `docker-compose.yml` line 68 | **P0-BLOCKER** | P0-A-07 — CloudBeaver isolation |
| GAP-06 | Tenant table | No Tenant ORM model; tenant identity is implicit string | No `class Tenant(Base)` | **P1-HARDENING** | P0-A-02 — Tenant table slice |
| GAP-07 | Structured logging | No structured logging / correlation ID | No logger calls found in `backend/app/` | **P1-HARDENING** | P0-A-07 — Logging hardening |
| GAP-08 | App title | `FastAPI(title="MES Lite")` — stale | `main.py` line 22 | **P2-FOLLOWUP** | Any cleanup slice |
| GAP-09 | CI PostgreSQL | No `services: postgres:` in `pr-gate.yml` — DB tests skip in CI | `pr-gate.yml` — no service block | **P1-HARDENING** | P0-A-07 — CI hardening |
| GAP-10 | CI lint/type | No `mypy`, `ruff`, `flake8` step in backend CI | `pr-gate.yml` — no lint step | **P1-HARDENING** | P0-A-07 — CI hardening |
| GAP-11 | JWT secret default | `jwt_secret_key: str = "change-me"` — no prod validation | `settings.py` line 24 | **P1-HARDENING** | P0-A-07 — Config hardening |
| GAP-12 | Debug default | `debug: bool = True` — unsafe for production if unset | `settings.py` line 11 | **P1-HARDENING** | P0-A-07 — Config hardening |
| GAP-13 | Action registry scope | `admin.user.manage` in ACTION_CODE_REGISTRY; binding to system roles not explicitly seeded/tested | `rbac.py`; `security_events.py` | **P1-HARDENING** | P0-A-04 — Action binding verification |
| GAP-14 | Scope assignment completeness | `RoleScope` vs `UserRoleAssignment` — two patterns; which is canonical unclear | `rbac.py` models — both present | **P1-HARDENING** | P0-A-04 — Scope assignment canonicalization |
| GAP-15 | `SOURCE_STRUCTURE.md` drift | `backend/app/i18n/` not documented in `SOURCE_STRUCTURE.md` | Source audit report §2.2 | **P2-FOLLOWUP** | Doc-only slice |
| GAP-16 | Supabase dead dependency | `@supabase/supabase-js` in `frontend/package.json` — unused | Source audit report §4.2 | **P2-FOLLOWUP** | Mechanical cleanup PR |
| GAP-17 | Claim migration debt | `OperationClaim` still present and active; deprecated per ENGINEERING_DECISIONS §10.1 | `models/station_claim.py`; `services/station_claim_service.py` | **P2-FOLLOWUP** | Separate claim deprecation slice (do not touch in P0-A) |
| GAP-18 | Downgrade strategy | Alembic `downgrade()` is no-op; no rollback path | `0001_baseline.py:downgrade()` | **P2-FOLLOWUP** | P0-A-01 |
| GAP-19 | Hardcoded role in routes | `if _effective_role_code(identity) != "SUP"` in `operations.py` lines 314, 344 | Source audit report §3.2 | **P1-HARDENING** | Separate slice — do not touch in P0-A |
| GAP-20 | Security event severity | No `severity` field on `SecurityEventLog` | `models/security_event.py` | **P2-FOLLOWUP** | P0-A-06 addendum |

---

## 11. P0-A Readiness Scorecard

| Area | Score | Rationale | Next Action |
|---|:---:|---|---|
| Alembic migration baseline | 2 | Structurally present; no-op baseline; not yet live driver | P0-A-01: activate Alembic as live migration runner; retire SQL runner |
| Tenant context / isolation | 2 | String-based tenant; repo filters explicit; no Tenant table | P0-A-02: add Tenant table + lifecycle; confirm isolation test coverage |
| IAM user lifecycle | 1 | Boolean-only `is_active`; activate/deactivate service present; no status enum | P0-A-03: add lifecycle status enum and transitions |
| Password hashing | 3 | Argon2; transparent rehash; production-ready | None |
| JWT identity | 3 | JWT identity-only; action guard server-side; middleware clean | None |
| Session lifecycle | 3 | DB-backed; revoke; logout-all; audit trail; tested | None |
| Refresh token rotation | 0 | Entirely absent | P0-A-03: implement RefreshToken model + rotation |
| Role model | 3 | Role table with type/scope/lifecycle; seeded; tested | None |
| Action registry | 2 | Static ACTION_CODE_REGISTRY + Permission table; 13 registered codes | P0-A-04: verify all seeded bindings; test coverage per action code |
| Role-action binding | 3 | RolePermission with scope/effect; UserRole + UserRoleAssignment | None |
| Scope node | 3 | Scope table with parent_scope_id hierarchy FK | None |
| Scope assignment | 2 | RoleScope present; two assignment patterns — canonicalization needed | P0-A-04 |
| Plant hierarchy | 0 | No Plant/Area/Line/Station/Equipment models | P0-A-05 |
| Audit log | 3 | Multiple audit log tables; tenant-scoped; tested | None |
| Security event | 3 | Model + service + repository + API + tests | Minor: severity field, broader action coverage |
| CORS / config | 2 | CORS present; allow-list; `debug=True` and `jwt_secret_key="change-me"` defaults unsafe | P0-A-07 |
| Runtime DB hygiene | 2 | `create_all` gated; SQL runner still active; Alembic not live | P0-A-01 |
| CloudBeaver dev-only | 0 | In primary compose with no production guard | P0-A-07 |
| Backend CI | 2 | Backend test job present; no DB service; no lint/type check | P0-A-07 |

**Total: 37 / 57** (scores 0–3 per 19 areas). Passing areas: 6/19 at score 3. Five BLOCKER gaps.

---

## 12. Recommended Implementation Sequence

### P0-A-01 — Alembic / Runtime DB Hygiene

**Intent:** Make Alembic the live migration driver; retire SQL runner from production startup.

**Why now:** GAP-01 is a P0-BLOCKER. Without this, production migrations are uncontrolled.

**In scope:**
- Activate Alembic `upgrade("head")` at `init_db()` startup in place of SQL runner.
- Retire `_apply_sql_migrations()` SQL runner from production init path (keep for bootstrap compatibility if needed).
- Add Alembic downgrade stub for baseline.
- Update `test_alembic_baseline.py` to confirm live startup uses Alembic.

**Explicitly out of scope:** New schema changes; model changes; seed data changes.

**Test focus:** `test_init_db_bootstrap_guard.py`; `test_alembic_baseline.py`; regression on full suite.

**Stop conditions:** If Alembic `upgrade("head")` requires DB changes not already in `0001_baseline`, stop and record.

---

### P0-A-02 — Tenant Context / Isolation Contract Hardening

**Intent:** Introduce a Tenant ORM model; lock tenant isolation contract with explicit DB-backed tenant identity.

**Why now:** GAP-06 (P1). Without a Tenant table, tenant creation/lifecycle has no server-side anchor. Blocking for multi-tenant onboarding.

**In scope:**
- Add `Tenant` model (tenant_id, name, is_active, created_at).
- Add Alembic migration for Tenant table.
- Add tenant-existence check to auth/identity chain.
- Add tests for tenant isolation with explicit Tenant table.

**Explicitly out of scope:** Tenant provisioning API; multi-tenant onboarding UI; cross-tenant admin features.

**Test focus:** Tenant isolation unit tests; login-with-unknown-tenant rejection.

**Stop conditions:** If tenant identity is not carried in JWT claim, stop — auth chain must be re-examined first.

---

### P0-A-03 — IAM Session / Refresh Token Alignment

**Intent:** Complete user lifecycle status (beyond boolean); add refresh token table and rotation path.

**Why now:** GAP-02 (P0-BLOCKER) and GAP-03 (P0-BLOCKER).

**In scope:**
- Add `status` enum field to `User` (PENDING, ACTIVE, SUSPENDED, LOCKED, DEACTIVATED).
- Add Alembic migration for status column.
- Update user lifecycle service to use status enum.
- Add `RefreshToken` model (token_hash, user_id, session_id, tenant_id, issued_at, expires_at, revoked_at).
- Add refresh token rotation path to auth service.
- Add tests for lifecycle transitions and refresh token rotation.

**Explicitly out of scope:** Invitation email; password reset email; OAuth/SSO.

**Test focus:** Status enum transitions; refresh token issue/rotate/revoke; expired token rejection.

**Stop conditions:** If session model must change to support refresh tokens, produce a design record first.

---

### P0-A-04 — Role / Action / Scope Assignment Alignment

**Intent:** Canonicalize scope assignment pattern; verify all action codes in registry are seeded and tested.

**Why now:** GAP-13 and GAP-14 (P1-HARDENING). Two assignment patterns (`RoleScope` vs `UserRoleAssignment`) need clarification before P0-B domain work relies on RBAC.

**In scope:**
- Determine canonical scope assignment pattern and document.
- Ensure ACTION_CODE_REGISTRY entries all have explicit role bindings tested.
- Add missing action-to-family binding tests.
- Verify ADM/OTS exclusions are tested.

**Explicitly out of scope:** New action codes; new role types; dynamic permission management UI.

**Test focus:** All 13 registered action codes; role-family binding; scope assignment round-trip.

**Stop conditions:** If two patterns cannot be reconciled without schema change, escalate to design gate.

---

### P0-A-05 — Plant Hierarchy / Scope Node Alignment

**Intent:** Introduce Plant/Area/Line/Station/Equipment as addressable ORM entities.

**Why now:** GAP-04 (P0-BLOCKER). Without hierarchy models, scope assignment to plant/station entities has no DB anchor.

**In scope:**
- Add `Plant`, `Area`, `Line`, `Station`, `Equipment` ORM models with tenant_id + hierarchy FK.
- Add Alembic migration.
- Add tests for hierarchy isolation and scope node binding.

**Explicitly out of scope:** Station session domain changes; execution domain changes; OEE models.

**Test focus:** Tenant-isolated hierarchy read; hierarchy FK integrity; scope binding.

**Stop conditions:** If execution models must change as a result, stop and document — do not touch execution in P0-A.

---

### P0-A-06 — Audit / Security Event Foundation Completion

**Intent:** Ensure all governed privileged actions emit security events; verify audit coverage.

**Why now:** GAP-20 is P2-FOLLOWUP; but broader action-coverage gap (GAP-13) is P1. Build on the existing complete security event infrastructure.

**In scope:**
- Identify governed write routes that do not emit security events.
- Add missing `record_security_event` calls for governed actions.
- Add tests confirming event emission for each.

**Explicitly out of scope:** Severity field (requires schema change — separate slice); event integrity enforcement.

**Test focus:** All governed write routes; cross-tenant audit isolation.

**Stop conditions:** If event emission requires outbox/transaction changes, stop and document.

---

### P0-A-07 — Backend CI / Config / Dev-only Tooling Hardening

**Intent:** Harden config defaults, CI, and CloudBeaver posture before P0-B expansion.

**Why now:** GAP-05 (P0-BLOCKER: CloudBeaver); GAP-09, GAP-10, GAP-11, GAP-12 (P1-HARDENING).

**In scope:**
- Move CloudBeaver to a dev-only compose override file.
- Add PostgreSQL service to `pr-gate.yml` for DB-dependent tests.
- Add `ruff` or equivalent lint step to backend CI.
- Add `debug=False` default for `app_env=production`.
- Add production secret validation (fail fast if `jwt_secret_key == "change-me"`).
- Update `FastAPI(title=...)` to "FleziBCG MOM".

**Explicitly out of scope:** Full test suite DB migration in CI; production deployment changes; pyproject.toml restructuring.

**Test focus:** `test_cors_policy.py`; `test_pr_gate_workflow_config.py`; config validation tests.

**Stop conditions:** If CI PostgreSQL service changes break existing tests, fix tests in same slice before merging.

---

## 13. Explicit Non-Goals Confirmed

This audit did NOT:
- Change production source code.
- Change tests.
- Add tests.
- Add migrations.
- Modify DB models.
- Modify routes.
- Modify services or repositories.
- Modify RBAC/action codes.
- Modify security event behavior.
- Modify tenant behavior.
- Modify auth/session behavior.
- Modify config.
- Modify CI workflow.
- Modify frontend.
- Modify MMD.
- Modify Execution or Station Execution.
- Implement ERP, Acceptance Gate, Backflush, APS, AI, or Digital Twin features.
- Add Redis, Kafka, OPA, Casbin, or Celery.
- Fix any issue found.

---

## 14. Stop Conditions / Unknowns

| Item | Type | Notes |
|---|---|---|
| No Tenant ORM model | UNKNOWN | Tenant isolation relies on string column consistency — works but not anchored in DB lifecycle |
| Alembic not live migration driver | KNOWN GAP | SQL runner still active; transition to Alembic-only path not complete |
| Refresh token entirely absent | KNOWN GAP | Not blocked by design ambiguity; implementation slice is clear |
| Plant hierarchy models absent | KNOWN GAP | Scope node present — hierarchy models can be added without touching execution |
| CloudBeaver in primary compose | KNOWN GAP | Mechanical change; no design ambiguity |
| `docs/design/00_platform/canonical-api-contract.md` missing at expected path | UNKNOWN | Equivalent found at `05_application/`; path drift noted |
| `docs/design/00_platform/product-scope-and-phase-boundary.md` | UNKNOWN | Not verified — not needed for P0-A classification |
| Two scope assignment patterns | KNOWN GAP | `RoleScope` vs `UserRoleAssignment` — require canonicalization in P0-A-04 |
| CI PostgreSQL absent | KNOWN GAP | DB tests skip in CI — mitigated by local/Docker runs; tracked as P1 |

No stop conditions triggered. Evidence is sufficient to classify all P0-A capabilities. Report write is allowed.

---

## 15. Final Recommendation

**Proceed with P0-A slicing.** Five P0-BLOCKER gaps exist and must be resolved before P0-B domain expansion begins:

1. **P0-A-01** — Activate Alembic as live migration driver (retire SQL runner from production startup).
2. **P0-A-03** — Add `RefreshToken` model and rotation path; add User lifecycle status enum.
3. **P0-A-04** (P1, but before P0-B) — Canonicalize scope assignment pattern.
4. **P0-A-05** — Add Plant/Area/Line/Station/Equipment hierarchy models.
5. **P0-A-07** — Move CloudBeaver out of primary compose; harden CI.

Sequence P0-A-01 first because all other migration slices depend on Alembic being the live driver.

Do not begin P0-B domain slices until P0-A-01, P0-A-03 (refresh token + lifecycle), and P0-A-05 (plant hierarchy) are complete.

---

## Appendix A — File Evidence

| File | Key Evidence | Notes |
|---|---|---|
| `backend/app/main.py` | `apply_cors_middleware(app)` present; `lifespan` pattern; title stale | CORS fixed since prior audit |
| `backend/app/db/init_db.py` | `bootstrap_schema=False` default; `_apply_sql_migrations()` still active | GAP-01 |
| `backend/alembic/versions/0001_baseline.py` | No-op baseline; `downgrade()` no-op | GAP-01, GAP-18 |
| `backend/app/models/user.py` | `is_active: bool` only; no lifecycle status enum | GAP-03 |
| `backend/app/models/session.py` | `revoked_at`; `revoke_reason`; `SessionAuditLog` | COMPLETE |
| `backend/app/models/rbac.py` | `Role`, `Permission`, `RolePermission`, `UserRole`, `Scope`, `UserRoleAssignment`, `RoleScope` | COMPLETE; GAP-14 |
| `backend/app/security/rbac.py` | `ACTION_CODE_REGISTRY` 13 codes; `SYSTEM_ROLE_FAMILIES` | PARTIAL; GAP-13 |
| `backend/app/security/auth.py` | Argon2 hash; JWT HS256; `AuthIdentity` | COMPLETE |
| `backend/app/security/dependencies.py` | `RequestIdentity`; `require_action`; `require_authenticated_identity` | COMPLETE |
| `backend/app/config/settings.py` | `cors_allow_origins_list`; `jwt_secret_key="change-me"`; `debug=True` | GAP-11, GAP-12 |
| `backend/app/models/security_event.py` | Tenant-scoped; no severity | COMPLETE for P0-A; GAP-20 |
| `docker-compose.yml:68` | CloudBeaver in primary compose | GAP-05 |
| `.github/workflows/pr-gate.yml` | Backend test job; Python 3.12; no postgres service | GAP-09, GAP-10 |
| `backend/tests/` | 330 tests collected; 327 pass, 3 skip | Full suite result 2026-05-01 |

---

## Appendix B — Commands Run

All commands were read-only. No DB mutations were performed.

```
# Alembic structural inspection (offline — no DB connection required)
python -m pytest --collect-only -q
# → 330 tests collected

python -m pytest -q
# → 327 passed, 3 skipped in 61.60s

# Directory inspection (via tool, not shell)
list_dir backend/app
list_dir backend/app/models
list_dir backend/app/api/v1
list_dir backend/app/security
list_dir backend/app/services
list_dir backend/app/repositories
list_dir backend/alembic/versions
list_dir backend/tests
list_dir .github/workflows

# Text searches (grep_search, read-only)
grep "create_all" backend/app/**
grep "RefreshToken" backend/**
grep "class.*Base" backend/app/models/*.py
grep "user_status|lifecycle_status" backend/app/models/*.py
grep "logout_all" backend/app/**
grep "plant_id|area_id|line_id|station_id|equipment_id" backend/**
grep "cloudbeaver" docker-compose.yml
```

Note: `alembic current` and `alembic heads` were not executed because they require a live DB connection (PostgreSQL) which is not guaranteed in this environment. Alembic structural state was confirmed via direct file inspection.
