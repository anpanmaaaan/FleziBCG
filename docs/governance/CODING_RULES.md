# CODING_RULES

**authoritative engineering rules**

Mandatory engineering rules for all contributors. Violations block merge unless the PR is explicitly classified as an intentional architecture / contract change and follows the required process.

---

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-27 | v2.0 | Final-safe production-hardening rules after Source Code Audit Response. Adjusted draft v2.0 to remain sync-consistent for P0-A, make Alembic mandatory, keep React Query/Zustand as future target, narrow idempotency/outbox scope, make RLS-ready but not mandatory in P0-A, and add P0-A scope guard. |
| 2026-04-23 | v1.0 | Initial canonical engineering rules. |

---

## 0. Purpose

This document defines the engineering rules for the FleziBCG codebase.

Its goals are to:

- keep the system predictable and safe to change;
- protect execution, governance, and tenant isolation semantics;
- separate mechanical changes from intentional architecture changes;
- ensure code remains compatible with MES/MOM domain rules;
- prevent reintroduction of tech debt classes already retired by hardening ADRs;
- keep P0 implementation slices narrow and production-safe.

This document is authoritative for:

- PR classification;
- verification gates;
- layering rules;
- tenant/scope isolation policy;
- API/DB/session rules;
- security baseline;
- AI engineering rules;
- definition of done.

For business and domain truth, see:

- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/02_domain/execution/business-truth-station-execution-v4.md`
- `docs/design/02_domain/quality/quality-domain-contracts.md`

For source structure truth, see:

- `docs/governance/SOURCE_STRUCTURE.md`

For reconciled implementation truths, see:

- `docs/governance/ENGINEERING_DECISIONS.md`

For production-hardening ADRs, see:

- `docs/design/10_hardening/`

---

## 1. Source of Truth Hierarchy

When documents disagree, apply this precedence:

1. the most specific authoritative design/business-truth document in `docs/design/`;
2. `docs/governance/CODING_RULES.md`;
3. `docs/governance/ENGINEERING_DECISIONS.md`;
4. `docs/governance/SOURCE_STRUCTURE.md`;
5. entry instructions / prompts;
6. inline comments.

### Rule

Do not average conflicting docs in code. Stop and reconcile first.

---

## 2. Engineering Principles

### 2.1 Backend is source of truth

- Frontend never derives execution truth.
- Frontend never derives permission truth.
- Frontend never authorizes protected actions.

### 2.2 Event-driven execution

- Execution events are append-only where eventing is used.
- Derived status must remain reproducible from authoritative facts/events.
- Cached/projection status is not authoritative.

### 2.3 Service layer owns business rules

- Routes stay thin.
- Repositories remain data access only.
- Business rule branching belongs in services.

### 2.4 Governance is first-class

- Separation of duties must hold.
- Privileged actions must be auditable.
- Support/admin operations must be reviewable.

### 2.5 AI is advisory by default

AI may summarize, explain, predict, or recommend.

AI may not silently mutate operational truth or bypass governance.

### 2.6 i18n hardcode enforcement

All user-facing UI strings in the frontend must be resolved through the i18n layer.

Mandatory rules:

- do not hardcode user-facing labels, button text, empty states, headings, badges, placeholders, helper text, dialog text, confirm text, or toast text in TS/TSX;
- do not render i18n keys directly to the UI;
- translate keys at the render boundary;
- `en.ts` and `ja.ts` must remain key-synchronized;
- adding, renaming, or deleting a key in one registry requires the matching change in the other registry in the same PR.

Verification:

```bash
cd frontend
npm run lint:i18n
npm run lint:i18n:registry
```

---

## 3. PR Classification

Every PR must declare one type.

### 3.1 Mechanical PR

Use for formatting, import cleanup, dead code removal, rename, non-behavioral refactor, and file movement without logic changes.

Rules:

- no runtime behavior change;
- no contract change;
- no feature creep;
- no unrelated cleanup beyond scope;
- route/OpenAPI baselines must remain unchanged.

### 3.2 Intentional Behavior PR

Use for bug fixes or behavior changes.

Required:

- PR description declares intended behavior change;
- affected tests are updated or added;
- affected docs are updated.

### 3.3 Architecture / Contract PR

Use for API contract changes, DB schema changes, IAM redesign, role/scope model changes, service boundary changes, new modules, and cross-layer refactors.

Required:

- explicit intent in PR description;
- design note or ADR for major changes;
- migration note if applicable;
- route/OpenAPI baseline update if applicable;
- documentation update.

---

## 4. Verification Gates

Run the gates relevant to the changed area.

### 4.1 Backend import check

```bash
cd backend
python -c "import app.main; print('import ok')"
```

### 4.2 Backend lint / format

```bash
cd backend
ruff check .
ruff format --check .
```

### 4.3 Backend tests

```bash
cd backend
python -m pytest -q
```

When coverage is configured:

```bash
cd backend
python -m pytest -q --cov=app --cov-report=term-missing
```

### 4.4 Backend type check

If configured:

```bash
cd backend
pyright
```

### 4.5 Frontend build / lint

```bash
cd frontend
npm run build
npm run lint
npm run lint:i18n
npm run lint:i18n:registry
```

### 4.6 Dependency vulnerability scan

When tooling is configured:

```bash
cd backend
pip-audit --strict
cd frontend
npm audit --audit-level=high
```

### 4.7 Docker healthcheck for infra changes

```bash
docker compose up -d
docker ps
```

### 4.8 Contract gates

Mechanical PRs must not change routes/OpenAPI baselines.

Architecture / Contract PRs may change baselines only when intentional, reviewed, and documented.

---

## 5. Backend Layering Rules

### 5.1 Routes

Allowed:

- request parsing;
- schema validation;
- auth dependency wiring;
- service delegation;
- response serialization.

Forbidden:

- business logic;
- direct repository calls;
- direct SQLAlchemy query logic;
- hidden transaction logic.

### 5.2 Services

Allowed:

- business rules;
- orchestration;
- transaction boundaries;
- repository composition;
- approval/auth checks;
- projection updates.

Forbidden:

- FastAPI `Request` / `Response` objects;
- UI-specific formatting;
- frontend-driven business branching.

### 5.3 Repositories

Allowed:

- persistence logic;
- explicit queries;
- scope-aware data access;
- ORM/session interaction.

Forbidden:

- business logic;
- approval logic;
- authorization truth;
- workflow decisions.

### 5.4 Models

Allowed:

- ORM definitions;
- persistence metadata;
- relationships.

Forbidden:

- business logic;
- service logic;
- route logic.

### 5.5 Schemas

Allowed:

- Pydantic DTOs;
- request/response validation;
- serialization shape.

Forbidden:

- side effects;
- repository/service logic;
- ORM persistence logic.

### 5.6 Sync / Async discipline — final-safe v2.0

Source Code Audit confirmed the current backend is synchronous.

P0-A must remain sync-consistent.

Rules:

- Do not migrate backend to full async inside P0-A.
- Do not introduce async SQLAlchemy or `asyncpg` inside P0-A.
- Do not mix sync and async DB access casually.
- If a route/service/repository is currently sync, keep it sync unless a dedicated ADR approves conversion.
- A future full-async migration requires a separate ADR and migration plan.

Allowed future target:

- The long-term stack may remain async-aware, but conversion is not part of P0-A.

Forbidden:

- partial async DB conversion in a DB/IAM foundation slice;
- introducing both sync and async sessions for the same repository family without explicit boundary documentation.

---

## 6. Frontend Layering Rules

### 6.1 Pages

Allowed:

- page orchestration;
- route-level state;
- API composition;
- interaction wiring.

Forbidden:

- direct fetch logic outside API layer;
- backend business rule duplication.

### 6.2 Components

Allowed:

- props-driven rendering;
- local UI interaction;
- presentational composition.

Forbidden:

- direct API calls from reusable components;
- permission truth;
- hidden domain logic.

### 6.3 API layer

Allowed:

- HTTP request/response handling;
- domain client functions;
- mapping between transport and UI types.

Forbidden:

- rendering;
- hooks inside transport clients;
- business decision logic.

### 6.4 Auth layer

Allowed:

- auth state;
- login/logout/session bootstrap;
- authentication-only route gating.

Forbidden:

- permission truth;
- business authorization logic.

### 6.5 Persona / navigation layer

Allowed:

- landing-page selection;
- menu exposure;
- UX-only route hints.

Forbidden:

- authorization decisions;
- backend rule duplication.

---

## 7. Tenant and Scope Isolation Policy

### 7.1 Core rule

Tenant and scope isolation are mandatory.

Every public repository method that accesses tenant-owned data must receive validated tenant/scope context explicitly.

No repository method may execute tenant-blind access to tenant-owned entities.

### 7.2 Implications

- Service layer passes tenant/scope context explicitly.
- Repository code must not silently escape scope boundaries.
- Cross-tenant access is allowed only through explicit privileged administrative paths.
- Frontend filtering is never a substitute for backend isolation.

### 7.3 Scope hierarchy

The codebase must be ready for hierarchical scope:

```text
tenant
 └─ plant
     └─ area
         └─ line
             └─ station
                 └─ equipment
