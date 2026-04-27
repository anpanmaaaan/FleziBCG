# Source Code Audit Report — FleziBCG

**Audit Date:** 2026-04-27  
**Baseline:** Latest consolidated design package 2026-04-26, Hardening v1, Hardening Housekeeping v1.1  
**Auditor:** Senior Software Architect (automated pre-implementation audit)  
**Status:** AUDIT ONLY — No code was modified during this review.

---

## 1. Executive Verdict

The FleziBCG codebase has a **solid, well-structured foundation** for the modular-monolith MOM platform, but carries **significant migration debt** and **several production-readiness gaps** that must be addressed before the system can be considered implementation-slice-ready.

**Strengths:**
- Backend layering (routes → services → repositories → models) is consistent and disciplined.
- Auth/session lifecycle is well-implemented: JWT proves identity only, sessions are DB-backed with revocation, Argon2 hashing, impersonation audit trail present.
- Execution domain is event-driven with derived status. Status is never stored directly as authoritative source of truth.
- `allowed_actions` is computed and returned from the backend — the frontend is not encoding authorization truth for the execution domain.
- Tenant isolation is explicit at repository level with `tenant_id` filters on every query.
- i18n infrastructure is complete and enforced by CI.
- Documentation depth is significant and covers domain, governance, and engineering decisions.

**Critical Gaps:**
- No Alembic. The custom SQL migration runner + `create_all()` is not production-safe.
- Claim-owned execution is still live and active — it is officially deprecated per ENGINEERING_DECISIONS.md §10 but not removed.
- No refresh token implementation.
- User lifecycle is incomplete (only `is_active` boolean — no pending/suspended/locked/deactivated states).
- Quality, Material, Traceability, and ERP domains are entirely mock-data placeholders in the frontend with zero backend models.
- No CORS configuration in the FastAPI app.
- CloudBeaver is included in the primary `docker-compose.yml` with no production guard.
- No backend CI pipeline; only frontend i18n lint CI exists.
- No React Query or consistent server-state management on the frontend.
- `@supabase/supabase-js` is a dependency in `frontend/package.json` with no apparent usage — likely dead code from a previous stack.
- `docs/design/` and `docs/business/design/` are parallel trees with overlapping content — creating navigation confusion.
- CODING_RULES.md references `docs/design/02_domain/...` but the canonical execution docs live at `docs/business/design/02_domain/...`.

**P0-A Feasibility:** **Hybrid** — the tenant, IAM, session, and role/scope tables exist and are partially usable, but require Alembic migration system introduction and User lifecycle completion before they can be trusted as canonical P0-A output.

---

## 2. Repository Structure

### 2.1 Actual Structure

```
/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env                     (local dev env, not committed)
│   ├── .venv/                   (virtual env, present in repo dir)
│   └── app/
│       ├── main.py
│       ├── api/v1/              (router + 11 route modules)
│       ├── config/settings.py
│       ├── db/                  (session, base, init_db)
│       ├── models/              (8 model files)
│       ├── repositories/        (8 repository files)
│       ├── schemas/             (12 schema files)
│       ├── security/            (auth, dependencies, rbac)
│       ├── services/            (12 service files)
│       └── i18n/                (NOT in SOURCE_STRUCTURE.md spec — extra folder)
│   └── scripts/
│       ├── migrations/          (12 SQL migration files)
│       └── seed/, verify_*.py   (dev scripts)
│   └── tests/                   (12 test files, no conftest.py visible)
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── eslint.config.js
│   ├── index.html
│   ├── supabase/                (NOT in SOURCE_STRUCTURE.md spec — vestigial)
│   └── src/
│       ├── main.tsx
│       ├── app/
│       │   ├── App.tsx
│       │   ├── routes.tsx
│       │   ├── api/             (httpClient, 7 API modules)
│       │   ├── auth/            (AuthContext, RequireAuth)
│       │   ├── components/
│       │   ├── data/            (mock data)
│       │   ├── i18n/            (infrastructure + registry)
│       │   ├── impersonation/
│       │   ├── pages/           (20 page files)
│       │   └── persona/         (personaLanding, PersonaLandingRedirect)
│       ├── lib/
│       ├── styles/
│       └── types/
├── docker-compose.yml           (includes CloudBeaver — production risk)
├── docker/                      (docker-compose.db.yml only)
├── docs/
│   ├── design/                  (canonical governance design docs)
│   ├── business/design/         (parallel tree — overlapping content)
│   ├── governance/              (CODING_RULES, ENGINEERING_DECISIONS, SOURCE_STRUCTURE)
│   ├── adr/                     (2 ADRs)
│   ├── architecture/
│   ├── phases/
│   └── audit/                   (this report)
├── .github/
│   ├── agent/AGENT.md
│   ├── copilot-instructions.md
│   └── workflows/frontend-i18n.yml
├── pyrightconfig.json
├── .env.docker
├── .env.example
└── docker-compose.yml
```

### 2.2 Findings Table

| Area | Current State | Evidence / File Path | Gap / Risk | Recommendation |
|---|---|---|---|---|
| Backend directory | Present, well-structured | `backend/app/` | `backend/app/i18n/` not in SOURCE_STRUCTURE spec | Keep; update SOURCE_STRUCTURE.md to reflect actual `i18n/` backend module |
| Frontend directory | Present, well-structured | `frontend/src/app/` | `supabase/` folder present (vestigial) | Remove `supabase/` folder and `@supabase/supabase-js` dependency in separate mechanical PR |
| Database migrations | Custom SQL runner, no Alembic | `backend/scripts/migrations/`, `backend/app/db/init_db.py` | No standard migration system; `create_all()` called at startup (production risk) | Introduce Alembic in P0-A slice |
| Tests | 12 backend test files, 0 frontend | `backend/tests/` | No CI for backend tests; no frontend tests | Add backend CI pipeline; add frontend build/type-check CI |
| CI/CD | Frontend i18n only | `.github/workflows/frontend-i18n.yml` | No backend test CI, no lint CI, no security scanning | Add backend and full test workflows |
| Docker/compose | CloudBeaver in primary compose | `docker-compose.yml:68` | CloudBeaver must be dev-only per SOURCE_STRUCTURE.md | Move CloudBeaver to `docker/docker-compose.cloudbeaver.yml` override |
| Docs structure | Two parallel design trees | `docs/design/` and `docs/business/design/` | Navigational ambiguity; CODING_RULES references wrong paths | Consolidate or create authoritative redirect README in each tree |
| Environment files | `.env.example` exists; `.env.docker` present | `/` | No production-vs-dev config split | Document which vars are mandatory for production |
| Lock files | `package-lock.json` present | `frontend/package-lock.json` | No `requirements.lock` for Python | Acceptable for now; note for P0-A infra hardening |

---

## 3. Backend Architecture

### 3.1 Summary Answers

