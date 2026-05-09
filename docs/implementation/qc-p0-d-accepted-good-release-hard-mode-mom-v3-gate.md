# Hard Mode MOM v3 Gate — QC P0-D Accepted-Good Release Semantics

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Authoritative quality domain docs explicitly define deferred accepted-good derivation until QC pass or authorized disposition, with quantity effects treated as backend-derived quality-to-execution policy outputs.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/02_domain/quality/quality-domain-contracts.md | Canonical quality principles, interaction contract, invariants, disposition vocabulary |
| docs/design/02_domain/quality/business-truth-quality-lite.md | Quality-lite core rules and accepted-good/report-good separation |
| docs/design/02_domain/quality/quality-integration.md | Integration rule for deferred accepted-good derivation |
| docs/design/02_domain/quality/quality-lite-command-event-contracts.md | Required commands/events for quality measurement/disposition |
| docs/design/02_domain/execution/business-truth-station-execution-v4.md | Execution core defers accepted-good derivation to quality-adjacent layer |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| submit_qc_measurement | Quality | quality-lite-command-event-contracts.md | Listed under Commands |
| record_quality_disposition | Quality | quality-lite-command-event-contracts.md | Listed under Commands |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| qc_measurement_submitted | measurement submission | quality-domain-contracts.md | Section 6 measurement/evaluation events |
| qc_result_recorded | evaluation result | quality-domain-contracts.md | Section 6 measurement/evaluation events |
| qc_hold_applied | out-of-spec hold activation | quality-domain-contracts.md | Section 6 measurement/evaluation events |
| disposition_decision_recorded | quality disposition decision | quality-domain-contracts.md | Section 6 review/decision events |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| QC_PASSED / QC_HOLD / QC_PENDING / QC_FAILED | Quality status | quality-domain-contracts.md | Section 5.2 canonical quality status |
| DECISION_PENDING / DISPOSITION_DONE | Review status | quality-domain-contracts.md | Section 5.3 review status |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| FE never decides pass/fail or accepted release | authorization/boundary | quality-domain-contracts.md | QD-001 |
| accepted good not automatically equal to reported good when gate exists | quantity | quality-domain-contracts.md | QD-005 |
| accepted good <= reported good | quantity | quality-domain-contracts.md | QD-INV-003 |
| hold needs explicit authorized decision path | quality_hold | quality-domain-contracts.md | QD-INV-004 |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| SPC/lab/CAPA/supplier quality workflows | quality-domain-contracts.md | Out of Quality Lite current scope |
| broad execution-core accepted-good projection redesign | execution business truth v4 | Accepted-good in execution core remains deferred |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| submit_qc_measurement | qc_measurement_submitted | domain_event | measurement_record_id, submitted_by | measurement audit trace | quality-domain-contracts.md |
| submit_qc_measurement | qc_result_recorded | domain_event | quality_status, review_status, quantity-effect fields | exposes deferred/released quantity effect | quality-domain-contracts.md |
| submit_qc_measurement(out-of-spec) | qc_hold_applied | domain_event | hold_id, reason, held_pending_good_qty | signals hold + deferred quantity | quality-domain-contracts.md |
| record_quality_disposition | disposition_decision_recorded | domain_event | hold_id, disposition_code, decided_by, quantity-effect fields | resolves hold and quantity acceptance effect | quality-domain-contracts.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| accepted_good_release_qty <= operation.good_qty | quantity | service | no | yes | quality-domain-contracts.md |
| hold disposition remains QAL-only default | authorization | service | no | yes | quality-domain-contracts.md |
| quantity effects are backend-derived only | ai_advisory_only / boundary | service + API schema | no | yes | quality-domain-contracts.md |
| tenant-scoped hold/disposition lookup | tenant | repository/service | no | yes | quality-domain-contracts.md |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Quality measurement | QC_HOLD + DECISION_PENDING | record_quality_disposition(RELEASE_QC_HOLD/ACCEPT_WITH_DEVIATION) | yes | disposition_decision_recorded | QC_PASSED + DISPOSITION_DONE + held_pending=0 | non-QAL denied | quality-domain-contracts.md |
| Quality measurement | QC_HOLD + DECISION_PENDING | record_quality_disposition(REQUIRE_RECHECK) | yes | disposition_decision_recorded | QC_PENDING + DISPOSITION_DONE + held_pending>0 | duplicate disposition denied | quality-domain-contracts.md |
| Quality measurement | QC_HOLD + DECISION_PENDING | record_quality_disposition(CONFIRM_SCRAP) | yes | disposition_decision_recorded | QC_FAILED + DISPOSITION_DONE + held_pending=0 | wrong tenant denied | quality-domain-contracts.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QD-P0D-01 | pass submission releases accepted qty | happy_path | qc_required op with reported good | submit in-spec | accepted release equals reported good, held pending 0 | qc_result_recorded payload has quantity effects | <= reported good | quality-domain-contracts.md |
| QD-P0D-02 | hold submission defers accepted qty | happy_path | qc_required op with reported good | submit out-of-spec | accepted release 0, held pending equals reported good | qc_hold_applied payload includes held pending | deferred acceptance | quality-domain-contracts.md |
| QD-P0D-03 | release disposition releases held qty | happy_path | active hold + reported good | disposition release | accepted release equals reported good, held 0 | disposition event has release qty | <= reported good | quality-domain-contracts.md |
| QD-P0D-04 | recheck keeps held pending qty | regression | active hold + reported good | disposition require recheck | accepted release 0, held pending equals reported good | disposition event has held pending | deferred acceptance | quality-domain-contracts.md |
| QD-P0D-05 | confirm scrap clears held pending qty | regression | active hold + reported good | disposition confirm scrap | accepted release 0, held pending 0 | disposition event has zero held | no accidental release | quality-domain-contracts.md |

## Implementation Plan

1. Extend quality response schemas with backend-derived quantity effect fields.
2. Add internal quantity-effect derivation helper in quality service from operation.good_qty and disposition code.
3. Add quantity-effect fields to quality domain event payloads (`qc_result_recorded`, `qc_hold_applied`, `disposition_decision_recorded`).
4. Add/extend targeted tests to verify release/defer/clear semantics per disposition code and event payload correctness.
5. Run targeted quality tests on mes_test and document results.
