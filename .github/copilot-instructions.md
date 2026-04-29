# GitHub Copilot Instructions — FleziBCG AI Brain Enterprise v4 — Stitch UI

## Entry Rule

Before non-trivial work, read in order:

1. `.github/agent/AGENT.md` if present
2. `docs/design/INDEX.md`
3. `docs/design/AUTHORITATIVE_FILE_MAP.md`
4. `docs/governance/CODING_RULES.md`
5. `docs/governance/ENGINEERING_DECISIONS.md`
6. `docs/governance/SOURCE_STRUCTURE.md`
7. `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`

This file is not the authoritative source for business logic. Design and governance docs are.

## Default AI Skill

Use:

```text
docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
```

## Required Routing Output

For every non-trivial task:

```markdown
## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:
```

## Hard Mode MOM v3

Hard Mode MOM v3 is mandatory for autonomous implementation and risky changes.

Use:

```text
docs/ai-skills/hard-mode-mom-v3/SKILL.md
```

Hard Mode MOM v3 triggers when work touches:

- execution state machine
- execution commands/events
- projections/read models
- station/session/operator/equipment
- production reporting
- downtime
- completion/closure
- quality hold
- material/inventory execution impact
- tenant/scope/auth
- IAM lifecycle
- role/action/scope assignment
- audit/security event
- critical invariant
- DB migration enforcing governance or operational truth

Before coding under v3, the agent must generate:

1. Design Evidence Extract
2. Event Map
3. Invariant Map
4. State Transition Map if stateful
5. Test Matrix
6. Verdict before coding

If any is missing: reject implementation.

## Hard Mode MOM v2

Use v2 for smaller/manual reviews:

```text
docs/ai-skills/hard-mode-mom-v2/SKILL.md
```

## FE / UI / UX Work — Stitch DESIGN.md Integration

When the task touches frontend UI, UX design, React components, Tailwind styling, Figma Make, Google Stitch, `DESIGN.md`, screen packs, or design consistency, read:

```text
docs/ai-skills/stitch-design-md-ui-ux/SKILL.md
DESIGN.md
docs/design/DESIGN.md
docs/audit/frontend-source-alignment-snapshot.md
```

If `docs/audit/frontend-source-alignment-snapshot.md` is missing, do not invent current frontend source status. Either inspect source directly or create the snapshot first.

For UI work, also keep the legacy enforcer available:

```text
docs/ai-skills/design-system-enforcer/SKILL.md
```

This UI/UX skill does not override Hard Mode MOM.

If a UI task touches execution, quality, material, station, operation, tenant/scope/auth, governed actions, allowed actions, operational status, or event/projection truth, also apply:

```text
docs/ai-skills/hard-mode-mom-v3/SKILL.md
```

Hard reject UI output that fakes backend truth, authorization, execution transitions, quality pass/fail, ERP posting, backflush completion, or deterministic AI decisions.

## Non-negotiables

- Backend is source of truth.
- Frontend sends intent only.
- Frontend does not derive execution state.
- Frontend does not decide authorization.
- Events are append-only operational facts.
- Projections are read models.
- JWT proves identity only.
- Authorization is server-side.
- AI is advisory only.
- Critical invariants must not rely only on UI validation.
- Do not invent product scope.
- Work in vertical slices.
- Prefer behavior-based tests.
- Do not use destructive Git commands unless explicitly requested and confirmed.
