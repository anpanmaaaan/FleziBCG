# Multi-Tenancy and Scope Architecture

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified scope hierarchy and mode-neutral execution context. |
| 2026-05-04 | v2.1 | Clarified tenant manufacturing defaults versus plant/scope manufacturing profile ownership. |

Status: Canonical tenancy/scope note.

## 1. Core rule

Tenant and scope isolation are mandatory.
Every tenant-owned repository access must receive validated tenant/scope context explicitly.

## 2. Scope hierarchy

The platform must be ready for:
- tenant
- plant
- area
- line
- station
- equipment

## 2.1 Tenant manufacturing defaults versus scope manufacturing profiles

Tenant is the governance, isolation, and default-configuration boundary.

Tenant may define:
- default manufacturing profile
- enabled manufacturing capabilities
- default hierarchy alias profile
- default governance and audit posture

Tenant must not be treated as the final manufacturing-mode boundary.

Actual manufacturing mode is resolved at operational scope level, especially:
- plant
- area
- line
- station
- equipment

This allows one tenant to operate multiple manufacturing modes across different facilities or areas.

Example:
- tenant default = `HYBRID`
- plant A = `DISCRETE`
- plant B = `BATCH`
- plant C = `CONTINUOUS`
- plant D = `HYBRID`

## 3. Execution implication

Execution must not assume station as the only lowest useful execution context.
For process/batch plants, the active execution context may be closer to:
- unit
- vessel
- reactor
- packaging train
- process segment

The hierarchy still supports this by treating equipment/resource context as first-class.

Execution services must resolve manufacturing profile from validated tenant/scope context and manufacturing definition context.

Execution must not infer manufacturing mode from frontend route, persona, or tenant default alone.

## 4. Role/scope implication

Permissions are evaluated against user role + scope.
Effective execution mutation still depends on station/resource session context, not on frontend visibility alone.
