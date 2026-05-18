# FleziBCG Current Implementation Truth

Status: Active
Last updated: 2026-05-17

This document is the short implementation truth for the pilot MVP track. It is
not a replacement for the business contract in `docs/system/mes-business-logic-v1.md`.
It tells implementation agents what is real in the repo today, what is partial,
and what must not be treated as operational truth.

## Authority Order

Use these sources in this order when planning or implementing a slice:

1. Backend code and tests under `backend/app` and `backend/tests`.
2. `docs/system/mes-business-logic-v1.md` for MES execution business rules.
3. `frontend/src/app/screenStatus.ts` for frontend screen maturity.
4. This file for current pilot scope and known non-goals.
5. Historical roadmap and closeout reports only as context.

If these sources disagree, do not expand scope. Patch the smallest active source
needed to remove the contradiction before writing feature code.

## Current Runtime Shape

FleziBCG is currently a modular-monolith MES/MOM application:

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL.
- Frontend: React/Vite, route-based MOM workspace, screen maturity registry.
- Deployment: Docker Compose with PostgreSQL, backend on port 8010, frontend via nginx on port 80.
- Pilot runtime mode: `DISCRETE`.
- Future supported profile: `BATCH_PROCESS`.

Backend remains the source of truth for authentication, authorization,
execution state, quality evaluation, allowed actions, and audit/security events.
Frontend route visibility and persona navigation are UX only.

## Backend Areas That Are Real

These domains have backend models/services/routes/tests and can be used as
pilot building blocks:

- Auth, refresh token, logout, logout-all, session revoke.
- Tenant anchor, RBAC, role/scope assignment, plant hierarchy.
- Impersonation, approvals, audit/security event foundation.
- Production orders, work orders, operations, dashboard summaries.
- Station queue, station sessions, operator identification, equipment binding.
- Execution commands: start, pause, resume, report quantity, downtime, complete, abort, close, reopen.
- Manufacturing master data: products, product versions, routings, routing operations, BOMs, resource requirements, reason codes.
- Quality lite: quality gate definitions/instances, measurements, holds, dispositions, deviations, nonconformances.
- Manufacturing mode profile anchors: tenant default plus plant/scope overrides.

## Frontend Screen Maturity

The frontend source of truth is `frontend/src/app/screenStatus.ts`.

Pilot-critical connected screens include:

- Login.
- Dashboard.
- Production Orders.
- Work Orders and Work Order Operations.
- Global Operations.
- Station Execution.
- QC Checkpoints and Defect Management.
- Operation Timeline.
- Station Session, Operator Identification, Equipment Binding.
- Quality Dashboard, Measurement Entry, Quality Holds, Quality Deviations, Quality Nonconformances.

Pilot-adjacent partial screens include:

- Product List and Product Detail.
- Route List, Route Detail, Routing Operation Detail.
- Operation Detail.
- User Management.
- Security Events.
- BOM List and BOM Detail.
- Resource Requirements.
- Reason Codes.

Screens currently treated as mock or shell must not be used as operational truth:

- Home, OEE Deep Dive, Dispatch Queue, Traceability, APS Scheduling.
- Role Management, Action Registry, Scope Assignments, Session Management, Audit Log, Tenant Settings, Plant Hierarchy.
- Line Monitor, Station Monitor, Downtime Analysis, Shift Summary, Supervisory Operation Detail.
- Material Readiness, Staging/Kitting, WIP Buffers.
- Integration, reporting, AI, digital twin, compliance, e-signature, electronic batch record screens.

## Pilot Golden Path Target

The next implementation work should harden one end-to-end path:

1. Login as seeded pilot roles.
2. Supervisor or manager sees production orders and operations.
3. Operator opens a station session.
4. Operator identifies themselves and binds equipment.
5. Operator sees the station queue.
6. Operator starts an operation.
7. Operator pauses/resumes or records downtime.
8. Operator reports good and scrap quantity.
9. Operator submits required quality measurements.
10. Backend evaluates quality.
11. Quality hold blocks completion when required.
12. QA resolves hold/deviation/nonconformance.
13. Operator completes and closes the operation.
14. Supervisor sees status and timeline from backend truth.

Every step must be backed by real API behavior and tests before frontend polish.

## Batch/Process Boundary

FleziBCG must support both discrete and batch/process manufacturing over time.
The current implementation does not include batch/process runtime.

Current guardrail:

- `DISCRETE` is the active pilot runtime mode.
- `BATCH_PROCESS` is a supported future profile.
- Tenant, plant, and scope records can carry manufacturing mode profile data.
- No recipe, procedure, ISA-88 phase state machine, weighing/dispensing, process parameter runtime, or eBR runtime is implemented.

Batch/process work must begin with design and schema slices after the discrete
pilot path is stable, or earlier only if a real pilot customer requires it.

## Current Non-Goals

Do not implement or present these as real pilot capabilities yet:

- AI recommendations or AI-driven decisions.
- APS optimizer or automatic dispatch recommendations.
- ERP/WMS/QMS/CMMS integrations.
- Full material backflush.
- Operational digital twin simulation.
- Regulated e-signature or electronic batch record.
- Batch/process recipe or phase runtime.

## How To Continue

Use `docs/implementation/pilot-mvp-continuous-operating-plan.md` as the weekly
execution loop. Pick one narrow business slice, prove backend truth first, then
connect the frontend and update `screenStatus.ts` in the same slice.

