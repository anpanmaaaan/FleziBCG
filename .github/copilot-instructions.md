# MOM Lite — Project Instructions
Before coding, read .github/agent/CODING_RULES.md and .github/agent/SOURCE_STRUCTURE.md.

## Project Overview

Lightweight Manufacturing Operations Management (MOM) system, ISA‑95 aligned. Modular monolith — do NOT split into microservices.

| Area | Path | Stack |
|------|------|-------|
| Backend | `backend/` | Python 3.12, FastAPI, SQLAlchemy 2.x, PostgreSQL, JWT (python-jose), Argon2, Pydantic 2 |
| Frontend | `frontend/` | React 18, TypeScript, Vite, React Router 7, Radix UI, Tailwind CSS 4, Recharts |
| Docs | `docs/` | Architecture decisions, phase gates, business logic contract |

## Build & Run

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010     # Dev: http://localhost:8010

# Frontend
cd frontend
npm install
npm run dev                                  # Dev: http://localhost:5173 (Vite default)
npm run build                                # Production build (must pass with zero TS errors)

# Docker (all services)
docker-compose up                            # Backend:8010, Frontend:80, DB:5432, CloudBeaver:8978

# Seed & verify (after DB is running)
cd backend
python -m scripts.seed.seed_all              # Deterministic seed scenarios S1–S4
python scripts/verify_users_auth.py          # Auth verification
python scripts/verify_approval.py            # Approval workflow verification
python scripts/verify_impersonation.py       # Impersonation verification
```

## Architecture Rules

- **Backend is source of truth** — frontend is a dumb view, never derives execution state
- **Event-driven execution** — `ExecutionEvent` is append-only; status is derived from events. A cached `status` column exists on `Operation` as a materialized projection, updated in the same transaction as the event write.
- **Tenant isolation mandatory** — tenant isolation is enforced at the route/service boundary. Repository functions MAY assume tenant context is already validated by the caller. Not every repository function filters by `tenant_id` directly.
- **Service layer owns business rules** — repositories are data access only, routes are thin
- **Pydantic schemas** for all request/response contracts
- **Backend returns enums/codes only** — no translated text (i18n-ready)

## Execution Flow (LOCKED)

Entry: Work Order → Operations. Execution state mutations occur in the **operations API / service layer**. Station APIs handle station **claim/release** only.

```
PLANNED ──[start]──→ IN_PROGRESS ──[report_qty]──→ IN_PROGRESS
                          │
                     [complete] or [abort]
                          ↓
                    COMPLETED or ABORTED
