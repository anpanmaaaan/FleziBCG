# MMD-FULLSTACK-11 — Product Version FE Write Intent / Governance-Gated Integration Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Added Product Version FE write intent on Product Detail using existing governed backend APIs for create, draft edit, release, and retire. |

## 1. Scope

In scope:
- Frontend API helpers for Product Version create, update, release, and retire
- Product Detail Product Version create form
- Product Detail draft-only edit flow
- Product Detail release and retire write-intent actions
- Safe handling for backend `401`, `403`, `404`, `409`, `422`, and `400`-style validation responses
- Product Version regression guardrail updates
- Product Detail i18n and screen-status updates
- Audit artifact for MMD-FULLSTACK-11

Out of scope:
- Product Version delete
- Product Version reactivate
- Product Version set_current
- Product Version clone/copy
- Product Version binding to BOM, Routing, or Resource Requirements
- ERP/PLM sync
- Engineering change workflow
- Acceptance Gate
- Backflush
- Quality linkage
- Material movement
- Traceability genealogy
- Backend source changes
- Database migrations

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
- docs/design/00_platform/product-business-truth-overview.md
- docs/design/DESIGN.md
- docs/audit/frontend-source-alignment-snapshot.md
- backend/app/api/v1/products.py
- backend/app/schemas/product.py
- backend/app/services/product_version_service.py
- frontend/src/app/api/productApi.ts
- frontend/src/app/pages/ProductDetail.tsx
- frontend/src/app/screenStatus.ts
- frontend/scripts/mmd-read-integration-regression-check.mjs

## 3. Pre-Coding Evidence Maps

### 3.1 Routing
- Selected brain: FleziBCG AI Brain v6 auto-execution
- Selected mode: Hard Mode MOM v3
- Hard Mode MOM: ON
- Reason: Product Version write intent touches governed master-data lifecycle truth and backend authorization boundaries.

### 3.2 Design Evidence Extract
- Product Detail already consumed backend Product and Product Version read APIs.
- Backend write endpoints already existed for create, patch, release, and retire.
- Backend request contracts forbid `lifecycle_status` and `is_current` write payload fields.
- Backend service enforces: create => `DRAFT`, update => `DRAFT` only, release => `DRAFT` only, retire => blocked for current version and allowed only from `DRAFT` or `RELEASED`.
- No Product Version `allowed_actions` read model is currently exposed to the frontend.

### 3.3 Event Map
| FE intent | Backend endpoint | Backend event truth |
|---|---|---|
| create | `POST /products/{product_id}/versions` | `PRODUCT_VERSION.CREATED` |
| update | `PATCH /products/{product_id}/versions/{version_id}` | `PRODUCT_VERSION.UPDATED` |
| release | `POST /products/{product_id}/versions/{version_id}/release` | `PRODUCT_VERSION.RELEASED` |
| retire | `POST /products/{product_id}/versions/{version_id}/retire` | `PRODUCT_VERSION.RETIRED` |

Boundary note:
Product Version FE writes remain MMD definition intent only. This slice does not introduce execution commands, state-machine transitions, material movement, quality decisions, ERP posting, or traceability side effects.

### 3.4 Invariant Map
| # | Invariant | Enforcement |
|---|---|---|
| I-01 | Frontend sends only allowed write payload fields | `productApi` request types |
| I-02 | Frontend does not send `lifecycle_status` | request type boundary + regression check |
| I-03 | Frontend does not send `is_current` | request type boundary + regression check |
| I-04 | Draft-only edit surfaced in UI | Product Detail lifecycle gate |
| I-05 | Release surfaced only for `DRAFT` | Product Detail lifecycle gate |
| I-06 | Retire hidden for `is_current=true` and non-`DRAFT/RELEASED` | Product Detail lifecycle gate |
| I-07 | Backend remains authorization truth | error handling + governance notice |
| I-08 | Forbidden Product Version commands remain absent | regression check |
| I-09 | Write success refreshes backend Product Version read model | Product Detail reload behavior |

### 3.5 State Transition Map
```
DRAFT -> RELEASED  (release)
DRAFT -> RETIRED   (retire)
RELEASED -> RETIRED (retire)

Editable in UI:
DRAFT only

Blocked / deferred in UI:
RETIRED -> DRAFT
RETIRED -> RELEASED
set_current
clone/copy
bind-*
```

### 3.6 Authorization / Permission Map
- Read endpoints require authenticated identity.
- Write endpoints require `admin.master_data.product_version.manage`.
- No generic Product Version `allowed_actions` payload exists in the current read model.
- Decision: lifecycle-gate the UI for plausibility, but never claim FE permission truth.
- Backend `401/403/404/409/422/400` responses remain final and are surfaced to the user.

