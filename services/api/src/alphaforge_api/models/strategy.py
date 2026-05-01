from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from alphaforge_api.models.base import Base, TimestampMixin


class Strategy(Base, TimestampMixin):
    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    latest_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    versions: Mapped[list["StrategyVersion"]] = relationship(
        back_populates="strategy", cascade="all, delete-orphan", order_by="StrategyVersion.version.desc()"
    )

    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_strategies_owner_name"),)


class StrategyVersion(Base, TimestampMixin):
    __tablename__ = "strategy_versions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: uuid.uuid4().hex)
    strategy_id: Mapped[str] = mapped_column(
        ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    dsl: Mapped[dict] = mapped_column(JSONB, nullable=False)         # parsed DSL document
    raw_source: Mapped[str] = mapped_column(Text, nullable=False)    # original yaml/json
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    strategy: Mapped[Strategy] = relationship(back_populates="versions")

    __table_args__ = (UniqueConstraint("strategy_id", "version", name="uq_strategy_versions_v"),)
