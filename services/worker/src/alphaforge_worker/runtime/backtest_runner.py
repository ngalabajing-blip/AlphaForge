"""
Backtest engine.

Given a backtest_id this runner:

1. Loads the backtest record + strategy version from the database.
2. Initialises portfolio, risk manager, indicator pipeline.
3. Streams OHLCV candles in order, updates indicators, evaluates rules.
4. Executes signals through the portfolio (with fees + slippage).
5. Persists the full trade list and aggregate metrics back to the DB.

For dev environments without a populated time-series store, we use the
synthetic :class:`CandleProvider`.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from alphaforge_shared.logging import get_logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alphaforge_worker.config import get_settings
from alphaforge_worker.dsl.evaluator import EvalContext, StrategyEvaluator
from alphaforge_worker.dsl.parser import parse_strategy
from alphaforge_worker.indicators import INDICATORS
from alphaforge_worker.runtime.data import CandleProvider
from alphaforge_worker.runtime.metrics import compute_metrics
from alphaforge_worker.runtime.portfolio import Portfolio
from alphaforge_worker.runtime.risk import RiskManager

log = get_logger("alphaforge_worker.backtest")


class BacktestRunner:
    def run(self, backtest_id: str) -> dict[str, Any]:
        return asyncio.run(self._run(backtest_id))

    async def _run(self, backtest_id: str) -> dict[str, Any]:
        settings = get_settings()
        engine = create_async_engine(settings.database_url, future=True)
        Session = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with Session() as session:
                bt = await self._load_backtest(session, backtest_id)
                if bt is None:
                    log.warning("backtest_not_found", backtest_id=backtest_id)
                    return {"status": "not_found"}
                await self._mark_running(session, bt)
                strategy_doc, raw_source = await self._load_strategy(session, bt)
                if strategy_doc is None:
                    return {"status": "missing_strategy"}
                summary = await self._execute(session, bt, strategy_doc)
                return summary
        finally:
            await engine.dispose()

    async def _load_backtest(self, session: AsyncSession, backtest_id: str):  # type: ignore[no-untyped-def]
        from alphaforge_api.models.backtest import Backtest

        return await session.get(Backtest, backtest_id)

    async def _load_strategy(self, session: AsyncSession, bt):  # type: ignore[no-untyped-def]
        from alphaforge_api.models.strategy import StrategyVersion

        stmt = select(StrategyVersion).where(
            StrategyVersion.strategy_id == bt.strategy_id,
            StrategyVersion.version == bt.strategy_version,
        )
        version = (await session.execute(stmt)).scalar_one_or_none()
        if version is None:
            return None, None
        try:
            doc = parse_strategy(version.raw_source)
            return doc, version.raw_source
        except Exception as exc:  # noqa: BLE001
            log.exception("strategy_parse_failed", error=str(exc))
            return None, None

    async def _mark_running(self, session: AsyncSession, bt) -> None:  # type: ignore[no-untyped-def]
        bt.status = "running"
        await session.commit()

    async def _execute(self, session: AsyncSession, bt, strategy):  # type: ignore[no-untyped-def]
        provider = CandleProvider()
        portfolio = Portfolio(
            cash=Decimal(str(bt.initial_balance)),
            fee_bps=Decimal(str(bt.fee_bps)),
            slippage_bps=Decimal(str(bt.slippage_bps)),
        )
        risk = RiskManager(strategy.risk, portfolio.cash)
        symbols = list(strategy.universe.symbols)

        # one indicator instance per (symbol, alias)
        indicator_pipeline: dict[str, dict[str, Any]] = defaultdict(dict)
        for ind in strategy.indicators:
            cls = INDICATORS.get(ind.name)
            if cls is None:
                log.warning("unknown_indicator", indicator=ind.name)
                continue
            for sym in symbols:
                try:
                    indicator_pipeline[sym][ind.alias] = cls(**ind.params)  # type: ignore[arg-type]
                except TypeError:
                    indicator_pipeline[sym][ind.alias] = cls()  # type: ignore[call-arg]

        evaluator = StrategyEvaluator(strategy)
        marks: dict[str, Decimal] = {}
        trade_pnls: list[Decimal] = []
        events: list[dict[str, Any]] = []

        # interleave candles by timestamp
        streams = {
            sym: provider.stream(
                symbol=sym,
                timeframe=bt.timeframe or strategy.universe.timeframe,
                start=bt.start_at,
                end=bt.end_at,
            )
            for sym in symbols
        }
        # naive merge (synthetic streams advance together)
        candle_count = 0
        for candles in zip(*streams.values()):
            for sym, candle in zip(symbols, candles):
                pipeline = indicator_pipeline[sym]
                indicator_values: dict[str, Any] = {}
                indicator_history: dict[str, list[float]] = {}
                for alias, indicator in pipeline.items():
                    indicator.update(candle)
                    val = indicator.latest()
                    indicator_values[alias] = val
                    if isinstance(val, dict):
                        for k, v in val.items():
                            indicator_values[f"{alias}.{k}"] = v
                    else:
                        indicator_history[alias] = indicator.history(64)
                marks[sym] = Decimal(str(candle["close"]))
                ctx = EvalContext(
                    indicators=indicator_values,
                    indicators_history=indicator_history,
                    ohlcv=[candle],
                    state={
                        "position": (
                            float(portfolio.positions.get(sym).quantity)
                            if portfolio.positions.get(sym)
                            else 0.0
                        )
                    },
                    parameters=dict(bt.parameters or {}),
                    last_close=float(candle["close"]),
                )
                outcomes = evaluator.evaluate(ctx)
                for outcome in outcomes:
                    if not outcome.fired:
                        continue
                    fill = self._execute_action(
                        portfolio=portfolio,
                        risk=risk,
                        outcome=outcome,
                        symbol=sym,
                        candle=candle,
                        marks=marks,
                    )
                    if fill is not None:
                        events.append(_fill_to_dict(fill))
                        if fill.pnl != 0:
                            trade_pnls.append(fill.pnl)
            portfolio.mark(candles[0]["ts"], marks)
            candle_count += 1

        metrics = compute_metrics(
            initial=Decimal(str(bt.initial_balance)),
            equity_curve=portfolio.equity_curve,
            trade_pnls=trade_pnls,
        )
        await self._persist(session, bt, metrics, events, portfolio)
        return {
            "status": "completed",
            "candles": candle_count,
            "trades": len(events),
            "pnl_pct": str(metrics.pnl_pct),
            "sharpe": str(metrics.sharpe),
            "max_drawdown": str(metrics.max_drawdown),
        }

    def _execute_action(self, *, portfolio, risk, outcome, symbol, candle, marks):  # type: ignore[no-untyped-def]
        action = outcome.action
        price = Decimal(str(candle["close"]))
        ts = candle["ts"]
        if action == "buy":
            qty = self._size_to_qty(outcome.size, portfolio, price)
            if qty <= 0:
                return None
            decision = risk.check(
                ts=ts,
                symbol=symbol,
                side="buy",
                price=price,
                quantity=qty,
                portfolio=portfolio,
                marks=marks,
            )
            if not decision.allowed:
                return None
            if decision.adjusted_quantity is not None:
                qty = decision.adjusted_quantity
            return portfolio.buy(symbol, price, qty, ts)
        if action == "sell":
            position = portfolio.positions.get(symbol)
            if position is None or position.is_flat():
                return None
            qty = self._size_to_qty(outcome.size, portfolio, price, base_quantity=position.quantity)
            qty = min(qty, position.quantity)
            return portfolio.sell(symbol, price, qty, ts)
        if action == "close":
            position = portfolio.positions.get(symbol)
            if position is None or position.is_flat():
                return None
            return portfolio.sell(symbol, price, position.quantity, ts)
        return None

    @staticmethod
    def _size_to_qty(size, portfolio, price, base_quantity=None):  # type: ignore[no-untyped-def]
        if size is None:
            if base_quantity is not None:
                return base_quantity
            # default: 10% of cash
            return (portfolio.cash * Decimal("0.1")) / price
        size_dec = Decimal(str(size))
        if 0 < size_dec <= 1:
            # fraction of cash
            return (portfolio.cash * size_dec) / price
        return size_dec  # absolute quantity

    async def _persist(self, session: AsyncSession, bt, metrics, events, portfolio) -> None:  # type: ignore[no-untyped-def]
        from alphaforge_api.repositories.backtest import BacktestRepository

        repo = BacktestRepository(session)
        for fill in portfolio.fills:
            await repo.add_trade(
                backtest_id=bt.id,
                opened_at=fill.ts,
                closed_at=fill.ts if fill.side == "sell" else None,
                symbol=fill.symbol,
                side=fill.side,
                entry_price=fill.price,
                exit_price=fill.price if fill.side == "sell" else None,
                quantity=fill.quantity,
                pnl=fill.pnl,
                fees=fill.fee,
            )
        await repo.finalize(
            bt,
            final_balance=metrics.final_balance,
            pnl_abs=metrics.pnl_abs,
            pnl_pct=metrics.pnl_pct,
            sharpe=metrics.sharpe,
            sortino=metrics.sortino,
            max_drawdown=metrics.max_drawdown,
            win_rate=metrics.win_rate,
            trades_count=metrics.trades_count,
            metrics=metrics.metrics,
            completed_at=datetime.now(tz=UTC),
        )
        await session.commit()


def _fill_to_dict(fill) -> dict:  # type: ignore[no-untyped-def]
    return {
        "symbol": fill.symbol,
        "side": fill.side,
        "price": str(fill.price),
        "quantity": str(fill.quantity),
        "fee": str(fill.fee),
        "pnl": str(fill.pnl),
        "ts": fill.ts.isoformat() if hasattr(fill.ts, "isoformat") else str(fill.ts),
    }
