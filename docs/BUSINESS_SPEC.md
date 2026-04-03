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

## Phase 5A — i18n Infrastructure (Completed)
Internationalization infrastructure was prepared early to establish a stable, typed translation contract before any runtime language behavior is introduced. This sequencing protects execution stability, prevents inconsistent text patterns, and keeps business semantics aligned across personas.

What was added (infrastructure only):
- i18n module folder and export entrypoint in frontend
- Domain-based namespaces
- Semantic key typing
- EN placeholder registry
- Stub translation hook surface for future phase wiring

What was intentionally NOT done:
- No UI text replacement in existing screens
- No locale switching behavior
- No language selector UI
- No backend API changes
- No runtime behavior changes

## Phase 2B — Global Operations Enhancement (Supervisor View)
Phase 2B was required to make Global Operations operationally useful for supervisor intervention, not just generic monitoring. The enhancement prioritizes what blocks production now and surfaces immediate Work Order impact while preserving read-only boundaries.

Value for the Supervisor persona:
- Faster triage of blocked and delayed operations
- Clear view of which Work Orders are impacted
- Better investigation ordering without entering execution controls

What was intentionally NOT included:
- No execution actions in Operations
- No dashboard KPI aggregation logic
- No role/auth enforcement
- No IE-specific or QA-specific dedicated views (future phases)
