# Business Truth — Station Execution (Canonical v1)

## Document purpose

This document defines the authoritative business truth for the **Station Execution** domain of the AI-driven MOM / MES platform.

It is a domain truth document, not a UI spec and not an API handbook. Its purpose is to make backend, frontend, QA, and operations teams use the same execution model.

This document is canonical for:

- station-level execution lifecycle
- execution truth boundaries
- state dimensions and derived status intent
- operator, supervisor, and quality intervention boundaries
- quantity, downtime, hold, and disposition logic
- what must exist now versus what is intentionally deferred

---

## 1. Scope

### 1.1 In scope

This document covers execution logic at station level:

- station session opening and closing
- operation claim and execution within a station context
- start, pause, resume, and complete execution
- quantity reporting
- downtime and reason handling
- station-side QC measurement submission
- backend QC evaluation and quality hold behavior
- exception raising and disposition decision flow
- station-level close and reopen rules
- station and supervisory read-model expectations

### 1.2 Out of scope

The following are out of scope for this document or only referenced at boundary level:

- work order and routing orchestration logic
- dispatch and release ownership as orchestration commands
- detailed material consumption
- full traceability / genealogy
- maintenance workflow
- APS / scheduling optimization
- digital twin simulation
- AI actions that mutate execution truth
- advanced rework routing and laboratory quality processes

---

## 2. Foundational principles

### BT-CORE-001 — Backend is the source of truth

The frontend never decides execution truth, authorization truth, or QC disposition truth. The frontend sends commands and renders backend-derived projections.

### BT-CORE-002 — Execution truth is event history

Important execution facts are stored as immutable business events with actor, timestamp, target, and business context.

### BT-CORE-003 — Status is derived

Execution, quality, review, and closure status are derived from event history and policy. Users do not directly edit status fields.

### BT-CORE-004 — Persona is not permission

A role name or screen visibility does not imply write permission. Backend authorization is checked per command, per scope.

### BT-CORE-005 — AI is advisory only

AI may observe, explain, summarize, predict, or recommend. AI must not silently start, pause, resume, complete, close, reopen, or disposition execution truth.

### BT-CORE-006 — Corrections must stay auditable

Execution truth must not be silently overwritten. In v1, corrections happen through controlled exception / disposition / reopen paths, not free-form destructive edits.

---

## 3. Business terminology

### 3.1 Station
A physical or logical execution point where an operator performs work and where station execution commands are issued.

### 3.2 Work Order (WO)
A production order that defines the wider manufacturing demand context.

### 3.3 Operation (OP)
A defined execution step within a routing or process sequence, typically performed at a compatible station.

### 3.4 Station Session
An active runtime session binding an operator to a station context.

### 3.5 Operation Execution Context
The runtime execution aggregate for one operation at one station.

### 3.6 Execution Event
An immutable business event such as start, pause, report quantity, downtime start, or completion.

### 3.7 Quality Hold
A quality-owned restriction that prevents normal progression until an authorized decision has been recorded.

### 3.8 Exception
A non-standard situation that requires explicit review and possible approval before selected commands may proceed.

### 3.9 Disposition decision
The backend-recorded decision for a pending operational or quality review. In canonical v1, the command name is **`record_disposition_decision`** and the event name is **`disposition_decision_recorded`**.

---

## 4. Primary aggregate and truth boundary

### BT-AGG-001 — Primary aggregate

The primary aggregate for this domain is:

**Operation Execution Context at a Station**

It is identified by business context including tenant, plant scope, station, work order, operation, and execution instance.

### BT-AGG-002 — Projection is not truth

Station screen, dashboard, Gantt, and operation detail screens render projections derived from execution truth. Projections are not the authority for command validation.

### BT-AGG-003 — Orchestration boundary

Dispatch and release are orchestration-owned concepts. Station execution consumes orchestration outcomes as preconditions and state inputs, but station actors do not own orchestration commands.

---

## 5. Role intent in station execution

### 5.1 OPR — Operator

Primary station actor.

Normally allowed to:

- open and close station session
- claim work already made available to the station
- start, pause, and resume execution
- report production quantity
- start and end downtime within policy
- submit QC measurements
- complete execution when no blocking rule exists
- raise selected exceptions

Normally not allowed to:

