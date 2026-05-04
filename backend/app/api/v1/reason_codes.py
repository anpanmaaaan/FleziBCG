from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.reason_code import (
    ReasonCodeCreateRequest,
    ReasonCodeItem,
    ReasonCodeUpdateRequest,
)
from app.security.dependencies import (
    RequestIdentity,
    require_action,
    require_authenticated_identity,
)
from app.security.rbac import has_action
from app.services.reason_code_service import (
    create_reason_code as create_reason_code_service,
    get_reason_code as get_reason_code_service,
    list_reason_codes as list_reason_codes_service,
    release_reason_code as release_reason_code_service,
    retire_reason_code as retire_reason_code_service,
    update_reason_code as update_reason_code_service,
)

router = APIRouter(prefix="/reason-codes", tags=["reason-codes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Read endpoints ───────────────────────────────────────────────────────────


@router.get("", response_model=list[ReasonCodeItem])
def list_reason_codes(
    domain: str | None = None,
    category: str | None = None,
    lifecycle_status: str | None = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[ReasonCodeItem]:
    has_manage = has_action(db, identity, "admin.master_data.reason_code.manage")
    return list_reason_codes_service(
        db,
        tenant_id=identity.tenant_id,
        reason_domain=domain,
        reason_category=category,
        lifecycle_status=lifecycle_status,
        include_inactive=include_inactive,
        has_manage_permission=has_manage,
    )


@router.get("/{reason_code_id}", response_model=ReasonCodeItem)
def get_reason_code(
    reason_code_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> ReasonCodeItem:
    has_manage = has_action(db, identity, "admin.master_data.reason_code.manage")
    code = get_reason_code_service(
        db,
        tenant_id=identity.tenant_id,
        reason_code_id=reason_code_id,
        has_manage_permission=has_manage,
    )
    if code is None:
        raise HTTPException(status_code=404, detail="Reason code not found")
    return code


# ─── Write endpoints ──────────────────────────────────────────────────────────


@router.post("", response_model=ReasonCodeItem, status_code=201)
def create_reason_code(
    payload: ReasonCodeCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(
        require_action("admin.master_data.reason_code.manage")
    ),
) -> ReasonCodeItem:
    try:
        return create_reason_code_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{reason_code_id}", response_model=ReasonCodeItem)
def update_reason_code(
    reason_code_id: str,
    payload: ReasonCodeUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(
        require_action("admin.master_data.reason_code.manage")
    ),
) -> ReasonCodeItem:
    try:
        return update_reason_code_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            reason_code_id=reason_code_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{reason_code_id}/release", response_model=ReasonCodeItem)
def release_reason_code(
    reason_code_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(
        require_action("admin.master_data.reason_code.manage")
    ),
) -> ReasonCodeItem:
    try:
        return release_reason_code_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            reason_code_id=reason_code_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{reason_code_id}/retire", response_model=ReasonCodeItem)
def retire_reason_code(
    reason_code_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(
        require_action("admin.master_data.reason_code.manage")
    ),
) -> ReasonCodeItem:
    try:
        return retire_reason_code_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            reason_code_id=reason_code_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
