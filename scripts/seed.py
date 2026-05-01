#!/usr/bin/env python3
"""
Seed the AlphaForge database with a small fleet of demo accounts,
strategies, alerts and audit jobs so the frontend looks alive
immediately after `alembic upgrade head`.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "api" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared" / "src"))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from alphaforge_api.db.session import Base  # type: ignore[import-not-found]
from alphaforge_api.db.models import (  # type: ignore[import-not-found]
    User, Strategy, StrategyVersion, Backtest, Signal, AuditJob, Alert,
)
from alphaforge_api.security.password import hash_password  # type: ignore[import-not-found]


DEFAULT_DSL = """\
strategy: "Demo EMA cross"
universe: { symbols: [ETH/USDT], timeframe: 1h }
indicators:
  - {name: ema, alias: fast, period: 12}
  - {name: ema, alias: slow, period: 26}
rules:
  - when: cross_up(fast, slow)
    then: buy
    size: 0.1
  - when: cross_down(fast, slow)
    then: close
"""


async def main() -> None:
    db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge")
    engine = create_async_engine(db_url)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    now = datetime.now(tz=timezone.utc)
    async with Session() as session:
        admin = User(
            email="admin@alphaforge.local",
            password_hash=hash_password("changeme"),
            full_name="AlphaForge Admin",
            role="admin",
            is_active=True,
        )
        researcher = User(
            email="quant@alphaforge.local",
            password_hash=hash_password("changeme"),
            full_name="Demo Researcher",
            role="researcher",
            is_active=True,
        )
        viewer = User(
            email="viewer@alphaforge.local",
            password_hash=hash_password("changeme"),
            full_name="Demo Viewer",
            role="viewer",
            is_active=True,
        )
        session.add_all([admin, researcher, viewer])
        await session.flush()

        strategy = Strategy(
            owner_id=researcher.id,
            name="Demo EMA cross",
            description="Seeded strategy",
            is_public=True,
            tags=["trend", "ema"],
        )
        session.add(strategy)
        await session.flush()

        version = StrategyVersion(
            strategy_id=strategy.id,
            version=1,
            raw_source=DEFAULT_DSL,
            parameters={"fast_period": 12, "slow_period": 26},
            notes="initial",
        )
        session.add(version)
        await session.flush()

        backtest = Backtest(
            strategy_id=strategy.id,
            strategy_version=1,
            owner_id=researcher.id,
            timeframe="1h",
            start_at=now - timedelta(days=30),
            end_at=now,
            initial_balance=Decimal("10000"),
            final_balance=Decimal("10880"),
            pnl_abs=Decimal("880"),
            pnl_pct=Decimal("8.8"),
            sharpe=Decimal("1.45"),
            sortino=Decimal("1.92"),
            max_drawdown=Decimal("0.07"),
            win_rate=Decimal("57.3"),
            trades_count=42,
            status="completed",
        )
        session.add(backtest)
        for i in range(8):
            session.add(Signal(
                strategy_id=strategy.id,
                strategy_version=1,
                symbol="ETH/USDT",
                action="buy" if i % 2 == 0 else "close",
                strength=0.6 + 0.05 * (i % 3),
                emitted_at=now - timedelta(hours=i),
                reasons=["cross_up", "rsi_low"] if i % 2 == 0 else ["cross_down"],
            ))
        session.add_all([
            AuditJob(
                requested_by=researcher.id,
                chain="eth",
                address="0x" + "ab" * 20,
                deep=True,
                status="completed",
                risk_score=72,
                risk_level="high",
                summary="Detected blacklist + delegatecall + onlyOwner",
                findings=[
                    {"category": "bytecode", "code": "DELEGATECALL", "severity": "high",
                     "description": "DELEGATECALL opcode used"},
                    {"category": "source", "code": "SOL_BLACKLIST", "severity": "high",
                     "description": "Blacklist add function present"},
                ],
                created_at=now - timedelta(hours=1),
                completed_at=now,
            ),
        ])
        session.add(Alert(
            owner_id=researcher.id,
            name="ETH/USDT critical anomaly",
            rule_type="anomaly",
            channels=["telegram", "discord"],
            enabled=True,
            fire_count=3,
            last_fired_at=now - timedelta(minutes=12),
        ))
        await session.commit()
    print("seeded.")


if __name__ == "__main__":
    asyncio.run(main())