- **Backend current stack:** SYNCHRONOUS (sync FastAPI middleware, sync SQLAlchemy ORM, sync repositories)
- **SQLAlchemy version:** 2.0.48 — using 2.x ORM with `Mapped`/`mapped_column` syntax but **sync** `sessionmaker`
- **DB driver:** `psycopg` 3.3.3 (psycopg3 sync binary — not asyncpg)
- **Routes thin or business-heavy:** Routes are **thin** — correct delegation to services
- **Service layer:** Present and owns business rules and transaction boundaries
- **Repository layer:** Present; data-access only (correct)
- **Domain rules:** Centralized in services (correct)
- **Error handling:** Mixed — `I18nHTTPException` handler in main.py, direct `HTTPException` in routes; no global uncaught-exception handler
- **Logging:** Not structured; no request_id, no correlation ID, no tenant_id in log context
- **Correlation ID:** Not supported
- **Multi-tenancy:** Handled at repository/service level via explicit `tenant_id` filtering on every query
- **CORS:** NOT CONFIGURED — `CORSMiddleware` is absent from `backend/app/main.py`

### 3.2 Findings Table

| Backend Area | Current State | Evidence / File Path | Baseline Fit | Risk | Recommendation |
|---|---|---|---|---|---|
| FastAPI entrypoint | `app = FastAPI(title="MES Lite")` — title is stale | `backend/app/main.py:11` | Minor drift | LOW | Update title to "FleziBCG MOM" in P0-A |
| `on_event("startup")` | Deprecated FastAPI API | `backend/app/main.py:14` | Low — functional | MEDIUM | Migrate to `lifespan` context manager |
| Auth middleware | Synchronous decode in `async def` | `backend/app/main.py:20-28` | Acceptable for sync stack | LOW | OK for sync stack; revisit if async migration |
| CORS | Not configured | `backend/app/main.py` — no CORSMiddleware | **MISSING** | **HIGH** | Add CORSMiddleware before P0-A goes to any integration environment |
| Router organization | `api/v1/router.py` includes 10 route modules | `backend/app/api/v1/router.py` | Fits SOURCE_STRUCTURE | LOW | OK |
| Service layer | 12 service files; business logic correct | `backend/app/services/` | Correct | LOW | OK |
| Repository layer | 8 repository files; data-access only | `backend/app/repositories/` | Correct | LOW | OK |
| SQLAlchemy stack | Sync `create_engine` + `SessionLocal` | `backend/app/db/session.py` | Not async; functional for current phase | MEDIUM | Document sync decision explicitly in ENGINEERING_DECISIONS.md |
| Transaction handling | Service layer calls `db.commit()` directly | `backend/app/services/*.py` | Service owns transactions — correct per rule 10.1 | LOW | OK |
| Error handling | `I18nHTTPException` + direct `HTTPException` in routes | `backend/app/main.py:34`, `backend/app/api/v1/*.py` | Partial | MEDIUM | Add generic 500 exception handler; standardize error shape per `canonical-api-contract.md` |
| Structured logging | Not implemented | `backend/app/` — no logger calls | **MISSING** | HIGH | Add structured logging with tenant_id, request_id, action_code in P0-A or immediately after |
| Config management | Pydantic Settings with env_file | `backend/app/config/settings.py` | Correct | LOW | OK; add explicit production-required-vars documentation |
| Backend i18n module | `backend/app/i18n/` — not in SOURCE_STRUCTURE | `backend/app/i18n/exceptions.py`, `resolver.py` | Minor structural drift | LOW | Add to SOURCE_STRUCTURE.md |
| `init_db` migration runner | Custom `*.sql` runner + `create_all()` on startup | `backend/app/db/init_db.py:39-65` | No Alembic | **BLOCKER** | Replace with Alembic in P0-A slice |
| Hardcoded role check in routes | `if _effective_role_code(identity) != "SUP"` | `backend/app/api/v1/operations.py:314,344` | Hardcoded role in route layer violates §5.1 | HIGH | Move role check to service or RBAC dependency |

---

## 4. Frontend Architecture

### 4.1 Summary Answers

- **React Query:** **NOT PRESENT** — `@tanstack/react-query` is absent from `package.json`
- **State management:** React Context only (AuthContext, ImpersonationContext, I18nContext). No Zustand, no Redux.
- **Backend permissions/allowed_actions:** Used partially — `OperationDetail.allowed_actions` is consumed in `StationExecution.tsx` and `OperationExecutionDetail.tsx`. Other screens do not consume backend-driven permission signals.
- **Authorization frontend-side:** Persona system is UX-only (correctly). Navigation and menu are persona-driven. No frontend-only authorization of execution actions.
- **Screens already existing (connected to backend):** LoginPage, Dashboard, ProductionOrderList, OperationList, OperationExecutionOverview, OperationExecutionDetail, GlobalOperationList, StationExecution, OEEDeepDive
- **Screens that are mock-data placeholders:** QCCheckpoints, DefectManagement, Traceability, APSScheduling, DispatchQueue, RouteList, RouteDetail, Production, ProductionTracking
- **Screen UI Inventory v2.2 match:** Not verifiable from repo — the audit did not locate a "Screen UI Inventory v2.2" document in the repo. Screens in `docs/design/04_ui/` describe v3.1 execution screens; other domains lack screen design docs in the codebase.
- **Station execution screens:** Implemented (StationExecution.tsx → stationApi + operationApi)
- **Global operations screens:** Implemented (GlobalOperationList, OperationExecutionOverview, OperationExecutionDetail)
- **Quality screens:** Mock-data placeholder only
- **Auth screens:** LoginPage implemented; no password-reset/account-management screens

### 4.2 Findings Table

| FE Area | Current State | Evidence / File Path | Baseline Fit | Risk | Recommendation |
|---|---|---|---|---|---|
| React Query | ABSENT | `frontend/package.json` — no `@tanstack/react-query` | Baseline recommends React Query | MEDIUM | Decision needed: adopt React Query or document Context-only approach in ENGINEERING_DECISIONS.md |
| State management | Context only | `frontend/src/app/auth/AuthContext.tsx`, `ImpersonationContext.tsx` | Functional; not React Query | MEDIUM | Document decision; add Zustand for non-server global state if needed |
| API client | `httpClient.ts` + per-domain API modules | `frontend/src/app/api/` | Correct layering | LOW | OK |
| Auth guard | `RequireAuth` (authentication-only) | `frontend/src/app/auth/RequireAuth.tsx` | Authentication gate only — correct per CODING_RULES §11.5 | LOW | OK |
| Permission guard | ABSENT | `frontend/src/app/` | No frontend permission guard exists | MEDIUM | Correct per rules — frontend must not encode permission truth. Clarify in CODING_RULES v2.0 that this is intentional. |
| Persona system | UX-only with DEV/STRICT mode | `frontend/src/app/persona/personaLanding.ts` | Correct UX-only behavior | LOW | Set STRICT as default for production via env variable |
| i18n | Infrastructure present, both locales | `frontend/src/app/i18n/registry/en.ts`, `ja.ts` | Correct; CI enforced | LOW | OK |
| QCCheckpoints | Mock data only | `frontend/src/app/pages/QCCheckpoints.tsx:23` | Domain not implemented | HIGH | Mark as placeholder; do not connect until quality domain backend exists |
| Traceability | Mock data only, uses ReactFlow | `frontend/src/app/pages/Traceability.tsx:37` | Domain not implemented | HIGH | Mark as placeholder |
| APSScheduling | Mock data only | `frontend/src/app/pages/APSScheduling.tsx:29` | Domain not implemented | LOW | Expected — out of current scope |
| DefectManagement | Mock data only | `frontend/src/app/pages/DefectManagement.tsx` | Domain not implemented | HIGH | Mark as placeholder |
| DispatchQueue | Exists as page, limited implementation | `frontend/src/app/pages/DispatchQueue.tsx` | Partial | MEDIUM | Clarify scope in next slice |
| Supabase dependency | `@supabase/supabase-js` in package.json | `frontend/package.json:46` | Not in architecture | **HIGH** | Remove in mechanical PR — dead dependency from prior stack |
| Frontend tests | ABSENT | `frontend/src/` | Not present | HIGH | Add page-level and component tests per CODING_RULES §13.2 |
| Error boundary | Not found in codebase | `frontend/src/app/` | Missing | MEDIUM | Add React error boundary at app root |
| Loading/empty states | Used in some pages | `frontend/src/app/pages/StationExecution.tsx` | Partial | LOW | Ensure pattern is consistent |

