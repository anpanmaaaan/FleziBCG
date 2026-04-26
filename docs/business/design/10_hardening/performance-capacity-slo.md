# ADR - Performance, Capacity, and SLO Baseline

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added initial performance/capacity/SLO baseline. |

## Status

**Accepted design direction.**

## Context

FleziBCG is intended to become production-grade. The design must define initial performance expectations early, even before full load testing.

## Decision

Define baseline SLO assumptions now. Validate with load testing before production rollout.

## Initial SLO Targets

| Capability | Initial Target | Notes |
|---|---:|---|
| Station queue read | p95 <= 500 ms | Cached/projection-backed if needed. |
| Start/pause/resume command | p95 <= 800 ms | Excludes external ERP posting. |
| Report production command | p95 <= 1000 ms | Backflush posting must be async if external. |
| Downtime start/end command | p95 <= 800 ms | Should not depend on ERP. |
| Operation detail read | p95 <= 700 ms | May use projections/tabs. |
| Global operations dashboard | p95 <= 1500 ms | Projection-backed. |
| Integration message enqueue | p95 <= 500 ms | Send/ack can be async. |
| Projection freshness | <= 5 seconds for station/line views | P0 target. |
| Audit write | same transaction or reliable async outbox | Must not be lost. |

## Capacity Assumption Template

Each plant rollout should estimate:

- number of tenants;
- plants per tenant;
- lines/stations/equipment;
- concurrent station sessions;
- events per operation;
- operations per shift;
- reporting refresh frequency;
- integration message volume;
- event retention period.

## Design Rules

1. Station execution commands must not synchronously wait for ERP posting.
2. Read-heavy dashboards should use read models/projections.
3. Hot tables need explicit indexes.
4. Event/reconciliation/integration tables need partition/archive strategy before high volume.
5. Gantt/timeline must use business viewport, not auto-fit full history by default.

## P0 Minimum

- Add indexes for station queue, operation status, events by aggregate, and audit lookup.
- Add correlation IDs in logs and responses.
- Define load-test scenarios before production pilot.

## Open Questions

- Exact event volume per station/shift.
- Target number of active stations per plant.
- Expected dashboard refresh rate.
- Production retention policies by customer/regulation.
