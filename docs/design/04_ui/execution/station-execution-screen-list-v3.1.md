# Station Execution — Screen List (Aligned Current Baseline)

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-22 | v3.1 | Align downtime reason documentation to backend master data using `reason_code`. |

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
| SE-SCR-03 | Start Downtime | Modal / inline panel | OPR | Select downtime reason from backend catalog, optionally add note, and open downtime | From cockpit | Yes |
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
