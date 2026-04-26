# Runtime Architecture Overview

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified modular-monolith boundaries for session-owned execution and future mode-specific apps. |

Status: Runtime architecture note.

## 1. Current runtime posture

- modular monolith
- FastAPI backend
- React frontend
- PostgreSQL source-of-truth store
- event-driven execution with projections/read models

## 2. Architectural modules to keep boundary-clean

- foundation / auth / access / session
- execution core
- quality
- traceability
- supervisory
- material
- maintenance/equipment context
- AI / analytics / digital twin
- integration adapters

## 3. Boundary-clean rule

The current runtime may remain a modular monolith, but module contracts must remain extraction-ready.
That especially applies to:
- session lifecycle
- execution events and projections
- quality gating
- traceability/genealogy
- AI advisory services

## 4. Execution-specific runtime decision

Execution mutations should flow through services that resolve:
- authenticated user context
- effective operator context
- effective equipment/resource context
- tenant/scope context

The runtime must not allow frontend-owned or route-owned truth for those concerns.
