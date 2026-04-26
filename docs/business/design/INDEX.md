# FleziBCG Design Documentation Index

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v2.3 | Added Hardening / ADRs section and updated read order after Hardening Housekeeping Patch v1.1. |
| 2026-04-26 | v2.2 | Updated index for latest consolidated design baseline and hardening-v1 package. |
| 2026-04-23 | v2.1 | Prior baseline index. |

## Status

**Canonical read-order index for FleziBCG design docs.**

Use this file to find the authoritative design sources. For production-hardening decisions, use `docs/design/10_hardening/`.

---

## 1. Start Here

1. `00_platform/product-business-truth-overview.md`
2. `00_platform/flezibcg-function-list.md`
3. `00_platform/domain-boundary-map.md`
4. `00_platform/product-scope-and-phase-boundary.md`
5. `AUTHORITATIVE_FILE_MAP.md`
6. `10_hardening/hardening-action-register.md`
7. `10_hardening/hardening-housekeeping-v1.1-report.md`

---

## 2. Platform Architecture

- `00_platform/system-overview-and-target-state.md`
- `00_platform/runtime-architecture-overview.md`
- `00_platform/product-business-truth-overview.md`
- `00_platform/flezibcg-function-list.md`
- `00_platform/domain-boundary-map.md`
- `00_platform/product-scope-and-phase-boundary.md`
- `00_platform/multi-tenancy-and-scope-architecture.md`
- `00_platform/authorization-model-overview.md`
- `00_platform/eventing-and-projection-architecture.md`
- `00_platform/master-data-strategy.md`
- `00_platform/material-traceability-vs-inventory-boundary.md`
- `00_platform/manufacturing-mode-hierarchy-mapping.md`
- `00_platform/deployment-architecture.md`

---

## 3. Foundation / Governance

- `01_foundation/identity-access-session-governance.md`
- `01_foundation/session-and-token-lifecycle.md`
- `01_foundation/user-lifecycle-and-admin-operations.md`
- `01_foundation/role-model-and-scope-resolution.md`
- `01_foundation/approval-and-separation-of-duties-model.md`
- `01_foundation/audit-and-observability-architecture.md`

---

## 4. Domain Docs

- `02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md`
- `02_domain/execution/business-truth-station-execution-v4.md`
- `02_domain/execution/execution-domain-overview.md`
- `02_domain/execution/station-execution-command-event-contracts-v4.md`
- `02_domain/execution/station-execution-state-matrix-v4.md`
- `02_domain/supervisory/supervisory-operations-domain.md`
- `02_domain/quality/quality-domain-overview.md`
- `02_domain/quality/quality-integration.md`
- `02_domain/quality/quality-lite-state-matrix.md`
- `02_domain/material/material-operations-domain.md`
- `02_domain/traceability/traceability-domain-overview.md`
- `02_domain/maintenance/maintenance-and-equipment-context-model.md`
- `02_domain/andon/andon-escalation-and-incident-model.md`
- `02_domain/planning/planning-and-scheduling-domain.md`

---

## 5. Hardening / ADRs

Read these before writing implementation prompts or production-grade code.

### 5.1 Hardening governance

- `10_hardening/README.md`
- `10_hardening/hardening-action-register.md`
- `10_hardening/immediate-consistency-patch.md`
- `10_hardening/hardening-task2-completion-report.md`
- `10_hardening/hardening-task3-adr-pack-summary.md`
- `10_hardening/hardening-task4-package-export-report.md`
- `10_hardening/hardening-housekeeping-v1.1-report.md`
- `10_hardening/cd-review-1-response.md`

### 5.2 Hardening ADRs

- `10_hardening/event-format-and-cloudevents-boundary.md`
- `10_hardening/api-versioning-and-error-format.md`
- `10_hardening/tenant-isolation-and-rls-strategy.md`
- `10_hardening/performance-capacity-slo.md`
- `10_hardening/database-partition-archive-strategy.md`
- `10_hardening/shopfloor-connectivity-strategy.md`
- `10_hardening/observability-stack.md`
- `10_hardening/authorization-policy-engine-adr.md`
- `10_hardening/oee-formula-and-kpi-definition.md`
- `10_hardening/traceability-epcis-alignment.md`
- `10_hardening/isa88-batch-alignment.md`
- `10_hardening/modular-monolith-extraction-aware-architecture.md`
- `10_hardening/cache-strategy.md`
- `10_hardening/ai-guardrails-and-operational-safety.md`
- `10_hardening/timezone-and-localization-strategy.md`

---

## 6. Integration / AI / Digital Twin

- `03_integration/integration-architecture-overview.md`
- `03_integration/erp-integration-boundary.md`
- `03_integration/external-interface-catalog.md`
- `03_integration/integration-failure-and-reconciliation-rules.md`
- `03_integration/shopfloor-connectivity-patterns.md`
- `04_ai/analytics-kpi-and-oee-model.md`
- `04_ai/ai-architecture-and-governance.md`
- `04_ai/ai-use-case-map-wave1-wave2.md`
- `04_ai/aps-lite-and-scheduling-support.md`
- `04_ai/operational-digital-twin-model.md`
- `04_ai/ai-and-digital-twin-interaction.md`

---

## 7. Application Contracts

- `05_application/canonical-api-contract.md`
- `05_application/api-design-guidelines.md`
- `05_application/canonical-api-surface-map.md`
- `05_application/api-catalog-current-baseline.md`
- `05_application/event-catalog-and-subscriber-map.md`
- `05_application/reporting-and-read-model-catalog.md`
- `05_application/frontend-backend-responsibility-map.md`
- `05_application/fe-screen-inventory-and-navigation-map.md`
- `05_application/screen-map-and-navigation-architecture.md`

---

## 8. Backend/API Details

- `06_application_backend/auth-session-api.md`
- `06_application_backend/user-and-access-api.md`
- `06_application_backend/execution-api.md`
- `06_application_backend/quality-lite-api.md`
- `06_application_backend/supervisory-operations-api.md`
- `06_application_backend/integration-api-boundary.md`

---

## 9. UI Packs

- `07_ui/ui-pack-roadmap.md`
- `07_ui/foundation-iam-screen-pack-canonical.md`
- `07_ui/station-execution-screen-pack-v4.md`
- `07_ui/global-operations-screen-pack-canonical.md`
- `07_ui/quality-lite-screen-pack-canonical.md`
- `07_ui/traceability-screen-pack-canonical.md`

---

## 10. Database Design

- `09_data/database-design-canonical.md`
- `09_data/database-table-catalog.md`
- `09_data/database-table-definitions.md`
- `09_data/database-table-definitions-hardening-amendment.md`
- `09_data/database-erd.md`
- `09_data/database-implementation-phasing.md`
- `09_data/erp-integration-database-design.md`
- `09_data/database-future-schema-appendix.md`

---

## 11. Operations / Engineering Governance

- `08_ops/testing-strategy-by-layer.md`
- `08_ops/performance-and-capacity-planning.md`
- `08_ops/migration-and-versioning-strategy.md`
- `08_ops/environment-and-configuration-strategy.md`
- `08_ops/backup-restore-and-dr-policy.md`
- `08_ops/release-readiness-checklist.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`

---

## 12. Rule

If a file is not listed here, it may still be useful, but do not treat it as authoritative without checking `AUTHORITATIVE_FILE_MAP.md`.
