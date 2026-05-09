# Full QA Ticketized Backlog (By Phase and Owner)

## Routing
- Selected brain: MOM Brain
- Selected mode: Product plus Architecture plus Strict
- Hard Mode MOM: v3
- Reason: Ticketization spans quality truth, execution gating, authorization, auditability, and release controls.

## Owner map

- `BE-QLTY`: Backend Quality team
- `BE-EXEC`: Backend Execution team
- `FE-APP`: Frontend App team
- `QA-AUTO`: Test Automation team
- `SEC-GOV`: Security and Governance team
- `DATA-OPS`: DB and Migration Ops team
- `PO-SA`: Product Owner and Solution Architect

## Priority and sequencing rules

1. Build and close all `Phase A` tickets before starting `Phase B` implementation tickets.
2. `Phase C` starts only after `Phase B` API/invariant tickets are accepted.
3. `Phase D` UI tickets can run in parallel with late `Phase C` read-model tickets if API contracts are frozen.
4. `Phase E` release tickets run after all earlier phase acceptance gates are green.

## Phase A — Domain model and policy foundation

| Ticket ID | Title | Owner | Depends on | Acceptance criteria | Validation gate |
|---|---|---|---|---|---|
| QA-A-001 | Define acceptance gate aggregates and enums | BE-QLTY | none | Gate definition and gate instance models exist with lifecycle enums and tenant fields | model tests pass |
| QA-A-002 | Add policy tables for applicability and rule sets | BE-QLTY | QA-A-001 | Policy persistence supports operation/context applicability and rule-set versioning | migration + repository tests pass |
| QA-A-003 | Add disposition catalog and governance metadata | BE-QLTY | QA-A-001 | Disposition codes include release, deviation, recheck, scrap with governance attributes | schema validation tests pass |
| QA-A-004 | Add deviation request aggregate foundation | BE-QLTY | QA-A-003 | Deviation request entity persists requester, rationale, status, and tenant linkage | unit tests pass |
| QA-A-005 | Add nonconformance base aggregate | BE-QLTY | QA-A-003 | NC entity exists with minimal operational lifecycle and trace references | unit tests pass |
| QA-A-006 | Author Alembic migrations for full Phase A schema | DATA-OPS | QA-A-001, QA-A-002, QA-A-003, QA-A-004, QA-A-005 | Migration chain is linear and upgrades from baseline to head cleanly | alembic baseline and upgrade tests pass |
| QA-A-007 | Publish Phase A schema contract note | PO-SA | QA-A-006 | Contract doc includes entities, states, and exclusions | design review accepted |

## Phase B — Backend commands, APIs, and invariants

| Ticket ID | Title | Owner | Depends on | Acceptance criteria | Validation gate |
|---|---|---|---|---|---|
| QA-B-001 | Implement gate definition lifecycle service | BE-QLTY | QA-A-006 | Create, activate, retire gate definitions with tenant and scope checks | service tests pass |
| QA-B-002 | Implement gate instance open/close commands | BE-QLTY | QA-A-006 | Instance lifecycle transitions enforced with invalid-state rejection | state transition tests pass |
| QA-B-003 | Implement gate-context measurement submit command | BE-QLTY | QA-B-002 | Submit accepts observed facts only and validates required-item completeness | input and invariant tests pass |
| QA-B-004 | Implement backend evaluation and hold application | BE-QLTY | QA-B-003 | Pass/fail and hold are server-derived and auditable | event payload tests pass |
| QA-B-005 | Implement deviation request command and queue retrieval | BE-QLTY | QA-A-004, QA-B-004 | Hold-linked deviation requests are created and queryable by quality actors | API integration tests pass |
| QA-B-006 | Implement governed disposition decision command | BE-QLTY | QA-B-004, QA-A-003 | Authorized quality actor decides release, deviation, recheck, scrap | authorization and audit tests pass |
| QA-B-007 | Enforce SoD for requester and decider paths | SEC-GOV | QA-B-005, QA-B-006 | Requester cannot decide own governed outcome where policy requires separation | security event tests pass |
| QA-B-008 | Add quality API endpoints for gate lifecycle and review | BE-QLTY | QA-B-001, QA-B-002, QA-B-003, QA-B-006 | REST endpoints exist with explicit schemas and HTTP semantics | API contract tests pass |
| QA-B-009 | Add event emission coverage for all quality commands | BE-QLTY | QA-B-004, QA-B-006 | All command handlers publish required domain/audit events | event matrix tests pass |
| QA-B-010 | Update docs for API and event catalog | PO-SA | QA-B-008, QA-B-009 | API catalog and implementation evidence are synced | docs checklist pass |

## Phase C — Execution gating and quantity-effects integration

