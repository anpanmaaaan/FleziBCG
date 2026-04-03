# PHASE 2C — Global Operations Enhancement (IE / Process View)

Status: COMPLETED (Baseline Locked)

## 1. Purpose & System Positioning
Phase 2C establishes an IE / Process investigation lens inside the existing Global Operations screen. This lens belongs to the operational investigation layer: it is read-only, pattern-oriented, and process-improvement focused.

Layer separation is explicit:
- Execution layer: runtime operation control (start, report, complete, abort) is outside this lens.
- Supervisor investigation layer: incident-first prioritization remains the Phase 2B concern.
- Dashboard layer: KPI synthesis and managerial summary remain Phase 3 concerns.
- IE / Process layer: recurring process deviation analysis without execution control.

## 2. IE / Process Persona Definition
This view is for IE and Process Engineering users who need evidence to prioritize process improvement actions.

Intended outcomes:
- Identify recurring delay patterns by process step.
- Detect cycle-time deviations and variability concentration.
- Locate repeat quality-impact signals tied to process behavior.

This view must not attempt to solve:
- Real-time shop-floor intervention workflow (Supervisor responsibility).
- Management KPI rollups or executive summaries (Dashboard responsibility).
- Operation execution actions and write workflows (Execution responsibility).

## 3. Investigation Questions (Business-Oriented)
The IE / Process lens is designed to answer:
- Which operations consistently deviate from planned cycle time?
- Where do delays repeat over time?
- Which process steps show highest variability?
- Which operation patterns correlate with repeat quality issues?
- Which process steps should be prioritized for improvement experiments?

## 4. Business Rule Matrix (MANDATORY)
| Rule | Definition | Trigger Condition | Source of Truth | Frontend Constraint |
|---|---|---|---|---|
| cycle_time | Actual operation cycle duration in minutes | actual_start and actual_end available | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |
| cycle_time_delta | cycle_time minus planned cycle duration | cycle_time and planned cycle available | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |
| delay_count | Count of delayed occurrences for comparable operation history | historical operation set resolved | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |
| delay_frequency | delay_count divided by historical comparable operation count | historical operation set size greater than zero | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |
| repeat_flag | Boolean marker for repeated delay pattern | delay_count meets backend-defined repeat threshold | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |
| often_late_flag | Boolean marker for frequently late pattern | delay_frequency meets backend-defined frequency threshold | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |
| high_variance_flag | Boolean marker for high cycle-time variability | historical cycle-time delta dispersion meets backend-defined threshold | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |
| qc_fail_count | Count of historical quality-fail proxy events for operation history | historical operation quality data available | Backend service derivation in Global Operations service layer | Frontend MUST NOT compute |

## 5. Data Derivation & Ownership
Ownership boundaries are locked as follows:
- Repository layer: data access only (query and load operations/history).
- Service layer: all analytical derivation and threshold evaluation.
- API layer: projection transport only, no business-rule derivation.
- Frontend UI layer: rendering, filtering, grouping, and interaction only using backend-provided semantics.

No analytical business rule is allowed in frontend code.

## 6. Lens Behavior & Interaction Rules
IE / Process lens behavior:
- Default lens configuration is IE / Process in Global Operations v2.
- Default ordering is cycle_time_delta descending, then delay_frequency descending.
- Grouping options support investigation by operation_number, work_center, and route_step.
- Row interaction remains drill-down to Operation Detail (read-only context).

Difference versus Supervisor lens:
- Supervisor lens emphasizes immediate incident triage (blocked/delayed now).
- IE / Process lens emphasizes repeatability, variability, and pattern concentration.

No persona auto-detection or enforcement is introduced in Phase 2C.

## 7. Boundaries & Non-Goals (LOCKED)
Non-negotiable exclusions in Phase 2C:
- No execution write actions in Global Operations.
- No dashboard KPI aggregation semantics.
- No role/auth enforcement or route gating.
- No new screen creation; lensing remains within existing Global Operations screen.
- No runtime language-switching behavior introduced by i18n infrastructure.

## 8. Relationship to Other Phases
Phase dependencies and enablement:
- Depends on EC-1 for correct execution-state and Work Order aggregation baseline.
- Builds on Phase 2B read-only Global Operations and Supervisor lens foundation.
- Respects Phase 3 Dashboard ownership by avoiding KPI/dashboard semantics.
- Prepares semantic contracts for future Role/Auth enforcement phase without implementing it.
- Prepares analytical surfaces for future AI advisory phase while preserving read-only control boundaries.

## 9. Completion Summary
Phase 2C closes the Operational Investigation layer by defining a stable, backend-derived IE / Process lens in Global Operations. It enables process-improvement discovery through repeat-pattern and variability semantics, while preserving strict separation from execution control, dashboard decision surfaces, and access-enforcement phases.