# Prompt — Upgrade P0-A Slices to Hard Mode MOM v3

```text
Follow docs/ai-skills/hard-mode-mom-v3/SKILL.md.

Task:
Upgrade existing P0-A foundation slices to Hard Mode MOM v3.

Target slices:
1. Tenant foundation
2. IAM user lifecycle
3. Role/action/scope assignment
4. Audit/security event foundation

Goal:
For each slice, read design docs and auto-generate:
- design evidence extract
- event map
- invariant map
- test matrix

Then patch implementation/tests only where needed.

Do not implement future scope:
- ERP Integration
- Acceptance Gate
- Backflush
- APS
- AI
- Digital Twin
- Compliance/e-record
- full Station Execution refactor
- claim removal

Required for every governed action:
- security/governance event decision
- tenant/scope invariant
- server-side authorization invariant
- negative tests
- verification report update

If design does not define a behavior, mark it:
BLOCKED_NEEDS_DESIGN

If phase boundary excludes it, mark it:
BLOCKED_SCOPE_EXCLUDED

Do not invent policy.
```
