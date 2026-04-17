"""
i18n message resolver.

Usage:
    from app.i18n import t, resolve_locale

    locale = resolve_locale(request)
    msg = t("auth.invalid_credentials", locale)
"""

from __future__ import annotations

from typing import Literal

from starlette.requests import Request

from app.i18n.messages_en import EN_MESSAGES
from app.i18n.messages_ja import JA_MESSAGES

SupportedLocale = Literal["en", "ja"]
DEFAULT_LOCALE: SupportedLocale = "en"

_REGISTRIES: dict[SupportedLocale, dict[str, str]] = {
    "en": EN_MESSAGES,
    "ja": JA_MESSAGES,
}


def resolve_locale(request: Request) -> SupportedLocale:
    """Extract locale from Accept-Language header. Falls back to 'en'."""
    accept = request.headers.get("accept-language", "")
    # Simple prefix match — no q-value parsing needed for two locales.
    for token in accept.split(","):
        lang = token.strip().split(";")[0].strip().lower()
        if lang.startswith("ja"):
            return "ja"
        if lang.startswith("en"):
            return "en"
    return DEFAULT_LOCALE


def t(key: str, locale: SupportedLocale = "en") -> str:
    """Resolve a message key to a localized string.

    Fallback chain: locale registry → EN registry → raw key.
    """
    registry = _REGISTRIES.get(locale, EN_MESSAGES)
    return registry.get(key) or EN_MESSAGES.get(key, key)
