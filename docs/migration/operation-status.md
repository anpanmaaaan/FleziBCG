# Operation Status Semantics — Current Model and Future Migration

## 1) Current State (vCurrent)
- Backend operation status enum currently uses `PLANNED`, `IN_PROGRESS`, `COMPLETED`, and `ABORTED`.
- In the current execution model, `PLANNED` is used as the practical "pending for execution" state.
- There is no separate backend `PENDING` execution enum yet.
- UI Label Rule (vCurrent): backend `PLANNED` must always be rendered as `Pending` in user-facing UI.
- The term `Ready` is reserved for a future readiness or eligibility dimension and must not be used as an execution status label.
- Execution lifecycle status is event-derived; persisted status fields are projections derived from execution events and must remain consistent with event history.

## 2) Business Rationale
- Reduced operator confusion: operators and supervisors need an execution-ready term, not planning semantics.
- No active scheduling/dispatch layer yet: a separate planning-release lifecycle is not enforced in Phase 1-2 execution flow.
- Execution maturity first: deterministic execution actions and event-derived state are prioritized over planning granularity.

## 3) When to Split PLANNED vs PENDING
Introduce a split only when at least one trigger becomes true:
- APS/scheduling introduces explicit release gates.
- Routing/release rules distinguish planning approval from execution readiness.
- QC/precondition gating blocks execution before release.
- Dispatch policy requires a formal transition from planning state to station-eligible queue state.

## 4) Future Target Model
Recommended future model separates planning and execution dimensions:
- Planning Status: `PLANNED` / `RELEASED`
- Execution Status: `PENDING` / `IN_PROGRESS` / `COMPLETED` / `ABORTED`

Guidance:
- `RELEASED` means planning has authorized execution eligibility.
- `PENDING` means released and waiting for operator execution start.
- Execution transitions continue to be event-driven and backend-derived.

## 5) Migration Guidelines (IMPORTANT)
### Backend enum evolution strategy
- Add new states/versioned semantics explicitly (no in-place silent meaning changes).
- Keep existing enum values backward-compatible during transition.
- Introduce compatibility mapping in service/serializer layer where required.

### API compatibility considerations
- Version API contract when response semantics change (`PLANNED` no longer meaning execution-pending).
- Preserve old clients via adapter mapping during rollout window.
- Document status contract clearly in API docs and release notes.
- Recommended migration approach: introduce `planning_status` and `execution_status` as separate fields in a versioned API (for example `v2`), while retaining the legacy `status` field during a deprecation window via explicit adapter mapping.

### UI impact and regression risks
- All status badges/filters must use centralized UI label mapping.
- Regression risk: any fallback to raw status string may leak internal enum terms.
- Add tests/checks for `PLANNED` display behavior to enforce `Pending` labeling.

### Data migration notes (historical records)
- Historical records with `PLANNED` must not be reinterpreted silently.
- If split introduces `RELEASED` or `PENDING`, backfill rules must be explicit and documented.
- Event history remains source of truth; snapshot projections should be recomputed safely where needed.

## 6) Hard Rule
- Never repurpose `PLANNED` semantics silently.
- Any PLANNED/PENDING split must be explicit, versioned, and documented before rollout.
