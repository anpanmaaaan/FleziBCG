# Copilot Addendum — Hard Mode MOM v3

Hard Mode MOM v3 supersedes v2 for autonomous implementation.

Use:

```text
docs/ai-skills/hard-mode-mom-v3/SKILL.md
```

## Required before coding

- Design Evidence Extract
- Event Map
- Invariant Map
- State Transition Map if stateful
- Test Matrix
- Verdict before coding

## Reject if

- maps are missing
- tests are happy-path only
- design evidence is missing
- behavior is excluded by phase boundary
- code invents business logic
- event is missing for operational/governance action
- invariant is missing
- projection/read model is source of truth
- UI is execution/permission truth
