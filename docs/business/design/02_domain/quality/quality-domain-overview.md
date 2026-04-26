# Quality Domain Overview

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v2.2 | Hardening Task 2 alignment. Clarified Pre-Acceptance Check as a Quality Gate type, not a separate aggregate; clarified Quality Lite vs Quality Gate lifecycle; clarified P0/P1 execution-gating boundary. |
| 2026-04-23 | v2.0 | Added alignment notes for session-owned execution and manufacturing-mode-neutral platform. |

## Status

**Canonical entry document for the quality domain.**

---

## 1. Purpose

This document explains:

- what Quality owns;
- what Quality Lite covers now;
- how quality interacts with execution;
- how Acceptance Gate extends Quality Lite;
- how quality remains compatible with discrete, batch, and process-oriented plants.

---

## 2. Domain Purpose

The Quality domain owns:

- QC applicability;
- measurement/inspection input;
- backend evaluation of pass/fail/hold;
- Acceptance Gate and Pre-Acceptance gate types;
- disposition flow;
- deviation/nonconformance foundation;
- accepted-good implications;
- quality-to-execution gate state.

Quality does not own execution runtime state. It gates or informs execution through orthogonal quality state and backend-derived `allowed_actions`.

---

## 3. Acceptance Gate Model

Canonical aggregate family:

```text
quality_gate_definition
quality_gate_instance
quality_gate_result
```

Canonical gate types:

```text
pre_acceptance
acceptance
release
in_process
final_inspection
```

Important clarification:

> **Pre-Acceptance Check is a canonical gate type under the Quality Gate aggregate. It is not a separate aggregate.**

`LAT` / `Pre-LAT` are tenant/plant display labels only. They must not become core table, API, or event names.

---

## 4. Interaction with Execution

Quality is execution-adjacent and policy-driven.

P0 boundary:

```text
Quality Lite can record inspection/measurement/evaluation and expose pass/fail/hold summary.
Full Acceptance Gate enforcement is design-now-build-later.
```

P1 boundary:

```text
Acceptance Gate may block complete, close, move-next, output release, WIP movement, or ERP output posting depending on policy.
```

Execution must not locally compute quality results. Execution reads backend-derived quality/gate state.

---

## 5. Quality Lite vs Quality Gate Lifecycle

Quality Lite operation-level summary and Quality Gate instance lifecycle are different models.

| Quality Gate instance status | Quality Lite operation summary | Notes |
|---|---|---|
| `pending` | `QC_PENDING` | Gate created but not evaluated. |
| `in_progress` | `QC_PENDING` | Measurement/review in progress. |
| `passed` | `QC_PASSED` | Gate passed. |
| `failed` | `QC_FAILED` | Gate failed. |
| `held` | `QC_HOLD` | Gate has hold impact. |
| `waived` | `QC_PASSED` or `QC_HOLD` by policy | Requires deviation/approval policy. |
| `cancelled` | `QC_NOT_REQUIRED` or `QC_PENDING` by context | Cancellation reason must be auditable. |

---

## 6. Platform-Neutral Rule

Quality must remain compatible with:

- operation-level discrete checks;
- batch/lot-oriented process checks;
- held/pending quantity derivation;
- final release/acceptance checks;
- future e-record/e-sign support.
