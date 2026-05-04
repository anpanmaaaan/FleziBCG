# MMD-BE-13A — Reason Code Write Boundary Audit / Event Guardrail Patch Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-04 | v1.0 | Verified and patched Reason Code write boundary guardrails after Reason Code write API foundation. |

## 1. Scope
This slice verifies that Reason Code write APIs remain strictly in MMD classification/reference truth and do not cross into operational domains. It also patches any detected boundary leak.

In-scope checks:
- Event boundary for Reason Code mutations
- Route boundary (allowed routes present, forbidden routes absent)
- Data boundary (write payload shape, schema forbids, no coupling)
- Lifecycle and authorization guardrails
- Downtime Reason boundary isolation

Out of scope (unchanged):
- New endpoints
- Frontend write support
- allowed_actions for Reason Code
- activate/deactivate, reactivate, hard delete, clone, bulk import, merge/split
- downtime_reason mapping
- execution/quality/material/inventory/scrap/backflush/ERP/traceability/maintenance behavior
- policy binding and authorization grants
- migrations

## 2. Baseline Evidence Used
- docs/audit/mmd-be-13-reason-code-write-api-foundation.md
- docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md
- docs/audit/mmd-be-10-reason-code-write-governance-contract.md
- docs/design/02_domain/product_definition/reason-code-write-governance-contract.md
- docs/audit/mmd-be-07-reason-code-minimal-read-model.md
- docs/audit/mmd-fullstack-08-reason-codes-fe-read-integration.md
- docs/design/02_domain/product_definition/reason-code-foundation-contract.md
- docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md
- docs/design/02_registry/action-code-registry.md
- docs/design/00_platform/product-business-truth-overview.md

## 3. Source Inspection Summary
Inspected backend source and tests:
- backend/app/models/reason_code.py
- backend/app/schemas/reason_code.py
- backend/app/repositories/reason_code_repository.py
- backend/app/services/reason_code_service.py
- backend/app/api/v1/reason_codes.py
- backend/app/security/rbac.py
- backend/app/models/downtime_reason.py
- backend/app/api/v1/downtime_reasons.py
- backend/app/schemas/operation.py
- backend/tests/test_reason_code_foundation_api.py
- backend/tests/test_reason_code_foundation_service.py
- backend/tests/test_mmd_rbac_action_codes.py

Keyword boundary sweep performed against reason-code write path and adjacent files for:
- downtime_reason, start_downtime, end_downtime, pause, resume
- quality, quality_hold
- material, inventory, scrap, backflush
- erp, posting
- traceability, genealogy
- maintenance, work_order
- policy, authorization, grant

## 4. Event Boundary Findings
Finding:
- Reason Code write events were scoped to security-event logging only, but naming used REASONCODE.*.

Patch applied:
- Normalized event names to canonical allowed set:
  - ReasonCode.CREATED
  - ReasonCode.UPDATED
  - ReasonCode.RELEASED
  - ReasonCode.RETIRED

Verification:
- No execution/downtime/material/quality/ERP/traceability/maintenance event names or side-effect service calls in reason_code_service.py.
- Added explicit test guard to lock canonical ReasonCode.* naming and forbid legacy REASONCODE.* naming.

## 5. Route Boundary Findings
Allowed routes verified present:
- POST /api/v1/reason-codes
- PATCH /api/v1/reason-codes/{reason_code_id}
- POST /api/v1/reason-codes/{reason_code_id}/release
- POST /api/v1/reason-codes/{reason_code_id}/retire

Forbidden routes verified absent:
- DELETE /api/v1/reason-codes/{reason_code_id}
- POST /api/v1/reason-codes/{reason_code_id}/reactivate
- POST /api/v1/reason-codes/{reason_code_id}/activate
- POST /api/v1/reason-codes/{reason_code_id}/deactivate
- POST /api/v1/reason-codes/{reason_code_id}/clone
- POST /api/v1/reason-codes/bulk-import
- POST /api/v1/reason-codes/{reason_code_id}/map-downtime-reason
- POST /api/v1/reason-codes/{reason_code_id}/bind-policy
- POST /api/v1/reason-codes/{reason_code_id}/execute
- POST /api/v1/reason-codes/{reason_code_id}/start-downtime
- POST /api/v1/reason-codes/{reason_code_id}/quality-accept
- POST /api/v1/reason-codes/{reason_code_id}/material-move
- POST /api/v1/reason-codes/{reason_code_id}/erp-post

