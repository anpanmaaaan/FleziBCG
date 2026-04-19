# Station Execution Operational SOP

Status: Authoritative operating procedure (v1)  
Owner: Product / Domain / Operations  
Primary consumers: Operators, Supervisors, Quality, Training, QA, Product, Backend, Frontend  
Scope: Shopfloor station execution only  
Depends on:
- `business-truth-station-execution.md`
- `station-execution-state-matrix.md`
- `station-execution-command-event-contracts.md`
- `station-execution-authorization-matrix.md`
- `station-execution-exception-and-approval-matrix.md`

---

# 1. Purpose

This document converts the station execution business truth into an **operator-facing and supervisor-facing standard operating procedure**.

It defines:

- how an operator should use the station screen during normal production
- how to react to pause, downtime, quality failure, and abnormal production conditions
- when a supervisor must intervene
- what must be recorded in the system versus what may remain only verbal or physical on shopfloor
- what actions are forbidden even if a user can physically access the screen

This file is intentionally written from an **operational behavior** viewpoint.  
It is not a screen mockup and not a transport/API document.

---

# 2. Audience and role intent

## 2.1 Roles in scope

| Role | Main purpose in this SOP |
|---|---|
| `OPR` | Execute assigned work at station, report quantities, report basic downtime, submit QC measurements |
| `SUP` | Monitor operations, resolve exceptions, approve exceptional actions, support shift continuity |
| `QCI` / `QAL` | Review quality failures, apply/release QC hold, record quality disposition |
| `ADM` / `OTS` | Not normal shopfloor actors; only act via controlled support flow when explicitly allowed |

## 2.2 Principle of use

The station screen is primarily an **operator execution tool**.

Supervisor and quality roles may use the screen or related operation detail views only for:

- monitoring
- review
- exception handling
- controlled correction through explicit business flow

The screen must not be used as a shortcut to bypass workflow, audit, or approval.

---

# 3. Core operating principles

## SOP-CORE-001 — The system records truth through actions, not through manual status editing

Users must not try to “fix” production by changing labels or asking IT to directly edit status fields.

Valid system truth comes from accepted business actions such as:

- open session
- claim operation
- start execution
- report quantity
- start/end downtime
- submit QC measurement
- complete execution
- raise exception
- approve/reject exception

## SOP-CORE-002 — If an event matters operationally, it must be recorded in the system

Examples:

- machine stopped for a real reason
- quantity produced
- QC failed
- operator cannot complete due to shortage or defect
- work handed over across shift

If these events are only communicated verbally, the MOM/MES timeline becomes unreliable.

## SOP-CORE-003 — Never use another person’s identity

Each user must act under their own authenticated identity.

Operators must not:

- use another operator’s session
- ask supervisors to “just click it” without proper review
- share login credentials

## SOP-CORE-004 — Supervisor involvement is required for exception, not for routine execution

Normal flow should stay operator-driven.

Supervisor intervention is required only when the process enters an approved exception path, such as:

- underproduction / short close
- quality hold
- overrun tolerance breach
- reopen after completion or closure
- hard block requiring override

---

# 4. Operating prerequisites before production starts

## 4.1 Shift readiness checks outside and inside the system

Before production starts, the operator must ensure that:

1. the correct station is being used
2. the user is logged in under the correct identity
3. the station is physically available and not under maintenance lock
4. the operation shown in the queue matches the intended job on the floor
5. required materials / tools / fixtures / documents are available according to local operating practice

### Note
In v1, not all of the above may be system-enforced.  
Even where the system does not yet hard-stop execution, local operating discipline still applies.

## 4.2 Open station session

The operator begins by opening a **station session**.

### Expected behavior
- select the correct station
- confirm that no conflicting active session exists if the station is exclusive-use
- verify that the system shows the correct queue and active shift context

### Do not proceed if
- the screen shows the wrong station
- the station appears inactive / blocked / out of service
- another user is incorrectly occupying the station
- the current operation queue clearly does not match shopfloor reality

### Required action if mismatch exists
- stop before starting production
- notify supervisor or designated line lead
- do not “work first and correct in system later” except under an approved downtime / back-entry policy

---

# 5. Normal operator workflow

## 5.1 Select and claim the next operation

The operator chooses the next valid operation from the station queue.

### Operator should verify
- the work order / operation on screen matches the physical job
- the station is the intended station for this step
- the previous step has been completed or released upstream
- there is no visible unresolved hold

