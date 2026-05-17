---
name: stitch-design-md-ui-ux
description: |
  DEPRECATED (2026-05-17). Consolidated into design-md-ui-governor. Do not load
  this skill independently. If the user mentions Stitch, Figma Make, design-md
  output, or FE/UI work, load design-md-ui-governor instead.
---

# DEPRECATED — Consolidated

This skill has been folded into `design-md-ui-governor` as of 2026-05-17.

**Replacement skill:** `docs/ai-skills/design-md-ui-governor/SKILL.md`

**Reason for consolidation:**

- Three UI/UX skills (`stitch-design-md-ui-ux`, `design-md-ui-governor`,
  `design-system-enforcer`) covered overlapping responsibility with confusing
  routing rules.
- Agents could not reliably choose between them.
- Content was duplicated; updates drifted out of sync.

**What was migrated to `design-md-ui-governor`:**

- React/Tailwind implementation rules (this file's strength) → SKILL.md §§ 2, 5, 8.
- Route accessibility gate → SKILL.md § 7.
- Persona route enforcement → SKILL.md § 5.2.
- UI output report format → SKILL.md § 9.
- Hard reject rules → SKILL.md § 10.
- Stitch / Figma Make / design-md handling guidance → SKILL.md § 3 (when to use).

**Do not** load this skill in parallel with `design-md-ui-governor`. Loading
both wastes context and risks contradictions.

If an external doc or prompt still references this skill, treat the reference
as an alias for `design-md-ui-governor`.
