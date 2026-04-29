from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.routing import Routing, RoutingOperation


def list_routings_by_tenant(db: Session, *, tenant_id: str) -> list[Routing]:
    return list(
        db.scalars(
            select(Routing)
            .options(selectinload(Routing.operations))
            .where(Routing.tenant_id == tenant_id)
            .order_by(Routing.routing_code.asc(), Routing.routing_id.asc())
        )
    )


def get_routing_by_id(db: Session, *, tenant_id: str, routing_id: str) -> Routing | None:
    return db.scalar(
        select(Routing)
        .options(selectinload(Routing.operations))
        .where(Routing.tenant_id == tenant_id, Routing.routing_id == routing_id)
    )


def get_routing_by_code(db: Session, *, tenant_id: str, routing_code: str) -> Routing | None:
    return db.scalar(
        select(Routing)
        .where(Routing.tenant_id == tenant_id, Routing.routing_code == routing_code)
    )


def get_routing_operation_by_id(
    db: Session,
    *,
    tenant_id: str,
    routing_id: str,
    operation_id: str,
) -> RoutingOperation | None:
    return db.scalar(
        select(RoutingOperation).where(
            RoutingOperation.tenant_id == tenant_id,
            RoutingOperation.routing_id == routing_id,
            RoutingOperation.operation_id == operation_id,
        )
    )


def get_routing_operation_by_sequence(
    db: Session,
    *,
    tenant_id: str,
    routing_id: str,
    sequence_no: int,
) -> RoutingOperation | None:
    return db.scalar(
        select(RoutingOperation).where(
            RoutingOperation.tenant_id == tenant_id,
            RoutingOperation.routing_id == routing_id,
            RoutingOperation.sequence_no == sequence_no,
        )
    )


def create_routing(db: Session, *, row: Routing) -> Routing:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_routing(db: Session, *, row: Routing) -> Routing:
    db.commit()
    db.refresh(row)
    return row


def create_routing_operation(db: Session, *, row: RoutingOperation) -> RoutingOperation:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_routing_operation(db: Session, *, row: RoutingOperation) -> RoutingOperation:
    db.commit()
    db.refresh(row)
    return row


def delete_routing_operation(db: Session, *, row: RoutingOperation) -> None:
    db.delete(row)
    db.commit()
