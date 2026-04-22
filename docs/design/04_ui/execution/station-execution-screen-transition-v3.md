# Station Execution — Screen Transition (Aligned Current Baseline)

## 1. Navigation-level transitions

| From | Trigger | To | Rule |
|---|---|---|---|
| Queue | Select operation row | Cockpit | Keep current queue filter |
| Cockpit | Back to Selection | Full selection mode | Keep current filter |
| Cockpit | Open Quick Queue | Quick Queue popup | Do not change primary mode |
| Quick Queue | Select operation row | Cockpit | Switch operation context; popup may close per current UX |

## 2. Claim-related transitions

### 2.1 Single-active-claim rule
- If operator does not already hold another unreleased claim in same station context, claim may proceed if backend says claimable.
- If operator already holds another unreleased claim in same station context:
  - second claim attempt is rejected
  - FE must not present it as normal claim action

### 2.2 Re-open owned context
Single-active-claim does not block:
- Back to Selection
- Quick Queue opening
- re-selecting the owned operation
- continuing pause / downtime / resume / complete flow on the same owned context

## 3. Execution flow transitions

| Current state | Trigger | Resulting state | Screen expectation |
|---|---|---|---|
| PLANNED | Claim + Start Execution | IN_PROGRESS | Stay in cockpit |
| IN_PROGRESS | Report Qty | IN_PROGRESS | Refresh context, remain in cockpit |
| IN_PROGRESS | Pause | PAUSED | Stay in cockpit |
| IN_PROGRESS | Start Downtime | BLOCKED + downtime_open=true | Stay in cockpit |
| BLOCKED | End Downtime | PAUSED + downtime_open=false | Stay in cockpit, no auto-resume |
| PAUSED | Resume | IN_PROGRESS | Stay in cockpit |
| COMPLETED + OPEN | Close Operation | COMPLETED + CLOSED | Refresh closure-aware cockpit state |
| CLOSED | Reopen Operation (reason required) | OPEN + controlled non-running state | Refresh cockpit from backend truth |

## 4. Release transitions

| Current state | Trigger | Result |
|---|---|---|
| PLANNED | Release Claim | Allowed |
| IN_PROGRESS / PAUSED / BLOCKED | Release Claim | Rejected / unavailable |

## 5. Closure-aware transitions

### 5.1 Close
- only from closeable completed/open context
- closure action lives in secondary guarded section
- after success, normal runtime-action UX should no longer appear usable

### 5.2 Reopen
- only from CLOSED context
- reopen reason is mandatory
- after success:
  - closure_status becomes OPEN
  - runtime returns to controlled non-running state
  - FE must reload backend truth
  - resumability path is backend-owned

## 6. Deferred future transitions
- QC submit -> QC hold / disposition
- raise_exception -> disposition workflow
- station session open/close first-class transitions
- claim handover / supervised reassignment / support recovery transfer
- explicit multi-claim-enabled operator policy mode
