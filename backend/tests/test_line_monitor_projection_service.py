from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.plant_hierarchy import Area, Line, Plant, Station
from app.models.station_session import StationSession
from app.security.dependencies import RequestIdentity
from app.services.station_queue_service import get_line_monitor_projection

_PREFIX = "TEST-LINE-MONITOR"
_TENANT_ID = "default"


def _identity() -> RequestIdentity:
    return RequestIdentity(
        user_id=f"{_PREFIX}-SUP",
        username=f"{_PREFIX}-SUP",
        email=None,
        tenant_id=_TENANT_ID,
        role_code="SUP",
        is_authenticated=True,
    )


def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if po_ids:
        wo_ids = list(
            db.scalars(
                select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
            )
        )
        if wo_ids:
            op_ids = list(
                db.scalars(
                    select(Operation.id).where(Operation.work_order_id.in_(wo_ids))
                )
            )
            if op_ids:
                db.execute(
                    delete(ExecutionEvent).where(
                        ExecutionEvent.operation_id.in_(op_ids)
                    )
                )
                db.execute(
                    delete(StationSession).where(
                        StationSession.current_operation_id.in_(op_ids)
                    )
                )
            db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    station_ids = [f"{_PREFIX}-ST-A", f"{_PREFIX}-ST-B", f"{_PREFIX}-ST-C"]
    db.execute(delete(StationSession).where(StationSession.station_id.in_(station_ids)))
    db.execute(delete(Station).where(Station.station_id.in_(station_ids)))
    db.execute(
        delete(Line).where(Line.line_id.in_([f"{_PREFIX}-LINE-A", f"{_PREFIX}-LINE-B"]))
    )
    db.execute(delete(Area).where(Area.area_id == f"{_PREFIX}-AREA"))
    db.execute(delete(Plant).where(Plant.plant_id == f"{_PREFIX}-PLANT"))
    db.commit()


@pytest.fixture
def line_monitor_fixture():
    db = SessionLocal()
    try:
        _purge(db)

        plant = Plant(
            plant_id=f"{_PREFIX}-PLANT",
            tenant_id=_TENANT_ID,
            plant_code=f"{_PREFIX}-PLANT",
            plant_name="Line Monitor Test Plant",
        )
        db.add(plant)
        db.flush()

        area = Area(
            area_id=f"{_PREFIX}-AREA",
            tenant_id=_TENANT_ID,
            plant_id=plant.plant_id,
            area_code=f"{_PREFIX}-AREA",
            area_name="Line Monitor Test Area",
        )
        db.add(area)
        db.flush()

        line_a = Line(
            line_id=f"{_PREFIX}-LINE-A",
            tenant_id=_TENANT_ID,
            area_id=area.area_id,
            line_code="LINE-A",
            line_name="Line A",
        )
        line_b = Line(
            line_id=f"{_PREFIX}-LINE-B",
            tenant_id=_TENANT_ID,
            area_id=area.area_id,
            line_code="LINE-B",
            line_name="Line B",
        )
        db.add(line_a)
        db.add(line_b)
        db.flush()

        station_a = Station(
            station_id=f"{_PREFIX}-ST-A",
            tenant_id=_TENANT_ID,
            line_id=line_a.line_id,
            station_code="ST-A",
            station_name="Station A",
        )
        station_b = Station(
            station_id=f"{_PREFIX}-ST-B",
            tenant_id=_TENANT_ID,
            line_id=line_a.line_id,
            station_code="ST-B",
            station_name="Station B",
        )
        station_c = Station(
            station_id=f"{_PREFIX}-ST-C",
            tenant_id=_TENANT_ID,
            line_id=line_b.line_id,
            station_code="ST-C",
            station_name="Station C",
        )
        db.add(station_a)
        db.add(station_b)
        db.add(station_c)
        db.flush()

        production_order = ProductionOrder(
            order_number=f"{_PREFIX}-PO-001",
            route_id=f"{_PREFIX}-R-01",
            product_name="Line monitor projection fixture",
            quantity=30,
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(production_order)
        db.flush()

        work_order = WorkOrder(
            production_order_id=production_order.id,
            work_order_number=f"{_PREFIX}-WO-001",
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(work_order)
        db.flush()

        def _mk_op(
            *, suffix: str, station_id: str, status: str, sequence: int
        ) -> Operation:
            op = Operation(
                operation_number=f"{_PREFIX}-OP-{suffix}",
                work_order_id=work_order.id,
                sequence=sequence,
                name=f"Operation {suffix}",
                status=status,
                planned_start=datetime(2099, 6, 1, 9, sequence, 0),
                planned_end=datetime(2099, 6, 1, 10, sequence, 0),
                quantity=10,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=False,
                station_scope_value=station_id,
                tenant_id=_TENANT_ID,
            )
            db.add(op)
            db.flush()
            return op

        op_running = _mk_op(
            suffix="RUN",
            station_id=station_a.station_id,
            status=StatusEnum.in_progress.value,
            sequence=10,
        )
        op_downtime = _mk_op(
            suffix="DOWN",
            station_id=station_b.station_id,
            status=StatusEnum.paused.value,
            sequence=20,
        )
        op_blocked = _mk_op(
            suffix="BLOCK",
            station_id=station_c.station_id,
            status=StatusEnum.blocked.value,
            sequence=30,
        )

        for op in (op_running, op_downtime, op_blocked):
            db.add(
                ExecutionEvent(
                    event_type=ExecutionEventType.OP_STARTED.value,
                    production_order_id=production_order.id,
                    work_order_id=work_order.id,
                    operation_id=op.id,
                    payload={"operator_id": "seed"},
                    tenant_id=_TENANT_ID,
                )
            )
        for op in (op_downtime, op_blocked):
            db.add(
                ExecutionEvent(
                    event_type=ExecutionEventType.DOWNTIME_STARTED.value,
                    production_order_id=production_order.id,
                    work_order_id=work_order.id,
                    operation_id=op.id,
                    payload={"reason_code": "BREAKDOWN_GENERIC"},
                    tenant_id=_TENANT_ID,
                )
            )

        db.add(
            StationSession(
                session_id=f"{_PREFIX}-SESSION-A",
                tenant_id=_TENANT_ID,
                station_id=station_a.station_id,
                operator_user_id="opr-line-a",
                status="OPEN",
                current_operation_id=op_running.id,
            )
        )

        db.commit()

        yield db
    finally:
        _purge(db)
        db.close()


def test_line_monitor_projection_maps_station_statuses(line_monitor_fixture):
    db = line_monitor_fixture

    items = get_line_monitor_projection(db, _identity())
    by_station = {item["station_id"]: item for item in items}

    assert by_station[f"{_PREFIX}-ST-A"]["status"] == "RUNNING"
    assert by_station[f"{_PREFIX}-ST-B"]["status"] == "DOWNTIME"
    assert by_station[f"{_PREFIX}-ST-C"]["status"] == "BLOCKED"

    assert by_station[f"{_PREFIX}-ST-A"]["operator_user_id"] == "opr-line-a"
    assert by_station[f"{_PREFIX}-ST-B"]["downtime_open"] is True


def test_line_monitor_projection_filters_by_line_code(line_monitor_fixture):
    db = line_monitor_fixture

    items = get_line_monitor_projection(db, _identity(), line_code="LINE-A")

    station_ids = {item["station_id"] for item in items}
    assert station_ids == {f"{_PREFIX}-ST-A", f"{_PREFIX}-ST-B"}
