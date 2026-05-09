# Full QA Feature Implementation Plan

## Routing
- Selected brain: MOM Brain
- Selected mode: Architecture plus Strict
- Hard Mode MOM: v3
- Reason: Full QA feature touches quality truth, execution gating, state transitions, eventing, disposition authority, and audit/security controls.

## 1. Goal and target scope

Build Full QA as an operational quality capability that evolves Quality Lite into controlled acceptance-gate execution, governed disposition, nonconformance lifecycle foundation, and quality-driven execution control.

Target scope in this plan:
- acceptance gate definition and runtime gate instances
- measurement capture and backend evaluation at gate level
- hold, release, and recheck with explicit authorization
- deviation and nonconformance foundation
- disposition outcomes (accept, reject, rework, scrap)
- execution allowed-actions blocking and release behavior
- quantity acceptance effects and audit trail
- quality UI surface expansion for operations and quality roles
- quality APIs, events, projections, and verification matrix

Out of scope for initial Full QA release wave:
- full enterprise CAPA program
- supplier quality module
- enterprise document control replacement
- laboratory and advanced SPC workflows beyond operational gate needs

## 2. Current state baseline

Already implemented baseline:
- Quality Lite measurement and evaluation
- quality hold gating behavior for execution
- strict required-item completeness for submit
- backend-owned quality truth and frontend intent-only contract

Main gaps to Full QA:
- no gate definition aggregate and lifecycle
- no full gate instance lifecycle state machine
- no formal deviation request and approval flow
- no full nonconformance lifecycle model
- limited disposition workflow depth and role fallback model
- limited projection/reporting depth for quality governance KPIs

## 3. Hard Mode MOM v3 verdict before coding

Verdict before coding: ALLOW_IMPLEMENTATION

Reason:
- design evidence exists for quality domain principles, state vocabulary, policy families, and API families
- roadmap defines phased expansion path from Quality Lite to Acceptance Gate and Quality Expansion
- governance rules enforce backend truth, event/invariant safety, and service-layer ownership

## 4. Design evidence extract

### Source docs read
- docs/design/INDEX.md
- docs/design/AUTHORITATIVE_FILE_MAP.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md
- docs/governance/SOURCE_STRUCTURE.md
- docs/design/02_domain/quality/quality-domain-contracts.md
- docs/design/02_domain/quality/business-truth-quality-lite.md
- docs/design/02_domain/quality/quality-lite-state-matrix.md
- docs/design/02_domain/quality/quality-lite-policy-and-master-data.md
- docs/design/05_application/api-catalog-current-baseline.md
- docs/design/05_application/canonical-api-contract.md
- docs/design/07_ui/quality-lite-screen-pack-canonical.md
- docs/roadmap/flezibcg-overall-roadmap-latest.md

### Commands or actions found
- submit measurement
- evaluate quality result
- apply quality hold
- request and decide disposition
- block or release execution actions based on quality

### Events found
- qc_measurement_submitted
- qc_result_recorded
- qc_hold_applied
- disposition_decision_recorded
- qc_hold_released
- qc_recheck_requested
- qc_scrap_confirmed
- qc_accepted_with_deviation

### States found
- quality status: QC_NOT_REQUIRED, QC_PENDING, QC_PASSED, QC_FAILED, QC_HOLD
- review status: NO_REVIEW, REVIEW_REQUIRED, DECISION_PENDING, DISPOSITION_DONE

### Invariants found
- backend determines pass or fail and hold truth
- frontend records input and intent only
- quality state remains orthogonal to execution state
- hold requires explicit authorized resolution path
- accepted good may differ from reported good under gating
- quality and governance facts must be auditable

### Explicit exclusions found in roadmap and contracts
- full CAPA in initial expansion wave
- full supplier quality
- enterprise document control as QMS replacement

## 5. Event map

