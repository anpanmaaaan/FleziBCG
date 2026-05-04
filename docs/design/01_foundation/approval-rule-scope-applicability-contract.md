# Approval Rule Scope-Aware Applicability Contract

| Field    | Value                                          |
|----------|------------------------------------------------|
| Slice    | P0-A-14                                        |
| Status   | ACTIVE                                         |
| Version  | v1.0                                           |
| Date     | 2026-05-04                                     |
| Author   | AI Brain (Hard Mode MOM v3)                    |
| Depends  | P0-A-13B governed-action-type-registry-contract.md |

## Revision History

| Date       | Version | Notes                                                                              |
|------------|---------|------------------------------------------------------------------------------------|
| 2026-05-04 | v1.0    | Defined scope-aware approval rule applicability contract before runtime adoption.  |

---

## 1. Purpose

This contract defines the **design decision** for how `ApprovalRule` applicability must evolve to support scope-aware matching.

As of P0-A-14 the runtime is NOT changed. This document locks the design decision so that future runtime adoption proceeds on a single, governed path.

**Design-only slice. No runtime changes.**

---

## 2. Current Source Evidence

### 2.1 ApprovalRule Model (runtime, as of 2026-05-04)

File: `backend/app/models/approval.py`

```python
class ApprovalRule(Base):
    __tablename__ = "approval_rules"
    id: Mapped[int]
    tenant_id: Mapped[str]       # tenant scope (may be "*" for wildcard)
    action_type: Mapped[str]     # matched action type (may be "*" for wildcard)
    approver_role_code: Mapped[str]
    is_active: Mapped[bool]
    created_at: Mapped[datetime]
```

No scope fields exist. Matching is `action_type` + `tenant_id` only.

### 2.2 Approval Repository Rule Lookup (runtime, as of 2026-05-04)

File: `backend/app/repositories/approval_repository.py`

```python
def get_rules_for_action(db, action_type: str, tenant_id: str) -> list[ApprovalRule]:
    return db.query(ApprovalRule).filter(
        ApprovalRule.action_type == action_type,
        ApprovalRule.tenant_id.in_([tenant_id, "*"]),
        ApprovalRule.is_active == True,
    ).order_by(ApprovalRule.tenant_id.desc()).all()
```

Wildcard `"*"` is supported for both `tenant_id` and (implicitly) `action_type` matching.

### 2.3 ApprovalRequest Governed Resource Fields (runtime, as of 2026-05-04)

Added in P0-A-13 migration `0011`:

```python
governed_resource_type: Mapped[str | None]       # nullable
governed_resource_id: Mapped[str | None]          # nullable
governed_resource_display_ref: Mapped[str | None] # nullable
governed_resource_tenant_id: Mapped[str | None]   # nullable
governed_resource_scope_ref: Mapped[str | None]   # nullable
governed_action_type: Mapped[str | None]          # nullable
```

These fields carry identity but are **not yet used in rule matching**.

### 2.4 Scope Model (runtime, as of 2026-05-04)

File: `backend/app/models/rbac.py`

Canonical scope hierarchy: `tenant → plant → area → line → station → equipment`

```python
SUPPORTED_SCOPE_TYPES = ("tenant", "plant", "area", "line", "station", "equipment")
```

---

## 3. Current Runtime Approval Rule Model

| Field              | Type    | Nullable | Wildcard | Notes                      |
|--------------------|---------|----------|----------|----------------------------|
| `tenant_id`        | str     | No       | `"*"`    | Tenant-specific or global  |
| `action_type`      | str     | No       | (future) | Current: exact match only  |
| `approver_role_code` | str   | No       | No       | RBAC role code             |
| `is_active`        | bool    | No       | -        | Active flag                |

**No scope, governed_resource_type, or governed_action_type fields exist on `ApprovalRule` today.**

---

## 4. Problem Statement

The current rule model is `action_type + tenant_id` only. This is insufficient because:

1. **Same action type, different scope** may require different approver roles.  
   Example: `SCRAP` at the plant level may require a plant manager; `SCRAP` at a specific line may require line supervisor.

2. **Same action type, different resource type** may require different approver roles.  
   Example: `QC_HOLD` on a work order vs. `QC_HOLD` on a batch lot may have distinct approval chains.

3. **governed_action_type vs. action_type** are now distinct namespaces (per P0-A-13B contract). Rule matching must eventually resolve against the governed action type taxonomy, not legacy string keys.

4. **ApprovalRequest now carries governed_resource_scope_ref** (P0-A-13), but no rule can currently match against it.

---

## 5. Scope-Aware Applicability Decision

### Decision

> **ApprovalRule must become scope-aware, governed-resource-type-aware, and governed-action-type-aware in a future runtime slice.**

The matching dimensions are:

| Dimension                   | Current | Future      |
|-----------------------------|---------|-------------|
| `tenant_id`                 | ✅      | ✅          |
| `action_type` (legacy key)  | ✅      | ✅ (compat) |
| `governed_action_type`      | ❌      | ✅          |
| `governed_resource_type`    | ❌      | ✅          |
| `scope_ref`                 | ❌      | ✅          |
| `scope_type`                | ❌      | ✅ (filter) |

### Current Runtime Posture (LOCKED, not changed in P0-A-14)

- Matching is `action_type + tenant_id` only.
- Wildcard `"*"` for `tenant_id` is supported and ordered after tenant-specific.
- No other matching dimensions are evaluated at runtime today.

---

## 6. Future ApprovalRule Field Candidates

The following fields are candidates for the future `ApprovalRule` table extension. **No migration is created in P0-A-14.**

| Candidate Field          | Type      | Nullable | Default | Purpose                                    |
|--------------------------|-----------|----------|---------|--------------------------------------------|
| `governed_action_type`   | str       | Yes      | NULL    | Match governed action type namespace       |
| `governed_resource_type` | str       | Yes      | NULL    | Match specific resource type               |
| `scope_ref`              | str       | Yes      | NULL    | Match canonical scope path (e.g. plant/01) |
| `scope_type`             | str       | Yes      | NULL    | Match scope level (e.g. "plant")           |
| `priority`               | int       | Yes      | NULL    | Explicit tie-break if multiple rules match |
| `effective_from`         | datetime  | Yes      | NULL    | Time-bounded activation                    |
| `effective_to`           | datetime  | Yes      | NULL    | Time-bounded expiry                        |

All new fields MUST be **nullable** to preserve backward compatibility with existing rules that carry no scope.

---

## 7. Rule Matching Precedence Contract

When scope-aware matching is activated in a future runtime slice, the following precedence order is REQUIRED:

| Priority | Match Criteria                                                                          | Label                        |
|----------|-----------------------------------------------------------------------------------------|------------------------------|
| 1        | tenant + scope_ref + governed_resource_type + governed_action_type                     | Most specific                |
| 2        | tenant + scope_ref + governed_action_type                                               | Scope + action               |
| 3        | tenant + governed_resource_type + governed_action_type                                  | Resource + action, no scope  |
| 4        | tenant + governed_action_type                                                           | Action only                  |
| 5        | tenant + action_type (legacy key)                                                       | Legacy fallback              |
| 6        | tenant wildcard `"*"` + action_type                                                     | Global fallback              |

**First non-empty match wins.**

If multiple rules match at the same priority level, `priority` field (ascending, lower = higher priority) resolves ties.  
If no `priority` is set, the first rule returned by creation order applies.

---

## 8. Tenant/Scope Fallback Contract

| Scenario                                | Behavior                                                 |
|-----------------------------------------|----------------------------------------------------------|
| Request has scope_ref, rule has no scope_ref | Rule is still a candidate (matches on other dims)   |
| Request has no scope_ref, rule has scope_ref  | Rule is NOT a candidate for that request             |
| Rule tenant_id = `"*"`                  | Matches any tenant (wildcard; lowest priority)           |
| Rule scope_ref = NULL                   | Matches any scope (unscoped rule; mid priority)          |
| Rule governed_action_type = NULL        | Matches any governed action type (untyped rule)          |

---

## 9. Relationship to Governed Resource Identity

Per P0-A-13 contract (`approval-request-governed-resource-identity-schema.md`):

- `ApprovalRequest.governed_resource_scope_ref` carries the scope path of the resource being governed.
- `ApprovalRequest.governed_resource_type` identifies the resource domain.
- `ApprovalRequest.governed_action_type` identifies the governed action type from the P0-A-13B taxonomy.

**Rule matching must consume these fields from the request** when scope-aware matching is activated.  
The rule lookup must be updated to join/filter against `governed_resource_scope_ref`, `governed_resource_type`, `governed_action_type` from the `ApprovalRequest` passed to `get_rules_for_action`.

---

## 10. Relationship to Governed Action Type Registry

Per P0-A-13B contract (`governed-action-type-registry-contract.md`):

- Governed action types follow the `<domain>.<resource>.<transition>` naming convention.
- `VALID_ACTION_TYPES` in `approval_service.py` is a **separate legacy namespace** from governed action types.
- Future rule matching must resolve `governed_action_type` against the governed action type registry, not against `VALID_ACTION_TYPES`.

**Coexistence rule**: An `ApprovalRule` may carry either `action_type` (legacy) or `governed_action_type` (new), not both simultaneously. The precedence table in Section 7 governs resolution order.

---

## 11. Backward Compatibility Requirements

