# Audit and Observability Architecture

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Expanded audit requirements for execution sessions and operator/resource context. |

Status: Canonical audit/observability note.

## 1. Audit rule

Important operational and governance mutations must be auditable.

## 2. Execution-specific audit requirements

When execution is session-owned, the audit model should distinguish at least:
- authenticated user
- identified operator
- station/resource session id
- equipment/resource id where relevant
- tenant/scope context
- action code
- target operation/run/step id

## 3. Observability requirements

Structured logs should include contextual identifiers where relevant:
- request_id
- tenant_id
- user_id
- operator_id when applicable
- action_code
- resource identifiers

## 4. AI-specific observability

AI outputs must remain traceable to source context, feature id, model/version where relevant, and effective user/scope context.
