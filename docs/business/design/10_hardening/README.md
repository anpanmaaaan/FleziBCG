# Hardening Documentation — FleziBCG MOM Platform

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.1 | Added housekeeping patch references: CD Review 1 response, timezone/localization ADR, current phase/BLOCKED reason fix, updated register. |
| 2026-04-26 | v1.0 | Created hardening folder for action register, immediate patches, and ADR pack. |

## Status

**Canonical production-hardening documentation folder.**

This folder sits on top of the latest baseline and does not authorize broad implementation by itself.

---

## 1. Core Hardening Governance

| File | Purpose |
|---|---|
| `hardening-action-register.md` | Canonical hardening backlog and task order. |
| `immediate-consistency-patch.md` | Summary of Task 2 immediate consistency fixes. |
| `hardening-task2-completion-report.md` | Task 2 completion report. |
| `hardening-task3-adr-pack-summary.md` | Task 3 ADR summary. |
| `hardening-task4-package-export-report.md` | Task 4 package export report. |
| `hardening-housekeeping-v1.1-report.md` | Task 4.1 housekeeping completion report. |
| `hardening-review-response.md` | Response to first hardening review. |
| `cd-review-1-response.md` | Response to CD Review 1 housekeeping feedback. |
| `cross-review-report-governance-note.md` | Clarifies cross-review reports are audit artifacts, not canonical truth. |

---

## 2. ADR / Decision Notes

| File | Purpose |
|---|---|
| `event-format-and-cloudevents-boundary.md` | Internal event schema vs CloudEvents boundary compatibility. |
| `api-versioning-and-error-format.md` | `/api/v1` and RFC 9457-compatible Problem Details. |
| `tenant-isolation-and-rls-strategy.md` | App-layer tenant/scope + P1 RLS defense-in-depth. |
| `performance-capacity-slo.md` | Initial performance/capacity targets. |
| `database-partition-archive-strategy.md` | Partition/archive/snapshot strategy. |
| `shopfloor-connectivity-strategy.md` | OPC UA/MQTT/Sparkplug/edge/time-sync direction. |
| `observability-stack.md` | Logs/metrics/traces/error tracking. |
| `authorization-policy-engine-adr.md` | Typed internal policy service and future OPA/Casbin evaluation. |
| `oee-formula-and-kpi-definition.md` | Deterministic OEE formula and source rules. |
| `traceability-epcis-alignment.md` | Internal genealogy and EPCIS compatibility path. |
| `isa88-batch-alignment.md` | ISA-88 batch/process deferral and upgrade path. |
| `modular-monolith-extraction-aware-architecture.md` | Modular monolith, extraction-aware architecture. |
| `cache-strategy.md` | DB-first P0, optional Redis/cache P1/P2. |
| `ai-guardrails-and-operational-safety.md` | AI metadata, validation, and no-autonomous-mutation rules. |
| `timezone-and-localization-strategy.md` | UTC storage, plant timezone, shift-cross-midnight, DST, i18n. |

---

## 3. Rule

Hardening docs inform implementation constraints and future decisions. They do not expand P0 scope unless a task explicitly says so.
