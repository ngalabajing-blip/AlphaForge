from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import CurrentUser, get_current_user
from alphaforge_api.repositories.signal import SignalRepository
from alphaforge_api.schemas.signal import SignalOut

router = APIRouter(prefix="/signals")


@router.get("", response_model=list[SignalOut])
async def list_signals(
    strategy_id: Optional[str] = None,
    symbol: Optional[str] = None,
    action: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
) -> list[SignalOut]:
    repo = SignalRepository(session)
    items = await repo.query(
        strategy_id=strategy_id,
        symbol=symbol,
        action=action,
        since=since,
        until=until,
        limit=limit,
    )
    return [SignalOut.model_validate(s) for s in items]
