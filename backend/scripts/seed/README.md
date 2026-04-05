# MES Lite Seed & Demo Data

This folder contains seed data generators for Phase 6 MES Lite, aligned with the business logic contract documented in `/docs/system/mes-business-logic-v1.md`.

## Purpose

Seed data is **NOT** for realism; it is for **validation** of core business rules. Each seed scenario is a regression test that exercises specific parts of the execution model.

## Seed Scenarios (S1–S4)

All scenarios are run automatically by `seed_all.py` and verified by `seed_all.py` verification suite.

### S1: Normal On-Time Completion

**File:** `scenario_s1_normal_completion.py`

**Business Rules Validated:**
- Normal execution path: PENDING → IN_PROGRESS → COMPLETED
- Status derivation: All operations complete within planned windows → WO status = COMPLETED
- Progress calculation: (completed_qty / quantity) × 100 = 100%
- Cycle time tracking: (actual_end - actual_start) is recorded

**Data:**
- 3 operations in sequence (Prep → Machine → Inspect)
- Each operation starts at planned_start and completes at planned_end
- All completions occur ≤ planned_end (on-time)
- Timestamps use future dates (2099) to ensure they're "on-time" relative to now

**Verification:**
- WO status = "COMPLETED"
- All operations status = "COMPLETED"
- Progress = 100%

---

### S2: Completed Late

**File:** `scenario_s2_completed_late.py`

**Business Rules Validated:**
- Late completion detection: actual_end > planned_end → COMPLETED_LATE status
- Work order aggregation: All ops COMPLETED_LATE → WO status = COMPLETED_LATE
- Delay calculation: delay_minutes = Max(0, actual_end - planned_end)
- Timing logic: Status derivation uses actual vs. planned timestamps

**Data:**
- 3 operations in sequence (Prep → Process → QC)
- Each operation starts at planned_start
- Each operation completes **1 hour after** planned_end (deliberate delay)
- Historical timestamps (2020) show this is a completed-late scenario

**Verification:**
- WO status = "COMPLETED_LATE"
- All operations status = "COMPLETED_LATE"
- delay_minutes > 0 for all operations

**Note on Late Timing:**
The seed uses past dates (2020) to demonstrate the completed-late scenario. Status derivation compares actual vs. planned timestamps *collected at execution time*, not "now" vs. planned. This ensures consistency regardless of when the seed is run.

---

### S3: In-Progress + Blocked Incident

**File:** `scenario_s3_in_progress_block.py`

**Business Rules Validated:**
- Blocking during execution: Operation can transition IN_PROGRESS → BLOCKED
- Work order status aggregation with mixed states:
  - At least one operation is BLOCKED
  - Status rules: If any op is BLOCKED and some are IN_PROGRESS → WO status = BLOCKED
- Incident/delay handling: Operator encounters a blocker (e.g., material shortage) and records it
- Supervisor lens filtering: Supervisor view highlights BLOCKED operations

**Data:**
- 3 operations: Prep, Process, Inspect
- Op 1 (Prep): Started → Blocked due to MATERIAL_SHORTAGE
- Op 2 (Process): Started → Left IN_PROGRESS (awaiting upstream resolution)
- Op 3 (Inspect): Left PENDING (not yet started due to upstream blocker)

**Verification:**
- Op 1 status = "BLOCKED"
- Op 2 status = "IN_PROGRESS"
- Op 3 status = "PENDING"
- WO status = "BLOCKED"
- Supervisor lens identifies Op 1 in BLOCKED bucket
- `block_reason_code` = "MATERIAL_SHORTAGE"

**Known Limitation:**
Currently uses `mark_blocked_for_incident_seed()` which sets status directly. Per the business logic contract, BLOCK should be a proper execution event (OP_BLOCKED). Future implementation should:
1. Add `OP_BLOCKED` and `OP_UNBLOCKED` to ExecutionEventType enum
2. Create a `block_operation()` service function
3. Update `mark_blocked_for_incident_seed()` to create proper events

---

### S4: Repeat Variance Analysis

**File:** `scenario_s4_repeat_variance.py`

**Business Rules Validated:**
- Process variance detection: Same operation name repeated with different cycle times
- IE/Process lens analytics: repeat_flag and high_variance_flag
- Variance calculation: cycle_time_delta from historical average
- Historical data for analysis: Multiple work orders containing same operation name
- Cycle time timing: (actual_end - actual_start) in minutes

**Data:**
- **Historical Executions (S4H1, S4H2, S4H3):** Same "Core" operation run 3 times with different cycle times:
  - S4H1: 5-minute cycle (quick)
  - S4H2: 60-minute cycle (normal, 12x slower) → variance detected
  - S4H3: 120-minute cycle (slow, extreme variance) → high_variance_flag
