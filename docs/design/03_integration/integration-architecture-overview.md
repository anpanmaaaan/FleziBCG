# Integration Architecture Overview

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Expanded integration framing for ERP, shop-floor, and process/batch growth. |

Status: Integration architecture overview.

## Core principles

- backend remains source of truth
- integrations adapt into canonical domain contracts
- external systems do not directly define execution truth names inside the UI
- design must remain on-prem friendly and failure-tolerant

## Main integration families
- ERP / planning / master data
- shop-floor equipment / PLC / SCADA / edge systems
- quality/lab systems later
- historian/time-series systems later
- maintenance/asset systems later
