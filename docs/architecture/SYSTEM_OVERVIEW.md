# SYSTEM_OVERVIEW

## Purpose
Provide a concise architecture snapshot of the MES modular monolith and its decision/execution boundaries.

## Scope
- Frontend (React + TypeScript)
- Backend (FastAPI + SQLAlchemy)
- Execution model ownership
- Monitoring and dashboard read surfaces

## Key Decisions (LOCKED)
- Modular monolith architecture is current target.
- Backend is the source of truth for execution and decision metrics.
- Execution state is event-driven and derived from append-only events.
- Read and write concerns are separated by surface and API contract.
- Tenant scoping is required in backend service/repository access.

## Explicitly Out Of Scope
- Microservice split
- Event streaming platform introduction
- AI execution ownership

## Future (FUTURE)
- Internal modular refinement without changing core execution boundaries.
