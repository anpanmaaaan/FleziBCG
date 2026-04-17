# No-Go Terminology — Status Model

**Purpose:** Prevent misuse of status terms across codebase and documentation.  
**Authority:** `docs/system/mes-business-logic-v1.md` §3 (Two-Dimension Status Model)  
**See also:** `docs/adr/ADR-0001-two-dimension-status-model.md`

---

## 1. Execution Lifecycle Status — Canonical Terms

These are the only valid execution lifecycle states for operations. Use these terms when referring to where an operation is in its execution flow.

| Canonical term | Meaning | UI display label (EN) | UI display label (JA) |
|----------------|---------|----------------------|----------------------|
| `PLANNED` | Not yet started; initial lifecycle state | "Planned" | "計画済み" |
| `IN_PROGRESS` | Operator has clocked on; work is active | "In Progress" | "進行中" |
| `COMPLETED` | Work finished normally | "Completed" | "完了" |
| `ABORTED` | Terminated before completion | "Aborted" | "中止" |

---

## 2. FORBIDDEN as Execution Lifecycle Labels

The following terms must **NOT** be used as execution lifecycle states or labels:

### 2.1 "Pending" as execution status

| Context | Verdict | Why |
|---------|---------|-----|
| `Operation.status === "PENDING"` | ❌ FORBIDDEN | Initial lifecycle state is `PLANNED`, not `PENDING` |
| `_derive_status()` returning `PENDING` | ❌ FORBIDDEN | Derivation must return `PLANNED` for no-event state |
| UI showing "Pending" for a `PLANNED` operation | ❌ FORBIDDEN | Display label for `PLANNED` is "Planned", not "Pending" |
| StatusBadge variant using "Pending" | ❌ FORBIDDEN | Use canonical "Planned" label |
| i18n key `common.status.pending` as lifecycle label | ❌ FORBIDDEN | Use `common.status.planned` |

### 2.2 "Blocked" as execution lifecycle state

| Context | Verdict | Why |
|---------|---------|-----|
| `_derive_status()` returning `BLOCKED` | ❌ FORBIDDEN | BLOCKED is a readiness dimension, not lifecycle |
| Execution lifecycle diagram including BLOCKED | ❌ FORBIDDEN | Not a lifecycle transition |
| GanttChart using "Blocked" as lifecycle status | ❌ FORBIDDEN | Separate concept from execution lifecycle |

### 2.3 "Running" / "Started" / "Active" as execution status

| Context | Verdict | Why |
|---------|---------|-----|
| `op.status === "Running"` in execution logic | ❌ FORBIDDEN | Canonical term is `IN_PROGRESS` |
| GanttChart status type `'Running'` | ⚠️ MIGRATE | Should use `IN_PROGRESS` internally, "In Progress" as display |

---

## 3. ALLOWED — Readiness/Dispatch Context

The following uses of "Pending" and "Blocked" are **legitimate** in readiness/dispatch contexts:

### 3.1 "Pending" in readiness context

| Context | Verdict | Why |
|---------|---------|-----|
| Station queue item labeled "Pending" (meaning: eligible for claim) | ✅ OK | Readiness indicator, not lifecycle state |
| `StationQueueItem.readiness_state === "PENDING"` | ✅ OK | Readiness dimension, orthogonal to lifecycle |
| Filter dropdown "Pending" in station queue view | ✅ OK | Filtering by readiness, not lifecycle |
| `ProductionOrder.status` = "PENDING" | ✅ OK | PO has its own status model, not operation lifecycle |

### 3.2 "Blocked" in readiness context

| Context | Verdict | Why |
|---------|---------|-----|
| Supervisor view showing "Blocked" bucket for constrained operations | ✅ OK | Read-only display of readiness constraint |
| `readiness_status === "BLOCKED"` (when readiness column is implemented) | ✅ OK | Readiness dimension, not lifecycle |
| Dashboard KPI counting blocked operations | ✅ OK | Aggregation of readiness state |

---

## 4. WO-Level Derived Display States

These values exist only at the Work Order level and are derived display states:

| Term | Level | Purpose | Lifecycle state? |
|------|-------|---------|-----------------|
| `LATE` | WO only | Forecasting: not completed and past planned_end | NO |
| `COMPLETED_LATE` | WO only | Completed after planned_end | NO |

These are **NOT** operation execution lifecycle values.

---

## 5. Quick-Reference Decision Tree

```
Is this about "where in the execution flow"?
  → Use PLANNED / IN_PROGRESS / COMPLETED / ABORTED
  → NEVER use PENDING or BLOCKED

Is this about "can this operation be dispatched/claimed"?
  → Use PENDING / BLOCKED / HOLD / READY (readiness dimension)
  → Clearly label as readiness, not lifecycle

Is this about Work Order aggregate status?
  → Use PLANNED / IN_PROGRESS / COMPLETED / COMPLETED_LATE / LATE
  → These are WO-level derived display values
```

---

## 6. Audit Lint Rules (for future automated checks)

When running terminology audits:

1. **CRITICAL:** `_derive_status` must not return `PENDING` or `BLOCKED`
2. **CRITICAL:** Execution lifecycle diagrams must use PLANNED as initial state
3. **MAJOR:** Frontend execution status type unions should include `PLANNED`, not `PENDING`
4. **MAJOR:** `mapExecutionStatusText(PLANNED)` should return "Planned", not "Pending"
5. **MINOR:** GanttChart internal status types should use backend enum codes
6. **INFO:** "Pending" in station queue / readiness context is allowed — do not flag
