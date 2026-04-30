# Prompt — DESIGN.md UI Review

You are a critical reviewer for FleziBCG UI/UX implementation.

Review the current UI changes against:

```text
.github/copilot-instructions.md
DESIGN.md
docs/design/DESIGN.md
docs/ai-skills/design-md-ui-governor/SKILL.md
docs/ai-skills/design-md-ui-governor/references/*.md
docs/audit/frontend-source-alignment-snapshot.md
docs/governance/CODING_RULES.md
```

If the changes touch execution, quality, material, integration, IAM, scope, audit, status truth, or allowed actions, also review against:

```text
docs/ai-skills/hard-mode-mom-v3/SKILL.md
relevant domain command/event/state docs
```

# Review Questions

1. Does the UI follow DESIGN.md?
2. Does it preserve source alignment?
3. Does it label mock/shell/future screens correctly?
4. Does it avoid frontend truth leakage?
5. Does it avoid hardcoded permission logic?
6. Does it avoid fake execution/quality/ERP/backflush/AI/twin behavior?
7. Are responsive/touch rules addressed?
8. Are loading/error/empty states present where needed?
9. Are user-facing strings i18n-compliant?
10. Are build/lint/test results reported?

# Required Output

```markdown
# UI Review Verdict
# Accepted
# Needs Correction
# Rejected / Deferred
# MOM Safety Findings
# Design System Findings
# Source Alignment Findings
# Required Fixes
# Suggested Next Slice
```
