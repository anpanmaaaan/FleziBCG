# Station Workflow Redesign Contract v1

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-10 | v1.0 | Initial workflow redesign contract for Station operator/supervisor journey, truth boundaries, and implementation slicing. |

## Status
Draft for implementation slicing

## Scope
- Define a canonical end-to-end Station workflow contract across operator entry, session context, queue/cockpit, execution actions, downtime/quantity visibility, completion, supervisor close/reopen, and end-session.
- Define screen and component contracts for a cohesive Station flow with backend truth preserved.
- Define command/action responsibilities and error/recovery behavior for existing command families.
- Define persona boundaries and frontend/backend truth boundaries for Station flow.
- Define responsive, touch, accessibility, and future E2E verification contract.
- Propose implementation slices only (no source/API changes in this document).

## Non-Goals
- No frontend implementation changes.
- No backend/service/API contract changes.
- No test implementation.
- No route changes.
- No claim/history migration design beyond workflow implications.
- No force-abort redesign.
- No quality domain expansion implementation.
- No material readiness backend implementation.
- No ERP/backflush/APS/AI/Digital Twin/compliance implementation changes.
- No global navigation redesign.

## Baseline Evidence
### Design and governance sources read
- docs/design/00_platform/product-business-truth-overview.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md
- docs/governance/SOURCE_STRUCTURE.md
- docs/design/INDEX.md
- docs/design/AUTHORITATIVE_FILE_MAP.md
- docs/design/02_domain/execution/business-truth-station-execution-v4.md
- docs/design/02_domain/execution/station-session-ownership-contract.md
- docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md
- docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md
- docs/design/02_domain/execution/station-execution-state-matrix-v4.md
- docs/design/02_domain/execution/station-execution-exception-and-approval-matrix-v4.md
- docs/design/02_domain/execution/domain-contracts-execution.md
- docs/design/07_ui/station-execution-screen-pack-v4.md
- docs/design/07_ui/station-execution-screen-pack-v3.1.md
- docs/design/07_ui/station-execution-component-map-v1.md
- docs/design/07_ui/station-execution-responsive-contract-v1.md
- docs/audit/frontend-source-alignment-snapshot.md

