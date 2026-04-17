# ADR-0001: Two-Dimension Status Model

**Date:** 2026-04-17  
**Status:** Accepted  
**Deciders:** MES Platform Team  
**Supersedes:** Single-status-column model in mes-business-logic-v1.md v1.0

---

## Context

A [Status Model Direction Audit](../audit/status-model-direction-audit.md) conducted on 2026-04-17 found that the codebase is a **conflicted hybrid**:

- **Execution derivation logic** (`_derive_status()`) implements a clean 4-state lifecycle (Direction B): `PLANNED → IN_PROGRESS → COMPLETED | ABORTED`
- **DB defaults, start guards, and station queue filters** still use `PENDING` (Direction A remnant)
- **`BLOCKED`** exists in `StatusEnum` but has **zero write paths** — no API endpoint, no service function, no event type
- The codebase works by "coincidental correctness" — the stale DB-default `PENDING` column value happens to satisfy guards that check for `PENDING`, while `_derive_status()` returns `PLANNED`

**Two authority documents contradicted each other:**

| Document | Initial state | BLOCKED | BLOCK/UNBLOCK events |
|----------|--------------|---------|---------------------|
| `mes-business-logic-v1.md` v1.0 | `PENDING` | ✅ Valid lifecycle state | ✅ Defined |
| `copilot-instructions.md` | `PLANNED` | ❌ "does NOT exist" | ❌ Not mentioned |

This contradiction caused confusion in code, agents, and audits.

---

## Decision

**Adopt a Two-Dimension Status Model (Option C)** that separates execution lifecycle from readiness/dispatch state:

### Dimension 1: ExecutionLifecycleStatus

Event-derived, authoritative. Answers: "Where is this operation in the execution flow?"

| Value | Meaning |
|-------|---------|
| `PLANNED` | Operation exists; execution has not started. **This is the initial state.** |
| `IN_PROGRESS` | Operator has clocked on; work is active |
| `COMPLETED` | Operator has clocked off; work finished normally |
| `ABORTED` | Operation terminated; will not resume |

- Exactly 4 values. No exceptions.
- `PENDING` and `BLOCKED` are **NOT** lifecycle states.
- `COMPLETED_LATE` and `LATE` are WO-level derived display states.
- Status is derived from `ExecutionEvent` log via `_derive_status()`.

### Dimension 2: ReadinessStatus

Orthogonal to lifecycle. Answers: "Is this operation eligible for dispatch?"

| Value | Meaning | Implementation |
|-------|---------|---------------|
| `PENDING` | Released, queued, eligible for claim | Currently implicit (station queue membership) |
| `BLOCKED` | Constraint prevents execution | **Not yet implemented** |
| `HOLD` | Quality/material hold | Future |
| `READY` | All prerequisites met | Future |

- Readiness does NOT affect `_derive_status()`.
- An operation can be `PLANNED` (lifecycle) and `BLOCKED` (readiness) simultaneously.
- When BLOCK/UNBLOCK is implemented, it modifies readiness state, not lifecycle.

---

## Consequences

### Documentation Alignment

1. `mes-business-logic-v1.md` updated to v1.1 — adds §3 (Two-Dimension Status Model), reframes BLOCK/UNBLOCK as readiness events
2. `copilot-instructions.md` updated — replaces absolute "PENDING does not exist" with two-dimension explanation
3. `docs/mom/no-go-terminology.md` created — distinguishes forbidden lifecycle labels from allowed readiness usage
4. `docs/execution/execution-lifecycle.md` — already aligned (uses PLANNED as initial state)

### UI Display Mapping (target state for code follow-up)

| Backend Lifecycle Status | Target display label (EN) | Target display label (JA) |
|--------------------------|---------------------------|---------------------------|
| `PLANNED` | "Planned" | "計画済み" |
| `IN_PROGRESS` | "In Progress" | "進行中" |
| `COMPLETED` | "Completed" | "完了" |
| `ABORTED` | "Aborted" | "中止" |