| Command or Action | Required Event | Event Type | Minimum payload | Projection impact |
|---|---|---|---|---|
| Create acceptance gate definition | quality_gate_defined | domain_event | gate id, context selector, policy version, actor | gate catalog projection |
| Activate gate for operation context | quality_gate_instance_opened | domain_event | gate instance id, operation id, gate type, opened by | gate-instance projection |
| Submit gate measurement | qc_measurement_submitted | domain_event | gate instance id, measurement record id, items, actor | measurement timeline projection |
| Evaluate measurement | qc_result_recorded | domain_event | record id, pass or fail, rule set version | result projection |
| Apply hold | qc_hold_applied | domain_event | hold id, gate instance id, reason code, blocked actions | execution allowed-actions projection |
| Request deviation | quality_deviation_requested | domain_event | deviation id, hold id, reason, requester | deviation queue projection |
| Decide disposition | disposition_decision_recorded | domain_event plus audit_event | review id, decision code, decider, rationale | hold and disposition projection |
| Release hold | qc_hold_released | projection_event | hold id, release reason, decider | execution unblocked actions projection |
| Require recheck | qc_recheck_requested | projection_event | hold id, recheck target, due rule | keep blocked and create recheck task |
| Confirm scrap | qc_scrap_confirmed | projection_event | operation id, quantity effect, decider | quantity acceptance projection |

## 6. Invariant map

| Invariant | Category | Enforcement layer | DB constraint needed | Test required |
|---|---|---|---|---|
| Pass or fail and hold computed server-side only | quality_hold | service | no | yes |
| Measurement submit contains observed facts only | integration_boundary | schema plus service | no | yes |
| Required measurement items must all be present | quality_hold | service | no | yes |
| Recheck decision must not clear hold by default | state_machine | service | no | yes |
| Disposition decider must be authorized quality role | authorization | service plus security | no | yes |
| Requester cannot be same as decider where SoD applies | auditability | service plus approval policy | optional | yes |
| Tenant and scope must match operation context | tenant plus scope | route dependency plus service | optional | yes |
| Accepted good effects derived from disposition policy | quantity | service | optional | yes |
| Every governed decision writes auditable event | auditability | service | no | yes |

## 7. State transition map (gate instance)

| Entity | Current state | Command | Allowed | Event | Next state | Invalid test |
|---|---|---|---|---|---|---|
| Gate instance | PENDING_MEASUREMENT | submit measurement | yes | qc_measurement_submitted | PENDING_EVALUATION | duplicate submit while lock |
| Gate instance | PENDING_EVALUATION | evaluate result pass | yes | qc_result_recorded | PASSED | evaluate with missing requirements |
| Gate instance | PENDING_EVALUATION | evaluate result fail | yes | qc_result_recorded plus qc_hold_applied | HOLD_ACTIVE | fail without hold creation |
| Gate instance | HOLD_ACTIVE | request deviation | yes | quality_deviation_requested | DEVIATION_PENDING | deviation without hold |
| Gate instance | HOLD_ACTIVE | decide release | yes | disposition_decision_recorded plus qc_hold_released | RELEASED | unauthorized decider |
| Gate instance | HOLD_ACTIVE | decide recheck | yes | disposition_decision_recorded plus qc_recheck_requested | RECHECK_REQUIRED | hold cleared unexpectedly |
| Gate instance | RECHECK_REQUIRED | resubmit measurement | yes | qc_measurement_submitted | PENDING_EVALUATION | submit partial items |
| Gate instance | RELEASED | close gate | yes | quality_gate_instance_closed | CLOSED | close before decision |

## 8. Implementation phases

### Phase A: Domain model and policy foundation
Deliverables:
- acceptance gate definition aggregate
- gate instance aggregate
- deviation request aggregate
- nonconformance base aggregate
- policy tables for applicability, rule sets, and disposition catalog

Exit criteria:
- migrations applied cleanly
- model relationships and constraints validated
- no frontend dependency required for domain truth

### Phase B: Backend commands, APIs, and service invariants
Deliverables:
- quality API expansion for gate lifecycle and disposition workflow
- service-layer command handlers with invariant enforcement
- event emission and projection update hooks
- authorization checks for quality roles and governed actions

