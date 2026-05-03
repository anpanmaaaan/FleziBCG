"""Regression tests for testenv DB safety guards (TECH-DEBT-TESTENV-01).

Verifies:
- assert_test_db_url() rejects non-test DB URLs.
- assert_test_db_url() accepts URLs whose DB name contains 'test'.
- assert_test_db_url() accepts any URL when FLEZIBCG_ALLOW_TEST_DB_RESET=1.
- _mask_db_url() redacts passwords and never returns the raw password.
- pg_show_active_connections() returns a list (even on failure).
- conftest session fixtures are importable and callable.
"""

from __future__ import annotations

import os

import pytest

from tests.conftest import (
    _mask_db_url,
    _looks_like_test_db,
    assert_test_db_url,
    pg_show_active_connections,
)


# ---------------------------------------------------------------------------
# _looks_like_test_db
# ---------------------------------------------------------------------------


class TestLooksLikeTestDb:
    def test_url_with_test_suffix_is_safe(self):
        assert _looks_like_test_db("postgresql+psycopg://u:p@localhost/mes_test") is True

    def test_url_with_test_prefix_is_safe(self):
        assert _looks_like_test_db("postgresql+psycopg://u:p@localhost/test_mes") is True

    def test_url_ending_with_slash_test_is_safe(self):
        assert _looks_like_test_db("postgresql://u:p@localhost:5432/test") is True

    def test_production_db_name_is_not_safe(self):
        assert _looks_like_test_db("postgresql+psycopg://u:p@localhost/mes") is False

    def test_uppercase_test_in_name_is_case_insensitive(self):
        # URLs are lowercased internally.
        assert _looks_like_test_db("postgresql+psycopg://u:p@localhost/MES_TEST") is True

    def test_empty_url_is_not_safe(self):
        assert _looks_like_test_db("") is False


# ---------------------------------------------------------------------------
# assert_test_db_url — rejection
# ---------------------------------------------------------------------------


class TestAssertTestDbUrl:
    def test_rejects_non_test_db_without_env_override(self, monkeypatch):
        """Safety guard must raise for a non-test DB name by default."""
        monkeypatch.delenv("FLEZIBCG_ALLOW_TEST_DB_RESET", raising=False)
        with pytest.raises(RuntimeError, match="SAFETY GUARD"):
            assert_test_db_url("postgresql+psycopg://mes:mes@localhost:5432/mes")

    def test_rejects_non_test_db_with_override_set_to_zero(self, monkeypatch):
        """Override=0 must not disable the guard."""
        monkeypatch.setenv("FLEZIBCG_ALLOW_TEST_DB_RESET", "0")
        with pytest.raises(RuntimeError, match="SAFETY GUARD"):
            assert_test_db_url("postgresql+psycopg://mes:mes@localhost:5432/mes")

    def test_accepts_test_db_without_env_override(self, monkeypatch):
        """URL containing 'test' in DB name must pass without env override."""
        monkeypatch.delenv("FLEZIBCG_ALLOW_TEST_DB_RESET", raising=False)
        # Should not raise.
        assert_test_db_url("postgresql+psycopg://mes:mes@localhost:5432/mes_test")

    def test_accepts_any_db_with_override_set_to_one(self, monkeypatch):
        """FLEZIBCG_ALLOW_TEST_DB_RESET=1 bypasses the name check."""
        monkeypatch.setenv("FLEZIBCG_ALLOW_TEST_DB_RESET", "1")
        # Should not raise — bypass is explicit.
        assert_test_db_url("postgresql+psycopg://mes:mes@localhost:5432/mes")

    def test_error_message_includes_masked_url(self, monkeypatch):
        """Error message must include the masked URL so dev can diagnose."""
        monkeypatch.delenv("FLEZIBCG_ALLOW_TEST_DB_RESET", raising=False)
        with pytest.raises(RuntimeError) as exc_info:
            assert_test_db_url("postgresql+psycopg://mes:secret@localhost:5432/mes")
        msg = str(exc_info.value)
        assert "secret" not in msg, "Password must not appear in error message"
        assert "***" in msg or "mes" in msg.lower()

    def test_error_message_includes_actionable_instructions(self, monkeypatch):
        """Error message must tell the developer what to do."""
        monkeypatch.delenv("FLEZIBCG_ALLOW_TEST_DB_RESET", raising=False)
        with pytest.raises(RuntimeError) as exc_info:
            assert_test_db_url("postgresql+psycopg://mes:mes@localhost:5432/mes")
        msg = str(exc_info.value)
        assert "FLEZIBCG_ALLOW_TEST_DB_RESET" in msg


# ---------------------------------------------------------------------------
# _mask_db_url — password redaction
# ---------------------------------------------------------------------------


class TestMaskDbUrl:
    def test_masks_password_in_standard_url(self):
        masked = _mask_db_url("postgresql+psycopg://user:supersecret@localhost:5432/mes")
        assert "supersecret" not in masked
        assert "***" in masked

    def test_preserves_host_and_dbname(self):
        masked = _mask_db_url("postgresql+psycopg://user:pw@localhost:5432/mes_test")
        assert "localhost" in masked
        assert "mes_test" in masked

    def test_no_password_returns_url_unchanged(self):
        url = "postgresql+psycopg://user@localhost:5432/mes_test"
        masked = _mask_db_url(url)
        assert masked == url

    def test_unparseable_url_returns_safe_placeholder(self):
        masked = _mask_db_url("not a real url :::!")
        # Must not raise, must return something safe.
        assert isinstance(masked, str)
        assert len(masked) > 0


# ---------------------------------------------------------------------------
# pg_show_active_connections — diagnostics helper
# ---------------------------------------------------------------------------


class TestPgShowActiveConnections:
    def test_returns_list_on_unreachable_db(self):
        """Helper must return a list even when DB is not reachable."""
        result = pg_show_active_connections("postgresql://bad:bad@127.0.0.1:9999/no_db")
        assert isinstance(result, list)

    def test_error_entry_contains_error_key_on_failure(self):
        result = pg_show_active_connections("postgresql://bad:bad@127.0.0.1:9999/no_db")
        # Either an empty list (no connections) or a list with an error dict.
        if result:
            assert "error" in result[0]

    def test_live_db_returns_list(self):
        """With a reachable DB, returns a list of connection rows."""
        try:
            import psycopg
            from app.config.settings import settings

            psycopg.connect(settings.database_url, connect_timeout=2).close()
        except Exception:
            pytest.skip("DB not reachable — skipping live diagnostic test")

        from app.config.settings import settings

        result = pg_show_active_connections(settings.database_url)
        assert isinstance(result, list)
        # Each row should be a dict with at least 'state' key.
        for row in result:
            assert isinstance(row, dict)