```

### 7.4 RLS-ready posture

P0-A schema must be RLS-ready, but PostgreSQL RLS enablement is P1 hardening unless explicitly approved earlier.

P0-A rules:

- tenant-owned tables carry `tenant_id`;
- repository methods filter by tenant;
- tests cover cross-tenant isolation;
- app-layer tenant/scope enforcement remains mandatory.

If RLS is enabled later, it is defense-in-depth and does not replace application-layer authorization.

---

## 8. Naming Conventions

### 8.1 Backend

- files/modules: `snake_case`;
- classes: `PascalCase`;
- functions/methods: `snake_case`;
- constants: `UPPER_SNAKE_CASE`.

### 8.2 Frontend

- components: `PascalCase`;
- hooks: `useSomething`;
- utilities: `camelCase`;
- route paths: `kebab-case`.

### 8.3 Database

- tables: `snake_case`;
- columns: `snake_case`;
- foreign keys: `<entity>_id`;
- timestamps: `created_at`, `updated_at`;
- event tables include canonical event-table-standard columns.

### 8.4 Action codes

Privileged or auditable actions must use explicit action codes.

Recommended format:

- lower-case;
- dot notation;
- verb-oriented.

Examples:

- `execution.start`
- `execution.complete`
- `approval.decide`
- `auth.logout_all`
- `admin.session.revoke`

### 8.5 Error codes

Stable machine-readable error codes use `UPPER_SNAKE_CASE`.

Examples:

- `OPERATION_NOT_FOUND`
- `SESSION_REQUIRED`
- `QUALITY_GATE_BLOCKED`
- `IDEMPOTENCY_KEY_REUSED`
- `RATE_LIMIT_EXCEEDED`

---

## 9. API Contract Rules

### 9.1 Boundary contracts

All request/response contracts must use Pydantic schemas.

### 9.2 Datetime rules

- API datetime values use ISO 8601 with timezone offset.
- UTC is the default storage/interchange policy unless explicitly justified.
- No naive datetime in API contracts.

### 9.3 Backend returns codes, not translated labels

- Backend returns enums/codes.
- Frontend handles display/i18n.
- Backend must not return UI-language business labels as authoritative values.

### 9.4 Error shape

Error responses follow RFC 9457 Problem Details with FleziBCG extensions.

Canonical shape:

```json
{
  "type": "https://docs.flezibcg/errors/OPERATION_NOT_FOUND",
  "title": "Operation not found",
  "status": 404,
  "detail": "The requested operation does not exist or is outside your scope.",
  "instance": "/api/v1/execution/operations/123",
  "code": "OPERATION_NOT_FOUND",
  "correlation_id": "uuid",
  "errors": []
}
```

Mandatory fields:

- `type`;
- `title`;
- `status`;
- `code`;
- `correlation_id`.

### 9.5 Pagination

| Endpoint type | Pagination style |
|---|---|
| Event/audit log endpoints | Cursor-based |
| Master data endpoints | Offset-based (`page` + `size`) |
| Search endpoints | Cursor-based with optional `total_estimate` |

Defaults:

- default `size` / `limit` = 50;
- maximum `size` / `limit` = 200;
- larger requests return `400` with `code = PAGE_SIZE_EXCEEDED`.

### 9.6 Compatibility rules

- adding optional fields is allowed in intentional contract PRs;
- removing or renaming public fields requires architecture/contract PR;
- enum/code changes require explicit contract review;
- API URL versioning uses `/api/v1`; breaking changes go to `/api/v2`.

### 9.7 Idempotency-Key header

Command-style mutation endpoints that create operational, security, approval, audit, or integration side effects must support `Idempotency-Key`.

Rules:

- Header name: `Idempotency-Key`;
- Format: UUIDv4 client-generated opaque key;
- TTL: 24 hours minimum dedup window unless endpoint-specific ADR says otherwise;
- same key + same payload hash returns original/cached response;
- same key + different payload hash returns `409 Conflict` with `code = IDEMPOTENCY_KEY_REUSED`.

Not mandatory for:

- GET/list endpoints;
- purely idempotent updates;
- display preferences;
- local UI settings;
- endpoints that create no business/audit side effects.

Do not introduce Redis only for idempotency in P0-A.

### 9.8 Required request headers

- `Authorization: Bearer <jwt>` for protected endpoints;
- `Idempotency-Key` for command-style side-effecting mutations;
- `X-Correlation-ID` optional, server generates if absent;
- `Accept-Language` may guide localized narratives, but stable codes remain authoritative.

---

## 10. Database and Migration Rules

### 10.1 Transaction ownership

Service layer owns transaction boundaries.

### 10.2 Query discipline

- avoid N+1 queries;
- add indexes for common query paths;
- use explicit locking only when justified;
- use JSONB only with explicit reason;
- keep repository methods explicit and narrow.

### 10.3 Alembic is canonical

Alembic is the canonical migration system.

Rules:

- introduce/use Alembic for schema management;
- one migration should have one clear concern;
- do not edit already-applied migrations;
- separate schema and data migrations when complexity is non-trivial;
- destructive migrations require rollback or mitigation notes;
- every migration implements a working `downgrade()` or explicitly marks `# IRREVERSIBLE` with rationale.

