# MMD-FULLSTACK-12 - BOM FE Write Intent / Governance-Gated Integration Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Added BOM FE write-intent integration for create, metadata update, release, retire, and item add/update/remove using existing governed backend APIs. |

## 1. Scope

In scope:
- Frontend API helpers for BOM write intents
- BOM List create-intent form bound to selected product context
- BOM Detail write-intent actions: metadata update, release, retire
- BOM Detail item write-intent actions: add, update, remove
- Lifecycle-plausible UI gating with backend-authoritative rejection handling
- i18n additions for write-intent UX and error handling
- Regression guardrail expansion for BOM write-intent contracts
- Audit artifact for MMD-FULLSTACK-12

Out of scope:
- Backend source changes
- Database migrations
- BOM hard delete
- BOM reactivate
- BOM clone/copy
- Bulk replace/edit/reorder operations
- Product-version binding from BOM UI
- Material/inventory/backflush side effects
- ERP posting or PLM sync
- Quality, traceability, APS, digital twin, or AI decision coupling

## 2. Baseline Evidence Used

Mandatory evidence inspected before coding:
- .github/copilot-instructions.md
- .github/agent/AGENT.md
- docs/design/INDEX.md
- docs/design/AUTHORITATIVE_FILE_MAP.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md
- docs/governance/SOURCE_STRUCTURE.md
- docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- docs/ai-skills/hard-mode-mom-v3/SKILL.md
- backend/app/api/v1/products.py
- backend/app/schemas/product.py
- backend/app/services/bom_service.py
- frontend/src/app/api/productApi.ts
- frontend/src/app/pages/BomList.tsx
- frontend/src/app/pages/BomDetail.tsx
- frontend/src/app/i18n/registry/en.ts
- frontend/src/app/i18n/registry/ja.ts
- frontend/scripts/mmd-read-integration-regression-check.mjs

## 3. Pre-Coding Evidence Maps

### 3.1 Routing
- Selected brain: FleziBCG AI Brain v6 auto-execution
- Selected mode: Hard Mode MOM v3
- Hard Mode MOM: ON
- Reason: BOM write intent touches governed lifecycle transitions and backend authorization boundaries in master data.

### 3.2 Design Evidence Extract
- Backend already exposes seven governed BOM write endpoints under products scope.
- BOM write endpoints require admin.master_data.bom.manage action authorization.
- BOM read endpoints require authenticated identity.
- Backend request contracts for BOM write do not include lifecycle_status or product_version_id in create/update metadata payloads.
- Backend item update contract excludes immutable fields line_no and component_product_id.
- No server-derived allowed_actions payload currently exists for BOM FE gating.

### 3.3 Event Map
| FE intent | Backend endpoint | Backend event truth |
|---|---|---|
| create BOM | POST /products/{product_id}/boms | PRODUCT_BOM.CREATED |
| update metadata | PATCH /products/{product_id}/boms/{bom_id} | PRODUCT_BOM.UPDATED |
| release | POST /products/{product_id}/boms/{bom_id}/release | PRODUCT_BOM.RELEASED |
| retire | POST /products/{product_id}/boms/{bom_id}/retire | PRODUCT_BOM.RETIRED |
| add item | POST /products/{product_id}/boms/{bom_id}/items | PRODUCT_BOM_ITEM.ADDED |
| update item | PATCH /products/{product_id}/boms/{bom_id}/items/{bom_item_id} | PRODUCT_BOM_ITEM.UPDATED |
| remove item | DELETE /products/{product_id}/boms/{bom_id}/items/{bom_item_id} | PRODUCT_BOM_ITEM.REMOVED |

Boundary note:
This slice submits intent only. No execution, quality disposition, inventory movement, ERP posting, traceability facts, or AI decisioning was introduced.

### 3.4 Invariant Map
| # | Invariant | Enforcement |
|---|---|---|
| I-01 | Frontend sends intent only; backend remains authorization truth | explicit governance notice + 401/403 handling |
| I-02 | Create/update metadata payload excludes lifecycle_status and product_version_id | request types + regression check |
| I-03 | Item update payload excludes line_no/component_product_id | request types + regression check |
| I-04 | Metadata edit and item mutations only surfaced in DRAFT | lifecycle gating in BomDetail |
| I-05 | Release only surfaced in DRAFT | lifecycle gating in BomDetail |
| I-06 | Retire only surfaced in DRAFT/RELEASED | lifecycle gating in BomDetail |
| I-07 | Forbidden BOM controls remain absent | regression check |
| I-08 | Post-mutation views refresh from backend read APIs | loadBoms/loadBom after successful writes |

