# FE Operator Identification for Station Login — Full Specification and Delivery Plan

## History

| Date | Version | Change |
|---|---|---|
| 2026-05-08 | v1.0 | Initial full specification and implementation plan for scan-ID operator identification in station session flow. |

## Status

Planning and specification artifact. No runtime code changes in this document.

Companion execution board:
- `docs/implementation/fe-operator-identification-station-login-execution-board.md`

## Routing
- Selected brain: MOM Brain
- Selected mode: Architecture + Strict
- Hard Mode MOM: v3
- Reason: Feature touches station session, operator identification, execution guards, and frontend execution workflow.

---

## 1. Feature Summary

Implement a production-ready operator identification flow for station login, replacing the current SHELL-only screen with backend-connected behavior.

Feature intent:
- Operator (or supervisor) opens a station session.
- Operator badge/ID is scanned or entered.
- Backend validates and persists identified operator for the active station session.
- Frontend displays backend-derived identified operator and readiness status.
- Execution commands remain backend-guarded and session-owned.

---

## 2. Current Source Status (As-Is)

### Frontend
- Route exists for operator identification: `frontend/src/app/routes.tsx`
- Page exists but is SHELL-only and all actions are disabled: `frontend/src/app/pages/OperatorIdentification.tsx`
- Screen status marks page as SHELL/NONE data source: `frontend/src/app/screenStatus.ts`
- Station Execution currently supports open/close session only: `frontend/src/app/pages/StationExecution.tsx`
- Frontend station API lacks identify-operator client method: `frontend/src/app/api/stationApi.ts`

### Backend
- API route exists for identify operator:
  - `POST /api/v1/station/sessions/{session_id}/identify-operator`
  - Source: `backend/app/api/v1/station_sessions.py`
- Request schema exists:
  - `IdentifyOperatorRequest { operator_user_id: string }`
  - Source: `backend/app/schemas/station_session.py`
- Service logic exists and enforces scope/session/eligibility guards:
  - `identify_operator_at_station(...)`
  - Source: `backend/app/services/station_session_service.py`

Conclusion:
- Backend capability exists.
- Frontend route exists.
- Missing function is frontend integration + UX flow + test coverage.

---

## 3. Design Evidence Extract (Hard Mode MOM v3)

### Source docs read
- `docs/design/INDEX.md`
- `docs/design/AUTHORITATIVE_FILE_MAP.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/02_domain/execution/station-execution-state-matrix-v4.md`
- `docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md`
- `docs/design/02_domain/execution/domain-contracts-execution.md`
- `docs/ai-skills/stitch-design-md-ui-ux/SKILL.md`
- `docs/design/DESIGN.md`
- `docs/audit/frontend-source-alignment-snapshot.md`

### Commands/actions found
- `open_station_session`
- `identify_operator`
- `close_station_session`
- Session-gated execution commands (start/pause/resume/report/downtime/complete)

### Events found
- `station_session_opened`
- `operator_identified_at_station`
- `station_session_closed`
- Execution runtime events unaffected by this FE slice

### States found
- Station session: active/open vs closed
- Execution runtime states: planned/in_progress/paused/blocked/completed/aborted
- Closure status: open/closed

### Invariants found
- Active execution mutation requires valid station session context
- Frontend is never source of execution or authorization truth
- Closed records reject execution writes except authorized reopen
- Tenant/scope checks are backend-enforced

### Explicit exclusions
- No backend execution state-machine changes
- No IAM model redesign
- No equipment binding feature implementation in this slice
- No claim retirement in this slice

---

## 4. Auto-generated Event Map (for this slice)

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| Identify operator in station session | `STATION_SESSION.OPERATOR_IDENTIFIED` | security_event/audit event (current implementation path) | `session_id`, `station_id`, `operator_user_id`, actor identity | station session snapshot updates operator assignment | `backend/app/services/station_session_service.py` |
| Open session (existing behavior) | `STATION_SESSION.OPENED` | security_event/audit event | station/session/operator fields | queue/session context readable | `backend/app/services/station_session_service.py` |
| Close session (existing behavior) | `STATION_SESSION.CLOSED` | security_event/audit event | status/closed_at fields | queue/session context readable | `backend/app/services/station_session_service.py` |

Note: This slice does not add new event types.

---

