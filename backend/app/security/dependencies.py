from dataclasses import dataclass, field

from fastapi import Depends, Header, HTTPException, Request

from app.db.session import SessionLocal
from app.security.auth import AuthIdentity
from app.security.rbac import PermissionFamily, has_action, has_permission


@dataclass
class RequestIdentity:
    user_id: str
    username: str
    email: str | None
    tenant_id: str
    role_code: str | None
    is_authenticated: bool
    session_id: str | None = field(default=None)
    impersonation_session_id: int | None = field(default=None)
    acting_role_code: str | None = field(default=None)


def _anonymous_identity(tenant_id: str) -> RequestIdentity:
    return RequestIdentity(
        user_id="anonymous",
        username="anonymous",
        email=None,
        tenant_id=tenant_id,
        role_code=None,
        is_authenticated=False,
    )


def get_request_identity(
    request: Request,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> RequestIdentity:
    auth_identity: AuthIdentity | None = getattr(request.state, "auth_identity", None)
    if auth_identity:
        return RequestIdentity(
            user_id=auth_identity.user_id,
            username=auth_identity.username,
            email=auth_identity.email,
            tenant_id=auth_identity.tenant_id,
            role_code=auth_identity.role_code,
            is_authenticated=True,
            session_id=auth_identity.session_id,
        )

    tenant = x_tenant_id or "default"
    return _anonymous_identity(tenant)


def _get_security_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_authenticated_identity(
    request: Request, db=Depends(_get_security_db)
) -> RequestIdentity:
    auth_identity: AuthIdentity | None = getattr(request.state, "auth_identity", None)
    if not auth_identity:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not auth_identity.session_id:
        raise HTTPException(status_code=401, detail="Session is missing")

    from app.services.session_service import is_session_active

    if not is_session_active(db, auth_identity.session_id, auth_identity.tenant_id):
        raise HTTPException(status_code=401, detail="Session is invalid or revoked")

    # TODO(Phase 6B): Introduce authorization/persona enforcement in dedicated policy layer.
    return RequestIdentity(
        user_id=auth_identity.user_id,
        username=auth_identity.username,
        email=auth_identity.email,
        tenant_id=auth_identity.tenant_id,
        role_code=auth_identity.role_code,
        is_authenticated=True,
        session_id=auth_identity.session_id,
    )


# WHY: Only EXECUTE, APPROVE, CONFIGURE actions performed under impersonation
# are audit-logged. VIEW and ADMIN are excluded because VIEW is read-only
# (low risk) and ADMIN impersonation is forbidden by FORBIDDEN_ACTING_ROLES.
_AUDITED_FAMILIES = frozenset({"EXECUTE", "APPROVE", "CONFIGURE"})


def require_permission(permission_family: PermissionFamily):
    def dependency(
        request: Request,
        identity: RequestIdentity = Depends(require_authenticated_identity),
        db=Depends(_get_security_db),
    ) -> RequestIdentity:
        from app.repositories.impersonation_repository import (
            get_active_impersonation_session,
        )
        from app.services.impersonation_service import log_impersonation_permission_use

        # WHY: Impersonation is resolved here (not in the route handler) so that
        # every permission-gated endpoint automatically picks up the acting role.
        # The real user_id is preserved — identity.user_id always refers to the
        # actual human, never the impersonated persona.
        effective_identity = identity
        active_session = get_active_impersonation_session(
            db, identity.user_id, identity.tenant_id
        )

        if active_session is not None:
            effective_identity = RequestIdentity(
                user_id=identity.user_id,
                username=identity.username,
                email=identity.email,
                tenant_id=identity.tenant_id,
                role_code=identity.role_code,
                is_authenticated=identity.is_authenticated,
                session_id=identity.session_id,
                impersonation_session_id=active_session.id,
                acting_role_code=active_session.acting_role_code,
            )

        if not has_permission(db, effective_identity, permission_family):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission_family}",
            )

        if active_session is not None and permission_family in _AUDITED_FAMILIES:
            log_impersonation_permission_use(
                db,
                active_session,
                permission_family,
                endpoint=str(request.url),
            )

        return effective_identity

    return dependency


def require_action(action_code: str):
    def dependency(
        request: Request,
        identity: RequestIdentity = Depends(require_authenticated_identity),
        db=Depends(_get_security_db),
    ) -> RequestIdentity:
        from app.repositories.impersonation_repository import (
            get_active_impersonation_session,
        )
        from app.services.impersonation_service import log_impersonation_permission_use

        effective_identity = identity
        active_session = get_active_impersonation_session(
            db, identity.user_id, identity.tenant_id
        )
        if active_session is not None:
            effective_identity = RequestIdentity(
                user_id=identity.user_id,
                username=identity.username,
                email=identity.email,
                tenant_id=identity.tenant_id,
                role_code=identity.role_code,
                is_authenticated=identity.is_authenticated,
                session_id=identity.session_id,
                impersonation_session_id=active_session.id,
                acting_role_code=active_session.acting_role_code,
            )

        if not has_action(db, effective_identity, action_code):
            raise HTTPException(
                status_code=403, detail=f"Missing required action: {action_code}"
            )

        if active_session is not None:
            # Preserve existing audit taxonomy by logging through permission family slot.
            log_impersonation_permission_use(
                db,
                active_session,
                permission_family=f"ACTION:{action_code}",
                endpoint=str(request.url),
            )

        return effective_identity

    return dependency
