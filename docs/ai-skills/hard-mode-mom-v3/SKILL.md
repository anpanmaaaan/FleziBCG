---
name: hard-mode-mom-v3
description: Auto-generates event maps, invariant maps, and test matrices from FleziBCG design docs before allowing implementation.
---

# FleziBCG Hard Mode MOM v3

## Purpose

Hard Mode MOM v3 is a design-driven enforcement layer.

It requires the agent to read authoritative design docs and auto-generate:

1. Event map
2. Invariant map
3. State transition map
4. Test matrix
5. Implementation gate

before coding.

## v3 Difference vs v2

```text
Design docs
→ extracted domain facts
→ event map
→ invariant map
→ test matrix
→ code
→ build
→ test
→ verify
```

If design evidence is missing, the agent must not invent behavior.

## When to Use

Use v3 for:

- execution core
- station/session/operator/equipment
- production reporting
- downtime
- completion/closure
- quality hold affecting execution
- material/inventory execution impact
- tenant/scope/auth
- IAM lifecycle
- role/action/scope assignment
- audit/security event
- DB schema enforcing operational or governance truth
- any autonomous implementation slice where event/invariant requirements must be derived from design docs

## Mandatory Design Reading

Always read:

```text
.github/copilot-instructions.md
docs/design/INDEX.md
docs/design/AUTHORITATIVE_FILE_MAP.md
docs/governance/CODING_RULES.md
docs/governance/ENGINEERING_DECISIONS.md
docs/governance/SOURCE_STRUCTURE.md
docs/design/00_platform/product-business-truth-overview.md
```

For foundation/governance:

```text
docs/design/01_foundation/
docs/design/09_data/
docs/design/05_application/
```

For execution:

```text
docs/design/01_domain/execution/
docs/design/05_workflows/
docs/design/09_data/
docs/design/05_application/event-catalog-and-subscriber-map.md
docs/design/05_application/api-catalog-current-baseline.md
```

For quality:

```text
docs/design/01_domain/quality/
docs/design/02_domain/quality/
docs/design/05_workflows/quality-workflows.md
```

For material/backflush/traceability:

```text
docs/design/02_domain/material/
docs/design/03_integration/
docs/design/09_data/
```

If paths differ, use `INDEX.md` and `AUTHORITATIVE_FILE_MAP.md`.

## Design Extraction Step

Before coding:

```markdown
## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|

### Commands / actions found
| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|

### Events found
| Event | Trigger | Source doc | Evidence |
|---|---|---|---|

### States found
| State | Entity | Source doc | Evidence |
|---|---|---|---|

### Invariants found
| Invariant | Type | Source doc | Evidence |
|---|---|---|---|

### Explicit exclusions
| Exclusion | Source doc | Reason |
|---|---|---|
```

Do not proceed if there is no design evidence for a behavior-changing slice.

## Auto-generated Event Map

```markdown
| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
```

Event categories:

- domain_event
- security_event
- audit_event
- integration_event
- projection_event
- none_required

Rules:

- operational execution action requires domain event
- IAM/governance action requires security/audit event
- integration request/retry/failure requires integration event
- read-only query usually requires no event unless audit policy says otherwise
- projection update cannot be the only fact

Reject if event map cannot be generated for an operational/governance command.

## Auto-generated Invariant Map

```markdown
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
```

Invariant categories:

- tenant
- scope
- authorization
- session
- station
- operator
- equipment
- state_machine
- event_append_only
- projection_consistency
- quantity
- quality_hold
- material_traceability
- integration_boundary
- auditability
- ai_advisory_only

Reject if critical invariant has no enforcement plan.

## Auto-generated State Transition Map

Required for stateful slices:

```markdown
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
```

Reject if:

- allowed states are not defined
- invalid states are not tested
- transition has no event
- code would directly assign status

## Auto-generated Test Matrix

```markdown
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
```

Required test types:

- happy_path
- invalid_state
- invalid_input
- wrong_tenant
- wrong_scope
- missing_permission
- duplicate_command
- event_payload
- projection_consistency
- db_invariant
- audit_security_event
- regression

## Implementation Gate

Before coding:

```markdown
# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION / BLOCKED_NEEDS_DESIGN / BLOCKED_SCOPE_EXCLUDED

## Reason
...

## Design Evidence Extract
...

## Auto-generated Event Map
...

## Auto-generated Invariant Map
...

## Auto-generated State Transition Map
...

## Auto-generated Test Matrix
...

## Implementation Plan
...
```

Only proceed if:

```text
Verdict before coding = ALLOW_IMPLEMENTATION
```

## Coding After Gate

1. Write tests first from generated test matrix.
2. Run tests and confirm they fail for missing behavior where practical.
3. Implement smallest safe code.
4. Run build/import checks.
5. Run targeted tests.
6. Run relevant regression tests.
7. Update verification report.

## Rejection Rules

Reject if:

- design docs do not define required behavior
- scope is explicitly excluded
- event map is missing
- invariant map is missing
- test matrix is missing
- only happy path tests exist
- state machine is implicit
- event is missing for operational/governance action
- invariant is not enforced
- projection/read model becomes source of truth
- frontend becomes execution or permission truth
- tenant/scope/auth is not server-side
- service layer is bypassed
- broad refactor is mixed with behavior change

## Output After Implementation

```markdown
# Hard Mode MOM v3 Implementation Result

## Verdict
ACCEPT / ACCEPT_WITH_FIXES / REJECT

## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM v3:
- Reason:

## Design evidence used
...

## Generated maps
- Event map:
- Invariant map:
- State transition map:
- Test matrix:

## Tests written first
...

## Implementation summary
...

## Build result
...

## Test result
...

## Verification
...

## Report/docs updates
...

## Remaining gaps
...
```

## Final Principle

Design evidence first.

Generated maps second.

Tests third.

Code fourth.

Verification last.

No design evidence, no invented behavior.