---

## 5. Database and Migrations

### 5.1 Summary Answers

- **Migration system:** Custom SQL runner (`_apply_sql_migrations`) + `Base.metadata.create_all()`. **Alembic is absent** despite being listed in `requirements.txt`.
- **Existing schema:** 12 SQL migration files applied: RBAC, impersonation, approval, users, sessions, scopes, custom roles, station claims, closure status, close/reopen metadata, downtime reasons.
- **Baseline alignment (Database Design v1.2):** Not verifiable — no "Database Design v1.2" document found in repo. Tables are aligned with execution domain contracts found in design docs.
- **Tenant isolation:** Present on all major tables (tenant_id columns with NOT NULL or indexed defaults).
- **UTC timestamps:** Mostly yes — `DateTime(timezone=True)` used, but some naive `DateTime` columns exist (e.g., `Operation.planned_start`).
- **Event tables:** `execution_events` is append-only (no update/delete path in code).
- **Audit:** Session audit, claim audit, approval audit, impersonation audit — present. No global audit_log table.
- **Enums overused:** `StatusEnum`, `ClosureStatusEnum`, `DowntimeReasonGroup` are Python enums used as DB value constraints (string columns) — acceptable for status/closure but `DowntimeReasonGroup` should ideally be a DB lookup table.
- **Current schema safe to extend?** Yes for P0-A foundational tables; risky for execution tables without Alembic.

### 5.2 Findings Table

| DB Area | Current State | Evidence / File Path | Baseline Fit | Risk | Recommendation |
|---|---|---|---|---|---|
| Alembic | In requirements.txt but not used | `backend/requirements.txt:1`, no `alembic.ini` | **Missing** | **BLOCKER** | Implement Alembic in P0-A; deprecate SQL runner |
| `create_all()` on startup | Runs at every app start | `backend/app/db/init_db.py:65` | Production-unsafe | **BLOCKER** | Replace with Alembic; remove `create_all()` from startup |
| Custom SQL migration runner | `_apply_sql_migrations` runs all `.sql` files sorted | `backend/app/db/init_db.py:39-57` | No idempotency tracking | HIGH | Temporary workaround; replace with Alembic env |
| `execution_events` table | Append-only; no update path | `backend/app/models/execution.py`, `backend/app/repositories/execution_event_repository.py` | Correct | LOW | OK |
| Tenant ID | Present on all major tables | `backend/app/models/*.py` | Correct | LOW | OK |
| Mixed timestamp timezone | `DateTime(timezone=True)` vs `DateTime` (naive) | `backend/app/models/master.py:45,46,73,74` | Inconsistent | MEDIUM | Make all timestamp columns timezone-aware in P0-A migration |
| Station model | No `Station` table — stations are `Scope` rows with `scope_type="station"` | `backend/app/models/rbac.py:125-154` | Architecture decision | MEDIUM | Document explicitly; plant hierarchy tables should be created in P0-A |
| Equipment model | Not found | `backend/app/models/` | Missing | MEDIUM | Required for ISA-95 alignment; add in plant hierarchy slice |
| Plant hierarchy | Partial — Scope table supports hierarchy via parent_scope_id | `backend/app/models/rbac.py:136` | Partial | MEDIUM | Create dedicated plant hierarchy tables in P0-A |
| Quality tables | Not found | `backend/app/models/` | **Missing** | HIGH | Required for Quality domain — P1 slice |
| Material / Traceability tables | Not found | `backend/app/models/` | **Missing** | HIGH | Required for Material domain — P2+ slice |
| ERP integration tables | Not found | `backend/app/models/` | Out of P0-A scope | LOW | Noted; out of current scope |
| Indexes | Partial — key FK and filter columns indexed | `backend/app/models/*.py` | Partial | MEDIUM | Review all query-hot columns; ensure index strategy with Alembic |
| Primary keys | Integer auto-increment (not UUID) on most tables | `backend/app/models/user.py`, `session.py` | Not UUID | MEDIUM | User.user_id is string UUID; PK is int. Acceptable; document decision |
| No global audit_log | Domain-specific audit tables only | `backend/app/models/` | Partial | MEDIUM | Consider generic security_events table for P0-A |

---

## 6. Auth / IAM / Session / Access Control

### 6.1 Summary Answers

- **What exists:** Login (DB-backed + config fallback), logout, logout-all, session revoke (admin), session list, JWT generation/validation, Argon2 hashing, session table with revocation, impersonation lifecycle, approval engine.
- **Incomplete:** Refresh token, password change/reset, user invite/activate/deactivate/lock/unlock lifecycle, user registration flow.
- **Insecure:** Plain-text password comparison fallback in `_verify_password` (config-path only — low risk in production but should be documented as explicit-only).
- **Conflicts with baseline:** User lifecycle states (PENDING/SUSPENDED/LOCKED/DEACTIVATED per CODING_RULES §11.3) not implemented.
- **Password hashing:** Argon2 — production-safe ✓
- **JWT as authorization truth:** No — JWT carries identity only; backend checks DB-backed permissions per request ✓
- **Roles hard-coded:** `SYSTEM_ROLE_FAMILIES` is frozen by design (correct per governance), but route-level hardcoded `if role_code != "SUP"` is a bug.
- **Scope enforced in backend:** Yes — `tenant_id` filter on all queries; station scope via `UserRoleAssignment` ✓
- **FE as authorization truth:** No ✓

### 6.2 Findings Table

