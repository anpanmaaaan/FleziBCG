# DESIGN.md Format Rules

## Purpose

DESIGN.md is an AI-readable markdown design-system file.

It should be structured enough for coding/design agents to apply consistently without a parser, JSON schema, or Figma export.

## Required Sections for FleziBCG

A FleziBCG DESIGN.md should include:

1. Visual Theme & Atmosphere
2. Color Palette & Roles
3. Typography Rules
4. Component Stylings
5. Layout Principles
6. Depth & Elevation
7. Do's and Don'ts
8. Responsive Behavior
9. Agent Prompt Guide
10. FleziBCG-Specific UI Contracts
11. Review Checklist

## Rules

- Keep design instructions concrete.
- Include semantic tokens and usage, not just color names.
- Include component behavior and states.
- Include responsive behavior.
- Include do-not-fake rules for MOM truth.
- Include operator/shopfloor-specific constraints.
- Do not copy another brand identity into FleziBCG.
- Do not let DESIGN.md override domain contracts.

## Good DESIGN.md Content

- clear visual personality;
- semantic status mapping;
- typography hierarchy;
- button/table/card/modal/timeline rules;
- layout density rules;
- touch target expectations;
- empty/loading/error state rules;
- agent prompt guide;
- review checklist.

## Bad DESIGN.md Content

- vague mood words only;
- external brand mimicry;
- color tokens without usage;
- UI rules that imply backend behavior;
- missing responsive guidance;
- no source-alignment instruction;
- future functionality presented as active.
