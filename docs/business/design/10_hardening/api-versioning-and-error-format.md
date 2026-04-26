# ADR - API Versioning and Error Format

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added API versioning and RFC 9457-compatible error format decision. |

## Status

**Accepted design direction.**

## Context

FleziBCG API contracts need stable versioning and machine-readable errors for frontend, integration adapters, and future agents. Older references to RFC 7807 should be updated because RFC 9457 obsoletes RFC 7807.

## Decision

Use URL major versioning for public/backend API surfaces:

```text
/api/v1/...
```

Use an RFC 9457-compatible Problem Details response shape, extended with FleziBCG-specific `code`, `correlation_id`, and optional `details`.

## Canonical Error Shape

```json
{
  "type": "https://docs.flezibcg/errors/OPERATION_NOT_FOUND",
  "title": "Operation not found",
  "status": 404,
  "detail": "The requested operation does not exist or is outside your scope.",
  "instance": "/api/v1/execution/operations/123",
  "code": "OPERATION_NOT_FOUND",
  "correlation_id": "uuid",
  "details": {}
}
```

## Rules

1. `code` remains mandatory for frontend/i18n/stable error handling.
2. `status` must match HTTP status.
3. `correlation_id` must be returned on all errors.
4. Validation errors should include structured field details.
5. Authorization errors must not leak out-of-scope entity existence.
6. Integration errors should include external system reference only when safe.

## Versioning Rules

| Change Type | API Version Impact |
|---|---|
| Add optional response field | no major version bump |
| Add optional request field | no major version bump |
| Remove/rename field | major version bump |
| Change command semantics | major version bump or new endpoint |
| Add enum value | no major bump, but clients must handle unknown values |
| Tighten authorization | no version bump |

## Anti-Patterns

- Do not return only `{ "error": "..." }`.
- Do not encode business errors only as HTTP 500.
- Do not expose stack traces in API errors.
- Do not introduce `/api/latest` for production clients.

## References

- RFC 9457: https://www.rfc-editor.org/rfc/rfc9457.html
