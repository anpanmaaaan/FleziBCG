# MMD-FE-QA-03 — Visual QA Preparation Pack (capture cần browser env)

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-20 | v0.1 | PO-SA agent preparation pack. Actual screenshot capture deferred to a coding/QA agent with a running browser + seeded backend (PO-SA sandbox is Linux-headless and has no Postgres of the project). |

> **Status note**: This file is the *preparation pack* for MMD-FE-QA-03, not the executed slice. It provides the seed plan, the expected-vs-observed matrix template, and the capture checklist. A coding/QA agent (or human QA) must run the actual capture against a running stack.

---

## 1. Why this is a prep pack, not the executed slice

The PO-SA agent works in a headless Linux sandbox without Postgres, without the FleziBCG `.venv`, without a browser GUI, and without the ability to render the React app. Visual QA evidence (screenshots, network capture, devtools console) cannot be produced from this environment.

To honor the slice DoD (12+ screenshots, expected-vs-observed matrix), this prep pack provides:

1. Seed-data SQL / fixture instructions.
2. Capture checklist (cases, personas, locales).
3. Expected outcome per case (so any deviation is a defect).
4. The verification gates the executor must run before and after capture.
5. The report template to fill in.

The executor (coding/QA agent or human) follows §3–§7 below and produces `docs/audit/mmd-fe-qa-03-runtime-visual-evidence-pack.md` + `docs/audit/mmd-fe-qa-03-screenshots/`.

---

## 2. Reading order for the executor

1. This prep pack.
2. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (authoritative contract — §8 UI, §9.3 capability matrix).
3. `docs/audit/mmd-current-state-report.md` v2.0.
4. `docs/audit/mmd-fe-qa-02-runtime-visual-evidence-pack.md` (pattern from a prior QA slice).
5. `docs/ai-skills/qa-e2e-layer/SKILL.md`.

---

## 3. Seed data

Use a fresh local stack against a clean Postgres schema upgraded to alembic head `0019` (the current Quality head — Quality migrations do not affect MMD seeding).

Tenant: any test tenant (e.g., `t-mmdqa-001`).

Master data seeds:

```
Product:        P1 (RELEASED)
Product Versions for P1:
  PV-DRAFT-A      lifecycle=DRAFT
  PV-DRAFT-B      lifecycle=DRAFT
  PV-RELEASED-1   lifecycle=RELEASED   bom_binding_required_for_release=false
  PV-RELEASED-2   lifecycle=RELEASED   bom_binding_required_for_release=true
  (none have is_current=true — that field stays advisory until MMD-PV-SETCURRENT-IMPL-01)

BOMs for P1:
  BOM-D    lifecycle=DRAFT
  BOM-R    lifecycle=RELEASED
  BOM-X    lifecycle=RETIRED
```

Personas to test:

| Persona | Action codes |
|---|---|
| ADM-FULL | `admin.master_data.product_version.manage` + `admin.master_data.bom.manage` |
| IEP-PV-ONLY | `admin.master_data.product_version.manage` only |
| OPR-NONE | no MMD action codes |

---

## 4. Capture matrix (12+ cases)

| # | Persona | Locale | PV state | BOM state | Binding | Flag | Expected readiness | Expected buttons |
|---:|---|---|---|---|---|---|---|---|
| 1 | ADM-FULL | en | PV-DRAFT-A | (no binding) | none | false | NOT_REQUIRED | Bind ENABLED, Toggle ENABLED |
| 2 | ADM-FULL | en | PV-DRAFT-A | (no binding) | none | true | BLOCKED_NO_BINDING | Bind ENABLED, Toggle ENABLED |
| 3 | ADM-FULL | en | PV-DRAFT-A | BOM-D bound | ACTIVE PRIMARY | true | BLOCKED_DRAFT_BOM | Unbind ENABLED, Toggle ENABLED |
| 4 | ADM-FULL | en | PV-DRAFT-A | BOM-X bound | ACTIVE PRIMARY (created BEFORE BOM was retired) | true | BLOCKED_RETIRED_BOM | Unbind ENABLED |
| 5 | ADM-FULL | en | PV-DRAFT-A | BOM-R bound | ACTIVE PRIMARY | true | READY | Unbind ENABLED |
| 6 | ADM-FULL | en | PV-RELEASED-2 | BOM-R bound | ACTIVE PRIMARY | true | (post-release; readiness display not relevant) | Bind/Unbind DISABLED |
| 7 | ADM-FULL | ja | PV-DRAFT-A | (no binding) | none | true | BLOCKED_NO_BINDING (Japanese label) | Same enable state |
| 8 | ADM-FULL | ja | PV-DRAFT-A | BOM-R bound | ACTIVE PRIMARY | true | READY (Japanese label) | Same enable state |
| 9 | IEP-PV-ONLY | en | PV-DRAFT-A | (no binding) | none | true | BLOCKED_NO_BINDING | Bind DISABLED (no bom.manage), Toggle ENABLED |
| 10 | IEP-PV-ONLY | en | PV-DRAFT-A | BOM-R bound | ACTIVE PRIMARY | true | READY | Unbind DISABLED, Toggle ENABLED |
| 11 | OPR-NONE | en | PV-DRAFT-A | (no binding) | none | false | NOT_REQUIRED | Bind DISABLED, Unbind DISABLED, Toggle DISABLED |
| 12 | ADM-FULL | en | PV-DRAFT-A | (no binding) | none | false → true → false (toggle round-trip) | NOT_REQUIRED → BLOCKED_NO_BINDING → NOT_REQUIRED | Toggle ENABLED both times |

