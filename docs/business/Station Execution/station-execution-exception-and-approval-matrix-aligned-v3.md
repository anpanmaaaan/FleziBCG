# Station Execution Exception and Approval Matrix
## Current implementation alignment note

Status: **Canonical target policy remains broader than current implementation**

## 1. Important current-baseline truth
The station-specific exception and disposition lifecycle is **not implemented** in the current backend baseline.

Therefore this matrix remains:
- design truth for future phases
- not current executable backend behavior

## 2. Current implementation effect
Because exception/disposition is not yet implemented:
- no exception record lifecycle exists in station execution core
- no `record_disposition_decision` command exists in current station execution backend
- no approved-effects consumption exists in the current execution-core baseline

## 3. What is implemented instead
The current baseline implements a narrower execution-core foundation:
- claim/start/pause/resume/report/downtime/complete
- closure_status
- close/reopen foundation
- narrow supervisor-owned close/reopen phase rule

## 4. Governance note
Do not read this matrix as “already executable behavior” in the current baseline. Treat it as deferred canonical target policy until the exception/review/quality layers are implemented.
