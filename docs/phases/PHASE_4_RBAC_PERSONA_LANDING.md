# PHASE 4 — RBAC & Persona-Based Landing

Status: COMPLETED (Baseline Locked)

## Purpose
Persona-based landing is required in a real MES to reduce role confusion, improve operational safety, and align each role with the correct decision surface at first entry.

This phase enforces clear separation of execution, monitoring, and decision layers:
- execution for runtime control,
- monitoring for read-only operational visibility,
- dashboard for decision-level synthesis.

## Scope
In scope:
- Persona-based default landing at application entry
- Persona-based menu visibility rules
- Route guardrails that keep users inside the correct layer

Out of scope:
- Backend authorization redesign
- Fine-grained permission matrix and policy engine
- i18n framework implementation
- AI logic or AI-driven routing

## Persona Definitions (LOCKED)
- Operator: Executes assigned operation work at station level.
- Shift / Line Leader: Monitors live line/work-order status and coordinates immediate response.
- Supervisor: Oversees execution progress and exceptions across work orders.
- Production Manager: Uses summary and health views for production decisions.
- Quality Engineer (QA): Focuses on quality checkpoints, defects, and quality signals.
- Process / IE Engineer: Monitors global operational flow and process-level patterns.
- Office / Management: Uses high-level dashboard visibility for business oversight.

## Persona → Default Landing Mapping (LOCKED)
- Operator → /station-execution
- Shift / Line Leader → /work-orders
- Supervisor → /work-orders
- Production Manager → /dashboard
- Office / Management → /dashboard
- Process / IE Engineer → /operations
- Quality Engineer (QA) → /quality

Rules:
- Mapping is applied on login and reload at /.
- Default landing is routing guidance only and does not grant permissions.

## Menu Visibility Rules
- Menu visibility is UX guidance, not a security boundary.
- Visible entries should prioritize persona-relevant surfaces and de-emphasize unrelated ones.

Example visibility by persona:
- Operator: Station Execution as primary; execution-monitoring links secondary.
- Shift / Line Leader and Supervisor: Work Orders primary; dashboard/quality secondary.
- Production Manager and Office / Management: Dashboard primary; work-orders monitoring secondary.
- Process / IE Engineer: Operations (Global) primary; work-order monitoring secondary.
- QA: Quality primary; dashboard and monitoring as supporting context.

## Route Guardrails (CRITICAL)
- When a persona attempts to enter a non-assigned layer, routing guardrails redirect to the persona default landing.
- Guardrails must avoid error pages and avoid partial rendering of disallowed surfaces.
- Redirect behavior is deterministic and consistent on direct URL access and refresh.

## Execution Safety Guarantees
- StationExecution remains the only write surface for runtime execution actions.
- Persona routing and menu behavior must not bypass execution boundaries.
- No persona receives implicit execution write capability via landing or menu rules.

## Relationship to Other Phases
- Phase 1 defines and locks execution flow and write ownership.
- Phase 2 defines read-only global operation monitoring.
- Phase 3 defines read-only dashboard decision APIs.
- Phase 4 binds Phases 1–3 by assigning stable persona entry points and guardrails aligned to those boundaries.

## Locked Constraints (Non-Negotiable)
- Persona landing mapping must not change without a new phase decision.
- Dashboard must not drill into Operations.
- Operations must not become the manager default landing.
- Station Execution must not be exposed to non-operators as a default surface.

## Completion Summary
Phase 4 finalizes persona-safe entry and navigation as an architectural baseline. It operationalizes read/write separation in day-to-day usage, preserves backend source-of-truth ownership, and prevents layer-mixing between execution control, monitoring, and managerial decision surfaces.
