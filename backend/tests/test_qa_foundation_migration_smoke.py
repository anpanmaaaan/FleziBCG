import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from app.config.settings import settings


BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


@pytest.fixture
def live_db_or_skip():
    import psycopg

    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
    except Exception:
        pytest.skip("DB not reachable - skipping migration smoke")

    return settings.database_url or ""


def _alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def _is_disposable_db(database_url: str) -> bool:
    normalized = database_url.lower()
    return (
        "sqlite" in normalized
        or "_test" in normalized
        or "/test" in normalized
        or "mes_test" in normalized
    )


def test_upgrade_head_smoke(live_db_or_skip):
    cfg = _alembic_config()
    command.upgrade(cfg, "head")


def test_conditional_downgrade_only_for_disposable_db(live_db_or_skip):
    if os.getenv("BE_QA_ALLOW_DESTRUCTIVE_ALEMBIC") != "1":
        pytest.skip("Set BE_QA_ALLOW_DESTRUCTIVE_ALEMBIC=1 to allow downgrade smoke")

    database_url = live_db_or_skip
    if not _is_disposable_db(database_url):
        pytest.skip("Downgrade smoke is blocked: database URL is not marked disposable")

    cfg = _alembic_config()
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
