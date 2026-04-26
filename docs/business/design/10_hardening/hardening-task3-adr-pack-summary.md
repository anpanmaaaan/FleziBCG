# Hardening Task 3 - ADR Pack Summary

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Created ADR pack for production-hardening decisions identified in design review. |

## Status

**Task 3 complete summary.**

This pack records decisions and hardening direction. It does not create implementation scope for P0 unless explicitly stated.

## 1. Decision Philosophy

The baseline remains valid. Task 3 strengthens it by adding production-hardening stances for:

- event interoperability;
- API versioning and error format;
- tenant isolation and RLS;
- performance/SLO/capacity;
- database partition/archive/snapshot;
- shopfloor connectivity;
- observability;
- policy-engine path;
- OEE formula;
- traceability/EPCIS compatibility;
- ISA-88 batch/process alignment;
- modular-monolith extraction awareness;
- cache strategy;
- AI guardrails.

## 2. Build Posture

| Area | P0 Build? | Decision |
|---|---:|---|
| CloudEvents | No | Internal event schema remains FleziBCG canonical; external/brokered events should be CloudEvents-compatible. |
| RFC 9457 error format | Yes, recommended | Adopt hybrid Problem Details response while preserving FleziBCG `code` and `correlation_id`. |
| PostgreSQL RLS | Not mandatory P0 | App-layer enforcement remains mandatory; RLS is P1 hardening for high-risk tenant tables. |
| Performance SLO | Design now | Define baseline SLOs and indexes before scale work. |
| Partition/archive | Design now | Do not overbuild, but prepare event/integration partition strategy. |
| OPC UA/MQTT/Sparkplug B | No | Design adapter path and edge buffering; do not build before integration phase. |
| Observability | Yes, minimum | Add correlation ID, structured logs, basic metrics, and audit observability early. |
| Policy engine | Not external P0 | Use typed internal policy service first; evaluate OPA/Casbin later. |
| OEE formula | Yes, docs/reporting | Define deterministic formula now. |
| EPCIS | No | Internal genealogy first; EPCIS compatibility/export later. |
| ISA-88 | No unless batch-first | Deliberate deferral, but model path for recipe/procedure/phase. |
| Cache/Redis | No mandatory P0 | DB projections first; Redis optional P1 for selected hot paths. |
| AI guardrails | Design now | AI remains advisory; no autonomous mutation. |

## 3. Next Task

Task 4 should merge:

1. latest baseline package;
2. Task 1 action register;
3. Task 2 immediate consistency patch;
4. Task 3 ADR pack;

and export a consolidated hardening baseline package.
