# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Authoritative Quality Lite docs define one review/disposition path, canonical disposition vocabulary, quality-owned actor ownership, and disposition event intent. This slice records authorized disposition decisions on active quality holds and updates review state without inventing quantity-release behavior.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/02_domain/quality/quality-domain-contracts.md | Disposition ownership, vocabulary, invariants, quality-to-execution interaction |
| docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Disposition command and event intent |
| docs/design/02_domain/quality/quality-lite-state-matrix.md | Review/quality status vocabulary |
| docs/design/02_domain/quality/quality-lite-policy-and-master-data.md | Disposition code catalog baseline |
| docs/design/05_application/api-catalog-current-baseline.md | Target API family for disposition |
| docs/design/05_application/canonical-api-contract.md | API schema rules |
| docs/governance/CODING_RULES.md | Backend-authoritative and service-layer rules |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| record_quality_disposition | Quality | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Listed later where enabled |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| disposition_decision_recorded | Authorized disposition recorded | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Event intent list |
| qc_hold_released | Derived effect after disposition where applicable | docs/design/02_domain/quality/quality-domain-contracts.md | Optional derived/projection event intents |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| DECISION_PENDING / DISPOSITION_DONE | Review status | docs/design/02_domain/quality/quality-lite-state-matrix.md | Canonical review statuses |
| QC_PASSED / QC_FAILED / QC_PENDING / QC_HOLD | Quality status | docs/design/02_domain/quality/quality-lite-state-matrix.md | Canonical quality statuses |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| Quality-owned decisions stay separated from operator actions | authorization | docs/design/02_domain/quality/quality-domain-contracts.md | QD-003 |
| QAL owns quality hold resolution path by default | authorization | docs/design/02_domain/quality/quality-domain-contracts.md | Section 7.2 |
| Hold requires explicit authorized decision path | quality_hold | docs/design/02_domain/quality/quality-domain-contracts.md | QD-INV-004 |
| Quality does not overwrite execution truth directly | state_machine | docs/design/02_domain/quality/quality-domain-contracts.md | QD-INT-001 |
| Important quality facts must remain traceable, including who decided disposition | auditability | docs/design/02_domain/quality/quality-domain-contracts.md | QD-006 |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| accepted-good quantity release policy effects | docs/design/02_domain/quality/quality-domain-contracts.md | Separate quantity policy slice |
| execution allowed-action gating updates | docs/design/02_domain/quality/quality-domain-contracts.md | Interaction is defined, but route/service gating change is separate slice |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| record_quality_disposition | disposition_decision_recorded | domain_event | hold_id, disposition_code, decided_by, decided_at | review/disposition history | quality-lite-command-event-contracts.md |
| record_quality_disposition (release-like result) | qc_hold_released | projection_event | hold_id, disposition_code | active hold queue | quality-domain-contracts.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| only active hold can be disposed | quality_hold | service | No | Yes | quality-domain-contracts.md |
| only QAL may decide by default | authorization | route + service | No | Yes | quality-domain-contracts.md |
| hold and decision must remain tenant-scoped | tenant | repository + service | Yes | Yes | CODING_RULES.md |
| decision is auditable and append-only | auditability | decision table + event log + security event | No | Yes | QD-006 |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Review status | DECISION_PENDING | record_quality_disposition | Yes | disposition_decision_recorded | DISPOSITION_DONE | no | quality-lite-state-matrix.md |
| Hold status | ACTIVE | record_quality_disposition | Yes | disposition_decision_recorded | RELEASED | no | quality-domain-contracts.md |
| Hold status | RELEASED | record_quality_disposition | No | none | unchanged | yes | quality-domain-contracts.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QD-001 | QAL releases hold | happy_path | active hold in tenant | QAL records RELEASE_QC_HOLD | review done, hold released | disposition_decision_recorded | authorized decision path | quality-domain-contracts.md |
| QD-002 | PMG blocked from disposition | missing_permission | active hold | PMG attempts decision | 403/permission error | no disposition event | QAL default ownership | quality-domain-contracts.md |
| QD-003 | tenant isolation | wrong_tenant | active hold in tenant A | tenant B decides | not found/forbidden | no decision event | tenant scoped hold access | CODING_RULES.md |
| QD-004 | already released hold reject | invalid_state | released hold | decide again | conflict | no duplicate decision event | one active review path only | quality-domain-contracts.md |

## Implementation Plan

1. Add disposition decision persistence model and migration.
2. Add repository helpers to fetch/update active holds and append decisions.
3. Add service logic to authorize QAL-only default disposition and map disposition codes to review/quality status.
4. Add API route for disposition command.
5. Add targeted tests and rerun QC suite on mes_test.
6. Update implementation docs after code change.