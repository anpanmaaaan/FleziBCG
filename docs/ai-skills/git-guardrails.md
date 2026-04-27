# Skill: git-guardrails

## Purpose
Prevent AI agents from executing destructive Git commands without explicit human approval.

## Use when
- Working with an AI coding agent.
- You want to block accidental push, reset, clean, or destructive branch operations.
- The repo is important and should not be modified dangerously by automation.

## Commands to block by default
- `git push`
- `git push --force`
- `git reset --hard`
- `git clean -f`
- `git clean -fd`
- `git branch -D`
- `git checkout .`
- `git restore .`

## Copilot note
GitHub Copilot Chat in VSCode does not run shell hooks the same way Claude Code does. For Copilot, use this as a policy file and human checklist.

## Recommended repo policy
Add this rule to `.github/copilot-instructions.md`:

```md
Copilot must never suggest or run destructive Git commands such as push, force push, reset --hard, clean -f, branch -D, checkout ., or restore . unless the user explicitly asks and confirms.
```

## Safe alternatives
- `git status`
- `git diff`
- `git diff --staged`
- `git log --oneline -n 10`
- `git restore --staged <file>` only when explicitly requested

## Output format
```md
# Git Safety Check

## Current status command to run
git status

## Blocked Commands
...

## Safe Workflow
1. Inspect
2. Diff
3. Stage selected files
4. Commit only after user review
```
