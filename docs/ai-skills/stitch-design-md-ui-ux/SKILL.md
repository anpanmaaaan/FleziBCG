---
name: stitch-design-md-ui-ux
description: FleziBCG-native FE/UI/UX skill inspired by Google Stitch design-md. Enforces DESIGN.md, source alignment, React/Tailwind consistency, and MOM-safe frontend boundaries.
---

# Skill — Stitch DESIGN.md UI/UX Enforcer for FleziBCG

## Purpose

Use this skill when the task touches:

- frontend UI or UX layout
- React components or page shells
- Tailwind styling
- design system consistency
- Google Stitch / Figma Make output
- `DESIGN.md` generation or update
- UI refactor or screen-pack implementation
- frontend source alignment

This skill adapts the Google Stitch `design-md` pattern into the FleziBCG AI Brain.

The goal is to make frontend output:

- visually consistent
- source-aligned
- design-system-aware
- implementation-ready
- MOM-safe

---

## Mandatory Inputs

Before designing or coding UI, read:

1. `DESIGN.md`
2. `docs/design/DESIGN.md` if present
3. `docs/audit/frontend-source-alignment-snapshot.md` if present
4. `docs/design/05_application/fe-screen-inventory-and-navigation-map.md` if present
5. `docs/design/05_application/screen-map-and-navigation-architecture.md` if present
6. `docs/design/07_ui/ui-pack-roadmap.md` if present
7. `.github/copilot-instructions.md`

If the task touches execution UI, also read:

8. `docs/design/02_domain/execution/station-execution-state-matrix-v4.md` if present
9. `docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md` if present
10. `docs/ai-skills/hard-mode-mom-v3/SKILL.md`

---

## Core UI Principles

### 1. Backend is source of truth

Frontend must not decide:

- execution state
- authorization
- allowed actions
- quality result
- acceptance status
- ERP posting status
- backflush completion
- AI deterministic conclusions

Frontend may only display backend-derived truth.

### 2. Persona is UX only

Frontend may organize navigation by persona, but persona must not be treated as permission.

Do not hide/show critical functionality as the only authorization control. Backend must enforce permissions.

### 3. MOM UI must be operationally clear

For operator/supervisor screens:

- prioritize current state
- show next safe action
- make blockers obvious
- surface elapsed time, target, and status context where useful
- avoid ambiguous color-only meaning
- use clear status labels

### 4. Industrial UX constraints

For shopfloor screens:

- touch targets should be large
- primary action should be visually dominant
- critical state should be readable at distance
- avoid tiny text for operator-critical data
- avoid hidden hover-only controls
- use confirmation for destructive or governed actions

### 5. Screen phase discipline

Every screen must be labelled internally as one of:

- `ACTIVE`
- `PARTIAL`
- `MOCK`
- `SHELL`
- `FUTURE`
- `DISABLED`

Future screens may exist as placeholders, but must not pretend to be implemented.

---

## DESIGN.md Responsibilities

When asked to generate or update `DESIGN.md`, produce or preserve a markdown design system with:

1. Product visual identity
2. Design principles
3. Layout system
4. Typography
5. Color tokens
6. Semantic colors
7. Status colors
8. Spacing scale
9. Component patterns
10. Navigation patterns
11. Form patterns
12. Table/data-grid patterns
13. Operator cockpit patterns
14. Supervisor dashboard patterns
15. Empty/loading/error states
16. Accessibility rules
17. Do-not-fake rules
18. MOM-specific UI constraints

---

## React / Tailwind Implementation Rules

When implementing UI:

- Use existing app shell if present.
- Preserve existing route structure unless the task explicitly requires change.
- Prefer reusable components.
- Avoid one-off styling chaos.
- Use Tailwind consistently.
- Keep components readable and small.
- Separate mock data from production code.
- Do not hardcode backend truth.
- Do not invent API fields.
- Do not invent permissions.
- Do not invent state transitions.

---

## Component Quality Checklist

Before finalizing a UI component, verify:

- It follows `DESIGN.md`.
- It works with the existing app shell.
- It has loading state when data-driven.
- It has error state when data-driven.
- It has empty state when list/data-driven.
- It does not fake auth.
- It does not fake backend-derived state.
- It does not introduce future scope as active functionality.
- It uses clear naming.
- It is reusable where reasonable.

---

## UI Output Format

For every FE/UI task, output:

```md
# UI/UX Implementation Report

## Selected Skill
stitch-design-md-ui-ux

## Source Inputs Read

## Design System Alignment

## Files Changed

## Screens Affected

## Components Added / Updated

## Data Source Status
CONNECTED / MOCK / SHELL / FUTURE

## MOM Safety Check
- Backend truth respected:
- Permission truth respected:
- State machine respected:
- Event/operation truth respected:

## Tests / Build Run

## Known Limitations

## Next Recommended FE Slice
```

---

## Hard Reject Rules

Reject or stop if the implementation:

- makes frontend the source of execution state
- hardcodes allowed actions
- fakes quality pass/fail
- fakes acceptance gate approval
- fakes ERP posting success
- fakes backflush completion
- treats AI insight as deterministic truth
- creates active screens for future scope without labelling them
- redesigns the entire app shell without approval
- mixes mock data into production API paths
