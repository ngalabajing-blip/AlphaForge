from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from alphaforge_api.models.base import Base, TimestampMixin


class AuditJob(Base, TimestampMixin):
    __tablename__ = "audit_jobs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    requested_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    chain: Mapped[str] = mapped_column(String(32), nullable=False)
    address: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    risk_score: Mapped[float | None] = mapped_column(Numeric(6, 3))
    risk_level: Mapped[str | None] = mapped_column(String(16))
    summary: Mapped[str | None] = mapped_column(Text)
    findings: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    bytecode_size: Mapped[int | None] = mapped_column()
    has_source: Mapped[bool | None] = mapped_column()
    error: Mapped[str | None] = mapped_column(Text)