| IAM Area | Current State | Evidence / File Path | Baseline Fit | Risk | Recommendation |
|---|---|---|---|---|---|
| Login (DB-backed) | Implemented | `backend/app/security/auth.py:146-193` | Correct | LOW | OK |
| Login (config fallback) | Implemented (bootstrap only) | `backend/app/security/auth.py:80-93` | Acceptable for dev/bootstrap | MEDIUM | Disable in production via config flag |
| Logout | Implemented | `backend/app/api/v1/auth.py:66-82` | Correct | LOW | OK |
| Logout-all | Implemented | `backend/app/api/v1/auth.py:85-96` | Correct | LOW | OK |
| Refresh token | **NOT IMPLEMENTED** | `backend/app/api/v1/auth.py`, `session.py` | **Missing** | HIGH | Implement in P0-A; sessions expire but no refresh path exists |
| Password change | **NOT IMPLEMENTED** | `backend/app/api/v1/auth.py` | **Missing** | HIGH | Required per CODING_RULES §11.1 |
| Password reset | **NOT IMPLEMENTED** | `backend/app/api/v1/auth.py` | **Missing** | HIGH | Required per CODING_RULES §11.1 |
| Session revoke (admin) | Implemented | `backend/app/api/v1/auth.py:121-136` | Correct | LOW | OK |
| User lifecycle states | Only `is_active` boolean | `backend/app/models/user.py:31` | Incomplete vs §11.3 | HIGH | Add status field (PENDING/ACTIVE/SUSPENDED/LOCKED/DEACTIVATED) in P0-A |
| Invite / activate flow | **NOT IMPLEMENTED** | `backend/app/` | Missing | MEDIUM | P0-A scope |
| Impersonation | Implemented with audit trail | `backend/app/models/impersonation.py`, `services/impersonation_service.py` | Correct | LOW | OK |
| SoD (requester ≠ decider) | Enforced in approval service | `backend/app/services/approval_service.py` | Correct | LOW | OK |
| FORBIDDEN_ACTING_ROLES | ADM/OTS cannot be impersonation targets | `backend/app/security/rbac.py:83` | Correct | LOW | OK |
| Plain-text password path | Falls back to plain comparison for non-hashed passwords | `backend/app/security/auth.py:68-75` | Risk if misconfigured | MEDIUM | Add explicit guard: log warning if plain comparison is used |
| Hardcoded role check in route | `if role_code != "SUP"` in operations router | `backend/app/api/v1/operations.py:314,344` | Violates §5.1 layering | HIGH | Move to service layer or RBAC dependency |
| JWT algorithm | HS256 with `change-me` default | `backend/app/config/settings.py:23` | Secure if env overridden | MEDIUM | Validate non-default key is set at startup; reject "change-me" in production mode |

---

## 7. Execution Domain

### 7.1 Summary Answers

- **Claim-owned or session-owned:** Currently **claim-owned** (`OperationClaim` table is live). This is declared migration debt per ENGINEERING_DECISIONS.md §10.1.
- **Station session:** NOT implemented. No `StationSession` table exists.
- **Claim present:** Yes — `OperationClaim`, `OperationClaimAuditLog`, full claim lifecycle in `station_claim_service.py`.
- **Operation statuses:** Stored as snapshot + derived from events. Snapshot updated in same transaction as event write. Event log is authoritative.
- **Event log append-only:** Yes — no update/delete path in `execution_event_repository.py`.
- **`report_production`:** `good_qty` + `scrap_qty` only — **rework qty is NOT modeled**.
- **`ABORTED` reachable:** Yes — via `abort_operation` endpoint.
- **`BLOCKED` reason modeled:** Partial — `BLOCKED` status derives from open downtime, but downtime reason is stored in event payload. No standalone `BLOCKED_REASON` enum or field on operation.
- **Quality/material/backflush mixed into execution:** No — `qc_required` flag exists on Operation but quality integration is not implemented. Execution stays clean.

### 7.2 Findings Table

| Execution Area | Current State | Evidence / File Path | Baseline Fit | Risk | Recommendation |
|---|---|---|---|---|---|
| Work order model | Present | `backend/app/models/master.py:58-88` | Correct | LOW | OK |
| Operation model | Present, well-modeled | `backend/app/models/master.py:90-148` | Correct | LOW | OK |
| Station model | No separate model — uses Scope | `backend/app/models/rbac.py:125` | Architectural decision | MEDIUM | Document; add dedicated Station/Equipment models in plant hierarchy slice |
| Equipment model | **NOT FOUND** | `backend/app/models/` | Missing | MEDIUM | Add in plant hierarchy slice |
| Operator identification | Via `operator_id` in OP_STARTED payload | `backend/app/services/operation_service.py:956` | Not session-bound | MEDIUM | Migration debt: target is station session ownership |
| Station session | **NOT IMPLEMENTED** | `backend/app/models/` | Missing — claim is migration debt | HIGH | Target state per ENGINEERING_DECISIONS §10.2 |
| Claim (OperationClaim) | Fully implemented | `backend/app/models/station_claim.py`, `services/station_claim_service.py` | Migration debt | MEDIUM | Keep as compatibility layer; do not extend; plan deprecation timeline |
| Start/pause/resume/complete | Implemented | `backend/app/services/operation_service.py` | Correct | LOW | OK |
| Downtime start/end | Implemented | `backend/app/services/operation_service.py:51-199` | Correct | LOW | OK |
| Close/reopen | Implemented | `backend/app/services/operation_service.py:847-941` | Correct | LOW | OK |
| Event log | Append-only `execution_events` | `backend/app/models/execution.py:37-61` | Correct | LOW | OK |
| Status derivation | From events — `_derive_status_from_runtime_facts` | `backend/app/services/operation_service.py:402-432` | Correct — event-sourced | LOW | OK |
| `allowed_actions` | Computed from event-derived status + closure_status | `backend/app/services/operation_service.py:709-748` | Correct — backend-driven | LOW | OK |
| Rework qty | **NOT MODELED** | `backend/app/services/operation_service.py:757-781` | Missing | MEDIUM | Add `rework_qty` to QTY_REPORTED event payload and quantity tracking |
| BLOCKED reason | Implicit via downtime payload | `backend/app/services/operation_service.py:166-175` | Partial | LOW | Acceptable for current scope |
| Event type naming inconsistency | Mix of UPPER_SNAKE (legacy) and lower_snake (canonical) | `backend/app/models/execution.py:20-34` | Known debt — comment present | MEDIUM | Migrate UPPER_SNAKE event types to lower_snake in migration debt cleanup |
| Hardcoded SUP role check in close/reopen routes | `if _effective_role_code(identity) != "SUP"` | `backend/app/api/v1/operations.py:314,344` | Violates route layering §5.1 | HIGH | Move to service layer or RBAC action dependency |
| Abort | Implemented via `abort_operation` | `backend/app/api/v1/operations.py:216-232` | Correct | LOW | OK — uses `require_permission("EXECUTE")` not `require_action` |

---

## 8. Quality / Material / Traceability / Integration

### 8.1 Summary Answers

- **Quality:** Frontend `QCCheckpoints.tsx` is a pure mock-data UI with no backend connection. No quality backend models, services, or routes exist. `qc_required` flag on Operation is a stub.
- **LAT/Pre-LAT:** Not found. Acceptance Gate is not modeled anywhere. No reference to "Acceptance Gate" found in backend code.
- **Backflush:** Not modeled. Zero backend code for material consumption or genealogy.
- **ERP integration:** Not modeled. Zero backend code for ERP posting or external ID mapping.
- **Traceability:** Frontend `Traceability.tsx` is a pure mock-data UI using ReactFlow. No backend.
- **Material staging/consumption:** Not modeled.
- **Integration messages:** Not modeled.

### 8.2 Findings Table

