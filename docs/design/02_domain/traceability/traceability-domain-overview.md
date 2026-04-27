# Traceability Domain Overview

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Reworked traceability overview to support both discrete and process/batch use cases. |

Status: Traceability domain overview.

## Purpose

Traceability owns:
- serial, lot, and batch identity
- genealogy edges
- backward/forward trace views
- material-consumption/production linkage

## Design rule

Traceability must not be reduced to serial-only discrete assumptions.
The platform must remain ready for lot/batch/genealogy-heavy flows.

For the explicit boundary against inventory/WIP, see `../../00_platform/material-traceability-vs-inventory-boundary.md`.
