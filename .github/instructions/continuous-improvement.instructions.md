---
name: "FleziBCG Continuous Improvement"
description: "Use when closing a non-trivial FleziBCG task, handling user feedback, fixing a bug, reviewing a failure, or refining an implementation after comments. Captures reusable lessons and updates repo memory so the agent improves over time."
---
# Continuous Improvement Guidance

Use this workflow after each non-trivial task, after meaningful user comments, and after each bug or failed validation that reveals a reusable lesson.

## Goal

- Improve future task execution without broadening scope mid-task.
- Turn mistakes, feedback, and validation outcomes into short reusable operating notes.
- Prefer repo memory for codebase-specific lessons and user memory only for durable cross-workspace preferences.

## When To Record A Lesson

Record or update memory when one of these is true:

- A bug exposed a recurring failure mode.
- A validation failure taught a repeatable repo-specific rule.
- A user correction clarified a stable preference or expectation.
- A repo command, test pattern, migration caveat, or environment quirk was verified.
- A previous assumption turned out wrong and the correction is likely reusable.

Do not record memory for one-off trivia, speculative guesses, or temporary noise.

## Specialized Workflows

For focused review closeout, follow `.github/instructions/post-review.instructions.md`.
For bug fixes and failed validations, follow `.github/instructions/post-bugfix.instructions.md`.

## How To Improve After Each Task

1. Compare outcome versus the original intent.
2. Identify one concrete thing that went well or failed.
3. Decide whether the lesson belongs in:
   - `/memories/repo/` for repo-specific facts, commands, test patterns, or architecture caveats
   - `/memories/` for durable user preferences across workspaces
   - no memory update if the lesson is not reusable
4. Keep the note short, factual, and action-oriented.
5. Before creating a new memory file, read `/memories/repo/` to find the best existing file to update.
6. Use the memory tool `view` command to read existing files, `str_replace` to update them, and `insert` to append new entries.

## After User Comments

- Treat corrections as high-signal feedback.
- If the feedback changes a stable workflow expectation, record it.
- On the next relevant task, actively apply the stored lesson instead of rediscovering it.

## After Bugs Or Failed Checks

- Name the failed assumption.
- Prefer the smallest correction that changes future behavior.
- Record the root cause and the reliable guard or validation that catches it earlier next time.

## Required Behavior In Final Responses

- If a reusable lesson was discovered, mention briefly that the workflow was updated or memory was captured.
- Do not dump raw memory content unless asked.
- Keep the closeout focused on the task outcome first.