| Domain Area | Current State | Evidence / File Path | Baseline Fit | Risk | Recommendation |
|---|---|---|---|---|---|
| Quality inspection | Mock-only frontend | `frontend/src/app/pages/QCCheckpoints.tsx:23` | **Missing domain** | HIGH | Out of P0-A scope; clearly mark as placeholder |
| Quality measurement | Not found | `backend/app/models/` | **Missing** | HIGH | P1+ scope |
| Acceptance Gate / LAT | Not found | entire codebase | **Missing** | HIGH | Document as explicit out-of-scope for P0-A through Px; implement in quality slice |
| Quality hold / disposition | Not found | entire codebase | **Missing** | HIGH | P1+ scope |
| Nonconformance | Not found | entire codebase | **Missing** | HIGH | P1+ scope |
| Material staging | Not found | entire codebase | **Missing** | HIGH | P2+ scope |
| Material consumption / Backflush | Not found | entire codebase | **Missing** | HIGH | P2+ scope |
| Traceability / genealogy | Mock-only frontend | `frontend/src/app/pages/Traceability.tsx:37` | **Missing domain** | HIGH | P2+ scope |
| ERP integration | Not found | entire codebase | **Missing** | LOW | Out of FleziBCG scope (ERP truth principle) |
| `qc_required` flag on Operation | Stub present | `backend/app/models/master.py:132` | Stub only | LOW | Wire to quality domain in P1 slice |
| `QC_MEASURE_RECORDED` event type | Defined but unused | `backend/app/models/execution.py:23` | Stub | LOW | Wire when quality domain is built |

---

## 9. Tests / CI / Tooling

### 9.1 Summary Answers

- **Tests meaningful:** Yes — 12 backend tests cover execution lifecycle, claim constraints, auth guards, status projection reconciliation.
- **Core auth paths tested:** Partially — auth guards for close/start-downtime exist; no login/logout/session tests.
- **Execution paths tested:** Yes — claim lifecycle, close/reopen, downtime auth, allowed_actions, status projection.
- **Migrations tested:** No.
- **Frontend tests:** NONE.
- **CI present:** Only `frontend-i18n.yml`. No backend test CI, no lint CI, no security scan.
- **Lint/type/format enforcement:** Backend: Ruff (in requirements, CI not enforced). Frontend: ESLint (`npm run lint`), no TypeScript strict checks in CI.
- **Coverage:** Not configured.

### 9.2 Findings Table

| Test/Tool Area | Current State | Evidence / File Path | Risk | Recommendation |
|---|---|---|---|---|
| Backend unit tests | 12 files covering execution/claims/auth | `backend/tests/` | MEDIUM | Add login/logout/session/impersonation tests; add tenant isolation tests |
| Frontend tests | ABSENT | `frontend/src/` | HIGH | Add page-level and component tests per CODING_RULES §13.2 |
| Backend CI | ABSENT | `.github/workflows/` | **HIGH** | Add CI: `pytest -q`, `ruff check`, `ruff format --check`, `python -c "import app.main"` |
| Frontend CI | i18n lint only | `.github/workflows/frontend-i18n.yml` | HIGH | Add: `npm run build`, `eslint src/` |
| Security scanning | ABSENT | `.github/workflows/` | HIGH | Add dependency scanning (Dependabot or Snyk) |
| Test DB setup | Not visible (no conftest.py in listed files) | `backend/tests/` | MEDIUM | Add `conftest.py` with SQLite or test Postgres fixture |
| Migration tests | ABSENT | `backend/tests/` | HIGH | Required once Alembic is introduced |
| Coverage reporting | ABSENT | `backend/` | LOW | Add as informational baseline |

---

## 10. Runtime / DevOps / Config

### 10.1 Summary Answers

- **CloudBeaver dev-only?** No — it is in the primary `docker-compose.yml`, not an override. This violates SOURCE_STRUCTURE.md §5.
- **Secrets hard-coded?** `POSTGRES_PASSWORD: mes` is hardcoded in `docker-compose.yml`. `JWT_SECRET_KEY` defaults to "change-me" (intentional warning signal).
- **`.env` files safe?** `.env.example` exists. `docker/.env.db` is referenced. No evidence of secret leakage in committed files.
- **Production vs dev config separated?** No — single `settings.py` with `debug: bool = True` default; no explicit production profile.
- **Deployment aligned?** Yes — single compose file is appropriate for on-prem/cloud adaptable direction.

### 10.2 Findings Table

| Runtime Area | Current State | Evidence / File Path | Risk | Recommendation |
|---|---|---|---|---|
| CloudBeaver in primary compose | Present as default service | `docker-compose.yml:68-83` | **HIGH** — violates SOURCE_STRUCTURE §5 | Move to `docker/docker-compose.cloudbeaver.yml`; document as dev-only override |
| Hardcoded DB password in compose | `POSTGRES_PASSWORD: mes` | `docker-compose.yml:33` | MEDIUM for dev | Acceptable for local dev; document that production requires env override |
| JWT_SECRET_KEY default | "change-me" default with explicit comment | `backend/app/config/settings.py:23` | LOW (self-documenting) | Add startup validation: reject "change-me" when `app_env == "prod"` |
| Debug mode default | `debug: bool = True` | `backend/app/config/settings.py:16` | MEDIUM | Default to False; set True only via env override |
| CORS missing | No `CORSMiddleware` in app | `backend/app/main.py` | **HIGH** for any browser integration | Add CORSMiddleware with explicit origin list per environment |
| Uvicorn configuration | Not visible in Dockerfile | `backend/Dockerfile` | MEDIUM | Ensure uvicorn starts with `--host 0.0.0.0 --port 8010 --no-access-log` (logs via structured logger) |
| Backup strategy | Not implemented | entire codebase | LOW for current phase | Document backup approach for production |
| Production config separation | None — single settings.py | `backend/app/config/settings.py` | MEDIUM | Add `app_env` checks or `.env.production` template |

---

## 11. Baseline Compatibility Matrix

| Baseline Principle | Current State | Compliant? | Evidence |
|---|---|---|---|
| Backend is source of truth | Backend computes allowed_actions, enforces permissions | ✅ YES | `backend/app/services/operation_service.py:709` |
| Frontend never derives execution truth | Frontend reads allowed_actions from API | ✅ YES | `frontend/src/app/pages/StationExecution.tsx` |
| Persona is UX-only | Persona system is display/nav only | ✅ YES | `frontend/src/app/persona/personaLanding.ts` |
| JWT proves identity only | JWT carries sub/username/role_code as hints; backend checks DB | ✅ YES | `backend/app/security/auth.py:96-114` |
| Execution is event-driven / append-only | execution_events is append-only; status derived from events | ✅ YES | `backend/app/models/execution.py`, `operation_service.py:402` |
| AI is advisory only | No AI features implemented | ✅ N/A | Not applicable |
| Digital Twin is derived state | Not implemented | ✅ N/A | Not applicable |
| ERP is not replaced | No ERP integration | ✅ N/A | Not applicable |
| Acceptance Gate is canonical | Not implemented | ⚠️ N/A | Out of current scope |
| Backflush is cross-domain | Not implemented | ⚠️ N/A | Out of current scope |
| Station Execution is session-owned | Claim-owned (migration debt) | ⚠️ DEBT | `backend/app/models/station_claim.py` |
| Multi-tenant mandatory | tenant_id on all tables; enforced at query level | ✅ YES | `backend/app/models/*.py` |
| Modular monolith | Monorepo, single FastAPI app | ✅ YES | `backend/app/main.py` |
| ISA-95 aligned | Partial — PO/WO/Operation hierarchy; no Equipment/Station model | ⚠️ PARTIAL | `backend/app/models/master.py` |

