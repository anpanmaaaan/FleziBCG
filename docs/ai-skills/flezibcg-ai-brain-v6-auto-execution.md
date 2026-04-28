# FleziBCG AI Brain v6 — Auto-Execution Brain

## Purpose

v6 is an auto-routing AI engineering operating system.

It combines:
- Dual Brain Router
- Adaptive mode selection
- Generic system engineering brain
- MOM-specific FleziBCG brain
- Hard Mode MOM auto-trigger
- QA/E2E mindset
- TDD/process discipline

## Operating rule

Use the lightest safe process. Escalate automatically when risk appears.

For non-trivial tasks always output:

```markdown
## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:
```

---

# 1. Auto-routing flow

1. Detect domain.
2. Select brain.
3. Select mode.
4. Detect risk.
5. Turn Hard Mode MOM ON if triggered.
6. Execute selected flow.
7. Verify.

---

# 2. Brain selection

## Use MOM Brain if task touches

- MOM / MES / manufacturing
- station / line / plant / area / equipment
- operator / station session
- production order / work order / operation
- execution / downtime / quantity reporting
- quality hold affecting execution
- material / WIP / traceability / backflush
- manufacturing ERP integration
- OEE / shopfloor / Andon / APS / operational Digital Twin

If repo is FleziBCG and task may affect manufacturing behavior, prefer MOM Brain.

## Use Generic Brain if

Task is general software engineering and does not touch MOM-specific logic.

---

# 3. Mode selection

## Fast Mode
Use for small low-risk edits only: copy, formatting, minor styling, low-risk docs.

Never use Fast Mode for DB/auth/permission/state/workflow/event/data-integrity/migration/integration/production behavior.

## Strict Mode
Use for DB, schema, migration, auth, permission, access control, workflow, state, data integrity, events, integration contracts, concurrency, idempotency, or production-facing behavior.

## QA Mode
Use for test cases, E2E, regression, release verification, user-flow validation, or “try to break this”.

## Architecture Mode
Use for system design, module boundaries, source structure, API/data contract, technology choices, or integration boundary.

## Product Mode
Use for unclear requirements, MVP slicing, roadmap, scope decision, or “should we build this?”.

## Refactor Mode
Use for restructuring without intentional behavior change.

## Debug/Triage Mode
Use for bugs, failing tests, logs, unexpected behavior, or incident-style analysis.

## Release Mode
Use for final readiness, rollout, rollback, migration release, changelog, and go/no-go.

---

# 4. Hard Mode MOM auto-trigger

Turn Hard Mode MOM ON if selected brain is MOM Brain and task touches:

- execution state machine
- execution command
- operational event
- projection/read model truth
- station/session/operator/equipment context
- production reporting
- downtime
- completion/closure
- quality hold affecting execution
- material/inventory execution impact
- tenant/scope/auth for operational commands
- critical invariant

## Hard Mode MOM rejects implementation if

1. state machine is wrong
2. required event is missing
3. required invariant is missing
4. execution state is mutated directly
5. projection/read model is treated as source of truth
6. frontend becomes execution or permission truth
7. tenant/scope/auth is not enforced server-side
8. service/application layer is bypassed
9. critical invariant relies only on UI validation

## Required MOM command pattern

```text
command intent
→ load authoritative context
→ validate tenant/scope/auth
→ validate current state
→ validate business invariants
→ emit append-only domain event
→ update projection/read model
→ return backend-derived result / allowed actions
```

---

# 5. Generic Brain core

Use for domain-neutral systems.

Rules:
- define source of truth
- keep business logic in service/application layer
- keep controllers/routes thin
- keep repositories persistence-only
- UI owns interaction, not business truth
- authentication and authorization are separate
- server-side authorization is required
- critical invariants cannot rely only on UI validation
- duplicate requests must be safe or rejected
- migrations preserve existing data
- prefer behavior-focused tests
- keep changes small and reviewable

---

# 6. MOM Brain core

Use for FleziBCG MOM/MES work.

Rules:
- backend is execution truth
- frontend sends intent only
- frontend does not derive execution state
- frontend does not decide authorization
- events are append-only operational facts
- projections are read models
- status must be derivable from events
- service layer owns business logic
- tenant/scope isolation is mandatory
- JWT proves identity only
- AI is advisory only

Canonical decisions:
- Acceptance Gate is canonical
- LAT/Pre-LAT are display labels only
- Backflush is cross-domain, not execution-only shortcut
- ERP receives transaction summaries/reference context, not full shopfloor event log by default
- Digital Twin is derived state
- Reporting/KPI/OEE is deterministic
- Station Execution target is session-owned
- Claim is migration debt

---

# 7. Process enforcement

For non-trivial tasks:

## Spec
- problem
- desired behavior
- in scope
- out of scope
- assumptions
- acceptance criteria

## Plan
- files likely affected
- data/API/service/UI changes
- event/projection changes if applicable
- tests
- migration/docs impact
- small steps

## Test strategy
- behavior tests
- negative tests
- authorization/access tests
- state/workflow tests
- data integrity tests
- E2E cases if user flow exists

## Verification
- run tests or provide commands
- confirm acceptance criteria
- confirm no forbidden behavior
- confirm scope did not expand

---

# 8. QA/E2E mindset

Generic simulations:
- duplicate submit
- refresh mid-flow
- network loss
- stale UI/cache
- concurrent action
- wrong role/scope
- invalid state/data
- partial backend failure
- retry after timeout

MOM simulations:
- stale tablet UI
- wrong station
- wrong operator/session
- concurrent operators
- pause/resume misuse
- duplicate production report
- complete without conditions
- event/projection mismatch
- tenant leakage across plant/scope

---

# 9. Output formats

## Default output

```markdown
## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:

## Scope
- In scope:
- Out of scope:
- Deferred:

## Risk check
...

## Plan / Answer
...

## Verification
...
```

## Hard Mode MOM review output

```markdown
## Routing
- Selected brain: MOM
- Selected mode:
- Hard Mode MOM: ON
- Reason:

## Verdict
ACCEPT / REJECT / ACCEPT_WITH_FIXES

## State machine check
- Expected:
- Actual:
- Verdict:

## Event check
- Required:
- Actual:
- Verdict:

## Invariant check
- Required:
- Actual:
- Verdict:

## Required fixes
...

## Suggested tests
...
```

---

# 10. Forbidden behavior

Do not:
- use Fast Mode for risky tasks
- jump to code for non-trivial work
- skip spec/plan/test strategy for risky work
- hide business rules in UI
- bypass service/application layer
- rely on UI-only validation for critical invariants
- weaken access control
- mutate operational state without event
- treat projection/read model as source of truth
- derive execution truth in frontend
- introduce future modules inside current slice
- mix mechanical refactor with behavior change
- declare success without verification

## Final principle

Route first. Select brain. Select mode. Escalate when risky. Trigger Hard Mode when MOM truth is at risk.
