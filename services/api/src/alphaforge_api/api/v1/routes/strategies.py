from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import (
    CurrentUser,
    get_current_user,
    require_permission,
)
from alphaforge_api.repositories.strategy import StrategyRepository
from alphaforge_api.schemas.common import Page, PageMeta
from alphaforge_api.schemas.strategy import (
    StrategyCreate,
    StrategyOut,
    StrategyUpdate,
    StrategyVersionOut,
)
from alphaforge_api.services.strategy_service import StrategyService

router = APIRouter(prefix="/strategies")


@router.get("", response_model=Page[StrategyOut])
async def list_strategies(
    page: int = 1,
    size: int = 50,
    mine: bool = True,
    public: bool = True,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Page[StrategyOut]:
    repo = StrategyRepository(session)
    owner_id = user.user_id if mine else None
    total = await repo.count(owner_id=owner_id, include_public=public)
    items = await repo.list(
        owner_id=owner_id,
        include_public=public,
        limit=size,
        offset=(page - 1) * size,
    )
    return Page(
        items=[StrategyOut.model_validate(s) for s in items],
        meta=PageMeta(
            total=total,
            page=page,
            size=size,
            has_next=page * size < total,
            has_prev=page > 1,
        ),
    )


@router.post("", response_model=StrategyOut, status_code=201)
async def create_strategy(
    payload: StrategyCreate,
    user: CurrentUser = Depends(require_permission("strategies:create")),
    session: AsyncSession = Depends(get_session),
) -> StrategyOut:
    service = StrategyService(session)
    strategy = await service.create(owner_id=user.user_id, payload=payload)
    return StrategyOut.model_validate(strategy)


@router.get("/{strategy_id}", response_model=StrategyOut)
async def get_strategy(
    strategy_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> StrategyOut:
    repo = StrategyRepository(session)
    s = await repo.get(strategy_id)
    if s is None:
        raise HTTPException(status_code=404, detail="strategy not found")
    if s.owner_id != user.user_id and not s.is_public:
        raise HTTPException(status_code=403, detail="forbidden")
    return StrategyOut.model_validate(s)


@router.patch("/{strategy_id}", response_model=StrategyOut)
async def update_strategy(
    strategy_id: str,
    payload: StrategyUpdate,
    user: CurrentUser = Depends(require_permission("strategies:edit")),
    session: AsyncSession = Depends(get_session),
) -> StrategyOut:
    service = StrategyService(session)
    strategy = await service.update(strategy_id=strategy_id, owner_id=user.user_id, payload=payload)
    return StrategyOut.model_validate(strategy)


@router.delete("/{strategy_id}", status_code=204)
async def delete_strategy(
    strategy_id: str,
    user: CurrentUser = Depends(require_permission("strategies:delete")),
    session: AsyncSession = Depends(get_session),
) -> None:
    service = StrategyService(session)
    await service.delete(strategy_id=strategy_id, owner_id=user.user_id)


@router.get("/{strategy_id}/versions", response_model=list[StrategyVersionOut])
async def list_versions(
    strategy_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[StrategyVersionOut]:
    repo = StrategyRepository(session)
    s = await repo.get(strategy_id)
    if s is None or (s.owner_id != user.user_id and not s.is_public):
        raise HTTPException(status_code=404, detail="strategy not found")
    versions = await repo.list_versions(strategy_id)
    return [StrategyVersionOut.model_validate(v) for v in versions]


@router.post("/{strategy_id}/versions", response_model=StrategyVersionOut, status_code=201)
async def add_version(
    strategy_id: str,
    raw_source: str,
    parameters: dict | None = None,
    notes: str | None = None,
    user: CurrentUser = Depends(require_permission("strategies:edit")),
    session: AsyncSession = Depends(get_session),
) -> StrategyVersionOut:
    service = StrategyService(session)
    version = await service.add_version(
        strategy_id=strategy_id,
        owner_id=user.user_id,
        raw_source=raw_source,
        parameters=parameters or {},
        notes=notes,
    )
    return StrategyVersionOut.model_validate(version)
