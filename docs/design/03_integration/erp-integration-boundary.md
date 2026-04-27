# ERP Integration Boundary

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified production-request boundary and non-coupling to one manufacturing mode. |

Status: ERP boundary note.

## Purpose

ERP integration should provide:
- production requests/orders
- master data
- planning/scheduling inputs
- confirmations/feedback outputs

## Boundary rule

The platform should not hard-wire ERP semantics directly into Station Execution-only shapes.
ERP-sourced work must be normalized into platform execution abstractions so both discrete and process-mode apps can reuse them.
