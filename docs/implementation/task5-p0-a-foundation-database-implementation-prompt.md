# Task 5 — P0-A Foundation Database Implementation Prompt

## Status

Ready to use for Agent implementation.

## Prompt

You are a senior backend engineer and database architect.

Your task is to implement **P0-A Foundation Database Slice** for FleziBCG.

This is a narrow implementation slice.

### In scope

- Alembic migration foundation
- Baseline current schema
- Remove/disable production `Base.metadata.create_all()` schema-management path
- Tenant foundation
- IAM user foundation
- User lifecycle status
- Session foundation
- Refresh token foundation
- Role/action foundation
- Role-action assignment
- User-role-scope assignment
- Scope node / hierarchical scope foundation
- Plant hierarchy: plant, area, line, station, equipment
- Scope compatibility/mapping with existing Scope/RBAC if present
- Audit log foundation
- Security event foundation
- CORS configuration hardening
- CloudBeaver dev-only posture if currently in main docker-compose
- Backend CI minimum if absent
- Tests for changed foundation behavior
- Implementation report

### Explicitly out of scope

Do NOT implement:

- ERP integration
- Acceptance Gate
- LAT / Pre-LAT logic
- Backflush
- Material readiness
- Traceability genealogy
- Quality Gate / Quality Lite
- APS
- AI
- Digital Twin
- Compliance / e-record / e-sign
- OPC UA / MQTT / Sparkplug
- Redis / Kafka / OPA / Casbin migration
- Full async migration
- Frontend React Query / Zustand migration
- Station Execution refactor
- Claim removal
- Rework flow or `rework_qty`
- `abort_operation` expansion

### Stack rule

Current backend is synchronous. P0-A must remain sync-consistent. Do not introduce async SQLAlchemy or asyncpg.

### Migration rule

Alembic is mandatory. `Base.metadata.create_all()` must not be production schema management.

### Implementation report

Create:

```text
docs/implementation/p0-a-foundation-database-implementation-report.md
```

with:

1. Summary
2. Scope Implemented
3. Files Changed
4. Database/Migration Changes
5. Existing Code Preserved
6. Migration Debt Left Intentionally
7. Tests Added/Updated
8. Verification Commands Run
9. Explicit Exclusions Confirmed
10. Next Recommended Slice
