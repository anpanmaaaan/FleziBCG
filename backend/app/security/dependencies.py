from dataclasses import dataclass

from fastapi import Header, HTTPException, Request

from app.security.auth import AuthIdentity


@dataclass
class RequestIdentity:
    user_id: str
    username: str
    email: str | None
    tenant_id: str
    role_code: str | None
    is_authenticated: bool


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
        )

    tenant = x_tenant_id or "default"
    return _anonymous_identity(tenant)


def require_authenticated_identity(request: Request) -> RequestIdentity:
    auth_identity: AuthIdentity | None = getattr(request.state, "auth_identity", None)
    if not auth_identity:
        raise HTTPException(status_code=401, detail="Authentication required")

    # TODO(Phase 6B): Introduce authorization/persona enforcement in dedicated policy layer.
    return RequestIdentity(
        user_id=auth_identity.user_id,
        username=auth_identity.username,
        email=auth_identity.email,
        tenant_id=auth_identity.tenant_id,
        role_code=auth_identity.role_code,
        is_authenticated=True,
    )