Optional extra cases (encouraged but not required for DoD):

- 13: Race: open two tabs as ADM-FULL, click Bind in both; one should succeed (HTTP 201), other should show 409 with `binding already exists` error toast.
- 14: 404: navigate to `/products/<missing>/versions/<missing>` and confirm not-found state renders.
- 15: 401/403 mid-session: revoke action code while page is open, click Bind → expect 403 with localized message.

---

## 5. Per-capture artifact requirements

For each row in §4 the executor produces:

1. PNG screenshot `case-XX-{persona}-{locale}-{state}.png` in `docs/audit/mmd-fe-qa-03-screenshots/`.
2. Network capture (HAR or text excerpt) for the underlying GET binding response and any POST/DELETE mutation triggered.
3. Console log snippet (any warning/error).
4. Observed readiness value (matched against Expected).
5. Observed button enable states (matched against Expected).

The report (`mmd-fe-qa-03-runtime-visual-evidence-pack.md`) gathers all rows in a table with `Expected | Observed | PASS/FAIL | screenshot link`.

---

## 6. Verification gates the executor must run

Before capture (baseline must be green on the commit being captured):

```powershell
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q `
  tests/test_bom_binding_api.py `
  tests/test_product_version_foundation_api.py `
  tests/test_mmd_rbac_action_codes.py
cd g:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read
npm.cmd run build
npm.cmd run lint
npm.cmd run lint:i18n:registry
npm.cmd run check:routes
```

Paste raw exit codes in the report header. PASS claim without exit code is rejected per `feedback_pass_claims_need_exit_code`.

After capture: no new commands required (this slice does not modify source code).

---

## 7. Stop conditions

- If any expected-vs-observed row mismatches → halt; do NOT patch FE in this slice; raise a defect ticket and stop the visual QA at that row.
- If `lint:i18n:registry` drift occurs mid-slice (someone modified registry while capture in progress) → halt; restart capture against a stable commit.
- If any backend regression command exits non-zero → halt; slice cannot ship on a red build.
- If the executor cannot reach 12 rows (e.g., env issue) → halt at 11 or fewer; mark slice INCOMPLETE; do not freeze the master baseline based on partial QA.

---

## 8. Cleanup item (GAP-MMD-15) — confirm during capture

The current-state v2.0 notes that `MockWarningBanner` / `BackendRequiredNotice` are still imported by 4 connected pages (BomList, BomDetail, ResourceRequirements, RoutingOperationDetail). Confirm during the QA whether these banners RENDER on the corresponding routes in normal happy-path flow:

| Route | Expected | If banner visible → defect |
|---|---|---|
| `/products/.../boms` (BomList) | No banner in happy path | File `MMD-FE-CLEANUP-BANNERS-01` |
| `/products/.../boms/:bomId` (BomDetail) | No banner in happy path | Same |
| `/resource-requirements` (ResourceRequirements) | Banner acceptable until MMD-RR-FE-WRITE-01 lands (page is read-only without governance UI; banner can stay) | Note in report, do not file defect |
| `/routes/:routeId/operations/:operationId` (RoutingOperationDetail) | Same — read-only without governance UI; banner can stay | Note in report |

This is observation-only in MMD-FE-QA-03. If a defect is filed, it is its own slice.

---

## 9. Definition of Done for the executed slice (when run)

- ≥ 12 screenshots produced and indexed.
- Expected-vs-observed table fully populated.
- All verification commands exit 0; raw exit codes pasted.
- Cleanup item §8 observation recorded.
- Report saved as `docs/audit/mmd-fe-qa-03-runtime-visual-evidence-pack.md`.
- Master baseline (`mmd-master-baseline-01-freeze-handoff.md`) section §6 row for GAP-MMD-15 updated to either RESOLVED or to a follow-up slice ID.

---

## 10. Definition of Done for THIS prep pack

- ✅ Seed plan documented.
- ✅ Capture matrix ≥ 12 cases.
- ✅ Expected outcomes derived from `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §8 (UI) and §9.3 (capability matrix).
- ✅ Verification gates listed for the executor.
- ✅ Stop conditions listed.
- ✅ GAP-MMD-15 observation routed.

End of MMD-FE-QA-03 preparation pack v0.1.
