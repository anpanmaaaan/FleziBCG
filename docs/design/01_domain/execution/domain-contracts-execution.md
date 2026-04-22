# DOMAIN CONTRACT — EXECUTION

## Purpose
Canonical execution domain definition.

---

## Dimensions

### Runtime Status
- NOT_STARTED
- RUNNING
- PAUSED
- COMPLETED

### Closure Status
- OPEN
- CLOSED

---

## Events
- execution.claimed
- execution.released
- execution.started
- execution.paused
- execution.resumed
- execution.completed
- execution.closed
- execution.reopened

---

## Action Codes
- execution.claim
- execution.start
- execution.pause
- execution.resume
- execution.complete
- execution.close
- execution.reopen

---

## Invariants
- Single active claim per operation
- Closed record cannot mutate
- Events are append-only