Note: The current code maps `PLANNED` → "Pending" — this is a bug to be fixed in the follow-up code PR.

### i18n Key Mapping (target state)

| i18n Key | EN value | JA value |
|----------|----------|----------|
| `common.status.planned` | "Planned" | "計画済み" |
| `common.status.in_progress` | "In Progress" | "進行中" |
| `common.status.completed` | "Completed" | "完了" |
| `common.status.aborted` | "Aborted" | "中止" |
| `common.status.blocked` | "Blocked" | "ブロック中" |
| `common.status.late` | "Delayed" | "遅延" |

---

## Follow-Up Implementation Plan

The following code changes are required in a **coordinated follow-up PR** (not in this ADR):

### Phase A: Backend Alignment (Critical)

1. **DB default fix:** Change `Operation.status` default from `StatusEnum.pending.value` to `StatusEnum.planned.value`
2. **Start guard fix:** `start_operation()` — check `StatusEnum.planned.value` instead of `StatusEnum.pending.value`
3. **Station queue filter fix:** Filter by `PLANNED` + `IN_PROGRESS` instead of `PENDING` + `IN_PROGRESS`
4. **Seed data fix:** Any seed operations created with `status = "PENDING"` should use `"PLANNED"`
5. **StatusEnum cleanup:** Mark `PENDING` and `BLOCKED` enum members with comments as readiness-only (keep for PO/WO usage)

### Phase B: Frontend Alignment (Major)

1. **executionMapper.ts:** Change `PLANNED` → "Planned" (currently maps to "Pending")
2. **operationApi.ts:** `OperationExecutionStatus` type — replace `"PENDING"` with `"PLANNED"`, add `"ABORTED"`
3. **GanttChart.tsx:** Refactor to use backend enum codes internally, map to display labels at render
4. **mapTimelineStatusToGanttStatus():** Compare backend enum codes, not display text output
5. **GlobalOperationList.tsx:** Remove `PENDING` from filter dropdown
6. **StationExecution.tsx:** Remove `"PENDING"` from clock-on guard (keep only `"PLANNED"`)
7. **OperationList.tsx:** Remove duplicate `mapBackendStatus()`, use central mapper

### Phase C: Cleanup (Minor)

1. Remove phantom `BLOCKED` handling from execution mapper (or keep for future readiness column)
2. Clean up `database.ts` stale type definitions
3. Update `SOURCE_STRUCTURE.md` — remove "block" references from operation routes/services

---

## Alternatives Considered

### Option A: Adopt Direction A (PENDING/BLOCKED as lifecycle states)

Rejected. This would require:
- Rewriting `_derive_status()` to return PENDING instead of PLANNED
- Implementing BLOCK/UNBLOCK as lifecycle events
- Contradicting `execution-lifecycle.md` which uses PLANNED

### Option B: Adopt Direction B strictly (remove PENDING/BLOCKED entirely)

Rejected. PENDING/BLOCKED have legitimate uses:
- PENDING makes sense as a readiness/dispatch concept
- BLOCKED as a readiness constraint is valuable for future supervisor workflows
- Removing them entirely would lose domain semantics

### Option C: Two-Dimension Model (SELECTED)

Best of both worlds:
- Execution lifecycle remains clean 4-state model (aligned with ISA-95)
- Readiness/dispatch gets its own dimension with PENDING/BLOCKED
- No domain semantics lost
- Clear separation prevents confusion

---

## References

- [Status Model Direction Audit](../audit/status-model-direction-audit.md)
- [mes-business-logic-v1.md §3](../system/mes-business-logic-v1.md#3-two-dimension-status-model)
- [execution-lifecycle.md](../execution/execution-lifecycle.md)
- [No-Go Terminology](../mom/no-go-terminology.md)
- [copilot-instructions.md — Execution Flow](../../.github/copilot-instructions.md)