### When to stop and escalate
- the wrong work order appears at the station
- a job is physically present but not visible in queue
- the system shows a hold or block that the operator cannot explain
- the same job appears to be active in another station unexpectedly

## 5.2 Start execution

Once the correct operation is claimed and the station is ready, the operator starts execution.

### Operational meaning
Starting execution means the station has begun real processing of the selected operation.

### Do not start if
- the job is not actually beginning
- the machine is still not ready
- the operator is only “reserving” the job for later
- mandatory local preconditions are not met

### Why this matters
False start events distort:

- runtime
- availability
- labor traceability
- operation lead time
- delay and bottleneck analytics

## 5.3 Report production during execution

Quantities must be reported as **actual deltas** when production occurs.

### Operator should report
- good quantity produced
- NG quantity produced
- defect reason when NG exists
- remark when required by local policy

### Good practice
Report close to the real event, not hours later from memory.

### Forbidden behavior
- entering estimated quantity just to keep the dashboard moving
- reporting all quantity at the end if intermediate reporting is operationally required
- hiding NG by adding it into good quantity
- entering quantity on behalf of another station

## 5.4 Pause execution for short interruptions

A short interruption may be handled as a pause when allowed by local policy and when the stop has not yet become a classified downtime.

### Examples
- quick cleaning
- short operator check
- minor reset
- waiting a very brief moment for continuation

### Important
If the interruption exceeds the configured threshold or is clearly caused by a production-affecting reason, the user must classify it as downtime instead of leaving it as an unqualified pause.

## 5.5 Resume execution

Resume only when the real production condition has resumed.

Do not resume if:

- a hard block still exists
- QC hold is still active
- the root reason of downtime is still open
- production is not actually restarting

## 5.6 Complete execution

Complete only when the station work for that operation is genuinely finished.

### Before completing, the operator should confirm
- all relevant quantity has been reported
- any real downtime has been closed
- mandatory QC submission has been done if required
- no unresolved hold remains
- the operation is not waiting on supervisor approval for an exception

### Do not complete if
- product is still being processed
- quantity is still uncertain
- QC is pending and mandatory
- there is known underproduction without approved exception
- there is known overrun beyond allowed tolerance without approval

## 5.7 Close station session

At the end of station use or shift responsibility, the operator closes the station session.

### A session must not be closed if
- execution is still running
- downtime is open
- quality action is left pending under the same user responsibility without proper handover
- the station is being abandoned without shift handover

---

# 6. Downtime operating procedure

## 6.1 When downtime must be recorded

Downtime must be recorded when the station stops for a meaningful production reason that affects runtime, output, or normal flow.

### Typical examples
- machine fault
- tooling issue
- material shortage
- upstream starvation / downstream blockage
- quality stop
- waiting for maintenance or supervisor
- utility problem

## 6.2 Downtime start procedure

When the stop becomes a real production interruption, the operator should:

1. pause execution if needed by screen flow
2. start downtime
3. choose the best available reason code
4. add comment if policy requires clarification
5. notify supervisor if the reason or duration exceeds local thresholds

## 6.3 Reason code discipline

Choose the **most accurate available reason**, not the easiest one.

### Forbidden behavior
- always choosing “Other” for speed
- hiding quality issues under generic waiting
- using a fake reason because the real reason seems embarrassing

### If the correct reason is not available
- choose the temporary fallback allowed by local policy
- add a comment
- notify supervisor / process owner so the master data can be corrected later

## 6.4 Downtime end procedure

End downtime when the reason causing the stop has genuinely been resolved.

Do not end downtime merely because:

- a supervisor asked to make the screen look better
- the team wants the dashboard to show green
- production is still not actually resumed

## 6.5 Long downtime escalation

If downtime passes the configured threshold for escalation:

- supervisor must be notified
- if relevant, maintenance or quality must be involved
- the operator should not repeatedly close and reopen downtime just to reduce measured duration

---

# 7. Quality operating procedure

## 7.1 Station users submit measurements, not final pass/fail truth

When the system requires QC input from the station, the operator enters the measured values or requested inspection data.

The system/backend evaluates the result according to configured quality rules.

### Operator must not
- guess measurements
- enter values without actual check if the check is required
- change values to force a pass
- ask another person to submit measurements under the wrong identity

## 7.2 What to do when QC passes

If QC passes:

- continue according to normal operation flow
- report quantities truthfully
- complete only when the rest of the execution conditions are satisfied

