# ADR-0002: STATUS MODEL MIGRATION - Incremental Orthogonalization Decision

**Date:** 2026-04-22  
**Status:** Accepted  
**Deciders:** MES Platform Team  
**Supersedes:** None

---

## Context (Current Reality)

The current Station Execution implementation uses one flattened runtime status string for execution flow:

- `PLANNED`
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`

This is accepted as an interim execution-core model, but it is not the canonical target architecture.
Canonical Station Execution remains a multi-dimension model (`dispatch_status`, `execution_status`, `quality_status`, `review_status`, `closure_status`).

Read/write logic must not assume the flattened runtime status is sufficient long-term.

---

## Decision

The project adopts **incremental orthogonalization** for status-model migration.

The project explicitly rejects a big-bang replacement of the current runtime status model in one refactor.

---

## Immediate Implementation Rule (Add First)

The next dimensions to add first are:

1. `closure_status`
2. `quality_status`
3. `review_status`

Why these first:

- they are orthogonal blockers/guards, not replacements for runtime execution flow
- they can be introduced incrementally without rewriting the current execution-core transitions
- they unlock close/reopen controls and future QC/review flows with explicit policy gates

---

## Explicit Deferrals

The following are intentionally deferred to later phases:

- full `dispatch_status` implementation
- station session entity
- `approved_effects` model
- full exception/disposition lifecycle
- full canonical state-matrix parity across all commands

Deferred does not mean optional; it means planned but not in this migration increment.

---

## Runtime Status Rule During Transition

During migration:

- current flattened runtime status remains the interim execution-state carrier for the existing execution core
- newly added orthogonal dimensions must not be folded back into the same flat runtime status string
- future code must model closure/quality/review as separate dimensions, not ad-hoc new runtime status values

---

## Command-Design Implication (Near-Term)

Near-term command guards must evolve as follows:

- runtime status continues to drive execution-state transitions
- `closure_status = CLOSED` blocks execution write commands until authorized reopen
- `quality_status` and `review_status` add explicit blocking to selected commands (including `resume_execution` and `complete_execution`)
- this is the approved interim path until broader canonical model rollout

---

## Canonical vs Implementation Statement

The canonical five-dimension model remains the target architecture.
Current implementation is moving toward that target in controlled increments.
Documentation and code must not claim full canonical parity before it is actually implemented and proven.

---

## What Must Be Added Now vs Later

### Add now

- decision-level commitment to incremental orthogonalization (this ADR)
- implementation rule that first-class orthogonal dimensions are added in this order: closure, quality, review
- guard design rule that these dimensions block selected write commands without replacing runtime execution flow

### Design now, implement later

- dispatch dimension rollout plan
- explicit approved-effect consumption model
- canonical command-level parity plan for all matrix rows

### Intentionally deferred

- items listed in Explicit Deferrals section above

---

## References

- `docs/business/Station Execution/business-truth-station-execution.md`
- `docs/business/Station Execution/station-execution-state-matrix.md`
- `docs/business/Station Execution/station-execution-command-event-contracts.md`
- `docs/adr/ADR-0001-two-dimension-status-model.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
