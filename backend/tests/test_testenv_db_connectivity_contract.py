"""Connectivity contract tests for the FleziBCG backend test DB infrastructure.

Tests in this file cover:
- DB URL masking redacts passwords.
- check_test_db_readiness() returns a clear message for unreachable hosts.
- check_test_db_readiness() includes compose file reference in failure message.
- check_test_db_readiness() succeeds for a live DB (skipped if DB not available).

These tests do NOT require a live DB except for the live-only test, which is
marked to skip cleanly when no DB is available.
"""

from __future__ import annotations

import pytest

from tests.conftest import (
    _DEV_DB_START_HINT,
    _mask_db_url,
    check_test_db_readiness,
    _to_psycopg_url,
)


# ---------------------------------------------------------------------------
# URL masking
# ---------------------------------------------------------------------------


class TestDbUrlMaskingContract:
    def test_mask_redacts_password(self) -> None:
        url = "postgresql+psycopg://mes:supersecret@localhost:5432/mes"
        masked = _mask_db_url(url)
        assert "supersecret" not in masked
        assert "***" in masked

    def test_mask_preserves_host_and_dbname(self) -> None:
        url = "postgresql+psycopg://mes:s3cr3t@db-host:5432/mydb"
        masked = _mask_db_url(url)
        assert "db-host" in masked
        assert "mydb" in masked
        assert "5432" in masked

    def test_mask_no_password_unchanged(self) -> None:
        url = "postgresql+psycopg://mes@localhost:5432/mes"
        assert _mask_db_url(url) == url

    def test_mask_never_returns_empty(self) -> None:
        for url in [
            "postgresql+psycopg://mes:pw@localhost:5432/mes",
            "not-a-url",
        ]:
            result = _mask_db_url(url)
            assert isinstance(result, str)
            assert len(result) > 0


# ---------------------------------------------------------------------------
# _to_psycopg_url — SQLAlchemy dialect stripping
# ---------------------------------------------------------------------------


class TestToPsycopgUrl:
    def test_strips_psycopg_dialect(self) -> None:
        url = "postgresql+psycopg://mes:pw@localhost:5432/mes"
        result = _to_psycopg_url(url)
        assert result == "postgresql://mes:pw@localhost:5432/mes"
        assert "+psycopg" not in result

    def test_strips_postgres_plus_psycopg_dialect(self) -> None:
        url = "postgres+psycopg://mes:pw@localhost:5432/mes"
        result = _to_psycopg_url(url)
        assert result == "postgresql://mes:pw@localhost:5432/mes"

    def test_plain_postgresql_url_unchanged(self) -> None:
        url = "postgresql://mes:pw@localhost:5432/mes"
        assert _to_psycopg_url(url) == url

    def test_non_matching_url_unchanged(self) -> None:
        url = "sqlite:///test.db"
        assert _to_psycopg_url(url) == url


# ---------------------------------------------------------------------------
# check_test_db_readiness — unreachable host
# ---------------------------------------------------------------------------


class TestCheckTestDbReadiness:
    _UNREACHABLE = "postgresql+psycopg://mes:mes@127.0.0.1:59999/mes"

    def test_returns_false_for_unreachable_host(self) -> None:
        ok, msg = check_test_db_readiness(self._UNREACHABLE)
        assert ok is False

    def test_failure_message_not_empty(self) -> None:
        ok, msg = check_test_db_readiness(self._UNREACHABLE)
        assert not ok
        assert len(msg) > 0

    def test_failure_message_redacts_password(self) -> None:
        ok, msg = check_test_db_readiness(self._UNREACHABLE)
        assert not ok
        assert ":mes@" not in msg or "***" in msg  # password 'mes' must be redacted

    def test_failure_message_references_compose_file(self) -> None:
        ok, msg = check_test_db_readiness(self._UNREACHABLE)
        assert not ok
        assert "docker-compose.db.yml" in msg

    def test_failure_message_references_compose_command(self) -> None:
        ok, msg = check_test_db_readiness(self._UNREACHABLE)
        assert not ok
        assert "docker compose" in msg

    def test_failure_message_references_force_recreate(self) -> None:
        """Message must explain the stale-container fix."""
        ok, msg = check_test_db_readiness(self._UNREACHABLE)
        assert not ok
        assert "--force-recreate" in msg

    def test_dev_db_start_hint_contains_compose_file(self) -> None:
        assert "docker-compose.db.yml" in _DEV_DB_START_HINT

    def test_dev_db_start_hint_contains_force_recreate(self) -> None:
        assert "--force-recreate" in _DEV_DB_START_HINT


# ---------------------------------------------------------------------------
# check_test_db_readiness — live DB (skip if unreachable)
# ---------------------------------------------------------------------------


def _live_db_url() -> str | None:
    """Return the configured DB URL, or None if settings cannot be loaded."""
    try:
        from app.config.settings import settings

        return settings.database_url or None
    except Exception:
        return None


def _live_db_available() -> bool:
    url = _live_db_url()
    if not url:
        return False
    ok, _ = check_test_db_readiness(url)
    return ok


@pytest.mark.skipif(not _live_db_available(), reason="live DB not available")
class TestCheckTestDbReadinessLive:
    def test_returns_true_for_live_db(self) -> None:
        url = _live_db_url()
        assert url is not None
        ok, msg = check_test_db_readiness(url)
        assert ok is True
        assert msg == ""
