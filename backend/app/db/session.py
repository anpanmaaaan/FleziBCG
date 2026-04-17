from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings


engine = create_engine(
    settings.database_url,
    future=True,
    # WHY: pool_pre_ping sends a lightweight check (SELECT 1) before reusing
    # a connection, preventing "server has gone away" errors after DB restarts.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    # WHY: expire_on_commit=False keeps object attributes accessible after
    # commit without an extra SELECT. Safe because our request-scoped sessions
    # are short-lived and discarded after the response.
    expire_on_commit=False,
)
