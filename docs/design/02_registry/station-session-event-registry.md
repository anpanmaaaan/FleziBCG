# Station Session Event Registry

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial candidate registry for P0-C-04B station session lifecycle events. |
| 2026-04-30 | v1.1 | P0-C-04B hardening: all four station session events promoted to CANONICAL_FOR_P0_C_STATION_SESSION. |

## Scope

This registry covers station session lifecycle events introduced in P0-C-04B.

Status for all events in this file:
- CANONICAL_FOR_P0_C_STATION_SESSION

## Canonical Events

| Event Name | Trigger Command | Logical Taxonomy | Payload Minimum | Status |
|---|---|---|---|---|
| STATION_SESSION.OPENED | open_station_session | domain_event | tenant_id, station_id, session_id, actor_user_id, opened_at | CANONICAL_FOR_P0_C_STATION_SESSION |
| STATION_SESSION.OPERATOR_IDENTIFIED | identify_operator_at_station | domain_event | tenant_id, station_id, session_id, operator_user_id, actor_user_id, occurred_at | CANONICAL_FOR_P0_C_STATION_SESSION |
| STATION_SESSION.EQUIPMENT_BOUND | bind_equipment_to_station_session | domain_event | tenant_id, station_id, session_id, equipment_id, actor_user_id, occurred_at | CANONICAL_FOR_P0_C_STATION_SESSION |
| STATION_SESSION.CLOSED | close_station_session | domain_event | tenant_id, station_id, session_id, actor_user_id, closed_at | CANONICAL_FOR_P0_C_STATION_SESSION |

## Notes

- Logical event taxonomy for all events in this registry: `domain_event`.
- Current runtime persistence uses the governed/security event infrastructure as a transitional implementation. This is intentional and does not affect canonical event name or payload semantics.
- A dedicated domain event store may replace this infrastructure in a future slice without changing event names or payloads.
- Event names, trigger commands, and payload minimums are frozen at this registry version for P0-C-04B scope.
- Subscriber contracts and projection consumers must be defined in a future P0-C slice before binding downstream services to these events.
