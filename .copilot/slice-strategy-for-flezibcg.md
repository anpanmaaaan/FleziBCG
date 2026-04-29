# Slice Strategy for FleziBCG

## Status

Recommended implementation strategy for FleziBCG after latest design baseline, hardening, source audit response, CODING_RULES v2.0, AI Brain v6, and Hard Mode MOM.

## Purpose

This document defines how FleziBCG should be implemented incrementally.

The goal is not to “build the whole backend first”.

The goal is to build a working, testable MOM platform through vertical slices:

```text
Design baseline → small slice → DB/BE/test/minimal FE verification → verify → next slice
```

---

# 1. Core Implementation Philosophy

## 1.1 Build system slices, not backend modules

Do not implement large backend modules in isolation.

Each slice should produce a verifiable system capability.

A proper slice may include:

- DB / migration
- backend model / repository
- service logic
- API route
- tests
- minimal frontend/API verification if needed
- documentation update if contract changes

## 1.2 Backend remains the source of truth

Frontend must not decide:

- execution state
- authorization
- approval
- operational truth

Frontend may:

- display backend-derived state
- send user intent
- guide interaction
- show backend-provided allowed actions

## 1.3 Smallest useful slice wins

A slice should be:

- small enough to review
- testable
- aligned with design baseline
- not mixed with unrelated refactor
- not dependent on future modules unless explicitly planned

## 1.4 Hard Mode MOM applies to execution-critical slices

If a slice touches execution, state machine, events, projections, station/session/operator/equipment, production reporting, downtime, completion, tenant/scope/auth, or critical invariants:

```text
Hard Mode MOM = ON
```

Reject implementation if:

- state machine is wrong
- required event is missing
- required invariant is missing
- projection is treated as source of truth
- frontend becomes execution truth
- service layer is bypassed

---

# 2. Slice Anatomy

Every implementation slice should follow this structure.

## 2.1 Slice definition

```markdown
## Slice ID
## Goal
## In scope
## Out of scope
## Design references
## DB / migration impact
## Backend impact
## Frontend impact
## Tests required
## Verification commands
## Risks
## Done criteria
```

## 2.2 Minimum done criteria

A slice is not done until:

- tests pass
- migration is safe if DB changed
- API behavior is verified if API changed
- no forbidden scope is added
- docs/ADR impact is checked
- implementation plan and verification report are updated

---

# 3. Recommended Phase Order

The recommended order is:

```text
P0-A Foundation Database Slice
→ P0-B Manufacturing Master Data Minimum
→ P0-C Execution Core
→ P0-D Quality Lite
→ P0-E Supervisory Operations
→ P1-A Integration Foundation
→ P1-B Acceptance Gate
→ P1-C Material Readiness + Backflush
→ P1-D Reporting / KPI / OEE
→ P1-E Andon / Notification / Maintenance Lite
→ P2+ APS / AI / Digital Twin / Compliance
```

Do not jump to AI, APS, Backflush, Acceptance Gate, Digital Twin, or Compliance before foundation and execution truth are stable.

---

# 4. P0-A — Foundation Database Slice Strategy

## Goal

Build the minimum governance/foundation layer required before manufacturing execution can be safely implemented.

## Why first

Execution, MMD, quality, material, and reporting all require:

- tenant
- scope
- user/session/auth
- plant hierarchy
- audit/security events
- migration discipline

## Slice P0-A-01 — Runtime Config Hardening

Status: already implemented if CORS hardening slice exists.

### Scope

- environment-driven backend config
- CORS allow-list
- startup import check
- focused tests

### Done criteria

- backend imports successfully
- CORS test passes
- no domain behavior touched

---

## Slice P0-A-02 — Alembic Foundation

### Goal

Replace ad-hoc schema evolution with explicit migration discipline.

### In scope

- Alembic config
- migration environment
- baseline revision
- upgrade verification on clean DB if possible
- documentation of migration command

### Out of scope

- broad schema redesign
- execution schema
- MMD schema
- ERP integration
- full data migration from legacy DB unless already required

### Tests / verification

```bash
cd backend
alembic upgrade head
pytest
```

If local DB setup is incomplete, verify with a temporary clean database or document blocker clearly.

### Done criteria

- Alembic exists
- migration can run
- current models/schema are represented or safely baselined
- create_all is no longer the canonical production path

---

## Slice P0-A-03 — Remove Production create_all Path

### Goal

Prevent application startup from mutating production schema implicitly.

### In scope

- disable/remove automatic `create_all()` from normal startup
- preserve explicit local/dev bootstrap if needed
- test/import verification
- README/dev instruction update if needed

### Out of scope

- rewriting all DB init scripts
- changing business schema
- station execution refactor

### Done criteria

- app startup does not create schema implicitly in production path
- local bootstrap path is explicit
- tests/import pass

---

## Slice P0-A-04 — Tenant Foundation

### Goal

Create canonical tenant base for multi-tenant platform behavior.

