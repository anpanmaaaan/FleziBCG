# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Quality measurement submission now has server-owned evaluation and a narrowed request schema, but completeness policy remained open. This slice implements strict completeness for required QC template items so partial required submissions are rejected server-side and the frontend reflects the same gate before submit.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/00_platform/product-business-truth-overview.md | backend authoritative truth baseline |
| docs/design/02_domain/quality/quality-domain-contracts.md | backend-owned quality truth and operator input boundary |
| docs/design/02_domain/quality/business-truth-quality-lite.md | quality-lite interaction and gate principles |
| docs/design/02_domain/quality/quality-lite-command-event-contracts.md | submit command and event baseline |
| docs/design/05_application/api-catalog-current-baseline.md | public quality API baseline |
| docs/governance/CODING_RULES.md | service-layer enforcement and backend truth |
| docs/design/DESIGN.md | frontend operational clarity and explicit blocker guidance |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| submit_qc_measurement | Quality | quality-lite-command-event-contracts.md | command list |
| load requirements and submit measurement values | Quality FE | business-truth-quality-lite.md | template-driven submission |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| qc_measurement_submitted | accepted submission | quality-lite-command-event-contracts.md | event intent |
| qc_result_recorded | backend evaluation | quality-lite-command-event-contracts.md | event intent |
| qc_hold_applied | out-of-spec result | quality-lite-command-event-contracts.md | event intent |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| QC_PASSED / QC_HOLD | quality status | quality-domain-contracts.md | canonical status set |
| PARTIAL | screen phase | stitch-design-md-ui-ux skill | screen status discipline |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| backend decides quality truth | quality_hold | quality-domain-contracts.md | QD-001 |
| operator records inputs, backend evaluates | quality_hold | quality-domain-contracts.md | QD-002 |
| frontend does not authoritatively decide pass/fail | integration_boundary | business-truth-quality-lite.md | core rules |
| blockers should be explicit in operator UX | projection_consistency | DESIGN.md | operational clarity |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| reinspection lifecycle expansion | quality-domain-contracts.md | out of current slice |
| route/menu/access policy changes | frontend alignment snapshot | route surface unchanged |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| submit_qc_measurement with full required set | qc_measurement_submitted | domain_event | measurement_record_id, submitted_by | measurement audit trace | quality-lite-command-event-contracts.md |
| submit_qc_measurement with full required set | qc_result_recorded | domain_event | quality_status, review_status | quality projection | quality-lite-command-event-contracts.md |
| submit_qc_measurement missing required set | none_required | none_required | n/a | request rejected, no mutation | quality-domain-contracts.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| all required template rows must be present | quality_hold | service | No | Yes | quality-domain-contracts.md |
| rejection path writes no quality events | event_append_only | service | No | Yes | coding rules |
| frontend submit affordance matches backend requirement completeness | projection_consistency | frontend page | No | Yes | DESIGN.md |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Measurement request | qc_required operation | submit_qc_measurement with all required rows | Yes | qc_measurement_submitted + qc_result_recorded (+ hold event if needed) | normal quality projection | no | quality-lite-command-event-contracts.md |
| Measurement request | qc_required operation | submit_qc_measurement missing required rows | No | none | unchanged | yes | quality-domain-contracts.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QCM-001 | strict completeness reject | invalid_input | qc_required operation with required template items | submit only subset | error REQUIRED_MEASUREMENTS_MISSING | no quality events | strict completeness enforced server-side | quality-domain-contracts.md |
| QCM-002 | normal pass with complete set | regression | qc_required operation | submit all required in-spec values | QC_PASSED | quality events present | no regression from strict rule | quality-lite-command-event-contracts.md |
| QCM-003 | frontend completeness affordance | projection_consistency | requirements loaded | required rows incomplete | submit disabled + explicit guidance | n/a | FE guidance aligned to backend rule | DESIGN.md |

## Implementation Plan

1. Add strict required-item completeness check in quality service submit path.
2. Update backend tests to submit full required measurement sets where expected and add missing-required regression.
3. Update MeasurementEntry submit affordance and state text to match strict completeness.
4. Run focused backend tests and frontend build/lint.