## 6. Data Boundary Findings
Verified:
- Create/Update write schemas use extra forbid.
- Write schemas do not accept downtime_reason_id, execution_policy_id, quality_policy_id, material_policy_id.
- Client cannot set lifecycle_status, tenant_id, reason_code_id in write payloads.
- Generic PATCH cannot mutate reason_code or reason_domain.

Patch added:
- New API test for immutable reason_category patch rejection.
- New service-level schema guard test for immutable reason_category.

## 7. Lifecycle / Authorization Guardrail Findings
Verified lifecycle guardrails:
- Create sets DRAFT.
- Update allowed only when current status is DRAFT.
- Release allowed only from DRAFT.
- Retire allowed from DRAFT or RELEASED.
- Retire rejects already RETIRED.
- Generic PATCH cannot set lifecycle_status.

Verified authorization guardrails:
- Mutation routes require admin.master_data.reason_code.manage.
- Read routes remain require_authenticated_identity and do not require manage action.
- Action code registry still contains admin.master_data.reason_code.manage mapped to ADMIN.

## 8. Downtime Reason Boundary Findings
Verified:
- No downtime_reason mapping in reason_code write service/repository.
- downtime_reasons API not modified.
- reason_code write path does not import downtime_reason repository/service.
- operation schema remains downtime-owned for start_downtime reason_code resolution.

## 9. Tests Added / Updated
Updated:
- backend/tests/test_reason_code_foundation_api.py
  - added test_update_reason_code_rejects_reason_category_patch

Updated:
- backend/tests/test_reason_code_foundation_service.py
  - added test_update_reason_code_rejects_immutable_reason_category
  - added test_reason_code_event_names_are_canonical_and_non_operational

Updated:
- Existing suites remained green after patch; no new endpoint tests beyond guardrail hardening.

## 10. Files Changed
- backend/app/services/reason_code_service.py
- backend/tests/test_reason_code_foundation_api.py
- backend/tests/test_reason_code_foundation_service.py
- docs/audit/mmd-be-13-reason-code-write-api-foundation.md
- docs/audit/mmd-be-13a-reason-code-write-boundary-guardrail.md

## 11. Verification Commands
Requested command form first:
- cd backend
- python -m pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
- python -m pytest -q tests/test_mmd_rbac_action_codes.py
- python -m pytest -q tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_bom_foundation_api.py

Result:
- python command unavailable on PATH in this environment (Windows app execution alias prompt).

Repo-compatible fallback executed:
- cd backend
- uv run --with pytest --with fastapi --with sqlalchemy --with httpx --with anyio --with passlib --with python-jose --with bcrypt --with pydantic-settings --with psycopg[binary] --with alembic --python 3.12 python -m pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
  - 62 passed, 1 warning
- uv run --with pytest --with fastapi --with sqlalchemy --with httpx --with anyio --with passlib --with python-jose --with bcrypt --with pydantic-settings --with psycopg[binary] --with alembic --python 3.12 python -m pytest -q tests/test_mmd_rbac_action_codes.py
  - 31 passed, 1 warning
- uv run --with pytest --with fastapi --with sqlalchemy --with httpx --with anyio --with passlib --with python-jose --with bcrypt --with pydantic-settings --with psycopg[binary] --with alembic --python 3.12 python -m pytest -q tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_bom_foundation_api.py
  - 83 passed, 1 warning

Frontend checks:
- cd frontend
- npm run check:mmd:read (blocked by PowerShell execution policy)
- npm run check:routes (blocked by PowerShell execution policy)
- npm.cmd run check:mmd:read
  - 134 passed, 0 failed
- npm.cmd run check:routes
  - PASS 24, FAIL 0

## 12. Remaining Risks / Deferred Items
- Event naming was corrected to ReasonCode.* in service; any external downstream consumer expecting legacy REASONCODE.* would need to align (none found in current tests/source).
- Write governance remains intentionally coarse under one manage action code; lifecycle-specific split remains deferred by design governance.
- Service/API boundary comments in tests include some non-ASCII artifacts from prior formatting; behavior is unaffected.

## 13. Final Verdict
PASS

Reason Code write path remains inside MMD classification/reference truth after patch:
- No operational side effects detected
- No downtime_reason coupling introduced
- No forbidden routes introduced
- Lifecycle and authorization guardrails hold
- Event naming now constrained to allowed ReasonCode.* security events
- Required backend and frontend verification checks passed via environment-compatible command pattern
