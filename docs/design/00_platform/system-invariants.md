# System Invariants (v4)

- One operator = one active execution (RUNNING | PAUSED)
- Execution cannot complete without quality pass (if required)
- Every state transition MUST emit an event
- Events are immutable and append-only
- All commands must result in either success event or error