---

## 12. Async Stack Decision

**Backend current stack is: SYNCHRONOUS**

Evidence:
- `backend/app/db/session.py`: `create_engine()` + sync `sessionmaker`
- `backend/app/main.py`: `async def auth_identity_middleware` but calls sync `decode_access_token`
- All service and repository functions are sync (`def`, not `async def`)
- Driver: `psycopg` (psycopg3 sync mode)
- FastAPI is framework-async but all handlers are `def` (sync)

**Recommendation: C — Stay sync for P0-A and revisit after foundation**

Rationale:
- The codebase is already functionally correct as a sync stack.
- FastAPI with sync handlers still handles concurrent requests (each in a threadpool worker).
- Migrating to full async (asyncpg, async SQLAlchemy, async session) is a high-effort refactor with significant correctness risk during a foundational database migration phase.
- The psycopg3 driver is already installed and capable of async if needed.
- P0-A should establish Alembic and stabilize the data model. Async migration can be a dedicated Engineering Decision after P0-A is stable.
- Document in ENGINEERING_DECISIONS.md: "Backend uses sync SQLAlchemy + psycopg3 sync driver. Full-async migration is deferred until after P0-A foundation is stable."

---

## 13. Frontend State Stack Decision

**Frontend current state stack is: React Context only (no React Query, no Zustand)**

Evidence:
- `frontend/package.json`: No `@tanstack/react-query` dependency.
- `frontend/src/app/auth/AuthContext.tsx`: Auth state via `useState`/`useCallback`.
- `frontend/src/app/impersonation/ImpersonationContext.tsx`: Impersonation state via Context.
- Server data is fetched ad-hoc (manual `useEffect` + `useState` in pages).
- No React Query mutation/invalidation pattern.

**Recommendation: A — Finalize React Query + Zustand as the target stack, with a migration plan**

Rationale:
- React Query provides cache invalidation, loading states, error states, and retry — all needed for MES real-time UIs.
- The current ad-hoc fetch pattern will not scale to 20+ pages without duplication and stale-state bugs.
- Zustand is appropriate for lightweight global client state (e.g., active impersonation banner state, toast queue).
- The existing Context providers (AuthContext, ImpersonationContext, I18nContext) are appropriate for their domains and should not be replaced with React Query — they are session-level singletons.
- Migration plan: introduce React Query in the next frontend implementation slice (not P0-A which is backend-focused). Migrate page-level data fetching incrementally.
- Document in ENGINEERING_DECISIONS.md: "Frontend server state management target: React Query + Zustand. Context retained for auth/session/i18n singletons. Migration to React Query is P1-FE scope."

---

## 14. P0-A Feasibility

**P0-A should be: HYBRID — Build new Alembic system on top of partially-valid existing tables**

Assessment:
- The tenant, IAM, user, session, role, action, and scope tables exist in the database schema (12 SQL migration files applied). They are functionally correct for the current use case.
- However, they were created with a custom SQL runner + `create_all()` — not Alembic.
- P0-A cannot safely proceed without replacing this migration infrastructure.
- The `User` model lacks lifecycle states (PENDING/ACTIVE/SUSPENDED/LOCKED/DEACTIVATED).
- Plant hierarchy tables are missing (Scope table supports hierarchy but is not a dedicated plant hierarchy model).
- There is no refresh token implementation.

**P0-A recommended scope:**
1. Introduce Alembic — create initial migration that reflects current schema state.
2. Remove `create_all()` from startup — migrations only.
3. Add `User.status` field with lifecycle states.
4. Add `RefreshToken` table + refresh token rotation flow.
5. Add dedicated `Plant`, `Area`, `Line`, `Station`, `Equipment` hierarchy tables (replacing current Scope-only approach or extending it).
6. Add global `security_events` / `audit_log` table.
7. Ensure all timestamp columns are `DateTime(timezone=True)` consistently.
8. Do NOT extend quality/material/ERP tables in P0-A.
9. Do NOT remove `OperationClaim` in P0-A — it is migration debt but still live.

**Blocked items:**
- CORS must be added before any integration environment testing.
- The CloudBeaver compose placement must be corrected before any infra PR.

---

## 15. Migration Debt Register

| Debt ID | Debt | Evidence / File Path | Severity | Fix Now? | Recommended Timing |
|---|---|---|---|---|---|
| DEBT-001 | No Alembic — custom SQL runner + create_all() | `backend/app/db/init_db.py:39-65` | **BLOCKER** | YES | P0-A |
| DEBT-002 | Claim-owned execution (deprecated, still live) | `backend/app/models/station_claim.py`, ENGINEERING_DECISIONS §10.1 | HIGH | NO | Post-P0-A station-session slice |
| DEBT-003 | No station session model | `backend/app/models/` | HIGH | NO | Station session implementation slice |
| DEBT-004 | User lifecycle states incomplete (only is_active) | `backend/app/models/user.py:31` | HIGH | YES | P0-A |
| DEBT-005 | No refresh token | `backend/app/api/v1/auth.py` | HIGH | YES | P0-A |
| DEBT-006 | No CORS configuration | `backend/app/main.py` | HIGH | YES | Immediate / P0-A |
| DEBT-007 | Hardcoded role check in route layer | `backend/app/api/v1/operations.py:314,344` | HIGH | YES | P0-A or next execution slice |
| DEBT-008 | CloudBeaver in primary docker-compose.yml | `docker-compose.yml:68` | HIGH | YES | Infra mechanical PR |
| DEBT-009 | No backend CI pipeline | `.github/workflows/` | HIGH | NO | Alongside P0-A |
| DEBT-010 | No React Query on frontend | `frontend/package.json` | MEDIUM | NO | P1-FE slice |
| DEBT-011 | `@supabase/supabase-js` dead dependency | `frontend/package.json:46` | MEDIUM | YES | Immediate mechanical PR |
| DEBT-012 | Mixed naive/timezone-aware DateTime columns | `backend/app/models/master.py:45,46` | MEDIUM | YES | P0-A migration |
| DEBT-013 | Event type naming inconsistency (UPPER vs lower) | `backend/app/models/execution.py:20-34` | MEDIUM | NO | Dedicated event envelope migration |
| DEBT-014 | Rework qty not modeled in report_production | `backend/app/services/operation_service.py:757` | MEDIUM | NO | Execution enhancement slice |
| DEBT-015 | No structured logging / correlation ID | `backend/app/` — no logging calls | MEDIUM | NO | P0-A or P1 observability slice |
| DEBT-016 | `debug: bool = True` default | `backend/app/config/settings.py:16` | MEDIUM | YES | Immediate config fix |
| DEBT-017 | FE Persona mode defaults to DEV (not STRICT) | `frontend/src/app/persona/personaLanding.ts:80` | MEDIUM | NO | Pre-production hardening |
| DEBT-018 | `docs/design/` vs `docs/business/design/` parallel trees | `docs/` | MEDIUM | NO | Docs consolidation sprint |
| DEBT-019 | CODING_RULES.md references wrong paths (`02_domain` instead of `business/design/02_domain`) | `docs/governance/CODING_RULES.md:29-33` | MEDIUM | YES | CODING_RULES v2.0 |
| DEBT-020 | No frontend tests | `frontend/src/` | MEDIUM | NO | P1-FE slice |
| DEBT-021 | `backend/app/i18n/` not in SOURCE_STRUCTURE.md | `docs/governance/SOURCE_STRUCTURE.md` | LOW | YES | SOURCE_STRUCTURE v1.2 |
| DEBT-022 | `frontend/supabase/` vestigial folder | `frontend/supabase/` | LOW | YES | Immediate mechanical PR |
| DEBT-023 | `app = FastAPI(title="MES Lite")` stale title | `backend/app/main.py:11` | LOW | NO | Next mechanical PR |
| DEBT-024 | `on_event("startup")` deprecated FastAPI API | `backend/app/main.py:14` | LOW | NO | P1 backend cleanup |
| DEBT-025 | No error boundary in frontend | `frontend/src/app/` | LOW | NO | P1-FE slice |

