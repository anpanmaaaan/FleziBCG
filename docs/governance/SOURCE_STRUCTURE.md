# Source Structure

Monorepo layout, entrypoints, folder ownership, and public contract baselines.

This document is authoritative for:
- repository structure
- entrypoints
- folder/module ownership
- runtime surfaces
- frozen public API baselines

This document is **not** authoritative for:
- business logic
- coding conventions
- API style rules
- DB migration rules
- IAM/session rules
- AI engineering rules

For those, see:
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`

---

## 1. Repository Layout

```text
/
├── backend/                 # Python / FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/                 # Application package
│   │   ├── main.py          # Backend entrypoint
│   │   ├── api/v1/          # Route handlers
│   │   ├── config/          # Settings / configuration
│   │   ├── db/              # Session factory, base, init
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── repositories/    # Data access
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── security/        # JWT auth, RBAC, route dependencies
│   │   └── services/        # Business logic
│   └── scripts/             # Seed, verify, maintenance scripts
│
├── frontend/                # React / TypeScript frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── eslint.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx         # Frontend entrypoint
│       ├── lib/             # Shared utilities
│       ├── styles/          # Global CSS / theme / Tailwind
│       ├── types/           # Shared frontend types
│       ├── assets/          # Static assets
│       └── app/             # Application code
│           ├── App.tsx      # Root component
│           ├── routes.tsx   # Router tree
│           ├── api/         # API clients + http client
│           ├── auth/        # Auth state + route guard
│           ├── components/  # Shared components + UI primitives
│           ├── data/        # Mock data (dev only)
│           ├── i18n/        # i18n infrastructure
│           ├── impersonation/ # Support/impersonation UX
│           ├── pages/       # Page-level views
│           └── persona/     # UX-only landing/menu behavior
│
├── docker-compose.yml       # Orchestration
├── docker/                  # Dev-only compose overrides
├── docs/                    # Architecture, governance, business docs
├── .github/                 # CI, entry instructions
└── pyrightconfig.json       # Python type-checking config
```

---

## 2. Entrypoints

| Surface   | File                      | Responsibility                                 |
|-----------|---------------------------|------------------------------------------------|
| Backend   | backend/app/main.py       | Build FastAPI app, mount routers, startup/init |
| Frontend  | frontend/src/main.tsx     | Render <App />, load global styles             |
| Docker    | docker-compose.yml        | Start core services and orchestration           |

---

## 3. Backend Folder Ownership

| Folder         | Ownership      | Responsibility                                 |
|----------------|---------------|------------------------------------------------|
| api/v1/        | Route layer   | Thin HTTP handlers: request parsing, validation |
| services/      | Service layer | Business logic, orchestration, transactions     |
| repositories/  | Data access   | Persistence and query logic only                |
| models/        | ORM layer     | SQLAlchemy table/entity definitions             |
| schemas/       | Contract      | Pydantic request/response contracts             |
| security/      | Security      | Auth dependencies, JWT, RBAC helpers            |
| config/        | Config        | Settings and environment loading                |
| db/            | Database      | Session factory, base, initialization           |

---

## 4. Frontend Folder Ownership

| Folder        | Ownership      | Responsibility                                 |
|---------------|---------------|------------------------------------------------|
| pages/        | Page layer    | Full-page orchestration, route-level state      |
| components/   | Component     | Reusable UI, props-driven rendering             |
| api/          | API layer     | HTTP client + domain API wrappers               |
| auth/         | Auth layer    | Auth context, session state, guards             |
| persona/      | UX layer      | UX-only landing/menu behavior                   |
| impersonation/| Support       | Active impersonation banner/state               |
| i18n/         | i18n layer    | i18n keys, lookup hooks, namespace structure    |
| styles/       | Style layer   | Theme, Tailwind, global CSS                     |
| lib/          | Utility       | Shared helper utilities                         |
| types/        | Type layer    | Shared TypeScript interfaces/types              |
| data/         | Dev data      | Mock-only development data                      |

---

## 5. Runtime Surfaces

| Service     | Purpose                                 |
|-------------|-----------------------------------------|
| db          | PostgreSQL                              |
| backend     | FastAPI backend                         |
| frontend    | Vite / nginx frontend surface           |
| cloudbeaver | DB inspection / admin tooling           |

---

## 6. Frozen Public Contract Baselines

These hashes represent the canonical public API surface. Any change to these must be treated as an intentional contract change.

| Artifact           | SHA-256                                                        | Method                                    |
|--------------------|---------------------------------------------------------------|-------------------------------------------|
| Routes inventory   | d2549a0c591214c676f8812e23fcbc23a4bd42afd3e8c1da19a164c68fd967d1 | Sorted route inventory excluding HEAD/OPTIONS |
| OpenAPI schema     | 4b945ee9cd9dfcb2a53cad19b97984306b445b0289e264680780f34d617412a6 | Canonical JSON dump of app.openapi()      |

Exact verification procedure is defined in docs/governance/CODING_RULES.md.

---

## 7. Key Configuration Files

| File                    | Purpose                                 |
|-------------------------|-----------------------------------------|
| backend/requirements.txt| Python dependencies                     |
| frontend/package.json   | Node dependencies and scripts           |
| frontend/tsconfig.json  | TypeScript configuration                |
| frontend/vite.config.ts | Vite build config                       |
| frontend/eslint.config.js| ESLint configuration                   |
| pyrightconfig.json      | Python type checking                    |
| .github/copilot-instructions.md | Entry instructions only          |

---

## 8. Ownership Boundaries

This document intentionally does not define:
	• tenant isolation policy
	• approval semantics
	• role/permission truth
	• session lifecycle semantics
	• AI behavior rules
	• execution lifecycle rules
Those belong to:
	• docs/design/00_platform/product-business-truth-overview.md
	• docs/governance/CODING_RULES.md
	• docs/governance/ENGINEERING_DECISIONS.md