| Ticket ID | Title | Owner | Depends on | Acceptance criteria | Validation gate |
|---|---|---|---|---|---|
| QA-C-001 | Integrate quality gate into allowed-actions derivation | BE-EXEC | QA-B-004, QA-B-006 | Execution actions block/unblock by active gate and hold truth | command guard tests pass |
| QA-C-002 | Implement accepted-good and held-pending quantity policy engine | BE-EXEC | QA-B-006 | Quantity effects are deterministic across release, recheck, reject, scrap | quantity regression tests pass |
| QA-C-003 | Project quality gate state into operation detail read model | BE-EXEC | QA-C-001 | Operation detail exposes gate status, hold status, and pending decisions | projection consistency tests pass |
| QA-C-004 | Add reconciliation checks for event-to-projection consistency | DATA-OPS | QA-C-003 | Reconciliation job detects drift between events and projections | reconciliation tests pass |
| QA-C-005 | Publish execution-quality interaction contract note | PO-SA | QA-C-001, QA-C-002, QA-C-003 | Design contract clarifies orthogonal states and quantity effects | design review accepted |

## Phase D — Frontend quality experience expansion

| Ticket ID | Title | Owner | Depends on | Acceptance criteria | Validation gate |
|---|---|---|---|---|---|
| QA-D-001 | Build gate definition management screens | FE-APP | QA-B-008 | Quality admins can view/create/activate gate definitions via APIs | E2E happy-path pass |
| QA-D-002 | Build gate instance dashboard and detail screen | FE-APP | QA-C-003 | Operations and quality actors can inspect gate state and hold context | E2E read-model pass |
| QA-D-003 | Extend measurement entry for gate instance context | FE-APP | QA-B-003 | Measurement UX captures only observed facts and honors required-item gating | E2E completeness pass |
| QA-D-004 | Build deviation request and disposition workflows | FE-APP | QA-B-005, QA-B-006 | Quality actors can request deviation and record disposition with clear audit context | E2E governed-action pass |
| QA-D-005 | Surface quality gate and hold visibility in operation detail | FE-APP | QA-C-003 | Operation screens show quality state without deriving backend truth | route and regression tests pass |
| QA-D-006 | Enforce i18n key parity for all new QA UI strings | FE-APP | QA-D-001, QA-D-002, QA-D-003, QA-D-004, QA-D-005 | en and ja registries synchronized, no hardcoded UI strings | lint:i18n and registry checks pass |
| QA-D-007 | Add Playwright coverage for full quality gate journeys | QA-AUTO | QA-D-004, QA-D-005 | E2E covers pass, hold, recheck, release, and unauthorized paths | CI Playwright suite pass |

## Phase E — Reporting, governance, and release hardening

| Ticket ID | Title | Owner | Depends on | Acceptance criteria | Validation gate |
|---|---|---|---|---|---|
| QA-E-001 | Implement quality KPI read models (hold aging, disposition outcomes) | BE-QLTY | QA-C-003 | KPI endpoints return stable quality governance metrics | API and projection tests pass |
| QA-E-002 | Add quality audit timeline query API | BE-QLTY | QA-B-009 | Timeline returns measurement, hold, deviation, and decision events | audit query tests pass |
| QA-E-003 | Add security-event completeness checks for governed actions | SEC-GOV | QA-B-006, QA-E-002 | Every governed disposition path emits required security/audit records | governance tests pass |
| QA-E-004 | Build production migration dry-run and rollback scripts | DATA-OPS | QA-A-006, QA-C-004 | Dry-run and rollback documented and tested on staging snapshot | migration rehearsal pass |
| QA-E-005 | Define feature flags and tenant rollout strategy | PO-SA | QA-C-003, QA-D-005 | Controlled tenant and line enablement plan with rollback conditions | release review accepted |
| QA-E-006 | Final go/no-go checklist and signoff package | PO-SA | QA-E-001, QA-E-002, QA-E-003, QA-E-004, QA-E-005 | Signed quality, execution, security, and operations approvals | release gate pass |

## Cross-phase technical debt and exclusions tickets

| Ticket ID | Title | Owner | Depends on | Acceptance criteria |
|---|---|---|---|---|
| QA-X-001 | Track CAPA future phase boundary | PO-SA | none | CAPA remains excluded from this release scope and moved to later roadmap phase |
| QA-X-002 | Track supplier quality future phase boundary | PO-SA | none | Supplier quality remains excluded from this release scope |
| QA-X-003 | Track document control integration boundary | PO-SA | none | Document control replacement explicitly out of scope for this implementation wave |

## Milestone plan

- Milestone M1: `Phase A` complete (`QA-A-*` closed)
- Milestone M2: `Phase B` complete (`QA-B-*` closed)
- Milestone M3: `Phase C` complete (`QA-C-*` closed)
- Milestone M4: `Phase D` complete (`QA-D-*` closed)
- Milestone M5: `Phase E` complete and release signoff (`QA-E-*` closed)

## Suggested labels for issue tracker

- `domain:quality`
- `area:backend`
- `area:frontend`
- `area:execution`
- `area:governance`
- `area:migration`
- `type:feature`
- `type:test`
- `priority:p0`

## Immediate next ticket to start

Start with `QA-A-001` and `QA-A-006` preparation tasks (entity contract review plus migration strategy) before API work.