## 5. Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| Frontend sends intent only | authorization/execution truth boundary | FE architecture + backend route/service guards | no | yes | `docs/governance/CODING_RULES.md` |
| Identify requires valid open session | session | backend service guard | no | yes | `backend/app/services/station_session_service.py` |
| Identify requires station scope eligibility | scope/operator | backend service guard | no | yes | `backend/app/services/station_session_service.py` |
| Station execution write requires valid session context | state_machine/session | backend operation service guards | no | regression | `docs/design/02_domain/execution/station-execution-state-matrix-v4.md` |
| i18n no hardcoded UI strings | ui governance | frontend lint gate | no | yes | `docs/governance/CODING_RULES.md` |

---

## 6. Auto-generated State Transition Map (State-aware feature path)

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| station_session | open + operator null/other | identify_operator | yes (if scope/eligibility valid) | `STATION_SESSION.OPERATOR_IDENTIFIED` | open + operator assigned | yes | `backend/app/services/station_session_service.py` |
| station_session | closed | identify_operator | no | none | unchanged | yes | `backend/app/services/station_session_service.py` |
| station_session | not found | identify_operator | no | none | unchanged | yes | `backend/app/api/v1/station_sessions.py` |
| execution command readiness (frontend render) | open session + owner mine | render action affordance | yes | none_required | UI can present ready state only from backend-derived context | yes | `frontend/src/app/pages/StationExecution.tsx` |

---

## 7. Functional Specification

### 7.1 User stories
1. As an operator, I can identify myself at the current station session by scanning or entering my operator ID.
2. As a supervisor, I can identify an eligible operator for the active station session.
3. As an operator, I can see whether my identification is accepted or rejected by backend truth.
4. As a user, I can navigate from station execution to operator identification and back without losing station context.

### 7.2 In-scope behavior
- Load current session context for station (or accept existing session id from navigation state/query).
- Accept badge/operator input.
- Submit identify request to backend endpoint.
- Reflect backend response with identified operator id and status.
- Show actionable error feedback mapped from backend reject families.
- Keep explicit statement that backend decides authorization/truth.

### 7.3 Out-of-scope behavior
- Opening station session automatically in this screen when none exists (can deep-link to station execution open-session control).
- Equipment-binding implementation.
- Client-side operator authorization decisions.
- Any execution command mutation from this screen.

### 7.4 UX and interaction contract
- Screen phase changes from SHELL to PARTIAL.
- Primary input: operator badge ID (string).
- Primary action: identify operator.
- Secondary action: return to station execution.
- Show session context block:
  - station id
  - session id
  - current identified operator (if any)
  - status badge (pending/verified/error, UI-level only)
- Show backend-only truth notice (no local fake validation outcomes).

### 7.5 Error handling contract (frontend mapping)
Map backend HTTP + detail codes/messages:
- 404 -> session not found
- 403 -> station out of scope / forbidden
- 400 -> invalid input, closed session, operator not eligible
- 401 -> auth expired (existing global handler)
- 409 (if surfaced in future) -> conflict state

Guideline:
- Show exact backend detail string where safe and understandable.
- Preserve i18n keys for generic fallbacks.

### 7.6 Data contract
Request:
- endpoint: `/api/v1/station/sessions/{session_id}/identify-operator`
- method: POST
- body: `{ operator_user_id: string }`

Response:
- station session object with updated `operator_user_id` and unchanged session identity fields.

### 7.7 Navigation and route accessibility gate
- Route remains `/operator-identification` in `frontend/src/app/routes.tsx`.
- Route remains under authenticated layout.
- Persona allowlist remains explicit in `frontend/src/app/persona/personaLanding.ts`.
- Navigation group remains Core Operations in `frontend/src/app/navigation/navigationGroups.ts`.
- `screenStatus` must be updated to PARTIAL + BACKEND_API.
- Direct URL route smoke must pass.

### 7.8 Accessibility and industrial UX
- Input and submit control must be touch-friendly (min 44-48px).
- Keyboard enter submits identify action.
- Loading and error states announced with semantic roles.
- Status not color-only; always include label text.

### 7.9 i18n requirements
- No hardcoded user-facing text in TSX.
- Add all new keys to both registries:
  - `frontend/src/app/i18n/registry/en.ts`
  - `frontend/src/app/i18n/registry/ja.ts`
- Run i18n lint gates.

---

## 8. Non-functional Requirements

- Must not change backend behavior or contracts.
- Must not weaken session guard model.
- Must keep frontend build/lint green.
- Must pass route accessibility gate.
- Must include at least one FE integration test and one E2E path for identify success/failure.

---