## 7.3 What to do when QC fails

If QC fails and a hold is applied:

1. stop treating the lot/operation as normal flow
2. do not continue as if the failure did not happen
3. isolate the physical situation according to local shopfloor practice
4. notify supervisor and/or quality role
5. wait for quality disposition or supervisor-approved path

### Operator must not
- force completion
- continue hidden processing under the same operation as if QC passed
- manually reinterpret failed output as good quantity
- ask IT or support to “remove hold quickly” without recorded decision

## 7.4 Quality disposition ownership

Disposition of QC failure belongs to the proper authority, typically:

- `QCI`
- `QAL`
- `SUP` only where policy explicitly allows

Possible dispositions may include:

- accept under deviation
- require recheck
- scrap / reject
- route to rework flow
- quarantine / hold

### v1 note
Where the system does not yet support the full advanced flow, the recorded disposition must still be explicit and auditable.

---

# 8. Exception and approval operating procedure

## 8.1 What counts as an exception

An exception is any case where normal operator flow cannot legally continue without additional approval or disposition.

### Typical examples
- short close / underproduction
- overrun above tolerance
- QC deviation acceptance
- resume after hard block
- reopen after close
- forced correction after major reporting mistake

## 8.2 Operator behavior when exception is needed

The operator must:

1. stop the normal flow at the correct point
2. raise or request the appropriate exception path
3. provide factual explanation and evidence if required
4. wait for disposition

The operator must not:

- invent missing quantity to avoid exception
- complete anyway and “tell supervisor later”
- ask someone else to approve under the operator’s own identity

## 8.3 Supervisor behavior when reviewing exception

The supervisor should verify:

- the exception is real
- the justification is credible
- evidence is sufficient
- separation of duties is respected
- approval is within the supervisor’s policy band

Supervisor must not approve:

- their own exception request
- an exception outside scope
- an exception with missing mandatory evidence
- an exception only to improve KPI appearance

## 8.4 Quality-owned exceptions

Where the exception is fundamentally a quality disposition issue, quality authority takes precedence over routine supervisory convenience.

---

# 9. Handling quantity mistakes and corrections

## 9.1 Principle

Historical execution truth must not be silently overwritten.

If quantity was entered incorrectly, the team must use the approved correction path.

## 9.2 If the mistake is noticed immediately and no downstream impact exists

Follow the system-supported correction flow, which may involve:

- corrective quantity event
- supervisor-approved correction
- reopen if completion already happened

## 9.3 If downstream impact already exists

Do not attempt ad hoc local fixes.

The team must escalate because the correction may affect:

- downstream release
- WIP accounting
- QC interpretation
- traceability
- performance reporting

## 9.4 Forbidden correction behavior

- deleting history informally
- asking admins to directly edit production totals in database
- making compensating fake production on another order
- hiding NG by adjusting good totals without explicit correction path

---

# 10. Shift handover procedure

## 10.1 Handover is a business event even if not yet modeled as a rich feature

If responsibility for the station or operation passes from one shift / operator to another, the handover must be operationally controlled.

## 10.2 Minimum handover checklist

Outgoing operator should communicate and, where supported, ensure the system reflects:

- which operation is active
- whether execution is running or paused
- current reported quantity position
- any open downtime and reason
- any pending QC action
- any unresolved exception or hold
- any physical abnormality on station

## 10.3 What the incoming operator should verify

- the screen state matches physical reality
- the active job on screen is the actual job in process
- there is no hidden issue not reflected in the system
- any open hold/downtime is understood before continuing

## 10.4 Forbidden handover behavior

- leaving the station without closing or handing over responsibility
- telling the next shift to “just continue” while system data is wrong
- continuing under the previous operator’s active identity

---

# 11. Supervisor daily operating procedure

## 11.1 Routine monitoring responsibilities

The supervisor should routinely monitor:

- stations with active downtime
- operations stuck in pause or block
- QC holds
- exceptions awaiting decision
- quantity deviations and abnormal NG patterns
- stations left open with unclear responsibility

## 11.2 When supervisor should intervene quickly

- repeated downtime without clear reason
- prolonged pause with no classification
- operator unable to complete due to quantity mismatch
- QC failure blocking flow
- station queue and physical reality diverge
- multiple users dispute which operation is active

## 11.3 Supervisor should prefer explicit decisions over informal instruction

If the system requires a formal exception or disposition, the supervisor should use that path rather than giving only a verbal instruction.

