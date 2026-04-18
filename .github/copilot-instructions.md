## MOM Lite — Coding Entry Instructions
Before coding, always read these documents in order:
1. `docs/system/mes-business-logic-v1.md`
2. `docs/governance/CODING_RULES.md`
3. `docs/governance/ENGINEERING_DECISIONS.md`
4. `docs/governance/SOURCE_STRUCTURE.md`
## Purpose of this file
This file is a short entry instruction only.
It is **not** the authoritative source for:
- business logic
- coding conventions
- API contract rules
- database rules
- IAM/session rules
- AI engineering rules
Those rules live in the governance and system documents above.
---
## Project Overview
MOM Lite is a lightweight ISA-95-aligned MES/MOM system.
### Current runtime architecture
- modular monolith
- backend: Python 3.12, FastAPI, SQLAlchemy 2.x, PostgreSQL
- frontend: React 18, TypeScript, Vite, Tailwind CSS
- authentication: JWT + Argon2
- deployment target: local / Docker / on-prem friendly
### Product direction
The long-term direction is AI-driven MES/MOM, but:
- execution truth remains deterministic
- backend remains source of truth
- AI is advisory by default
---
## Hard Constraints
### 1. Backend is source of truth
- frontend never derives execution state
- frontend never decides authorization
- persona is UX-only
### 2. Execution is event-driven
- execution events are append-only
- status is derived from events
- projections are not the source of truth
### 3. Tenant and scope isolation are mandatory
- no tenant-blind access to tenant-owned data
- validated tenant/scope context must be explicit
### 4. Service layer owns business logic
- routes stay thin
- repositories are data access only
### 5. JWT proves identity, not authorization
- permissions are checked server-side per request
- frontend must not encode permission truth
### 6. Admin/support are not default production actors
- privileged operational access must go through approved support / impersonation flow
- all such actions must be auditable
### 7. AI may explain, predict, and recommend
AI must not:
- silently mutate execution
- bypass auth, approval, or SoD
- present uncertain output as system fact
---
## PR Reminder
Before opening a PR, determine which type it is:
- Mechanical PR
- Intentional Behavior PR
- Architecture / Contract PR
Follow the rules in `docs/governance/CODING_RULES.md`.
---
## Final Reminder
When documents disagree:
1. business logic contract wins
2. coding rules win next
3. engineering decisions clarify implementation intent
4. source structure explains ownership only
Do not invent a third interpretation in code.