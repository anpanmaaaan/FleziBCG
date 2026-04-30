---
name: design-md-ui-governor
description: Use this skill for FleziBCG UI/UX design, Figma Make/Stitch output, DESIGN.md governance, frontend screen packs, component styling, responsive behavior, and source-aligned UI implementation.
---

# Skill — DESIGN.md UI Governor for FleziBCG

## Purpose

This skill integrates the DESIGN.md pattern into FleziBCG's internal AI brain.

Use it to make UI output:

- visually consistent;
- source-aligned;
- manufacturing-operations appropriate;
- responsive and touch-aware;
- truthful about backend/data readiness;
- safe against frontend business-truth leakage.

This skill governs UI design and frontend implementation guidance only. It does not override domain, backend, authorization, event, API, or database contracts.

---

## When to Use

Use this skill when a task touches:

- `DESIGN.md` creation/update;
- Figma Make / Google Stitch / design-md output;
- frontend screens;
- React components;
- Tailwind styling;
- screen packs;
- navigation/app shell;
- status badges;
- responsive/touch behavior;
- UI implementation prompts;
- UI review reports.

Also use it when reviewing whether UI output is too generic, too decorative, or unsafe for MOM execution.

---

## Mandatory Reading Order

Before non-trivial UI work, read:

1. `.github/copilot-instructions.md`
2. `DESIGN.md`
3. `docs/design/DESIGN.md` if present
4. `docs/ai-skills/design-md-ui-governor/SKILL.md`
5. `docs/ai-skills/design-md-ui-governor/references/design-md-format-rules.md`
6. `docs/ai-skills/design-md-ui-governor/references/flezibcg-mom-ui-guardrails.md`
7. `docs/ai-skills/design-md-ui-governor/references/source-alignment-rules.md`
8. `docs/audit/frontend-source-alignment-snapshot.md` if present
9. relevant UI/screen inventory docs
10. relevant domain contract docs if the UI touches execution, quality, material, integration, IAM, scope, or audit.

If `docs/audit/frontend-source-alignment-snapshot.md` is missing and the task depends on current frontend structure, inspect the source directly or stop and create the snapshot first.

---

## Mandatory Co-Skills

Use `hard-mode-mom-v3` in addition to this skill when UI touches:

- execution state machine;
- execution commands/events;
- projections/read models;
- station/session/operator/equipment;
- production reporting;
- downtime;
- quality hold/evaluation;
- material/inventory execution impact;
- tenant/scope/auth;
- role/action/scope assignment;
- audit/security events;
- any critical invariant.

Use implementation slicing rules if the user asks for a coding-agent prompt.

---

## Core Rules

### 1. DESIGN.md is UI style authority only

`DESIGN.md` defines visual and interaction style. It does not define business semantics.

### 2. Backend remains source of truth

Frontend must not decide:

- execution state;
- authorization;
- allowed actions;
- quality pass/fail;
- acceptance gate result;
- ERP posting state;
- backflush completion;
- AI deterministic outcome;
- digital twin truth.

### 3. Source alignment first

Do not redesign from zero if existing source screens/components already exist and are usable.

Preserve and extend existing patterns unless explicitly tasked to migrate them.

### 4. Screen phase discipline

Every screen must be one of:

- `ACTIVE`
- `PARTIAL`
- `MOCK`
- `SHELL`
- `FUTURE`
- `DISABLED`

Never present future functionality as working.

### 5. Industrial UX discipline

Operator/shopfloor UI must be:

- readable at distance;
- touch-friendly;
- action-oriented;
- state-first;
- blocker-visible;
- not cluttered by dashboard decorations.

### 6. Responsive is mandatory

Every UI task must declare responsive behavior for desktop, tablet, and constrained width.

For Station Execution, tablet/touch behavior matters more than dense desktop grids.

### 7. i18n and status discipline

User-facing strings must go through i18n where current repo rules require it.

Status labels must map to stable codes or clearly declared placeholder states.

---

## Required Output for UI Tasks

```markdown
# UI/UX Implementation Report

## Selected Skill
- design-md-ui-governor

## Source Inputs Read

## Scope

## Design System Alignment

## Source Alignment

## Files Changed

## Screens Affected

## Components Added / Updated

## Data Source Status
ACTIVE / PARTIAL / MOCK / SHELL / FUTURE / DISABLED

## MOM Safety Check
- Backend truth respected:
- Permission truth respected:
- Execution state truth respected:
- Quality truth respected:
- Integration/ERP truth respected:
- AI/Digital Twin truth respected:

## Responsive / Accessibility Check

## Tests / Build Run

## Known Limitations

## Next Recommended FE Slice
```

---

## Hard Reject Conditions

Reject or stop if UI work:

- fakes backend truth;
- hardcodes permission truth;
- derives execution state in frontend;
- fakes quality pass/fail;
- fakes acceptance gate approval;
- fakes ERP posting success;
- fakes backflush completion;
- treats AI insight as deterministic authority;
- makes digital twin visualization look authoritative without backend/twin state evidence;
- creates active screens for future scope without labels;
- redesigns the entire app shell without explicit scope;
- mixes mock data into production API paths;
- ignores responsive/touch constraints for station/operator screens;
- copies third-party brand design language as FleziBCG identity.
