# Governed Action Type Registry Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Defined governed action type registry contract for future approval runtime adoption. |

## 1. Purpose

This contract defines the source-of-truth model for future governed approval action types.

It exists to lock taxonomy and governance boundaries before runtime implementation.

This is design-only. It does not authorize runtime implementation.

## 2. Current Source Evidence

Evidence reviewed:

- docs/audit/p0-a-13a-governed-resource-identity-schema-closeout-report.md
- docs/audit/p0-a-13-governed-resource-identity-schema-report.md
- docs/design/01_foundation/governed-action-approval-applicability-contract.md
- docs/design/01_foundation/approval-service-generic-extension-contract.md
- docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md
- backend/app/models/approval.py
- backend/app/schemas/approval.py
- backend/app/services/approval_service.py
- backend/app/security/rbac.py
- docs/design/02_registry/action-code-registry.md
- backend/tests/test_approval_governed_resource_identity_schema.py
- backend/tests/test_approval_service_current_behavior.py
- backend/tests/test_approval_security_events.py

Current source truth:

1. Approval runtime still enforces six hardcoded VALID_ACTION_TYPES.
2. Approval API authorization uses RBAC action codes approval.create and approval.decide.
3. ApprovalRequest now has nullable governed_action_type (schema foundation only).
4. No runtime governed action registry exists yet.
5. Security-event emission currently uses APPROVAL.REQUESTED / APPROVAL.APPROVED / APPROVAL.REJECTED.

## 3. Current Runtime Approval Action Types

Current runtime ApprovalRequest.action_type accepts only:

- QC_HOLD
- QC_RELEASE
- SCRAP
- REWORK
- WO_SPLIT
- WO_MERGE

Contract lock:

- This set remains runtime truth until a future implementation slice explicitly changes it.
- This contract does not change current runtime behavior.

## 4. Problem Statement

The platform has governed_action_type schema foundation but lacks canonical governed action type registry contract.

Without a contract:

- future governed action naming can drift,
- mapping to RBAC can become inconsistent,
- event taxonomy can diverge across domains,
- adoption rules can become ad hoc.

A design contract is required before runtime adoption of governed_action_type.

## 5. Governed Action Type Definition

Decision:

A governed action type identifies the governed transition intent requested for a governed resource and evaluated through approval governance.

Governed action type semantics:

- transition-intent truth,
- resource-context aware,
- independent from transport and endpoint naming,
- stable enough for audit, policy, and migration.

It is not a freeform request string.

## 6. Relationship to RBAC Action Codes

Decision:

Governed action types and RBAC action codes are distinct layers connected by explicit mapping.

RBAC action code answers:

- may this actor invoke or decide this class of operation?

Governed action type answers:

- what governed transition is being requested for approval?

Contract lock:

1. Approval does not replace RBAC.
2. RBAC remains authorization truth at API boundary.
3. Governed action type remains transition-governance truth.
4. Mapping from governed action type to required RBAC action code must be explicit and testable.

## 7. Relationship to ApprovalRequest.governed_action_type

Current state:

- ApprovalRequest.governed_action_type exists and is nullable.
- Runtime does not enforce or match on it.

Contract decision:

- governed_action_type is currently schema foundation only.
- Future runtime adoption must use this field as canonical transition identity.
- Existing action_type continues to drive current runtime matching until future migration slice.

## 8. Naming Convention

Decision:

Future governed action type naming follows:

- <domain>.<resource>.<transition>

Examples (contract examples only, not runtime additions):

- quality.lot.release
- execution.wo.split
- execution.wo.merge
- master_data.product_version.release
- master_data.bom.retire

MMD examples above are future examples only and are not implementation in this slice.

Naming rules:

1. lowercase, dot-separated segments,
2. no spaces,
3. transition verb in final segment,
4. resource noun in middle segment,
5. domain segment must align with domain boundary map.

## 9. Initial Runtime Posture

Current runtime posture is unchanged:

1. VALID_ACTION_TYPES remains the only runtime action allowlist.
2. governed_action_type remains nullable schema-only field.
3. No runtime governed action registry exists.
4. No scope-aware rule matching is implemented.
5. No APPROVAL.CANCELLED service path is implemented.

## 10. Future Registry Shape

Candidate registry fields (contract level only):

- governed_action_type
- domain
- resource_type
- transition
- required_rbac_action_code
- security_event_requested
- security_event_approved
- security_event_rejected
- default_requires_approval
- status
- version

This slice does not create runtime table/model for this registry.

## 11. Future Adoption Rules

Before runtime adoption of a new governed action type:

1. Add contract entry to governed action registry definition.
2. Define explicit required_rbac_action_code mapping.
3. Define governed resource identity requirements.
4. Define scope applicability expectations.
5. Define SecurityEventLog mapping.
6. Add regression tests.
7. Roll out with backward-compatible migration strategy.

No domain may directly adopt new governed action types without satisfying these rules.

## 12. SecurityEventLog Mapping

Future approval lifecycle mapping per governed action type:

- requested -> APPROVAL.REQUESTED
- approved -> APPROVAL.APPROVED
- rejected -> APPROVAL.REJECTED
- cancelled -> APPROVAL.CANCELLED only if service path is intentionally implemented

Current emission remains unchanged in this slice.

## 13. Test Requirements Before Runtime Adoption

Required test categories:

1. governed action registry integrity tests,
2. governed action to RBAC mapping tests,
3. approval request validation tests for governed_action_type,
4. tenant and scope applicability tests,
5. separation-of-duties tests under impersonation,
6. SecurityEventLog taxonomy tests,
7. backward compatibility tests for existing six runtime action types.

No runtime adoption is allowed without these tests.

## 14. Explicitly Out of Scope

This contract does not:

- implement runtime governed action registry,
- modify VALID_ACTION_TYPES,
- modify ACTION_CODE_REGISTRY,
- add MASTER_DATA approval action type runtime behavior,
- enforce governed_action_type in approval runtime,
- implement scope-aware approval rule matching,
- add migrations,
- add APIs,
- add frontend/Admin UI,
- implement APPROVAL.CANCELLED service path.

## 15. Open Questions

1. Future ownership model for governed action registry (foundation-owned vs domain-owned extension model).
2. Whether version should be semantic version, integer revision, or effective-date model.
3. Whether default_requires_approval should support conditional policy expressions.
4. Whether transition aliases are allowed during migration windows.
5. How to phase from current action_type runtime matching to governed_action_type runtime matching.

## 16. Final Decision

Decision:

- Establish a design-level governed action type registry contract now.
- Keep runtime unchanged.
- Treat governed_action_type as schema foundation only until a dedicated runtime adoption slice.
- Enforce strict distinction: RBAC action code is permission truth; governed action type is governed transition truth.