### In scope

- tenant model/table if missing
- tenant lifecycle status
- tenant_id relationship for tenant-owned foundation entities
- tenant context utility if currently missing
- tests for tenant isolation basics

### Out of scope

- RLS
- multi-tenant billing
- tenant admin UI beyond minimal placeholder
- cross-tenant analytics

### Done criteria

- tenant exists as explicit concept
- tenant-owned queries are not tenant-blind
- tests cover wrong-tenant rejection where applicable

---

## Slice P0-A-05 — IAM User Lifecycle Alignment

### Goal

Align user model with governance baseline.

### In scope

- user lifecycle status
- password/auth compatibility if already present
- server-side authorization checks remain explicit
- tests for active/inactive user behavior

### Out of scope

- enterprise SSO
- SCIM
- MFA
- full IAM UI

### Done criteria

- user lifecycle is explicit
- disabled/inactive user cannot act
- tests cover allowed and rejected cases

---

## Slice P0-A-06 — Session / Refresh Token Foundation

### Goal

Create safe session lifecycle foundation.

### In scope

- user session table alignment
- refresh token table/foundation
- logout current session
- logout all sessions / revoke all
- token rotation path if sufficiently specified
- tests

### Out of scope

- device management UI
- advanced risk scoring
- OAuth/OIDC

### Done criteria

- session lifecycle is testable
- revoke/logout behavior is deterministic
- refresh token path does not rely only on frontend state

---

## Slice P0-A-07 — Role / Action / Scope Foundation

### Goal

Build minimal authorization foundation.

### In scope

- action registry foundation
- role/action assignment
- scope assignment
- server-side authorization dependency/service
- tests for allowed/denied actions

### Out of scope

- OPA/Casbin migration
- full policy engine
- advanced SoD workflow

### Done criteria

- JWT is identity only
- permission checked server-side
- role/action/scope works in tests

---

## Slice P0-A-08 — Plant Hierarchy Foundation

### Goal

Create canonical operational hierarchy.

### In scope

- plant
- area
- line
- station
- equipment
- hierarchy relationships
- lifecycle/status where required
- tests for parent/child consistency

### Out of scope

- equipment telemetry
- OPC UA/MQTT/Sparkplug
- SCADA integration
- Digital Twin graph

### Done criteria

- hierarchy exists and can support execution later
- station/equipment have tenant/scope context
- tests cover invalid hierarchy references

---

## Slice P0-A-09 — Audit / Security Event Foundation

### Goal

Ensure governed actions are auditable.

### In scope

- audit log/security event model if missing
- actor/time/action/context fields
- append-only posture
- service helper to record security/audit event
- tests for audit event creation

### Out of scope

- compliance e-record
- e-signature
- external SIEM integration

### Done criteria

- privileged/security-sensitive events can be recorded
- event contains actor/time/action/context
- tests cover audit creation

---

## Slice P0-A-10 — Backend CI Minimum

### Goal

Ensure minimum automated verification.

### In scope

- GitHub Actions backend test workflow
- install dependencies
- run pytest
- optional lint/typecheck if already configured

### Out of scope

- full deployment pipeline
- container registry
- production infra

### Done criteria

- PR can run backend tests
- docs-only PRs can skip heavy checks if configured
- workflow passes or failure reason is explicit

---

# 5. P0-B — Manufacturing Master Data Minimum

## Goal

Create the minimum manufacturing definitions required before execution core.

## Build only after P0-A foundation is stable.

## Slice P0-B-01 — Product Foundation

### Scope

- product table/model
- product status
- product version if design requires
- list/detail API
- tests

### Out of scope

- full PLM
- complex version workflow
- ERP master data sync

---

## Slice P0-B-02 — Routing Foundation

### Scope

- routing
- routing operation
- sequence/order
- product-routing relation
- released/draft status if specified
- tests

### Out of scope

- full recipe/ISA-88
- advanced planning
- optimization

---

## Slice P0-B-03 — Resource Requirement Mapping

### Scope

- operation to station/equipment requirement
- work center/resource requirement
- validation against plant hierarchy
- tests

### Out of scope

- finite capacity scheduling
- APS
- equipment telemetry

---

## Slice P0-B-04 — Reason Code / Reference Data Foundation

### Scope

- reason code categories where needed
- downtime reason foundation if specified
- master-data vs enum policy alignment
- read-only APIs if applicable

### Out of scope

- broad admin UI
- enterprise master data governance workflow

---

# 6. P0-C — Execution Core Slice Strategy

## Goal

Build production-grade minimum execution truth.

Hard Mode MOM is always ON for P0-C.

## Slice P0-C-01 — Work Order / Operation Foundation

### Scope

- work order
- operation
- lifecycle/status projection
- tenant/scope/hierarchy links
- tests

### Required

- backend-derived status
- no frontend truth
- no shortcut completion

---

## Slice P0-C-02 — Station Session Foundation

### Scope