Exit criteria:
- command handlers reject invalid state and unauthorized actor
- event map coverage implemented for all operational commands
- route handlers remain thin and service-owned business logic is complete

### Phase C: Execution gating and quantity-effects integration
Deliverables:
- allowed-actions integration with gate hold states
- quantity acceptance effect handling for release, reject, rework, scrap
- operation detail projection updates for quality and acceptance visibility

Exit criteria:
- execution commands blocked or allowed according to quality gate truth
- accepted good and held quantity effects are deterministic and auditable
- regression tests prove no bypass path

### Phase D: Frontend quality experience expansion
Deliverables:
- gate instance dashboard and detail views
- measurement capture UX aligned with strict completeness and backend contract
- deviation and disposition flows for quality actors
- status and hold visibility in operation screens

Exit criteria:
- frontend sends intent only; no truth derivation
- i18n parity maintained for en and ja
- accessibility gate and route guard behavior verified

### Phase E: Reporting, governance, and release hardening
Deliverables:
- quality operational KPIs and hold aging views
- audit timeline for measurement and disposition decisions
- release checklist and rollback plan
- production-safe migration and reconciliation scripts

Exit criteria:
- go or no-go checklist signed by quality, execution, and governance owners
- quality events and projections are reconciliable
- security and audit events complete for governed actions

## 9. Test matrix (minimum)

| Test ID | Scenario | Type | Then |
|---|---|---|---|
| QA-HAPPY-001 | required measurements pass | happy_path | status becomes QC_PASSED and execution unblocked |
| QA-HAPPY-002 | fail leads to hold | happy_path | status QC_HOLD and blocked allowed-actions |
| QA-STATE-001 | invalid disposition from non-hold state | invalid_state | command rejected, no event written |
| QA-INPUT-001 | missing required measurement item | invalid_input | submit rejected with explicit code |
| QA-AUTH-001 | unauthorized disposition actor | missing_permission | rejected and security event emitted |
| QA-TENANT-001 | cross-tenant operation access | wrong_tenant | rejected, no data leak |
| QA-SCOPE-001 | invalid scope assignment | wrong_scope | rejected |
| QA-EVENT-001 | measurement event payload integrity | event_payload | payload contains required ids and versions |
| QA-EVENT-002 | disposition event payload integrity | event_payload | decision metadata and actor present |
| QA-PROJ-001 | projection reflects hold apply and release | projection_consistency | projection converges to event truth |
| QA-DB-001 | migration invariants for gate relations | db_invariant | constraints prevent orphaned gates |
| QA-AUDIT-001 | governed disposition writes audit trail | audit_security_event | audit event present and queryable |
| QA-REG-001 | existing Quality Lite flow still valid | regression | no behavioral regression in current flow |
| QA-FE-001 | measurement page strict gating | regression | submit disabled until complete |
| QA-FE-002 | quality header visibility selectors stable | regression | visible-only assertions pass |

## 10. Delivery sequencing and timeline

- Sprint 1 and 2: Phase A
- Sprint 3 and 4: Phase B
- Sprint 5: Phase C
- Sprint 6: Phase D
- Sprint 7: Phase E and release readiness

Recommended release style:
- behind feature flags for new gate workflows
- shadow projection validation before hard cutover
- incremental enablement by tenant and line

## 11. Risks and mitigations

- Risk: scope explosion into full enterprise QMS
  - Mitigation: keep CAPA and supplier quality out of first release wave

- Risk: execution bypass under hold
  - Mitigation: dual enforcement in command handlers and allowed-actions projection

- Risk: contract drift between backend and frontend
  - Mitigation: strict schema validation and E2E contract assertions

- Risk: migration instability in production data
  - Mitigation: dry-run scripts and reversible rollout plan per migration slice

## 12. First implementation slice recommendation

Start with Full QA Slice 1:
- gate definition and gate instance lifecycle foundation
- measurement and evaluation through gate instance context
- hold apply and release events with invariant tests

Why first:
- highest leverage for execution safety
- minimal UI expansion needed to validate core truth
- creates foundation for deviation and nonconformance slices
