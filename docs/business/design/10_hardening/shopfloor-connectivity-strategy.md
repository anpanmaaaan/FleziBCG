# ADR - Shopfloor Connectivity Strategy

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added shopfloor connectivity stance for OPC UA, MQTT/Sparkplug B, edge buffering, ordering, and time sync. |

## Status

**Accepted design direction.**

## Context

FleziBCG starts with human/operator execution flows and MOM-level operational truth. Future production environments may need connection to machines, SCADA, historian, gateways, and sensors.

OPC UA is widely positioned for industrial interoperability across machine-to-machine and machine-to-enterprise communication. Sparkplug provides an MQTT-based framework for integrating devices, applications, sensors, and gateways within MQTT infrastructure.

## Decision

FleziBCG will not build raw control-layer ownership in P0.

FleziBCG will support a future **shopfloor connectivity adapter layer** for:

- OPC UA read/subscription paths;
- MQTT/Sparkplug B edge gateway paths;
- SCADA/Historian reference links;
- device event import into MOM context;
- edge buffering and store-and-forward.

## Boundary

| Layer | Owner |
|---|---|
| PLC/control logic | PLC/SCADA/control system |
| High-frequency telemetry | Historian/time-series system |
| MOM operational context | FleziBCG |
| Device-to-MOM adapter | Integration/edge layer |
| Operator command truth | FleziBCG backend |

## Connectivity Patterns

### Pattern 1 - Human UI Command

Operator acts through FleziBCG UI/API. Backend authorizes and records execution event.

### Pattern 2 - Historian Context Link

FleziBCG stores references/time windows to historian data instead of copying high-frequency raw telemetry.

### Pattern 3 - OPC UA Adapter

Adapter reads/subscribes to selected equipment parameters and normalizes to operational context events.

### Pattern 4 - MQTT/Sparkplug B Edge Gateway

Gateway publishes device state/metrics. FleziBCG subscribes through integration adapter and maps events to station/equipment/operation context.

## Hardening Rules

1. Device events require idempotency keys.
2. Adapter must preserve source timestamp and received timestamp.
3. Ordering must be defined per source device/equipment stream.
4. Edge gateway should support store-and-forward.
5. Time sync should use NTP minimum; PTP where high precision is required.
6. Machine-derived input must not bypass authorization for business actions.
7. Equipment signal does not automatically complete operation unless a governed automation rule exists.

## P0/P1/P2 Posture

| Phase | Posture |
|---|---|
| P0 | Human UI/API execution only; no direct machine control. |
| P1 | SCADA/Historian context link and selected device/context import. |
| P2 | OPC UA/MQTT/Sparkplug B adapter framework. |
| P3 | Advanced edge intelligence and closed-loop advisory workflows. |

## References

- OPC UA overview: https://opcfoundation.org/about/opc-technologies/opc-ua/
- Eclipse Sparkplug specification: https://sparkplug.eclipse.org/specification/
