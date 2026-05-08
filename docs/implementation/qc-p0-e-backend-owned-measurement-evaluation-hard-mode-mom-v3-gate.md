# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Authoritative quality docs require backend-owned quality truth and explicitly prohibit frontend-authoritative pass/fail decisions. This correction slice narrows the existing measurement submit path so spec limits and valid measurement items are resolved server-side from the operation requirement context rather than trusted from the request payload.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/00_platform/product-business-truth-overview.md | platform truth and backend-authoritative operational facts |
| docs/design/02_domain/quality/quality-domain-contracts.md | backend-owned quality truth, operator-input boundary, canonical events/invariants |
| docs/design/02_domain/quality/business-truth-quality-lite.md | quality-lite rules and FE/backend boundary |
| docs/design/02_domain/quality/quality-lite-state-matrix.md | canonical quality/review statuses |
| docs/design/02_domain/quality/quality-lite-command-event-contracts.md | measurement submit command and event intent |
| docs/governance/CODING_RULES.md | backend source-of-truth and service-layer enforcement |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| submit_qc_measurement | Quality | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | listed under Commands |
| get quality measurement requirements | Quality | docs/design/02_domain/quality/business-truth-quality-lite.md | template-driven measurement submission |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| qc_measurement_submitted | measurement submission | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | event intent list |
| qc_result_recorded | backend evaluation result | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | event intent list |
| qc_hold_applied | out-of-spec evaluation | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | event intent list |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| QC_PASSED / QC_HOLD | quality status | docs/design/02_domain/quality/quality-lite-state-matrix.md | canonical quality statuses |
| NO_REVIEW / DECISION_PENDING | review status | docs/design/02_domain/quality/quality-lite-state-matrix.md | canonical review statuses |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| Backend decides quality truth | quality_hold | docs/design/02_domain/quality/quality-domain-contracts.md | QD-001 |
| Operator records inputs, not final quality outcome | quality_hold | docs/design/02_domain/quality/quality-domain-contracts.md | QD-002 |
| Frontend does not decide pass/fail | quality_hold | docs/design/02_domain/quality/business-truth-quality-lite.md | core rules |
| Service layer owns business rules | authorization | docs/governance/CODING_RULES.md | backend layering rules |
| Tenant-scoped operation lookup remains mandatory | tenant | docs/governance/CODING_RULES.md | tenant isolation policy |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| requirement completeness / mandatory-all-items enforcement | docs/design/02_domain/quality/quality-domain-contracts.md | not defined for this correction slice |
| recheck hold semantics | docs/design/02_domain/quality/quality-domain-contracts.md | follow-up slice |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| submit_qc_measurement | qc_measurement_submitted | domain_event | measurement_record_id, submitted_by, submitted_at | measurement audit trace | quality-lite-command-event-contracts.md |
| submit_qc_measurement | qc_result_recorded | domain_event | quality_status, review_status, quantity-effect fields | quality result projection | quality-lite-command-event-contracts.md |
| submit_qc_measurement when any value is out of backend spec | qc_hold_applied | domain_event | hold_id, reason, review_status | active hold queue | quality-lite-command-event-contracts.md |
| submit_qc_measurement with unsupported item code | none_required | none_required | n/a | command rejected, no mutation | quality-domain-contracts.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| backend thresholds override client-supplied thresholds | quality_hold | service | No | Yes | QD-001 / business-truth-quality-lite.md |
| unknown measurement item code is rejected | quality_hold | service | No | Yes | QD-002 |
| tenant-scoped operation lookup is preserved | tenant | service + repository | No | Yes | CODING_RULES.md |
| rejected invalid input writes no quality events | event_append_only | service | No | Yes | quality-domain-contracts.md |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Quality status | QC_PENDING conceptually | submit_qc_measurement with in-spec value under backend thresholds | Yes | qc_measurement_submitted + qc_result_recorded | QC_PASSED | no | quality-lite-state-matrix.md |
| Quality status | QC_PENDING conceptually | submit_qc_measurement with out-of-spec value under backend thresholds | Yes | qc_measurement_submitted + qc_result_recorded + qc_hold_applied | QC_HOLD | no | quality-lite-state-matrix.md |
| Quality status | QC_PENDING conceptually | submit_qc_measurement with unsupported item code | No | none | unchanged | yes | quality-domain-contracts.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QME-001 | backend thresholds override client thresholds | regression | qc_required operation with DIM_A backend spec 10.0-10.5 | submit DIM_A=12.0 with client upper_limit=99 | status QC_HOLD, response thresholds are backend values | qc_hold_applied written | client cannot force pass | quality-domain-contracts.md |
| QME-002 | unknown item code rejected | invalid_input | qc_required operation | submit UNKNOWN item code | ValueError / 400 path | no quality events | only backend-known items accepted | quality-domain-contracts.md |
| QME-003 | normal in-spec pass still works | regression | qc_required operation | submit valid in-spec DIM_A | QC_PASSED | qc_result_recorded written | no regression | quality-lite-command-event-contracts.md |

## Implementation Plan

1. Add regression tests for backend-threshold override and unknown item code rejection.
2. Resolve the backend requirement map inside quality service from the operation requirement context.
3. Evaluate submitted values against backend limits and echo backend limits in stored/result values.
4. Run focused quality service pytest slice and update implementation report.