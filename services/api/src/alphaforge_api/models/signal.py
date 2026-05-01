from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from alphaforge_api.models.base import Base, TimestampMixin


class Signal(Base, TimestampMixin):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    strategy_id: Mapped[str] = mapped_column(ForeignKey("strategies.id"), nullable=False, index=True)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    emitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    strength: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    suggested_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(28, 8))
    indicators: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    reasons: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    __table_args__ = (
        Index("ix_signals_symbol_emitted_at", "symbol", "emitted_at"),
    )
