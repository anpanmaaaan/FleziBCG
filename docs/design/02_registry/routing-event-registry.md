# Routing Event Registry (P0-B)

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial registry entries for Routing Foundation candidate events in P0-B-02 implementation. |
| 2026-04-29 | v1.1 | Events canonicalized following successful P0-B-02 hardening: migration verified, DB schema verified, full suite 134 passed. |

Status: CANONICAL. Events finalized for P0-B-02 Routing Foundation scope. DB migration and schema verified 2026-04-29.

## Scope

This registry tracks Routing Foundation event names implemented in P0-B-02.

All entries in this file are:
- CANONICAL_FOR_P0_B_ROUTING

Logical event taxonomy = domain_event.
Current runtime persistence may use governed/security event infrastructure as transitional implementation until a dedicated domain event store is introduced.

## Registry Entries

| event_name | domain | event_type | source command | payload minimum | producer | consumers/subscribers | lifecycle status | version | notes |
|---|---|---|---|---|---|---|---|---|---|
| ROUTING.CREATED | product_definition | domain_event (transitional persistence via security-event infrastructure) | create_routing | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | backend routing service (`app.services.routing_service.create_routing`) | routing read models (future), planning linkage consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_ROUTING | 1.0.0 | Event name finalized in P0-B-02 hardening. |
| ROUTING.UPDATED | product_definition | domain_event (transitional persistence via security-event infrastructure) | update_routing | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | backend routing service (`app.services.routing_service.update_routing`) | routing read models (future), planning linkage consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_ROUTING | 1.0.0 | Includes allowed RELEASED non-structural updates only in P0-B. |
| ROUTING.OPERATION_ADDED | product_definition | domain_event (transitional persistence via security-event infrastructure) | add_routing_operation | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | backend routing service (`app.services.routing_service.add_routing_operation`) | routing sequence consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_ROUTING | 1.0.0 | DRAFT-only operation mutation in P0-B. |
| ROUTING.OPERATION_UPDATED | product_definition | domain_event (transitional persistence via security-event infrastructure) | update_routing_operation | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | backend routing service (`app.services.routing_service.update_routing_operation`) | routing sequence consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_ROUTING | 1.0.0 | DRAFT-only operation mutation in P0-B. |
| ROUTING.OPERATION_REMOVED | product_definition | domain_event (transitional persistence via security-event infrastructure) | remove_routing_operation | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | backend routing service (`app.services.routing_service.remove_routing_operation`) | routing sequence consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_ROUTING | 1.0.0 | DRAFT-only operation mutation in P0-B. |
| ROUTING.RELEASED | product_definition | domain_event (transitional persistence via security-event infrastructure) | release_routing | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | backend routing service (`app.services.routing_service.release_routing`) | downstream routing-link eligibility consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_ROUTING | 1.0.0 | Represents DRAFT -> RELEASED transition only. |
| ROUTING.RETIRED | product_definition | domain_event (transitional persistence via security-event infrastructure) | retire_routing | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | backend routing service (`app.services.routing_service.retire_routing`) | downstream new-link guard consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_ROUTING | 1.0.0 | Used for RETIRED downstream-link blocking policy in P0-B. |

## Notes

- This file is intentionally phase-bounded to P0-B routing foundation only.
- Event names are CANONICAL as of P0-B-02 hardening completion (2026-04-29).
- Logical event taxonomy = domain_event. Current runtime persistence may use governed/security event infrastructure as transitional implementation until a dedicated domain event store is introduced.
- Current implementation persists through governed security-event infrastructure while preserving domain-event naming in payload and report artifacts.
