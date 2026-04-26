# ADR - Authorization Policy Engine Strategy

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added policy-engine decision path for authorization hardening. |

## Status

**Accepted design direction.**

## Context

FleziBCG authorization must combine identity, role, action, scope, operational state, approval, delegation, support session, and separation-of-duties rules. If policy logic is scattered across controllers/routes, it will become untestable.

## Decision

P0 will use a typed internal policy service.

Do not adopt OPA/Casbin by default in P0. Instead, create an explicit ADR evaluation path for P1/P2 if policy complexity grows.

## P0 Policy Shape

```text
can(actor, action, resource, scope, context) -> decision
```

Decision includes:

- allowed/denied;
- reason code;
- required approval if any;
- applicable scope;
- audit metadata.

## Required Inputs

| Input | Meaning |
|---|---|
| Actor | authenticated user/session/support mode context |
| Action | backend action code |
| Resource | target entity type and ID |
| Scope | tenant/plant/area/line/station/equipment |
| Operational context | operation state, quality gate state, closure status, session ownership |
| Governance context | approval, delegation, SoD |

## Rules

1. No policy logic hidden in frontend.
2. No policy logic hidden inside React route guards.
3. Controllers/routes call policy service or command service that calls policy service.
4. Denied decisions use stable reason codes.
5. Policy decisions should be unit-tested.
6. Support/impersonation mode cannot bypass SoD.

## P1 Evaluation Options

| Option | Pros | Cons |
|---|---|---|
| Continue typed internal policy service | Simple, testable, team-owned | May become large if many dynamic policies. |
| Casbin | RBAC/ABAC model support | Adds dependency/model complexity. |
| OPA | Powerful externalized policy | Operational overhead, policy language/team learning curve. |

## Decision Trigger for External Policy Engine

Evaluate external engine if:

- custom roles/scopes become highly dynamic;
- customers need policy-as-config;
- policy audit/explainability requires external rules;
- multiple services need shared policy decisions.
