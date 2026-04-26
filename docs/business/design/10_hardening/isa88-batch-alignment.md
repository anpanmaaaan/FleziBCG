# ADR - ISA-88 Batch Alignment

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added ISA-88 batch/process alignment and deferral decision. |

## Status

**Accepted design direction.**

## Context

FleziBCG must support discrete, batch, continuous/process, and hybrid manufacturing over time. Current baseline starts from MES execution core and progressively expands into broader MOM.

ISA-88 is important for batch/process environments. ISA training material describes the standard as using models and terminology for batch control.

## Decision

Do not force full ISA-88 model into P0.

Add explicit ISA-88 alignment path for P1/P2 if the target plant or customer is batch/process-heavy.

## Current P0 Model

P0 execution uses:

```text
work_order -> work_order_operation -> station_session -> execution_events
```

This is sufficient for base execution tracking.

## Future ISA-88-Compatible Model

| ISA-88 Concept | FleziBCG Future Mapping |
|---|---|
| Process cell | plant/area/process cell alias in scope hierarchy |
| Unit | equipment/resource unit |
| Equipment module | equipment module / equipment group |
| Control module | external control-layer reference, not MOM-owned by default |
| Procedure | recipe/procedure definition |
| Unit procedure | recipe unit procedure |
| Operation | recipe/process operation |
| Phase | executable phase step |
| Control recipe | released batch execution recipe snapshot |

## P1/P2 Additions

- `mfg.recipes`
- `mfg.recipe_phases`
- `mfg.recipe_parameters`
- batch/process order context;
- weighing/dispensing;
- material charging;
- phase execution;
- process parameter records;
- batch genealogy;
- electronic batch record package where required.

## Severity Rule

If target customer is batch/pharma/food/chemical regulated plant, ISA-88 alignment moves from P2 to P1.

## Guardrail

Do not model process/batch using only discrete station/operation assumptions once batch-specific execution begins.

## References

- ISA Batch Control training overview: https://www.isa.org/training/course-description/ic40
