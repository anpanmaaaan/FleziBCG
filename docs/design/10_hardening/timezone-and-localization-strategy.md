# Timezone and Localization Strategy — FleziBCG

## Status

P1-HARDENING ADR. Does not block P0-A, but P0-A should prepare plant timezone fields.

## Decisions

- Store persisted instants in UTC-compatible timestamps.
- Use plant canonical IANA timezone for production calendar, shift boundary, and OEE reporting.
- Use frontend i18n keys for UI text.
- Do not hard-code country-specific calendar/timezone assumptions in core.
- Support cross-midnight shifts by plant-local business-date rules.
- `recorded_at` should come from trusted backend/database clock.
- `occurred_at` may represent source/business time and must be validated.

## P0-A Requirement

Plant foundation should include a canonical `timezone` field.