### Source evidence read (current behavior)
- frontend/src/app/pages/StationSession.tsx
- frontend/src/app/pages/OperatorIdentification.tsx
- frontend/src/app/pages/EquipmentBinding.tsx
- frontend/src/app/pages/StationExecution.tsx
- frontend/src/app/pages/OperationExecutionDetail.tsx
- frontend/src/app/components/station-execution/*
- frontend/src/app/api/stationApi.ts
- frontend/src/app/api/operationApi.ts
- frontend/src/app/routes.tsx
- frontend/src/app/persona/personaLanding.ts
- frontend/src/app/screenStatus.ts
- backend/app/api/v1/station_sessions.py
- backend/app/api/v1/operations.py
- backend/app/services/station_session_service.py
- backend/app/services/operation_service.py
- backend/app/services/station_queue_service.py

### Hard Mode MOM v3 pre-implementation evidence extract
| Evidence type | Summary |
|---|---|
| Commands/actions found | open/identify/bind/close station session; start/pause/resume/report/start downtime/end downtime/complete/close/reopen operation. |
| Events found | Station session lifecycle events plus execution events (started/paused/resumed/reported/downtime/completed/closed/reopened). |
| States found | Runtime: PLANNED, IN_PROGRESS, PAUSED, BLOCKED, COMPLETED, ABORTED. Closure: OPEN, CLOSED. |
| Critical invariants found | Closed records block execution writes; valid open station session required for execution mutation; backend derives allowed actions; append-only event truth. |
| Explicit exclusions | Quality/material/approval expansion beyond current execution baseline remains deferred for this contract. |

## Product Principles
- Backend is source of execution, authorization, and session truth.
- Frontend sends intents, renders backend-derived state, and provides recovery guidance.
- Station execution ownership is session-based (not claim as target truth).
- Allowed actions are backend-derived; frontend must not infer legality from status text alone.
- Execution facts are append-only events; projections are read models.
- Persona in UI is navigation/presentation; permission is server-side.

## Current Problems
- Station journey is split across separate surfaces with weak handoff.
- Operator entry to active cockpit is not cohesive.
- Operation detail tabs are partially placeholder-backed.
- Error UX is now normalized but workflow-level recovery path is still fragmented.
- Some entry endpoint failures still return free-text details rather than stable codes.
- No explicit backend equipment-mismatch code is currently observed in station session entry APIs.
- Full Playwright journey for Station workflow is not yet defined as executable suite.

## Target Workflow Overview
Canonical station workflow stages:
- STX-000 Station Entry
- STX-001 Station Session
- STX-002 Operator Identification
- STX-003 Equipment Binding / Context Confirmation
- STX-004 Queue / Cockpit
- STX-005 Active Operation
- STX-006 Downtime / Quantity / Quality / Material Visibility
- STX-007 Completion
- STX-008 Supervisor Review / Close / Reopen
- STX-009 End Session

Design decision:
- Operator flow should run in one consolidated Station Shell with stage panels and deterministic stage progression/handoff.
- Supervisor review remains separate surface(s) linked from cockpit/detail and not embedded as primary operator action path.

## Station Workflow Stages
| Stage | Name | Required | Entry condition | Exit condition | Notes |
|---|---|---:|---|---|---|
| STX-000 | Station Entry | Yes | User enters /station with station context or selected station | Station context confirmed | Missing stationId must resolve before progression. |
| STX-001 | Station Session | Yes | Station resolved | Active OPEN session exists for station | Open session is backend command. |
| STX-002 | Operator Identification | Yes | Session exists | Session has identified operator usable for command guards | Auth user and identified operator remain distinct concepts. |
| STX-003 | Equipment Binding / Context Confirmation | Conditional | Session exists; station policy may require equipment | Required equipment bound (if policy-required) | Optional for fixed/single-resource stations. |
| STX-004 | Queue / Cockpit | Yes | Session/operator/equipment prerequisites satisfied | Operation selected and cockpit active | Queue ownership hints are backend-derived. |
| STX-005 | Active Operation | Yes | Operation selected and executable | Operation reaches terminal runtime path for current cycle | Actions are backend-allowed and guard-protected. |
| STX-006 | Downtime/Quantity/Quality/Material Visibility | Yes | Active operation context | Operator can continue or escalate with clear blockers | Quality/material visibility is required; full domain mutation may remain out of current scope. |
| STX-007 | Completion | Yes | Runtime status IN_PROGRESS with completion preconditions met | Execution completed | Completion remains backend-validated. |
| STX-008 | Supervisor Review / Close / Reopen | Conditional | Completed or closed operation context with SUP role | Close/reopen decision persisted | Not primary operator action path. |
| STX-009 | End Session | Yes | Work complete or handoff decision reached | Station session closed | Must fail safely if active execution would be orphaned. |

## Operator Journey
1. Enter Station Shell with station context.
2. Open or resume station session.
3. Identify operator.
4. Bind equipment when required by station policy.
5. Enter queue and pick operation.
6. Operate from cockpit using backend-allowed actions only.
7. Handle downtime/report quantity/observe blockers.
8. Complete operation when preconditions pass.
9. End station session or continue with next queue item.

Operator constraints:
- No direct authority to close/reopen unless explicitly allowed by backend role/policy.
- No frontend-derived ownership or legality decisions.

## Supervisor Journey
1. Access supervisory operation surface from operations list/detail/cockpit context.
2. Review operation status, closure state, timeline/audit context, and active blockers.
3. Execute close/reopen commands where SUP policy and backend constraints permit.
4. Support escalation visibility: quality hold, material readiness blockers, station conflicts.
5. Return control to operator flow without taking over primary operator cockpit interactions.

Supervisor boundary:
- Supervisor actions are available as explicit supervisory functions, not as default operator primary CTAs.

## Screen Contract
### Recommended model
Consolidated Station Shell with stage panels for operator flow, plus separate supervisor surfaces.

### Operator shell layout contract
- Context Bar: station, session state, operator, equipment, operation identity.
- Stage Panel Rail: STX-000..STX-009 with current stage and prerequisites.
- Main Work Area: queue/cockpit/action zones by current stage.
- Recovery Banner Area: normalized error + guided next step.
- Support Links Area: supervisor review, operation detail, timeline (role-aware).

### Surface responsibilities
| Surface | Purpose | Data source status |
|---|---|---|
| Station Shell (operator) | Entry -> session -> identify -> bind -> queue -> execute -> complete -> end session | Backend API plus known placeholders where explicitly labeled |
| Operation detail/timeline | Deep read context and audit visibility | Partial today; must remain explicitly labeled when placeholder-backed |
| Supervisory operation surface | Close/reopen/support escalation | Backend-governed actions, role-gated |

## Component Contract
Cockpit zones are mandatory in STX-004/STX-005:
- Context Bar
- Session/Operator/Equipment Card
- Active Operation Hero
- Queue/Next Work
- Allowed Action Zone
- Downtime/Quantity Panels
- Error/Recovery Banner
- Quality/Material/Blocker Visibility
- End Session/Handoff Area

Component behavior rules:
- Action buttons render from backend allowed_actions plus ownership/session context gates already provided by backend projections.
- Stage navigation cannot skip required prerequisites unless backend explicitly reports satisfied context.
- Placeholder data blocks must carry PARTIAL/SHELL labeling.

## Command / Action Contract
| UI Action | Backend endpoint/command intent | Primary persona | Backend guard truth | Event intent |
|---|---|---|---|---|
| Open session | POST /v1/station/sessions | OPR | station scope + no active open session | STATION_SESSION.OPENED |
| Identify operator | POST /v1/station/sessions/{id}/identify-operator | OPR | session exists/open + station scope + operator eligibility | STATION_SESSION.OPERATOR_IDENTIFIED |
| Bind equipment | POST /v1/station/sessions/{id}/bind-equipment | OPR | session exists/open + station scope + equipment validation | STATION_SESSION.EQUIPMENT_BOUND |
| Close session | POST /v1/station/sessions/{id}/close | OPR | session exists/open + no active execution orphaning | STATION_SESSION.CLOSED |
| Start | POST /v1/operations/{id}/start | OPR | open session guard + state/closure/invariant checks | OP_STARTED |
| Pause | POST /v1/operations/{id}/pause | OPR | open session guard + state checks | EXECUTION_PAUSED |
| Resume | POST /v1/operations/{id}/resume | OPR | open session guard + no open downtime + hold/station checks | EXECUTION_RESUMED |
| Report quantity | POST /v1/operations/{id}/report-quantity | OPR | open session guard + IN_PROGRESS + quantity invariant checks | QTY_REPORTED |
| Start downtime | POST /v1/operations/{id}/start-downtime | OPR | open session guard + state + reason validity | DOWNTIME_STARTED |
| End downtime | POST /v1/operations/{id}/end-downtime | OPR | open session guard + open-downtime invariant | DOWNTIME_ENDED |
| Complete | POST /v1/operations/{id}/complete | OPR | open session guard + IN_PROGRESS + no hold/open downtime | OP_COMPLETED |
| Close operation | POST /v1/operations/{id}/close | SUP | role SUP + completion/closure guards | OPERATION_CLOSED_AT_STATION |
| Reopen operation | POST /v1/operations/{id}/reopen | SUP | role SUP + closure + reason guards | OPERATION_REOPENED |

## Error / Recovery Contract
Baseline: use normalized Station error mapper for operator-facing recovery behavior.

| Condition | Primary error family/code | UI behavior | Recovery guidance |
|---|---|---|---|
| Missing station id | UI context error | Blocking warning panel before session actions | Prompt to open from Station context route with stationId |
| No active session | STATION_SESSION_REQUIRED | Warning banner + disable execution actions | Open Station Session |
| Session closed | STATION_SESSION_CLOSED | Warning banner | Open new session |
| Operator mismatch | STATION_SESSION_OPERATOR_MISMATCH | Warning banner + status marker | Re-identify operator or switch session |
| Station mismatch | STATION_SESSION_STATION_MISMATCH | Warning banner | Return to correct station context |
| Equipment missing | EQUIPMENT_REQUIRED (or fallback) | Warning banner + equipment CTA | Bind required equipment |
| Equipment mismatch | EQUIPMENT_MISMATCH (or fallback) | Warning banner + context card emphasis | Select/bind equipment matching station/session policy |
| Active execution prevents close session | STATION_SESSION_ACTIVE_EXECUTION | Warning banner and keep session open | Complete/pause/end active execution first |
| Permission denied | AUTH_SCOPE_FAIL / 403 | Danger banner | Contact supervisor/admin; verify scope |
| Operation closed | STATE_CLOSED_RECORD / OPERATION_CLOSED | Danger banner and disable runtime actions | Use supervisor reopen flow if permitted |
| Quality hold | STATE_QC_HOLD_ACTIVE / OPERATION_QUALITY_HOLD_OPEN | Danger banner + blocker panel | Resolve hold through quality/supervisor path |
| Material not ready | material readiness blocker family (future stable code needed) | Warning/danger blocker panel | Route to material readiness workflow/escalation |
| Unknown/server failure | UNKNOWN fallback | Generic warning panel + retry action | Refresh/retry/contact supervisor |

Recovery UX rules:
- Show title + message + recovery action hint.
- Never expose raw backend stack/detail as primary user copy.
- Keep error state local to current stage panel and preserve context for retry.

## Persona / Permission Boundary
- OPR: station session lifecycle (open/identify/bind/close), queue selection, execution mutation commands.
- SUP: close/reopen operation, supervisory review/escalation support.
- QC/QAL: quality domain actions remain quality-owned and should be linked, not reimplemented in operator cockpit.
- ADM/OTS: not default shopfloor actors; any intervention is governed and auditable.

Boundary rule:
- Persona/menu visibility does not grant backend authority.

## Frontend / Backend Truth Boundary
Non-negotiable contract:
- Backend decides session validity.
- Backend decides command availability.
- Backend decides allowed actions.
- Backend owns state/event truth.
- Frontend shows guidance and sends intents only.
- Frontend must not derive command legality locally.

Practical FE rules:
- No local state machine that can authorize prohibited command paths.
- No frontend-only ownership source.
- No synthetic completion/quality/material truth in cockpit.

## Data Requirements
Required operator shell payload groups:
- Station context: station_id, scope context.
- Session context: session_id, status, operator_user_id, equipment_id.
- Queue context: operation id/number/name, status, downtime_open, ownership summary.
- Operation detail context: runtime status, closure_status, quantities, allowed_actions, timers, quality_hold_open.
- Downtime reason master data.
- Error code/message shape stable enough for mapper-based guidance.

Data quality constraints:
- Use backend canonical IDs for all command invocations.
- Avoid stale operation overlays after command mutation; refresh operation + queue.

## State / Event Visibility
UI-visible states (minimum):
- Runtime status
- Closure status
- Downtime open
- Session ownership summary
- Allowed actions
- Quality hold signal

Event visibility contract:
- Cockpit should show recent action outcomes and link to operation timeline surface.
- Timeline deep detail can remain separate, but shell must expose a deterministic path to it.

## Quality / Material / Downtime / Blocker Boundary
- Downtime is execution-native and must be first-class in cockpit.
- Quality hold is a blocker signal in execution flow; full quality disposition remains in quality domain surfaces.
- Material readiness is a blocker visibility contract in Station shell; backend material truth remains authoritative.
- Blockers must appear in one consolidated Blocker Visibility area with clear next owner (operator/supervisor/quality/material).

## Responsive / Touch UX Contract
- Preserve existing station responsive contract priorities: tablet landscape and portrait first, desktop second.
- Stage controls and primary command buttons must remain touch-safe and large enough for shopfloor interaction.
- Context and blocker indicators must remain visible without requiring deep scrolling in common tablet views.
- Queue filtering and action strips must avoid horizontal overflow failures.

## Accessibility Contract
- Stage rail and zone landmarks must support semantic navigation and screen readers.
- Error and blocker banners must use alert/status semantics.
- Primary command controls require keyboard operability and visible focus.
- Color is not sole status signal; text/icon pairing required.
- Disabled action states should include reason hints where operationally meaningful.

## E2E Test Contract
Positive future scenario (single flow):
1. Open station.
2. Identify operator.
3. Bind equipment.
4. See queue.
5. Select operation.
6. Start.
7. Pause.
8. Resume.
9. Report quantity.
10. Start downtime.
11. End downtime.
12. Complete.
13. End session.

Negative scenarios (must exist):
- Start command without active session.
- Command with closed session.
- Operator mismatch.
- Permission denied.
- Quality hold blocks completion.

Test contract notes:
- Validate backend error code to normalized recovery banner mapping.
- Assert frontend never enables illegal command path after backend reject.
- Assert stage handoff continuity across refresh/navigation.

## Implementation Slicing Proposal
1. Slice A (contract-first shell orchestration)
- Introduce Station Shell stage model and handoff contract in FE architecture docs and route behavior proposal.
- Keep existing pages but define shell host integration points.

2. Slice B (operator entry consolidation)
- Consolidate STX-000 to STX-003 into staged shell panels with shared context store from backend responses.
- Keep existing endpoints and command payload contracts unchanged.

3. Slice C (queue/cockpit cohesion)
- Merge STX-004 to STX-006 under one cockpit flow container with zone layout contract enforcement.
- Preserve allowed_actions and session-ownership behavior from backend.

4. Slice D (completion and end-session hardening)
- Standardize STX-007 and STX-009 transitions with deterministic confirmations and recovery states.

5. Slice E (supervisor surface contract alignment)
- Refine STX-008 links and review context from shell to supervisory surfaces.

6. Slice F (E2E coverage rollout)
- Add full positive/negative Playwright journey per this contract once shell slices are implemented.

## Open Questions
- Should backend entry endpoints standardize all guard failures to stable code enums (including current free-text details) before shell consolidation?
- What is the canonical backend error code for equipment mismatch in station-session entry flow?
- Should station policy for equipment-required be explicit in current-session response to avoid UI ambiguity?
- For STX-009 End Session, should close-session be blocked when queue has PAUSED/BLOCKED operations not owned by active operator?
- Should operation timeline remain separate page or embedded panel once backend timeline API reaches parity?

## Definition of Done
Contract-level done:
- Canonical STX-000..STX-009 workflow model is documented and unambiguous.
- Screen model recommendation is explicit and actionable.
- Cockpit zone contract is explicit and role-safe.
- Supervisor boundary is explicit and not operator-primary.
- Error/recovery matrix covers required conditions.
- Truth boundary explicitly forbids frontend-derived legality.
- E2E positive and negative contracts are defined.
- Slice plan is implementation-ready without API redesign.

Implementation-ready done criteria for next slices:
- No backend/API contract changes required to begin shell consolidation.
- FE stages can be implemented incrementally without breaking current connected command paths.
- Outstanding backend error-code normalization is tracked as dependency gap, not hidden.
