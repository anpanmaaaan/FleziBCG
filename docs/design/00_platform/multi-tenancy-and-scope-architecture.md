# Multi-Tenancy and Scope Architecture

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified scope hierarchy and mode-neutral execution context. |

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

## 3. Execution implication

Execution must not assume station as the only lowest useful execution context.
For process/batch plants, the active execution context may be closer to:
- unit
- vessel
- reactor
- packaging train
- process segment

The hierarchy still supports this by treating equipment/resource context as first-class.

## 4. Role/scope implication

Permissions are evaluated against user role + scope.
Effective execution mutation still depends on station/resource session context, not on frontend visibility alone.