`Base.metadata.create_all()` must not be used as production schema management.

P0-A must introduce or align Alembic before adding canonical foundation tables.

### 10.4 Idempotency and concurrency

Any write path that appends events, updates projections, changes approval state, or mutates sessions must have documented transactional behavior.

### 10.5 Online migration rule

FleziBCG targets production/plant environments where downtime may be expensive. Non-trivial schema changes should follow expand/backfill/contract.

Forbidden in one risky step:

- adding `NOT NULL` column without safe default/backfill plan;
- renaming a column in a single deployment step;
- dropping a column still referenced by deployed code;
- changing a column type incompatibly;
- adding unique constraints on populated tables without dedup verification.

### 10.6 Transactional outbox pattern

Transactional outbox is mandatory before implementing:

- cross-domain event publication;
- async integration dispatch;
- ERP posting;
- notification dispatch;
- external message publishing.

P0-A does not need an outbox worker unless it introduces such side effects.

Forbidden:

- network calls to external systems inside a DB transaction;
- bypassing outbox for cross-domain/external side effects once those flows exist.

### 10.7 Transaction isolation level

Default isolation level: PostgreSQL `READ COMMITTED`.

Escalate only with explicit rationale.

Use pessimistic locking sparingly. Prefer optimistic locking with a `version` column where appropriate.

