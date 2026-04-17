# Coding Rules

Mandatory rules for every contributor. Violations block merge.

---

## 1. Mechanical-Refactor Policy

| Rule | Detail |
|------|--------|
| **No runtime-behavior changes** | Do not change runtime behavior unless the PR description explicitly states the intent. |
| **Preserve public APIs** | The OpenAPI schema and route inventory must be identical before and after. Any diff blocks merge. |
| **No feature creep** | Do not add features, refactor unrelated code, or make "improvements" beyond the stated scope. |
| **No speculative abstractions** | Do not create helpers, wrappers, or abstractions for one-time operations. |
| **No unnecessary additions** | Do not add docstrings, comments, or type annotations to code you did not change — **unless** the PR is explicitly scoped to that purpose (e.g., "add maintenance comments", "add return-type hints"). In that case the PR description must state the scope and changes must stay within it. |

---

## 2. Verification Requirements

Every PR that touches backend code **must** pass the following gates before merge.

### 2.1 Import Check

```bash
cd backend
python -c "import app.main; print('import ok')"
```

Expected output: `import ok`

### 2.2 Ruff Lint

```bash
cd backend
source ../.venv/bin/activate
ruff check .
```

Expected output: `All checks passed!`

### 2.3 Ruff Format

```bash
cd backend
source ../.venv/bin/activate
ruff format --check .
```

Expected output: `N files already formatted.` (no reformatting needed)

### 2.4 Pytest

```bash
cd backend
source ../.venv/bin/activate
python -m pytest -q
```

Must exit 0. Any failure blocks merge.

### 2.5 Contract Gates (SHA baseline)

Before **and** after the PR, capture the route inventory and OpenAPI schema using canonical scripts, then compare SHA-256 hashes. A mismatch blocks merge.

```bash
# Routes snapshot (excludes auto-generated HEAD/OPTIONS)
cd backend
python -c "
from app.main import app
lines = set()
for r in app.routes:
    for m in sorted(getattr(r, 'methods', set()) - {'HEAD', 'OPTIONS'}):
        lines.add(f'{m} {r.path}')
for l in sorted(lines, key=lambda x: (x.split(' ',1)[1], x.split(' ',1)[0])):
    print(l)
" | sha256sum

# OpenAPI snapshot (compact JSON, sorted keys)
cd backend
python -c "
import json
from app.main import app
print(json.dumps(app.openapi(), sort_keys=True, separators=(',', ':')))
" | sha256sum
```

Frozen baselines (updated when a contract-changing PR lands):

| Artifact | SHA-256 |
|----------|---------|
| Routes | `d2549a0c591214c676f8812e23fcbc23a4bd42afd3e8c1da19a164c68fd967d1` |
| OpenAPI | `4b945ee9cd9dfcb2a53cad19b97984306b445b0289e264680780f34d617412a6` |

### 2.6 Frontend Build

Every PR that touches frontend code must produce a clean build:

```bash
cd frontend
npm run build
```

Zero TypeScript errors required.

### 2.7 Docker Healthchecks

After infra changes (`docker-compose.yml`, Dockerfiles):

```bash
docker-compose up -d
docker ps   # all 4 services must show (healthy)
```

---

## 3. Comment Style Guidelines

Use structured comment prefixes to explain non-obvious code. Do **not** comment what the code does — comment **why**.

| Prefix | When to use | Example |
|--------|-------------|---------|
| `WHY:` | Explains a design decision that is not obvious from context | `# WHY: Argon2 chosen over bcrypt for side-channel resistance` |
| `INTENT:` | States the goal of a block so future editors know its purpose | `# INTENT: Recompute parent WO status after child op state change` |
| `INVARIANT:` | Documents a condition that must always hold | `# INVARIANT: requester_id ≠ decider_user_id (separation of duties)` |
| `EDGE:` | Flags a non-obvious edge case being handled | `# EDGE: Token may be None on unauthenticated endpoints like /auth/login` |

Rules:

