from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrategyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_public: bool = False
    tags: list[str] = Field(default_factory=list)
    raw_source: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)


class StrategyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    is_archived: bool | None = None
    tags: list[str] | None = None


class StrategyVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    version: int
    raw_source: str
    parameters: dict[str, Any]
    notes: str | None
    created_at: datetime


class StrategyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    name: str
    description: str | None
    is_public: bool
    is_archived: bool
    tags: list[str]
    latest_version: int
    created_at: datetime
    updated_at: datetime
