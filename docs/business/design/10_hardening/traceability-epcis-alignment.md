# ADR - Traceability and EPCIS Alignment

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added EPCIS compatibility decision for traceability. |

## Status

**Accepted design direction.**

## Context

FleziBCG traceability uses internal operational genealogy:

- material lots;
- operation material consumptions;
- operation outputs;
- genealogy edges;
- quality/disposition context.

Some industries/customers may need GS1 EPCIS compatibility for supply-chain visibility event exchange. GS1 describes EPCIS as a traceability event messaging standard for sharing event data using a common language.

## Decision

FleziBCG will not store all traceability data as EPCIS events from day one.

FleziBCG will maintain an internal genealogy model first and design an EPCIS-compatible export/import mapping layer later.

## Internal Model First

| FleziBCG concept | Purpose |
|---|---|
| `trc.material_lots` | Lot/batch/serial identity. |
| `trc.operation_material_consumptions` | Input material consumed by operation. |
| `trc.operation_outputs` | Output produced by operation. |
| `trc.genealogy_edges` | Input-output lineage. |
| `qual.quality_gate_results` | Acceptance/reject/hold context. |

## EPCIS Compatibility Mapping

| EPCIS Event Type | Potential FleziBCG Mapping |
|---|---|
| ObjectEvent | Lot/serial observed, created, moved, status changed. |
| AggregationEvent | Pack/carton/pallet aggregation. |
| TransformationEvent | Input material transformed into output lot/batch/product. |
| TransactionEvent | Link object/lot with business transaction/order/shipment. |
| AssociationEvent | Associate objects without transformation where relevant. |

## P0/P1/P2 Posture

| Phase | Posture |
|---|---|
| P0 | No EPCIS. Basic operation/material/quality trace context only if needed. |
| P1 | Internal genealogy model and traceability search. |
| P2 | EPCIS export/import mapping where customer/regulatory demand exists. |

## Guardrails

- Do not force EPCIS vocabulary into all internal tables.
- Preserve enough internal context to generate EPCIS later.
- Keep EPCIS as interoperability layer, not replacement for MOM genealogy.

## References

- GS1 EPCIS and CBV: https://www.gs1.org/standards/epcis
