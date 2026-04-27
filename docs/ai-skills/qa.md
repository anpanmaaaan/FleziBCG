# Skill: qa

## Purpose
Review a change, feature, or document for quality before release or handoff.

## Use when
- A feature is implemented but needs verification.
- A document needs consistency review.
- A PR needs a checklist-style QA pass.

## Process
1. Define the QA target.
2. Identify acceptance criteria.
3. Check behavior against criteria.
4. Check edge cases.
5. Check docs/tests if relevant.
6. Categorize findings by severity.

## Output format
```md
# QA Report

## Scope
## Acceptance Criteria Checked
## Findings

### Critical
### Major
### Minor
### Suggestions

## Pass / Fail
## Required Fixes Before Merge
```

## Rules
- Distinguish defects from suggestions.
- Do not expand scope mid-QA.
- Cite files/sections when possible.