- Place the comment on the line **above** the relevant code, not inline.
- One prefix per comment. Do not combine (e.g., no `# WHY/EDGE:`).
- Do not add comments to code you did not change (see §1).

---

## 4. Boundary & Layering Conventions

### 4.1 Backend Layers

```
Routes (app/api/v1/)  →  Services (app/services/)  →  Repositories (app/repositories/)
         │                        │                              │
    Thin handlers           Business logic              Data access only
    Auth + schema           Owns rules                  Tenant-filtered queries
    validation              Calls repos                 No business rules
```

| Layer | Allowed dependencies | Forbidden |
|-------|---------------------|-----------|
| **Routes** | Services, Schemas, Security (dependencies) | Repositories, Models (direct), SQLAlchemy session |
| **Services** | Repositories, Models, Schemas, other Services | Routes, FastAPI Request/Response objects |
| **Repositories** | Models, SQLAlchemy session | Services, Routes, business logic |
| **Security** | Models (User), config, JWT libs | Services, Repositories |
| **Schemas** | Pydantic, Python stdlib | Models, Services, Repositories |
| **Models** | SQLAlchemy, Python stdlib | Everything else |

Additional backend rules:

- **Tenant isolation is mandatory.** Every repository query MUST filter by `tenant_id`. No exceptions.
- **Backend is source of truth.** Frontend never derives execution state.
- **Backend returns enums/codes only.** No translated text (i18n-ready).
- **JWT proves identity only.** Do NOT encode permissions in JWT. Authorization is checked per-request.

### 4.2 Frontend Layers

```
Pages (app/pages/)  →  Components (app/components/)  →  API (app/api/)
                              │
                         UI primitives (components/ui/)
```

| Layer | Allowed dependencies | Forbidden |
|-------|---------------------|-----------|
| **Pages** | Components, API, Auth, Persona, i18n, Hooks, Types | Direct fetch/axios calls, business logic |
| **Components** | UI primitives, lib/utils, Types | API calls (except via props/callbacks), Auth context reads (except Layout/TopBar) |
| **API** | httpClient, Types, Mappers | Components, Pages, React hooks |
| **Auth** | API (authApi), React context | Pages, Components |
| **Styles** | CSS custom properties, Tailwind utilities | Hardcoded hex colors (ESLint warns) |

Additional frontend rules:

- **Cross-module imports use `@/` alias.** ESLint `no-restricted-imports` enforces barrel imports for `auth`, `api`, `impersonation`, `persona`, `components`, `data`, `i18n`.
- **No hardcoded hex colors.** ESLint `no-restricted-syntax` warns on hex literals. Use CSS custom properties from `theme.css`. Exception: `components/flags/*.tsx` (national flag SVGs).
- **Frontend NEVER checks permissions.** Backend decides via 403. Persona is UX-only (landing page + menu visibility).
- **All new UI text MUST use semantic i18n keys.**

### 4.3 Naming Conventions

| Context | Convention | Example |
|---------|-----------|---------|
| Backend services | `snake_case` verbs | `start_operation()`, `create_approval_request()` |
| Frontend APIs | `camelCase` objects | `operationApi.start()`, `approvalApi.create()` |
| Routes | `kebab-case` | `/api/v1/operations/{id}/start` |
| Models | `PascalCase` | `ProductionOrder`, `ExecutionEvent` |
| DB tables | `snake_case` | `production_orders`, `execution_events` |

---

## 5. Governance Constraints

These rules are **locked** and require a Phase 7+ design gate to change:

- Do NOT add/rename permission families or change role→family mappings.
- Do NOT bypass approval for QC/scrap/rework actions.
- Do NOT encode permission logic in frontend.
- Do NOT remove tenant isolation from any repository.
- Do NOT add new impersonator roles.
- Do NOT modify execution state machine without updating `docs/system/mes-business-logic-v1.md`.
- `requester_id ≠ decider_user_id` — even under impersonation (separation of duties).
- Audit logs (approval + impersonation) are append-only, never deleted.
