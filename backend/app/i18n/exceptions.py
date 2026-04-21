"""
Structured i18n-aware HTTP exception.

Usage in routes:
    from app.i18n.exceptions import I18nHTTPException

    raise I18nHTTPException(
        status_code=401,
        error_code="auth.invalid_credentials",
    )

The global handler in main.py resolves the localized message from Accept-Language.
"""

from __future__ import annotations

from fastapi import HTTPException


class I18nHTTPException(HTTPException):
    """HTTPException that carries a semantic error_code for i18n resolution."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        # Store the error_code; detail is set to the code as a fallback.
        super().__init__(status_code=status_code, detail=error_code, headers=headers)
        self.error_code = error_code
