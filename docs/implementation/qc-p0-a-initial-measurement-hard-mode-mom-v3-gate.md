# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Authoritative quality design docs define a minimal Quality Lite command/event and state baseline for measurement submission and hold creation. This slice implements only backend measurement submission and backend-evaluated pass/hold with append-only event evidence, without inventing out-of-scope SPC/lab/CAPA behavior.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/00_platform/product-business-truth-overview.md | Backend truth, event-driven operational facts, governance principles |
| docs/design/02_domain/quality/quality-domain-contracts.md | Canonical quality entities, statuses, event intent, ownership, invariants |
| docs/design/02_domain/quality/business-truth-quality-lite.md | Quality Lite scope and execution interaction baseline |
| docs/design/02_domain/quality/quality-lite-state-matrix.md | Canonical quality/review status vocabulary |
| docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Required commands and event intents |
| docs/design/05_application/canonical-api-contract.md | API contract and datetime/code rules |
| docs/governance/CODING_RULES.md | Layering, backend-source-of-truth, verification gates |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| submit_qc_measurement | Quality | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Listed in Quality Lite commands |
| record_quality_disposition (later) | Quality | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Explicitly later-phase command |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| qc_measurement_submitted | Measurement submitted | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Event intent list |
| qc_result_recorded | Backend evaluation complete | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Event intent list |
| qc_hold_applied | Failed evaluation requiring hold | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Event intent list |
| disposition_decision_recorded | Disposition command | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Event intent list (later slice) |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| QC_NOT_REQUIRED / QC_PENDING / QC_PASSED / QC_FAILED / QC_HOLD | Quality status | docs/design/02_domain/quality/quality-lite-state-matrix.md | Canonical quality statuses |
| NO_REVIEW / REVIEW_REQUIRED / DECISION_PENDING / DISPOSITION_DONE | Review status | docs/design/02_domain/quality/quality-lite-state-matrix.md | Canonical review statuses |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| Backend decides quality truth | quality_hold | docs/design/02_domain/quality/quality-domain-contracts.md | QD-001 |
| Operator records inputs; backend evaluates | quality_hold | docs/design/02_domain/quality/quality-domain-contracts.md | QD-002 |
| Quality state orthogonal to execution state | state_machine | docs/design/02_domain/quality/quality-domain-contracts.md | QD-004 |
| Accepted good may differ from reported good under QC | quantity | docs/design/02_domain/quality/quality-domain-contracts.md | QD-005 |
| Auditability for submit/evaluate/disposition | auditability | docs/design/02_domain/quality/quality-domain-contracts.md | QD-006 |
| Tenant isolation is mandatory | tenant | docs/governance/CODING_RULES.md | Tenant/scope isolation policy |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| SPC/control chart/sample plans/lab/CAPA/supplier quality | docs/design/02_domain/quality/quality-domain-contracts.md | Explicit out-of-scope in Quality Lite |
| Disposition write flow in this first slice | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Command marked later |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| submit_qc_measurement | qc_measurement_submitted | domain_event | operation_id, measurement_record_id, submitted_by, submitted_at | measurement history read model | quality-lite-command-event-contracts.md |
| submit_qc_measurement | qc_result_recorded | domain_event | operation_id, measurement_record_id, quality_status, reviewed_status | operation quality status view | quality-lite-command-event-contracts.md |
| submit_qc_measurement (failed eval) | qc_hold_applied | domain_event | operation_id, hold_id, reason, review_status=DECISION_PENDING | hold queue/read model | quality-lite-command-event-contracts.md |
| list quality holds | none_required | none_required | n/a | query only | canonical-api-contract.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| record tenant must match operation tenant | tenant | service + repository query filters | Yes | Yes | CODING_RULES.md |
| measurement submission only for qc_required operations | quality_hold | service guard | No | Yes | quality-domain-contracts.md |
| backend computes pass/hold from submitted values | quality_hold | service | No | Yes | QD-001/QD-002 |
| quality hold creation does not mutate execution status names | state_machine | service | No | Yes | QD-004 |
| measurement and values are append-only facts | event_append_only | service + event log | No | Yes | product-business-truth-overview.md |
| submit action is auditable through event facts | auditability | execution event append | No | Yes | QD-006 |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Quality status | QC_PENDING | submit_qc_measurement (all pass) | Yes | qc_measurement_submitted + qc_result_recorded | QC_PASSED | no | quality-lite-state-matrix.md |
| Quality status | QC_PENDING | submit_qc_measurement (any fail) | Yes | qc_measurement_submitted + qc_result_recorded + qc_hold_applied | QC_HOLD | no | quality-lite-state-matrix.md |
| Quality status | QC_NOT_REQUIRED | submit_qc_measurement | No | none | unchanged | yes | quality-domain-contracts.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QL-001 | pass evaluation | happy_path | qc_required operation | submit measurement values in range | status QC_PASSED, no hold | qc_measurement_submitted + qc_result_recorded | backend-evaluated result | quality-lite-command-event-contracts.md |
| QL-002 | hold evaluation | happy_path | qc_required operation | submit one out-of-range value | status QC_HOLD, hold row created | includes qc_hold_applied | review_status DECISION_PENDING | quality-lite-state-matrix.md |
| QL-003 | qc not required reject | invalid_state | qc_required false operation | submit measurement | 409 conflict | no quality events | no mutation | quality-domain-contracts.md |
| QL-004 | tenant isolation submit | wrong_tenant | operation in tenant A | tenant B submits | 404/403 | no quality events in tenant B | strict tenant boundary | CODING_RULES.md |
| QL-005 | list holds tenant isolation | wrong_tenant | holds in tenant A and B | list as tenant A | only tenant A holds | none_required | tenant filter enforced | CODING_RULES.md |
| QL-006 | invalid input payload | invalid_input | authenticated actor | send empty measurements | 400/422 | none | schema/service validation | canonical-api-contract.md |

## Implementation Plan

1. Add Quality Lite ORM models for measurement record/value and quality hold.
2. Add Alembic migration for new quality tables and indexes.
3. Add schemas and service-layer evaluation logic for submit command.
4. Append quality event intents to execution event stream payload for auditability.
5. Add quality API router endpoints:
   - POST /api/v1/quality/measurements
   - GET /api/v1/quality/holds
6. Add targeted tests for pass/hold, qc_required guard, and tenant isolation.
7. Update implementation docs after code change.