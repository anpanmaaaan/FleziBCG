# Planning and Scheduling Domain

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.0 | Added first-class planning and scheduling domain note. |

Status: Canonical domain overview.

## 1. Purpose

This domain explains how FleziBCG treats planning and scheduling as a first-class module without letting it overwrite execution truth.

## 2. Scope

This domain includes:
- sequencing support
- dispatch recommendation
- finite-capacity-aware planning support
- disruption-aware replanning hints
- planning/execution alignment support

## 3. Core rule

Planning proposes.
Execution confirms reality.

APS outputs may influence priorities, recommendations, and what-if analysis, but they must not silently rewrite operational truth.

## 4. AI note

AI may improve APS through:
- better delay prediction
- better bottleneck prediction
- better resequencing recommendations
- better responsiveness to live disruption

AI-enhanced APS still remains advisory-first unless explicitly governed otherwise.