## 9. Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| OID-FE-001 | Load with active session | happy_path | valid auth + station context + open session | open page | session summary renders | none_required | FE uses backend-derived session context | FE |
| OID-FE-002 | Identify success | happy_path | open session + eligible operator id | submit identify | UI shows verified/updated operator | backend event implicit via service | frontend does not derive result locally | FE+BE |
| OID-FE-003 | Session not found | invalid_input | stale session id | submit identify | 404 error shown | none_required | no fake success state | FE |
| OID-FE-004 | Out of scope | missing_permission | user lacks station scope | submit identify | 403 error shown | none_required | backend authz truth preserved | FE+BE |
| OID-FE-005 | Ineligible operator | invalid_input | operator not active for station | submit identify | 400 error shown | none_required | backend eligibility truth preserved | FE+BE |
| OID-FE-006 | Closed session | invalid_state | session closed | submit identify | reject shown | none_required | session mutability invariant preserved | FE+BE |
| OID-FE-007 | i18n parity | regression | new keys added | run lint:i18n:registry | pass | none_required | no hardcoded strings | FE |
| OID-FE-008 | Route accessibility | regression | route registration + persona + status map | run route checks + direct URL | pass | none_required | route gate preserved | FE |
| OID-E2E-001 | End-to-end identify happy path | e2e | authenticated operator + open session | navigate + identify | operator reflected in UI and station context | optional backend assertion via API response | backend truth only | FE E2E |

---

## 10. Implementation Plan (Phased)

## Phase 0 — Contract and UX baseline (small)
Deliverables:
- Confirm backend request/response shape in FE types.
- Finalize i18n key list and error mapping table.

Files expected:
- `frontend/src/app/api/stationApi.ts`
- `frontend/src/app/i18n/registry/en.ts`
- `frontend/src/app/i18n/registry/ja.ts`

Exit criteria:
- Types compile.
- i18n keys mirrored.

## Phase 1 — API client and page activation
Deliverables:
- Add `identifyOperator(sessionId, operatorUserId)` to station API client.
- Convert operator identification page from SHELL to PARTIAL backend-connected form.
- Render loading/error/success states.

Files expected:
- `frontend/src/app/api/stationApi.ts`
- `frontend/src/app/pages/OperatorIdentification.tsx`
- optional shared helper in `frontend/src/app/api/*` if needed

Exit criteria:
- Manual identify flow works against backend.
- No hardcoded strings.

## Phase 2 — Route and flow integration
Deliverables:
- Connect station execution session block to operator identification route.
- Pass station/session context through URL params or navigation state.
- Add/back link behavior.

Files expected:
- `frontend/src/app/pages/StationExecution.tsx`
- `frontend/src/app/routes.tsx` (only if route params are changed; prefer no route shape change)

Exit criteria:
- Operator can move from station execution to identify flow and back.
- Context remains stable.

## Phase 3 — Governance and status alignment
Deliverables:
- Update screen status from SHELL to PARTIAL/BACKEND_API.
- Verify persona allowlist and nav grouping stay consistent.

Files expected:
- `frontend/src/app/screenStatus.ts`
- `frontend/src/app/persona/personaLanding.ts` (only if necessary)
- `frontend/src/app/navigation/navigationGroups.ts` (only if necessary)

Exit criteria:
- Route accessibility gate passes fully.

## Phase 4 — Test and verification hardening
Deliverables:
- Add focused frontend test(s) for page behavior.
- Add E2E scenario for identify operator success and one reject case.
- Run FE verification gates.

Files expected:
- `frontend/e2e/*` new spec for station/operator identification
- Optional component/page test file under frontend test setup

Verification commands:
- `cd frontend && npm run build`
- `cd frontend && npm run lint`
- `cd frontend && npm run lint:i18n`
- `cd frontend && npm run lint:i18n:registry`
- `cd frontend && npm run check:routes`
- targeted e2e command as configured

Exit criteria:
- All relevant checks pass.
- Feature is ready for PR review.

---

## 11. Risks and Mitigations

1. Risk: Session context missing when opening operator page directly.
- Mitigation: support station_id query param and resolve current session by station; fail gracefully with action hint.

2. Risk: Confusion between authenticated user and identified operator.
- Mitigation: explicit UI labels and backend-truth notice; do not auto-authorize from frontend state.

3. Risk: i18n regressions from new strings.
- Mitigation: add keys in both registries in same commit and run registry parity lint.

4. Risk: Route/persona drift.
- Mitigation: run route smoke checks and direct URL validation.

---

## 12. Definition of Done

