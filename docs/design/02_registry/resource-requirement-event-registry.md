# Resource Requirement Event Registry (P0-B)

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial candidate registry entries for P0-B-03 Resource Requirement Mapping implementation. |
| 2026-04-29 | v1.1 | Resource Requirement Mapping events canonicalized after P0-B-03 verification hardening. |

Status: CANONICAL. Resource Requirement Mapping event names are finalized for P0-B-03 scope.

## Scope

This registry tracks Resource Requirement Mapping event names implemented in P0-B-03.

All entries in this file are:
- CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT

Logical event taxonomy = domain_event.
Current runtime persistence may use governed/security event infrastructure as transitional implementation until a dedicated domain event store is introduced.

## Registry Entries

| event_name | domain | event_type | source command | payload minimum | producer | consumers/subscribers | lifecycle status | version | notes |
|---|---|---|---|---|---|---|---|---|---|
| RESOURCE_REQUIREMENT.CREATED | product_definition | domain_event (transitional persistence via security-event infrastructure) | create_resource_requirement | tenant_id, actor_user_id, requirement_id, routing_id, operation_id, required_resource_type, required_capability_code, changed_fields, occurred_at | backend resource requirement service (`app.services.resource_requirement_service.create_resource_requirement`) | resource requirement read models (future), planning linkage consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | 1.0.0 | Canonicalized for verified P0-B-03 scope. |
| RESOURCE_REQUIREMENT.UPDATED | product_definition | domain_event (transitional persistence via security-event infrastructure) | update_resource_requirement | tenant_id, actor_user_id, requirement_id, routing_id, operation_id, required_resource_type, required_capability_code, changed_fields, occurred_at | backend resource requirement service (`app.services.resource_requirement_service.update_resource_requirement`) | resource requirement read models (future), planning linkage consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | 1.0.0 | DRAFT-only requirement mutation in P0-B. |
| RESOURCE_REQUIREMENT.REMOVED | product_definition | domain_event (transitional persistence via security-event infrastructure) | remove_resource_requirement | tenant_id, actor_user_id, requirement_id, routing_id, operation_id, required_resource_type, required_capability_code, changed_fields, occurred_at | backend resource requirement service (`app.services.resource_requirement_service.delete_resource_requirement`) | resource requirement read models (future), planning linkage consumers (future), dashboards (future), audit pipelines | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | 1.0.0 | Hard-delete event for DRAFT-only mutation window in P0-B. |

## Notes

- This file is intentionally phase-bounded to P0-B resource requirement mapping only.
- Event names are canonical for P0-B-03 scope.
- Current implementation persists through governed security-event infrastructure while preserving domain-event naming in payload and report artifacts.
