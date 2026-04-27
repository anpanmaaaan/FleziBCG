# Skill: setup-pre-commit

## Purpose
Set up pre-commit quality checks using tools such as Husky, lint-staged, Prettier, type checking, and tests.

## Use when
- A repo lacks local quality gates.
- You want to prevent formatting/type/test regressions before commit.
- You need consistent contributor workflow.

## Process
1. Detect package manager.
2. Inspect existing scripts.
3. Add missing scripts carefully.
4. Install/configure Husky.
5. Configure lint-staged.
6. Add checks:
   - Formatting
   - Linting
   - Type checking
   - Relevant tests
7. Verify with a dry run.

## Output format
```md
# Pre-commit Setup Plan

## Existing Scripts
## Proposed Tools
## Files To Change
## Commands
## Verification
```

## Rules
- Do not overwrite existing scripts blindly.
- Keep hooks fast.
- Prefer staged-file checks where possible.
- Full test suites may belong in CI, not pre-commit.
