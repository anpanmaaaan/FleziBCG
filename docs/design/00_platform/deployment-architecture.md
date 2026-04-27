# Deployment Architecture

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Minor alignment to manufacturing environments and plant rollout realities. |

Status: Deployment posture note.

## 1. Target deployment posture

The platform must support:
- on-prem friendly deployment
- controlled-network plant deployment
- cloud-hosted deployment where allowed
- hybrid rollout by region/site
- single-tenant or multi-tenant posture depending product strategy

## 2. Manufacturing-mode implication

Deployment architecture must not assume one industry shape only.
Discrete, batch, and hybrid plants may differ in:
- network topology
- integration density
- historian dependence
- edge connectivity
- uptime/maintenance windows

The platform should remain tolerant of those differences without changing core product principles.
