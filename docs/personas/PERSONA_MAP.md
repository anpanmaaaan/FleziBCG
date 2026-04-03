# PERSONA_MAP

## Purpose
Map business personas to decision responsibilities without changing execution ownership boundaries.

## Scope
- Production Manager
- Supervisor
- Operator
- Office / Coordination roles

## Key Decisions (LOCKED)
- Production Manager: Uses dashboard summary/health for prioritization and escalation decisions.
- Supervisor: Uses Work Order and operation monitoring to identify risk and route response.
- Operator: Executes only through Station Execution runtime workflow.
- Office/Coordination: Uses read-only monitoring and dashboard context for communication and planning support.

## Explicitly Out Of Scope
- Persona-specific write permissions beyond current execution model
- AI-assisted persona actions
- Role-policy redesign

## Future (FUTURE)
- Persona-specific dashboards/views only if they preserve read/write separation.
