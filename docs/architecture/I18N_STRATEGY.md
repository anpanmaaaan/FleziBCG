# I18N_STRATEGY

## Purpose
Define language and localization strategy compatible with stable backend contracts.

## Scope
- API response semantics
- Frontend display mapping
- Tenant/user language handling boundaries

## Key Decisions (LOCKED)
- Backend returns enums/codes, not translated business text.
- Frontend maps codes to display text via semantic keys.
- Business logic is not encoded in translated strings.
- Dashboard and monitoring surfaces remain code-driven for i18n safety.

## Explicitly Out Of Scope
- Server-side translated narrative responses
- Locale-specific business-rule branching
- Full i18n framework selection in this documentation phase

## Future (FUTURE)
- Tenant/user preference-driven language packs at UI layer.
