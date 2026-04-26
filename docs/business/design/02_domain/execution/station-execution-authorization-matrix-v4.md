# Station Execution Authorization Matrix

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Reworked command ownership around station-session-based execution. |

Status: Canonical authorization truth for the approved next-step Station Execution design.

## 1. Command ownership intent

| Command | Target normal owner | Notes |
|---|---|---|
| `open_station_session` | OPR | Station/resource session open under scope rules |
| `identify_operator` | OPR | Usually self/linked operator only in normal flow |
| `bind_equipment` | OPR | Required where station/resource policy requires explicit binding |
| `start_execution` | OPR | Backend scope/action + active session guards apply |
| `pause_execution` | OPR | Backend scope/action + active session guards apply |
| `resume_execution` | OPR | Backend scope/action + active session guards apply |
| `report_production` | OPR | Backend scope/action + active session guards apply |
| `start_downtime` | OPR | Backend scope/action + active session guards apply |
| `end_downtime` | OPR | Backend scope/action + active session guards apply |
| `complete_execution` | OPR | Backend scope/action + active session guards apply |
| `close_operation` | SUP | Current phase rule may remain supervisor-owned |
| `reopen_operation` | SUP | Current phase rule may remain supervisor-owned |
| `close_station_session` | OPR | Reject when active work would be orphaned |

## 2. Important notes

- visibility of a screen/action is never proof that the action is allowed
- backend authorization remains authoritative
- active execution session context is required for execution writes
- support/admin production-write paths remain governed and auditable, not default behavior
