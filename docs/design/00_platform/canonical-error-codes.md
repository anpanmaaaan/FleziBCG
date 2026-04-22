# Canonical Error Codes (v4)

## Purpose
Define a global, stable, and extensible error code system used across all domains.

## Format
<PREFIX>_<CATEGORY>_<DETAIL>

## Prefix
- EXE: Execution
- QLT: Quality
- AUTH: Authorization
- VAL: Validation
- SYS: System

## Execution
- EXE_STATE_INVALID
- EXE_ALREADY_ACTIVE
- EXE_CLOSED_RECORD
- EXE_DOWNTIME_OPEN
- EXE_QC_BLOCKED

## Quality
- QLT_TEMPLATE_MISSING
- QLT_INPUT_INVALID
- QLT_RULE_VIOLATION
- QLT_HOLD_ACTIVE
- QLT_REVIEW_REQUIRED

## Auth
- AUTH_UNAUTHORIZED
- AUTH_ROLE_INVALID

## Validation
- VAL_REQUIRED_FIELD
- VAL_INVALID_FORMAT
- VAL_OUT_OF_RANGE

## System
- SYS_INTERNAL_ERROR
- SYS_DB_ERROR
- SYS_TIMEOUT

## Response
{
  "error_code": "EXE_STATE_INVALID",
  "message": "...",
  "details": {}
}
