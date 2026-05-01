from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from alphaforge_api.models.base import Base, TimestampMixin


class Backtest(Base, TimestampMixin):
    __tablename__ = "backtests"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    strategy_id: Mapped[str] = mapped_column(
        ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    strategy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False, index=True)

    # window
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(8), nullable=False)

    # config
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False)
    fee_bps: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("10"), nullable=False)
    slippage_bps: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("5"), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # results
    final_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(28, 8))
    pnl_abs: Mapped[Optional[Decimal]] = mapped_column(Numeric(28, 8))
    pnl_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    sharpe: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    sortino: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    max_drawdown: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    win_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    trades_count: Mapped[Optional[int]] = mapped_column(Integer)
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text)

    trades: Mapped[list["BacktestTrade"]] = relationship(
        back_populates="backtest", cascade="all, delete-orphan", lazy="selectin"
    )


class BacktestTrade(Base):
    __tablename__ = "backtest_trades"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    backtest_id: Mapped[str] = mapped_column(
        ForeignKey("backtests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False)
    exit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(28, 8))
    quantity: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False)
    pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(28, 8))
    fees: Mapped[Decimal] = mapped_column(Numeric(28, 8), default=Decimal("0"), nullable=False)

    backtest: Mapped[Backtest] = relationship(back_populates="trades")
