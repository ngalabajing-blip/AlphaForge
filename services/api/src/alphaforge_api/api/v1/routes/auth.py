from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.config import get_settings
from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import (
    Role,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from alphaforge_api.repositories.user import UserRepository
from alphaforge_api.schemas.user import TokenPair, UserCreate, UserOut

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> UserOut:
    repo = UserRepository(session)
    if await repo.get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="email already registered")
    user = await repo.create(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role.value,
    )
    return UserOut.model_validate(user)


@router.post("/token", response_model=TokenPair)
async def token(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    repo = UserRepository(session)
    user = await repo.get_by_email(form.username)
    if not user or not user.password_hash or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user inactive")
    role = Role(user.role) if user.role in {r.value for r in Role} else Role.RESEARCHER
    await repo.touch_login(user)
    return TokenPair(
        access_token=create_access_token(subject=user.id, role=role),
        refresh_token=create_refresh_token(subject=user.id),
        expires_in=get_settings().jwt_access_expires,
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(refresh_token: str, session: AsyncSession = Depends(get_session)) -> TokenPair:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="invalid token type")
    repo = UserRepository(session)
    user = await repo.get(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="user not found or inactive")
    role = Role(user.role)
    return TokenPair(
        access_token=create_access_token(subject=user.id, role=role),
        refresh_token=create_refresh_token(subject=user.id),
        expires_in=get_settings().jwt_access_expires,
    )
