# Approval Service Generic Extension Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Defined generic approval extension boundary for future governed domain adoption. |

## 1. Purpose

This document defines the contract boundary for any future generic extension of the approval service.

It exists to prevent premature runtime expansion of the current approval implementation into domain workflows that require governed resource identity, hierarchical scope applicability, platform-grade audit evidence, and strict separation of duties.

This is a design-first contract. It does not authorize runtime implementation by itself.

## 2. Current Source Evidence

Current evidence comes from:

- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`
- `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`
- `docs/design/01_foundation/approval-and-separation-of-duties-model.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/01_foundation/role-model-and-scope-resolution.md`
- `docs/design/02_registry/action-code-registry.md`
- `backend/app/models/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/schemas/approval.py`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/security_event_service.py`
- `backend/app/models/security_event.py`
- `backend/tests/test_approval_service_current_behavior.py`

Current source truth established by those files:

1. Current approval is generic only at table/schema shape, not at runtime capability.
2. Runtime support is limited to six hardcoded `action_type` values in `VALID_ACTION_TYPES`.
3. Current approval applicability is tenant-aware only.
4. Current SoD uses the real user identity, including under impersonation.
5. Current audit evidence is approval-local plus impersonation permission-use audit, not platform `SecurityEventLog` evidence for approval business events.
6. Current approval does not mutate domain truth directly.

## 3. Current Approval Capability

Current approval supports:

- request creation through `approval.create`
- decision through `approval.decide`
- current request states `PENDING`, `APPROVED`, and `REJECTED`
- tenant-scoped request lookup
- tenant-specific and wildcard rule lookup
- requester-versus-decider SoD using real user identity
- approval-local audit rows via `ApprovalAuditLog`

Current approval request identity is represented only by:

- `action_type`
- `subject_type`
- `subject_ref`

These fields are sufficient for the current narrow approval service, but not sufficient for generic governed domain adoption.

## 4. Current Limitations

Current approval must not be treated as a generic governed-action platform because it has the following limitations:

1. `action_type` is a narrow hardcoded allowlist, not a generic registry-controlled governed action contract.
2. `subject_type` and `subject_ref` are opaque descriptive strings, not explicit governed resource identity.
3. Approval applicability is tenant-aware only and does not evaluate plant, area, line, station, or equipment scope.
4. Approval decisions emit only approval-local audit records and do not emit platform `SecurityEventLog` records for approval business events.
5. Approval decisions do not carry a domain adoption contract that binds the approval to a later domain transition.
6. `CANCELLED` is schema-only debt and not an implemented lifecycle path.

## 5. Governed Resource Identity Contract

Future generic approval must not rely only on freeform `subject_type` and `subject_ref`.

Before runtime generic adoption, a governed resource identity contract must be defined explicitly. Contract-candidate fields are:

- `governed_resource_type`
- `governed_resource_id`
- `governed_resource_display_ref`
- `governed_resource_tenant_id`
- `governed_resource_scope_ref`
- `governed_action_type`

Contract requirements:

1. `governed_resource_type` must identify the governed domain entity class in a stable backend-controlled vocabulary.
2. `governed_resource_id` must identify the authoritative backend entity instance, not only a display label.
3. `governed_resource_display_ref` may exist for operator/admin readability, but must never replace the authoritative identity.
4. `governed_resource_tenant_id` must align with backend tenant truth.
5. `governed_resource_scope_ref` must resolve to the canonical scope foundation or an equivalent canonical scope reference.
6. `governed_action_type` must identify the governed transition intent attached to the resource.

Contract rule:

> Generic approval requests must be bound to explicit governed resource identity and governed action intent, not only to descriptive strings.

Compatibility note:

Current `subject_type` and `subject_ref` may remain as compatibility/display fields in a future migration path, but they must not remain the only governed identity contract for generic adoption.

## 6. Generic Action Type Contract

Future generic approval must not accept arbitrary unmanaged action strings.

Future governed action types must be:

- registry-controlled
- backend-owned
- explicitly mapped to domain command intent
- migration-safe
- auditable

Required rules:

1. A future governed action type must be added only through an intentional contract change.
2. Governed action type naming must be stable and versionable enough to survive schema, API, and reporting evolution.
3. Governed action type must map to a real backend command intent, not to a UI label.
4. Approval action types and domain action codes must not be conflated. `approval.create` and `approval.decide` remain approval-domain action codes for the approval API surface.
5. Domain adoption must still keep its domain command/action authorization boundary.

Contract rule:

> Approval genericity is not permission genericity. Future governed action types identify what is being governed; they do not replace domain action-code authorization.

This slice does not define any new runtime action type.

## 7. Tenant and Scope Applicability Contract

Future generic approval applicability must be hierarchical-scope-aware before domain adoption.

At minimum, applicability must support the canonical hierarchy already established by the platform:

- tenant
- plant
- area
- line
- station
- equipment

This may be modeled through canonical scope IDs, scope references, or scope paths, provided the contract remains backend-derived and consistent with the scope foundation.

Required rules:

