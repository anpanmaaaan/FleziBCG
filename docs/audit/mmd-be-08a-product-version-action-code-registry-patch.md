# MMD-BE-08A — Product Version Action Code Registry Patch Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Added Product Version MMD mutation action code before write API implementation. |

## 1. Scope
This slice is a narrow backend authorization-registry patch.

In scope:
- add Product Version MMD mutation action code to runtime registry
- add regression checks proving the code exists and Product Version routes remain read-only
- update action-code governance registry documentation

Out of scope:
- Product Version write API implementation
- frontend changes
- migrations/schema changes
- Product Version write behavior changes

## 2. Baseline Evidence Used
Mandatory evidence inspected:
- docs/audit/mmd-write-gov-01-command-boundary.md
- docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md
- docs/design/02_domain/product_definition/product-version-write-governance-contract.md
- docs/audit/mmd-be-08-product-version-write-governance-contract.md
- docs/audit/mmd-be-02-rbac-action-code-fix.md
- docs/design/02_registry/action-code-registry.md

Additional evidence inspected:
- docs/audit/mmd-be-03-product-version-foundation-read-model.md
- docs/audit/mmd-fullstack-06-product-version-fe-read-integration.md
- docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md

Source inspection highlights:
- backend/app/security/rbac.py did not contain admin.master_data.product_version.manage.
- backend/app/api/v1/products.py still contains Product Version read routes only (GET list/detail).
- backend/tests/test_product_version_foundation_api.py already locks absence of Product Version write routes.

## 3. Authorization Contract Decision
Decision:
- Add `admin.master_data.product_version.manage` as a domain-specific MMD mutation code.
- Map it to `ADMIN` family, consistent with existing MMD manage action codes.
- Keep existing codes unchanged:
  - `admin.master_data.product.manage`
  - `admin.master_data.routing.manage`
  - `admin.master_data.resource_requirement.manage`

Rationale:
- Product Version write governance contract requires dedicated action code before future write APIs.
- Registry addition alone must not introduce or imply write endpoint behavior.

## 4. Files Changed
- backend/app/security/rbac.py
- backend/tests/test_mmd_rbac_action_codes.py
- docs/design/02_registry/action-code-registry.md
- docs/audit/mmd-be-08a-product-version-action-code-registry-patch.md

## 5. Backend Changes
### Runtime registry
In backend/app/security/rbac.py, added:
- `"admin.master_data.product_version.manage": "ADMIN"`

No API route, service, schema, or migration changes were made.

### Test coverage extension
In backend/tests/test_mmd_rbac_action_codes.py, added tests for:
- Product Version manage action code existence
- Product Version manage action code family and domain-specific identity
- existing MMD action code continuity
- Product Version read endpoint guard (no require_action)
- no Product Version write route markers in products router source

## 6. Tests Added / Updated
Updated:
- backend/tests/test_mmd_rbac_action_codes.py

Added test intents:
- test_product_version_manage_action_code_exists
- test_product_version_manage_action_code_is_domain_specific
- test_existing_mmd_action_codes_still_exist
- test_product_version_read_endpoints_do_not_require_manage_action
- test_no_product_version_write_routes_exist_yet

## 7. Read Endpoint Impact
No read endpoint behavior change.

Product Version read endpoints remain authenticated-read and unchanged:
- GET /api/v1/products/{product_id}/versions
- GET /api/v1/products/{product_id}/versions/{version_id}

## 8. Boundary Guardrails
Verified guardrails:
- No Product Version write API added.
- No frontend source changed.
- No DB migration/schema changes.
- Action-code addition does not grant endpoint behavior by itself.
- Existing MMD action codes remain present.

## 9. Verification Commands
Executed for this slice:
- cd backend
- python -m pytest -q tests/test_mmd_rbac_action_codes.py
- python -m pytest -q tests/test_product_version_foundation_api.py tests/test_product_version_foundation_service.py
- cd frontend
- npm run check:mmd:read
- npm run check:routes

## 10. Remaining Risks / Deferred Items
- Dedicated Product Version write APIs remain deferred to a future implementation slice.
- Role/permission seed review for the new action code in environment-specific data remains an operational follow-up if needed.
- Granular Product Version verbs (create/update/release/retire split) remain deferred; current contract uses `.manage`.

## 11. Final Verdict
PASS — MMD-BE-08A completed as a narrow authorization-registry patch.

Definition of done status:
- Product Version action code exists in runtime registry.
- Action-code registry doc updated.
- Existing MMD action codes preserved.
- Product Version write APIs remain unimplemented.
- Read endpoints remain unchanged.
- Regression tests expanded for new governance checks.
- No frontend changes, no migration changes, no auto-commit.
