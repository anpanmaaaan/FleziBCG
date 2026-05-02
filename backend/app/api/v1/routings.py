from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.resource_requirement import (
    ResourceRequirementCreateRequest,
    ResourceRequirementItem,
    ResourceRequirementUpdateRequest,
)
from app.schemas.routing import (
    RoutingCreateRequest,
    RoutingItem,
    RoutingOperationCreateRequest,
    RoutingOperationUpdateRequest,
    RoutingUpdateRequest,
)
from app.security.dependencies import RequestIdentity, require_action, require_authenticated_identity
from app.services.routing_service import (
    add_routing_operation as add_routing_operation_service,
    create_routing as create_routing_service,
    get_routing_by_id as get_routing_by_id_service,
    list_routings as list_routings_service,
    release_routing as release_routing_service,
    remove_routing_operation as remove_routing_operation_service,
    retire_routing as retire_routing_service,
    update_routing as update_routing_service,
    update_routing_operation as update_routing_operation_service,
)
from app.services.resource_requirement_service import (
    create_resource_requirement as create_resource_requirement_service,
    delete_resource_requirement as delete_resource_requirement_service,
    get_resource_requirement_by_id as get_resource_requirement_by_id_service,
    list_resource_requirements as list_resource_requirements_service,
    update_resource_requirement as update_resource_requirement_service,
)

router = APIRouter(prefix="/routings", tags=["routings"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[RoutingItem])
def list_routings(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[RoutingItem]:
    return list_routings_service(db, tenant_id=identity.tenant_id)


@router.get("/{routing_id}", response_model=RoutingItem)
def get_routing_by_id(
    routing_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> RoutingItem:
    row = get_routing_by_id_service(db, tenant_id=identity.tenant_id, routing_id=routing_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Routing not found")
    return row


@router.post("", response_model=RoutingItem)
def create_routing(
    payload: RoutingCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.routing.manage")),
) -> RoutingItem:
    try:
        return create_routing_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except ValueError as exc:
        if str(exc) == "Duplicate routing_code in tenant":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{routing_id}", response_model=RoutingItem)
def update_routing(
    routing_id: str,
    payload: RoutingUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.routing.manage")),
) -> RoutingItem:
    try:
        return update_routing_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate routing_code in tenant":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{routing_id}/operations", response_model=RoutingItem)
def add_routing_operation(
    routing_id: str,
    payload: RoutingOperationCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.routing.manage")),
) -> RoutingItem:
    try:
        return add_routing_operation_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate sequence_no in routing":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{routing_id}/operations/{operation_id}", response_model=RoutingItem)
def update_routing_operation(
    routing_id: str,
    operation_id: str,
    payload: RoutingOperationUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.routing.manage")),
) -> RoutingItem:
    try:
        return update_routing_operation_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
            operation_id=operation_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate sequence_no in routing":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{routing_id}/operations/{operation_id}", response_model=RoutingItem)
def remove_routing_operation(
    routing_id: str,
    operation_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.routing.manage")),
) -> RoutingItem:
    try:
        return remove_routing_operation_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
            operation_id=operation_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{routing_id}/release", response_model=RoutingItem)
def release_routing(
    routing_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.routing.manage")),
) -> RoutingItem:
    try:
        return release_routing_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{routing_id}/retire", response_model=RoutingItem)
def retire_routing(
    routing_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.routing.manage")),
) -> RoutingItem:
    try:
        return retire_routing_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/{routing_id}/operations/{operation_id}/resource-requirements",
    response_model=list[ResourceRequirementItem],
)
def list_resource_requirements(
    routing_id: str,
    operation_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[ResourceRequirementItem]:
    return list_resource_requirements_service(
        db,
        tenant_id=identity.tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )


@router.get(
    "/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}",
    response_model=ResourceRequirementItem,
)
def get_resource_requirement_by_id(
    routing_id: str,
    operation_id: str,
    requirement_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> ResourceRequirementItem:
    row = get_resource_requirement_by_id_service(
        db,
        tenant_id=identity.tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
        requirement_id=requirement_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Resource requirement not found")
    return row


@router.post(
    "/{routing_id}/operations/{operation_id}/resource-requirements",
    response_model=ResourceRequirementItem,
)
def create_resource_requirement(
    routing_id: str,
    operation_id: str,
    payload: ResourceRequirementCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.resource_requirement.manage")),
) -> ResourceRequirementItem:
    try:
        return create_resource_requirement_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
            operation_id=operation_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate resource requirement in operation":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch(
    "/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}",
    response_model=ResourceRequirementItem,
)
def update_resource_requirement(
    routing_id: str,
    operation_id: str,
    requirement_id: str,
    payload: ResourceRequirementUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.resource_requirement.manage")),
) -> ResourceRequirementItem:
    try:
        return update_resource_requirement_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
            operation_id=operation_id,
            requirement_id=requirement_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate resource requirement in operation":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete(
    "/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}",
    response_model=ResourceRequirementItem,
)
def delete_resource_requirement(
    routing_id: str,
    operation_id: str,
    requirement_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.resource_requirement.manage")),
) -> ResourceRequirementItem:
    try:
        return delete_resource_requirement_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            routing_id=routing_id,
            operation_id=operation_id,
            requirement_id=requirement_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
