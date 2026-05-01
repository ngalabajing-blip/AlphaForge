from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.models.signal import Signal


class SignalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def insert(self, **kwargs) -> Signal:  # type: ignore[no-untyped-def]
        s = Signal(**kwargs)
        self.session.add(s)
        await self.session.flush()
        return s

    async def query(
        self,
        *,
        strategy_id: str | None = None,
        symbol: str | None = None,
        action: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
    ) -> list[Signal]:
        stmt = select(Signal)
        if strategy_id:
            stmt = stmt.where(Signal.strategy_id == strategy_id)
        if symbol:
            stmt = stmt.where(Signal.symbol == symbol.upper())
        if action:
            stmt = stmt.where(Signal.action == action.lower())
        if since:
            stmt = stmt.where(Signal.emitted_at >= since)
        if until:
            stmt = stmt.where(Signal.emitted_at <= until)
        stmt = stmt.order_by(Signal.emitted_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(Signal)
        return int((await self.session.execute(stmt)).scalar() or 0)
