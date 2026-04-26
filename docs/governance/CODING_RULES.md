# CODING_RULES

**authoritative engineering rules**

Mandatory engineering rules for all contributors. Violations block merge unless the PR is explicitly classified as an intentional architecture / contract change and follows the required process.

---

## 0. Purpose

This document defines the engineering rules for the codebase.

Its goals are to:
- keep the system predictable and safe to change
- protect execution, governance, and tenant isolation semantics
- separate mechanical changes from intentional architecture changes
- ensure code remains compatible with MES/MOM domain rules
- provide a foundation for future AI-driven MES/MOM capabilities

This document is authoritative for:
- PR classification
- verification gates
- layering rules
- tenant/scope isolation policy
- API/DB/session rules
- AI engineering rules
- definition of done

For business and domain truth, see:
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/02_domain/execution/business-truth-station-execution-v4.md`
- `docs/design/02_domain/quality/quality-domain-contracts.md`

For structure/layout truth, see:
- `docs/governance/SOURCE_STRUCTURE.md`

For reconciled implementation truths, see:
- `docs/governance/ENGINEERING_DECISIONS.md`

---

## 1. Source of Truth Hierarchy

When documents disagree, apply the following precedence:

1. the most specific authoritative design/business-truth document in `docs/design/`
2. `docs/governance/CODING_RULES.md`
3. `docs/governance/ENGINEERING_DECISIONS.md`
4. `docs/governance/SOURCE_STRUCTURE.md`
5. entry instructions / prompts
6. inline comments

### Rule
Do not “average” conflicting docs in code.
Stop and reconcile first.

---

## 2. Engineering Principles

### 2.1 Backend is source of truth
- frontend never derives execution truth
- frontend never derives permission truth
- frontend never authorizes protected actions

### 2.2 Event-driven execution
- execution events are append-only
- derived status must remain reproducible from events
- cached/projection status is not authoritative

### 2.3 Service layer owns business rules
- routes stay thin
- repositories remain data access only
- business rule branching belongs in services

### 2.4 Governance is first-class
- separation of duties must hold
- privileged actions must be auditable
- support/admin operations must be reviewable

### 2.5 AI is advisory by default

AI may summarize, explain, predict, or recommend.  
AI may not silently mutate operational truth or bypass governance.

---

## 2.6 i18n Hardcode Enforcement

All user-facing UI strings in the frontend must be resolved via `useI18n().t(key)`.

### Mandatory rules
- do not hardcode user-facing labels, button text, empty states, headings, badges, placeholders, helper text, dialog text, confirm text, or toast text in TS/TSX
- do not render i18n keys directly to the UI; any value that is an i18n key must be translated at the render boundary via `t(...)`
- values returned from mappers, selectors, status helpers, or API adapters that represent display text must be either:
  - already localized final text, or
  - explicit i18n keys that are translated by the consuming UI
- never mix these two meanings in one helper without naming it clearly
- locale registry files must remain static literal registries; do not add runtime merging, `require(...)`, computed synchronization, nested exports, or self-healing locale logic inside registry files
- `en.ts` and `ja.ts` must remain key-synchronized; adding, renaming, or deleting a key in one registry requires the matching change in the other registry in the same PR
- placeholder English copied from another locale is allowed only as a temporary fallback during implementation, but the matching key must still exist in both registries before merge

### Verification requirements
- when a PR changes user-facing frontend text, contributors must run `npm run lint:i18n`
- when a PR changes any i18n registry file, contributors must also verify that `en.ts` and `ja.ts` contain the same key set
- when a PR changes helpers that return status or label values consumed by UI, contributors must verify that the affected screen renders translated text rather than raw keys
- `npm run lint:i18n` is the required verification entrypoint and must pass both hardcoded-string checks and locale registry parity checks

To prevent regressions, a lint-like enforcement script is provided:

  npm run lint:i18n

This script scans for common hardcoded string patterns in TSX files (e.g., JSX text nodes, toast/confirm/title literals) and fails if violations are found. All contributors must pass this check before PR approval.

Locale registry parity is enforced by:

  npm run lint:i18n:registry

See `frontend/scripts/check_i18n_hardcode.sh` and `frontend/scripts/check_i18n_registry_parity.mjs` for details.

---

## 3. PR Classification

Every PR must declare one of these types.

### 3.1 Mechanical PR
Use for:
- formatting
- import cleanup
- dead code removal
- rename
- non-behavioral refactor
- file movement without logic changes

#### Rules
- no runtime behavior change
- no contract change
- no feature creep
- no unrelated cleanup beyond scope
- route/OpenAPI baselines must remain unchanged

### 3.2 Intentional Behavior PR
Use for:
- bug fix that changes runtime behavior
- business rule correction
- execution rule correction
- approval/governance change
- auth/session/user lifecycle behavior change

#### Required
- PR description must declare intended behavior change
- affected tests must be updated or added
- affected docs must be updated

### 3.3 Architecture / Contract PR
Use for:
- API contract changes
- DB schema changes
- IAM redesign
- role/scope model changes
- service boundary changes
- new modules/features
- cross-layer refactors

#### Required
- explicit intent in PR description
- design note or ADR for major changes
- migration note if applicable
- route/OpenAPI baseline update if applicable
- documentation update required

---

## 4. Verification Gates

### 4.1 Backend import check
```bash
cd backend
python -c "import app.main; print('import ok')"
```
### 4.2 Lint
```bash
cd backend
ruff check .
```
### 4.3 Format
```bash
cd backend
ruff format --check .
```
### 4.4 Pytest
```bash
cd backend
python -m pytest -q
```
### 4.5 Frontend build
```bash
cd frontend
npm run build
# Zero TypeScript errors are required.
```
### 4.6 Docker healthcheck (infra changes)
```bash
docker-compose up -d
docker ps
```
### 4.7 Contract gates
**Mechanical PR**
Routes SHA and OpenAPI SHA must remain unchanged.
**Architecture / Contract PR**
Routes/OpenAPI diffs are allowed only if:
  •    intentional
  •    reviewed
  •    baselines updated
  •    docs updated

---

## 5. Backend Layering Rules
### 5.1 Routes
Allowed:
  • request parsing
  • schema validation
  • auth dependency wiring
  • service delegation
  • response serialization
Forbidden:
  • business logic
  • direct repository calls
  • direct SQLAlchemy query logic
  • hidden transaction logic
### 5.2 Services
Allowed:
  • business rules
  • orchestration
  • transaction boundaries
  • repository composition
  • approval/auth checks
  • projection updates
Forbidden:
  • FastAPI Request/Response objects
  • UI-specific formatting
  • frontend-driven business branching
### 5.3 Repositories
Allowed:
  • persistence logic
  • explicit queries
  • scope-aware data access
  • ORM/session interaction
Forbidden:
  • business logic
  • approval logic
  • authorization truth
  • workflow decisions
### 5.4 Models
Allowed:
  • ORM definitions
  • persistence metadata
  • relationships
Forbidden:
  • business logic
  • service logic
  • route logic
### 5.5 Schemas
Allowed:
  • Pydantic DTOs
  • request/response validation
  • serialization shape
Forbidden:
  • side effects
  • repository/service logic
  • ORM persistence logic

---

## 6. Frontend Layering Rules
### 6.1 Pages
Allowed:
  • page orchestration
  • route-level state
  • API composition
  • interaction wiring
Forbidden:
  • direct fetch logic outside API layer
  • backend business rule duplication
### 6.2 Components
Allowed:
  • props-driven rendering
  • local UI interaction
  • presentational composition
Forbidden:
  • direct API calls from reusable components
  • permission logic
  • hidden domain logic
### 6.3 API layer
Allowed:
  • HTTP request/response handling
  • domain client functions
  • mapping between transport and UI types
Forbidden:
  • rendering
  • hooks inside transport clients
  • business decision logic
### 6.4 Auth layer
Allowed:
  • auth state
  • login/logout/session bootstrap
  • authentication-only route gating
Forbidden:
  • permission truth
  • business authorization logic
### 6.5 Persona / navigation layer
Allowed:
  • landing-page selection
  • menu exposure
  • UX-only route hints
Forbidden:
  • authorization decisions
  • backend rule duplication

---

## 7. Tenant and Scope Isolation Policy
This section is authoritative.
### 7.1 Core rule
Tenant and scope isolation are mandatory.
Every public repository method that accesses tenant-owned data must receive validated tenant/scope context explicitly.
No repository method may execute tenant-blind access to tenant-owned entities.
### 7.2 Implications
  • service layer passes tenant/scope context explicitly
  • repository code must not silently escape scope boundaries
  • cross-tenant access is allowed only through explicit privileged administrative paths
  • frontend filtering is never a substitute for backend isolation
### 7.3 Scope hierarchy
The codebase must be ready for hierarchical scope:
tenant
 └─ plant
     └─ area
         └─ line
             └─ station
                 └─ equipment

---

## 8. Naming Conventions
### 8.1 Backend
  • files/modules: snake_case
  • classes: PascalCase
  • functions/methods: snake_case
  • constants: UPPER_SNAKE_CASE
### 8.2 Frontend
  • components: PascalCase
  • hooks: useSomething
  • utilities: camelCase
  • route paths: kebab-case
### 8.3 Database
  • tables: snake_case
  • columns: snake_case
  • foreign keys: <entity>_id
  • timestamps: created_at, updated_at
### 8.4 Action codes
Privileged or auditable actions must use explicit action codes.
Recommended format:
  • lower-case
  • dot notation
  • verb-oriented
Examples:
  • execution.start
  • execution.complete
  • approval.decide
  • auth.logout_all
  • admin.session.revoke

---

## 9. API Contract Rules
### 9.1 Boundary contracts
All request/response contracts must use Pydantic schemas.
### 9.2 Datetime rules
  • API datetime values use ISO 8601
  • UTC is the default storage/interchange policy unless explicitly justified otherwise
### 9.3 Backend returns codes, not translated text
  • enums/codes only
  • frontend handles display/i18n
  • backend must not return UI-language business labels as authoritative values
### 9.4 Error shape
Use a consistent error shape.
Example:
{
  "error": {
    "code": "OPERATION_NOT_FOUND",
    "message": "Operation not found"
  }
}
### 9.5 Pagination/filtering
Paginated endpoints must standardize:
  • page or cursor style
  • max page size
  • sort format
  • filter format
### 9.6 Compatibility rules
  • adding optional fields is allowed in intentional contract PRs
  • removing or renaming public fields requires architecture/contract PR
  • enum/code changes require explicit contract review

---

## 10. Database and Migration Rules
### 10.1 Transaction ownership
Service layer owns transaction boundaries.
### 10.2 Query discipline
  • avoid N+1 queries
  • add indexes for common query paths
  • use explicit locking only when justified
  • use JSONB only with explicit reason
  • keep repository methods explicit and narrow
### 10.3 Migration discipline
  • use Alembic
  • one migration should have one clear concern
  • do not edit already-applied migrations
  • separate schema and data migrations when complexity is non-trivial
  • destructive migrations require rollback or mitigation notes
### 10.4 Idempotency and concurrency
Endpoints that must be idempotent must be explicitly documented and tested.
Any write path that:
  • appends events
  • updates projections
  • changes approval state
  • mutates sessions
must have clearly documented transactional behavior.

---

## 11. Authentication, Authorization, and Session Rules
### 11.1 Authentication lifecycle
The system must support:
  • login
  • logout current session
  • logout all sessions
  • token refresh
  • password change
  • password reset request
  • password reset confirm
  • session revoke
### 11.2 JWT rules
  • JWT proves identity only
  • JWT is not the final authorization source
  • all protected actions must be checked server-side
### 11.3 User lifecycle
User states should be explicit:
  • pending
  • active
  • suspended
  • locked
  • deactivated
### 11.4 Role and scope assignment
Role assignment and scope assignment are separate concerns and must be auditable.
### 11.5 Frontend auth rules
  • RequireAuth is authentication gating only
  • frontend must not encode permission truth
  • persona/menu visibility is UX-only

---

## 12. Approval, Impersonation, and Governance Rules
### 12.1 Separation of duties
Requester must never equal decider, including under impersonation.
### 12.2 Approval validity
A governed action is valid only if:
  • RBAC allows the action
  • approval rule allows the acting role for that action
  • SoD rule is satisfied
### 12.3 Impersonation rules
  • only approved support/admin roles may impersonate
  • impersonation must be time-bound
  • impersonation requires reason
  • impersonation must not bypass SoD
  • impersonation must be fully audited
### 12.4 Support / break-glass policy
Support actions are privileged and must be:
  • explicit
  • time-bound
  • logged
  • reviewable

---

## 13. Testing Strategy by Layer
### 13.1 Backend
  • route tests: integration tests
  • service tests: business-rule unit tests
  • repository tests: integration tests when query behavior is non-trivial
  • security tests: required for protected endpoints
  • approval and impersonation tests: mandatory
### 13.2 Frontend
  • page-level tests for orchestration flows
  • component tests for reusable UI behavior
  • hook/util tests for isolated logic
  • build must remain clean
### 13.3 Domain-critical test areas
Coverage is expected for:
  • execution lifecycle transitions
  • approval SoD
  • impersonation restrictions
  • tenant/scope isolation
  • session revoke/logout flows

---

## 14. Frontend State and Data-fetching Rules
### 14.1 Data ownership
  • pages own data-fetch orchestration
  • reusable components do not fetch directly unless explicitly designed as feature-bound components
### 14.2 State discipline
  • do not duplicate server truth in multiple local states without reason
  • distinguish server state from transient UI state
  • loading / empty / error states must be explicit
### 14.3 Large data UI
Large lists, timelines, and boards must use performance-aware rendering:
  • virtualization
  • grouped rendering
  • viewport-based rendering
  • capped tick/grid counts where applicable

---

## 15. Tailwind and UI Rules
### 15.1 Styling discipline
  • use theme tokens / approved CSS custom properties
  • do not hardcode arbitrary hex colors outside approved exceptions
  • avoid unreadable class strings
  • extract repeated patterns when duplication becomes meaningful
### 15.2 Accessibility basics
  • interactive elements must be keyboard reachable
  • focus states must remain visible
  • disabled state must be visually and semantically clear
### 15.3 Performance-sensitive screens
Screens such as:
  • Gantt
  • dashboards
  • large tables
  • queue boards
must define rendering constraints and avoid uncontrolled DOM growth.

---

## 16. Logging and Observability Rules
### 16.1 Structured logging
Logs should include contextual identifiers where relevant:
  • request_id
  • tenant_id
  • user_id
  • action_code
  • resource identifiers
### 16.2 Sensitive data rules
Never log:
  • passwords
  • tokens
  • secrets
  • sensitive personal data unless explicitly approved and protected
### 16.3 Auditable operations
The following must be auditable:
  • execution mutations
  • approval decisions
  • impersonation lifecycle
  • session revoke/logout-all
  • role/scope assignment changes
  • admin/support actions

---

## 17. Security Rules
### 17.1 Secrets
  • no secrets in repo
  • use env or approved secret management
  • local development secrets must not leak into committed files
### 17.2 Input handling
  • validate all boundary input with schema
  • no raw SQL string interpolation with user-controlled values
  • sanitize risky external inputs where applicable
### 17.3 Error exposure
  • production responses must not expose internal stack traces
  • diagnostics belong in logs, not client responses

---

## 18. AI-specific Engineering Rules
### 18.1 AI is advisory by default
AI features may:
  • summarize
  • explain
  • predict
  • recommend
AI features may not:
  • silently mutate execution state
  • bypass auth, approval, or SoD
  • present uncertain output as deterministic system fact
### 18.2 AI access context
All AI features must respect:
  • tenant scope
  • user role
  • effective scope
  • approval/governance restrictions
### 18.3 AI traceability
Important AI outputs must be traceable to:
  • source context
  • feature id
  • model/version where applicable
  • user and scope context
### 18.4 AI output labeling
UI must clearly distinguish:
  • system fact
  • AI insight
  • AI prediction
  • AI recommendation

---

## 19. Documentation Rules
### 19.1 Contract changes
Any contract change must update the authoritative doc in the same PR.
### 19.2 Architecture changes
Major architecture changes require:
  • design note or ADR
  • migration impact note
  • explicit PR classification as architecture/contract change
### 19.3 Comment policy
Comments explain why, not what.
Approved prefixes:
  • WHY:
  • INTENT:
  • INVARIANT:
  • EDGE:
Do not add comments to untouched code unless the PR scope explicitly includes it.

---

## 20. Git / PR / Review Rules
### 20.1 PR descriptions
Every PR must state:
  • PR type
  • intended scope
  • whether runtime behavior changes
  • whether contract changes
  • whether docs/migrations are included
### 20.2 Review checklist
Reviewer must confirm:
  • correct PR classification
  • tests passed
  • docs updated if needed
  • migration reviewed if applicable
  • no hidden contract drift
  • security/governance impact considered

---

## 21. Definition of Done
A change is done only when:
  • code passes required verification gates
  • behavior/contract intent is explicit
  • docs are updated if required
  • migrations are included if required
  • security and audit implications are addressed
  • reviewer can identify the correct source of truth
  • no undocumented hidden behavior is introduced

---

## 22. Forbidden Without Explicit Architecture Gate
The following are forbidden unless approved through an architecture/contract PR:
  • changing permission families
  • changing locked role mappings without governance review
  • bypassing approval for governed actions
  • encoding permission truth in frontend
  • introducing tenant-blind data access
  • changing execution state semantics without business logic update
  • granting production execution power to admin/support by default
  • introducing cloud-only mandatory dependencies
  • introducing autonomous AI control of execution
