# Authoritative File Map — FleziBCG Design Docs

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v2.3 | Restored Application, Integration, Database, UI, and Hardening sections after CD Review 1 housekeeping feedback. |
| 2026-04-26 | v2.2 | Updated for latest consolidated design baseline. |
| 2026-04-23 | v2.0 | Baseline authoritative file map. |

## Status

**Canonical source-of-truth map.**

Do not duplicate contradictory truths across files. If there is a conflict, this map identifies the file to trust first.

---

## 1. Product and Scope Truth

| Truth Area | Authoritative File |
|---|---|
| Overall product truth | `00_platform/product-business-truth-overview.md` |
| Function inventory | `00_platform/flezibcg-function-list.md` |
| Function hardening amendments | `00_platform/flezibcg-function-list-hardening-amendment.md` |
| Domain ownership/boundaries | `00_platform/domain-boundary-map.md` |
| Product phase/build posture | `00_platform/product-scope-and-phase-boundary.md` |
| Manufacturing-mode hierarchy | `00_platform/manufacturing-mode-hierarchy-mapping.md` |
| Material vs traceability/inventory boundary | `00_platform/material-traceability-vs-inventory-boundary.md` |

---

## 2. Foundation / Governance Truth

| Truth Area | Authoritative File |
|---|---|
| IAM/session/access governance | `01_foundation/identity-access-session-governance.md` |
| Session/token lifecycle | `01_foundation/session-and-token-lifecycle.md` |
| User lifecycle | `01_foundation/user-lifecycle-and-admin-operations.md` |
| Role/scope resolution | `01_foundation/role-model-and-scope-resolution.md` |
| Approval/SoD | `01_foundation/approval-and-separation-of-duties-model.md` |
| Audit/observability foundation | `01_foundation/audit-and-observability-architecture.md` |
| Engineering rules | `docs/governance/CODING_RULES.md` |
| Engineering decisions | `docs/governance/ENGINEERING_DECISIONS.md` |
| Source structure/tooling | `docs/governance/SOURCE_STRUCTURE.md` |

---

## 3. Execution Truth

| Truth Area | Authoritative File |
|---|---|
| Station Execution business truth | `02_domain/execution/business-truth-station-execution-v4.md` |
| Station Execution command/event contracts | `02_domain/execution/station-execution-command-event-contracts-v4.md` |
| Station Execution state matrix | `02_domain/execution/station-execution-state-matrix-v4.md` |
| Execution authorization | `02_domain/execution/station-execution-authorization-matrix-v4.md` |
| Execution policy/master data | `02_domain/execution/station-execution-policy-and-master-data-v4.md` |
| Execution operational SOP | `02_domain/execution/station-execution-operational-sop-v4.md` |
| Execution exception/approval | `02_domain/execution/station-execution-exception-and-approval-matrix-v4.md` |

Older v3/v3.1 Station Execution files are superseded stubs unless explicitly marked otherwise.

---

## 4. Quality / Material / Traceability Truth

| Truth Area | Authoritative File |
|---|---|
| Quality domain overview | `02_domain/quality/quality-domain-overview.md` |
| Quality integration | `02_domain/quality/quality-integration.md` |
| Quality Lite state matrix | `02_domain/quality/quality-lite-state-matrix.md` |
| Material operations | `02_domain/material/material-operations-domain.md` |
| Traceability | `02_domain/traceability/traceability-domain-overview.md` |
| Maintenance context | `02_domain/maintenance/maintenance-and-equipment-context-model.md` |
| Andon/incidents | `02_domain/andon/andon-escalation-and-incident-model.md` |
| Planning/APS | `02_domain/planning/planning-and-scheduling-domain.md` |

---

## 5. Application / API / Event Truth

| Truth Area | Authoritative File |
|---|---|
| API contract standard | `05_application/canonical-api-contract.md` |
| API design guidelines | `05_application/api-design-guidelines.md` |
| API surface grouping | `05_application/canonical-api-surface-map.md` |
| API catalog | `05_application/api-catalog-current-baseline.md` |
| Event catalog/subscriber map | `05_application/event-catalog-and-subscriber-map.md` |
| Reporting/read models | `05_application/reporting-and-read-model-catalog.md` |
| FE/BE responsibility split | `05_application/frontend-backend-responsibility-map.md` |

---

## 6. UI Truth

