# FE Operator Identification Station Login — Ticketized Execution Board

## History

| Date | Version | Change |
|---|---|---|
| 2026-05-08 | v1.0 | Initial execution board with ticketized stories, dependencies, estimates, and delivery gates. |

## Status — IMPLEMENTED 2026-05-08

All 9 tickets complete. Gates: i18n parity ✅ 1982 keys, route smoke ✅, TypeScript (2 pre-existing unrelated errors only ✅), E2E spec committed ✅.

Execution planning artifact. Use with the companion spec:
- `docs/implementation/fe-operator-identification-station-login-spec-plan.md`

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict + QA
- Hard Mode MOM: v3
- Reason: Feature affects station session/operator execution flow with backend-truth invariants and requires coordinated FE/Execution/Tester delivery.

---

## 1. Delivery Board Summary

Epic:
- EPIC-STN-OPID-01 — Station Session Operator Identification (Scan-ID Login)

Objective:
- Move operator identification from SHELL to PARTIAL backend-connected flow without changing backend truth ownership.

Success metric:
- End-to-end identify flow works from station operation context with passing verification gates and no regression in session-guarded execution paths.

---

## 2. Ticket Board

### 2.1 Ready Queue

| Ticket | Title | Type | Owner | Estimate | Priority | Dependency |
|---|---|---|---|---|---|---|
| STN-OPID-001 | Lock FE/BE contract table | Analysis | Execution + Frontend | 0.5d | P0 | none |
| STN-OPID-002 | Add station API identify client | Frontend | Frontend | 0.5d | P0 | STN-OPID-001 |
| STN-OPID-003 | Activate OperatorIdentification page | Frontend | Frontend | 1.5d | P0 | STN-OPID-002 |
| STN-OPID-004 | Integrate StationExecution navigation/context | Frontend | Frontend | 1.0d | P0 | STN-OPID-003 |
| STN-OPID-005 | Update screen status and route governance | Governance | Frontend | 0.5d | P1 | STN-OPID-004 |
| STN-OPID-006 | Add FE behavior tests | Test | Tester + Frontend | 1.0d | P0 | STN-OPID-004 |
| STN-OPID-007 | Add E2E identify scenarios | Test | Tester | 1.0d | P0 | STN-OPID-004 |
| STN-OPID-008 | Run full FE verification gates | Verification | Tester | 0.5d | P0 | STN-OPID-005, STN-OPID-006, STN-OPID-007 |
| STN-OPID-009 | Release readiness + rollback rehearsal | Release | PO-SA + Tester | 0.5d | P1 | STN-OPID-008 |

### 2.2 In Progress

| Ticket | Title | Owner | Status |
|---|---|---|---|
| none | none | n/a | not started |

### 2.3 Done

| Ticket | Title | Owner | Status |
|---|---|---|---|
| none | none | n/a | not started |

---

## 3. Ticket Details

## STN-OPID-001 — Lock FE/BE Contract Table

Scope:
- Finalize endpoint, payload, and reject-code mapping for FE consumption.

Files:
- `frontend/src/app/api/stationApi.ts`
- `backend/app/api/v1/station_sessions.py`
- `backend/app/schemas/station_session.py`

Acceptance:
1. Endpoint path and method confirmed.
2. Request/response contract validated against live backend source.
3. Error-family mapping approved (400/403/404/401).

Evidence:
- Contract table added/confirmed in companion spec.

---

## STN-OPID-002 — Add Station API Identify Client

Scope:
- Add `identifyOperator(sessionId, operatorUserId)` to station API client.

Files:
- `frontend/src/app/api/stationApi.ts`

Acceptance:
1. Method uses `/v1/station/sessions/{session_id}/identify-operator`.
2. Request body matches backend schema.
3. Response typed as station session item.

Evidence:
- API client diff + compile success.

---

## STN-OPID-003 — Activate OperatorIdentification Page

Scope:
- Replace SHELL-only disabled UI with backend-connected form and states.

Files:
- `frontend/src/app/pages/OperatorIdentification.tsx`
- `frontend/src/app/i18n/registry/en.ts`
- `frontend/src/app/i18n/registry/ja.ts`

Acceptance:
1. Operator ID input and submit action active.
2. Loading, success, and error states are visible and backend-driven.
3. Backend-truth notice remains explicit.
4. No hardcoded user-facing strings.

Evidence:
- UI screenshots for success/reject states.

---

## STN-OPID-004 — Integrate StationExecution Context Flow

Scope:
- Add user journey from station operation area to operator identification and back.

Files:
- `frontend/src/app/pages/StationExecution.tsx`
- optional: `frontend/src/app/routes.tsx` (only if route shape changes, avoid if possible)

