from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import (
    CurrentUser,
    Role,
    get_current_user,
    require_role,
)
from alphaforge_api.repositories.user import UserRepository
from alphaforge_api.schemas.common import Page, PageMeta
from alphaforge_api.schemas.user import UserOut

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserOut)
async def me(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    repo = UserRepository(session)
    record = await repo.get(user.user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="user not found")
    return UserOut.model_validate(record)


@router.get("", response_model=Page[UserOut], dependencies=[Depends(require_role(Role.ADMIN))])
async def list_users(
    page: int = 1,
    size: int = 50,
    session: AsyncSession = Depends(get_session),
) -> Page[UserOut]:
    if page < 1 or size < 1 or size > 200:
        raise HTTPException(status_code=400, detail="invalid pagination")
    repo = UserRepository(session)
    total = await repo.count()
    items = await repo.list(limit=size, offset=(page - 1) * size)
    return Page(
        items=[UserOut.model_validate(u) for u in items],
        meta=PageMeta(
            total=total,
            page=page,
            size=size,
            has_next=page * size < total,
            has_prev=page > 1,
        ),
    )
