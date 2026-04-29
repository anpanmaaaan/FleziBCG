Follow docs/ai-skills/autonomous-implementation-agent/SKILL.md.
Follow docs/ai-skills/hard-mode-mom-v3/SKILL.md.

Task:
Continue autonomous implementation from the current repo state.

Required loop:

PLAN
→ HARD MODE MOM v3 GATE
→ TEST FIRST
→ CODE
→ BUILD
→ TEST
→ VERIFY
→ UPDATE REPORT
→ NEXT SLICE

Rules:

1. Do not stop after one slice.
2. If a slice is blocked, mark BLOCKED_NEEDS_DESIGN or BLOCKED_SCOPE_EXCLUDED and continue to the next safe slice.
3. Do not invent business logic.
4. Do not implement excluded future scope.
5. Use design docs to generate event map, invariant map, and test matrix before coding.
6. Write tests first from the generated matrix.
7. Run build/test verification.
8. Update reports after every slice.

Current priority:

1. Upgrade existing P0-A slices to Hard Mode MOM v3.
2. Complete remaining P0-A codeable items.
3. Move to P0-B only when P0-A is stable.
