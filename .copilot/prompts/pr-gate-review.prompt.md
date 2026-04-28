Follow docs/ai-skills/pr-gate-reviewer.md.

Review this PR using FleziBCG PR Gate.

Inputs:
- PR title: {{title}}
- PR description: {{description}}
- Changed files: {{changed_files}}
- Diff: {{diff}}

Required:
1. Classify PR.
2. Select Generic or MOM Brain.
3. Select mode.
4. Turn Hard Mode MOM ON if triggered.
5. Give APPROVE / REQUEST_CHANGES / COMMENT_ONLY.
6. Reject if state machine/event/invariant rules are violated.
