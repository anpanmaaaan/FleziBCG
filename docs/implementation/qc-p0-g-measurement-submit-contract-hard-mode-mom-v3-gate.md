# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Quality truth is already server-owned, but the public request contract still exposed threshold fields that implied client authority. This slice narrows the contract so the submit API accepts only operator-observed facts and the frontend sends only those facts while displaying backend-owned requirement limits read-only.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/00_platform/product-business-truth-overview.md | backend-authoritative operational truth |
| docs/design/02_domain/quality/quality-domain-contracts.md | backend-owned quality truth and operator-input boundary |
| docs/design/02_domain/quality/business-truth-quality-lite.md | frontend does not decide pass/fail and quality interacts with execution through backend truth |
| docs/design/02_domain/quality/quality-lite-command-event-contracts.md | measurement submit command/event baseline |
| docs/design/05_application/api-catalog-current-baseline.md | public quality API baseline |
| docs/governance/CODING_RULES.md | backend-source-of-truth and service-layer enforcement |
| docs/design/DESIGN.md | frontend operational clarity and backend-truth boundary |
| docs/audit/frontend-source-alignment-snapshot.md | current frontend maturity and route/source alignment context |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| submit_qc_measurement | Quality | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | listed command |
| load measurement requirements | Quality | docs/design/02_domain/quality/business-truth-quality-lite.md | template-driven measurement submission |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| qc_measurement_submitted | measurement submission | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | event intent list |
| qc_result_recorded | backend evaluation | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | event intent list |
| qc_hold_applied | out-of-spec result | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | event intent list |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| QC_PASSED / QC_HOLD | quality status | docs/design/02_domain/quality/quality-domain-contracts.md | canonical quality statuses |
| PARTIAL | screen phase | docs/ai-skills/stitch-design-md-ui-ux/SKILL.md | screen phase discipline |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| Backend decides quality truth | quality_hold | docs/design/02_domain/quality/quality-domain-contracts.md | QD-001 |
| Operator records inputs, not final quality outcome | quality_hold | docs/design/02_domain/quality/quality-domain-contracts.md | QD-002 |
| Frontend does not decide pass/fail | quality_hold | docs/design/02_domain/quality/business-truth-quality-lite.md | core rules |
| Frontend must display backend truth, not invent API fields | integration_boundary | docs/ai-skills/stitch-design-md-ui-ux/SKILL.md | Core UI Principles |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| required-item completeness enforcement | docs/design/02_domain/quality/quality-domain-contracts.md | separate follow-up slice |
| new route or navigation changes | docs/audit/frontend-source-alignment-snapshot.md | route surface unchanged |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| submit_qc_measurement | qc_measurement_submitted | domain_event | measurement_record_id, submitted_by, submitted_at | measurement audit trace | quality-lite-command-event-contracts.md |
| submit_qc_measurement | qc_result_recorded | domain_event | quality_status, review_status | quality result projection | quality-lite-command-event-contracts.md |
| submit_qc_measurement with invalid extra request fields | none_required | none_required | n/a | command rejected | quality-domain-contracts.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| request contract accepts only operator-observed facts | integration_boundary | schema + frontend API client | No | Yes | QD-002 |
| threshold fields are rejected, not ignored | quality_hold | schema | No | Yes | QD-001 |
| frontend displays backend limits read-only | projection_consistency | frontend page | No | Yes | DESIGN.md / Stitch skill |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Measurement request | requirement-backed operation | submit_qc_measurement with item_code + measured_value | Yes | qc_measurement_submitted | normal quality projection | no | quality-lite-command-event-contracts.md |
| Measurement request | requirement-backed operation | submit_qc_measurement with lower_limit/upper_limit extras | No | none | unchanged | yes | quality-domain-contracts.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QMC-001 | request rejects threshold extras | invalid_input | measurement payload with lower/upper fields | validate request | schema rejects extra fields | no events | threshold fields not part of public contract | quality-domain-contracts.md |
| QMC-002 | backend quality flow still passes | regression | qc_required operation | submit valid item/value pair | QC_PASSED or QC_HOLD as before | quality events preserved | narrowed contract does not regress behavior | quality-lite-command-event-contracts.md |
| QMC-003 | frontend submits only item/value | regression | requirements loaded on measurement page | submit measurement | request shape excludes thresholds | n/a | FE sends intent only | Stitch skill |

## Implementation Plan

1. Narrow backend request schemas to `item_code` and `measured_value` only and forbid extra fields.
2. Update backend tests to the narrowed payload and add a regression for threshold-field rejection.
3. Update frontend API types and MeasurementEntry payload building.
4. Keep backend requirement limits visible in the UI as read-only display values.
5. Run focused backend tests and frontend build/lint.