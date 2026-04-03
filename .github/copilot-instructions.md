# MES Lite Project Instructions

## Project type
This repository contains a lightweight MES system with:
- frontend in `frontend/`
- backend in `backend/`
- docs in `docs/`

## Backend stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- JWT auth
- simple RBAC
- modular monolith

## Architecture rules
- UI sends intent only
- backend is the source of truth
- backend derives state from append-only execution events
- no direct UI state mutation for execution status
- multi-tenant with tenant_id on tenant-owned tables
- enforce tenant filtering in service/repository layer
- Phase 1 only: deterministic MES execution, no AI/ML, no APS, no streaming infra

## Execution flow baseline (LOCKED)

The following execution flow is non-negotiable:

- Execution entry starts at Work Order, not Production Order
- Production Order is planning context and filter only
- Operation is the smallest execution unit
- Station Execution is the only write surface

Canonical execution flow:
- /work-orders
- /work-orders/:woId/operations
- /operations/:operationId/detail
- /station-execution?operationId=...

Do NOT introduce screens that mix Production Order, Work Order,
and Operation execution semantics.

## Coding rules
- keep modules small and explicit
- prefer service layer over putting logic in route handlers
- repository layer must not contain business rules
- use Pydantic schemas for request/response
- write clear names, avoid magic values
- do not over-engineer
- do not introduce Kafka, microservices, or cloud-only dependencies

## Business scope
Phase 1 includes:
- dashboard read APIs
- operations list/detail APIs
- execution tracking
- operation start
- quantity reporting
- operation complete
- QC measure record (backend computes pass/fail)

## Phase 2 scope (READ-ONLY monitoring)

Phase 2 introduces a Global Operation List for monitoring only.

Rules:
- Global Operation List is read-only
- No start / complete / report actions allowed
- No execution state derivation in frontend
- Backend remains source of truth

Allowed:
- status display via enum mapping
- filters by status, work center, WO, PO
- drill-down to operation detail

Not allowed:
- write actions
- business rule inference in UI

## Non-goals
- no AI control
- no advanced scheduling
- no external workflow engine
- no streaming platform

## Future-ready guardrails

### AI
- AI is advisory only
- AI may read execution events and history
- AI must never trigger or control execution actions
- No AI logic in execution or service layers in Phase 1–2

### Multi-language (i18n)
- Backend returns enums and codes, not translated text
- UI text must not contain business logic
- Prefer semantic keys for UI text (i18n-ready)
- Language preference belongs to tenant or user

### Microservice
- Current architecture is modular monolith
- Do NOT prematurely split into microservices
- Clear module boundaries are preferred over service extraction

## Phase 4 — RBAC & Persona Landing (LOCKED)

- Persona to default landing rules:
	- OPERATOR -> /station-execution
	- SUPERVISOR / SHIFT_LEADER -> /work-orders
	- MANAGER / OFFICE -> /dashboard
	- IE / PROCESS -> /operations
	- QA -> /quality

- Guardrail rules:
	- Agents MUST NOT change persona landing without new phase
	- Agents MUST NOT expose Station Execution to non-operators
	- Agents MUST NOT make Operations (Global) a manager default
	- Agents MUST NOT introduce execution logic into Dashboard

- Enforcement notes:
	- Phase 4 RBAC is frontend/UX-level only
	- Backend execution APIs are unchanged
	- Future phases may extend RBAC but must not violate these rules

## Phase 5A — i18n Infrastructure Rules (LOCKED)

- From Phase 5A onward:
	- All new UI text MUST use semantic i18n keys
	- Hardcoded business text is forbidden

- Backend MUST continue returning enums/codes only

- i18n runtime behavior MUST NOT be enabled without a new phase

- Phase 5B is the earliest phase allowed to:
	- Replace UI text with t()
	- Add language selector
	- Introduce locale switching

## Phase 2B — Global Operations Supervisor Rules (LOCKED)

- Global Operations is READ-ONLY.
- Supervisor view prioritizes BLOCKED and DELAYED operations.
- Operations MUST NOT include execution actions.
- Operations MUST NOT aggregate KPIs (Dashboard responsibility).
- Persona awareness does NOT imply role enforcement.
- IE / QA views are future phases and must not be mixed.