---

## 16. Risk Register

| Risk ID | Risk | Severity | Evidence | Impact | Recommendation |
|---|---|---|---|---|---|
| RISK-001 | No Alembic — schema drift undetectable in production | **BLOCKER** | `backend/app/db/init_db.py:65` | Schema corruption on production redeploy | Implement Alembic in P0-A before any production deployment |
| RISK-002 | CloudBeaver accessible in production compose | **HIGH** | `docker-compose.yml:68` | Unintended DB admin surface exposed | Move to dev-only override immediately |
| RISK-003 | No CORS configuration | **HIGH** | `backend/app/main.py` | Browser integration will fail or use insecure wildcard defaults | Add CORSMiddleware before any browser integration |
| RISK-004 | No refresh token — sessions expire mid-shift with no recovery | **HIGH** | `backend/app/api/v1/auth.py` | Operator forced to re-login mid-operation — execution integrity risk | Implement refresh token in P0-A |
| RISK-005 | Claim-owned execution is deprecated but still live | **HIGH** | `backend/app/models/station_claim.py` | Any new execution logic built on claim model creates deeper debt | Isolate claim code; build station session alongside; deprecate on schedule |
| RISK-006 | Quality/Material/Traceability entirely mock — not visible in backend | **HIGH** | `frontend/src/app/pages/QCCheckpoints.tsx` | Stakeholders may not realize these domains are unimplemented | Clearly label as out-of-scope in roadmap; do not demo as real |
| RISK-007 | No backend CI — regressions undetected | **HIGH** | `.github/workflows/` | Production-breaking changes can merge undetected | Add backend CI before P0-A implementation begins |
| RISK-008 | Hardcoded role check in routes violates layering contract | **HIGH** | `backend/app/api/v1/operations.py:314,344` | Role changes require route-level code changes; role drift not detectable | Move to service/RBAC layer |
| RISK-009 | User lifecycle incomplete | **HIGH** | `backend/app/models/user.py:31` | Cannot implement invite/activate/deactivate workflows | Add in P0-A |
| RISK-010 | No structured logging — incident diagnosis very difficult | **HIGH** | `backend/app/` | Cannot correlate events to tenant/user/operation | Add structured logging before production |
| RISK-011 | `@supabase/supabase-js` dead dependency — supply chain attack surface | **MEDIUM** | `frontend/package.json:46` | Unnecessary CVE exposure; confusing to reviewers | Remove in immediate mechanical PR |
| RISK-012 | Mixed DateTime timezone-awareness | **MEDIUM** | `backend/app/models/master.py:45` | Time comparison bugs in multi-timezone deployments | Fix in P0-A migration |
| RISK-013 | Event type naming mix (UPPER_SNAKE vs lower_snake) | **MEDIUM** | `backend/app/models/execution.py:20-34` | Event consumers must handle both formats | Clean up with dedicated migration |
| RISK-014 | Rework qty missing from report_production | **MEDIUM** | `backend/app/services/operation_service.py:757` | Rework tracking unavailable — OEE calculations incomplete | Add in execution enhancement slice |
| RISK-015 | Parallel `docs/design/` trees cause navigation confusion | **MEDIUM** | `docs/design/`, `docs/business/design/` | Contributors use wrong authoritative docs | Consolidate or add explicit README pointers |
| RISK-016 | No frontend tests | **MEDIUM** | `frontend/src/` | UI regressions undetected | Add before significant FE development |
| RISK-017 | `debug: bool = True` default | **MEDIUM** | `backend/app/config/settings.py:16` | Debug mode in production exposes internals | Fix immediately |
| RISK-018 | Persona enforcement defaults to DEV mode | **MEDIUM** | `frontend/src/app/persona/personaLanding.ts:80` | Wrong-role users can access any screen in DEV mode | Set STRICT for non-development environments |

---

## 17. Recommended Next Steps

**Immediate (before P0-A implementation begins):**

1. **Remove Supabase dependency + vestigial folder** — Mechanical PR. Remove `@supabase/supabase-js` from `frontend/package.json` and delete `frontend/supabase/` directory.
2. **Move CloudBeaver to dev-only override** — Mechanical PR. Create `docker/docker-compose.cloudbeaver.yml`; remove CloudBeaver from primary `docker-compose.yml`.
3. **Fix debug default** — Mechanical PR. Change `debug: bool = True` to `debug: bool = False` in `settings.py`.
4. **Add CORS middleware** — Intentional Behavior PR. Add `CORSMiddleware` with configurable allowed origins from settings.
5. **Fix hardcoded role check in routes** — Intentional Behavior PR. Move `role_code != "SUP"` logic to service layer or introduce `require_role` RBAC dependency.

**P0-A Implementation slice (required before production-ready foundation):**

6. **Introduce Alembic** — Architecture/Contract PR. Create `backend/alembic/` with initial migration capturing current schema state. Remove `create_all()` from startup. All future schema changes via Alembic.
7. **User lifecycle states** — Architecture/Contract PR. Add `status` field to User model (PENDING/ACTIVE/SUSPENDED/LOCKED/DEACTIVATED). Add lifecycle transition endpoints.
8. **Refresh token** — Architecture/Contract PR. Add `refresh_tokens` table and `/auth/refresh` endpoint with token rotation.
9. **Plant hierarchy tables** — Architecture/Contract PR. Add dedicated `plants`, `areas`, `lines`, `stations`, `equipment` tables or extend Scope model with explicit hierarchy support.
10. **Fix DateTime consistency** — Alembic migration. Make all timestamp columns `DateTime(timezone=True)`.
11. **Add backend CI** — Infrastructure PR. Add GitHub Actions workflow for: `pytest -q`, `ruff check .`, `ruff format --check .`, import check.
12. **Add startup JWT secret validation** — Intentional Behavior PR. Reject "change-me" secret when `app_env == "prod"`.

**Post-P0-A:**

13. **Introduce React Query** — P1-FE slice. Replace manual `useEffect`/`useState` data fetching with React Query hooks.
14. **Consolidate docs tree** — Documentation PR. Merge `docs/design/` and `docs/business/design/` or add clear authoritative README.
15. **Update CODING_RULES.md paths** — Mechanical PR. Fix path references from `docs/design/02_domain/` to `docs/business/design/02_domain/`.
16. **Add structured logging** — Intentional Behavior PR. Introduce structured logger with tenant_id, request_id, action_code context.
17. **Event type naming migration** — Migration debt slice. Normalize all event types to lower_snake per canonical naming standard.
18. **Station session model** — Dedicated execution slice. Implement StationSession to replace claim-owned execution per ENGINEERING_DECISIONS §10.2.

