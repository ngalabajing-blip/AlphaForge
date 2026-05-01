"""
GraphQL surface — strawberry-graphql backed.

Exposes Strategy, Backtest, Signal, Alert, Audit and Market queries.
Subscriptions stream live signals and market updates to web/desktop clients.

The router is mounted at ``/graphql``. All queries require an authenticated
caller (JWT in the ``Authorization: Bearer ...`` header or ``X-API-Key``).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import strawberry
from alphaforge_shared.symbols import parse_symbol
from sqlalchemy import select
from strawberry.fastapi import GraphQLRouter

from alphaforge_api.core.database import db
from alphaforge_api.models.alert import Alert as AlertORM
from alphaforge_api.models.audit import AuditJob as AuditORM
from alphaforge_api.models.signal import Signal as SignalORM
from alphaforge_api.models.strategy import Strategy as StrategyORM
from alphaforge_api.services.market_service import MarketService


# ── Types ─────────────────────────────────────────────────────────────────────
@strawberry.type
class StrategyType:
    id: str
    name: str
    description: str | None
    is_public: bool
    tags: list[str]
    latest_version: int
    created_at: datetime


@strawberry.type
class SignalType:
    id: str
    strategy_id: str
    run_id: str
    symbol: str
    action: str
    strength: float
    emitted_at: datetime
    reasons: list[str]


@strawberry.type
class AlertType:
    id: str
    name: str
    rule_type: str
    enabled: bool
    fire_count: int
    channels: list[str]
    created_at: datetime


@strawberry.type
class AuditType:
    id: str
    chain: str
    address: str
    status: str
    risk_score: float | None
    risk_level: str | None
    summary: str | None
    created_at: datetime


@strawberry.type
class CandleType:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@strawberry.type
class MarketTickerType:
    symbol: str
    price: float
    ts: datetime


# ── Queries ───────────────────────────────────────────────────────────────────
@strawberry.type
class Query:
    @strawberry.field
    async def strategies(self, public_only: bool = False, limit: int = 50) -> list[StrategyType]:
        async with db.session() as sess:
            stmt = select(StrategyORM).order_by(StrategyORM.updated_at.desc()).limit(limit)
            if public_only:
                stmt = stmt.where(StrategyORM.is_public.is_(True))
            rows = (await sess.execute(stmt)).scalars().all()
            return [
                StrategyType(
                    id=s.id,
                    name=s.name,
                    description=s.description,
                    is_public=s.is_public,
                    tags=s.tags,
                    latest_version=s.latest_version,
                    created_at=s.created_at,
                )
                for s in rows
            ]

    @strawberry.field
    async def signals(
        self,
        strategy_id: str | None = None,
        symbol: str | None = None,
        limit: int = 100,
    ) -> list[SignalType]:
        async with db.session() as sess:
            stmt = select(SignalORM)
            if strategy_id:
                stmt = stmt.where(SignalORM.strategy_id == strategy_id)
            if symbol:
                stmt = stmt.where(SignalORM.symbol == symbol.upper())
            stmt = stmt.order_by(SignalORM.emitted_at.desc()).limit(limit)
            rows = (await sess.execute(stmt)).scalars().all()
            return [
                SignalType(
                    id=s.id,
                    strategy_id=s.strategy_id,
                    run_id=s.run_id,
                    symbol=s.symbol,
                    action=s.action,
                    strength=float(s.strength),
                    emitted_at=s.emitted_at,
                    reasons=s.reasons,
                )
                for s in rows
            ]

    @strawberry.field
    async def alerts(self, owner_id: str | None = None) -> list[AlertType]:
        async with db.session() as sess:
            stmt = select(AlertORM)
            if owner_id:
                stmt = stmt.where(AlertORM.owner_id == owner_id)
            rows = (await sess.execute(stmt)).scalars().all()
            return [
                AlertType(
                    id=a.id,
                    name=a.name,
                    rule_type=a.rule_type,
                    enabled=a.enabled,
                    fire_count=a.fire_count,
                    channels=a.channels,
                    created_at=a.created_at,
                )
                for a in rows
            ]

    @strawberry.field
    async def audits(self, address: str | None = None, limit: int = 50) -> list[AuditType]:
        async with db.session() as sess:
            stmt = select(AuditORM).order_by(AuditORM.created_at.desc()).limit(limit)
            if address:
                stmt = stmt.where(AuditORM.address == address.lower())
            rows = (await sess.execute(stmt)).scalars().all()
            return [
                AuditType(
                    id=j.id,
                    chain=j.chain,
                    address=j.address,
                    status=j.status,
                    risk_score=(float(j.risk_score) if j.risk_score is not None else None),
                    risk_level=j.risk_level,
                    summary=j.summary,
                    created_at=j.created_at,
                )
                for j in rows
            ]

    @strawberry.field
    async def candles(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> list[CandleType]:
        sym = parse_symbol(symbol)
        from datetime import datetime, timedelta

        end = datetime.now(tz=UTC)
        start = end - timedelta(days=14)
        rows = await MarketService().candles(sym, timeframe=timeframe, start=start, end=end, limit=limit)
        return [
            CandleType(
                ts=datetime.fromisoformat(r["ts"]),
                open=r["open"],
                high=r["high"],
                low=r["low"],
                close=r["close"],
                volume=r["volume"],
            )
            for r in rows
        ]


# ── Subscriptions ─────────────────────────────────────────────────────────────
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def market_ticker(
        self, symbol: str, interval_seconds: float = 1.0
    ) -> AsyncGenerator[MarketTickerType, None]:
        sym = parse_symbol(symbol)
        service = MarketService()
        try:
            while True:
                price = await service.latest(sym)
                yield MarketTickerType(
                    symbol=sym.canonical,
                    price=float(price.price),
                    ts=price.ts,
                )
                await asyncio.sleep(max(0.1, interval_seconds))
        except asyncio.CancelledError:
            return


schema = strawberry.Schema(query=Query, subscription=Subscription)
graphql_router = GraphQLRouter(schema)
