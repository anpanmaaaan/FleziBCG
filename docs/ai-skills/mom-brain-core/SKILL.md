---
name: mom-brain-core
description: FleziBCG MOM-specific engineering rules.
---

# MOM Brain Core

Rules:

- backend is execution truth
- frontend sends intent only
- frontend does not derive execution state
- frontend does not decide authorization
- events are append-only operational facts
- projections are read models
- status derived from events
- tenant/scope isolation mandatory
- JWT proves identity only
- AI advisory only

Canonical decisions:

- Acceptance Gate is canonical
- LAT/Pre-LAT are display labels only
- Backflush is cross-domain
- ERP receives summary/reference context, not full event log by default
- Digital Twin is derived state
- Reporting/OEE is deterministic
- Station Execution target is session-owned
- Claim is migration debt
