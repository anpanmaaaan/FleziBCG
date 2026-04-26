# ADR - Cache Strategy

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added DB-first cache strategy and optional Redis hardening path. |

## Status

**Accepted design direction.**

## Context

FleziBCG needs responsive station queues and dashboards. Cache can help, but introducing Redis/cache too early creates consistency and invalidation complexity.

## Decision

P0 is database/projection-first. Redis is not mandatory for P0.

P1 may introduce Redis or another cache selectively for hot paths after measurement.

## P0 Pattern

- PostgreSQL as source of truth.
- Read models/projections for station queue, operation status, line state.
- Proper indexes.
- Short-lived application memory cache only where safe.

## P1 Cache Candidates

| Use Case | Cache Type | Notes |
|---|---|---|
| Station queue snapshot | Redis or in-memory | Must invalidate/rebuild on execution events. |
| Allowed actions | Short TTL cache | Must be invalidated by role/scope/state changes. |
| Session/token revocation | Redis optional | DB remains source of truth. |
| Integration retry locks | Redis optional | Prevent duplicate processing. |
| Reference/master data | Read-through cache | Safe for low-change data with versioning. |

## Guardrails

1. Cache must never be the source of authorization truth.
2. Cache must not hide stale quality/closure/session state.
3. All cacheable reads need stale-data tolerance definition.
4. Write commands must validate against source truth, not cache only.
5. Cache failure must degrade safely.
