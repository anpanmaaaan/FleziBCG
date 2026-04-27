# FleziBCG Latest Design Pack — 2026-04-27

## Status

**Latest repo-ready design pack rebuilt for download.**

This package consolidates the currently available design baseline with the latest accepted governance updates:

```text
Latest consolidated design baseline 2026-04-26
+ Hardening v1
+ Hardening Housekeeping v1.1
+ Source Code Audit Response
+ CODING_RULES.md v2.0 final-safe
```

## Important Note

This package was rebuilt from the available workspace artifacts:

- `FleziBCG_latest_repo_ready_design_package_v-next_2026-04-23.zip`
- latest `product-business-truth-overview.md`
- `CODING_RULES.md v2.0` patch
- review / audit / roadmap source notes available in the workspace

It is safe to use as a repo-ready design pack for the next implementation step, but if your repo already contains the previous hardening package, you can also apply the included docs as overlay updates.

## Key Baseline Decisions

- Backend is the source of truth.
- Frontend is UX/navigation only.
- Persona is not permission.
- JWT proves identity only.
- Authorization is checked per backend request.
- Execution remains event-driven where relevant.
- Status/projections are derived and are not the source of truth.
- AI is advisory only.
- Digital Twin is derived state.
- ERP/QMS/CMMS/WMS/SCADA/Historian are not replaced by FleziBCG.
- Acceptance Gate is canonical; LAT/Pre-LAT are display labels only.
- Backflush is cross-domain.
- Station Execution target is session-owned; claim is migration debt.

## Current Engineering Decision

- Current backend implementation is sync.
- P0-A must remain sync-consistent.
- Alembic-first.
- Do not migrate full async in P0-A.
- Do not migrate frontend to React Query/Zustand in P0-A.
- Do not introduce Redis/Kafka/OPA/OPC UA/MQTT/Sparkplug in P0-A.

## Next Recommended Step

```text
Task 5 — P0-A Foundation Database Implementation
```

P0-A scope:

- Alembic baseline
- tenant
- IAM user lifecycle
- sessions
- refresh token foundation
- role/action/scope assignment
- audit/security event foundation
- plant hierarchy
- scope-node compatibility
- CORS/config hardening
- CloudBeaver dev-only posture
- backend CI minimum

Explicit exclusions:

- ERP integration
- Acceptance Gate
- Backflush
- APS
- AI
- Digital Twin
- Compliance/e-record
- OPC UA/MQTT/Sparkplug
- Redis/Kafka/OPA
- frontend state migration
- Station Execution refactor
