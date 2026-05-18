# Pilot MVP Continuous Operating Plan

Status: Active
Last updated: 2026-05-17

This plan is optimized for a solo founder working with coding AI agents. It is
slice-based by design: every slice must leave the product more usable, more
truthful, or more testable.

## Weekly Loop

Run the same loop every week:

1. Pick one business slice, not a broad module.
2. Confirm backend truth first: schema, service, API, RBAC, audit/event behavior.
3. Connect the frontend only after backend behavior is testable.
4. Add or update tests for the exact workflow.
5. Update `frontend/src/app/screenStatus.ts` if any screen maturity changes.
6. Update the relevant implementation note or closeout report.

If a slice tries to start AI, APS, digital twin, ERP, compliance, or batch
runtime before the pilot path is stable, stop and move it to future scope.

## Slice Order

### Slice 1: Product Truth And Guardrails

Done when:

- Current implementation truth exists and is linked from the README.
- Historical roadmap is marked as historical.
- Manufacturing mode profile anchors exist for tenant, plant, and scope.
- Runtime remains discrete-first.

### Slice 2: Pilot Seed And Login

Done when:

- Demo accounts are documented and work against the current backend.
- Login, refresh, logout, logout-all, and session revoke have targeted tests.
- Tenant mismatch and inactive tenant checks fail closed.

### Slice 3: Station Session Entry

Done when:

- Operator can open a station session with station scope enforced.
- Operator identification and equipment binding are backend-connected.
- The frontend does not infer execution authorization locally.

### Slice 4: Station Queue And Start

Done when:

- Operator sees only eligible station queue work from backend.
- Start operation emits backend execution truth.
- Duplicate/invalid start attempts fail closed.
- Supervisor can see status change through backend read APIs.

### Slice 5: Pause, Resume, Downtime, Quantity

Done when:

- Pause/resume and downtime start/end are tested command paths.
- Good/scrap quantity reporting is backend-owned.
- Operation status and allowed actions are derived from backend state.

### Slice 6: Quality-Gated Completion

Done when:

- Required quality measurements are loaded from backend.
- Measurement submission is validated and evaluated by backend.
- Failed or incomplete required measurements create/keep a quality hold.
- Completion is blocked until the quality hold is resolved.

### Slice 7: QA Resolution

Done when:

- QAL can resolve holds/deviations/nonconformances through backend APIs.
- OPR/SUP/PMG/ADM direct boundaries are tested.
- Security/audit events exist for important denied or privileged actions.

### Slice 8: Complete, Close, Timeline

Done when:

- Operator completes and closes an operation only when backend allows it.
- Reopen remains controlled by supervisor authority.
- Operation timeline shows backend events for the pilot path.
- A Playwright or script-level golden path exists.

## Frontend Rules

- Connected pilot screens must use real backend APIs.
- Partial screens must state the narrow gap in `screenStatus.ts`.
- Shell and mock screens must never be demoed as operational truth.
- UI affordances may hide unavailable actions, but backend remains the authority.

## Backend Rules

- Alembic is the production schema path.
- Execution events and backend projections are the execution truth.
- Allowed actions are backend-derived.
- Authorization is checked per request.
- Tenant isolation is enforced at repository/service/API boundaries.
- Quality evaluation is backend-owned.

## Future Expansion Order

After the pilot path is stable:

1. Supervisory operations and deterministic reports.
2. Material readiness and WIP visibility.
3. Integration foundation: external systems, inbox/outbox, retry, reconciliation.
4. Batch/process foundation: recipe, phase, batch context, process parameters.
5. Compliance/eBR only if the first batch/process customer requires it.
6. AI advisory layer after deterministic reporting exists.
7. Digital twin after operational projections are reliable.