### 3.7 API Contract Map
| FE helper | Request fields |
|---|---|
| `createProductVersion` | `version_code`, `version_name`, `effective_from`, `effective_to`, `description` |
| `updateProductVersion` | `version_name`, `effective_from`, `effective_to`, `description` |
| `releaseProductVersion` | none |
| `retireProductVersion` | none |

### 3.8 Test Matrix
| Check | Target |
|---|---|
| `npm.cmd run check:mmd:read` | Product Version FE regression guardrails |
| `npm.cmd run build` | frontend compile |
| `npm.cmd run lint` | frontend lint |
| `npm.cmd run lint:i18n:registry` | i18n key parity |
| `npm.cmd run check:routes` | route smoke coverage |
| `g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_product_version_foundation_api.py tests/test_product_version_foundation_service.py tests/test_mmd_rbac_action_codes.py` | backend Product Version/RBAC contract preservation |

### 3.9 Verdict Before Coding
PROCEED — implement a minimal Product Detail write-intent slice using existing governed backend APIs, lifecycle-gated in UI, with backend authorization truth preserved.

## 4. Files Changed

### Frontend implementation
- `frontend/src/app/api/productApi.ts` — added Product Version write request types and write helpers
- `frontend/src/app/api/index.ts` — exported Product Version write request types
- `frontend/src/app/pages/ProductDetail.tsx` — added Product Version create, draft edit, release, retire intent UI and backend-owned error handling
- `frontend/src/app/screenStatus.ts` — updated Product Detail maturity note
- `frontend/src/app/i18n/registry/en.ts` — added Product Version write-intent strings
- `frontend/src/app/i18n/registry/ja.ts` — added Product Version write-intent strings
- `frontend/scripts/mmd-read-integration-regression-check.mjs` — replaced old read-only Product Version lock with governed write-intent guardrails

### Audit artifact
- `docs/audit/mmd-fullstack-11-product-version-fe-write-intent.md` — this report

## 5. FE Behavior Summary

### Create
- Inline Product Version create form added to Product Detail.
- Frontend validates required `version_code` and effective-date ordering before request.
- Success reloads Product Version list from backend.

### Draft Edit
- Edit affordance appears only for `DRAFT` versions.
- Version Code remains read-only after creation.
- Success reloads Product Version list from backend.

### Release / Retire
- Release action appears only for `DRAFT` versions.
- Retire action is disabled for current versions and for statuses outside `DRAFT` / `RELEASED`.
- Confirmation prompt precedes each lifecycle action.

### Authorization Truth
- No persona-based or client-side RBAC truth was introduced.
- UI copy states that authorization and final transition truth remain backend-governed.
- Backend rejection responses are mapped to operator-facing messages without inventing local policy state.

## 6. Verification Results

### Frontend — MMD regression
```
93 passed, 0 failed
```

### Frontend — build
```
✓ built in 11.21s
```

### Frontend — lint
```
eslint src/
```
No lint diagnostics were reported for the touched files.

### Frontend — i18n registry parity
```
[i18n-registry] PASS: en.ts and ja.ts are key-synchronized (1770 keys).
```

### Frontend — route smoke
```
PASS: 24
FAIL: 0
```

### Frontend — optional full i18n lint
```
scripts/check_i18n_hardcode.sh: line 4: $'\r': command not found
```
This is an existing Windows/CRLF shell-script portability issue in `lint:i18n:hardcode`, not a Product Version slice failure.

### Backend — Product Version API / service / RBAC
```
52 passed, 1 warning in 2.80s
```
Warning observed:
- Test environment warns that the local database URL does not look test-specific.

## 7. Boundary Guardrails Verified

- No delete / reactivate / set-current / clone / bind-* Product Version UI was added.
- No backend source or migration files were modified.
- Product Version FE write payload types exclude `lifecycle_status` and `is_current`.
- Backend remains authorization truth for Product Version writes.
- Product Detail still consumes Product Version backend reads after each mutation.
- Product lifecycle actions remain separate and still not connected in this slice.

## 8. Remaining Risks / Deferred Items

- FE cannot pre-resolve Product Version manage authorization without a backend-derived capability field; unauthorized users will see lifecycle-plausible actions but receive backend `403` on submit.
- Clearing optional Product Version fields to `null` is not supported by the current backend update semantics.
- Optional `lint:i18n` remains non-portable on this Windows environment until the shell script line endings / invocation are normalized.

## 9. Final Verdict

PASS — MMD-FULLSTACK-11 completed as a minimal, governance-gated Product Version FE write-intent integration on Product Detail.