Reason: verbal-only handling creates audit gaps and future confusion.

---

# 12. Support / admin operating restriction

## 12.1 Production actions by support are exceptional

`ADM` and `OTS` are not normal production actors.

If they must help on a live station situation, they must do so through the approved support / impersonation mechanism.

## 12.2 Required conditions for support intervention

- legitimate support need exists
- support action is auditable
- the acting identity and original requester are traceable
- support does not bypass required approval logic

## 12.3 Forbidden support behavior

- directly changing truth in database to make screens look consistent
- acting as operator without support-session trace
- approving production exceptions merely because a user requested urgency

---

# 13. Physical reality vs system reality mismatch

## 13.1 Principle

When physical reality and system state do not match, the mismatch must be resolved deliberately.

Neither side should be ignored.

## 13.2 Typical mismatch examples

- product physically running but system shows not started
- system shows running but station is idle
- queue shows wrong work order
- quantity on screen clearly differs from physical count
- QC hold exists in system but material has already moved physically

## 13.3 Required response

1. stop further uncontrolled propagation if risk is material
2. identify last known correct point
3. involve supervisor
4. use explicit correction / reopen / exception path
5. document reason and evidence where required

Do not continue blindly and plan to “fix all data later”.

---

# 14. End-of-shift / end-of-day minimum checks

Before the shift or daily responsibility ends, the team should ensure:

- no station is unintentionally left `RUNNING`
- open downtime items are real and intentional
- open QC holds are visible to the next responsible team
- unresolved exceptions are handed over with owner and status
- station sessions are not left open without ownership
- production quantities entered during the shift are not obviously incomplete

This checklist is especially important in the early implementation phase while process discipline is being stabilized.

---

# 15. Training requirements

## 15.1 Operators must be trained on

- difference between start / pause / downtime / complete
- why quantity is reported by delta
- why NG and reason capture matter
- why they cannot self-approve exceptions
- what to do when QC fails
- how to perform clean shift handover

## 15.2 Supervisors must be trained on

- exception and approval responsibilities
- separation of duties
- difference between operational convenience and auditable truth
- how to resolve mismatch without bypassing process

## 15.3 Quality users must be trained on

- QC hold logic
- disposition ownership
- when quality decision overrides production convenience

---

# 16. UI / UX implications from this SOP

This is not a UI specification, but the following UX behaviors should exist to support correct operations.

## 16.1 Station screen should make the next correct action obvious

Examples:

- if running, show report / pause / downtime / complete actions
- if QC hold is active, prevent misleading continue actions
- if no session exists, do not show execution actions as primary path

## 16.2 The system should clearly explain blocked actions

When rejecting an action, the system should state why, for example:

- mandatory QC still pending
- open downtime must be closed first
- exception approval required
- user lacks role/scope

## 16.3 The system should discourage ambiguous behavior

Examples:

- warn before closing session with unresolved items
- force reason for NG quantity
- force classification if pause exceeds threshold
- clearly display who owns the current station session

---

# 17. Minimum KPI interpretation cautions

Operational users and supervisors must understand that metrics such as runtime, downtime, OEE, output, and delays are only as trustworthy as execution discipline.

Therefore:

- false starts damage runtime truth
- unclassified pauses damage downtime truth
- hidden NG damages quality and output truth
- late back-entry damages timeline truth
- informal exception handling damages auditability and root-cause analysis

This SOP exists not only to control user behavior, but to protect the reliability of future MOM analytics and AI advisory layers.

---

# 18. What must exist now vs later

## 18.1 Must exist now

- open / close station session discipline
- claim / start / report / pause / downtime / resume / complete basic flow
- mandatory reason for NG when NG is reported
- mandatory downtime start/end with reason path
- explicit QC fail / hold handling
- explicit exception + supervisor decision path
- shift handover discipline even if partially procedural

## 18.2 May be designed now and implemented later

- digital sign-off for handover
- richer evidence upload
- guided recovery wizard for mismatch
- advanced rework routing
- machine-originated assist suggestions
- AI-guided root-cause hints

---

# 19. Summary

The station execution SOP is built on a simple principle:

**Normal work should be easy, abnormal work should be explicit, and no one should have to hide reality to keep the system moving.**

If operators, supervisors, and quality roles follow this procedure:

- execution truth remains reliable
- review and approvals stay auditable
- KPIs stay meaningful
- later AI layers can be trusted as advisory consumers of real manufacturing history

