# ADR - Event Format and CloudEvents Boundary

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added decision for internal event schema and CloudEvents-compatible external boundary. |

## Status

**Accepted design direction.**

## Context

FleziBCG currently uses DB-backed append-only event tables and derived projections. The internal event shape already supports audit and reconstruction needs through fields such as event type, aggregate type, aggregate ID, timestamps, actor, correlation ID, causation ID, and payload.

Future integration or brokered events may need interoperability across services, platforms, and external systems. CloudEvents is a CNCF specification for describing event data in a common way.

## Decision

FleziBCG will keep its **internal DB event schema** as the canonical operational event format.

For external, brokered, webhook, or cross-service event delivery, FleziBCG should expose a **CloudEvents-compatible envelope**.

## Mapping

| FleziBCG internal field | CloudEvents-compatible field |
|---|---|
| `id` | `id` |
| `event_type` | `type` |
| `occurred_at` | `time` |
| domain/app origin | `source` |
| `aggregate_type` + `aggregate_id` | `subject` |
| `payload` | `data` |
| schema/version reference | `dataschema` or extension |
| JSON payload | `datacontenttype = application/json` |
| `correlation_id` | extension `correlationid` |
| `causation_id` | extension `causationid` |
| `tenant_id` | extension `tenantid` |

## P0 Rule

P0 does not need a broker. Internal DB event tables remain sufficient.

## P1/P2 Rule

When events leave the modular monolith boundary, use CloudEvents-compatible envelope.

## Anti-Patterns

- Do not rename internal DB fields just to mimic CloudEvents.
- Do not publish every shopfloor event to ERP.
- Do not let CloudEvents envelope become authorization or business truth.

## References

- CloudEvents specification: https://github.com/cloudevents/spec
