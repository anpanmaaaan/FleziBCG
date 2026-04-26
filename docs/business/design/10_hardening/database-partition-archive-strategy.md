# ADR - Database Partition, Archive, Snapshot, and Retention Strategy

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added database partition/archive/snapshot strategy. |

## Status

**Accepted design direction.**

## Context

FleziBCG uses append-only events and integration messages. These tables can grow quickly and affect station queue, reporting, audit, and reconciliation performance.

## Decision

Do not implement full partitioning in P0 unless volume requires it, but design tables and queries so partitioning/archive can be added without redesign.

## Candidate High-Volume Tables

| Table Family | Partition Candidate | Suggested Key |
|---|---|---|
| `exe.execution_events` | Yes | `occurred_at` monthly/weekly + tenant filter |
| `qual.quality_events` | Yes | `occurred_at` monthly/weekly |
| `audit.audit_log` | Yes | `occurred_at` monthly |
| `audit.security_events` | Yes | `occurred_at` monthly |
| `intg.inbound_messages` | Yes | `received_at` monthly |
| `intg.outbound_messages` | Yes | `created_at` monthly |
| `intg.message_processing_attempts` | Yes | `started_at` monthly |
| `intg.erp_posting_requests` | Maybe | `requested_at` monthly |
| `rpt.*` projections | Usually no | Rebuildable/current state |

## Snapshot Strategy

Use snapshots for expensive rebuilds:

- operation current status;
- station queue;
- line current state;
- OEE shift summary;
- integration status summary;
- digital twin state snapshots when introduced.

Snapshots/projections must be rebuildable from source events/transactions.

## Archive Strategy

| Data Type | Hot Retention | Archive Note |
|---|---:|---|
| Execution events | configurable, e.g. 90-180 days | archive by tenant/plant/time. |
| Audit/security events | customer/regulatory dependent | may require longer retention. |
| Integration payloads | configurable | redact sensitive payloads if needed. |
| Read models | current/rebuildable | no long-term retention required unless report snapshots. |
| Compliance records | regulated/customer dependent | follow compliance policy. |

## Guardrails

- Do not delete source operational events without retention policy.
- Do not archive data required by open work orders, open quality holds, or unreconciled integration postings.
- Do not store large binary payloads directly in event tables.
- Store payload references where payloads become large.

## Implementation Path

P0:
- design indexes and timestamp columns;
- avoid queries that scan full event history;
- add retention policy placeholders.

P1:
- partition high-volume event/integration tables if volume justifies;
- add archive jobs and replay validation.

P2:
- add cold storage/export where customer/regulatory demand exists.
