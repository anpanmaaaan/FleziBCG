# AI Interaction with Planning and Scheduling

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.1 | Reframed APS as a first-class module and this file as its AI interaction note. |

Status: AI/APS interaction note.

## Scope

Planning & Scheduling (APS) is a first-class platform module.
This file describes how AI interacts with APS.

For domain ownership of APS itself, see:
- `../02_domain/planning/planning-and-scheduling-domain.md`

## AI role in APS

AI remains advisory-first.
It may provide:
- sequencing hints
- delay-risk views
- resource-conflict prediction
- what-if comparisons
- replanning recommendations later

It must not silently rewrite execution truth or bypass governance.
