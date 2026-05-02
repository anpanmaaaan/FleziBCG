# Action Code Registry

This file is the authoritative reference for fine-grained action codes used in
`ACTION_CODE_REGISTRY` in `backend/app/security/rbac.py`.

Action codes resolve to a `PermissionFamily`. The runtime check in `has_action()` maps
the code to its family and evaluates DB-backed role→permission rows.

> **Do not add action codes here without a corresponding entry in `rbac.py`.**
> The registry in `rbac.py` is the runtime truth. This document is the governance record.

---

## Permission Families

| Family | Purpose |
|---|---|
| `EXECUTE` | Shopfloor / station execution actions |
| `APPROVE` | Approval and sign-off actions |
| `CONFIGURE` | Setup, engineering, configuration actions |
| `ADMIN` | Platform administration, master data management |
| `VIEW` | Read-only access (no fine-grained action code required; use `require_authenticated_identity`) |

---

## Registry

### Execution Domain

| Action Code | Family | Description |
|---|---|---|
| `execution.start` | EXECUTE | Start a production operation |
| `execution.complete` | EXECUTE | Complete a production operation |
| `execution.report_quantity` | EXECUTE | Report output / scrap quantity |
| `execution.pause` | EXECUTE | Pause an operation |
| `execution.resume` | EXECUTE | Resume a paused operation |
| `execution.start_downtime` | EXECUTE | Open a downtime record |
| `execution.end_downtime` | EXECUTE | Close a downtime record |
| `execution.close` | EXECUTE | Close an operation |
| `execution.reopen` | EXECUTE | Re-open a closed operation |

### Approval Domain

| Action Code | Family | Description |
|---|---|---|
| `approval.create` | APPROVE | Create an approval request |
| `approval.decide` | APPROVE | Approve or reject an approval request |

### IAM / Platform Administration

| Action Code | Family | Description |
|---|---|---|
| `admin.impersonation.create` | ADMIN | Create an operator impersonation session |
| `admin.impersonation.revoke` | ADMIN | Revoke an active impersonation session |
| `admin.user.manage` | ADMIN | IAM user lifecycle management (create, update, assign roles) |

### Manufacturing Master Data (MMD) — Added by MMD-BE-02

| Action Code | Family | Description |
|---|---|---|
| `admin.master_data.product.manage` | ADMIN | Create, update, release, or retire a Product definition |
| `admin.master_data.routing.manage` | ADMIN | Create, update, add/remove operations, release, or retire a Routing |
| `admin.master_data.resource_requirement.manage` | ADMIN | Create, update, or delete a Resource Requirement on a Routing Operation |

### Configuration Administration — Added by P0-A-07B

| Action Code | Family | Description |
|---|---|---|
| `admin.downtime_reason.manage` | ADMIN | Create, update, or deactivate a Downtime Reason reference entry |

---

## Naming Convention

```
<top_domain>.<sub_domain>[.<entity>].<verb>
```

Examples:
- `execution.start` → top domain = execution, verb = start
- `admin.user.manage` → top domain = admin, entity = user, verb = manage
- `admin.master_data.product.manage` → top domain = admin, sub domain = master_data, entity = product, verb = manage

---

## Governance Rules

1. Read endpoints must not use `require_action`. Use `require_authenticated_identity` for read-only access.
2. MMD mutation codes must NOT share `admin.user.manage`. IAM user management and master data management are separate governance domains.
3. Action codes map 1:1 to their PermissionFamily. Do not invent cross-family codes.
4. Adding a new action code requires: (a) entry in `rbac.py`, (b) entry in this file, (c) a regression test.

---

## History

| Date | Slice | Change |
|---|---|---|
| 2026-05-02 | MMD-BE-02 | Added `admin.master_data.product.manage`, `admin.master_data.routing.manage`, `admin.master_data.resource_requirement.manage` |
| 2026-05-02 | P0-A-07B | Added `admin.downtime_reason.manage` — resolves GAP-1 from P0-A-07A |
