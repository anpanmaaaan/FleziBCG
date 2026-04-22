# Station Execution — Canonical Screen Pack (Aligned Current Baseline)

This pack consolidates the current canonical screen baseline for Station Execution
aligned to the implemented **Station Execution Core / pre-QC / pre-review** scope.

## Included sections
1. Screen List
2. Screen Design
3. Screen Transition

## Baseline scope
- queue / operation selection
- claim / safe planned-only release claim
- execution cockpit
- report quantity
- pause / resume
- downtime start / end
- complete execution
- closure-aware close / reopen foundation
- active-state continuity (`IN_PROGRESS`, `PAUSED`, `BLOCKED`)
- queue filter persistence / selected-outside-filter helper
- explicit Back to Selection navigation
- Quick Queue popup as quick-switch panel
- single-active-claim default

## Explicitly deferred
- QC measurement / QC hold / quality disposition
- exception / approval / disposition
- station session open/close as first-class hardened flow
- claim handover / reassignment / support recovery transfer
- multi-claim-enabled operator flow
- full close/reopen policy matrix parity (quality/review-owned gating and approval-owned variants)

---

# Station Execution — Screen List (Aligned Current Baseline)

## Scope
This document locks the **screen inventory** for the current implemented
Station Execution baseline before QC lite / review flow expansion.

## In scope
- queue / operation selection
- claim / release claim
- execution cockpit
- report quantity
- pause / resume
- downtime start / end
- complete execution
- closure-aware close / reopen foundation
- active-state continuity (`IN_PROGRESS`, `PAUSED`, `BLOCKED`)
- queue filter persistence / selected-outside-filter helper
- explicit Back to Selection navigation
- Quick Queue popup as quick-switch panel
- single-active-claim default

## Out of scope for this baseline
- QC measurement / QC hold / quality disposition
- exception / approval / disposition inbox
- station session open/close as first-class screen
- supervisor/global-ops screens outside operator station flow
- claim handover / reassignment / support recovery transfer
- full close/reopen policy matrix parity (quality/review/approval-owned variants)
- multi-claim-enabled operator flow

## Principles
- Queue visibility != claimability.
- Queue and cockpit must consume the same backend-derived execution truth.
- `allowed_actions` from backend is the primary action authority.
- `Release Claim` is currently safe only for `PLANNED`.
- Single-active-claim default blocks claim stacking, not navigation.
- Close/Reopen are implemented as **closure-aware foundation controls**, not as full policy-gated variants.

## Screen inventory

| ID | Screen | Type | Primary role | Purpose | Entry point | Current baseline |
|---|---|---|---|---|---|---|
| SE-SCR-01 | Station Queue / Operation Selection | Main page mode | OPR | View station queue, filter, claim claimable item, reopen owned active context | Default station execution landing | Yes |
| SE-SCR-02 | Station Execution Cockpit | Main page mode | OPR | Execute backend-truth-aligned commands on selected operation | Select item from queue | Yes |
| SE-SCR-03 | Start Downtime | Modal / inline panel | OPR | Enter downtime reason + note and open downtime | From cockpit | Yes |
| SE-SCR-04 | Release Claim Confirmation | Dialog | OPR / controlled support | Confirm release only for planned/unstarted safe context | From queue/cockpit when allowed | Yes |
| SE-SCR-05 | Selected item outside filter helper | Inline helper state | OPR | Preserve filter and explain selected item outside visible subset | From queue after refresh/action | Yes |
| SE-SCR-06 | Back to Selection navigation | Header navigation affordance | OPR | Return from cockpit to full selection mode without losing context | From cockpit | Yes |
| SE-SCR-07 | Quick Queue popup | Quick-switch panel | OPR | View queue quickly and switch operation without leaving cockpit | From cockpit header | Yes |
| SE-SCR-08 | Reopen reason dialog | Modal / dialog | SUP in current phase rule | Collect required reopen reason for closure-aware reopen action | From cockpit closure section | Yes |

