# Skill: migrate-to-shoehorn

## Purpose
Migrate TypeScript test files away from unsafe `as` type assertions toward `@total-typescript/shoehorn` helpers.

## Use when
- Tests use excessive `as SomeType`.
- Fixtures need partial or mock typed data.
- Type assertions hide missing required fields.

## Process
1. Find test files with `as` assertions.
2. Classify assertions:
   - Safe literal narrowing
   - Unsafe fixture construction
   - Mock object shaping
3. Replace unsafe fixture assertions with shoehorn helpers.
4. Keep runtime behavior unchanged.
5. Run typecheck and tests.

## Output format
```md
# Shoehorn Migration Plan

## Files Found
## Unsafe Assertions
## Proposed Replacements
## Validation
```

## Rules
- Do not modify production code unless needed.
- Do not weaken types to make tests pass.
- Prefer explicit fixture builders.
- Keep test intent readable.