### 10.8 Timestamp rule

- `recorded_at` must be generated by trusted backend/database clock.
- `occurred_at` may represent source/business/device time, but must be validated.
- Store timezone-safe timestamps.
- Avoid naive datetimes in persisted operational truth.

---

## 11. Authentication, Authorization, and Session Rules

### 11.1 Authentication lifecycle

The system must support, by roadmap phase:

- login;
- logout current session;
- logout all sessions;
- token refresh;
- password change;
- password reset request/confirm;
- session revoke.

### 11.2 JWT rules

- JWT proves identity only.
- JWT is not final authorization source.
- Protected actions must be checked server-side.
- Default access token TTL: 15 minutes.
- Default refresh token TTL: 7 days.
- Refresh token rotation is required when refresh implementation exists.
- Refresh tokens are stored hashed server-side.
- Refresh token plaintext must never be persisted.

### 11.3 User lifecycle

User states should be explicit:

- `pending`;
- `active`;
- `suspended`;
- `locked`;
- `deactivated`.

### 11.4 Role and scope assignment

Role assignment and scope assignment are separate concerns and must be auditable.

### 11.5 Frontend auth rules

- `RequireAuth` is authentication gating only.
- Frontend must not encode permission truth.
- Persona/menu visibility is UX-only.

### 11.6 MFA rule

MFA is required for:

- `ADM`;
- `OTS`;
- support / break-glass contexts;
- production data correction where policy requires step-up.

MFA may be implemented after P0-A if not already present, but new privileged flows must not be designed in ways that make MFA retrofit difficult.

---

## 12. Approval, Impersonation, and Governance Rules

### 12.1 Separation of duties

Requester must never equal decider, including under impersonation.

### 12.2 Approval validity

A governed action is valid only if:

- RBAC allows the action;
- approval rule allows the acting role;
- SoD rule is satisfied;
- operational context allows the action.

### 12.3 Impersonation rules

- only approved support/admin roles may impersonate;
- impersonation must be time-bound;
- impersonation requires reason;
- impersonation must not bypass SoD;
- impersonation must be fully audited;
- initiation should require MFA step-up where MFA is available.

---

## 13. Testing Strategy by Layer

### 13.1 Backend

- route tests: integration tests;
- service tests: business-rule unit tests;
- repository tests: integration tests when query behavior is non-trivial;
- security tests: required for protected endpoints;
- approval and impersonation tests: mandatory when those flows are touched.

### 13.2 Frontend

- page-level tests for orchestration flows;
- component tests for reusable UI behavior;
- hook/util tests for isolated logic;
- build must remain clean.

### 13.3 Domain-critical test areas

Coverage is expected for:

- execution lifecycle transitions;
- approval SoD;
- impersonation restrictions;
- tenant/scope isolation;
- session revoke/logout flows.

### 13.4 Coverage targets

| Layer | Target |
|---|---:|
| Service layer | 80% line coverage where configured |
| Repository layer | 70% line coverage where configured |
| Route layer | 70% line coverage where configured |
| Security/auth/policy/approval | 100% meaningful branch coverage target |

Security/auth/policy/approval uncovered branches require explicit justification.

Do not chase blind 100% line coverage with low-value tests.

### 13.5 Integration test database

- tests should run against real PostgreSQL where repository/migration behavior matters;
- no SQLite substitute for PostgreSQL-specific behavior;
- tests must be independent.

---

## 14. Frontend State and Data-fetching Rules

### 14.1 Data ownership

- Pages own data-fetch orchestration.
- Reusable components do not fetch directly unless explicitly designed as feature-bound components.

### 14.2 State discipline

- Do not duplicate server truth in multiple local states without reason.
- Distinguish server state from transient UI state.
- Loading/empty/error states must be explicit.

### 14.3 Large data UI

Large lists, timelines, and boards must use performance-aware rendering:

- virtualization;
- grouped rendering;
- viewport-based rendering;
- capped tick/grid counts where applicable.

