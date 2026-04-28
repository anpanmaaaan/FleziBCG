# Adaptive Mode Router

Select the lightest safe mode.

Modes:
- Fast
- Strict
- QA
- Architecture
- Product
- Refactor
- Debug/Triage
- Release

Never use Fast Mode for DB, auth, permission, tenant/scope, state/workflow, event/projection, data integrity, migration, integration, or production-facing behavior.