```

Valid states: `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `ABORTED`. No other states exist.
- `PENDING` does NOT exist — the initial state is `PLANNED`.
- `BLOCKED` does NOT exist — the abort terminal state is `ABORTED`.
- Status is **derived** from the append-only `ExecutionEvent` log via `_derive_status()`. A cached `status` column on `Operation` is a materialized projection, not the source of truth.
- Execution entry starts at Work Order, NOT Production Order
- Operation is the smallest execution unit
- **Station Execution** is a UI/UX concept (the operator's write surface). Under the hood, execution mutations flow through `app/api/v1/operations.py` → `app/services/operation_service.py`. Station APIs (`app/api/v1/station.py`) handle station **claim/release** only — they do NOT mutate execution state.
- Do NOT introduce screens mixing PO, WO, and Operation execution semantics

## Backend Module Map

| Layer | Path | Purpose |
|-------|------|---------|
| Routes | `app/api/v1/` | Thin handlers (auth, operations, dashboard, approval, impersonation, iam, station, execution_timeline, production_orders) |
| Services | `app/services/` | Business logic (operation_service, approval_service, impersonation_service, iam_service, dashboard_service, global_operation_service, work_order_execution_service, station_claim_service, session_service, user_service, execution_timeline_service) |
| Repositories | `app/repositories/` | Data access with tenant filtering |
| Models | `app/models/` | SQLAlchemy ORM (master, execution, rbac, approval, impersonation, station_claim, user, session) |
| Schemas | `app/schemas/` | Pydantic request/response |
| Security | `app/security/` | JWT auth, RBAC permission checks, route dependencies |
| DB | `app/db/` | Session factory, base, init (migrations + seed) |

## Frontend Module Map

| Module | Path | Purpose |
|--------|------|---------|
| Pages | `src/app/pages/` | LoginPage, Dashboard, StationExecution, GlobalOperationList |
| API | `src/app/api/` | API clients; `httpClient.ts` auto-injects Bearer token + X-Tenant-ID |
| Auth | `src/app/auth/` | AuthContext, RequireAuth guard |
| Persona | `src/app/persona/` | Role→landing page redirect + route visibility gating (UX only, NOT authorization) |
| i18n | `src/app/i18n/` | i18n key infrastructure; `useI18n` hook is wired and used at runtime |
| Components | `src/app/components/` | Layout, GanttChart, StatusBadge, ActiveImpersonationBanner, TopBar, PageHeader |
| Routes | `src/app/routes.tsx` | React Router tree |

## Coding Conventions

- Keep modules small and explicit
- Prefer service layer over putting logic in route handlers
- Repository layer must not contain business rules
- Use Pydantic schemas for request/response
- Write clear names, avoid magic values
- Do not over-engineer
- Do not introduce Kafka, microservices, or cloud-only dependencies
- All new UI text MUST use semantic i18n keys (Phase 5A onward)

### Naming

| Context | Convention | Example |
|---------|-----------|---------|
| Backend services | snake_case verbs | `start_operation()`, `create_approval_request()` |
| Frontend APIs | camelCase objects | `operationApi.start()`, `approvalApi.create()` |
| Routes | kebab-case | `/api/v1/operations/{id}/start` |
| Models | PascalCase | `ProductionOrder`, `ExecutionEvent` |
| DB tables | snake_case | `production_orders`, `execution_events` |

## Governance (Phase 6 — LOCKED)

Full governance specification: `docs/system/mes-business-logic-v1.md`

### Critical Rules (Always Enforced)

**RBAC — 5 permission families (VIEW, EXECUTE, APPROVE, CONFIGURE, ADMIN):**
- Frozen role→family mappings. Do NOT modify without Phase 7+ design gate.
- OPR→EXECUTE, SUP→VIEW+EXECUTE, IEP→VIEW+CONFIGURE, QAL→VIEW+APPROVE, PMG→VIEW+APPROVE, ADM→VIEW+ADMIN

**MOM Business Roles (official role set for all new features):**

| Code | MOM Role | Domain | Permissions | Forbidden |
|------|----------|--------|-------------|-----------|
| OPR | Operator | Shop-floor execution | EXECUTE | Cannot approve, configure, or admin |
| SUP | Supervisor | Shift oversight | VIEW, EXECUTE | Cannot approve or admin |
| IEP | IE / Process Engineer | Routing, standards | VIEW, CONFIGURE | Cannot execute or approve |
| QAL | QC Lead / Approver | Quality approval | VIEW, APPROVE | Cannot execute or admin |
| PMG | Production Manager | Planning approval | VIEW, APPROVE | Cannot execute or admin |
| ADM | Administrator | System admin | VIEW, ADMIN | Cannot execute (must impersonate OPR) |

**Non-MOM / Technical Roles (exist in code, NOT part of MOM business role set):**

| Code | Purpose | Permissions | Notes |
|------|---------|-------------|-------|
| OTS | On-The-Spot support | VIEW, ADMIN | Can impersonate; same restrictions as ADM. System/support role only. |
| QCI | QC Inspector | VIEW | Read-only variant for QC viewing. |
| EXE | Execution viewer | VIEW | Read-only technical viewer. |

Non-MOM roles MUST NOT be used as targets for new MOM features. New features MUST map to the official MOM role set above.

**Separation of duties:**
- `requester_id ≠ decider_user_id` — even under impersonation
- Both RBAC check AND approval_rules check must pass
- Audit logs (approval + impersonation) are append-only, never deleted

**Impersonation:**
- Only ADM/OTS can impersonate; cannot impersonate other admins
- Time-bound: default 60 min, max 480 min
- Does NOT bypass separation of duties or escalate permissions

**Persona:**
- UX-only (landing page + menu visibility), NOT authorization
- Frontend NEVER checks permissions — backend decides via 403

**Authentication vs Authorization are completely separate:**
- JWT proves identity only; do NOT encode permissions in JWT
- `role_code` is carried in the JWT as a **display hint**, not a security gate — authorization is checked per-request on the backend via `has_permission()` against the static role→family map

### Forbidden Without Phase 7+ Gate

- Adding/renaming permission families or changing role mappings
- Bypassing approval for QC/scrap/rework actions
- Encoding permission logic in frontend
- Removing tenant isolation from any repository
- Adding new impersonator roles
- Modifying execution state machine without updating business logic docs
- Introducing APS/scheduling logic into execution layer
- Granting EXECUTE to ADM/OTS

### Verification Discipline

After changes to execution, governance, or approval logic:

```bash
# All checks must PASS
cd backend
python scripts/verify_users_auth.py
python scripts/verify_approval.py
python scripts/verify_impersonation.py
```

After frontend changes: `cd frontend && npm run build` (zero TS errors required).

Business logic changes must be reflected in `docs/system/mes-business-logic-v1.md`.

## Key Documentation

| Topic | Path |
|-------|------|
| Business logic contract (authoritative) | `docs/system/mes-business-logic-v1.md` |
| Architecture overview | `docs/architecture/SYSTEM_OVERVIEW.md` |
| Execution model | `docs/architecture/EXECUTION_MODEL.md` |
| Read/write separation | `docs/architecture/READ_WRITE_SEPARATION.md` |
| i18n strategy | `docs/architecture/I18N_STRATEGY.md` |
| AI guardrails | `docs/architecture/AI_GUARDRAILS.md` |
| Phase gates | `docs/phases/PHASE_*.md` |
| Persona map | `docs/personas/PERSONA_MAP.md` |
| Demo accounts | `DEMO_ACCOUNTS.md` |

## Non-Goals

- No AI control of execution (advisory only, read-only access to events)
- No advanced scheduling / APS
- No external workflow engine
- No streaming platform (Kafka, etc.)
- No premature microservice extraction