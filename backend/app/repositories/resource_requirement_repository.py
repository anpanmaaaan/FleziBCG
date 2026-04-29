from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resource_requirement import ResourceRequirement


def list_resource_requirements_by_operation(
    db: Session,
    *,
    tenant_id: str,
    routing_id: str,
    operation_id: str,
) -> list[ResourceRequirement]:
    return list(
        db.scalars(
            select(ResourceRequirement)
            .where(
                ResourceRequirement.tenant_id == tenant_id,
                ResourceRequirement.routing_id == routing_id,
                ResourceRequirement.operation_id == operation_id,
            )
            .order_by(
                ResourceRequirement.required_resource_type.asc(),
                ResourceRequirement.required_capability_code.asc(),
                ResourceRequirement.requirement_id.asc(),
            )
        )
    )


def get_resource_requirement_by_id(
    db: Session,
    *,
    tenant_id: str,
    routing_id: str,
    operation_id: str,
    requirement_id: str,
) -> ResourceRequirement | None:
    return db.scalar(
        select(ResourceRequirement).where(
            ResourceRequirement.tenant_id == tenant_id,
            ResourceRequirement.routing_id == routing_id,
            ResourceRequirement.operation_id == operation_id,
            ResourceRequirement.requirement_id == requirement_id,
        )
    )


def get_resource_requirement_by_unique_key(
    db: Session,
    *,
    tenant_id: str,
    operation_id: str,
    required_resource_type: str,
    required_capability_code: str,
) -> ResourceRequirement | None:
    return db.scalar(
        select(ResourceRequirement).where(
            ResourceRequirement.tenant_id == tenant_id,
            ResourceRequirement.operation_id == operation_id,
            ResourceRequirement.required_resource_type == required_resource_type,
            ResourceRequirement.required_capability_code == required_capability_code,
        )
    )


def create_resource_requirement(db: Session, *, row: ResourceRequirement) -> ResourceRequirement:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_resource_requirement(db: Session, *, row: ResourceRequirement) -> ResourceRequirement:
    db.commit()
    db.refresh(row)
    return row


def delete_resource_requirement(db: Session, *, row: ResourceRequirement) -> None:
    db.delete(row)
    db.commit()
