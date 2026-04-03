# AI_GUARDRAILS

## Purpose
Capture explicit non-goals and boundaries for AI-related capabilities.

## Scope
- Current and near-term AI constraints
- Separation from execution control

## Key Decisions (LOCKED)
- AI is not part of execution control.
- AI cannot trigger start/report/complete actions.
- AI logic is excluded from execution and service layers in current phases.
- Execution and dashboard outcomes remain deterministic and backend-owned.

## Explicitly Out Of Scope
- AI-based scheduling or dispatch decisions
- AI-generated execution state changes
- AI workflow orchestration in runtime paths

## Future (FUTURE)
- Advisory-only AI insights may consume read data if governance remains read-only.