1. Tenant match alone is not sufficient for generic governed adoption.
2. Approval applicability must be resolvable against the governed resource scope.
3. Wildcard/default behavior, if retained, must be explicitly ordered and testable.
4. Scope resolution must remain backend truth and must not be delegated to frontend interpretation.
5. Approval applicability must be deterministic for the governed resource and governed action pair.

Contract rule:

> Generic approval adoption is blocked until approval applicability can resolve tenant and canonical operational scope for the governed resource.

## 8. SoD / Authorization Boundary

Separation of duties remains non-negotiable.

Required invariants:

- `requester_real_user_id != decider_real_user_id`
- impersonation must not bypass SoD
- effective acting role may be used for policy evaluation, but real user identity must be used for SoD

Authorization boundary rules:

1. RBAC remains required but not sufficient for governed actions.
2. Approval policy must be evaluated in addition to RBAC.
3. SoD must be evaluated in addition to RBAC and approval policy.
4. Domain adoption must continue to require the correct domain authorization boundary for the later state-changing command.

Contract rule:

> Future generic approval is a governance layer over domain action intent, not a replacement for domain authorization.

## 9. Audit / Security Event Requirements

Future generic approval request and decision actions must emit platform audit/security evidence.

Required future evidence:

1. Platform `SecurityEventLog` or an equivalent canonical security/audit event must be emitted for approval request creation.
2. Platform `SecurityEventLog` or an equivalent canonical security/audit event must be emitted for approval decision.
3. Security event payload must identify at least:
   - tenant
   - real actor user id
   - event type
   - governed resource type
   - governed resource id
   - governed action type
   - outcome or decision
4. If impersonation is active, the evidence must preserve real-user identity and impersonation context.
5. Approval-local audit rows may be retained, but they are not sufficient as the only governance evidence for generic adoption.

Contract rule:

> Future governed approval actions require platform-grade security/audit evidence in addition to any approval-local audit stream.

## 10. Domain Adoption Contract

Generic approval cannot directly mutate domain state.

Domain adoption rules:

1. Approval is a governance gate.
2. The target domain service remains the source of truth for the actual state transition.
3. Approval success must not by itself finalize the domain transition.
4. The target domain service must validate its own current state, invariants, and authorization before mutating domain truth.
5. Domain-specific side effects remain domain-owned.

Contract rule:

> Approval decides whether a governed transition is authorized to proceed. The domain service still decides whether the state transition is valid and performs the actual change.

## 11. Future API Contract

Any future runtime generic extension will require intentional API contract changes.

Expected implications:

1. Future approval request payloads will need explicit governed resource identity fields.
2. Future approval decision responses may need to expose governed resource identity and standardized outcome metadata.
3. Backward compatibility for current approval consumers must be explicitly evaluated.
4. Public API changes must follow architecture/contract PR rules.
5. API contracts must expose backend-derived codes, not UI-defined labels.

This slice does not add, change, or approve any runtime API.

## 12. Future DB / Migration Implications

Any future runtime generic extension will require intentional database and migration handling.

Likely implications:

1. Approval request storage will need explicit governed resource identity fields.
2. Approval applicability storage may need explicit scope-aware policy references.
3. Approval/security evidence may need canonical cross-reference fields for governed resource context.
4. Existing rows based only on `subject_type` and `subject_ref` will need a compatibility or migration strategy.

This slice does not add schema, columns, constraints, or migrations.

## 13. Test Requirements Before Runtime Adoption

Before any runtime generic adoption, at minimum the following tests are required:

1. generic action type registry tests
2. governed resource identity tests
3. tenant/scope approval applicability tests
4. SoD negative tests
5. impersonation SoD tests
6. security event emission tests
7. domain adoption tests proving approval is a gate and domain remains source of truth
8. terminal-state tests
9. backward-compatibility tests for the current six action types until intentionally superseded

## 14. Explicitly Out of Scope

This contract does not:

- implement a generic approval service
- add any runtime action type
- add any runtime action code
- add governed resource columns
- modify approval runtime service behavior
- modify approval models, schemas, repositories, or API routes
- add migrations
- add approval API endpoints
- add frontend or Admin UI
- modify MMD source, tests, or docs
- change `ACTION_CODE_REGISTRY`
- change route guards

## 15. Open Questions

1. Should future governed action type truth live in a dedicated approval-governed action registry, a broader governance registry, or a domain-owned contract set with centralized validation?
2. Should `governed_resource_scope_ref` resolve to a scope ID, a `(scope_type, scope_value)` pair, or a canonical scope path abstraction?
3. Should future approval/security events use approval-specific event types, or a broader governed-action security event taxonomy?
4. What compatibility window is acceptable for requests that only have legacy `subject_type` and `subject_ref` fields?
5. Should optional `CANCELLED` exist as a runtime approval state later, or remain absent until a concrete operational need exists?

## 16. Final Decision

Decision: create the generic approval extension contract now, but keep runtime unchanged.

The current approval service is stable enough to document and constrained enough to reject premature generic adoption.

Future generic adoption is allowed only after:

1. explicit governed resource identity exists,
2. governed action type is registry-controlled,
3. tenant and canonical scope applicability are modeled,
4. platform security-event evidence is emitted,
5. domain adoption keeps the domain service as source of truth.