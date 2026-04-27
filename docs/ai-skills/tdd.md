# Skill: tdd

## Purpose
Use test-driven development with a red-green-refactor loop.

## Core principle
Tests should verify behavior through public interfaces, not implementation details.

## Good tests
- Exercise real code paths.
- Read like specifications.
- Verify observable behavior.
- Survive internal refactors.

## Bad tests
- Test private methods.
- Mock internal collaborators unnecessarily.
- Break when implementation changes but behavior does not.
- Query internals instead of using public interfaces.

## Anti-pattern: horizontal slicing
Do not write all tests first and then all implementation.

Prefer vertical TDD:

```text
RED: write one failing behavior test
GREEN: implement minimal code
REFACTOR: clean up safely
repeat
```

## Process
1. Confirm the public interface.
2. List the most important behaviors.
3. Pick one behavior.
4. Write one failing test.
5. Implement the smallest code needed to pass.
6. Run tests.
7. Refactor only when green.
8. Repeat.

## Output format
```md
# TDD Plan

## Public Interface
## Behaviors to Test
## First Tracer Bullet

### RED
<test>

### GREEN
<minimal implementation>

### REFACTOR
<safe cleanup>

## Next Cycles
```

## Checklist per cycle
- [ ] Test describes behavior, not implementation.
- [ ] Test uses public interface only.
- [ ] Test would survive internal refactor.
- [ ] Code is minimal for this test.
- [ ] No speculative features added.
- [ ] Refactor only while green.