## Notes
- Queue must show at least `PLANNED`, `IN_PROGRESS`, `PAUSED`, `BLOCKED`.
- `PAUSED` / `BLOCKED` are visible, but not normal claim targets.
- `downtime_open` must be visible enough to explain blocked-by-downtime situations.
- Close/Reopen are not deferred anymore; only **full policy-gated parity** remains deferred.


---

# Station Execution — Screen Design (Aligned Current Baseline)

## 1. Design principles
- Backend is source of truth.
- Queue is the scan / select / claim / reopen-context surface.
- Cockpit is the action surface.
- Quick Queue is a quick-switch panel, not a replacement for full selection mode.
- Queue visibility != claimability.
- `allowed_actions` is the main FE action authority; status branches are secondary helpers only.
- Claim continuity must persist through `IN_PROGRESS`, `BLOCKED`, `PAUSED`.
- Release Claim must not be used to break active execution continuity.
- Single-active-claim default must be reflected in backend and UX.
- Close/Reopen must appear as closure-aware secondary controls, not as ordinary runtime buttons.

## 2. Station Queue / Operation Selection

### Purpose
Help the operator:
- scan the station queue
- claim a truly claimable item
- reopen or re-enter owned active work without losing context

### Queue row data
- status
- downtime_open
- claim.state
- claim.claimed_by_user_id
- operation / WO / PO identifiers
- closure-aware state only where needed for owned completed/closed context if surfaced by current backend truth

### Claim affordance rules
`Claim` / `Ready to claim` should appear only when:
- `claim.state = none`
- status is in current backend claimable set
- operator does not already hold another unreleased claim in the same station context

If operator already holds another unreleased claim:
- other rows are not normal claim targets
- FE should suppress or disable second-claim affordance
- helper text should explain why claim is blocked

### Release affordance rules
Ordinary `Release Claim` is safe only when:
- `claim.state = mine`
- `status = PLANNED`

For `IN_PROGRESS`, `PAUSED`, `BLOCKED`:
- release must be disabled or unavailable

## 3. Station Execution Cockpit

### Purpose
Main execution action surface for selected operation.

### Layout zones
1. Context strip
   - station
   - work order
   - operation
   - claim ownership
   - status
   - closure signal if relevant

2. Execution / production context
   - quantities
   - remaining
   - downtime active / not active
   - next-action hint

3. Quantity entry
   - Good Qty (delta)
   - Scrap Qty (delta)
   - Report Qty as primary action

4. Runtime actions
   - Start / Pause / Resume
   - Start Downtime / End Downtime
   - Complete Operation

5. Closure actions (secondary / guarded)
   - Close Operation (backend-truth-gated)
   - Reopen Operation (backend-truth-gated, reason required)

### Closure-aware behavior
When `closure_status = CLOSED`:
- runtime execution writes should not look normally available
- closure state should be visually clear
- Reopen should be the closure-specific path if backend truth allows it
- Reopen must require a reason dialog
- FE must reload backend truth after success rather than faking a running state

When reopened:
- render according to backend truth
- current foundation behavior is controlled non-running reopened state
- claim continuity and resumability are backend-managed

### Status focus rules
- `BLOCKED + downtime_open=true` -> focus on `End Downtime`
- after `end_downtime` -> `PAUSED`, not auto-resume
- `PAUSED` -> Resume only when backend allows
- `CLOSED` -> closure-aware message + reopen path if allowed

## 4. Start Downtime
- fields: reason class, optional note
- submit returns to same cockpit
- cockpit moves into blocked/downtime-active focus

## 5. Release Claim Confirmation
- only for safe planned context
- refresh queue and selected state after success
- not a recovery tool for active execution

## 6. Selected item outside filter helper
- preserve current filter
- do not silently reset to All
- short helper message only

## 7. Explicit non-goals of this baseline
- QC entry / QC hold
- exception/disposition UI
- full close/reopen policy matrix parity
- generic non-downtime block-cause UI beyond current baseline
- claim handover / supervised reassignment / support recovery transfer


---

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
