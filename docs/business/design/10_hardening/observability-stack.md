# ADR - Observability Stack

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added observability hardening decision. |

## Status

**Accepted design direction.**

## Context

A production-grade MOM platform must be diagnosable. FleziBCG has strong audit and event design, but operational observability must cover logs, metrics, traces, integration failures, projection lag, queue health, and security signals.

## Decision

Adopt observability as a first-class platform concern.

Minimum P0 observability:

- structured logs;
- correlation ID on every request/command/event;
- audit log for governed actions;
- basic API latency/error metrics;
- database error and slow-query visibility;
- integration-ready trace fields even before integrations are built.

P1/P2 observability:

- OpenTelemetry-style distributed tracing;
- integration inbox/outbox dashboards;
- projection lag metrics;
- station/session health dashboards;
- alerting for failed postings/retries/reconciliation gaps.

## Signal Model

| Signal | Purpose |
|---|---|
| Logs | Debug and operational event context. |
| Metrics | Latency, throughput, error rate, queue depth, projection lag. |
| Traces | End-to-end request/command/integration path. |
| Audit | Business/security accountability. |
| Events | Domain facts. |
| Health checks | Runtime readiness/liveness. |

## Required Correlation Fields

- `correlation_id`
- `causation_id` where applicable
- `tenant_id`
- `actor_user_id` where applicable
- `station_id` / `operation_id` where applicable
- `external_system_id` for integration paths
- `message_id` / `posting_request_id` for integration paths

## Minimum Metrics

| Metric | Phase |
|---|---|
| API p50/p95/p99 latency | P0 |
| API error rate by route/code | P0 |
| command success/failure count | P0 |
| station queue read latency | P0 |
| execution event write latency | P0 |
| projection refresh lag | P0/P1 |
| integration pending/failed/retrying messages | P1 |
| ERP posting pending/failed/reconciled count | P1 |
| audit write failures | P0 |
| database slow queries | P0 |

## Guardrails

- Do not log raw passwords, tokens, secrets, or full sensitive payloads.
- Integration payload logging must support redaction.
- AI prompts/outputs require special redaction policy when introduced.
- Audit logs are not a substitute for technical traces.