- record final disposition decisions
- release quality hold by authority
- reopen a closed execution record
- approve their own exception path

### 5.2 SUP — Supervisor

Operational oversight role with controlled intervention.

Normally allowed to:

- monitor multiple stations
- raise and decide operational exceptions within policy
- approve short close / overrun / force complete / selected reopen cases
- reopen a closed execution record in allowed execution-owned cases
- consume approved operational decisions where policy allows

Normally not allowed to:

- act as the default quality approver
- bypass SoD rules
- perform unrestricted production manipulation

### 5.3 QCI / QAL — Quality roles

Quality-owned decision makers.

Normally allowed to:

- review QC failures
- record quality-owned disposition decisions
- release or maintain quality hold according to policy
- determine selected deviation / recheck / scrap outcomes

### 5.4 IEP — Engineering / industrial engineering role

May hold diagnostic and analytical visibility. In v1 station execution, IEP is not a default execution writer and not a default disposition approver.

### 5.5 ADM / OTS — Admin / support roles

Not default production actors. If they affect production truth, it must be through controlled support or impersonation mode with full audit and policy checks.

### 5.6 PMG / EXE in station execution v1

Broader business roles may exist at platform level, but they are out of the station execution write and approval path in canonical v1. Their visibility or escalation behavior is defined outside this implementation pack.

---

## 6. State dimensions

Station execution uses multiple state dimensions rather than one giant enum.

### 6.1 Dispatch status
Represents whether orchestration has made the operation available to this station.

Possible values:

- `NOT_DISPATCHED`
- `DISPATCHED`
- `CLAIMED`
- `RELEASED_TO_EXECUTE`

Note: dispatch and release are orchestration-owned transitions, but these statuses are visible as station-execution preconditions.

### 6.2 Execution status
Represents active execution runtime.

Possible values:

