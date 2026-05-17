# FleziBCG MOM UI Guardrails

Frontend owns: layout, navigation, interaction state, visualization, display formatting.
Backend owns: execution truth, status, authorization, approval, audit, quality evaluation, ERP posting, material/backflush.

Persona ≠ permission. Persona-based navigation may help find screens; must not be security.

Operator UI: prioritize current context, current state, next safe action, blockers, quantities/time. Avoid dense dashboards and hidden controls.

Supervisor UI: blocked/delayed operations, line/station state, current WIP, downtime/quality/material blockers, drill-down to events, escalation needs.

AI UI: advisory only — show advisory label, source, uncertainty; no mutation authority, no approval authority.

Future module rules: APS, AI, Digital Twin, Backflush, Acceptance Gate, full Compliance/e-record, ERP posting, advanced material workflows — placeholders only unless current slice explicitly includes them.
