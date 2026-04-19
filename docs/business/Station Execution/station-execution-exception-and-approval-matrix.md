# Station Execution Exception and Approval Matrix (Canonical v1)

Status: Authoritative exception and approval policy  
Owner: Product / Domain / Security / Backend  
Depends on: `business-truth-station-execution.md`, `station-execution-state-matrix.md`, `station-execution-command-event-contracts.md`, `station-execution-authorization-matrix.md`

---

## 1. Purpose

This document defines:

- which situations are modeled as station-execution exceptions
- who may raise them
- who may decide them
- what approval unlocks
- what SoD and evidence rules apply

It is the canonical approval pack for station execution v1.

---

## 2. Core principles

### EX-001 — Exception is a first-class business object
Every exception exists as an explicit backend record with lifecycle, ownership, evidence, and audit trail.

### EX-002 — Approval is not the same as authorization
An actor may have the correct role family yet still be blocked by scope, SoD, missing evidence, or policy.

### EX-003 — Requester must not equal approver
When SoD is required, the raising actor must not be the deciding actor.

### EX-004 — Approval must unlock a defined effect
Approved exception must unlock a specific backend-consumable effect. No vague approval is allowed.

### EX-005 — Rejection remains visible
Rejected exception remains in immutable history and must not disappear silently.

---

## 3. Exception lifecycle

### 3.1 Exception statuses

- `OPEN`
- `PENDING_APPROVAL`
- `APPROVED`
- `REJECTED`
- `CANCELLED`
- `EXPIRED`
- `DISPOSED`

### 3.2 Lifecycle rules

- creating an exception does not mean it is approved
- approved exception becomes `DISPOSED` only after the intended business effect is consumed or explicitly finalized
- rejected / cancelled / expired / disposed exceptions remain immutable except for audit annotations

---

## 4. Approval bands

Canonical v1 approval bands:

- `BAND_1_SUPERVISORY`
- `BAND_2_QUALITY`
- `BAND_3_CONTROLLED_SUPPORT`

These bands classify ownership and governance, not UI labels.

---

## 5. Canonical exception type catalog

- `SHORT_CLOSE_REQUEST`
- `OVERRUN_REQUEST`
- `FORCE_COMPLETE_REQUEST`
- `REOPEN_OPERATION_REQUEST`
- `FORCE_RESUME_REQUEST`
- `BLOCK_OVERRIDE_REQUEST`
- `QC_DEVIATION_ACCEPT_REQUEST`
- `QC_HOLD_RELEASE_REQUEST`
- `QC_RECHECK_REQUEST`
- `SCRAP_DISPOSITION_REQUEST`
- `SUPPORT_INTERVENTION_REQUEST`
- `BACKDATED_EVENT_REQUEST`

---

## 6. Canonical decision model

### 6.1 Canonical decision command

- `record_disposition_decision`

### 6.2 Canonical decision event

- `disposition_decision_recorded`

### 6.3 Decision outcome enum

- `APPROVED`
- `REJECTED`

### 6.4 Canonical disposition codes

- `ALLOW_SHORT_CLOSE`
- `ALLOW_OVERRUN`
- `ALLOW_FORCE_COMPLETE`
- `ALLOW_REOPEN`
- `ALLOW_FORCE_RESUME`
- `ALLOW_BLOCK_OVERRIDE`
- `RELEASE_QC_HOLD`
- `ACCEPT_WITH_DEVIATION`
- `REQUIRE_RECHECK`
- `CONFIRM_SCRAP`

Notes:

- `disposition_code` is required when approving
- backend derives any machine-usable `approved_effects` from this code and the exception type
- `approved_effects` is not client-owned input

---

## 7. Canonical matrix

