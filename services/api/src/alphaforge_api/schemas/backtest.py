from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BacktestCreate(BaseModel):
    strategy_id: str
    strategy_version: int | None = None
    start_at: datetime
    end_at: datetime
    timeframe: str = "1h"
    initial_balance: Decimal = Field(default=Decimal("10000"))
    fee_bps: Decimal = Field(default=Decimal("10"))
    slippage_bps: Decimal = Field(default=Decimal("5"))
    parameters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("end_at")
    @classmethod
    def _end_after_start(cls, v: datetime, info: Any) -> datetime:
        start = info.data.get("start_at")
        if start and v <= start:
            raise ValueError("end_at must be after start_at")
        return v


class BacktestTradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    opened_at: datetime
    closed_at: datetime | None
    symbol: str
    side: str
    entry_price: Decimal
    exit_price: Decimal | None
    quantity: Decimal
    pnl: Decimal | None
    fees: Decimal


class BacktestSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    strategy_id: str
    status: str
    start_at: datetime
    end_at: datetime
    timeframe: str
    initial_balance: Decimal
    final_balance: Decimal | None
    pnl_pct: Decimal | None
    sharpe: Decimal | None
    max_drawdown: Decimal | None
    trades_count: int | None
    created_at: datetime


class BacktestOut(BacktestSummary):
    fee_bps: Decimal
    slippage_bps: Decimal
    pnl_abs: Decimal | None
    sortino: Decimal | None
    win_rate: Decimal | None
    metrics: dict[str, Any]
    error: str | None
    trades: list[BacktestTradeOut] = Field(default_factory=list)
