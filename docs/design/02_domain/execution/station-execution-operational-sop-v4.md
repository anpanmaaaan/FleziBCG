# Station Execution Operational SOP

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Reworked normal operator flow to session/operator/equipment-first design. |

Status: Canonical operational SOP for the approved next-step Station Execution design.

## 1. Normal operator flow

Normal operator flow in the approved next-step design is:
1. enter station/work-center execution surface
2. open or restore active station session
3. identify operator by scan/manual entry as allowed
4. bind/select equipment if the station/resource policy requires it
5. select the operation/work item
6. start execution
7. report production during execution
8. pause / resume as needed
9. start / end downtime with reason from the system catalog
10. complete execution

## 2. What operators should not do

Operators should not:
- bypass operator identification in normal flow
- bypass equipment binding where required
- reopen closed records in normal flow
- close completed records under current supervisory phase rule
- bypass backend downtime reason master data
- assume that visible buttons prove authorization

## 3. Downtime handling

Downtime must be explicitly started and ended.
Ending downtime returns the work to non-running state; it does not auto-resume.

## 4. Closure handling

Current phase rule remains supervisor-owned close/reopen foundation unless later policy broadens it safely.

## 5. Deferred operational areas

Not part of this current next-step pack implementation target:
- full QC measurement workflow in the same operator flow
- quality hold / disposition workflow
- exception/disposition lifecycle
- support-mode operational intervention flows as default behavior
