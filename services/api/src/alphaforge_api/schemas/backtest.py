from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BacktestCreate(BaseModel):
    strategy_id: str
    strategy_version: Optional[int] = None
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
    closed_at: Optional[datetime]
    symbol: str
    side: str
    entry_price: Decimal
    exit_price: Optional[Decimal]
    quantity: Decimal
    pnl: Optional[Decimal]
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
    final_balance: Optional[Decimal]
    pnl_pct: Optional[Decimal]
    sharpe: Optional[Decimal]
    max_drawdown: Optional[Decimal]
    trades_count: Optional[int]
    created_at: datetime


class BacktestOut(BacktestSummary):
    fee_bps: Decimal
    slippage_bps: Decimal
    pnl_abs: Optional[Decimal]
    sortino: Optional[Decimal]
    win_rate: Optional[Decimal]
    metrics: dict[str, Any]
    error: Optional[str]
    trades: list[BacktestTradeOut] = Field(default_factory=list)
