# Source Structure

Monorepo layout, entrypoints, folder ownership, and frozen contract baselines.

---

## 1. Repository Layout

```
/
├── backend/                 # Python / FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/                 # Application package
│   │   ├── main.py          # ← BACKEND ENTRYPOINT
│   │   ├── api/v1/          # Route handlers
│   │   ├── config/          # Settings (pydantic-settings)
│   │   ├── db/              # Session factory, base, init + seed
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── repositories/    # Data access (tenant-filtered)
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── security/        # JWT auth, RBAC, route dependencies
│   │   └── services/        # Business logic
│   └── scripts/             # Verification & seed scripts
│       ├── seed/            # Deterministic seed (S1–S4)
│       ├── migrations/      # DB migrations
│       ├── verify_users_auth.py
│       ├── verify_approval.py
│       ├── verify_impersonation.py
│       ├── verify_station_claim.py
│       ├── verify_station_queue_claim.py
│       ├── verify_clock_on.py
│       └── verify_clock_off.py
│
├── frontend/                # React / TypeScript frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── eslint.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx         # ← FRONTEND ENTRYPOINT
│       ├── lib/             # Shared utilities (cn())
│       ├── styles/          # CSS: index.css, tailwind.css, theme.css
│       ├── types/           # Shared TypeScript types
│       ├── assets/          # Static assets
│       └── app/             # Application code
│           ├── App.tsx      # Root component
│           ├── routes.tsx   # React Router tree
│           ├── api/         # API clients + httpClient
│           ├── auth/        # AuthContext, RequireAuth
│           ├── components/  # Shared components + ui/ primitives
│           ├── data/        # Mock data (dev only)
│           ├── i18n/        # i18n key infrastructure
│           ├── impersonation/ # ImpersonationContext
│           ├── pages/       # Page components
│           └── persona/     # Role→landing page redirect (UX only)
│
├── docker-compose.yml       # Orchestration (4 services)
├── docker/                  # Dev-only compose overrides
├── docs/                    # Architecture, phases, specs
├── .github/                 # CI config, copilot instructions
└── pyrightconfig.json       # Python type-checking config
```

---

## 2. Entrypoints

| Surface | File | What it does |
|---------|------|--------------|
| **Backend** | `backend/app/main.py` | Creates `FastAPI(title="MES Lite")`, mounts all routers via `app.include_router(api_router)`, runs `init_db()` on startup, adds auth middleware |
| **Frontend** | `frontend/src/main.tsx` | Renders `<App />` into `#root`, imports global styles |
| **Docker** | `docker-compose.yml` | Starts `db`, `backend`, `frontend`, `cloudbeaver` on `mes-network` |

---

## 3. Backend Folder Ownership

| Folder | Owner | Responsibility |
|--------|-------|---------------|
| `api/v1/` | Route layer | Thin HTTP handlers — auth gating, request validation, delegate to services |
| `services/` | Service layer | All business logic — execution flow, approval workflow, impersonation, RBAC enforcement |
| `repositories/` | Data layer | SQLAlchemy queries — every query MUST filter by `tenant_id` |
| `models/` | ORM layer | SQLAlchemy table definitions — no logic |
| `schemas/` | Contract layer | Pydantic models for request/response — no side effects |
| `security/` | Security layer | JWT encode/decode (`auth.py`), FastAPI deps (`dependencies.py`), RBAC checks (`rbac.py`) |
| `config/` | Config layer | `settings.py` — pydantic-settings `BaseSettings`, env-driven |
| `db/` | Database layer | Session factory (`session.py`), declarative base (`base.py`), init + seed (`init_db.py`) |

### Backend Routes (api/v1/)

| File | Endpoint prefix | Domain |
|------|----------------|--------|
| `auth.py` | `/auth` | Login, token refresh |
| `operations.py` | `/operations` | Operation CRUD, start, complete, block |
| `production_orders.py` | `/production-orders` | Production order queries |
| `dashboard.py` | `/dashboard` | Dashboard aggregation |
| `approvals.py` | `/approvals` | Approval request / decision |
| `impersonations.py` | `/impersonations` | Impersonation session management |
| `iam.py` | `/iam` | User and role management |
| `station.py` | `/station` | Station claims and execution |
| `execution_timeline.py` | `/execution-timeline` | Timeline event queries |

### Backend Services

| File | Domain |
|------|--------|
| `operation_service.py` | Operation execution (start / complete / block) |
| `global_operation_service.py` | Cross-tenant operation queries |
| `work_order_execution_service.py` | Work order execution flow + status recomputation |
| `dashboard_service.py` | Dashboard metric aggregation |
| `approval_service.py` | Approval request / decision workflow |
| `impersonation_service.py` | Impersonation session lifecycle |
| `iam_service.py` | Identity & access management |
| `user_service.py` | User CRUD |
| `session_service.py` | Login session management |
| `station_claim_service.py` | Station claim logic |
| `execution_timeline_service.py` | Timeline event queries |

