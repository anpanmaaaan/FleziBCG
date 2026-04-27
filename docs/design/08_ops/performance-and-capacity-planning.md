# Performance and Capacity Planning

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Added notes on session/context lookup and large-screen rendering. |

Status: Performance/capacity note.

## Main focus areas
- queue and cockpit reads
- event-to-projection performance
- Gantt/timeline rendering
- station-session lookup and validation
- audit/log volume
- later genealogy/twin analytics

## Rule

Ownership correctness and audit correctness matter more than saving a trivial join or session lookup.
Index and cache consciously, but do not collapse concepts prematurely for convenience.
