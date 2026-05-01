from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: str
    rule_config: dict[str, Any] = Field(default_factory=dict)
    channels: list[str] = Field(default_factory=list)
    cooldown_seconds: int = 300
    enabled: bool = True


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    rule_config: Optional[dict[str, Any]] = None
    channels: Optional[list[str]] = None
    cooldown_seconds: Optional[int] = None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    name: str
    description: Optional[str]
    enabled: bool
    rule_type: str
    rule_config: dict[str, Any]
    channels: list[str]
    cooldown_seconds: int
    last_fired_at: Optional[datetime]
    fire_count: int
    created_at: datetime


class AlertDeliveryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alert_id: str
    channel: str
    delivered_at: datetime
    success: bool
    error: Optional[str]