### 14.4 State management target

Target frontend model:

- React Query for server state;
- Zustand for client/UI state where needed;
- React Router search params for shareable URL state.

Current frontend migration to React Query/Zustand is not part of P0-A unless the slice explicitly touches frontend state architecture.

Forbidden:

- storing JWT in Zustand or localStorage;
- direct `fetch()` calls scattered outside API layer;
- storing backend permission truth only in frontend state.

### 14.5 Error boundary

Every major page should have an error boundary before production release.

Error boundaries must:

- show localized fallback;
- avoid exposing stack trace;
- preserve correlation/support context where available.

### 14.6 Real-time update strategy

P0 default: polling.

P1+ candidate: WebSocket/SSE where justified.

Rules:

- WebSocket is not source of truth;
- always reconcile with backend truth after reconnect;
- do not poll faster than 5 seconds without explicit performance justification.

---

## 15. Tailwind and UI Rules

### 15.1 Styling discipline

- use theme tokens / approved CSS custom properties;
- do not hardcode arbitrary hex colors outside approved exceptions;
- extract repeated patterns when duplication becomes meaningful.

### 15.2 Accessibility basics

- interactive elements must be keyboard reachable;
- focus states must remain visible;
- disabled state must be visually and semantically clear;
- target WCAG 2.1 AA for P0 screens;
- color contrast ratio ≥ 4.5:1 for normal text, ≥ 3:1 for large text.

### 15.3 Performance-sensitive screens

Gantt, dashboards, large tables, and queue boards must define rendering constraints and avoid uncontrolled DOM growth.

---

## 16. Logging and Observability Rules

### 16.1 Structured logging

Logs should include contextual identifiers where relevant:

- `request_id`;
- `tenant_id`;
- `user_id`;
- `operator_id` when applicable;
- `action_code`;
- `resource_identifiers`;
- `correlation_id`;
- `causation_id`.

### 16.2 Sensitive data rules

Never log:

- passwords;
- JWTs;
- refresh tokens;
- API keys;
- secrets;
- idempotency keys;
- full sensitive personal data unless explicitly approved and protected.

### 16.3 Auditable operations

The following must be auditable:

- execution mutations;
- approval decisions;
- impersonation lifecycle;
- session revoke/logout-all;
- role/scope assignment changes;
- admin/support actions;
- production data correction;
- MFA enrolment/reset;
- failed authentication attempts where threshold/policy requires.

### 16.4 Structured log format

Logs are emitted as JSON to STDOUT where runtime logging has been configured.

Recommended fields:

```json
{
  "ts": "2026-04-27T08:15:32.123Z",
  "level": "INFO",
  "logger": "app.services.execution.start_execution",
  "message": "Execution started",
  "correlation_id": "uuid",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "request_id": "uuid",
  "action_code": "execution.start"
}
```

No `print()` in production code.

---

## 17. Security Rules

### 17.1 Secrets

- no secrets in repo;
- use env or approved secret management;
- local development secrets must not leak into committed files;
- production secrets must be rotated according to deployment policy.

### 17.2 Input handling

- validate boundary input with schemas;
- no raw SQL string interpolation with user-controlled values;
- maximum request body size defaults should be explicit;
- file upload rules require separate ADR before P1/P2 upload features.

### 17.3 Error exposure

- production responses must not expose stack traces;
- diagnostics belong in logs;
- error responses include `correlation_id`.

### 17.4 Cryptography baseline

Password hashing:

- algorithm: `argon2id`;
- library: `argon2-cffi` or approved equivalent;
- forbidden: MD5, SHA-1, unsalted SHA-256, plaintext password storage.

TLS:

- production minimum TLS 1.2;
- TLS 1.3 preferred;
- HTTP allowed only behind approved TLS-terminating proxy or for local/dev.

CORS:

- default deny;
- allowed origins are explicit per environment;
- credentials only when cookie-based auth requires it.

CSRF:

