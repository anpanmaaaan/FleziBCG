# ADR - AI Guardrails and Operational Safety

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added AI guardrails and operational safety decision. |

## Status

**Accepted design direction.**

## Context

FleziBCG is AI-driven, but AI is advisory by default. AI will eventually summarize, explain, predict, and recommend across operations. It must not silently mutate execution, quality, material, maintenance, or integration truth.

## Decision

AI remains a separate advisory/intelligence layer.

No AI output can directly execute a production command without explicit human/backend-governed command path.

## AI Capability Layers

| Layer | Meaning | Mutation Allowed? |
|---|---|---:|
| Observe | Read operational facts | No |
| Explain | Explain events/KPI/delays | No |
| Predict | Predict risk/anomaly | No |
| Recommend | Recommend action | No direct mutation |
| Assist command drafting | Draft command intent for human review | Only after normal backend authorization/approval |

## Required AI Metadata

AI outputs should store:

- `ai_run_id`;
- model/provider name;
- model version where available;
- prompt/template version;
- input scope;
- evidence references;
- confidence score where meaningful;
- output schema version;
- human feedback;
- generated timestamp.

## Guardrails

1. AI cannot bypass role/scope/action authorization.
2. AI cannot bypass approval or SoD.
3. AI cannot silently write execution events.
4. AI cannot mark quality pass/fail.
5. AI cannot post to ERP.
6. AI recommendations must show evidence or source context.
7. AI output must be distinguishable from deterministic reporting.
8. Natural-language query should not reveal out-of-scope data.
9. Prompt injection risk must be addressed before external document/web ingestion.
10. Fallback behavior must be deterministic when AI fails.

## Early Use Cases

- shift summary;
- OEE deep dive explanation;
- downtime/bottleneck explanation;
- delay risk hints;
- anomaly feed;
- quality trend explanation;
- integration/reconciliation summary.

## Anti-Pattern

Do not create an AI button that executes production actions directly from a generated recommendation.
