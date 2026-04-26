# ADR - OEE Formula and KPI Definition

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added deterministic OEE formula and KPI data source rules. |

## Status

**Accepted design direction.**

## Context

Reporting/KPI/OEE must be deterministic. AI may explain OEE but must not calculate alternative hidden truth.

## Decision

Use the standard OEE structure:

```text
OEE = Availability x Performance x Quality
```

## Canonical Formula

```text
Planned Production Time = scheduled production time - planned breaks/exclusions
Run Time = Planned Production Time - unplanned downtime
Availability = Run Time / Planned Production Time
Performance = (Ideal Cycle Time x Total Count) / Run Time
Quality = Good Count / Total Count
OEE = Availability x Performance x Quality
```

## Data Sources

| Metric | Source |
|---|---|
| Planned Production Time | shift/production calendar + schedule/line availability policy |
| Planned breaks | shift calendar / production calendar |
| Unplanned downtime | `exe.downtime_events` with reason/type policy |
| Run Time | derived from calendar and downtime |
| Ideal Cycle Time | `mfg.routing_operations.standard_cycle_time_sec` or product/operation standard |
| Total Count | good + scrap + rework where included by policy |
| Good Count | accepted/good quantity from execution and/or quality gate result |
| Quality losses | scrap/reject/rework depending policy |

## Policy Decisions Required

| Decision | Default |
|---|---|
| Does rework count as total count? | Yes if produced/reported; quality treatment depends disposition. |
| Does planned downtime reduce planned production time? | Yes if configured as planned exclusion. |
| Does quality hold count as good? | No until accepted/released. |
| Which time zone applies? | Plant timezone for shift reporting. |
| How to handle cross-shift operation? | Split event durations by shift boundaries. |

## Reporting vs AI

RPT owns deterministic OEE. AI may generate explanations like bottleneck or anomaly insight but cannot overwrite deterministic KPI.

## References

- OPC Foundation MachineTool OEE model: https://reference.opcfoundation.org/MachineTool/v102/docs/C.1.4
