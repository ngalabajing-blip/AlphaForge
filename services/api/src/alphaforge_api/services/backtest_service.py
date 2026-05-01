from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.kafka_client import kafka_producer
from alphaforge_api.repositories.backtest import BacktestRepository
from alphaforge_api.repositories.strategy import StrategyRepository
from alphaforge_api.schemas.backtest import BacktestCreate
from alphaforge_shared.events import OrderEvent  # placeholder for future direct enqueue


class BacktestService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = BacktestRepository(session)
        self.strategy_repo = StrategyRepository(session)

    async def create_and_enqueue(self, *, payload: BacktestCreate, requested_by: str):
        strategy = await self.strategy_repo.get(payload.strategy_id)
        if strategy is None:
            raise HTTPException(status_code=404, detail="strategy not found")
        version = payload.strategy_version or strategy.latest_version
        if not await self.strategy_repo.get_version(strategy.id, version):
            raise HTTPException(status_code=400, detail="strategy version not found")

        bt = await self.repo.create(
            strategy_id=strategy.id,
            strategy_version=version,
            requested_by=requested_by,
            status="queued",
            start_at=payload.start_at,
            end_at=payload.end_at,
            timeframe=payload.timeframe,
            initial_balance=payload.initial_balance,
            fee_bps=payload.fee_bps,
            slippage_bps=payload.slippage_bps,
            parameters=payload.parameters,
        )

        # Enqueue via Celery / Kafka (best effort — service should not fail if broker is down).
        try:
            await self._enqueue(bt.id)
        except Exception:
            pass
        return bt

    async def _enqueue(self, backtest_id: str) -> None:
        try:
            from celery import Celery  # type: ignore[import-not-found]
        except ImportError:  # pragma: no cover
            return
        # We do NOT import the worker package — talk to it via task name only to keep
        # the API/worker boundary clean.
        from alphaforge_api.core.config import get_settings
        settings = get_settings()
        app = Celery("af-api", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
        app.send_task("alphaforge_worker.run_backtest", args=[backtest_id])

    async def cancel(self, backtest_id: str) -> None:
        bt = await self.repo.get(backtest_id)
        if bt is None:
            raise HTTPException(status_code=404, detail="backtest not found")
        if bt.status in {"completed", "failed", "cancelled"}:
            return
        await self.repo.update_status(bt, "cancelled")
