---
name: flezibcg-ai-brain-v6-auto-execution
description: Main auto-routing engineering brain for FleziBCG. Selects Generic/MOM brain, adaptive mode, and Hard Mode v3 when needed.
---

# FleziBCG AI Brain v6 — Auto-Execution

## Purpose

This skill automatically selects:

1. Brain:
   - Generic Brain
   - MOM Brain

2. Mode:
   - Fast
   - Strict
   - QA
   - Architecture
   - Product
   - Refactor
   - Debug/Triage
   - Release

3. Enforcement:
   - Hard Mode MOM v3 for autonomous/risky MOM implementation
   - Hard Mode MOM v2 for focused review

## Required Output

For every non-trivial task:

```markdown
## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:
```

## Brain Selection

### Use MOM Brain if task touches

- MOM / MES / manufacturing
- station / line / plant / area / equipment
- operator / station session
- production order / work order / operation
- execution / downtime / quantity reporting
- quality hold affecting execution
- material / WIP / traceability / backflush
- manufacturing ERP integration
- OEE / shopfloor / Andon / APS / operational Digital Twin
- IAM/scope/audit foundation for FleziBCG

If ambiguous in the FleziBCG repo, prefer MOM Brain.

### Use Generic Brain if

Task is general software engineering and does not touch MOM-specific logic.

## Mode Selection

### Fast Mode

Small low-risk edits only: copy, formatting, low-risk docs.

Never use for DB/auth/permission/state/workflow/event/data-integrity/migration/integration/production behavior.

### Strict Mode

Use for DB, schema, migration, auth, permission, access control, workflow, state, data integrity, events, integration contracts, concurrency, idempotency, or production-facing behavior.

### QA Mode

Use for test cases, E2E, regression, release verification, user-flow validation, or “try to break this”.

### Architecture Mode

Use for system design, module boundaries, source structure, API/data contract, technology choices, or integration boundary.

### Product Mode

Use for unclear requirements, MVP slicing, roadmap, scope decision, or “should we build this?”.

### Refactor Mode

Use for restructuring without intentional behavior change.

### Debug/Triage Mode

Use for bugs, failing tests, logs, unexpected behavior, or incident-style analysis.

### Release Mode

Use for final readiness, rollout, rollback, migration release, changelog, and go/no-go.


### UI / UX Mode Add-on

If the task touches frontend UI, UX, React, Tailwind, screen packs, Figma Make, Google Stitch, or `DESIGN.md`, also invoke:

```text
docs/ai-skills/stitch-design-md-ui-ux/SKILL.md
```

This add-on is compatible with both Generic Brain and MOM Brain.

If UI work touches execution state, station/session/operator/equipment, quality hold, material impact, allowed actions, tenant/scope/auth, or governed actions, Hard Mode MOM v3 still applies.

Do not let UI implementation fake backend truth, authorization truth, execution state, quality result, ERP posting, backflush completion, or AI deterministic decisions.

## Hard Mode Selection

Use Hard Mode MOM v3 if:

- autonomous implementation
- risky MOM/governance slice
- task touches state/event/invariant/tenant/auth/execution
- agent is expected to code and test

Use Hard Mode MOM v2 if:

- reviewing a small PR
- manually checking existing implementation
- no new behavior coding is requested

## Required Command Pattern for MOM/Governance Actions

```text
command intent
→ load authoritative context
→ validate tenant/scope/auth
→ validate current state, if stateful
→ validate business invariants
→ write append-only domain/security event
→ update projection/read model if applicable
→ return backend-derived result / allowed actions
```

## Forbidden

Do not:

- invent business logic
- use frontend as execution/permission truth
- treat projection/read model as source of truth
- skip event for operational/governance actions
- skip invariant tests
- use Fast Mode for risky tasks
- declare done without verification
