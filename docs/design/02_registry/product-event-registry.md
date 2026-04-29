# Product Event Registry (P0-B)

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial registry finalization for Product Foundation events in P0-B. |

Status: Canonical registry entries for Product Foundation scope.

## Scope

This registry finalizes Product Foundation event names for P0-B only.

All entries in this file are:
- CANONICAL_FOR_P0_B

## Registry Entries

| event_name | domain | event_type | source command | payload minimum | producer | consumers/subscribers | lifecycle status | version | notes |
|---|---|---|---|---|---|---|---|---|---|
| PRODUCT.CREATED | product_definition | domain_event | create_product | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | backend product service (`app.services.product_service.create_product`) | execution read models (future), queue/cockpit/detail projections (future), supervisory dashboards (future), audit and observability pipelines | CANONICAL_FOR_P0_B | 1.0.0 | Event name is canonical for P0-B contract. Runtime persistence currently uses security-event infrastructure transport in P0-B implementation. |
| PRODUCT.UPDATED | product_definition | domain_event | update_product | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | backend product service (`app.services.product_service.update_product`) | execution read models (future), queue/cockpit/detail projections (future), supervisory dashboards (future), audit and observability pipelines | CANONICAL_FOR_P0_B | 1.0.0 | In P0-B, changed_fields must include only fields actually mutated by the command. |
| PRODUCT.RELEASED | product_definition | domain_event | release_product | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | backend product service (`app.services.product_service.release_product`) | routing foundation consumers (future), release/read-model projections (future), supervisory dashboards (future), audit and observability pipelines | CANONICAL_FOR_P0_B | 1.0.0 | Must represent transition from DRAFT to RELEASED only. |
| PRODUCT.RETIRED | product_definition | domain_event | retire_product | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | backend product service (`app.services.product_service.retire_product`) | routing linkage guard consumers (future), release/read-model projections (future), supervisory dashboards (future), audit and observability pipelines | CANONICAL_FOR_P0_B | 1.0.0 | Used to block new downstream linkage for retired products in P0-B behavior. |

## Notes

- This file is the canonical event registry source for Product Foundation in P0-B.
- Scope is intentionally limited to Product Foundation commands and lifecycle transitions.
- Any payload expansion beyond `payload minimum` requires explicit contract/version update.
