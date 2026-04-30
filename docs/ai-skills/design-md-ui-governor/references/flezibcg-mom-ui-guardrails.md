# FleziBCG MOM UI Guardrails

## Backend Truth Boundary

Frontend owns:

- layout;
- navigation;
- interaction state;
- visualization;
- display formatting;
- local UI composition.

Backend owns:

- execution truth;
- status truth;
- authorization truth;
- approval truth;
- audit truth;
- quality evaluation truth;
- ERP/integration posting result truth;
- material/backflush truth.

## Persona Is Not Permission

Persona-based navigation may help users find screens, but it must not be treated as security.

Never describe a frontend role/menu check as authorization enforcement.

## Operator UI Rules

Operator UI should prioritize:

1. current context;
2. current state;
3. next safe action;
4. blockers;
5. quantities/time.

Avoid dense dashboards and hidden controls.

## Supervisor UI Rules

Supervisor UI should prioritize:

- blocked/delayed operations;
- line/station state;
- current WIP;
- downtime/quality/material blockers;
- drill-down to event history;
- escalation needs.

## AI UI Rules

AI is advisory.

AI UI must show:

- advisory label;
- source/context;
- uncertainty where relevant;
- no mutation authority;
- no approval authority.

## Future Module Rules

APS, AI, Digital Twin, Backflush, Acceptance Gate, full Compliance/e-record, ERP posting, and advanced material workflows may appear as future placeholders only unless the current implementation slice explicitly includes them.