- cookie-based auth requires CSRF strategy;
- bearer-token-only machine/API clients do not need CSRF.

Random/secrets:

- use Python `secrets` for security-sensitive tokens;
- use constant-time comparison for secrets/tokens.

### 17.5 Rate limiting

Mandatory for auth and sensitive mutation endpoints.

Baseline examples:

| Endpoint / Context | Default Limit | Scope |
|---|---:|---|
| login | 5 attempts / 15 min | per-IP + per-username |
| refresh | 30 / 5 min | per-user/session |
| password reset | 3 / 1 hour | per-IP + per-email |
| invite user | 10 / 1 hour | per-tenant |
| human station command | conservative default such as 60 / min | per-station-session |
| machine/edge ingestion | separate endpoint and limit | per-external-system |

Do not share human station command limits with machine/edge ingestion limits.

Redis is not required for P0-A; in-memory/dev fallback is acceptable only for local/dev.

### 17.6 Dependency vulnerability management

Required direction:

- backend: `pip-audit` when configured;
- frontend: `npm audit --audit-level=high` when configured;
- Dependabot or Renovate recommended.

Lockfiles are authoritative and must be committed.

---

## 18. AI-specific Engineering Rules

### 18.1 AI is advisory by default

AI features may summarize, explain, predict, or recommend.

AI features may not:

- silently mutate execution state;
- bypass auth, approval, or SoD;
- present uncertain output as deterministic system fact.

### 18.2 AI access context

All AI features must respect:

- tenant scope;
- user role;
- effective scope;
- approval/governance restrictions.

### 18.3 AI traceability

Every AI output must be traceable to:

- source context;
- feature id;
- model/version;
- prompt/template version;
- user and scope context;
- confidence score where applicable;
- output schema version.

### 18.4 AI output labeling

UI must distinguish:

- system fact;
- AI insight;
- AI prediction;
- AI recommendation.

### 18.5 AI safety guardrails

- AI input must respect tenant/scope filtering before model call.
- AI output must pass schema validation before display.
- AI output must never trigger backend command directly.
- Prompt injection defenses are required before external text ingestion.
- Model upgrades require Architecture/Contract PR.

---

## 19. Documentation Rules

### 19.1 Contract changes

Any contract change must update the authoritative doc in the same PR.

### 19.2 Architecture changes

Major architecture changes require:

- design note or ADR;
- migration impact note;
- explicit PR classification as Architecture / Contract.

### 19.3 Comment policy

Comments explain why, not what.

Approved prefixes:

- `WHY:`
- `INTENT:`
- `INVARIANT:`
- `EDGE:`
- `SECURITY:`
- `PERF:`

### 19.4 ADR maintenance

- New architecture decisions go to `docs/design/10_hardening/` or `docs/governance/ENGINEERING_DECISIONS.md` depending scope.
- ADR file names use kebab-case.
- Accepted ADRs are not deleted; superseded ADRs are marked superseded.

---

## 20. Git / PR / Review Rules

### 20.1 PR descriptions

Every PR states:

- PR type;
- intended scope;
- runtime behavior changes;
- contract changes;
- docs/migrations included;
- security or AI impact.

### 20.2 Review checklist

Reviewer confirms:

- correct PR classification;
- tests passed;
- docs updated if needed;
- migrations reviewed if applicable;
- no hidden contract drift;
- security/governance impact considered;
- dependency scan clean where relevant.

### 20.3 Commit hygiene

Use conventional commit style:

```text
<type>(<scope>): <subject>
```

Types:

- `feat`
- `fix`
- `docs`
- `style`
- `refactor`
- `test`
- `chore`
- `perf`
- `security`

---

## 21. Definition of Done

A change is done only when:

- required verification gates pass;
- behavior/contract intent is explicit;
- docs are updated if required;
- migrations are included if required;
- migrations follow safe pattern;
- security and audit implications are addressed;
- reviewer can identify the correct source of truth;
- no undocumented hidden behavior is introduced.

---

## 22. Forbidden Without Explicit Architecture Gate

