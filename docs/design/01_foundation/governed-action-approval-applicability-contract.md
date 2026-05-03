# Governed Action Approval Applicability Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Defined governed action and approval applicability contract for future generic approval runtime adoption. |

## 1. Purpose

This document defines the source-of-truth decision for future governed approval action types and approval applicability resolution.

It exists to answer the remaining design questions left open by the generic approval extension contract:

- where governed approval action types should be controlled;
- how they relate to RBAC action codes;
- how governed resource identity binds to approval requests;
- how tenant and scope applicability should be resolved;
- how future approval/security event taxonomy should be named.

This is a design-only contract. It does not authorize runtime implementation by itself.

## 2. Current Source Evidence

Current source evidence comes from:

- `docs/design/01_foundation/approval-service-generic-extension-contract.md`
- `docs/audit/p0-a-11b-generic-approval-extension-contract-report.md`
- `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`
- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`
- `docs/design/01_foundation/approval-and-separation-of-duties-model.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/01_foundation/role-model-and-scope-resolution.md`
- `docs/design/02_registry/action-code-registry.md`
- `backend/app/models/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/schemas/approval.py`
- `backend/app/models/rbac.py`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/security_event_service.py`
- `backend/app/models/security_event.py`

Current source truth established by those files:

1. Current approval uses a narrow runtime `action_type` allowlist, not a generic governed action registry.
2. Current approval API authorization uses RBAC action codes `approval.create` and `approval.decide`.
3. Current approval rule matching is keyed by `action_type` and `tenant_id` only.
4. Current approval request identity is only `subject_type` plus `subject_ref`.
5. Current approval applicability is tenant-aware only, while the platform scope foundation is hierarchical.
6. Current approval writes approval-local audit rows and does not emit approval business events through `SecurityEventLog`.

## 3. Problem Statement

Future generic approval runtime adoption requires a stable decision on two separate but related concepts:

1. what governed transition is being requested;
2. whether the requester and later decider are allowed for that governed transition on that governed resource in that tenant/scope context.

Current runtime does not yet define:

- a governed action registry separate from the narrow runtime allowlist;
- a formal mapping from governed transition identity to RBAC action identity;
- a governed resource identity contract richer than `subject_type` and `subject_ref`;
- a scope-aware approval applicability model;
- a canonical approval security-event taxonomy.

## 4. Governed Action Type Decision

Decision:

> Future governed approval action types must be registry-controlled and must be separate from RBAC action codes.

Rationale:

1. RBAC action codes answer whether an actor may invoke or decide a protected class of API operation.
2. Governed approval action types answer which governed transition is being requested for a governed resource.
3. A single RBAC action code may gate multiple governed transitions over time, while those transitions still need distinct approval semantics and audit evidence.
4. Treating governed approval action types as direct RBAC action codes would collapse permission truth and governance-transition truth into one surface.

Required contract rules:

1. Governed approval action types must not be arbitrary strings.
2. Governed approval action types must be defined in a dedicated registry-controlled contract surface.
3. Governed approval action types must be explicit and stable enough for migration, audit, and reporting.
4. A governed approval action type may map to a corresponding RBAC action code or command intent, but it is not identical to it.

## 5. Relationship to RBAC Action Codes

Decision:

> Governed approval action types and RBAC action codes are separate source-of-truth layers connected by explicit mapping.

RBAC action code meaning:

- answers: `can this actor invoke or decide this protected operation class?`

Governed approval action type meaning:

- answers: `which governed transition is being requested for this governed resource?`

Contract rules:

1. Approval does not replace RBAC.
2. RBAC action codes remain the authorization gate for approval API surfaces such as `approval.create` and `approval.decide`.
3. Future domain adoption must still require the correct domain RBAC action boundary for the actual domain mutation path.
4. Governed approval action type must map explicitly to one of the following:
   - a domain RBAC action code,
   - a backend command intent,
   - or both.
5. The mapping must be backend-controlled and testable.

Decision summary:

- RBAC action code is permission truth.
- Governed approval action type is governed transition truth.
- Approval is an additional governance gate layered on top of RBAC, not a substitute for RBAC.

## 6. Governed Resource Identity Decision

Decision:

> Future approval requests must bind governed approval action types to explicit governed resource identity fields, not only to `subject_type` and `subject_ref`.

Future contract-candidate fields remain:

- `governed_resource_type`
- `governed_resource_id`
- `governed_resource_display_ref`
- `governed_resource_tenant_id`
- `governed_resource_scope_ref`
- `governed_action_type`

Relationship to current fields:

1. `subject_type` and `subject_ref` are current compatibility/display fields only.
2. They may remain temporarily during migration or compatibility handling.
3. They must not remain the only governed identity surface for generic approval adoption.

Decision summary:

- governed resource identity is explicit future contract truth;
- `subject_type` and `subject_ref` are not sufficient as the long-term governed identity model.

## 7. Approval Applicability Resolution

Decision:

> Future approval applicability must be backend-resolved and must evaluate both governed transition context and governed resource context.

At minimum, future applicability matching must evaluate:

- `tenant_id`
- `scope_ref` or equivalent canonical scope reference
- `governed_resource_type`
- `governed_action_type`
- `requester_role`
- `acting_role`

