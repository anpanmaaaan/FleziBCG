# Slice Strategy for FleziBCG

## Purpose

This document defines how FleziBCG should be implemented incrementally.

The goal is not to build the whole backend first.

The goal is to build a working, testable MOM platform through vertical slices:

```text
Design baseline → small slice → DB/BE/test/minimal FE verification → verify → next slice
```

---

# 1. Core Philosophy

## Build system slices, not backend modules

Each slice should produce a verifiable system capability.

A proper slice may include:

- DB / migration
- backend model / repository
- service logic
- event/security event if governed action
- API route
- tests
- minimal frontend/API verification if needed
- documentation update if contract changes

## Backend remains source of truth

Frontend must not decide:

- execution state
- authorization
- approval
- operational truth

Frontend may:

- display backend-derived state
- send user intent
- guide interaction
- show backend-provided allowed actions

## Hard Mode MOM v3 applies to critical slices

If a slice touches execution, state machine, events, projections, station/session/operator/equipment, production reporting, downtime, completion, tenant/scope/auth, IAM, role/scope, audit, or critical invariants:

```text
Hard Mode MOM v3 = ON
```

---

# 2. Recommended Phase Order

```text
P0-A Foundation Database Slice
→ P0-B Manufacturing Master Data Minimum
→ P0-C Execution Core
→ P0-D Quality Lite
→ P0-E Supervisory Operations
→ P1-A Integration Foundation
→ P1-B Acceptance Gate
→ P1-C Material Readiness + Backflush
→ P1-D Reporting / KPI / OEE
→ P1-E Andon / Notification / Maintenance Lite
→ P2+ APS / AI / Digital Twin / Compliance
```

Do not jump to AI, APS, Backflush, Acceptance Gate, Digital Twin, or Compliance before foundation and execution truth are stable.

---

# 3. P0-A Foundation

## Goal

Build governance/foundation layer required before execution.

## Slices

1. Runtime config hardening
2. Alembic foundation
3. Remove production create_all path
4. Tenant foundation
5. IAM user lifecycle
6. Session / refresh token foundation
7. Role / action / scope foundation
8. Plant hierarchy foundation
9. Audit / security event foundation
10. Backend CI minimum

## Explicit exclusions

- ERP Integration
- Acceptance Gate
- Backflush
- APS
- AI
- Digital Twin
- Compliance/e-record
- OPC UA / MQTT / Sparkplug
- Kafka / Redis / OPA migration
- full Station Execution refactor
- claim removal unless isolated and explicitly planned

---

# 4. P0-B MMD Minimum

Build only after P0-A foundation is stable.

Slices:

1. Product foundation
2. Routing foundation
3. Resource requirement mapping
4. Reason/reference data foundation

Out of scope:

- full PLM
- recipe/phase ISA-88 full model
- ERP master data sync
- advanced planning

---

# 5. P0-C Execution Core

Hard Mode MOM v3 always ON.

Slices:

1. Work Order / Operation Foundation
2. Station Session Foundation
3. Execution Event Log
4. Start Execution Command
5. Pause / Resume Execution
6. Production Reporting
7. Downtime Start / End
8. Complete / Close / Reopen

Required:

- backend-derived status
- no frontend truth
- no shortcut completion
- command → validate → event → projection
- negative tests

---

# 6. P0-D Quality Lite

Slices:

1. QC Requirement Link
2. Measurement Entry
3. Backend Evaluation
4. Quality Hold Visibility

Out of scope:

- full Acceptance Gate
- deviation approval
- CAPA
- enterprise QMS

---

# 7. P0-E Supervisory Operations

Read-only visibility from execution truth.

Slices:

1. Operation List / Detail Read Model
2. Line / Station Monitor
3. Event Timeline
4. Basic Reports

Out of scope:

- AI insight
- full OEE deep dive
- APS
- Digital Twin

---

# 8. Agent Continuation Rule

After each slice:

1. update implementation plan
2. update verification report
3. run tests
4. select next safest slice
5. continue

Stop only if:

- design contradiction exists
- migration risk requires human decision
- business logic must be invented
- Hard Mode MOM v3 blocks implementation
- remaining scope belongs to excluded future modules
