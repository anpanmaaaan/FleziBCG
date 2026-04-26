# FleziBCG Function List — Hardening Amendment

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Hardening Task 2 amendment for production reporting/rework wording. |

## Status

**Amendment to Function List v2.1.**

This file patches wording only. It does not add new functions.

---

## 1. Replace EXE-08 Wording

Replace the current `EXE-08 Production Reporting` description if it says:

```text
Report good/scrap/rework quantities.
```

with:

```text
P0: report good and scrap quantities only. Rework quantity/context is P1/P2 via Quality disposition and Rework flow.
```

## 2. Reason

P0 Station Execution contract accepts:

```text
good_delta
scrap_delta
```

It does not accept `rework_delta` because rework requires additional lifecycle semantics:

- quality disposition;
- rework instruction;
- rework operation or routing;
- genealogy implication;
- possible approval;
- reporting/reposting rules.

## 3. Related Future Functions

Rework remains valid in the product function landscape, but not inside P0 `report_production`.

| Function area | Future handling |
|---|---|
| Quality Operations | Rework disposition. |
| Execution Management | Rework execution flow. |
| Traceability | Rework genealogy. |
| Inventory/WIP | Scrap/loss/rework material context. |
| Integration | ERP scrap/rework/yield-loss posting where needed. |
