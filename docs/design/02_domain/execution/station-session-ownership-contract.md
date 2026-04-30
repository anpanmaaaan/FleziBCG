# Station Session Ownership Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | P0-C-04A contract finalization. DOC-ONLY, PROPOSE-ONLY. No implementation changes. |

## Routing
- Selected brain: MOM Brain
- Selected mode: Architecture
- Hard Mode MOM: v3
- Reason: Contract finalization for execution ownership touching station/session/operator, state/event/invariant, and migration safety boundaries.

## 1. Purpose

Define StationSession as the target ownership context for Station Execution.

This contract clarifies:
- StationSession is the target execution ownership model.
- OperationClaim remains compatibility debt during migration.
- This contract does not remove claim.
- This contract does not implement execution command behavior changes.

Out of scope for P0-C-04A:
- No StationSession model implementation.
- No migration.
- No claim code modifications.
- No execution command guard behavior changes.
- No API implementation.

## 2. Aggregate Definition

### 2.1 Aggregate Name

StationSession

### 2.2 Minimum Fields

- session_id
- tenant_id
- station_id
- operator_user_id
- opened_at
- closed_at
- status
- equipment_id (optional)
- current_operation_id (optional)
- created_at
- updated_at

### 2.3 Status Values

- OPEN
- CLOSED
- EXPIRED: deferred unless/until lifecycle policy explicitly introduces expiration semantics

Current contract decision:
- OPEN and CLOSED are required.
- EXPIRED is deferred for later slice unless policy/ops need requires explicit TTL-based close semantics.

### 2.4 Ownership Semantics

- A StationSession belongs to exactly one tenant and one station.
- A StationSession may have exactly one identified operator context at a time.
- Equipment context is optional and policy-driven.
- current_operation_id is optional and informational unless later slices make it invariant-bearing.

## 3. Lifecycle

### 3.1 Commands

- open_station_session
- identify_operator_at_station
- bind_equipment_to_station_session (optional by policy)
- close_station_session

### 3.2 Lifecycle Rules

- Session opens from no-active-session context.
- Session close transitions ownership context to inactive.
- Closed session cannot accept new execution commands.
- Session belongs to one tenant and one station for its entire lifecycle.
- Operator identity must be explicit, not inferred from frontend assumptions.

### 3.3 State Rules

- No active closed session.
- CLOSED is terminal for command-bearing ownership context.
- Re-open semantics are not part of P0-C-04A and must be explicitly defined before implementation if required.

## 4. Events

Candidate lifecycle events:

- STATION_SESSION.OPENED
- STATION_SESSION.OPERATOR_IDENTIFIED
- STATION_SESSION.EQUIPMENT_BOUND
- STATION_SESSION.CLOSED

Event status for P0-C-04A (provenance — historical at time of writing):
- CANDIDATE_FOR_P0_C_STATION_SESSION
- NEEDS_EVENT_REGISTRY_FINALIZATION

Finalization note (P0-C-04B hardening, 2026-04-30):
- All four events above have been promoted to CANONICAL_FOR_P0_C_STATION_SESSION.
- See: docs/design/02_registry/station-session-event-registry.md v1.1

## 5. Ownership Invariants

Mandatory invariants:

1. tenant isolation is mandatory.
2. station scope isolation is mandatory.
3. one active station session per station (selected invariant for target ownership).
4. one active operator context per station session.
5. execution command context must eventually validate station session.
6. frontend cannot provide ownership truth.
7. claim cannot be expanded.
8. claim and session must not create contradictory ownership truth.
9. no command rejection behavior change until explicitly implemented in later slice.

Interpretation constraints:
- Ownership truth is backend-derived.
- Projection/read views cannot become ownership source of truth.
- Session ownership semantics are orthogonal to runtime execution status names.

## 6. Claim Compatibility Boundary

Claim in current source is defined as:
- compatibility layer
- migration debt
- not target ownership truth
- required to remain backward-compatible until replacement plan is implemented

Boundary rules:
- Do not remove claim in P0-C-04A.
- Do not break claim tests.
- Do not use claim to define new target behavior.
- Do not create dual authoritative ownership.

Authority rule during migration:
- Claim may continue to operate for backward compatibility.
- Session is target ownership direction.
- Any overlap must preserve single effective ownership truth per command path.

## 7. Migration Strategy

### 7.1 Options

A. Big-bang claim removal
- Fastest path to target shape.
- Highest regression and compatibility risk.

B. Compatibility bridge
- Keep claim behavior stable.
- Introduce StationSession in controlled slices.
- Move command context alignment incrementally.

C. Claim-only hardening
- Lowest immediate risk.
- Defers ownership migration and prolongs debt.

### 7.2 Recommended Decision

Option B - Compatibility Bridge

### 7.3 Slice Plan

- P0-C-04A Contract finalization (this document)
- P0-C-04B StationSession model + lifecycle only
- P0-C-04C Diagnostic session context bridge
- P0-C-04D Command context guard alignment
- P0-C-04E Claim compatibility/deprecation lock

## 8. API Surface Proposal (Propose Only)

Proposed endpoints:
- POST /station-sessions
- GET /station-sessions/current
- POST /station-sessions/{session_id}/identify-operator
- POST /station-sessions/{session_id}/bind-equipment
- POST /station-sessions/{session_id}/close

Namespace decision:
- Candidate A: /station/sessions
- Candidate B: /station-sessions

Recommendation:
- Use /station/sessions

Justification:
- Existing station capabilities already live under /station/* and reflect station-scoped workflows.
- Session ownership here is a station-execution bounded concern, not a global standalone session domain.
- /station/sessions preserves route discoverability for station UI/API consumers while avoiding fragmented root surface.

## 9. Test Matrix for Future Implementation

Future required tests:

1. open session happy path
2. single active session per station
3. tenant mismatch rejected
4. station mismatch rejected
5. identify operator
6. close session
7. closed session cannot be used
8. claim tests remain green
9. no command behavior change in P0-C-04B
10. future diagnostic bridge does not reject commands yet
11. event emission for session lifecycle

Suggested assertion layers:
- service-level invariants
- route-level tenant/scope/auth errors
- event payload minimal fields
- regression parity against claim compatibility tests

## 10. Stop Conditions

Stop future implementation if any occurs:

1. claim tests fail
2. session creates dual ownership ambiguity
3. command behavior changes without explicit approval
4. station/session event contract is unclear
5. migration requires data transformation not specified
6. frontend becomes ownership truth

## 11. Final Verdict

READY_FOR_P0_C_04B_MODEL_IMPLEMENTATION

## 12. Non-Negotiable Boundaries for P0-C-04A

- DOC-ONLY slice.
- No runtime behavior changes.
- No schema/model implementation.
- No migration implementation.
- No API route implementation.
- No claim behavior change.
- No execution guard behavior change.
