# Immediate Consistency Patch — FleziBCG Hardening Task 2

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Created immediate consistency patch after design review. Fixes P0/P1 ambiguity without expanding product scope. |

## Status

**Task 2 completed patch.**

This patch addresses immediate internal inconsistency and ambiguity identified in the review. It does not introduce production-hardening ADRs yet. Those belong to Task 3.

---

## 1. Patch Scope

Task 2 fixes or clarifies:

| ID | Issue | Resolution |
|---|---|---|
| T2-01 | Rework mismatch between Function List and Station Execution contract | P0 `report_production` is good/scrap only. Rework is P1 via Quality/Rework flow. |
| T2-02 | `ABORTED` exists but has no transition | `ABORTED` is reserved/future-only in P0; no current abort command. |
| T2-03 | Quality-gated execution ambiguity | P0 does not enforce full Acceptance Gate guard; P1 will add explicit quality gate guard to allowed actions. |
| T2-04 | Pre-Acceptance unclear as entity vs type | Pre-Acceptance Check is a canonical `gate_type` under Quality Gate aggregate, not a separate aggregate. |
| T2-05 | Quality Lite state vs Quality Gate lifecycle drift | Added explicit mapping table. |
| T2-06 | Backflush consumption record vs material consumption event relationship unclear | Backflush record is enriched transaction; material consumption event is append-only fact. Link added. |
| T2-07 | Backflush trigger timing drift | Aligned triggers: `quantity_reported`, `operation_completed`, `operation_closed`. |
| T2-08 | CloudBeaver listed as runtime surface without dev-only warning | Clarified CloudBeaver is local/dev-only and forbidden as default production runtime. |
| T2-09 | Cross-review report becoming canonical accidentally | Marked review report as audit artifact, not authoritative design truth. |

---

## 2. Files Patched

```text
docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md
docs/design/02_domain/execution/station-execution-state-matrix-v4.md
docs/design/02_domain/quality/quality-domain-overview.md
docs/design/02_domain/quality/quality-lite-state-matrix.md
docs/design/02_domain/material/material-operations-domain.md
docs/design/09_data/database-table-definitions-hardening-amendment.md
docs/design/00_platform/flezibcg-function-list-hardening-amendment.md
docs/governance/SOURCE_STRUCTURE.md
docs/design/10_hardening/cross-review-report-governance-note.md
```

---

## 3. Explicit Non-Scope

Task 2 does not solve:

- CloudEvents boundary compatibility;
- RFC 9457 / API error format;
- API versioning ADR;
- RLS strategy;
- OPC UA / MQTT / Sparkplug B;
- OEE formula;
- performance/capacity SLO;
- partition/archive strategy;
- observability stack;
- policy engine ADR;
- EPCIS / ISA-88 alignment.

Those are Task 3 ADRs.