| Truth Area | Authoritative File |
|---|---|
| FE screen inventory | `05_application/fe-screen-inventory-and-navigation-map.md` |
| Screen navigation architecture | `05_application/screen-map-and-navigation-architecture.md` |
| UI pack roadmap | `07_ui/ui-pack-roadmap.md` |
| Station execution UI | `07_ui/station-execution-screen-pack-v4.md` |
| Foundation IAM UI | `07_ui/foundation-iam-screen-pack-canonical.md` |
| Global operations UI | `07_ui/global-operations-screen-pack-canonical.md` |
| Quality Lite UI | `07_ui/quality-lite-screen-pack-canonical.md` |
| Traceability UI | `07_ui/traceability-screen-pack-canonical.md` |

---

## 7. Integration Truth

| Truth Area | Authoritative File |
|---|---|
| ERP boundary | `03_integration/erp-integration-boundary.md` |
| Integration architecture | `03_integration/integration-architecture-overview.md` |
| External interface catalog | `03_integration/external-interface-catalog.md` |
| Failure/reconciliation rules | `03_integration/integration-failure-and-reconciliation-rules.md` |
| Shopfloor connectivity | `03_integration/shopfloor-connectivity-patterns.md` |
| Backend integration API boundary | `06_application_backend/integration-api-boundary.md` |
| ERP integration database design | `09_data/erp-integration-database-design.md` |

---

## 8. Database Truth

| Truth Area | Authoritative File |
|---|---|
| Database architecture | `09_data/database-design-canonical.md` |
| Table inventory | `09_data/database-table-catalog.md` |
| Logical table definitions | `09_data/database-table-definitions.md` |
| Hardening DB amendment | `09_data/database-table-definitions-hardening-amendment.md` |
| ERD | `09_data/database-erd.md` |
| Implementation phasing | `09_data/database-implementation-phasing.md` |
| Future schema appendix | `09_data/database-future-schema-appendix.md` |

---

## 9. AI / Reporting / Digital Twin Truth

| Truth Area | Authoritative File |
|---|---|
| KPI/OEE/reporting | `04_ai/analytics-kpi-and-oee-model.md` |
| AI architecture/governance | `04_ai/ai-architecture-and-governance.md` |
| AI use-case roadmap | `04_ai/ai-use-case-map-wave1-wave2.md` |
| APS-lite | `04_ai/aps-lite-and-scheduling-support.md` |
| Operational digital twin | `04_ai/operational-digital-twin-model.md` |
| AI/digital twin interaction | `04_ai/ai-and-digital-twin-interaction.md` |

---

## 10. Hardening Truth

| Truth Area | Authoritative File |
|---|---|
| Hardening backlog/register | `10_hardening/hardening-action-register.md` |
| Immediate consistency patch | `10_hardening/immediate-consistency-patch.md` |
| Hardening response to review | `10_hardening/hardening-review-response.md` |
| CD Review 1 housekeeping response | `10_hardening/cd-review-1-response.md` |
| Task 4.1 completion report | `10_hardening/hardening-housekeeping-v1.1-report.md` |
| CloudEvents/event format | `10_hardening/event-format-and-cloudevents-boundary.md` |
| API version/error format | `10_hardening/api-versioning-and-error-format.md` |
| Tenant isolation/RLS | `10_hardening/tenant-isolation-and-rls-strategy.md` |
| Performance/capacity SLO | `10_hardening/performance-capacity-slo.md` |
| Partition/archive/snapshot | `10_hardening/database-partition-archive-strategy.md` |
| Shopfloor connectivity | `10_hardening/shopfloor-connectivity-strategy.md` |
| Observability | `10_hardening/observability-stack.md` |
| Authorization policy engine | `10_hardening/authorization-policy-engine-adr.md` |
| OEE formula/KPI | `10_hardening/oee-formula-and-kpi-definition.md` |
| EPCIS alignment | `10_hardening/traceability-epcis-alignment.md` |
| ISA-88 batch alignment | `10_hardening/isa88-batch-alignment.md` |
| Extraction-aware architecture | `10_hardening/modular-monolith-extraction-aware-architecture.md` |
| Cache strategy | `10_hardening/cache-strategy.md` |
| AI guardrails | `10_hardening/ai-guardrails-and-operational-safety.md` |
| Timezone/localization | `10_hardening/timezone-and-localization-strategy.md` |

---

## 11. Audit Artifacts

Review reports and cross-review reports are audit artifacts. They can justify why a decision was made, but they must not override canonical product/domain/API/database truth.
