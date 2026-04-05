from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.impersonation_repository import get_active_impersonation_session
from app.schemas.auth import AuthUser
from app.schemas.iam import ImpersonationSummary, MeCapabilitiesResponse, RoleAssignmentSummary
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.iam_service import get_role_assignments_for_identity

router = APIRouter(prefix="/iam", tags=["iam"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/me/capabilities", response_model=MeCapabilitiesResponse)
def me_capabilities(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> MeCapabilitiesResponse:
    assignments = [
        RoleAssignmentSummary.model_validate(item)
        for item in get_role_assignments_for_identity(db, identity)
    ]

    primary_assignment = next((item for item in assignments if item.is_primary), None)
    active_session = get_active_impersonation_session(db, identity.user_id, identity.tenant_id)

    return MeCapabilitiesResponse(
        user=AuthUser(
            user_id=identity.user_id,
            username=identity.username,
            email=identity.email,
            tenant_id=identity.tenant_id,
            role_code=identity.role_code,
        ),
        assignments=assignments,
        primary_assignment=primary_assignment,
        impersonation=ImpersonationSummary(
            active=active_session is not None,
            session_id=active_session.id if active_session is not None else None,
            acting_role_code=active_session.acting_role_code if active_session is not None else None,
            expires_at=active_session.expires_at if active_session is not None else None,
        ),
    )
