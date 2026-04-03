# PHASE 2B — Global Operations Enhancement (Supervisor View)

Status: COMPLETED (Baseline Locked)

## Purpose
Phase 2B refines Global Operations into a Supervisor-focused investigation workspace so operational intervention priorities are visible immediately without entering execution surfaces.

This phase clarifies layer responsibilities:
- Dashboard: decision-level KPI and health interpretation.
- Work Orders: execution-context tracking by work order flow.
- Operations (Global): read-only cross-work-order investigation for active blockers and delays.

## Persona Focus (Supervisor)
Supervisor questions this screen must answer:
- Where is production currently blocked or delayed?
- Which Work Orders are impacted right now?
- What should be investigated first?

This screen explicitly does NOT attempt to solve:
- Dashboard KPI synthesis and management-level rollups.
- Long-horizon IE/process analytics.
- Execution actions or station-level control.

## Scope
In scope:
- Read-only investigation enhancements for global operations.
- Status-first prioritization for urgent operational states.
- Work Order impact visibility for fast triage.

Out of scope:
- Execution actions (start/complete/report).
- KPI aggregation and dashboard semantics.
- Role/auth enforcement.
- IE and QA dedicated lenses (future phases).

## Backend Design (Read-only)
Phase 2B uses service-layer derivation for investigation fields while preserving data ownership boundaries.

Derived in service layer:
- `supervisor_bucket`
- `delay_minutes`
- `block_reason_code`
- `qc_risk_flag`
- `wo_blocked_operations` / `wo_delayed_operations`

Repository layer remains data-only and must not contain business rules.

## Frontend Design (Supervisor Lens)
The Supervisor lens behavior is investigation-oriented and read-only:
- Default prioritization favors `BLOCKED`, then `DELAYED`, then `IN_PROGRESS`.
- Ordering then follows delay duration (descending) for intervention urgency.
- Work Order impact is visible per operation and can be reviewed via Work Order grouping.
- Row interaction navigates only to Operation Detail (read-only context).
- No navigation shortcuts to execution write surfaces are introduced.

## UX Principles (LOCKED)
- Global Operations is an investigation workspace.
- Dashboard semantics must not be mixed into Operations.
- No visual or interaction pattern may imply execution control from this screen.

## Relationship to Other Phases
- Builds on Phase 2 baseline read-only Operations monitoring.
- Respects Phase 3 Dashboard boundary by avoiding KPI aggregation responsibilities.
- Prepares clean semantics for future Role/Auth enforcement phases without implementing enforcement in Phase 2B.

## Locked Constraints (Non-Negotiable)
- Global Operations remains read-only.
- Supervisor view must not become a Dashboard substitute.
- Role/auth enforcement cannot be introduced without a new approved phase.

## Completion Summary
Phase 2B is a semantic milestone for Operations: it transforms a generic monitoring list into a Supervisor-first investigation surface while preserving strict read-only and layer-boundary rules. This improves intervention clarity without altering execution authority, dashboard ownership, or access-control scope.