### 3.5 State Transition Map
DRAFT -> RELEASED (release)
DRAFT -> RETIRED (retire)
RELEASED -> RETIRED (retire)

Editable in UI:
- DRAFT metadata and items

Blocked/deferred in UI:
- hard delete
- reactivate
- clone/copy
- bulk replace/reorder
- bind product version
- inventory/material/backflush coupling

### 3.6 Test Matrix
| Check | Target |
|---|---|
| npm.cmd run check:mmd:read | BOM write/read FE regression guardrails |
| npm.cmd run build | frontend compile |
| npm.cmd run lint | frontend lint |
| npm.cmd run lint:i18n:registry | i18n parity |
| npm.cmd run check:routes | route smoke coverage |
| npm.cmd run lint:i18n | optional full i18n lint |
| g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_bom_foundation_api.py tests/test_bom_foundation_service.py tests/test_mmd_rbac_action_codes.py | backend BOM/RBAC contract preservation |

### 3.7 Verdict Before Coding
PROCEED - implement minimal BOM FE write-intent integration with lifecycle-plausible controls and backend-authoritative rejection handling.

## 4. Files Changed

### Frontend implementation
- frontend/src/app/api/productApi.ts - added BOM write request types and seven write helpers
- frontend/src/app/api/index.ts - exported BOM write request types
- frontend/src/app/pages/BomList.tsx - added product-scoped BOM create intent form and safe backend error mapping
- frontend/src/app/pages/BomDetail.tsx - added lifecycle-gated metadata/item write intents and release/retire controls
- frontend/src/app/i18n/registry/en.ts - added BOM write-intent strings
- frontend/src/app/i18n/registry/ja.ts - added BOM write-intent strings
- frontend/scripts/mmd-read-integration-regression-check.mjs - added BOM write-intent regression checks

### Audit artifact
- docs/audit/mmd-fullstack-12-bom-fe-write-intent.md - this report

## 5. FE Behavior Summary

### BOM List
- Requires selected product context before create action is enabled.
- Validates required fields and date range before submit.
- Sends create intent via POST helper and refreshes backend BOM list on success.
- Maps 401/403/404/409/422 and fallback errors without inventing local policy truth.

### BOM Detail
- Loads BOM detail via product+bom context and keeps backend as read truth.
- Metadata update available only while DRAFT.
- Release available only while DRAFT.
- Retire available only while DRAFT or RELEASED.
- Item add/edit/remove available only while DRAFT.
- Successful writes always reload backend detail.

### Governance
- Both BOM screens display explicit backend-authorization governance notice.
- No client-side role inference or fake permission truth introduced.
- Backend 403 remains final and operator-visible.

## 6. Verification Results

### Frontend - MMD regression
```
122 passed, 0 failed
```

### Frontend - build
```
✓ built in 10.01s
```

### Frontend - lint
```
eslint src/
```
No lint diagnostics were emitted.

### Frontend - i18n registry parity
```
[i18n-registry] PASS: en.ts and ja.ts are key-synchronized (1816 keys).
```

### Frontend - route smoke
```
PASS: 24
FAIL: 0
```

### Frontend - optional full i18n lint
```
scripts/check_i18n_hardcode.sh: line 4: $'\r': command not found
```
This is an existing Windows/CRLF shell-script portability issue in lint:i18n:hardcode.

### Backend - BOM API/service/RBAC
```
90 passed, 1 warning in 5.07s
```
Warning observed:
- Local database URL does not look test-specific (existing test-environment warning).

## 7. Boundary Guardrails Verified

- No forbidden BOM controls were introduced.
- No backend or migration files were changed.
- Frontend payload contracts preserve backend governance boundaries.
- Backend remains final authority for permission and lifecycle transitions.
- BOM write actions remain product-scoped and reload backend read truth after mutation.

## 8. Remaining Risks / Deferred Items

- Without server-derived BOM allowed_actions, UI uses lifecycle-plausible gating and still depends on backend 403 for final permission truth.
- Optional full i18n lint remains non-portable on this Windows environment until line endings/invocation are normalized.

## 9. Final Verdict

PASS - MMD-FULLSTACK-12 completed as a governance-gated BOM FE write-intent integration using existing backend contract truth.
