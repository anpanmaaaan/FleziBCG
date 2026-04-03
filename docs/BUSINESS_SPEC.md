# BUSINESS_SPEC

## Purpose
Define the MES business boundaries and decision model across completed phases, with execution as the operational core and dashboard as a read-only decision surface.

## Scope
- Phase 1 execution control and tracking
- Phase 2 global operations monitoring (read-only)
- Phase 3 dashboard backbone (summary + health)
- Persona-aligned responsibilities for Production Manager, Supervisor, Operator, and Office roles

## Key Decisions (LOCKED)
- Execution entry is Work Order, not Production Order.
- Operation is the smallest execution unit.
- Station Execution is the only write surface for execution lifecycle actions.
- Backend is the single source of truth; frontend does not derive execution rules.
- Global Operations view is monitoring-only and read-only.
- Dashboard is decision-level and read-only (problem detection, location, and drill-down intent).
- Dashboard drill-down contract points to Work Orders context, not execution write screens.
- Tenant isolation is mandatory for backend reads and writes.

## Explicitly Out Of Scope
- AI-driven execution control
- Advanced scheduling / APS optimization logic
- Streaming/event bus infrastructure
- Microservice decomposition in current phases
- Frontend-side business rule inference

## Future (FUTURE)
- Additional decision metrics only if derived in backend service layer
- Extended persona-based reporting views without changing execution ownership boundaries