---

## 18. Recommended CODING_RULES v2.0 Adjustments

The following adjustments are recommended for `CODING_RULES.md` v2.0 before it is finalized:

1. **Section references — fix path discrepancy:** Update references in §0 ("For business and domain truth, see…") from `docs/design/02_domain/…` to `docs/business/design/02_domain/…` to match actual canonical file locations.

2. **Async stack decision — codify sync-first:** Add explicit statement: "Backend uses synchronous SQLAlchemy + psycopg3 until explicitly migrated. Do not introduce async session factories or async ORM without an Architecture/Contract PR and ENGINEERING_DECISIONS update."

3. **Frontend state management — codify React Query target:** Add explicit statement: "Frontend server state target is React Query. New pages must use React Query hooks for API data fetching. Context is reserved for auth/session/i18n singletons."

4. **Route layer rule — no role checks in routes:** Strengthen §5.1 Forbidden list to explicitly include: "• no hard-coded role code comparisons (`role_code != 'X'`) — role checks belong in RBAC dependencies or service layer."

5. **CORS as mandatory:** Add to §17 Security Rules: "CORS must be explicitly configured via CORSMiddleware. Wildcard `*` origin is forbidden in production."

6. **Refresh token as required:** Add to §11.1 Authentication lifecycle: "refresh token" to the required session lifecycle operations.

7. **No `create_all()` in production startup:** Add to §10.3 Migration discipline: "Do not call `Base.metadata.create_all()` in production startup. Schema changes are exclusively via Alembic migrations."

8. **Persona enforcement mode:** Add to §6.5 (Persona/navigation layer): "Persona enforcement mode must be STRICT in all non-development environments. DEV mode is permitted only for local development."

9. **Datetime policy:** Add explicit rule: "All `DateTime` columns must use `DateTime(timezone=True)`. Naive datetime columns are forbidden in new schema."

10. **Supabase/external dependency gate:** Add to §17 Security Rules: "Unused or vestigial dependencies from prior stack versions must be removed before merge."

11. **SOURCE_STRUCTURE drift:** Add: "Backend `app/i18n/` module is an approved addition to the backend folder structure for i18n-aware exception handling. SOURCE_STRUCTURE.md must be updated to reflect this."

---

## 19. Recommended Task 5 Implementation Strategy

**Task 5 (P0-A Foundation Database Slice) Strategy: Hybrid + Alembic-First**

### Phase A: Infrastructure gate (non-negotiable pre-work)
Before writing a single P0-A model, the following must be in place:
- Alembic initialized and capturing current schema as baseline migration
- `create_all()` removed from startup
- Backend CI with at minimum: `pytest`, `ruff check`, import validation
- CORS configured (even if permissive for dev)

### Phase B: P0-A Schema additions via Alembic
All additions must be isolated Alembic migrations with clear rollback strategy:
1. `users` table — add `status` column
2. `refresh_tokens` table — new
3. Plant hierarchy tables — new (`plants`, `areas`, `lines`, `stations`, `equipment`)
4. `security_events` / `audit_log` table — new
5. DateTime timezone normalization — ALTER columns

### Phase C: P0-A Backend service additions
1. `/auth/refresh` endpoint and refresh token rotation service
2. User lifecycle state transitions (activate, deactivate, suspend, lock, unlock)
3. Plant hierarchy CRUD service and routes
4. Scope node management aligned with new hierarchy tables

### Phase D: P0-A Validation
- All new paths covered by tests
- `pytest -q` passes in CI
- `ruff check` passes
- Alembic downgrade tested (at least -1 step)
- No `create_all()` in startup code

### Excluded from P0-A (explicitly):
- ERP integration, Acceptance Gate, Backflush, APS, AI, Digital Twin, Compliance/e-record, OPC UA/MQTT, Redis/Kafka/OPA
- Quality domain models
- Station session (OperationClaim stays as migration debt — do not touch)
- Frontend changes (P0-A is backend database foundation only)

---

## Summary Verdict

The FleziBCG codebase is **architecturally sound but not yet production-ready**. The backend layering, event-driven execution model, auth/session design, and tenant isolation are all correctly implemented and well-reasoned. The execution domain is functional and covers the critical operator lifecycle.

The primary blockers before production trust can be established are: (1) absence of Alembic making schema management uncontrolled, (2) missing CORS configuration, (3) no refresh token leaving operators session-stranded mid-shift, (4) incomplete user lifecycle, and (5) no backend CI allowing regressions to ship silently.

Quality, Material, Traceability, and ERP domains exist only as frontend mock placeholders — this is expected for the current phase but must not be presented as functional.

The codebase is **ready for CODING_RULES v2.0 finalization** after the path reference fixes and the async/frontend-state/CORS additions are incorporated.

The codebase is **conditionally ready for P0-A implementation** — conditional on the Alembic infrastructure gate being completed first. P0-A must not be written against the current `create_all()` startup model.

---

## Top 10 Risks

1. RISK-001 — No Alembic: schema drift risk in production (**BLOCKER**)
2. RISK-003 — No CORS configuration (**HIGH**)
3. RISK-004 — No refresh token: mid-shift auth expiry (**HIGH**)
4. RISK-007 — No backend CI: regressions undetected (**HIGH**)
5. RISK-002 — CloudBeaver in production compose (**HIGH**)
6. RISK-005 — Claim-owned execution is deprecated but still live (**HIGH**)
7. RISK-009 — User lifecycle incomplete (**HIGH**)
8. RISK-010 — No structured logging (**HIGH**)
9. RISK-008 — Hardcoded role check in routes (**HIGH**)
10. RISK-006 — Quality/Material/Traceability are entirely mock (**HIGH**)

## Top 10 Recommended Actions

1. **Introduce Alembic in P0-A** — non-negotiable before production
2. **Add CORS middleware** — immediate fix
3. **Implement refresh token** — P0-A
4. **Add backend CI pipeline** — before P0-A implementation starts
5. **Move CloudBeaver to dev-only compose override** — immediate mechanical PR
6. **Fix hardcoded role checks in routes** — next intentional behavior PR
7. **Complete User lifecycle states** — P0-A
8. **Remove Supabase dead dependency** — immediate mechanical PR
9. **Add structured logging** — P0-A or P1 observability
10. **Consolidate docs tree and fix CODING_RULES path references** — CODING_RULES v2.0 PR

## Recommendation on CODING_RULES v2.0 Finalization

**PROCEED** — with the 11 adjustments listed in Section 18 incorporated. The existing CODING_RULES are well-written and cover the critical governance areas. The adjustments are additive corrections to path references and explicit codifications of decisions that are already implemented but undocumented in the rules.

## Recommendation on Task 5 P0-A Implementation

**PROCEED — conditionally.** The architectural foundation is solid enough for P0-A to build on. However, the **Alembic infrastructure gate must be completed first** (estimated 1 day of work). P0-A written against the current `create_all()` model will create additional migration debt immediately. Once Alembic is in place and backend CI is running, P0-A can proceed on the schema additions described in Section 19.
