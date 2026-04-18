# ENGINEERING_DECISIONS

One-page reconciled engineering truths for MOM Lite.
This file exists to remove ambiguity across instructions, coding rules, and source structure.
It does not replace the business logic contract.
It clarifies how engineering implementation decisions should be interpreted.

---
## 1. Authoritative Truths
### 1.1 Business truth
`docs/system/mes-business-logic-v1.md` is the authoritative source for:
- execution semantics
- status model
- approval semantics
- impersonation constraints
- business phase boundaries
### 1.2 Engineering truth
`docs/governance/CODING_RULES.md` is the authoritative source for:
- PR classification
- verification gates
- layering rules
- tenant/scope isolation rules
- API, DB, and session rules
- AI engineering rules
### 1.3 Repository truth
`docs/governance/SOURCE_STRUCTURE.md` is authoritative only for:
- repo layout
- module ownership
- entrypoints
- folder responsibility
- frozen public baselines
### 1.4 Entry instruction truth
`.github/copilot-instructions.md` is a short pointer file only.
It is not a full governance specification.

---
## 2. Runtime Architecture
### Current state
- modular monolith
- no microservice split in current runtime architecture
- no Kafka / workflow engine / cloud-only dependency by default
### Future direction
The codebase should remain:
- modular
- boundary-clean
- extraction-ready
But contributors must not prematurely introduce:
- microservice-only assumptions
- distributed messaging requirements
- cloud-vendor lock-in

---
## 3. Core System Principles
### 3.1 Backend is source of truth
- frontend is a dumb view
- frontend never derives execution truth
- frontend never makes authorization decisions
### 3.2 Event-driven execution
- execution events are append-only
- lifecycle state is derived
- cached status is a projection, not the source of truth
### 3.3 Persona is UX-only
- landing page and menu exposure are UX concerns
- persona is not authorization
### 3.4 JWT proves identity only
- JWT does not grant permission by itself
- authorization is checked server-side per request

---
## 4. Tenant and Scope Isolation
### Engineering decision
Tenant and scope isolation are mandatory.
**Chosen interpretation:**
Every public repository method that accesses tenant-owned data must receive validated tenant/scope context explicitly.
No tenant-owned query may be tenant-blind.
This means:
- service layer is responsible for passing validated tenant/scope context
- repository code must not silently escape tenant/scope boundaries
- callers must not rely on frontend filtering for isolation
This reconciles earlier ambiguity between “repository MUST filter tenant_id directly” and “service boundary validates tenant context first”.

---
## 5. Role Taxonomy
### 5.1 Official MOM business roles
These are the primary roles for new business-facing MOM features:
- OPR
- SUP
- IEP
- QAL
- PMG
- PLN
- INV
- ADM
### 5.2 Technical / support / read-only roles
These may exist in implementation, but are not primary MOM business roles:
- OTS
- QCI
- EXE
### 5.3 Role design principle
Use official MOM business roles for new domain features.
Technical roles may support:
- support flows
- read-only access
- transitional compatibility
- system operations

---
## 6. Admin and Support Policy
### 6.1 ADM
- full system administration
- not default production execution persona
### 6.2 OTS
- support / break-glass / on-the-spot support role
- not a normal production persona
### 6.3 Production access
Admin/support production actions must be:
- explicit
- time-bound
- auditable
- governed by support / impersonation policy
### 6.4 Forbidden
Do not treat ADM/OTS as default shop-floor execution actors.

---
## 7. Approval and SoD
### Locked decision
Requester must never equal decider, including under impersonation.
### Additional interpretation
Any governed action must satisfy both:
- authorization check
- approval rule eligibility
Neither alone is sufficient.

---
## 8. Frontend vs Backend Boundary
### Frontend owns
- screen composition
- UX state
- navigation
- display formatting
- i18n
### Backend owns
- execution truth
- status truth
- authz
- approval truth
- audit truth
### Consequence
A visible screen is not proof that an action is allowed.

---
## 9. AI-driven MOM Principle
The product direction is AI-driven MES/MOM.
### AI may:
- summarize
- explain
- detect anomalies
- predict
- recommend
### AI may not by default:
- mutate execution state
- bypass auth / approval / SoD
- replace deterministic business truth
- present uncertain output as authoritative fact
### Engineering implication
AI features must be implemented as:
- advisory
- auditable
- scope-aware
- role-aware

---
## 10. Contribution Decision Rule
Before coding, every contributor should answer:
1. Am I changing business truth?
2. Am I changing engineering truth?
3. Am I changing only structure/layout?
4. Am I changing contract/API/schema?
5. Am I introducing or depending on AI behavior?
If the answer is unclear, stop and clarify before coding.