---

## 4. Frontend Folder Ownership

| Folder | Owner | Responsibility |
|--------|-------|---------------|
| `pages/` | Page layer | Full-page views — compose components, call API, manage page state |
| `components/` | Component layer | Reusable UI — receives data via props, no direct API calls |
| `components/ui/` | Primitive layer | shadcn/ui + Radix primitives (48 components) — zero business logic |
| `api/` | API layer | `httpClient.ts` (auto-injects Bearer token + X-Tenant-ID), domain API clients |
| `auth/` | Auth layer | `AuthContext` (JWT storage), `RequireAuth` route guard |
| `persona/` | Persona layer | Role→landing page mapping — UX only, NOT authorization |
| `impersonation/` | Impersonation layer | `ImpersonationContext` — banner + session management |
| `i18n/` | i18n layer | Key definitions, namespace registry, `useI18n` hook |
| `styles/` | Style layer | `theme.css` (61 CSS custom properties), `tailwind.css`, `index.css` |
| `lib/` | Utility layer | `cn()` class-name merge utility |
| `types/` | Type layer | Shared TypeScript interfaces |
| `data/` | Mock data | Dev-only mock datasets |

### Frontend Pages (20)

| Page | Purpose |
|------|---------|
| `LoginPage` | Auth entry |
| `Home` | Landing redirect |
| `Dashboard` | KPI overview |
| `StationExecution` | Station-level execution (primary write surface) |
| `GlobalOperationList` | Cross-WO operation monitor |
| `OperationList` | WO-scoped operation list |
| `OperationExecutionOverview` | Operation execution summary |
| `OperationExecutionDetail` | Single operation execution |
| `ProductionOrderList` | PO listing |
| `Production` | Production overview |
| `ProductionTracking` | Production progress tracking |
| `OEEDeepDive` | OEE analytics |
| `APSScheduling` | Scheduling view |
| `DispatchQueue` | Dispatch queue |
| `RouteList` / `RouteDetail` | Manufacturing routes |
| `QCCheckpoints` | Quality control |
| `DefectManagement` | Defect tracking |
| `Traceability` | Traceability view |
| `GanttStressTestPage` | Gantt chart stress test (dev) |

---

## 5. Docker Orchestration

`docker-compose.yml` defines 4 services on `mes-network` (bridge):

| Service | Image / Build | Port | Healthcheck |
|---------|--------------|------|-------------|
| `db` | `postgres:15` | 5432 | `pg_isready` |
| `backend` | `./backend` (Dockerfile) | 8010 | `/docs` endpoint (curl) |
| `frontend` | `./frontend` (Dockerfile, nginx) | 80 | `wget -qO-` to localhost |
| `cloudbeaver` | `dbeaver/cloudbeaver:latest` | 8978 | `curl -sf` to localhost |

Shared volume: `docker_postgres_data` (external, persists across rebuilds).

---

## 6. Frozen Contract Baselines

These hashes represent the canonical public API surface. Any PR that changes these must be an **intentional contract change** with updated baselines.

| Artifact | SHA-256 | Method |
|----------|---------|--------|
| **Routes inventory** | `d2549a0c591214c676f8812e23fcbc23a4bd42afd3e8c1da19a164c68fd967d1` | `set(METHOD, path)` excluding HEAD/OPTIONS, sorted by `(path, method)`, piped to `sha256sum` |
| **OpenAPI schema** | `4b945ee9cd9dfcb2a53cad19b97984306b445b0289e264680780f34d617412a6` | `json.dumps(app.openapi(), sort_keys=True, separators=(',', ':'))` piped to `sha256sum` |

Verification commands are documented in [CODING_RULES.md](CODING_RULES.md#25-contract-gates-sha-baseline).

---

## 7. Key Configuration Files

| File | Purpose |
|------|---------|
| `backend/requirements.txt` | Python dependencies (pinned) |
| `frontend/package.json` | Node dependencies + scripts |
| `frontend/tsconfig.json` | TypeScript config — `@/*` path alias, ES2022 target |
| `frontend/vite.config.ts` | Vite config — `@/` resolve alias, Tailwind plugin |
| `frontend/eslint.config.js` | ESLint flat config — boundary rules, hex color warning |
| `frontend/postcss.config.mjs` | PostCSS config |
| `pyrightconfig.json` | Pyright type-checking |
| `.github/copilot-instructions.md` | AI assistant system constraints |