- station session
- operator identification context
- equipment binding where required
- active session invariant
- tests

### Required invariants

- no duplicate active session where uniqueness is required
- station/session/operator context explicit
- tenant/scope enforced

---

## Slice P0-C-03 — Execution Event Log

### Scope

- append-only execution event table/model
- event schema
- event append helper/service
- projection update pattern
- tests

### Required

- events include actor/time/entity/context
- projection is not source of truth

---

## Slice P0-C-04 — Start Execution Command

### Scope

- start execution command/API
- validate current state
- emit `ExecutionStarted` or canonical equivalent
- update projection
- return backend-derived allowed actions
- tests

### Required tests

- valid start
- invalid state
- wrong tenant/scope
- missing permission
- duplicate start

---

## Slice P0-C-05 — Pause / Resume Execution

### Scope

- pause command
- resume command
- events
- projection update
- tests

### Required tests

- pause only from running
- resume only from paused
- duplicate behavior safe/rejected

---

## Slice P0-C-06 — Production Reporting

### Scope

- report good/scrap quantity
- event emission
- projection update
- quantity validation
- tests

### Out of scope

- rework full flow
- backflush
- ERP posting

---

## Slice P0-C-07 — Downtime Start / End

### Scope

- start downtime
- end downtime
- reason code relation
- event emission
- projection update
- tests

### Required tests

- cannot end unopened downtime
- cannot double-open if invariant disallows
- tenant/scope/auth checks

---

## Slice P0-C-08 — Complete / Close / Reopen

### Scope

- complete execution
- close operation
- controlled reopen if baseline supports
- events
- projection update
- tests

### Required

- no complete without conditions
- closed operation cannot mutate unless reopen exists
- event/projection consistency

---

# 7. P0-D — Quality Lite Slice Strategy

## Goal

Add minimum operational quality interaction without becoming full QMS.

## Slice P0-D-01 — QC Requirement Link

- operation/product quality requirement
- applicability
- tests

## Slice P0-D-02 — Measurement Entry

- measurement entry
- backend validation
- tests

## Slice P0-D-03 — Backend Evaluation

- pass/fail/hold evaluation
- no frontend pass/fail truth
- tests

## Slice P0-D-04 — Quality Hold Visibility

- quality hold status visible to execution/supervisor
- allowed_actions blocked where applicable
- tests

Out of scope:

- full Acceptance Gate
- deviation approval
- CAPA
- enterprise QMS

---

# 8. P0-E — Supervisory Operations Slice Strategy

## Goal

Create read-only visibility from execution truth.

## Slice P0-E-01 — Operation List / Detail Read Model

- operation list
- operation detail
- filters
- backend read model
- tests

## Slice P0-E-02 — Line / Station Monitor

- station state projection
- line monitor
- tests

## Slice P0-E-03 — Event Timeline

- operation event timeline
- read-only
- tests

## Slice P0-E-04 — Basic Reports

- downtime summary
- production summary
- deterministic only
- tests

Out of scope:

- AI insight
- full OEE deep dive
- APS
- Digital Twin

---

# 9. When Minimal FE Is Needed

FE is not required for every foundation slice.

Add minimal FE only when it verifies or stabilizes real user flow.

## FE required earlier for

- login/session verification
- user/session management if already present
- station execution flow
- operator action flow
- supervisor read-only visibility

## FE not required yet for

- pure migration foundation
- backend-only invariant
- internal audit event helper
- CI setup

## FE rule

Frontend must not become truth.

If FE is added, it should:

- call backend API
- show backend-derived state
- display backend-provided allowed actions
- avoid local business rule duplication

---

# 10. Agent Continuation Rule

Agent should continue automatically slice by slice.

After each slice:

1. update `docs/implementation/autonomous-implementation-plan.md`
2. update `docs/implementation/autonomous-implementation-verification-report.md`
3. run tests
4. select next safest slice
5. continue

Stop only if:

- design contradiction exists
- migration risk requires human decision
- business logic must be invented
- Hard Mode MOM rejects the approach
- remaining scope belongs to excluded future modules

---

# 11. Recommended Immediate Next Slices

Given current status, the next sequence should be:

```text
P0-A-02 Alembic Foundation
P0-A-03 Remove Production create_all Path
P0-A-04 Tenant Foundation
P0-A-05 IAM User Lifecycle Alignment
P0-A-06 Session / Refresh Token Foundation
P0-A-07 Role / Action / Scope Foundation
P0-A-08 Plant Hierarchy Foundation
P0-A-09 Audit / Security Event Foundation
P0-A-10 Backend CI Minimum
```

Then move to:

```text
P0-B MMD Minimum
P0-C Execution Core
```

Do not start P0-C until P0-A and required P0-B foundations are stable.

---

# 12. Final Principle

Do not build a backend monolith in isolation.

Build FleziBCG as a verified system:

```text
foundation → master data → execution truth → quality lite → supervisory visibility
```

Each slice must produce a safer, more truthful, more testable system.