1. **Existing ApprovalRule rows with action_type + tenant_id MUST continue to match** after scope-aware fields are added.
2. New nullable fields on `ApprovalRule` MUST default to NULL.
3. Existing API callers that do not supply governed resource identity fields MUST continue to receive approval decisions based on legacy matching.
4. **No existing test may be broken** by addition of scope-aware fields.
5. Migration adding scope fields to `ApprovalRule` MUST be purely additive (nullable columns, no NOT NULL without default).

---

## 12. Future DB/Migration Requirements

When a future runtime slice activates scope-aware matching:

1. A new Alembic migration must add nullable columns to `approval_rules`:
   - `governed_action_type VARCHAR NULL`
   - `governed_resource_type VARCHAR NULL`
   - `scope_ref VARCHAR NULL`
   - `scope_type VARCHAR NULL`
   - `priority INTEGER NULL`
   - `effective_from TIMESTAMP NULL`
   - `effective_to TIMESTAMP NULL`

2. Migration must be additive only (no backfill required; NULL means "match-all" for new dims).

3. An index on `(tenant_id, governed_action_type, scope_ref)` is RECOMMENDED for query performance.

4. No DOWN migration required if this is a greenfield deployment slice.

---

## 13. Future API Contract Implications

When scope-aware matching is activated:

1. `ApprovalRuleCreate` schema must optionally accept the new fields.
2. `ApprovalRuleResponse` must expose all fields including nullable scope fields.
3. Seed API endpoints (`seed_approval_rules`) must accept scope-qualified rules.
4. Admin UI must display scope-qualified rules with their precedence level clearly shown.

**No API changes are made in P0-A-14.**

---

## 14. Test Requirements Before Runtime Adoption

Before any runtime activation of scope-aware matching, the following tests MUST exist and pass:

| Test ID   | Description                                                               |
|-----------|---------------------------------------------------------------------------|
| T-SA-01   | Rule with exact scope_ref matches request with matching scope_ref         |
| T-SA-02   | Rule with no scope_ref matches request with any scope_ref                 |
| T-SA-03   | Rule with scope_ref does NOT match request with different scope_ref       |
| T-SA-04   | Precedence: tenant+scope+action wins over tenant+action only              |
| T-SA-05   | Precedence: tenant+action wins over wildcard tenant+action                |
| T-SA-06   | Legacy action_type-only rule still matches when no scope fields supplied  |
| T-SA-07   | governed_action_type rule takes precedence over legacy action_type        |
| T-SA-08   | governed_resource_type filter excludes rules for different resource types |
| T-SA-09   | priority field resolves ties at same precedence level                     |
| T-SA-10   | effective_from/effective_to excludes time-expired rules                   |
| T-SA-11   | Security event APPROVAL.REQUESTED still emitted for scope-qualified rule  |
| T-SA-12   | No scope-aware decision leaks into frontend (backend-only test)           |

**These tests do not exist in P0-A-14. They are created in the future runtime slice.**

---

## 15. Explicitly Out of Scope (P0-A-14)

The following are **NOT** part of this slice:

- Any migration adding scope fields to `approval_rules`
- Any change to `approval_repository.py` rule lookup logic
- Any change to `approval_service.py`
- Any change to `ApprovalRule` ORM model
- Any change to `ApprovalRequest` ORM model (already updated in P0-A-13)
- Any new API endpoints
- Any frontend changes
- Any new seed data
- Any test for scope-aware matching (tests listed in Section 14 are future)

---

## 16. Open Questions

| ID   | Question                                                                   | Status  |
|------|----------------------------------------------------------------------------|---------|
| OQ-1 | Should scope_ref be a foreign key to the Scope table or a plain string?    | Open    |
| OQ-2 | Should governed_action_type on ApprovalRule validate against the registry? | Open    |
| OQ-3 | Should priority be a float to allow insertion between existing priorities? | Open    |
| OQ-4 | Should effective_from/effective_to be enforced at DB level or service?     | Open    |
| OQ-5 | When multiple rules match at P1, is it an error or does priority resolve?  | Open    |

---

## 17. Final Decision

> **APPROVED: ApprovalRule scope-aware applicability design is locked as defined in this contract.**
>
> Current runtime (action_type + tenant_id only) is UNCHANGED.  
> Future runtime adoption MUST follow the matching precedence defined in Section 7.  
> All new fields MUST be nullable and backward-compatible per Section 11.  
> No runtime code, migration, or test is changed in P0-A-14.  
> This contract supersedes the scope-awareness intent stated in Section 9 of the governed-action-approval-applicability-contract.md (P0-A-11C).

---

## Related Documents

- [P0-A-11C] `docs/design/01_foundation/governed-action-approval-applicability-contract.md`
- [P0-A-13] `docs/design/01_foundation/approval-request-governed-resource-identity-schema.md`
- [P0-A-13B] `docs/design/01_foundation/governed-action-type-registry-contract.md`
- [P0-A-14 Audit] `docs/audit/p0-a-14-approval-rule-scope-applicability-decision-report.md`
