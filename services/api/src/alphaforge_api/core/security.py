"""
Authentication & authorization primitives.

* JWT issuance / verification (HS256)
* Password hashing (bcrypt)
* API-key hashing & verification
* RBAC role enum + permission map
* FastAPI dependencies for ``current_user`` / ``require_role``
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from alphaforge_api.core.config import get_settings
from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_api.security")
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


class Role(str, Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"
    SERVICE = "service"


PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.ADMIN: frozenset(
        {
            "read:any", "write:any",
            "strategies:create", "strategies:edit", "strategies:delete",
            "backtests:run", "backtests:read",
            "alerts:manage",
            "audits:run", "audits:read",
            "users:manage", "apikeys:manage",
        }
    ),
    Role.RESEARCHER: frozenset(
        {
            "read:any",
            "strategies:create", "strategies:edit",
            "backtests:run", "backtests:read",
            "alerts:manage",
            "audits:run", "audits:read",
            "apikeys:manage:self",
        }
    ),
    Role.VIEWER: frozenset({"read:any"}),
    Role.SERVICE: frozenset({"read:any", "write:internal"}),
}


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _pwd.verify(password, password_hash)
    except Exception:
        return False


def create_access_token(*, subject: str, role: Role, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role.value,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.jwt_access_expires)).timestamp()),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(*, subject: str) -> str:
    settings = get_settings()
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.jwt_refresh_expires)).timestamp()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc


# ── API keys ──────────────────────────────────────────────────────────────────
API_KEY_PREFIX = "afk_"


def generate_api_key() -> tuple[str, str]:
    """Return ``(plaintext_key, hashed)``. The plaintext is shown once."""
    secret = secrets.token_urlsafe(32)
    plaintext = f"{API_KEY_PREFIX}{secret}"
    hashed = hash_api_key(plaintext)
    return plaintext, hashed


def hash_api_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


# ── Auth dependencies ─────────────────────────────────────────────────────────
class CurrentUser:
    """Lightweight auth principal placed on the request state."""

    def __init__(self, user_id: str, role: Role, source: str, scopes: frozenset[str] | None = None):
        self.user_id = user_id
        self.role = role
        self.source = source
        self.scopes = scopes or PERMISSIONS[role]

    def can(self, permission: str) -> bool:
        return permission in self.scopes or "write:any" in self.scopes


async def get_current_user(
    request: Request,
    token: str | None = Depends(_oauth2_scheme),
) -> CurrentUser:
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return _principal_from_api_key(api_key)
    if not token:
        raise HTTPException(status_code=401, detail="not authenticated")
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="wrong token type")
    role_value = payload.get("role")
    try:
        role = Role(role_value)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="invalid role") from exc
    return CurrentUser(user_id=payload["sub"], role=role, source="jwt")


def _principal_from_api_key(api_key: str) -> CurrentUser:
    """Stub principal resolution by api key — production lookups happen in db.

    The actual key/role lookup is performed in the apikeys repository which is
    invoked from the routers; this lightweight helper provides a default.
    """
    if not api_key.startswith(API_KEY_PREFIX):
        raise HTTPException(status_code=401, detail="invalid api key")
    return CurrentUser(user_id=f"apikey:{api_key[-8:]}", role=Role.SERVICE, source="api-key")


def require_role(*allowed: Role):
    """FastAPI dependency factory: enforce caller role membership."""

    async def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user

    return _dep


def require_permission(permission: str):
    async def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.can(permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user

    return _dep
