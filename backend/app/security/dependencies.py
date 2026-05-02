from dataclasses import dataclass, field

from fastapi import Depends, Header, HTTPException, Request

from app.db.session import SessionLocal
from app.security.auth import AuthIdentity
from app.security.rbac import PermissionFamily, has_action, has_permission


# INTENT: RequestIdentity separates authentication from authorization context.
# user_id always refers to the real human, even under impersonation.
# acting_role_code carries the impersonated role for RBAC checks.
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


def _normalize_tenant(tenant_id: str | None) -> str:
    return (tenant_id or "").strip() or "default"


def _assert_tenant_header_matches_identity(
    auth_identity: AuthIdentity,
    x_tenant_id: str | None,
) -> None:
    if x_tenant_id is None:
        return
    request_tenant = _normalize_tenant(x_tenant_id)
    if request_tenant != auth_identity.tenant_id:
        raise HTTPException(status_code=403, detail="Tenant header mismatch")


def get_request_identity(
    request: Request,
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> RequestIdentity:
    auth_identity: AuthIdentity | None = getattr(request.state, "auth_identity", None)
    if auth_identity:
        _assert_tenant_header_matches_identity(auth_identity, x_tenant_id)
        return RequestIdentity(
            user_id=auth_identity.user_id,
            username=auth_identity.username,
            email=auth_identity.email,
            tenant_id=auth_identity.tenant_id,
            role_code=auth_identity.role_code,
            is_authenticated=True,
            session_id=auth_identity.session_id,
        )

    tenant = _normalize_tenant(x_tenant_id)
    return _anonymous_identity(tenant)


def _get_security_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_authenticated_identity(
    request: Request,
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    db=Depends(_get_security_db),
) -> RequestIdentity:
    auth_identity: AuthIdentity | None = getattr(request.state, "auth_identity", None)
    if not auth_identity:
        raise HTTPException(status_code=401, detail="Authentication required")

    _assert_tenant_header_matches_identity(auth_identity, x_tenant_id)

    # INVARIANT: Session validity is checked on every authenticated request,
    # not just at login. This enables real-time revocation (e.g., admin
    # revoking a compromised session takes effect immediately).
    if not auth_identity.session_id:
        raise HTTPException(status_code=401, detail="Session is missing")

    from app.services.session_service import is_session_active

    if not is_session_active(db, auth_identity.session_id, auth_identity.tenant_id):
        raise HTTPException(status_code=401, detail="Session is invalid or revoked")

    # INVARIANT (P0-A-02C): Tenant lifecycle is checked on every authenticated
    # request. Policy A (strict): missing tenant row → rejected (no legacy allow).
    # DISABLED/SUSPENDED/inactive tenant rows are also hard-rejected here.
    from app.repositories.tenant_repository import is_tenant_lifecycle_active

    if not is_tenant_lifecycle_active(db, auth_identity.tenant_id):
        raise HTTPException(status_code=403, detail="Tenant is not active")

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


# INTENT: require_action mirrors require_permission but resolves via
# ACTION_CODE_REGISTRY → family, supporting fine-grained action codes
# (e.g., "execution.start") alongside coarse permission families.
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
