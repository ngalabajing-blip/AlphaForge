from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    rule_type: str
    rule_config: dict[str, Any] = Field(default_factory=dict)
    channels: list[str] = Field(default_factory=list)
    cooldown_seconds: int = 300
    enabled: bool = True


class AlertUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    rule_config: dict[str, Any] | None = None
    channels: list[str] | None = None
    cooldown_seconds: int | None = None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    name: str
    description: str | None
    enabled: bool
    rule_type: str
    rule_config: dict[str, Any]
    channels: list[str]
    cooldown_seconds: int
    last_fired_at: datetime | None
    fire_count: int
    created_at: datetime


class AlertDeliveryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alert_id: str
    channel: str
    delivered_at: datetime
    success: bool
    error: str | None
