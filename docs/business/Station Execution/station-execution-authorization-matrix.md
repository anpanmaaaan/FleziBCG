# Station Execution Authorization Matrix (Canonical v1)

Status: Authoritative authorization policy for station execution  
Owner: Product / Security / Backend  
Depends on: `business-truth-station-execution.md`, `station-execution-state-matrix.md`, `station-execution-command-event-contracts.md`

---

## 1. Purpose

This document defines who may perform which station execution commands in canonical v1.

It is backend authorization truth for:

- command ownership
- scope expectations
- role boundaries
- quality-owned versus operational-owned decision paths
- support / impersonation restrictions

---

## 2. Authorization principles

### AUTH-001 — Backend-first authorization
All command authorization is enforced on backend per command and per scope.

### AUTH-002 — Persona does not imply write permission
Seeing a screen or reading a projection does not imply command rights.

### AUTH-003 — Quality-owned decisions are separate from operational-owned decisions
- operational disposition decisions are normally owned by `SUP`
- quality-owned disposition decisions are normally owned by `QCI/QAL`

### AUTH-004 — Support/admin are not normal production actors
`ADM` and `OTS` may act only through controlled support mode where policy allows.

### AUTH-005 — Broader business roles are out of scope here
`PMG` and `EXE` are not part of the canonical station execution write / approval path in v1 and are therefore excluded from the matrix below.

---

## 3. Roles in scope for this matrix

- `OPR`
- `SUP`
- `QCI/QAL`
- `IEP`
- `ADM`
- `OTS`

Legend:

- `A` = allowed as normal owner
- `C` = conditionally allowed under policy
- `S` = support-mode only
- `N` = not allowed

---

## 4. Scope rules

### 4.1 OPR scope
Normal write scope is same station only.

### 4.2 SUP scope
Normal write/decision scope is same station or parent line / area according to assignment.

### 4.3 QCI/QAL scope
Normal quality decision scope is same plant / quality scope according to assignment.

### 4.4 IEP scope
Diagnostic visibility only in canonical v1, unless a future policy explicitly adds a write path.

### 4.5 ADM / OTS scope
Controlled support only, audited and policy-gated.

---

## 5. Matrix

## 5.1 Station session and execution commands

| Command | OPR | SUP | QCI/QAL | IEP | ADM | OTS |
|---|---|---|---|---|---|---|
| `open_station_session` | A | C | N | N | S | S |
| `close_station_session` | A | C | N | N | S | S |
| `claim_operation` | A | C | N | N | S | S |
| `start_execution` | A | C | N | N | S | S |
| `pause_execution` | A | C | N | N | S | S |
| `resume_execution` | A | C | N | N | S | S |
| `report_production` | A | C | N | N | S | S |
| `start_downtime` | A | C | N | N | S | S |
| `end_downtime` | A | C | N | N | S | S |
| `submit_qc_measurement` | A | C | C | N | S | S |
| `complete_execution` | A | C | N | N | S | S |
| `close_operation` | N | C | C | N | S | S |
| `reopen_operation` | N | A | C | N | S | S |

### Notes

- `SUP` may execute selected station commands conditionally for recovery or oversight, but is not intended to behave as the default operator.
- `QCI/QAL` may participate in `submit_qc_measurement` or `close_operation` only when a quality-owned policy explicitly requires their role in the flow.

---

## 5.2 Exception and decision commands

| Command | OPR | SUP | QCI/QAL | IEP | ADM | OTS |
|---|---|---|---|---|---|---|
| `raise_exception` | C | A | A | C | S | S |
| `record_disposition_decision` | N | A (operational-owned only) | A (quality-owned only) | N | S | S |

### Notes

- `OPR` may raise only exception types allowed by policy.
- `IEP` may raise only selected diagnostic / engineering-triggered exceptions if policy enables it.
- `SUP` does **not** own quality disposition by default in canonical v1.
- `QCI/QAL` do **not** own normal operational approvals such as short close by default.

---

## 6. Command-specific conditional rules

### AUTH-CMD-001 — `resume_execution`

`resume_execution` is allowed only when both authorization and state/policy checks pass. Authorization alone never bypasses quality hold or pending decision.

### AUTH-CMD-002 — `complete_execution`

`complete_execution` may require a consumable approved effect, but the actor still needs command authorization.

### AUTH-CMD-003 — `record_disposition_decision`

Backend must validate:

- actor role ownership for the target exception type
- actor scope
- SoD constraints
- support-mode requirements where relevant

### AUTH-CMD-004 — `reopen_operation`

`reopen_operation` is exceptional and must validate actor authorization plus downstream dependency and approval rules.

---

## 7. Exception domain ownership mapping

### 7.1 Operational-owned exception types
Normally decided by `SUP`:

- `SHORT_CLOSE_REQUEST`
- `OVERRUN_REQUEST`
- `FORCE_COMPLETE_REQUEST`
- `REOPEN_OPERATION_REQUEST` when purely execution-owned
- `FORCE_RESUME_REQUEST`
- `BLOCK_OVERRIDE_REQUEST`

### 7.2 Quality-owned exception types
Normally decided by `QCI/QAL`:

- `QC_DEVIATION_ACCEPT_REQUEST`
- `QC_HOLD_RELEASE_REQUEST`
- `QC_RECHECK_REQUEST`
- `SCRAP_DISPOSITION_REQUEST` when quality-owned by policy

### 7.3 Controlled-support exception types
Support-mode only:

- `SUPPORT_INTERVENTION_REQUEST`
- `BACKDATED_EVENT_REQUEST`

---

## 8. SoD rules

### AUTH-SOD-001
Requester must not equal approver when SoD is required by policy.

### AUTH-SOD-002
Support-mode actor must not self-approve their own intervention request.

### AUTH-SOD-003
A role technically capable of approval may still be blocked by SoD or scope mismatch.

---

## 9. Support / impersonation rules

### AUTH-SUP-001
`ADM` and `OTS` cannot act as normal floor operators.

### AUTH-SUP-002
If support mode permits a command, the resulting events must include support-mode audit metadata.

### AUTH-SUP-003
Support mode must never be used to evade SoD or quality ownership rules.

---

## 10. Read-access guidance

This matrix governs write and approval rights. Read access is defined separately and may be broader.

In canonical v1:

- `OPR`, `SUP`, `QCI/QAL`, and `IEP` may have read access according to scope
- `ADM` and `OTS` may have support/debug visibility according to governance policy
- `PMG` and `EXE` may have broad read visibility outside this write matrix

