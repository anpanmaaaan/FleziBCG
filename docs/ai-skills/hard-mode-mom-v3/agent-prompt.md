# Prompt — Hard Mode MOM v3

```text
Follow docs/ai-skills/hard-mode-mom-v3/SKILL.md.

Use Hard Mode MOM v3:
auto-generate event map + invariant map + test matrix from design docs before coding.

Task:
<PASTE TASK HERE>

Mandatory flow:

1. Read relevant design docs using:
   - docs/design/INDEX.md
   - docs/design/AUTHORITATIVE_FILE_MAP.md
   - governance docs
   - relevant domain docs

2. Produce Design Evidence Extract.

3. Auto-generate:
   - Event Map
   - Invariant Map
   - State Transition Map if stateful
   - Test Matrix

4. Decide:
   - ALLOW_IMPLEMENTATION
   - BLOCKED_NEEDS_DESIGN
   - BLOCKED_SCOPE_EXCLUDED

5. If allowed:
   PLAN → TEST FIRST → CODE → BUILD → TEST → VERIFY → REPORT

Reject implementation if:
- design evidence is missing
- event map is missing
- invariant map is missing
- test matrix is missing
- behavior is excluded by phase boundary
- state machine is implicit
- required event is missing
- required invariant is missing
- tests are happy-path only

Do not invent business logic.
```
