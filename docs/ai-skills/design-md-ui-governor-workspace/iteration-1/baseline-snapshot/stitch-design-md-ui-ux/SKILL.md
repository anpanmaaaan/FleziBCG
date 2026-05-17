---
name: stitch-design-md-ui-ux
description: FleziBCG-native FE/UI/UX skill inspired by Google Stitch design-md. Enforces DESIGN.md, source alignment, React/Tailwind consistency, and MOM-safe frontend boundaries.
---

# Skill — Stitch DESIGN.md UI/UX Enforcer for FleziBCG

## Purpose

Use when task touches frontend UI/UX, React components, Tailwind, design system consistency, Google Stitch/Figma Make, DESIGN.md, UI refactor, screen-pack, frontend source alignment.

Goal: visually consistent, source-aligned, design-system-aware, implementation-ready, MOM-safe.

## Core UI Principles

1. Backend is source of truth — FE must not decide execution state, authorization, allowed actions, quality result, acceptance, ERP posting, backflush, AI deterministic conclusions.
2. Persona is UX only — backend enforces permissions.
3. MOM UI must be operationally clear — current state, next safe action, blockers obvious, elapsed/target/context, clear status labels.
4. Industrial UX constraints — large touch targets, dominant primary action, readable at distance, no tiny text, no hover-only controls, confirmation for destructive.
5. Screen phase discipline — ACTIVE/PARTIAL/MOCK/SHELL/FUTURE/DISABLED.

## React/Tailwind Rules

Use existing app shell. Preserve route structure. Prefer reusable components. Avoid one-off styling. Tailwind consistently. Small readable components. Separate mock from production. Don't hardcode backend truth. Don't invent API fields, permissions, or state transitions.

## Route Accessibility Gate

For new route: registered in router, nested under correct layout, not swallowed by index/catch-all, auth guard understood, persona enforcement updated, sidebar entry exists, screenStatus entry exists, direct URL smoke-tested.

## Component Quality Checklist

Follows DESIGN.md, works with shell, has loading/error/empty states, no fake auth, no fake backend state, no future scope as active, clear naming, reusable.

## UI Output Format

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
## MOM Safety Check
## Tests / Build Run
## Known Limitations
## Next Recommended FE Slice
## Route Accessibility Verification
```

## Hard Reject Rules

Frontend as source of execution state, hardcoded allowed actions, faked quality/acceptance/ERP/backflush, AI as deterministic, active screens for future scope without labels, redesigns shell without approval, mocks in production paths.
