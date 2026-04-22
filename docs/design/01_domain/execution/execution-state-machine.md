# EXECUTION STATE MACHINE

## Runtime

NOT_STARTED -> RUNNING -> PAUSED -> RUNNING -> COMPLETED

## Closure

OPEN -> CLOSED -> OPEN

---

## Rules
- No transition without event
- COMPLETED cannot go back to RUNNING
- CLOSED blocks all mutations except reopen
