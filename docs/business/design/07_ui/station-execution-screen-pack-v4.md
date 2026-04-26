# Station Execution Screen Pack

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Reworked UI pack to the approved session-owned execution design. |

Status: Canonical UI pack aligned to the approved next-step Station Execution design.

## 1. Scope

This pack covers discrete-first operator-facing execution surfaces.

## 2. Screen list

### STX-000 Station Session Entry
Purpose:
- open/restore active station session
- identify operator
- bind/select equipment when required

Primary data:
- station context
- session state
- operator lookup result
- equipment choices where relevant

Actions:
- open session
- identify operator
- bind equipment
- enter queue/cockpit

### STX-001 Station Queue
Purpose:
- show queued operations for the active station context
- show current status, occupancy/session context, and priority context
- allow operator to select work where allowed

Primary data:
- queue rows
- operation identity
- runtime status
- closure_status
- active ownership/session summary
- remaining quantity
- recommended-next hint later

Actions:
- navigate to cockpit/detail
- no first-class claim action in target UX

### STX-002 Execution Cockpit
Purpose:
- run the primary execution lifecycle for the selected operation

Primary data:
- operation header
- quantities
- current status
- downtime-open signal
- allowed_actions
- recent activity
- active station session summary
- identified operator
- bound equipment where relevant

Actions:
- start
- pause
- resume
- report production
- start/end downtime
- complete
- close/reopen when visible to authorized supervisory actor

### STX-003 Downtime Dialog
Purpose:
- collect governed downtime reason selection
- capture optional comment when policy requires

### STX-004 Operation Detail
Purpose:
- show deeper operational context, event history, and audit-friendly view
- serve as navigation target from lists/Gantt

## 3. UI principles

- queue, cockpit, and detail must show the same backend-derived truth
- button availability uses backend allowed_actions
- downtime reason options come from backend master data
- FE must not infer execution legality from visible status text alone
- FE must not invent claim ownership locally

## 4. Deferred from this pack

- QC screens embedded in the same flow
- exception/disposition screens
- process/batch execution console