Feature is done when all are true:
1. Operator identification page performs real backend identify call.
2. Session and operator state shown are backend-derived.
3. Station execution can navigate into identification flow with context.
4. Screen status is PARTIAL and no longer SHELL.
5. FE lint/build/i18n/route checks pass.
6. Test matrix minimum coverage is implemented.
7. No backend truth, authorization truth, or execution state is derived by frontend.

---

## 13. Verdict Before Coding (Hard Mode MOM v3)

ALLOW_IMPLEMENTATION

Reason:
- Authoritative execution and governance docs provide explicit behavior contracts.
- Backend endpoint and service already exist, reducing risk to frontend integration scope.
- Invariant and test strategy are defined.
- Scope is narrow and does not require contract-breaking backend changes.

---

## 14. Comprehensive Delivery Plan (Execution-Ready)

This section converts the phased plan into an operational delivery blueprint with clear ownership, sequencing, checkpoints, and release control.

### 14.1 Workstream structure

| Workstream | Scope | Primary Agent/Owner | Supporting |
|---|---|---|---|
| WS-A Contract Baseline | Validate FE/BE API contract and error-family mapping | Execution + Frontend | Tester |
| WS-B UX/Screen Implementation | Activate operator identification route from SHELL to PARTIAL | Frontend | Execution |
| WS-C Station Flow Integration | Connect station execution session panel to operator identify flow | Frontend | Execution |
| WS-D Governance and Route Safety | screenStatus/persona/nav/route-access gate alignment | Frontend | PO-SA |
| WS-E Verification and Regression | Unit/integration/E2E plus route/i18n checks | Tester | Frontend + Execution |
| WS-F Release and Adoption | rollout guardrails, fallback path, and telemetry checks | PO-SA | Frontend + Execution + Tester |

### 14.2 Milestone plan

| Milestone | Target Outcome | Entry Criteria | Exit Criteria |
|---|---|---|---|
| M1 Contract Lock | API and errors are unambiguous for FE coding | Current endpoint verified in backend | Contract table approved, no unknown fields/codes |
| M2 Feature Activation | OperatorIdentification page is backend-connected | M1 done | Identify succeeds/fails correctly with clear UX states |
| M3 Station Journey Complete | StationExecution -> Identify -> StationExecution journey works | M2 done | Context preserved, no navigation dead-end |
| M4 Quality Gate Pass | Tests and governance gates pass | M3 done | build/lint/i18n/routes/tests green |
| M5 Controlled Release | Feature enabled with rollback-ready posture | M4 done | Go/no-go checklist approved |

### 14.3 Suggested implementation schedule

| Day | Focus | Deliverable |
|---|---|---|
| Day 1 | WS-A | Finalized API + reject-code mapping table |
| Day 2-3 | WS-B | Functional OperatorIdentification screen |
| Day 4 | WS-C | StationExecution integration and context link |
| Day 5 | WS-D + WS-E | status/governance sync + tests + route gates |
| Day 6 | WS-F | release readiness and rollback verification |

Note: If environment or E2E setup is unstable, extend WS-E by 1-2 days before release.

---

## 15. Detailed Backlog and Task Breakdown

### 15.1 Epic and story map

Epic: Station Session Operator Identification (Scan-ID Login)

Stories:
1. FE-STN-OPID-01: Add identify operator API client method.
2. FE-STN-OPID-02: Implement active OperatorIdentification page behavior.
3. FE-STN-OPID-03: Integrate station operation flow navigation/context.
4. FE-STN-OPID-04: Update status/governance artifacts.
5. FE-STN-OPID-05: Add regression tests and E2E coverage.
6. FE-STN-OPID-06: Release checklist and rollback rehearsal.

### 15.2 Task checklist by story

#### FE-STN-OPID-01
- Add `identifyOperator(sessionId, operatorUserId)` in `frontend/src/app/api/stationApi.ts`.
- Type request/response from existing `StationSessionItem` contract.
- Ensure error propagation preserves backend `detail`.

#### FE-STN-OPID-02
- Replace disabled shell controls with active input + submit action.
- Add loading/success/error rendering states.
- Keep backend-truth disclaimer visible.
- Support keyboard-enter submission.

#### FE-STN-OPID-03
- Add navigation entry point from `frontend/src/app/pages/StationExecution.tsx`.
- Pass and consume station/session context (query or nav-state).
- Add reliable return path to station execution.