Acceptance:
1. Operator can navigate with session/station context preserved.
2. Return path to station execution exists and is stable.
3. No disruption to open/close session controls.

Evidence:
- Manual route smoke recording.

---

## STN-OPID-005 — Governance and Route Safety Sync

Scope:
- Reflect actual maturity in screen status and preserve route/persona/nav integrity.

Files:
- `frontend/src/app/screenStatus.ts`
- optional validation in `frontend/src/app/persona/personaLanding.ts`
- optional validation in `frontend/src/app/navigation/navigationGroups.ts`

Acceptance:
1. `/operator-identification` phase changes to PARTIAL.
2. Data source changes to BACKEND_API.
3. Persona access remains intentional and documented.

Evidence:
- Route accessibility checklist.

---

## STN-OPID-006 — FE Behavior Tests

Scope:
- Add page-level behavior tests for success and reject handling.

Files:
- frontend test file(s) per existing FE test setup

Acceptance:
1. Happy-path identify test passes.
2. Rejection-path test (e.g., 404 or 403) passes.
3. No false local success state when backend rejects.

Evidence:
- Test run output attached.

---

## STN-OPID-007 — E2E Identify Scenarios

Scope:
- Add Playwright scenario for operator identify user flow.

Files:
- `frontend/e2e/` new spec file

Acceptance:
1. E2E happy path passes.
2. E2E reject path passes.
3. Station flow remains usable after identify action.

Evidence:
- Playwright output + screenshots/videos (if configured).

---

## STN-OPID-008 — Verification Gate Run

Scope:
- Execute all required FE gates.

Commands:
1. `cd frontend && npm run build`
2. `cd frontend && npm run lint`
3. `cd frontend && npm run lint:i18n`
4. `cd frontend && npm run lint:i18n:registry`
5. `cd frontend && npm run check:routes`
6. Targeted tests for STN-OPID-006/007

Acceptance:
1. All mandatory gates pass.
2. Any flaky failures are triaged and resolved or ticketed before release.

Evidence:
- Verification summary in PR description.

---

## STN-OPID-009 — Release Readiness and Rollback

Scope:
- Final go/no-go review and fallback validation.

Acceptance:
1. Go/no-go checklist completed.
2. Rollback steps confirmed (FE-only revert path).
3. Known limitations documented.

Evidence:
- Release checklist artifact.

---

## 4. Dependency Graph

```text
STN-OPID-001
  -> STN-OPID-002
     -> STN-OPID-003
        -> STN-OPID-004
           -> STN-OPID-005
           -> STN-OPID-006
           -> STN-OPID-007
                -> STN-OPID-008
                   -> STN-OPID-009
```

Parallelizable after STN-OPID-004:
- STN-OPID-005, STN-OPID-006, STN-OPID-007

---

## 5. Definition of Ready (DoR)

A ticket is ready when:
1. Scope is explicit and single-slice.
2. Input contract and files-in-scope are known.
3. Acceptance criteria are testable.
4. Dependencies are resolved or explicitly blocked.

---

## 6. Definition of Done (DoD)

A ticket is done when:
1. Acceptance criteria all pass.
2. Required tests and gates pass.
3. i18n and route-governance checks pass if touched.
4. Evidence is attached in PR or implementation notes.
5. No backend-truth or auth-truth violations introduced.

---

## 7. Risk Register (Ticketized)

| Risk ID | Risk | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R-01 | Missing session context on direct URL | medium | Context fallback + clear guidance message | Frontend |
| R-02 | Confusion between login user and identified operator | high | Explicit labels + backend-truth notice | Frontend |
| R-03 | i18n key drift EN/JA | medium | i18n registry lint gate | Frontend |
| R-04 | Route/persona drift | high | check:routes + direct URL smoke | Tester |
| R-05 | E2E infra flakiness | medium | stabilize test env before release decision | Tester |

---

## 8. Weekly Reporting Template

Use this format during execution:

```markdown
## STN-OPID Weekly Update
- Completed tickets:
- In-progress tickets:
- Blocked tickets:
- Gate status:
- Risks changed:
- Next 3 tasks:
```

---

## 9. Merge and Release Checklist

1. All P0 tickets complete: STN-OPID-001/002/003/004/006/007/008
2. P1 tickets either complete or explicitly deferred with note
3. Mandatory FE gates pass
4. E2E identify flow evidence attached
5. Rollback procedure documented
6. PR scope contains only intended files

---

## 10. Next-Slice Candidates (Post-Completion)

1. Equipment binding connection in same station session journey.
2. Scanner hardware compatibility matrix and debounce handling.
3. Operator lookup assist UX (if approved) without client-side authority decisions.
4. Consolidation of station shell pages after stability window.
