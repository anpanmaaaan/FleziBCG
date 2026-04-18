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
```

---

## 2. Ownership & Baselines

- Each folder is owned by the corresponding engineering team (backend, frontend, infra).
- Entry points are frozen for contract stability.
- Public API and DB contracts are baseline-locked; changes require contract PR.
- This file does not define business rules, coding conventions, or governance constraints.
- For those, see:
  - `docs/governance/CODING_RULES.md`
  - `docs/governance/ENGINEERING_DECISIONS.md`
  - `docs/system/mes-business-logic-v1.md`