| Exception type | Typical raised by | Required approver | Approval band | SoD required | Typical evidence | Canonical approval effect |
|---|---|---|---|---|---|---|
| `SHORT_CLOSE_REQUEST` | OPR, SUP | SUP | `BAND_1_SUPERVISORY` | Yes | expected qty, remaining qty, reason | `ALLOW_SHORT_CLOSE` |
| `OVERRUN_REQUEST` | OPR, SUP | SUP | `BAND_1_SUPERVISORY` | Yes | overrun amount, reason | `ALLOW_OVERRUN` |
| `FORCE_COMPLETE_REQUEST` | SUP | SUP | `BAND_1_SUPERVISORY` | Yes | unresolved condition summary | `ALLOW_FORCE_COMPLETE` |
| `REOPEN_OPERATION_REQUEST` | SUP, QCI/QAL | SUP for execution-owned case; QCI/QAL for quality-owned case | `BAND_1_SUPERVISORY` or `BAND_2_QUALITY` | Yes | reopen reason, downstream check | `ALLOW_REOPEN` |
| `FORCE_RESUME_REQUEST` | SUP | SUP | `BAND_1_SUPERVISORY` | Yes | block summary, mitigation | `ALLOW_FORCE_RESUME` |
| `BLOCK_OVERRIDE_REQUEST` | SUP | SUP | `BAND_1_SUPERVISORY` | Yes | override reason | `ALLOW_BLOCK_OVERRIDE` |
| `QC_DEVIATION_ACCEPT_REQUEST` | QCI/QAL, SUP | QCI/QAL | `BAND_2_QUALITY` | Yes | QC result, spec breach, rationale | `ACCEPT_WITH_DEVIATION` |
| `QC_HOLD_RELEASE_REQUEST` | QCI/QAL, SUP | QCI/QAL | `BAND_2_QUALITY` | Yes | hold reason, review result | `RELEASE_QC_HOLD` |
| `QC_RECHECK_REQUEST` | OPR, SUP, QCI/QAL | QCI/QAL | `BAND_2_QUALITY` | Yes | failed sample context | `REQUIRE_RECHECK` |
| `SCRAP_DISPOSITION_REQUEST` | OPR, SUP, QCI/QAL | QCI/QAL when quality-owned; SUP only if policy marks purely operational scrap threshold | `BAND_2_QUALITY` or `BAND_1_SUPERVISORY` | Yes | qty, reason, threshold context | `CONFIRM_SCRAP` |
| `SUPPORT_INTERVENTION_REQUEST` | ADM, OTS | configured support approver under policy | `BAND_3_CONTROLLED_SUPPORT` | Yes | incident id, justification, impact | support-controlled effect only |
| `BACKDATED_EVENT_REQUEST` | SUP, QCI/QAL, ADM/OTS under policy | configured support / governance approver | `BAND_3_CONTROLLED_SUPPORT` | Yes | true occurrence time, reason, audit note | controlled backdated effect |

---

## 8. Unlock rules

Approved exception may unlock only the effect mapped to its approved disposition.

### 8.1 Operational unlock examples

- `ALLOW_SHORT_CLOSE` may unlock `complete_execution` below normal quantity expectation
- `ALLOW_OVERRUN` may unlock overrun reporting and/or completion within approved bounds
- `ALLOW_FORCE_COMPLETE` may unlock `complete_execution` despite selected operational condition
- `ALLOW_REOPEN` may unlock `reopen_operation`
- `ALLOW_FORCE_RESUME` may unlock `resume_execution` from blocked state
- `ALLOW_BLOCK_OVERRIDE` may unlock `resume_execution` or other block-clearing behavior according to policy

### 8.2 Quality unlock examples

- `RELEASE_QC_HOLD` may clear quality hold and allow later resume / completion if no other blocker remains
- `ACCEPT_WITH_DEVIATION` may permit accepted-good progression according to policy
- `REQUIRE_RECHECK` may route the context into recheck path; it does not directly unlock normal completion unless policy later says so
- `CONFIRM_SCRAP` may finalize scrap outcome and allow closure if all other rules pass

---

## 9. SoD and evidence rules

### EX-SOD-001
Requester must not be the same as approver where policy marks SoD required.

### EX-SOD-002
Support actor must not self-approve support intervention.

### EX-EVD-001
Approval must be rejected when mandatory evidence is missing.

### EX-EVD-002
Evidence requirements are policy-driven but must be auditable at decision time.

---

## 10. Backend expectations

1. Exception domain ownership comes from exception type and policy.
2. Backend derives `approved_effects` from approved disposition; client does not submit authoritative effect flags.
3. Approved effects should be consumable and auditable.
4. Rejected exception keeps review history; it must not erase the original request.

---

## 11. Explicit exclusions in canonical v1

The following are intentionally excluded from the default station execution approval path:

- `PMG` as normal station execution approver
- `EXE` as normal station execution approver
- separate canonical command names such as `record_supervisor_decision` or `record_quality_disposition`
- optional decision outcome such as `REQUEST_MORE_INFORMATION` as part of the canonical v1 contract

If a future phase introduces these, it must do so as an explicit versioned extension.

