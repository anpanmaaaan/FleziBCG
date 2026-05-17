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

---

## Core Rules

### 1. DESIGN.md is UI style authority only
### 2. Backend remains source of truth
### 3. Source alignment first
### 4. Screen phase discipline (ACTIVE/PARTIAL/MOCK/SHELL/FUTURE/DISABLED)
### 5. Industrial UX discipline — readable at distance, touch-friendly, action-oriented
### 6. Responsive is mandatory
### 7. i18n and status discipline

---

## Required Output for UI Tasks

```markdown
# UI/UX Implementation Report
## Selected Skill
## Source Inputs Read
## Scope
## Design System Alignment
## Source Alignment
## Files Changed
## Screens Affected
## Components Added / Updated
## Data Source Status
## MOM Safety Check
## Responsive / Accessibility Check
## Tests / Build Run
## Known Limitations
## Next Recommended FE Slice
```

## Hard Reject Conditions

Reject if UI fakes backend truth, hardcodes permissions, derives execution state in FE, fakes quality, fakes acceptance gate, fakes ERP posting, treats AI as deterministic, creates active screens for future scope without labels, redesigns shell without scope, mixes mock data into production paths, ignores responsive/touch, copies third-party brand.
