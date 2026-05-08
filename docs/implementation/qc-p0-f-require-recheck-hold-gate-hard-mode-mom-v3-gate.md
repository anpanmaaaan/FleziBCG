# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Authoritative quality docs require quality-to-execution gating through active holds and distinguish recheck from hold release. This correction slice preserves the active quality gate for `REQUIRE_RECHECK` instead of treating every disposition as a release.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/00_platform/product-business-truth-overview.md | backend-authoritative operational truth |
| docs/design/02_domain/quality/quality-domain-contracts.md | quality-owned decisions, optional `qc_recheck_requested`, hold/release vocabulary |
| docs/design/02_domain/quality/business-truth-quality-lite.md | quality must affect execution through allowed-actions and derived quantity effects |
| docs/design/02_domain/quality/quality-lite-state-matrix.md | canonical `QC_PENDING`, `DECISION_PENDING`, `DISPOSITION_DONE` vocabulary |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | execution progression guard expectations |
| docs/governance/CODING_RULES.md | backend source-of-truth and service-layer enforcement |

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| record_quality_disposition | Quality | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | listed command |
| resume_execution | Execution | docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | progression command |
| complete_execution | Execution | docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | progression command |

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| disposition_decision_recorded | quality disposition decision | docs/design/02_domain/quality/quality-lite-command-event-contracts.md | event intent list |
| qc_hold_released | release-like result | docs/design/02_domain/quality/quality-domain-contracts.md | optional derived/projection-facing event |
| qc_recheck_requested | recheck result | docs/design/02_domain/quality/quality-domain-contracts.md | optional derived/projection-facing event |

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|
| QC_PENDING | quality status | docs/design/02_domain/quality/quality-lite-state-matrix.md | canonical quality status |
| DECISION_PENDING | review status | docs/design/02_domain/quality/quality-lite-state-matrix.md | canonical review status |
| ACTIVE / RELEASED | hold status | implementation baseline aligned to quality gate behavior | active hold drives execution gate |

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| quality affects execution through gating, not status renames | state_machine | docs/design/02_domain/quality/quality-domain-contracts.md | QD-004 / interaction contract |
| hold requires explicit authorized resolution path | quality_hold | docs/design/02_domain/quality/business-truth-quality-lite.md | core rules |
| active quality hold blocks execution progression | quality_hold | docs/design/02_domain/quality/business-truth-quality-lite.md | execution interaction |
| backend decides allowed progression | authorization | docs/governance/CODING_RULES.md | backend source-of-truth |

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
| frontend disposition UX changes | docs/design/02_domain/quality/business-truth-quality-lite.md | backend correction slice only |
| broader measurement completeness policy | docs/design/02_domain/quality/quality-domain-contracts.md | unrelated to recheck gate |

## Auto-generated Event Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| record_quality_disposition(REQUIRE_RECHECK) | disposition_decision_recorded | domain_event | hold_id, disposition_code, decided_by | decision history | quality-lite-command-event-contracts.md |
| record_quality_disposition(REQUIRE_RECHECK) | qc_recheck_requested | projection_event | hold_id, disposition_code, quality_status | keep hold queue / gate active | quality-domain-contracts.md |
| resume_execution while recheck hold active | none_required | none_required | n/a | command rejected | business-truth-quality-lite.md |

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| REQUIRE_RECHECK must not clear active hold gate | quality_hold | service | No | Yes | quality-domain-contracts.md |
| release event only for release-like dispositions | projection_consistency | service | No | Yes | quality-domain-contracts.md |
| resume/complete remain blocked while recheck hold active | state_machine | service + existing execution guard | No | Yes | business-truth-quality-lite.md |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Hold | ACTIVE | record_quality_disposition(REQUIRE_RECHECK) | Yes | disposition_decision_recorded + qc_recheck_requested | ACTIVE | no | quality-domain-contracts.md |
| Quality status | QC_HOLD | record_quality_disposition(REQUIRE_RECHECK) | Yes | disposition_decision_recorded | QC_PENDING | no | quality-lite-state-matrix.md |
| Execution | PAUSED + active recheck hold | resume_execution | No | none | unchanged | yes | business-truth-quality-lite.md |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| QRG-001 | require recheck keeps hold active | regression | active hold | QAL records REQUIRE_RECHECK | hold status remains ACTIVE, quality becomes QC_PENDING | includes disposition_decision_recorded and no qc_hold_released | recheck not treated as release | quality-domain-contracts.md |
| QRG-002 | recheck emits recheck projection event | event_payload | active hold | QAL records REQUIRE_RECHECK | qc_recheck_requested emitted | event payload carries hold_id and quality_status | projection aligned to decision | quality-domain-contracts.md |
| QRG-003 | paused execution remains blocked after require recheck | projection_consistency | paused op + active hold | REQUIRE_RECHECK then resume | STATE_QC_HOLD_ACTIVE | no resume event | active hold gate preserved | business-truth-quality-lite.md |

## Implementation Plan

1. Add focused tests for REQUIRE_RECHECK hold persistence and resume blocking.
2. Update disposition service to branch on disposition type instead of always releasing the hold.
3. Emit `qc_recheck_requested` for REQUIRE_RECHECK and suppress `qc_hold_released` there.
4. Run focused quality + execution gating tests and update implementation report.