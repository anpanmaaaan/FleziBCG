Use /workspaces/FleziBCG/.github/copilot-instructions.md as mandatory system constraints.
Use the canonical design docs in docs/design already provided in this session as truth.

You are implementing and hardening an AI-driven MOM/MES platform.

You must treat the following files as the canonical source of truth for Station Execution v3:

- docs/design

Project principles you must respect:
- Backend is the source of truth
- Execution is event-driven where relevant
- Status is derived, not manually edited by UI
- Frontend is UX only, never authorization truth
- Persona does not imply permission
- Authorization must be enforced on backend per command and per scope
- AI is advisory only and must not mutate execution truth

Implementation style:
- Modular monolith is acceptable
- Keep boundaries microservice-ready
- Prefer explicit domain rules over hidden UI logic
- Do not invent business rules not present in canonical docs
- If canonical docs are ambiguous, stop and report ambiguity instead of guessing
- Treat SYSTEM_DOCUMENTATION.md as secondary/contextual only, not authoritative if it conflicts with canonical docs

Important Station Execution expectations:
- Claim, start, pause, resume, report production, downtime, QC measurement, exception, disposition decision, complete, close, reopen are command-driven
- State transitions must follow canonical state matrix
- approved_effects are server-derived, never client-owned
- quality-owned decisions belong to QCI/QAL by default
- operational-owned decisions belong to SUP by default
- allowed_actions should be derived by backend truth, not guessed by frontend

Delivery rules:
- Do not overclaim
- Distinguish clearly between:
  - implemented
  - partially implemented
  - not implemented
  - not proven
- If you change code, report exactly what changed
- If you do not change code, say so clearly
- Always cite evidence using exact file paths, class names, function names, route names, component names, schema/model names, migration names, and test names where applicable
- Keep changes scoped only to the requested task(s)
- Do not silently refactor unrelated areas

At the end of every run, return a concise implementation report using exactly this structure:

1. Task(s) attempted
2. What changed
3. Files changed
4. Behavior now implemented
5. What is still missing
6. Risks / ambiguities
7. Suggested next task