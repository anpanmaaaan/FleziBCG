# Station Execution Operational SOP
## Current implemented baseline alignment note

Status: **Operational SOP aligned to the current implemented execution-core baseline**

This SOP is intentionally limited to what is actually implemented now.

## 1. Normal operator flow now
Normal operator flow in the current baseline is:

1. Select and claim operation
2. Start execution
3. Report production during execution
4. Pause / resume as needed
5. Start / end downtime with reason
6. Complete execution

## 2. What operators should not do
Operators should not:
- stack multiple unreleased claims in the same station context
- use ordinary release to break continuity of active work
- reopen closed records
- close completed records under the current phase rule
- bypass downtime classification when the stop is real

## 3. Downtime handling now
Downtime is implemented and must be explicitly started and ended.
Ending downtime returns the work to non-running state; it does not auto-resume execution.

## 4. Closure handling now
Current phase rule:
- supervisors own the available close/reopen foundation
- close/reopen are post-execution closure controls, not normal runtime operator controls

## 5. Deferred operational areas
Not part of the current implemented baseline:
- station session procedure in system
- QC measurement workflow
- quality hold / disposition workflow
- exception/disposition workflow
- support-mode operational intervention flows
