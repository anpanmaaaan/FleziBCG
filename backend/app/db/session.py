import logging
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings


def _get_sqlite_fallback_url() -> str:
    backend_dir = Path(__file__).resolve().parents[2]
    return f"sqlite:///{backend_dir / 'dev.db'}"


def _seed_sqlite_sample_data(engine):
    from datetime import datetime

    from app.models.master import Base, Operation, ProductionOrder, WorkOrder

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine, future=True, autocommit=False, autoflush=False, expire_on_commit=False)
    session = Session()
    try:
        existing = session.scalar(select(func.count()).select_from(ProductionOrder)) or 0
        if existing > 0:
            return

        now = datetime.now()
        po1 = ProductionOrder(
            order_number="PO-1001",
            route_id="R-1001",
            product_name="Widget A",
            quantity=100,
            status="IN_PROGRESS",
            planned_start=now,
            planned_end=now.replace(hour=23, minute=59, second=59),
            tenant_id="default",
        )
        wo1 = WorkOrder(
            work_order_number="WO-1001",
            status="IN_PROGRESS",
            planned_start=now,
            planned_end=now.replace(hour=17, minute=0, second=0),
            actual_start=now,
            tenant_id="default",
        )
        op1 = Operation(
            operation_number="OP-1001",
            sequence=1,
            name="Cutting",
            status="COMPLETED",
            planned_start=now,
            planned_end=now.replace(hour=11, minute=0, second=0),
            actual_start=now,
            actual_end=now.replace(hour=10, minute=30, second=0),
            quantity=100,
            completed_qty=100,
            good_qty=100,
            scrap_qty=0,
            qc_required=True,
            tenant_id="default",
        )
        op2 = Operation(
            operation_number="OP-1002",
            sequence=2,
            name="Assembly",
            status="IN_PROGRESS",
            planned_start=now,
            planned_end=now.replace(hour=17, minute=0, second=0),
            actual_start=now,
            quantity=100,
            completed_qty=40,
            good_qty=40,
            scrap_qty=0,
            qc_required=False,
            tenant_id="default",
        )
        wo1.operations = [op1, op2]
        po1.work_orders = [wo1]

        po2 = ProductionOrder(
            order_number="PO-1002",
            route_id="R-1002",
            product_name="Gizmo B",
            quantity=50,
            status="PENDING",
            planned_start=now,
            planned_end=now.replace(hour=23, minute=59, second=59),
            tenant_id="default",
        )

        session.add_all([po1, po2])
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _create_engine():
    engine = create_engine(
        settings.database_url,
        future=True,
        pool_pre_ping=True,
    )

    if settings.app_env == "dev" and settings.database_url.startswith("postgresql"):
        try:
            with engine.connect():
                pass
        except OperationalError as exc:
            logging.warning(
                "Primary database unavailable, using local SQLite fallback: %s",
                exc,
            )
            fallback_url = _get_sqlite_fallback_url()
            engine = create_engine(
                fallback_url,
                future=True,
                connect_args={"check_same_thread": False},
            )
            _seed_sqlite_sample_data(engine)

    return engine


engine = _create_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
