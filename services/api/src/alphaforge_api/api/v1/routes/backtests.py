from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import CurrentUser, get_current_user, require_permission
from alphaforge_api.repositories.backtest import BacktestRepository
from alphaforge_api.schemas.backtest import BacktestCreate, BacktestOut, BacktestSummary
from alphaforge_api.schemas.common import Page, PageMeta
from alphaforge_api.services.backtest_service import BacktestService

router = APIRouter(prefix="/backtests")


@router.post("", response_model=BacktestOut, status_code=202)
async def create_backtest(
    payload: BacktestCreate,
    user: CurrentUser = Depends(require_permission("backtests:run")),
    session: AsyncSession = Depends(get_session),
) -> BacktestOut:
    service = BacktestService(session)
    bt = await service.create_and_enqueue(payload=payload, requested_by=user.user_id)
    return BacktestOut.model_validate(bt)


@router.get("", response_model=Page[BacktestSummary])
async def list_backtests(
    page: int = 1,
    size: int = 50,
    strategy_id: str | None = None,
    status_: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
) -> Page[BacktestSummary]:
    repo = BacktestRepository(session)
    total = await repo.count(strategy_id=strategy_id, status=status_)
    items = await repo.list(
        strategy_id=strategy_id, status=status_,
        limit=size, offset=(page - 1) * size,
    )
    return Page(
        items=[BacktestSummary.model_validate(b) for b in items],
        meta=PageMeta(total=total, page=page, size=size,
                      has_next=page * size < total, has_prev=page > 1),
    )


@router.get("/{backtest_id}", response_model=BacktestOut)
async def get_backtest(
    backtest_id: str,
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
) -> BacktestOut:
    repo = BacktestRepository(session)
    bt = await repo.get(backtest_id, with_trades=True)
    if bt is None:
        raise HTTPException(status_code=404, detail="backtest not found")
    return BacktestOut.model_validate(bt)


@router.delete("/{backtest_id}", status_code=204)
async def cancel_backtest(
    backtest_id: str,
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(require_permission("backtests:run")),
) -> None:
    service = BacktestService(session)
    await service.cancel(backtest_id)
