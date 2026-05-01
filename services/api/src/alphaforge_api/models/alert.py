from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from alphaforge_api.models.base import Base, TimestampMixin


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)        # price_drop, anomaly, signal, audit_failed, …
    rule_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    channels: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    cooldown_seconds: Mapped[int] = mapped_column(default=300, nullable=False)
    last_fired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    fire_count: Mapped[int] = mapped_column(default=0, nullable=False)

    deliveries: Mapped[list["AlertDelivery"]] = relationship(back_populates="alert", cascade="all, delete-orphan")


class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    alert_id: Mapped[str] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    alert: Mapped[Alert] = relationship(back_populates="deliveries")
