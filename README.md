
Project: AI-driven MES/MOM Platform Design & Architecture

This project is for designing and evolving a lightweight but production-grade AI-driven MES/MOM system aligned with ISA-95.
The system direction is:

* start from a strong MES execution core
* progressively expand into a broader MOM platform
* keep AI as advisory/intelligence layer first, not source of truth
* support future capabilities such as digital twin, OEE deep dive AI, APS-lite / scheduling, quality operations, traceability, and later full MOM domains

Core product principles

* Backend is the source of truth
* Execution is event-driven and append-only where relevant
* Status is derived, projections are not the source of truth
* Frontend is UX only for visibility/navigation, never authorization truth
* Persona ≠ permission
* JWT proves identity only, authorization is checked per request on backend
* AI is advisory by default: explain, predict, recommend; it must not silently mutate execution or bypass auth/approval/SoD

Current architecture direction

* current implementation/runtime can remain modular monolith
* design should stay microservice-ready in boundaries
* target deployment should be on-prem and cloud adaptable
* target system should be multi-tenant
* stack: Python / FastAPI / React / Tailwind / PostgreSQL

IAM / governance direction

The role/access model is a major foundation and should be treated as platform-level architecture, not just UI matrix.

Key decisions:

* separate:
    * Identity
    * Access Control
    * User Lifecycle
    * Approval & Delegation
    * Session / Security Governance
* support:
    * login
    * logout
    * logout all sessions
    * refresh token
    * session revoke
    * user invitation / activation / deactivation / lock / unlock
    * role + scope assignment
    * approval for privileged access
    * impersonation / support mode with full audit
* Admin/support are not default production actors
* production actions by ADM/OTS should go through controlled impersonation / support session
* keep separation of duties strict: requester must not equal approver, even under impersonation

Role design direction

Use MES/MOM best-practice role thinking:

* OPR
* SUP
* IEP
* QCI / QAL
* PMG
* EXE
* ADM
* OTS

General principles:

* system roles as baseline
* future-ready for custom roles
* future-ready for multi-role
* future-ready for scope hierarchy
* keep FE screen exposure separate from BE authorization
* station execution is operator-focused
* supervisor should have monitoring + limited intervention, not full operator-style execution
* PMG is broad-view + selected approvals, not pure read-only
* QC and APS screens may exist early as shells/placeholders, but scope meaning must be defined clearly at each phase

Scope hierarchy direction

Design for hierarchical scope, not tenant-only long term:

* tenant
* plant
* area
* line
* station
* equipment

Documentation / governance direction

Project documentation should be split clearly:

* business truth
* coding rules
* engineering decisions
* source structure
* short entry instructions

Key governance idea:

* no duplicated contradictory truths across files
* one authoritative file for engineering rules
* one authoritative file for business logic
* one short decision file to reconcile ambiguous implementation truths

Product roadmap direction

Recommended implementation order:

1. Foundation
    * auth, role, scope, session, approval, audit, master data, plant hierarchy
2. Execution core
    * WO/OP execution, events, status derivation, downtime/reason handling
3. Supervisory layer
    * global operations, dashboards, operation detail, Gantt
4. Quality lite + traceability
5. AI wave 1
    * summaries, anomaly detection, OEE insights, delay/bottleneck hints
6. Material / maintenance / operational digital twin
7. APS-lite / planning support
8. Broader MOM expansion

AI-driven MES/MOM direction

AI should be designed in layers:

* observe
* explain
* predict
* recommend

Priority AI use cases:

* OEE Deep Dive AI
* anomaly detection
* shift summary
* delay risk prediction
* bottleneck explanation
* quality trend explanation
* natural-language operational insights

Digital twin direction

Digital twin should start as operational digital twin, not 3D-first:

* line / station / machine / WO / WIP / queue / block / delay state
* later support what-if analysis and planning-aware simulation
* AI can sit on top of twin for anomaly detection, explainability, prediction, and recommendation

Gantt / timeline direction

Gantt should follow MES best practice:

* use business viewport modes (shift/day/week/fit)
* do not auto-fit full data span as default
* do not let realtime continuously rescale full timeline
* support grouped rendering for large WO
* row click should navigate to Operation Detail screen, not open inline detail panel

Working style preference for this project

When discussing this project:

* think at overall architecture and roadmap level, not only current phase
* always distinguish:
    * what must be done now
    * what should be designed now but implemented later
    * what can wait
* prioritize foundation and execution truth before advanced AI
* use MES/MOM best practice as default lens
* when reviewing design, call out:
    * inconsistencies
    * governance risks
    * scale/performance risks
    * future extensibility issues