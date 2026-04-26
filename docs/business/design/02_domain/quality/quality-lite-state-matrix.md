# Quality Lite State Matrix

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v2.1 | Hardening Task 2 alignment. Added mapping from Quality Gate instance lifecycle to Quality Lite operation-level quality summary. |
| 2026-04-23 | v2.0 | Replaced placeholder with minimal state vocabulary. |

## Status

**Quality Lite operation-level state vocabulary.**

Quality Lite state is a summary projection for execution/operation visibility. It is not identical to the full Quality Gate instance lifecycle.

---

## 1. Canonical Quality Lite Statuses

- `QC_NOT_REQUIRED`
- `QC_PENDING`
- `QC_PASSED`
- `QC_FAILED`
- `QC_HOLD`

---

## 2. Canonical Review Statuses

- `NO_REVIEW`
- `REVIEW_REQUIRED`
- `DECISION_PENDING`
- `DISPOSITION_DONE`

---

## 3. Quality Gate Lifecycle Mapping

| Gate instance status | Quality Lite status | Rule |
|---|---|---|
| `pending` | `QC_PENDING` | Waiting for measurement/evaluation. |
| `in_progress` | `QC_PENDING` | Measurement/evaluation in progress. |
| `passed` | `QC_PASSED` | Gate passed. |
| `failed` | `QC_FAILED` | Gate failed. |
| `held` | `QC_HOLD` | Gate blocks release/progression. |
| `waived` | policy-derived | Usually `QC_PASSED` with deviation record, or `QC_HOLD` until approved. |
| `cancelled` | context-derived | Usually `QC_NOT_REQUIRED` if legitimately cancelled, otherwise remains `QC_PENDING`. |

---

## 4. Execution Guard Note

P0 Station Execution does not enforce full Acceptance Gate policy.

When P1 Quality-Gated Execution is enabled, execution `allowed_actions` must include this quality summary and may reject actions with `QUALITY_GATE_BLOCKED`.
