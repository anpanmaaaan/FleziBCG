# AI Architecture and Governance

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Expanded AI governance around mode-neutral platform context. |

Status: AI governance note.

## AI role in the product

AI may:
- summarize
- explain
- predict
- recommend

AI may not by default:
- mutate execution truth
- bypass auth/approval/SoD
- present uncertain output as system fact

## Design rule

AI services must consume canonical backend truth and remain compatible with both discrete and later process/batch domains.
