from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.approval import (
    ApprovalCreateRequest,
    ApprovalDecideRequest,
    ApprovalDecisionResponse,
    ApprovalRequestResponse,
)
from app.security.dependencies import RequestIdentity, require_action, require_permission
from app.services.approval_service import (
    create_approval_request,
    decide_approval_request,
    get_pending_approval_requests,
)

router = APIRouter(prefix="/approvals", tags=["approvals"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ApprovalRequestResponse, status_code=201)
def create_approval(
    request_data: ApprovalCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("approval.create")),
):
    """
    Submit an approval request.

    Any authenticated user may create a request.
    The effective role (acting_role_code if impersonating, else real role_code)
    is recorded as the requester_role_code for audit purposes.
    """
    effective_role = identity.acting_role_code or identity.role_code
    try:
        appr_req = create_approval_request(
            db=db,
            requester_id=identity.user_id,
            requester_role_code=effective_role,
            tenant_id=identity.tenant_id,
            request_data=request_data,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return appr_req


@router.get("/pending", response_model=list[ApprovalRequestResponse])
def list_pending(
    action_type: str | None = Query(None, description="Filter by action type"),
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("APPROVE")),
):
    """
    List pending approval requests for the caller's tenant.

    Requires APPROVE permission. Optionally filter by action_type.
    """
    return get_pending_approval_requests(db, identity.tenant_id, action_type)


@router.post("/{request_id}/decide", response_model=ApprovalDecisionResponse)
def decide_approval(
    request_id: int,
    decide_data: ApprovalDecideRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("approval.decide")),
):
    """
    Approve or reject a pending approval request.

    Requires APPROVE permission.
    - Requester cannot decide their own request (checked against real user_id).
    - Effective role must match the approval_rule for the action_type.
    - Impersonation does not bypass the requester-equals-decider check.
    """
    effective_role = identity.acting_role_code or identity.role_code
    try:
        decision = decide_approval_request(
            db=db,
            request_id=request_id,
            decider_user_id=identity.user_id,
            decider_role_code=effective_role,
            tenant_id=identity.tenant_id,
            decide_data=decide_data,
            impersonation_session_id=identity.impersonation_session_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return decision
