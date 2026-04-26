# Hardening Review Response

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Captured response posture to external/senior review comments. |

## Status

**Review response artifact.**

## 1. Accepted Direction

The review is valid and should be used as production-hardening input. It does not invalidate the baseline. It strengthens the baseline.

## 2. Accepted Immediate Fixes

Handled in Task 2:

- Rework mismatch;
- ABORTED reserved/future;
- Quality gate deferred guard;
- Pre-Acceptance as gate type;
- Quality Lite vs Gate lifecycle mapping;
- Backflush record/event relationship;
- Backflush trigger timing;
- CloudBeaver dev-only;
- Cross-review report governance.

## 3. Accepted ADRs

Handled in Task 3:

- CloudEvents boundary compatibility;
- RFC 9457-compatible error format;
- tenant isolation/RLS strategy;
- performance/capacity/SLO;
- partition/archive/snapshot strategy;
- shopfloor connectivity;
- observability;
- policy-engine path;
- OEE formula;
- EPCIS compatibility;
- ISA-88 batch/process path;
- modular monolith extraction-aware wording;
- cache strategy;
- AI guardrails.

## 4. Explicit Rejections / Adjustments

| Review suggestion | Response |
|---|---|
| Rename all line/station to work_center/work_unit now | Do not rename core now. Add ISA-95 semantic mapping/alias later to avoid cascade. |
| Make Pre-Acceptance a separate aggregate | Do not create separate aggregate. It is a `gate_type` under Quality Gate. |
| Replace internal event schema with CloudEvents | Do not replace internal DB schema. Use CloudEvents-compatible external boundary. |
| Build Redis/Kafka/OPA/OPC UA immediately | Do not build immediately. Document hardening path and trigger conditions. |
| Turn FleziBCG into full QMS/WMS/CMMS/eBR suite | Do not expand baseline scope. Keep integration/adjacent capability boundaries. |

## 5. Final Position

Baseline remains authoritative. Hardening docs are now companion decision records and should be merged into the next consolidated package.
