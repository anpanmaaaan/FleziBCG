"""baseline

Revision ID: 0001
Revises:
Create Date: 2026-04-28 00:00:00.000000

WHY: This is a no-op baseline revision that represents the schema state
established by Base.metadata.create_all() and the 12 SQL migration scripts
(backend/scripts/migrations/0001–0012). It does not recreate any tables.

USAGE:
  Existing installations (DB already provisioned):
    alembic stamp 0001

  New / clean installations:
    python -m app.db.init_db   # creates schema + seeds
    alembic stamp 0001         # registers alembic version

  Future schema changes: use alembic revision --autogenerate
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # INTENTIONAL NO-OP: schema was already established outside Alembic.
    # All future schema changes must be applied via Alembic revisions only.
    pass


def downgrade() -> None:
    # INTENTIONAL NO-OP: we cannot safely drop a pre-existing baseline schema.
    pass
