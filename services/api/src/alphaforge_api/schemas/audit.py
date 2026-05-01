from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditRequestIn(BaseModel):
    chain: str = Field(min_length=2, max_length=32)
    address: str = Field(min_length=4, max_length=64)
    deep: bool = True


class FindingOut(BaseModel):
    rule: str
    severity: str
    title: str
    description: str
    location: str | None
    cwe: str | None
    swc: str | None


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chain: str
    address: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    risk_score: float | None
    risk_level: str | None
    summary: str | None
    findings: list[dict[str, Any]] = Field(default_factory=list)
    bytecode_size: int | None
    has_source: bool | None
    error: str | None
    created_at: datetime
