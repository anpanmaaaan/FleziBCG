# Station Execution Policy and Master Data
## Current implemented backend baseline alignment

Status: **Configuration/policy alignment note for the current implemented backend baseline**

This version focuses on policy truths that already matter to the current implementation.

## 1. Implemented-important execution policy truths

### PMD-EXEC-001 — One running execution per station
Current safe default:
- `one_running_execution_per_station = true`

### PMD-EXEC-002 — Single active unreleased claim per operator per station context
Current safe default:
- `allow_claim_without_release = false`

Meaning:
- operator may not stack unreleased claims in the same station context
- queue remains visible, but second-claim attempts are rejected
- this is ownership clarity, not navigation restriction

### PMD-EXEC-003 — Start requires claim
Current baseline behavior assumes:
- `allow_start_without_claim = false`

### PMD-EXEC-004 — Report while paused
Current implemented baseline:
- `allow_report_while_paused = false`

### PMD-EXEC-005 — Complete with open downtime
Current implemented baseline:
- `allow_complete_with_open_downtime = false`

## 2. Closure policy truths implemented now

### PMD-CLOSE-001 — Manual close exists
Current baseline supports manual close foundation.

### PMD-CLOSE-002 — Close authorization phase rule
Current implemented phase rule:
- `close_operation` is hardened to `SUP` at API boundary

### PMD-CLOSE-003 — Reopen foundation exists
Current baseline supports reopen foundation with:
- required reopen reason
- reopen metadata
- controlled non-running reopened behavior (`PAUSED`)
- claim continuity preservation/restoration when safe

## 3. Deferred policy families
Designed but not implemented end-to-end in the current baseline:
- session policy family
- quality policy family
- exception/disposition policy family
- full close/reopen approval-policy matrix
- accepted-good derivation modes

## 4. Master-data warning
The current execution-core baseline still uses some hardcoded behavior where full policy-driven resolution is not yet implemented. Do not mistake this for final multi-plant policy maturity.
