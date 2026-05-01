from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SignalQuery(BaseModel):
    strategy_id: str | None = None
    symbol: str | None = None
    action: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    limit: int = Field(default=100, ge=1, le=1000)


class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    strategy_id: str
    run_id: str
    emitted_at: datetime
    symbol: str
    action: str
    strength: Decimal
    suggested_size: Decimal | None
    indicators: dict
    reasons: list[str]
