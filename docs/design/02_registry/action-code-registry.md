# Action Code Registry

Status: Authoritative action-code registry  
Scope: Cross-domain action naming  
Depends on:
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`

This document defines the canonical action-code registry for MOM Lite.

It is authoritative for:
- action-code naming
- action-code family ownership
- auditable privileged action vocabulary
- FE/BE/shared references for controlled actions

This document is not:
- the RBAC permission matrix by itself
- the business truth for whether an action is allowed in a specific state
- the UI label registry

---

## 1. Purpose

Action codes are needed so the platform can:
- log actions consistently
- reason about permissions consistently
- expose auditable operation names
- keep FE and BE aligned on action identity

They are especially important for:
- authorization
- audit
- support mode
- approval/governance
- analytics/usage tracking

---

## 2. Naming rules

### ACR-001 — lower-case dot notation
Format:
`<domain>.<verb>`  
or where needed  
`<domain>.<subdomain>.<verb>`

Examples:
- `execution.start`
- `execution.report_qty`
- `approval.decide`
- `session.revoke`
- `admin.session.revoke`

### ACR-002 — action code identifies the governed action, not the UI button text
Use:
- `execution.complete`
Not:
- `complete_button`

### ACR-003 — do not encode role into action code
Use:
- `execution.close`
Not:
- `supervisor.close`

Role ownership belongs to authorization logic, not code naming.

---

## 3. Execution action family

### Claim / ownership
- `execution.claim`
- `execution.release`

### Runtime lifecycle
- `execution.start`
- `execution.pause`
- `execution.resume`
- `execution.complete`

### Quantity / reporting
- `execution.report_qty`
- `execution.report_scrap`

### Downtime
- `execution.start_downtime`
- `execution.end_downtime`

### Closure
- `execution.close`
- `execution.reopen`

---

## 4. Quality action family

### Measurement
- `quality.submit_qc_measurement`

### Review / exception
- `quality.raise_exception`

### Disposition
- `quality.record_disposition_decision`

### Future reserved examples
- `quality.release_hold`
- `quality.request_recheck`
- `quality.accept_with_deviation`
- `quality.confirm_scrap`

These future-reserved examples may still map to one canonical decision command in implementation.  
Reserve them for analytics/policy reasoning only if needed, but do not create duplicate command boundaries casually.

---

## 5. Approval action family

- `approval.request`
- `approval.decide`
- `approval.cancel`
- `approval.delegate`

---

## 6. Auth / session action family

- `auth.login`
- `auth.logout`
- `auth.logout_all`
- `auth.refresh`
- `auth.password_change`
- `auth.password_reset_request`
- `auth.password_reset_confirm`

- `session.revoke`
- `session.view`
- `session.list`

---

## 7. IAM action family

- `iam.user.invite`
- `iam.user.activate`
- `iam.user.deactivate`
- `iam.user.lock`
- `iam.user.unlock`
- `iam.role.assign`
- `iam.role.unassign`
- `iam.scope.assign`
- `iam.scope.unassign`

---

## 8. Impersonation / support action family

- `impersonation.start`
- `impersonation.end`

### Administrative/support examples
- `admin.session.revoke`
- `admin.user.lock`
- `support.break_glass.start`
- `support.break_glass.end`

Use these only where separate administrative/support observability is needed.

---

## 9. Action code usage rules

### ACR-USE-001 — Use canonical action code in audit logs
Each auditable protected action should record:
- action code
- actor
- scope
- target
- outcome

### ACR-USE-002 — Action code is not sufficient permission truth
Possessing or displaying an action code does not itself authorize the action.

### ACR-USE-003 — FE may use action names for UX hints, but backend remains authoritative
Visible affordance is never proof of permission.

### ACR-USE-004 — `allowed_actions` in projections may expose canonical command/action names
Projection-level `allowed_actions` should remain consistent with this registry and canonical command vocabulary.

---

## 10. Relationship to commands

Command names and action codes are related but not always identical.

### Example
Command boundary:
- `submit_qc_measurement`

Action code:
- `quality.submit_qc_measurement`

### Rule
- command name = transport/business command vocabulary
- action code = auditable authorization/logging vocabulary

Use one-to-one mapping where practical.

---

## 11. Reserved future families

The following domains may add action families later:
- `maintenance.*`
- `material.*`
- `traceability.*`
- `planning.*`
- `digital_twin.*`
- `ai.*`

Any new family must:
- follow this naming pattern
- be added here first
- avoid collisions with existing codes

---

## 12. Forbidden patterns

- upper-case action codes
- snake_case action codes
- role-specific action code names
- UI-text-derived action codes
- multiple codes for the same protected action without explicit reason
- inventing feature-local action code strings inside components or services

---

## 13. Compatibility rule

Renaming an action code is a contract-level change because it may affect:
- audit queries
- authorization mapping
- analytics
- support tooling

Therefore renames require:
- architecture/contract PR
- registry update
- impacted doc update
