# Execution Domain Overview

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Reworked execution overview for session-owned target design and manufacturing-mode neutrality. |

Status: Canonical entry document for the execution domain.

## 1. Purpose

This document explains:
- what execution owns
- what the current strongest app baseline is
- what the approved next-step target design is
- which detailed documents are authoritative

## 2. Domain purpose

The execution domain owns deterministic production execution truth for:
- production request / execution run / execution step
- runtime lifecycle mutation
- quantity mutation
- downtime/loss capture
- closure/reopen foundation
- execution session ownership context

## 3. Current strongest app baseline

The strongest implemented baseline remains **Station Execution Core / Pre-QC / Pre-Review**, historically centered on operation execution at station context.
Current code still carries claim-centric behavior in places.

## 4. Approved next-step target design

The approved direction is:
- deprecate claim from the target model
- move ownership to active station/resource session context
- separate authenticated user, identified operator, and equipment/resource context
- keep Station Execution as the discrete-first application, not the universal execution grammar

## 5. Domain principles

- backend is source of execution truth
- important facts are append-only events
- status is derived
- queue, cockpit, and detail must agree on the same backend truth
- close is not the same as complete
- reopen must preserve resumability safely
- platform abstractions must remain compatible with discrete, batch, continuous, and hybrid plants

## 6. Authoritative detailed docs

- `business-truth-station-execution-v4.md`
- `domain-contracts-execution.md`
- `execution-state-machine.md`
- `station-execution-state-matrix-v4.md`
- `station-execution-authorization-matrix-v4.md`
- `station-execution-command-event-contracts-v4.md`
- `station-execution-policy-and-master-data-v4.md`
- `station-execution-operational-sop-v4.md`
