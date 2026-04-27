# Eventing and Projection Architecture

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.1 | Added explicit implementation note for DB-backed event log and optional broker evolution. |

Status: Canonical eventing/projection note.

## 1. Core rule

Important operational facts are append-only events.
Lifecycle status and read models are derived.

## 2. Current implementation direction

The minimum valid implementation pattern for FleziBCG is:
- DB-backed append-only event log/history
- deterministic service-layer write rules
- derived projections/read models for queue, cockpit, detail, dashboards, and timeline views

A broker, workflow engine, or distributed event backbone is **optional later**, not required by default to satisfy the platform's event-driven principle.

## 3. Event families

### Foundation events
- user/session lifecycle
- role/scope assignment
- approval and impersonation lifecycle

### Execution events
- session opened/closed
- operator identified
- equipment bound/unbound
- execution started/paused/resumed/completed/aborted
- production/downtime/material-related events as applicable
- close/reopen events

### Quality events
- QC measurement submitted
- QC result evaluated
- hold applied/released
- disposition recorded

### Traceability/material events
- lot consumed/produced/transferred
- genealogy edges
- inventory/WIP movement events later

## 4. Projection design rules

- queue, cockpit, detail, and Gantt must derive from the same backend event truth
- projections may flatten status for ergonomics, but must not become source of truth
- event-derived read models should remain reproducible from the event stream/history
- current discrete-first screens may consume discrete-specific projections, but the event model must not assume only station/claim semantics forever

## 5. Transition rule for claim deprecation

Claim-centric events may exist during migration.
They are compatibility debt, not target vocabulary.
Target execution ownership events should be session-oriented.
