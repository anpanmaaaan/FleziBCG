# ENGINEERING_DECISIONS

One-page reconciled engineering truths for FleziBCG MOM Platform.
This file exists to remove ambiguity across instructions, coding rules, and source structure.
It does not replace platform or domain business truth.

---
## 1. Authoritative Truths
### 1.1 Product and domain business truth
Use the most specific authoritative design document in this package:
- `docs/design/00_platform/product-business-truth-overview.md` for platform/product truth
- `docs/design/02_domain/execution/business-truth-station-execution-v4.md` and related execution contracts for execution truth
- `docs/design/02_domain/quality/quality-domain-contracts.md` and `business-truth-quality-lite.md` for quality truth
### 1.2 Engineering truth
`docs/governance/CODING_RULES.md` remains authoritative for engineering rules.
### 1.3 Repository truth
`docs/governance/SOURCE_STRUCTURE.md` remains authoritative for structure and public baselines.

---
## 2. Runtime Architecture
### Current state
- modular monolith
- no forced microservice split
### Future direction
- modular
- extraction-ready
- no cloud-only or distributed-only assumptions by default

---
## 3. Core System Principles
- backend is source of truth
- execution is append-only/event-driven where relevant
- persona is UX-only
- JWT proves identity only

---
## 4. Tenant and Scope Isolation
Tenant and scope isolation are mandatory.
Validated tenant/scope context must remain explicit at repository boundaries.

---
## 5. Role Taxonomy
Primary MOM business roles:
- OPR
- SUP
- IEP
- QAL
- PMG
- PLN
- INV
- ADM

Specialized/support compatibility roles may exist separately, including:
- QCI
- OTS

---
## 6. Admin and Support Policy
ADM/OTS are not default production execution actors.
Production access by support/admin must be explicit, time-bound, auditable, and governed.

---
## 7. Approval and SoD
Requester must never equal decider, including under impersonation.

---
## 8. Frontend vs Backend Boundary
Frontend owns UX composition.
Backend owns execution truth, authz, approval truth, and audit truth.

---
## 9. AI-driven MOM Principle
AI is advisory by default and must not silently mutate execution or bypass governance.

---
## 10. Execution Architecture Decisions
### 10.1 Claim deprecation
Claim is deprecated from the target execution model.
Any remaining claim-centric implementation is compatibility debt during migration.

### 10.2 Session-owned execution
Target execution ownership is based on active execution session context.
For Station Execution this is a station session that binds:
- authenticated user
- identified operator
- bound equipment/resource context when required
