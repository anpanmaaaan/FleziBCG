---
name: design-system-enforcer
description: |
  DEPRECATED (2026-05-17). Consolidated into design-md-ui-governor. Do not load
  this skill independently. If the user mentions DESIGN.md enforcement, design
  system, or FE/UI governance, load design-md-ui-governor instead.
---

# DEPRECATED — Consolidated

This skill has been folded into `design-md-ui-governor` as of 2026-05-17.

**Replacement skill:** `docs/ai-skills/design-md-ui-governor/SKILL.md`

**Reason for consolidation:**

- Three UI/UX skills (`design-system-enforcer`, `design-md-ui-governor`,
  `stitch-design-md-ui-ux`) covered overlapping responsibility.
- This skill was the most lightweight (essentially a rejection checklist) — its
  content now lives in SKILL.md § 8 (Component Quality Checklist) and § 10
  (Hard Reject Conditions) of `design-md-ui-governor`.

**Do not** load this skill in parallel with `design-md-ui-governor`. If an
external doc or prompt still references this skill, treat the reference as an
alias for `design-md-ui-governor`.