#### FE-STN-OPID-04
- Update `frontend/src/app/screenStatus.ts` route phase to PARTIAL.
- Confirm persona access remains intentional in `frontend/src/app/persona/personaLanding.ts`.
- Validate nav group remains coherent in `frontend/src/app/navigation/navigationGroups.ts`.

#### FE-STN-OPID-05
- Add focused FE behavior tests for success and reject.
- Add E2E for happy path and one error path.
- Run FE verification commands and capture output in PR notes.

#### FE-STN-OPID-06
- Prepare go/no-go checklist.
- Verify fallback user path when identify fails.
- Confirm rollback path (revert FE route behavior to shell-safe mode if required).

---

## 16. Acceptance Criteria (Expanded)

### 16.1 Functional acceptance
1. Operator can identify via manual ID entry or scanner keyboard input.
2. Backend response immediately updates shown operator context.
3. Rejects are explicit and non-ambiguous by error family.
4. No execution command state is inferred locally from identification attempt.

### 16.2 UX acceptance
1. Touch-safe controls on tablet viewport.
2. Clear primary action hierarchy (Identify vs Back).
3. Status readability without color dependency.
4. Empty/no-session state guides user to valid next action.

### 16.3 Governance acceptance
1. `screenStatus` reflects true maturity phase.
2. Persona routing behavior remains explicit and tested.
3. i18n parity remains exact between EN/JA registries.

### 16.4 Technical acceptance
1. No backend API contract changes required.
2. No new lint or type errors introduced.
3. E2E scenario executes in CI/dev environment.

---

## 17. Dependency and Blocker Matrix

| Dependency | Type | Owner | Status | Blocker if missing |
|---|---|---|---|---|
| `identify-operator` endpoint | Backend contract | Execution | AVAILABLE | yes |
| Session context availability in FE flow | Frontend integration | Frontend | PARTIAL | yes |
| i18n key parity tooling | FE governance | Frontend | AVAILABLE | medium |
| Route smoke checks (`check:routes`) | FE governance | Frontend | AVAILABLE | medium |
| Playwright/e2e environment stability | Test infra | Tester | PARTIAL | yes for release |

Blocker policy:
- Any contract blocker halts coding of dependent tasks.
- Any E2E infrastructure blocker allows merge only if risk is accepted and ticketed as release-blocking follow-up.

---

## 18. Validation and Gate Plan

### 18.1 Mandatory gates before merge
1. `cd frontend && npm run build`
2. `cd frontend && npm run lint`
3. `cd frontend && npm run lint:i18n`
4. `cd frontend && npm run lint:i18n:registry`
5. `cd frontend && npm run check:routes`
6. Feature tests (unit/integration)
7. New E2E scenario(s)

### 18.2 Optional but recommended
1. Backend targeted station-session tests for confidence:
   - `backend/tests/test_station_session_lifecycle.py`
   - `backend/tests/test_station_session_command_guard_enforcement.py`
2. Manual tablet viewport smoke (landscape/portrait)

### 18.3 Evidence artifact checklist
- screenshots of success and rejection states
- command outputs for all mandatory gates
- route accessibility checklist in PR description
- known limitation note (if any)

---

## 19. Rollout, Monitoring, and Rollback

### 19.1 Rollout strategy
- Release as additive change to existing station flow (no route removal).
- Keep StationExecution open/close path stable while adding identify flow.
- Do not hide existing controls until identify flow is verified in target environment.

### 19.2 Monitoring indicators
- FE error rate for identify requests (4xx/5xx trend)
- frequency of 400 eligibility failures
- frequency of 404 stale session failures
- user retry rate per station (proxy for UX friction)

### 19.3 Rollback strategy
- Revert FE changes in OperatorIdentification and StationExecution linking.
- Preserve backend behavior (no rollback needed for backend in this slice).
- Restore page phase to SHELL if emergency fallback is required.

---

## 20. Communication Plan

### 20.1 Stakeholder updates
- Daily short update during implementation window:
  - completed
  - next
  - blockers

### 20.2 Review packet
- spec link
- diff summary
- test evidence
- residual risk statement

### 20.3 Handover note for operations/supervisors
- how to access identify screen
- expected behavior on errors
- where to report scope/eligibility misconfigurations

---

## 21. Post-Release Follow-up Backlog

1. Add dedicated scanner-device compatibility checklist (USB HID scanners, locale keyboards).
2. Extend flow for equipment binding once policy requires it.
3. Add operator lookup helper UX (if approved) without changing backend truth model.
4. Consider consolidating station-session shell pages into one connected operator cockpit route after this slice stabilizes.

