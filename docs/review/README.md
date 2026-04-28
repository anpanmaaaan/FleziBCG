# FleziBCG Review Gates

This folder contains PR review checklists.

## Files

- `pr-hard-mode-checklist.md`: reviewer checklist for PRs, especially MOM-critical changes.

## How to use

1. Create PR.
2. Fill `.github/pull_request_template.md`.
3. GitHub Actions runs `.github/workflows/pr-gate.yml`.
4. If PR touches MOM-critical files, Hard Mode MOM gate runs.
5. Reviewer uses `docs/ai-skills/pr-gate-reviewer.md`.