Additional notes:

1. `requester_role` and `acting_role` are part of applicability because approval policy may vary by who is asking and who is deciding.
2. Real-user identity remains authoritative for SoD even if acting role is used for policy evaluation.
3. Applicability resolution must stay backend-owned and deterministic.

This slice does not define the physical schema for applicability storage.

## 8. Tenant and Scope Contract

Decision:

> Future approval applicability must be tenant-aware and canonical-scope-aware.

Required canonical scope support:

- tenant
- plant
- area
- line
- station
- equipment

Contract rules:

1. Tenant-only applicability is insufficient for generic domain adoption.
2. Scope applicability must resolve against the governed resource scope reference.
3. Scope matching may use scope ID, scope path, or equivalent canonical scope reference, provided it remains consistent with the scope foundation.
4. Scope resolution must remain backend truth and must not rely on frontend interpretation.
5. Wildcard/default fallback may exist, but only as an explicit, ordered, testable policy rule.

## 9. Approval Rule Matching Contract

Decision:

> Future approval rule matching must become resource/action/scope-aware rather than action-type-only.

Current state:

- `ApprovalRule` is keyed by `action_type`, `approver_role_code`, and `tenant_id`.

Future contract rule:

Approval rule matching must be capable of matching on at least:

- tenant
- governed action type
- governed resource type
- governed resource scope reference
- decider acting role
- requester role where policy requires it

Decision summary:

1. Current action-type-only rule matching is adequate only for the current narrow approval service.
2. Future generic adoption requires rule matching over both governed transition identity and governed resource context.
3. This slice intentionally leaves physical schema design open.

## 10. Security Event Taxonomy Expectations

Decision:

> Future approval business events must use a canonical approval security-event taxonomy.

Expected future taxonomy:

- `APPROVAL.REQUESTED`
- `APPROVAL.APPROVED`
- `APPROVAL.REJECTED`
- `APPROVAL.CANCELLED` only if cancellation is intentionally implemented later

Required event payload meaning:

1. `APPROVAL.REQUESTED` means a governed approval request was created.
2. `APPROVAL.APPROVED` means a governed approval request was approved.
3. `APPROVAL.REJECTED` means a governed approval request was rejected.
4. `APPROVAL.CANCELLED` must not be emitted unless cancellation becomes a real runtime state.

Required payload minimum:

- tenant
- real actor user id
- governed resource type
- governed resource id
- governed action type
- outcome or decision
- impersonation context if applicable

This slice defines taxonomy expectations only. It does not implement event emission.

## 11. Future DB / Migration Implications

Any future runtime adoption of this contract will likely require:

1. explicit governed action type storage or registry support,
2. explicit governed resource identity fields on approval requests,
3. explicit scope-aware applicability references,
4. approval rule matching structures richer than `(action_type, approver_role_code, tenant_id)`,
5. compatibility handling for legacy rows using only `subject_type` and `subject_ref`.

This slice does not add schema, constraints, or migrations.

## 12. Future API Contract Implications

Any future runtime adoption of this contract will likely require:

1. request payloads carrying explicit governed action type and governed resource identity,
2. response payloads exposing governed approval context clearly,
3. API contracts that preserve the distinction between approval API RBAC action codes and governed transition identity,
4. compatibility handling for current narrow approval API consumers.

This slice does not add or approve any runtime API change.

## 13. Test Requirements Before Runtime Adoption

Before runtime adoption, at minimum the following tests are required:

1. governed action registry tests
2. RBAC/governed-action mapping tests
3. governed resource identity tests
4. tenant/scope applicability tests
5. approval rule matching tests
6. SoD negative tests
7. security event taxonomy tests
8. backward compatibility tests for the current six action types until intentionally superseded

## 14. Explicitly Out of Scope

This contract does not:

- implement generic approval runtime
- add a runtime governed action registry
- add any runtime governed action type
- add any RBAC action code
- modify approval runtime service, models, schemas, repositories, or API
- add migrations
- add approval API endpoints
- add frontend or Admin UI
- modify MMD source, tests, or docs
- change `ACTION_CODE_REGISTRY`
- change route guards

## 15. Open Questions

1. Should the future governed action registry live fully inside approval/governance docs, or should it become a platform-level governance registry shared by multiple governed domains?
2. Should `governed_resource_scope_ref` resolve to scope ID, `(scope_type, scope_value)`, or canonical scope path at runtime?
3. How should future approval rule specificity precedence work when both broader and narrower scope policies match?
4. Should requester-role-sensitive applicability be universal or only required for selected governed transitions?
5. When cancellation is implemented, should `APPROVAL.CANCELLED` represent requester cancellation only, or also admin/governance cancellation?

## 16. Final Decision

Decision: future governed approval action types are separate from RBAC action codes and must be connected by explicit backend-controlled mapping.

Future generic approval runtime adoption is blocked until:

1. governed action type truth is registry-controlled,
2. governed resource identity is explicit,
3. approval applicability is tenant and canonical-scope aware,
4. approval rule matching is resource/action/scope aware,
5. approval business events have canonical `APPROVAL.*` security-event taxonomy.