- **Main Scenario (S4):** Current work order with 3 operations:
  - Op 1 (Core): Completed in ~15 minutes (falls within variance range of history)
  - Op 2 (Secondary): LEFT IN_PROGRESS
  - Op 3 (Final): LEFT PENDING

**Verification:**
- S4H1, S4H2, S4H3 all have COMPLETED status
- S4 main scenario has Op 1 = COMPLETED, Op 2 = IN_PROGRESS, Op 3 = PENDING
- IE lens shows repeat_flag = true for "Core" operation (appears in multiple WOs)
- IE lens shows high_variance_flag = true (120-min outlier)
- cycle_time_minutes calculated correctly for all ops

---

## Seed User Data

Seed users are created in `backend/app/db/init_db.py` via `seed_demo_users()`:

| Username | Password | Role | Landing Page |
|---|---|---|---|
| admin | password123 | ADM | (no default; free roam) |
| manager | password123 | PMG | /dashboard |
| supervisor | password123 | SUP | /operations?lens=supervisor |
| operator | password123 | OPR | /station-execution |
| qa | password123 | QAL | /operations?lens=qc |

**Password Note:** Demo passwords are lowercase for simplicity. Production deployments must override via environment config or secure seeding.

---

## Seed Workflow

```
python -m backend.scripts.verify_users_auth.py
  → Run approval engine verification (AP-1 through AP-12 checks)

python -m backend.scripts.verify_impersonation.py
  → Run impersonation verification (IM-1 through IM-22 checks)

python -m backend.scripts.seed.seed_all.py
  → Populate S1–S4 scenarios
  → Run integrated verification (S1, S2, S3, S4 checks)

python -m scripts.seed.seed_station_execution_opr
  → Create dedicated Station Execution demo dataset for OPR user `operator`
  → Seeds operations scoped to `STATION_01` with mixed states (PENDING + IN_PROGRESS)
```

---

## Key Alignment Points with Business Logic Contract

### Status Derivation (Section 4)

- ✅ **S1:** Demonstrates PENDING → IN_PROGRESS → COMPLETED derivation
- ✅ **S2:** Demonstrates COMPLETED_LATE (actual_end > planned_end)
- ✅ **S3:** Demonstrates 3-operation aggregation with BLOCKED status
- ✅ **S4:** Demonstrates variance detection based on cycle_time

### Execution Invariants (Section 3.3)

- ✅ START on PENDING (S1, S2, S3, S4)
- ✅ Multiple operations in sequence
- ✅ COMPLETE on IN_PROGRESS (S1, S2, S4)
- ✅ BLOCK on IN_PROGRESS (S3 - currently via direct status set)

### Persona & UX (Section 5)

- ✅ S3 validates Supervisor lens (BLOCKED operations visible)
- ✅ S4 validates IE/Process lens (variance flags visible)
- ✅ S1, S2 validate Dashboard KPI data (progress, delay_minutes)

### Authorization & Governance (Section 6)

- ✅ Seed users created with correct roles (OPR, SUP, PMG, etc.)
- ✅ All operations triggered via "seed-user" (demo identity)
- ✅ No approval requests in S1–S4 (execution-only paths)
- ✅ No impersonation in seed data (tested separately in verify_impersonation.py)

---

## Extending Seed Scenarios

To add a new scenario:

1. **Create** `scenario_sN_description.py` (e.g., `scenario_s5_rework_approval.py`)
2. **Use helpers** from `common.py`: `create_scenario_context()`, `run_start()`, `run_complete()`, etc.
3. **Register** in `seed_all.py`:
   ```python
   from .scenario_sN_description import seed as seed_sN
   # ... in main() ...
   context_sN = seed_sN(db)
   ```
4. **Add verification** in `seed_all.py`:
   ```python
   def _verify_sN(db, ...) -> VerificationResult:
       # Assert business rule validated
       pass
   ```
5. **Document** the scenario in this README

---

## Change History

|  | Change |
|---|---|
| **2026-04-03** | Phase 6: Updated S1–S4 with timestamp support; S2 now demonstrates late completion; S4 shows variance with varying cycle times |
| **Earlier** | Phase 6A: Initial seed scaffolding (S1–S4 basic structure) |

---

## Notes for Future Phases

### Phase 7: Approval & QC Workflows

Add scenarios demonstrating:
- S5: QC_HOLD request + approval flow
- S6: SCRAP request (multi-role PMG/QAL approval)
- S7: WO_SPLIT with proper approval rules

### Phase 8: Multi-Tenant & Site Scoping

Add scenarios demonstrating:
- S8: Multi-tenant execution (different tenant_id)
- S9: Site-scoped RBAC (plant/area/line scopes)

### Current Gaps (Phase 6)

- **OP_BLOCKED event:** Currently simulated; should be a proper execution event
- **REPORT_QUANTITY:** Not demonstrated in seed scenarios (operations start → complete directly)
- **Approval workflows:** Not demonstrated in seed data (reserved for Phase 7)
