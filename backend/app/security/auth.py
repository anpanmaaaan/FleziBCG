import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class AuthIdentity:
    user_id: str
    username: str
    email: str | None
    tenant_id: str
    role_code: str | None


def _settings() -> Settings:
    return Settings()


def _load_default_users() -> list[dict[str, str]]:
    settings = _settings()
    try:
        raw = json.loads(settings.auth_default_users_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid auth_default_users_json configuration") from exc

    if not isinstance(raw, list):
        raise ValueError("auth_default_users_json must be a JSON list")

    users: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        username = str(item.get("username", "")).strip()
        password = str(item.get("password", "")).strip()
        tenant_id = str(item.get("tenant_id", "default")).strip() or "default"
        if not username or not password:
            continue
        users.append(
            {
                "user_id": str(item.get("user_id", username)),
                "username": username,
                "email": str(item.get("email")) if item.get("email") is not None else None,
                "password": password,
                "tenant_id": tenant_id,
                "role_code": str(item.get("role_code")) if item.get("role_code") is not None else None,
            }
        )
    return users


def _verify_password(plain_password: str, stored_password: str) -> bool:
    if stored_password.startswith("$2"):
        return pwd_context.verify(plain_password, stored_password)
    return plain_password == stored_password


def authenticate_user(username: str, password: str) -> AuthIdentity | None:
    for user in _load_default_users():
        if user["username"] != username:
            continue
        if not _verify_password(password, user["password"]):
            return None
        return AuthIdentity(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            tenant_id=user["tenant_id"],
            role_code=user["role_code"],
        )
    return None


def create_access_token(identity: AuthIdentity) -> str:
    settings = _settings()
    expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    expire_at = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": identity.user_id,
        "username": identity.username,
        "email": identity.email,
        "tenant_id": identity.tenant_id,
        "role_code": identity.role_code,
        "exp": expire_at,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> AuthIdentity | None:
    settings = _settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None

    user_id = payload.get("sub")
    username = payload.get("username")
    tenant_id = payload.get("tenant_id")
    if not user_id or not username or not tenant_id:
        return None

    return AuthIdentity(
        user_id=str(user_id),
        username=str(username),
        email=str(payload.get("email")) if payload.get("email") is not None else None,
        tenant_id=str(tenant_id),
        role_code=str(payload.get("role_code")) if payload.get("role_code") is not None else None,
    )
