"""Centralized test DB fixtures for FleziBCG backend.

INTENT:
- Runs DB migration (Alembic upgrade head) exactly once per pytest session via a
  session-scoped autouse fixture.  Individual test fixtures that call init_db()
  afterwards see _ALEMBIC_UPGRADE_RAN=True and skip the migration; seed functions
  remain idempotent.
- Provides a test DB URL safety guard that warns (or raises) when tests run
  against a DB that does not look test-specific.
- Disposes the SQLAlchemy connection pool on session teardown so no connections
  linger after the test run.
- Exposes a pg_show_active_connections() helper for lock diagnostics from tests.

INVARIANTS:
- This module must not change any production DB/session/auth/tenant behavior.
- Production runtime code (app/db/session.py, app/db/init_db.py) is untouched.
- No test fixture here shadows the per-test-file db_session / bridge_fixture /
  station_session_fixture / station_queue_fixture fixtures.  Those fixtures
  control their own transaction scope and cleanup.
"""

from __future__ import annotations

import os
import warnings
from typing import Generator
from urllib.parse import urlparse

import pytest


# ---------------------------------------------------------------------------
# Internal helpers (callable from tests via import)
# ---------------------------------------------------------------------------


def _mask_db_url(url: str) -> str:
    """Return DB URL with password replaced by ***. Safe for logging."""
    try:
        parsed = urlparse(url)
        if parsed.password:
            safe_netloc = parsed.netloc.replace(
                f":{parsed.password}@", ":***@", 1
            )
            return url.replace(parsed.netloc, safe_netloc, 1)
        return url
    except Exception:  # pragma: no cover
        pass
    return "<unparseable-url>"


def _looks_like_test_db(url: str) -> bool:
    """Return True if the DB name in url looks test-specific.

    Heuristics (case-insensitive):
      - DB path component contains 'test'
      - e.g. /mes_test, /test_mes, /test, /_test_*
    """
    url_lower = url.lower()
    return (
        "_test" in url_lower
        or "/test" in url_lower
        or url_lower.endswith("/test")
        or "mes_test" in url_lower
        or "test_mes" in url_lower
    )


def assert_test_db_url(url: str) -> None:
    """Fail loudly if url does not look like a safe test DB.

    Passes unconditionally when FLEZIBCG_ALLOW_TEST_DB_RESET=1 is set.

    Usage::

        from tests.conftest import assert_test_db_url
        assert_test_db_url(settings.database_url)

    Raises RuntimeError with a clear message so the developer immediately
    knows which DB was targeted and what to do.
    """
    allow_override = os.environ.get("FLEZIBCG_ALLOW_TEST_DB_RESET", "").strip() == "1"
    if allow_override:
        return
    if not _looks_like_test_db(url):
        raise RuntimeError(
            "SAFETY GUARD — test DB reset refused.\n"
            f"  Resolved DB URL (masked): {_mask_db_url(url)}\n"
            "  The database name does not contain 'test'.\n"
            "  Either:\n"
            "    1. Point DATABASE_URL / POSTGRES_DB at a DB whose name contains 'test', OR\n"
            "    2. Set FLEZIBCG_ALLOW_TEST_DB_RESET=1 to explicitly allow reset on this DB.\n"
            "  Refusing to run destructive test operations against a non-test DB."
        )


def pg_show_active_connections(url: str, *, dbname: str | None = None) -> list[dict]:
    """Return active PostgreSQL connections for diagnostic purposes.

    Passwords are NOT included in the returned data.
    Safe to call from test teardown or lock-diagnostic helpers.

    Args:
        url:    DB URL used only for the diagnostic connection itself.
        dbname: Filter results to this database name. If None, returns all
                connections except the diagnostic connection itself.

    Returns:
        List of dicts with keys: pid, state, wait_event_type, wait_event,
        query_start, query_snippet.  Returns [{"error": str}] on failure.
    """
    try:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(
            url, connect_timeout=2, row_factory=dict_row
        ) as conn:
            with conn.cursor() as cur:
                if dbname:
                    cur.execute(
                        "SELECT pid, state, wait_event_type, wait_event,"
                        " query_start,"
                        " left(query, 120) AS query_snippet"
                        " FROM pg_stat_activity"
                        " WHERE datname = %s AND pid != pg_backend_pid()"
                        " ORDER BY query_start NULLS LAST",
                        (dbname,),
                    )
                else:
                    cur.execute(
                        "SELECT pid, state, wait_event_type, wait_event,"
                        " query_start,"
                        " left(query, 120) AS query_snippet"
                        " FROM pg_stat_activity"
                        " WHERE pid != pg_backend_pid()"
                        " ORDER BY query_start NULLS LAST"
                    )
                return cur.fetchall()
    except Exception as exc:  # pragma: no cover
        return [{"error": str(exc)}]


# ---------------------------------------------------------------------------
# Session-scoped autouse fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def _init_db_once() -> Generator[None, None, None]:
    """Run DB migration and seed exactly once per pytest session.

    WHY: Individual test fixtures call init_db() in their setup, but
    _ALEMBIC_UPGRADE_RAN (module-level flag in app.db.init_db) ensures Alembic
    only runs once per process.  Running this fixture first guarantees:

      1. Schema is at Alembic head before any test opens a session.
      2. RBAC/demo seed data exists before tests read it.
      3. Individual fixture calls to init_db() become cheap no-ops for the
         Alembic step and idempotent for the seed step.

    DB not reachable → skips silently; tests that need a real DB skip
    themselves via their own psycopg connectivity check.
    """
    try:
        import psycopg
        from app.config.settings import settings

        url = settings.database_url or ""
        psycopg.connect(url, connect_timeout=2).close()
    except Exception:
        # DB not available — live DB tests will skip themselves.
        yield
        return

    # Safety: warn if running against a non-test DB name.
    from app.config.settings import settings

    url = settings.database_url or ""
    if not _looks_like_test_db(url):
        warnings.warn(
            f"Running tests against a DB that does not look test-specific.\n"
            f"  URL (masked): {_mask_db_url(url)}\n"
            "  Set POSTGRES_DB to a name containing 'test' for isolation, or\n"
            "  set FLEZIBCG_ALLOW_TEST_DB_RESET=1 to silence this warning.",
            stacklevel=1,
        )

    from app.db.init_db import init_db

    init_db()
    yield


@pytest.fixture(scope="session", autouse=True)
def _dispose_engine_on_session_end() -> Generator[None, None, None]:
    """Dispose the SQLAlchemy connection pool after the test session ends.

    WHY: Without explicit disposal, pooled connections remain open until the
    Python process exits.  On CI (where the DB port is shared), these idle
    connections can block a subsequent test run that tries to drop/recreate
    objects.  engine.dispose() closes all checked-in connections immediately.
    """
    yield
    try:
        from app.db.session import engine

        engine.dispose()
    except Exception:  # pragma: no cover
        pass
