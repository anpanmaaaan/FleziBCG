# ADR - Tenant Isolation and PostgreSQL RLS Strategy

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added tenant isolation and RLS hardening strategy. |

## Status

**Accepted design direction.**

## Context

FleziBCG is multi-tenant and hierarchical-scope-ready. Current design already requires tenant/scope authorization at backend application/service/repository level.

PostgreSQL Row Level Security can provide defense-in-depth through table-specific policies. PostgreSQL enables/disables RLS with `ALTER TABLE`, and policies are created with `CREATE POLICY`.

## Decision

P0 must enforce tenant and scope at application/service/repository level.

RLS is not mandatory for all P0 tables, but should be designed as a **P1 hardening layer** for high-risk tenant-owned tables.

## Target Layering

| Layer | Rule |
|---|---|
| API route | Authenticate and establish actor/session context. |
| Policy service | Resolve action + role + scope + operational policy. |
| Repository | Always filter by `tenant_id` and relevant scope. |
| PostgreSQL RLS | P1 defense-in-depth for high-risk tables. |
| Audit | Record allow/deny/action outcome where needed. |

## Candidate RLS Tables

- `iam.users`
- `access.user_role_assignments`
- `plant.scope_nodes`
- `exe.work_orders`
- `exe.work_order_operations`
- `exe.execution_events`
- `qual.*`
- `inv.*`
- `trc.*`
- `intg.inbound_messages`
- `intg.outbound_messages`
- `intg.erp_posting_requests`

## P1 RLS Pattern

```sql
ALTER TABLE exe.work_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_work_orders
ON exe.work_orders
USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

Use `FORCE ROW LEVEL SECURITY` only after carefully testing ownership/admin migration paths.

## Non-Negotiable Rule

RLS does not replace application-layer authorization. Repository tenant filter remains mandatory even when RLS exists.

## Risks

- Harder debugging.
- Migration/admin scripts may fail if session variables are not set.
- Performance must be tested.
- Superuser/table owner bypass behavior must be controlled.

## References

- PostgreSQL Row Security Policies: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- PostgreSQL CREATE POLICY: https://www.postgresql.org/docs/current/sql-createpolicy.html
