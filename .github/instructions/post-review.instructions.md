---
name: "FleziBCG Post-Review"
description: "Use when closing a spec review, code review, PR review, or design review in FleziBCG. Captures review findings, records reusable lessons, and ensures follow-up actions are explicit before moving on."
---
# Post-Review Workflow

Run this checklist after every non-trivial review session.

## 1. Classify Each Finding

Before closing the review, classify every finding as one of:

- **Critical** — blocks approval or implementation; must be resolved in this slice
- **Major** — must be addressed before production; may go to next slice if tracked
- **Minor** — good-to-have; can be deferred with an explicit note
- **Observation** — no action required; record for awareness only

Do not leave findings as "noted" without a classification.

## 2. Resolve Or Defer Each Finding

For every Critical or Major finding:

- State the recommended fix or the open question it raises.
- Record it in the spec, implementation plan, or test matrix if applicable.
- Do not mark the review closed while a Critical finding is unresolved.

For Minor findings and Observations:

- Optionally note them in an open questions section.
- Do not block slice delivery on them.

## 3. Record Reusable Lessons

After the findings are classified, decide:

- Is there a recurring failure mode or invariant gap that would recur in future reviews?
- Is there a review pattern or domain rule that was not obvious from the docs but is now verified?

If yes:

1. Read `/memories/repo/` to find the best existing file to update.
2. Add one short factual note using the memory `str_replace` or `insert` command.
3. Prefer updating `/memories/repo/flezibcg-notes.md` for general codebase lessons.
4. Create a new memory file only when the lesson belongs to a clearly distinct topic.

## 4. Closeout Statement

The review response must end with:

```
## Review Closeout
- Critical findings: [count or "none"]
- Major findings: [count or "none"]
- Minor/Observation findings: [count or "none"]
- Blocking items resolved: [yes / no / deferred with note]
- Memory updated: [yes — what was recorded / no]
- Next action: [what must happen next]
```
