# Product Scope and Phase Boundary

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified platform-vs-app scope and manufacturing-mode boundaries. |

Status: Canonical phase-boundary note.

## 1. Purpose

This document separates:
- what the platform must support now
- what must be designed now but may be implemented later
- what is explicitly out of current delivery scope

## 2. Scope layers

### 2.1 Platform scope now
Must be designed now:
- identity, access, session, audit, SoD
- hierarchical scope model
- unified execution abstractions
- operator and equipment context separation
- event-driven truth
- manufacturing-mode neutrality

### 2.2 Current application scope now
Must be designed and progressively implemented now:
- Station Execution as the discrete-first app
- current supervisory surfaces
- Quality Lite and accepted-good direction
- initial traceability direction

### 2.3 Designed now, implemented later
- batch/process execution app
- broader material operations
- maintenance operations
- advanced genealogy and lot split/merge flows
- digital twin depth
- APS beyond advisory support

### 2.4 Explicitly out of current immediate scope
- full ISA-88 recipe engine
- full historian-native continuous-process runtime
- full enterprise maintenance suite
- full CAPA/laboratory enterprise quality suite

## 3. Key phase boundary rules

- Station Execution is not allowed to become the universal language of the whole platform.
- Claim may exist temporarily for compatibility but is deprecated from the target execution model.
- Session-owned execution is the approved next-step target.
- Quality, traceability, material, and process/batch evolution must remain compatible with the platform abstractions chosen now.