Forbidden unless approved through Architecture / Contract PR:

- changing permission families;
- changing locked role mappings without governance review;
- bypassing approval for governed actions;
- encoding permission truth in frontend;
- introducing tenant-blind data access;
- changing execution state semantics without business logic update;
- granting production execution power to admin/support by default;
- introducing cloud-only mandatory dependencies;
- introducing autonomous AI control of execution;
- adding top-level dependency without security review;
- changing cryptography algorithm or parameters;
- changing rate-limit baseline;
- converting sync backend to async;
- changing API versioning scheme;
- changing pagination contract;
- bypassing transactional outbox for cross-domain/external side effects once those exist;
- disabling MFA for ADM/OTS where MFA is implemented/required.

---

## 23. Tech-Debt Prevention Checklist

Before each implementation slice, verify:

### 23.1 Code debt

- no magic numbers in business logic;
- no duplicated authorization logic;
- no duplicated tenant filter logic;
- no FE-side derivation of execution legality.

### 23.2 Architecture debt

- cross-domain references documented as extraction debt where present;
- no synchronous external call inside DB transaction;
- no projection write outside authoritative event/fact path;
- no frontend state holding server truth.

### 23.3 Test debt

- security/auth tests added for changed flows;
- no skipped tests without expiry and tracking issue;
- repository/tenant isolation paths tested where touched.

### 23.4 Dependency debt

- lockfiles committed;
- dependency scan clean where configured;
- no unpinned production dependencies without reason.

### 23.5 Documentation debt

- ADR present for non-obvious architecture decision;
- CODING_RULES updated when new pattern is enforced;
- AUTHORITATIVE_FILE_MAP reflects new authoritative docs.

### 23.6 Infrastructure debt

- secrets not committed;
- structured logs where runtime code is touched;
- correlation ID propagated where endpoint code is touched;
- no CloudBeaver in production runtime.

### 23.7 Security debt

- argon2id for password hashing;
- CORS allowlist explicit;
- rate limiting on auth and sensitive mutation endpoints;
- no secrets in logs;
- CSRF protection when cookie-based auth is used.

---

## 24. Phased Application of v2.0 Rules

### Phase A — before / during P0-A Foundation Database

Mandatory direction:

- Alembic migration foundation;
- cryptography baseline;
- CORS allowlist posture;
- structured logging direction;
- dependency scan direction;
- tenant isolation tests for changed foundation paths;
- P0-A scope guard.

Implementation occurs only where the slice touches the relevant endpoint/runtime path.

### Phase B — before P0-D Quality Lite

- MFA for ADM/OTS where privileged flows exist;
- transactional outbox before cross-domain/external side effects;
- pagination contract enforcement;
- coverage thresholds in CI;
- online migration discipline.

### Phase C — before P1

- frontend React Query/Zustand migration where needed;
- page-level error boundaries for complex pages;
- real-time update strategy;
- optional RLS enablement;
- cache strategy if performance data justifies it.

### Rule

Earlier-phase violations remain blocking after their phase begins, but do not implement a later-phase runtime capability just to satisfy this document.

---

## 25. P0-A Scope Guard

P0-A must not implement:

- ERP integration;
- Acceptance Gate;
- Backflush;
- APS;
- AI;
- Digital Twin;
- Compliance/e-record;
- OPC UA / MQTT / Sparkplug implementation;
- Redis / Kafka / OPA implementation;
- full async migration;
- frontend React Query/Zustand migration;
- Station Execution refactor;
- claim removal;
- rework flow;
- `rework_qty`;
- `abort_operation` expansion.

P0-A focuses only on:

- Alembic;
- tenant;
- IAM;
- sessions;
- refresh tokens;
- roles/actions;
- scope assignments;
- audit/security events;
- plant hierarchy;
- scope-node compatibility;
- CORS/config hardening;
- CloudBeaver dev-only posture;
- backend CI minimum where absent.

---

## End of CODING_RULES v2.0
