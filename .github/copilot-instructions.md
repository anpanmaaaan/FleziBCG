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

## Non-goals
- no AI control
- no advanced scheduling
- no external workflow engine
- no streaming platform