- `NOT_STARTED`
- `RUNNING`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`

### 6.3 Quality status
Represents quality requirement and current QC outcome.

Possible values:

- `QC_NOT_REQUIRED`
- `QC_PENDING`
- `QC_PASSED`
- `QC_FAILED`
- `QC_HOLD`

### 6.4 Review status
Represents whether the execution context is waiting for an explicit decision.

Possible values:

- `NO_REVIEW`
- `REVIEW_REQUIRED`
- `DECISION_PENDING`
- `DISPOSITION_DONE`

### 6.5 Closure status
Represents whether the business record is open for normal execution actions.

Possible values:

- `OPEN`
- `CLOSED`

Important: reopen is **not** a closure status. Reopen is represented by an event plus reopen metadata such as `reopen_count`, `last_reopened_at`, and `last_reopened_by`.

Implementation note (incremental orthogonalization):

- `closure_status` is implemented as a separate persisted dimension in backend operation records
- canonical invariant is enforced: `CLOSED` records reject execution write commands
- `close_operation` and `reopen_operation` command foundations are implemented
- current reopen effect is an interim controlled non-running reopened state (`PAUSED` projection)
- fuller close/reopen policy gates that depend on `quality_status` / `review_status` remain deferred

---

## 7. Station session business truth

### BT-SS-001 — Open station session

A station session may be opened only when:

- the user is authenticated
- the user is authorized for station scope
- the station is active and not administratively disabled
- station exclusivity policy allows the session

Event:
- `station_session_opened`

### BT-SS-002 — Close station session

A station session may be closed only when station policy allows safe exit.

In v1, close should be rejected when:

- a running execution still exists in that session context
- a mandatory unresolved hold prevents exit per policy
- an open downtime tied to the active execution would be orphaned

Event:
- `station_session_closed`

### BT-SS-003 — One running execution per station (v1)

Canonical v1 assumes one active running execution at a station at a time, unless a future policy explicitly enables multi-slot or multi-lane execution.

---

## 8. Core execution lifecycle

### BT-EX-001 — Claim is station-owned

Claim means the station actor selects work already made available by orchestration.

Event:
- `operation_claimed`

### BT-EX-002 — Start execution

Execution may start only when:

- the operation is claimed or otherwise eligible to start in station context
- a valid station session exists
- no hard hold blocks start
- no open downtime already exists for that execution context
- pre-start gates, if configured, pass

Event:
- `execution_started`

### BT-EX-003 — Pause execution

Pause is a station-runtime interruption that does not by itself classify root cause as downtime.

Event:
- `execution_paused`

### BT-EX-004 — Resume execution

Resume is allowed only when:

- no open downtime remains
- no quality hold blocks progress
- no pending disposition blocks progress
- no other hard block remains unresolved
- station concurrency rule still passes

Event:
- `execution_resumed`

### BT-EX-005 — Blocked is derived

`BLOCKED` is not a user-entered free state. It is derived when hard conditions exist, for example:

- quality hold requires stop
- approved policy maps a review state to hard block
- operational block policy is active

### BT-EX-006 — Complete execution

Completion means execution work at the station is finished.

Completion is allowed only when:

- execution has started
- no open downtime remains
- no mandatory QC is still pending
- no hard quality hold remains
- no required disposition decision remains pending
- quantity completion rule is satisfied or a valid approved exception exists

Event:
- `execution_completed`

### BT-EX-007 — Close operation at station

Close is a post-execution business closure step. `COMPLETED` and `CLOSED` are not the same.

Close is allowed only when:

- execution is completed
- no unresolved review remains
- no unresolved QC requirement remains
- minimum audit and evidence requirements are satisfied

Event:
- `operation_closed_at_station`

### BT-EX-008 — Reopen operation at station

Reopen is an exceptional action.

Reopen is allowed only when:

- closure status is `CLOSED`
- an authorized actor performs the action
- reopen reason is present
- downstream dependency / consumption checks pass
- approval exists where policy requires it

Event:
- `operation_reopened`

Effect:
- closure status becomes `OPEN`
- execution status becomes a controlled non-running state, typically `PAUSED`
- reopen metadata is incremented and stamped

---

## 9. Quantity truth

### BT-QTY-001 — Quantity is event-driven and reported as delta

Station quantity is reported by delta events, not by overwriting running totals.

### BT-QTY-002 — Good and NG are distinct

Good quantity and non-good quantity are recorded separately.

### BT-QTY-003 — Accepted good is not the same as reported good

Canonical v1 distinguishes:

- `reported_good_qty`
- `reported_ng_qty`
- `accepted_good_qty`

`accepted_good_qty` is derived server-side according to quality and disposition policy.

### BT-QTY-004 — Negative free-form correction is not allowed in v1

Canonical v1 does not allow arbitrary negative corrective quantity events from station UI.

If quantity requires controlled correction, the path is:

- raise exception
- record disposition decision if required
- reopen if policy requires a reopened execution context
- then record valid forward-going events under controlled flow

### BT-QTY-005 — Overrun and short close are policy-controlled

Quantity outside normal completion expectation must not be silently accepted. It must either be blocked or unlocked by approved exception and policy.

---

## 10. Downtime truth

### BT-DT-001 — Downtime is an interval event pair

Downtime is represented by explicit start and end events, not by a manually edited duration field.

Events:
- `downtime_started`
- `downtime_ended`

### BT-DT-002 — Downtime requires reason classification

A valid reason code must be associated according to downtime policy.

### BT-DT-003 — Open downtime blocks selected progression

In v1, an open downtime prevents:

- `resume_execution`
- `complete_execution`
- station session close when orphaning would occur

### BT-DT-004 — Pause and downtime are not the same

Pause means runtime interruption. Downtime means classified loss interval. Policy may require a paused execution to be converted into downtime after threshold.

---

## 11. Quality truth

### BT-QC-001 — Station UI submits measurements, not truth disposition

The station UI submits QC measurements or observation payloads. The frontend must not be the authority for final pass/fail/deviation/release decisions.

### BT-QC-002 — Backend evaluates QC result

Backend applies configured QC policy and records result events.

Events:
- `qc_measurement_submitted`
- `qc_result_recorded`

### BT-QC-003 — QC fail may create quality hold

If configured policy requires hold or review, backend creates the hold state and associated review requirement.

Event:
- `qc_hold_applied`

### BT-QC-004 — Quality hold release is quality-owned in v1

Canonical v1 does not use a separate business command such as `release_qc_hold` as the primary decision command.

Quality hold release, deviation acceptance, recheck confirmation, and related outcomes are recorded through the canonical command:

- `record_disposition_decision`

The resulting event is:

- `disposition_decision_recorded`

A separate event such as `qc_hold_released` may still be emitted or derived if implementation chooses, but it is not the canonical decision command boundary.

### BT-QC-005 — Quality disposition owner

In canonical v1, final quality-owned disposition is performed by `QCI/QAL`, not by `SUP` as default owner.

---

## 12. Review and disposition truth

### BT-RV-001 — Review states indicate decision need, not actor identity

`DECISION_PENDING` means the execution context awaits an authorized decision. It does not imply the decision must belong to supervisor specifically.

### BT-RV-002 — Canonical decision command

Canonical v1 uses one decision command:

- `record_disposition_decision`

This command is used for both:

- operational exception decisions
- quality-owned disposition decisions

Ownership and authorization depend on exception type and policy, not on different command names.

### BT-RV-003 — Canonical decision event

The canonical decision event is:

- `disposition_decision_recorded`

### BT-RV-004 — Decision input model

Canonical decision input contains:

- `decision_outcome`
  - `APPROVED`
  - `REJECTED`
- `disposition_code`
  - required when `decision_outcome = APPROVED`

`approved_effects` is **not** a client-owned input in canonical v1. If used, it is derived server-side in event payload or projections.

### BT-RV-005 — Requester must not equal approver

When SoD is required, the requester and the decision actor must not be the same person.

---

## 13. Exception truth

### BT-EXC-001 — Exception is a first-class business object

An exception is not only a UI badge or comment. It must exist as an explicit backend record.

### BT-EXC-002 — Canonical station execution exception types in v1

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

### BT-EXC-003 — Approval unlocks a defined business effect

An approved exception must unlock a specific backend-checked business effect, such as:

- allow short close
- allow overrun
- allow force complete
- allow reopen
- allow force resume
- allow block override
- release quality hold
- accept with deviation
- require recheck
- confirm scrap disposition

---

## 14. Authorization truth

### BT-AUTH-001 — Backend-first authorization

All write commands are authorized on backend per command and per scope.

### BT-AUTH-002 — Station execution write path in canonical v1

Canonical v1 station execution write / approval path is limited to:

- `OPR`
- `SUP`
- `QCI/QAL`
- `ADM/OTS` only under controlled support mode where policy allows

`PMG` and `EXE` are not part of the normal station execution write or approval path in v1.

### BT-AUTH-003 — Quality-owned versus operational-owned decisions

- Operational exceptions are normally decided by `SUP`.
- Quality-owned decisions are normally decided by `QCI/QAL`.
- Support/admin intervention uses separate controlled support policy.

---

## 15. Read-model expectations

Station and supervisory projections should expose at least:

- station session context
- active work order and operation
- dispatch status
- execution status
- quality status
- review status
- closure status
- reported good / NG quantity
- accepted good quantity
- remaining quantity
- current downtime status
- exception summary
- last event timestamp
- allowed actions derived by backend
- reopen metadata if applicable

Backend should derive `allowed_actions`; frontend should not guess business-valid actions on its own.

---

## 16. Must exist now versus later

### 16.1 Must exist now

Canonical v1 requires at least:

- station session
- claim / start / pause / resume / report / complete / close / reopen
- downtime start / end with reason
- QC measurement submission and backend QC result evaluation
- exception raising
- canonical disposition decision flow
- role/scope authorization
- auditability
- policy-driven accepted-good derivation

### 16.2 Design now, implement later

- multi-slot station execution
- advanced rework loops
- rich genealogy
- machine-triggered automated commands
- advanced delegated approval patterns
- broader escalation roles inside execution write path

### 16.3 Can wait

- AI action layers
- full digital twin behavior
- APS-lite orchestration optimization
- advanced maintenance integration

---

## 17. Canonical vocabulary summary

The following names are canonical in station execution v1 and should be used consistently across implementation documents:

- review pending state: `DECISION_PENDING`
- closure states: `OPEN`, `CLOSED`
- reopen representation: `operation_reopened` event plus reopen metadata
- decision command: `record_disposition_decision`
- decision event: `disposition_decision_recorded`
- decision input: `decision_outcome`, `disposition_code`
- no client-owned `approved_effects`
- no separate canonical decision commands named `record_supervisor_decision`, `record_quality_disposition`, or `release_qc_hold`

