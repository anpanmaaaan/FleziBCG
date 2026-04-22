# CANONICAL GLOSSARY

## Purpose
Defines shared vocabulary across backend, frontend, and AI. Terms are authoritative and must not be redefined locally.

---

## Core Terms

### Work Order (WO)
Production demand unit containing one or more Operations.

### Operation (OP)
Smallest schedulable execution unit. Executed at a Station.

### Station
Physical or logical execution point.

### Execution Session
Active claim of an Operation by an Operator at a Station. At most one active session per Operation.

### Runtime Status
Execution lifecycle state: NOT_STARTED, RUNNING, PAUSED, COMPLETED.

### Closure Status
Record lock state: OPEN, CLOSED.

### Event
Append-only record representing a domain change. Source of truth for execution.

### Projection
Derived, query-optimized state built from events. Not authoritative.

### Action Code
Canonical identifier for a user/system action (e.g., execution.start).

### Tenant
Top-level isolation boundary.

### Scope
Hierarchical boundary: tenant → plant → area → line → station → equipment.

### Approval
Governed decision required for certain actions, subject to SoD.

### SoD (Separation of Duties)
Requester must not be the decider for the same governed action.

---

## Rules
- Same term = same meaning across system
- Backend returns codes/enums; UI handles labels/i18n
- Do not redefine terms in services or UI
