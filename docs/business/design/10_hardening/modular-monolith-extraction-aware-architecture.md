# ADR - Modular Monolith, Extraction-Aware Architecture

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Clarified modular monolith wording from extraction-ready to extraction-aware. |

## Status

**Accepted design direction.**

## Context

FleziBCG starts as a modular monolith with PostgreSQL. Prior docs use microservice-ready or extraction-ready wording. However, a single database with cross-domain foreign keys is not fully extraction-ready. It is better described as extraction-aware.

## Decision

Use the phrase:

```text
modular monolith, extraction-aware boundaries
```

not:

```text
fully extraction-ready microservice architecture
```

## Rules

1. Bounded-context schemas remain useful inside one database.
2. Cross-domain foreign keys are allowed in P0/P1 for integrity, but must be documented as extraction debt.
3. Future extraction candidates should use stable IDs and domain APIs/events rather than direct table ownership.
4. Projections/read models may duplicate data across boundaries.
5. Integration and reporting should not become hidden shared-domain dumping grounds.

## Cross-Domain Reference Policy

| Reference Type | Preferred Pattern |
|---|---|
| Same bounded context | FK allowed. |
| Foundation/shared reference | FK allowed with caution. |
| Cross-domain high-integrity P0 relation | FK allowed, mark extraction debt. |
| Future extraction candidate | Stable ID + domain read model/event preferred. |
| External system | `core.external_id_map`, never external ID as PK. |

## Extraction Candidates Later

- Integration service;
- Reporting service;
- AI/Insight service;
- Digital Twin service;
- Notification service;
- APS service.

Execution and Quality should not be extracted until core operational truth is stable.
