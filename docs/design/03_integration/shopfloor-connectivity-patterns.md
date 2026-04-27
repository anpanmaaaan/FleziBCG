# Shopfloor Connectivity Patterns

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Expanded to cover machine/resource context beyond discrete stations. |

Status: Shop-floor connectivity note.

## Patterns

- human-driven UI command flow
- sensor/machine signal ingestion
- downtime signal enrichment later
- equipment/resource availability context
- edge buffering where needed

## Design rule

Connectivity adapters must feed canonical backend truth.
They must not silently become alternative execution authorities.
