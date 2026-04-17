"""
Backend i18n module — lightweight message resolver for API error responses.

Architecture rule: Backend returns error codes / message keys.
The optional `message` field provides a localized human-readable string
based on Accept-Language, but the `error_code` is the contract.

Supported locales: en (canonical), ja (secondary).
"""

from app.i18n.resolver import t, resolve_locale  # noqa: F401
