from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphaforge_api.models.backtest import Backtest, BacktestTrade


class BacktestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, backtest_id: str, *, with_trades: bool = False) -> Backtest | None:
        if with_trades:
            stmt = select(Backtest).options(selectinload(Backtest.trades)).where(Backtest.id == backtest_id)
            return (await self.session.execute(stmt)).scalar_one_or_none()
        return await self.session.get(Backtest, backtest_id)

    async def create(self, **kwargs: Any) -> Backtest:
        bt = Backtest(**kwargs)
        self.session.add(bt)
        await self.session.flush()
        return bt

    async def list(
        self,
        *,
        strategy_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Backtest]:
        stmt = select(Backtest)
        if strategy_id:
            stmt = stmt.where(Backtest.strategy_id == strategy_id)
        if status:
            stmt = stmt.where(Backtest.status == status)
        stmt = stmt.order_by(Backtest.created_at.desc()).limit(limit).offset(offset)
        return list((await self.session.execute(stmt)).scalars().all())

    async def count(self, *, strategy_id: str | None = None, status: str | None = None) -> int:
        stmt = select(func.count()).select_from(Backtest)
        if strategy_id:
            stmt = stmt.where(Backtest.strategy_id == strategy_id)
        if status:
            stmt = stmt.where(Backtest.status == status)
        return int((await self.session.execute(stmt)).scalar() or 0)

    async def update_status(self, bt: Backtest, status: str, *, error: str | None = None) -> Backtest:
        bt.status = status
        if error:
            bt.error = error
        await self.session.flush()
        return bt

    async def finalize(
        self,
        bt: Backtest,
        *,
        final_balance: Decimal,
        pnl_abs: Decimal,
        pnl_pct: Decimal,
        sharpe: Decimal,
        sortino: Decimal,
        max_drawdown: Decimal,
        win_rate: Decimal,
        trades_count: int,
        metrics: dict,
        completed_at: datetime,
    ) -> Backtest:
        bt.status = "completed"
        bt.final_balance = final_balance
        bt.pnl_abs = pnl_abs
        bt.pnl_pct = pnl_pct
        bt.sharpe = sharpe
        bt.sortino = sortino
        bt.max_drawdown = max_drawdown
        bt.win_rate = win_rate
        bt.trades_count = trades_count
        bt.metrics = metrics
        await self.session.flush()
        return bt

    async def add_trade(self, **kwargs: Any) -> BacktestTrade:
        trade = BacktestTrade(**kwargs)
        self.session.add(trade)
        await self.session.flush()
        return trade
