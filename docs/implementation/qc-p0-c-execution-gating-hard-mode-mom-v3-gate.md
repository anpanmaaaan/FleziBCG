# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Authoritative quality contracts define that QC hold may block execution progression. Existing execution service explicitly marks QC blockers as deferred. This slice implements minimal backend progression gating for active QC holds on resume/complete commands and aligns allowed-actions projection accordingly.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/02_domain/quality/quality-domain-contracts.md | QD-INT-002 hold blocks progression, quality/execution boundary |
| docs/design/02_domain/quality/business-truth-quality-lite.md | quality-execution integration principle |
| docs/design/02_domain/quality/quality-lite-state-matrix.md | QC_HOLD vocabulary |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | execution command guard framing |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | command/error-family expectations |
| docs/governance/CODING_RULES.md | backend source of truth and service-layer enforcement |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| resume_execution | Execution | execution state matrix | progression command |
| complete_execution | Execution | execution state matrix | progression command |
| quality hold gate | Quality+Execution | quality-domain-contracts.md | QD-INT-002 |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| qc_hold_applied | QC fail/hold | quality-lite-command-event-contracts.md | quality hold event intent |
| disposition_decision_recorded | hold resolution | quality-lite-command-event-contracts.md | disposition event intent |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| QC_HOLD | quality status | quality-lite-state-matrix.md | canonical quality status |
| IN_PROGRESS / PAUSED | execution status | execution state docs | resume/complete relevant states |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| quality hold may block progression | state_machine | quality-domain-contracts.md | QD-INT-002 |
| quality does not overwrite execution status names | state_machine | quality-domain-contracts.md | QD-INT-001 |
| backend decides allowed progression | authorization | CODING_RULES.md | backend source-of-truth |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| quantity accepted-good release policy | quality-domain-contracts.md | separate quantity slice |
| full approval-bridge for execution resume/complete overrides | quality-domain-contracts.md | not required for minimal hold gate |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| resume_execution (while active hold) | none (reject) | none_required | n/a | command rejected | quality-domain-contracts.md |
| complete_execution (while active hold) | none (reject) | none_required | n/a | command rejected | quality-domain-contracts.md |
| derive allowed_actions | none_required | none_required | n/a | remove blocked actions | CODING_RULES.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| active quality hold suppresses resume/complete affordances | quality_hold | service projection | No | Yes | QD-INT-002 |
| active quality hold blocks resume command | state_machine | service command guard | No | Yes | QD-INT-002 |
| active quality hold blocks complete command | state_machine | service command guard | No | Yes | QD-INT-002 |
| non-progression actions remain available as before | regression | service projection | No | Yes | execution contracts |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Execution | PAUSED + active QC_HOLD | resume_execution | No | none | unchanged | yes | quality-domain-contracts.md |
| Execution | IN_PROGRESS + active QC_HOLD | complete_execution | No | none | unchanged | yes | quality-domain-contracts.md |
| Allowed-actions projection | PAUSED + active QC_HOLD | derive actions | n/a | none | omit resume_execution | yes | CODING_RULES.md |
| Allowed-actions projection | IN_PROGRESS + active QC_HOLD | derive actions | n/a | none | omit complete_execution | yes | CODING_RULES.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QG-001 | paused with active hold cannot resume | invalid_state | paused op + active hold | resume command | STATE_QC_HOLD_ACTIVE | no resume event | hold blocks progression | quality-domain-contracts.md |
| QG-002 | in-progress with active hold cannot complete | invalid_state | in-progress op + active hold | complete command | STATE_QC_HOLD_ACTIVE | no complete event | hold blocks progression | quality-domain-contracts.md |
| QG-003 | allowed actions omit resume under hold | projection_consistency | paused op + active hold | derive detail | resume not listed | none | projection aligned with guard | CODING_RULES.md |
| QG-004 | allowed actions omit complete under hold | projection_consistency | in-progress op + active hold | derive detail | complete not listed | none | projection aligned with guard | CODING_RULES.md |

## Implementation Plan

1. Add quality repository helper for active hold existence by operation.
2. Update execution allowed-actions derivation to accept quality-hold flag.
3. Compute quality-hold flag in derive_operation_detail.
4. Add resume/complete command guards with `STATE_QC_HOLD_ACTIVE`.
5. Add targeted regression tests for command rejection and action suppression.
6. Run targeted tests on mes_test and update implementation report.