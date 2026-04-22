# Station Execution — Screen Design (Aligned Current Baseline)

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-22 | v3.1 | Align downtime reason documentation to backend master data using `reason_code`. |

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
- source of options: backend API `/api/v1/downtime-reasons`
- option display: `reason_name`
- submit payload: `reason_code` only
- frontend must not hardcode or derive downtime reason semantics
- loading state required while catalog is being fetched
- empty state required when no active reasons are available
- submit disabled when no reason is selected
- fields: downtime reason from system catalog, optional note
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
