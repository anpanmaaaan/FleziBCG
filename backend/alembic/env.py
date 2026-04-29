"""Alembic migration environment for FleziBCG backend.

INVARIANT: sqlalchemy.url is sourced from application settings only.
Never hard-code DB credentials here.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

# WHY: Ensure 'backend/' directory is on sys.path so that 'app.*' imports
# resolve correctly when alembic is invoked from backend/ (the default).
_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from alembic import context

# Import models via init_db module — it registers every ORM model with
# Base.metadata via its top-level imports. The init_db() function itself is
# NOT called here; only module-level model registrations are needed.
from app.db.base import Base
import app.db.init_db as _models  # noqa: F401 — side-effect: registers all models

# App engine (already configured with correct DB URL from settings).
from app.db.session import engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection required)."""
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (live DB connection)."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
