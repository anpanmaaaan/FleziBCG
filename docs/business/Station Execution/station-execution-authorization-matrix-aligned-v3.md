# Station Execution Authorization Matrix
## Current implemented backend baseline alignment

Status: **Authoritative authorization truth for the current implemented backend baseline**  
Scope: **Station Execution Core / Pre-QC / Pre-Review**

This file reconciles canonical role intent with what is actually enforced now.

## 1. Implemented command ownership now

| Command | Current implemented phase rule |
|---|---|
| `claim_operation` | OPR normal owner; backend scope/action rules apply |
| `start_execution` | OPR normal owner; backend scope/action + claim ownership apply |
| `pause_execution` | OPR normal owner; backend scope/action + claim ownership apply |
| `resume_execution` | OPR normal owner; backend scope/action + claim ownership apply |
| `report_production` | OPR normal owner; backend scope/action + claim ownership apply |
| `start_downtime` | OPR normal owner; backend scope/action + claim ownership apply |
| `end_downtime` | OPR normal owner; backend scope/action + claim ownership apply |
| `complete_execution` | OPR normal owner; backend scope/action + claim ownership apply |
| `close_operation` | **SUP-only phase rule at API boundary** |
| `reopen_operation` | **SUP-only phase rule at API boundary** |

## 2. Important implementation-phase notes

- `close_operation` is intentionally hardened to a narrow `SUP`-only API rule in the current pre-QC baseline.
- `reopen_operation` is also implemented with a narrow supervisor-owned path in the current phase.
- This is stricter than the broader future canonical matrix and is intentional until richer quality/review/policy context exists.

## 3. Deferred canonical participation
Not implemented in the current baseline:
- QCI/QAL conditional participation in close/reopen under quality-owned policy context
- support/admin production-write support-mode paths for these commands
- exception/disposition ownership matrix execution in code

## 4. Principle reminder
Visible screen state is never proof that the action is allowed. Backend authorization remains authoritative.
